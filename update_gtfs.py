import os
import datetime
import pytz
import PyRSS2Gen

import subprocess
import filecmp

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

# use local files for file comparison
CALENDAR_DATES_CURRENT_LOCAL = "temp/weekly-updated-service/gtfs_bus/calendar_dates.txt"
CALENDAR_DATES_SHAKEUP_LOCAL = "temp/master/gtfs_bus/calendar_dates.txt"

CALENDAR_DATES_CURRENT = "https://gitlab.com/LACMTA/gtfs_bus/-/raw/master/calendar_dates/calendar_dates.txt"
CALENDAR_DATES_EXPRESS = "../inputs/dse-sofi-express.csv"
CALENDAR_DATES_CURRENT_NEW = "current/calendar_dates.txt"

ROOT_DIR = os.getcwd()
CALENDAR_DATES_FILENAME = 'calendar_dates.txt'
EXPRESS_FILENAME = 'dse-sofi-express.csv'

REMOTE_FTP_PATH = '/nextbus/prod/'
REMOTE_CURRENT_PATH = 'https://gitlab.com/LACMTA/gtfs_bus/-/raw/master/calendar_dates/calendar_dates.txt'

OUTPUT_DIR = ROOT_DIR + '/data/'

INPUT_DIR = ROOT_DIR + '/inputs/'
INPUT_WEEKLY_DIR = 'temp/weekly/'

# change this to download the FTP file even if it doesn't match today's date
# MATCHING_DATE = datetime.date.today()
MATCHING_DATE = datetime.datetime(2022, 7, 6)

def update_rss(title, link, description):
	log("Now: " + str(datetime.datetime.now(pytz.timezone('US/Pacific'))))

	rss = PyRSS2Gen.RSS2(
		title = "LACMTA Bus GTFS Updates",
		link = "https://gitlab.com/LACMTA/gtfs_bus",
		description = "This RSS feed updates when the LA Metro Bus GTFS data is updated.",
		lastBuildDate = datetime.datetime.now(pytz.timezone('US/Pacific')),
		items = [
			PyRSS2Gen.RSSItem(
				title = title,
				link = link,
				description = description,
				pubDate = datetime.datetime.now(pytz.timezone('US/Pacific'))
			)])

	rss.write_xml(open(OUTPUT_DIR + "rss.xml", "w"))
	return

def has_new_calendar_dates(f1, f2):
	# may need a better way to do this
	# filecmp.cmp() returns TRUE if the files are the same (no shakeup)
	return not filecmp.cmp(f1, f2)

def copy_master_to_weekly_updated_service_branch():
	print('--- Copying master to weekly-updated-service branch')
	result = subprocess.run('cp -r temp/master/gtfs_bus/*.txt temp/weekly-updated-service/gtfs_bus/', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	print('Output: ' + result.stdout)
	print('Errors: ' + result.stderr)
	return

def add_calendar_dates_to_master():
	date = datetime.date.today()
	folder_name = str(date)
	new_folder = 'temp/master/gtfs_bus/calendar_dates/' + folder_name
	# copy calendar_dates.txt to master

	print('--- Making folder: ' + new_folder)
	result = subprocess.run('mkdir -p ' + new_folder, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	print('Output: ' + result.stdout)
	print('Errors: ' + result.stderr)

	print('--- Copying calendar_dates.txt to temp folder')
	result = subprocess.run('cp ' + 'temp/weekly/calendar_dates.txt ' + new_folder, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	print('Output: ' + result.stdout)
	print('Errors: ' + result.stderr)

	return

def zip_gtfs(directory):
	try:
		print('--- Removing zip file')
		result = subprocess.run('rm ' + directory + '*zip', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print('Output: ' + result.stdout)
		print('Errors: ' + result.stderr)

		print('--- Zipping ' + directory)
		result = subprocess.run('cd ' + directory + '; zip -r gtfs_bus *.txt', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print('Output: ' + result.stdout)
		print('Errors: ' + result.stderr)

		print('GTFS files zipped in: ' + directory)
	except:
		print('failed to zip GTFS files')
	return

def main():
	# check if there is a new calendar_dates.txt file on the FTP server
	if ftp_helper.connect_to_ftp(REMOTE_FTP_PATH, FTP_SERVER, FTP_USER, FTP_PW):
		if ftp_helper.get_file_from_ftp(CALENDAR_DATES_FILENAME, INPUT_WEEKLY_DIR, MATCHING_DATE):
			print('FTP file - success')
			gitlab_url = 'https://oauth2:' + GITLAB_TOKEN + '@gitlab.com/LACMTA/gtfs_bus.git'
			starting_calendar_dates_file = ''

			# cloning takes a while to run because we have some large files.

			# clone [master] branch
			git_helper.clone_branch(gitlab_url, 'master','temp/master')

			# clone [weekly-updated-service] branch
			git_helper.clone_branch(gitlab_url, 'weekly-updated-service','temp/weekly-updated-service')

			# copy the GTFS files from the [master] branch into the [weekly-updated-service] branch
			# need a way to recognize when to completely replace calendar_dates.txt vs using the existing one from the [weekly-updated-service] branch

			copy_master_to_weekly_updated_service_branch()
			starting_calendar_dates_file = 'temp/weekly-updated-service/gtfs_bus/calendar_dates.txt'

			# OLD FAULTY IMPLEMENTATION:
			# check if a new calendar_dates.txt has been released as part of the base GTFS and set the starting calendar_dates.txt file accordingly
			# if has_new_calendar_dates(CALENDAR_DATES_SHAKEUP_LOCAL, CALENDAR_DATES_CURRENT_LOCAL):
			# 	print('New base calendar_dates.txt exists')

			# 	# clear out `calendar_dates/` folder contents from [master] branch
			# 	calendar_dates_folder = 'temp/master/gtfs_bus/calendar_dates'
			# 	subprocess.run('if [ -d ' + calendar_dates_folder + ' ]; then rm -rf ' + calendar_dates_folder + '; fi', shell=True)
			# 	# subprocess.run('mkdir -p ' + calendar_dates_folder, shell=True)
			# 	# print('New master branch folder created')

			# 	starting_calendar_dates_file = 'temp/master/gtfs_bus/calendar_dates.txt'
			# 	# print('Starting folder set to master branch')
			# else:
			# 	print('No new base calendar_dates.txt exists')
			# 	starting_calendar_dates_file = 'temp/weekly-updated-service/gtfs_bus/calendar_dates.txt'
			# 	print('Starting folder set to weekly-updated-service branch')
				

			add_calendar_dates_to_master()
			weekly_data = list_helper.get_file_as_list(INPUT_WEEKLY_DIR + CALENDAR_DATES_FILENAME)
			current_data = list_helper.get_file_as_list(starting_calendar_dates_file)

			# check if the new calendar_dates.txt file is empty
			if len(weekly_data) <= 1:
				print('New calendar_dates.txt file is empty')

				express_data = list_helper.get_file_as_list(INPUT_DIR + EXPRESS_FILENAME)
				print('Express entries: ' + str(len(express_data)))
			else:
				print('New calendar_dates.txt file is not empty')
				print('Weekly entries: ' + str(len(weekly_data)))
				
				# don't need this if we just use the entire express_data file
				# date_range = list_helper.get_date_range(weekly_data)

				express_data = list_helper.get_file_as_list(INPUT_DIR + EXPRESS_FILENAME)

				# don't need this if we just use the entire express_data file
				# express_data = list_helper.get_in_date_range(express_data, date_range)

				current_data = list_helper.remove_in_date_range(current_data, date_range)

			weekly_express_combined_data = list_helper.combine_list_data(weekly_data, express_data)
			
			result = list_helper.combine_list_data(current_data, weekly_express_combined_data)
			result = list_helper.sort_list(result)
			list_helper.write_data_to_file(result, 'temp/weekly-updated-service/gtfs_bus/calendar_dates.txt')
			
			zip_gtfs('temp/weekly-updated-service/gtfs_bus/')

			git_helper.commit_and_push(str(datetime.datetime.now()) + ' weekly update', 'temp/weekly-updated-service/gtfs_bus/')
			
			# Not sure if we actually want to keep udpating the master branch
			# git_helper.commit_and_push(str(datetime.date.today()) + ' weekly update', 'temp/master/gtfs_bus/')

			update_rss("Weekly Updated GTFS", "https://gitlab.com/LACMTA/gtfs_bus/-/raw/weekly-updated-service/gtfs_bus.zip", "A new GTFS zip file for LA Metro's bus service has been uploaded with this week's new calendar_dates.txt file. The calendar_dates.txt file contains updated service for the upcoming 2 weeks.")
		else:
			print('FTP file - failure')
		
		ftp_helper.disconnect_from_ftp()
	
main()
