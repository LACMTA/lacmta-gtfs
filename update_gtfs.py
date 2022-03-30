import os
import datetime
import pytz
import PyRSS2Gen

import subprocess

import utils.ftp_helper as ftp_helper
import utils.date_helper as date_helper
import utils.log_helper as log_helper
import utils.list_helper as list_helper
import utils.git_helper as git_helper

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

log = log_helper.build_log(True)

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
INPUT_WEEKLY_DIR = INPUT_DIR + 'weekly/'

def push_to_github():
	os.system('git pull')
	os.system('git add .')
	os.system('git commit -m "Auto update"')
	os.system('git push')
	return

def push_to_gitlab():
	log('Start push to GitLab')
	scratch_dir= 'scratch'

	# Test repository:
	# repo_dir = 'token-test'
	# target_gitlab = 'LACMTA/token-test.git'

	# GTFS Bus repository:
	repo_dir = 'gtfs_bus'
	target_gitlab = 'LACMTA/gtfs_bus.git'

	target_dir = scratch_dir + '/' + repo_dir

	output = subprocess.run('if [ -d ' + scratch_dir + ' ]; then rm -rf ' + scratch_dir + '; fi', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	log('Clean up scratch directory')
	log('Output: ' + output.stdout)
	log('Errors: ' + output.stderr)
	
	output = subprocess.run('mkdir ' + scratch_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	log('Created scratch directory')
	log('Output: ' + output.stdout)
	log('Errors: ' + output.stderr)
	
	output = subprocess.run('mkdir ' + target_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	log('Create target directory: ' + target_dir)
	log('Output: ' + output.stdout)
	log('Errors: ' + output.stderr)
	
	output = subprocess.run('git -C ' + scratch_dir + ' clone https://oauth2:' + GITLAB_TOKEN + '@gitlab.com/' + target_gitlab, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	log('Clone target repository: ' + target_gitlab)
	log('Output: ' + output.stdout)
	log('Errors: ' + output.stderr)

	output = subprocess.run('git -C ' + target_dir + ' config user.email "kinn@metro.net"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	log('Configure user.email')
	log('Output: ' + output.stdout)
	log('Errors: ' + output.stderr)

	output = subprocess.run('git -C ' + target_dir + ' config user.name "Nina Kin"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	log('Configure user.name')
	log('Output: ' + output.stdout)
	log('Errors: ' + output.stderr)
	
	output = subprocess.run('cp data/calendar_dates.txt ' + target_dir + '/calendar_dates/calendar_dates.txt', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	log('Copy calendar_dates.txt')
	log('Output: ' + output.stdout)
	log('Errors: ' + output.stderr)

	output = subprocess.run('git -C ' + target_dir + ' commit -am "Auto update calendar_dates"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	log('Commit calendar_dates.txt')
	log('Output: ' + output.stdout)
	log('Errors: ' + output.stderr)

	output = subprocess.run('git -C ' + target_dir + ' push', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	log('Push calendar_dates.txt')
	log('Output: ' + output.stdout)
	log('Errors: ' + output.stderr)
	
	log('End push to GitLab')
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
	if ftp_helper.connect_to_ftp(REMOTE_FTP_PATH, FTP_SERVER, FTP_USER, FTP_PW):
		if ftp_helper.get_file_from_ftp(CALENDAR_DATES_FILENAME, INPUT_WEEKLY_DIR):
			print('success')
			# weekly_data = list_helper.get_file_as_list(INPUT_WEEKLY_DIR + CALENDAR_DATES_FILENAME)
			
			# date_range = list_helper.get_date_range(weekly_data)

			# express_data = list_helper.get_file_as_list(INPUT_DIR + EXPRESS_FILENAME)
			# express_data = list_helper.get_in_date_range(express_data, date_range)

			# weekly_express_combined_data = list_helper.combine_list_data(weekly_data, express_data)
			
			# current_data = list_helper.get_url_as_list(REMOTE_CURRENT_PATH)
			# current_data = list_helper.remove_in_date_range(current_data, date_range)
			
			# result = list_helper.combine_list_data(current_data, weekly_express_combined_data)
			# list_helper.write_data_to_file(result, OUTPUT_DIR + CALENDAR_DATES_FILENAME)

			# push_to_gitlab()
			# update_rss()
		else:
			print('failure')
		ftp_helper.disconnect_from_ftp()
	
main()
