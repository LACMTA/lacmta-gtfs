import os
import re
import datetime
import csv
from typing import Dict
import pytz
import PyRSS2Gen
import requests

from utils.ftp_helper import *
from utils.date_helper import *
from utils.log_helper import *


RUNNING_LOCALLY = None
FTP_SERVER = None
FTP_USER = None
FTP_PW = None
GITLAB_TOKEN = None

try:
    from config import *
    RUNNING_LOCALLY = True
except ImportError:
    RUNNING_LOCALLY = False
    print('No config file found. Using default values.')

if not RUNNING_LOCALLY:
	FTP_SERVER = os.environ.get('SERVER')
	FTP_USER = os.environ.get('FTP_USERNAME')
	FTP_PW = os.environ.get('FTP_PASS')
	GITLAB_TOKEN = os.environ.get('GITLAB_TOKEN')

if RUNNING_LOCALLY:
	FTP_SERVER = Config.SERVER
	FTP_USER = Config.USERNAME
	FTP_PW = Config.PASS
	GITLAB_TOKEN = Config.GITLAB_TOKEN

log = build_log(True)

CALENDAR_DATES_CURRENT = "https://gitlab.com/LACMTA/gtfs_bus/-/raw/master/calendar_dates/calendar_dates.txt"
#CALENDAR_DATES_SHAKEUP = "https://gitlab.com/LACMTA/gtfs_bus/-/raw/master/calendar_dates.txt"
CALENDAR_DATES_EXPRESS = "../inputs/dse-sofi-express.csv"
CALENDAR_DATES_CURRENT_NEW = "current/calendar_dates.txt"

ROOT_DIR = os.getcwd()
CALENDAR_DATES_FILENAME = 'calendar_dates.txt'
EXPRESS_FILENAME = 'dse-sofi-express.csv'

REMOTE_FTP_PATH = '/nextbus/prod/'
REMOTE_CURRENT_PATH = 'https://gitlab.com/LACMTA/gtfs_bus/-/raw/master/calendar_dates/calendar_dates.txt'

OUTPUT_DIR = ROOT_DIR + '/data/'

INPUT_DIR = ROOT_DIR + '/inputs/'
INPUT_WEEKLY_DIR = ROOT_DIR + '/inputs/weekly/'

def first_wednesday_before_date(date):
	while date.strftime('%A') != 'Wednesday':
		date = date + datetime.timedelta(days=-1)
	if date.strftime('%A') == 'Wednesday':
		return date

def get_date_range(list_data):
	start_date = ''
	
	for row in list_data:
		if (row[1] == 'date'):
			continue
		row_date = convert_text_to_date(row[1])
		if start_date == '' or row_date < start_date:
			start_date = row_date
	
	if start_date.strftime('%A') != 'Wednesday':
		start_date = first_wednesday_before_date(start_date)
	
	start_end_date = {
		'start_date': start_date,
		'end_date': start_date + datetime.timedelta(weeks=2)
	}
	return start_end_date

def is_in_date_range(date, range):
	if date >= range['start_date'] and date <= range['end_date']:
		return True
	else:
		return False

def get_in_date_range(list_data, data_range):
	result_data = []
	count = 0 
	for row in list_data:
		if (row[1] == 'date'):
			continue
		row_date = convert_text_to_date(row[1])
		if is_in_date_range(row_date, data_range):
			count += 1
			result_data.append(row)
	log("Found " + str(count) + " lines")
	return result_data

def remove_in_date_range(list_data, date_range):
	result_data = []
	count = 0 
	for row in list_data:
		if (row[1] == 'date'):
			result_data.append(row)
			continue
		row_date = convert_text_to_date(row[1])

		if is_in_date_range(row_date, date_range):
			count += 1
			continue
		else:
			result_data.append(row)
	
	log("Removed " + str(count) + " lines")
	return result_data

def get_file_as_list(file):
	result = csv.reader(open(file, 'r'))
	log("Read " + file)
	return list(result)

def get_url_as_list(url):
	response = requests.get(url)
	csv_response = csv.reader(response.text.splitlines())
	log("Read " + url)
	return list(csv_response)

def combine_list_data(data_1, data_2):
	result_data = []
	for row in data_1:
		result_data.append(row)
	for row in data_2:
		# remove header row from data_2 if it exists
		if (row[1] == 'date'):
			continue
		result_data.append(row)
	return result_data

def write_data_to_file(list_data, filepath):
	with open(filepath, 'w') as f:
		writer = csv.writer(f)
		writer.writerows(list_data)
	log("Wrote " + filepath)
	return

def push_to_github():
	os.system('git pull')
	os.system('git add .')
	os.system('git commit -m "Auto update"')
	os.system('git push')
	return

def push_to_gitlab():
	scratch_dir= 'scratch'

	# Test repository:
	target_dir = 'scratch/token-test'
	target_gitlab = 'LACMTA/token-test.git'

	# GTFS Bus repository:
	# target_dir = 'scratch/gtfs_bus'
	# target_gitlab = 'LACMTA/gtfs_bus.git'

	os.system('if [ -d ' + scratch_dir + ' ]; then rm -rf ' + scratch_dir + '; fi')
	os.system('mkdir ' + scratch_dir)
	os.system('mkdir ' + target_dir)
	os.system('git -C ' + scratch_dir + ' clone https://oauth2:' + GITLAB_TOKEN + '@gitlab.com' + target_gitlab)
	os.system('cp data/calendar_dates.txt ' + target_dir + '/calendar_dates.txt')
	os.system('git -C ' + target_dir + ' add .')
	os.system('git -C ' + target_dir + ' commit -m "Auto update calendar_dates"')
	os.system('git -C ' + target_dir + ' push')
	return

def update_rss():
	log("Now: " + str(datetime.datetime.now(pytz.timezone('US/Pacific'))))

	rss = PyRSS2Gen.RSS2(
		title = "LACMTA Bus GTFS Updates",
		link = "https://gitlab.com/LACMTA/gtfs_bus",
		description = "This RSS feed updates when the LA Metro Bus GTFS data is updated.",
		lastBuildDate = datetime.datetime.now(pytz.timezone('US/Pacific')),
		items = [
			PyRSS2Gen.RSSItem(
				title = "Weekly calendar_dates.txt update",
				link = "https://gitlab.com/LACMTA/gtfs_bus",
				description = "The weekly calendar_dates.txt file has been updated.",
				pubDate = datetime.datetime.now(pytz.timezone('US/Pacific'))
			)])

	rss.write_xml(open(OUTPUT_DIR + "rss.xml", "w"))
	return

def main():
	if connect_to_ftp(REMOTE_FTP_PATH, FTP_SERVER, FTP_USER, FTP_PW):
		if get_file_from_ftp(CALENDAR_DATES_FILENAME, INPUT_WEEKLY_DIR):
			weekly_data = get_file_as_list(INPUT_WEEKLY_DIR + CALENDAR_DATES_FILENAME)
			
			date_range = get_date_range(weekly_data)

			express_data = get_file_as_list(INPUT_DIR + EXPRESS_FILENAME)
			express_data = get_in_date_range(express_data, date_range)

			weekly_express_combined_data = combine_list_data(weekly_data, express_data)
			
			current_data = get_url_as_list(REMOTE_CURRENT_PATH)
			current_data = remove_in_date_range(current_data, date_range)
			
			result = combine_list_data(current_data, weekly_express_combined_data)
			write_data_to_file(result, OUTPUT_DIR + CALENDAR_DATES_FILENAME)

			# push_to_github()
			push_to_gitlab()
			update_rss()
		
		disconnect_from_ftp()
	
main()


# push to gitlab
