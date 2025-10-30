import os
import datetime
import pytz

import subprocess
import filecmp

from dotenv import load_dotenv

import utils.ftp_helper as ftp_helper
import utils.date_helper as date_helper
import utils.log_helper as log_helper
import utils.list_helper as list_helper
import utils.git_helper as git_helper

load_dotenv()

FTP_SERVER = os.environ.get('FTP_SERVER')
FTP_USER = os.environ.get('FTP_USER')
FTP_PW = os.environ.get('FTP_PW')
GITLAB_TOKEN = os.environ.get('GITLAB_TOKEN')

log = log_helper.build_log(True)

# FTP Info

REMOTE_FTP_PATH = '/nextbus/prod/'


# Path variables
GITLAB_REPO = 'gtfs_bus'
GITLAB_PATH = f'https://gitlab.com/LACMTA/{GITLAB_REPO}/'
GTFS_BUS_ZIP = 'gtfs_bus.zip'

TEMP_DIR_FTP = 'temp/ftp'
TEMP_DIR_MASTER = 'temp/master'
TEMP_DIR_WEEKLY_UPDATED_SERVICE = 'temp/weekly-updated-service'

CALENDAR_DATES_FILENAME = 'calendar_dates.txt'
EXPRESS_FILENAME = 'dse-sofi-express.csv'

def has_new_calendar_dates(f1, f2):
	# may need a better way to do this
	# filecmp.cmp() returns TRUE if the files are the same (no shakeup)
	return not filecmp.cmp(f1, f2)

def print_outputs(results):
	for result in results:
		if (result):
			print(result)
	return

def copy_master_to_weekly_updated_service():
	print('--- Unzip master branch gtfs_bus.zip file, overwriting existing files')
	result = subprocess.run(f'unzip -o {TEMP_DIR_MASTER}/{GITLAB_REPO}/{GTFS_BUS_ZIP} -d {TEMP_DIR_MASTER}/{GITLAB_REPO}/', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	print_outputs([result.stdout, result.stderr])

	print('--- Copying master to weekly-updated-service branch')
	result = subprocess.run(f'cp -r {TEMP_DIR_MASTER}/{GITLAB_REPO}/*.txt {TEMP_DIR_WEEKLY_UPDATED_SERVICE}/{GITLAB_REPO}/', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	print_outputs([result.stdout, result.stderr])

	print('--- Copy README.md file from master to weekly-updated-service branch')
	result = subprocess.run(f'cp {TEMP_DIR_MASTER}/{GITLAB_REPO}/README.md {TEMP_DIR_WEEKLY_UPDATED_SERVICE}/{GITLAB_REPO}/', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	print_outputs([result.stdout, result.stderr])
	return

def add_calendar_dates_to_master():
	date = datetime.date.today()
	folder_name = str(date)

	# Make new temp folder for calendar_dates.txt in master branch
	new_folder = f'{TEMP_DIR_MASTER}/{GITLAB_REPO}/calendar_dates/{folder_name}'
	# copy calendar_dates.txt to master

	print('--- Make new folder in master branch and copy from temp FTP folder')
	result = subprocess.run(f'''
						 mkdir -p {new_folder};
						 cp {TEMP_DIR_FTP}/calendar_dates.txt {new_folder}
						''', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	result = subprocess.run(f'mkdir -p {new_folder}; cp {TEMP_DIR_FTP}/calendar_dates.txt {new_folder}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	print_outputs([result.stdout, result.stderr])

	return

def zip_gtfs(directory):
	try:
		print('--- Removing old zip file and creating a new one')
		result = subprocess.run(f'''
						  rm {directory}*zip;
						  cd {directory};
						  zip -r gtfs_bus *.txt
						  ''', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print_outputs([result.stdout, result.stderr])

		print(f'GTFS files zipped in: {directory}')
	except:
		print('failed to zip GTFS files')
	return

def remove_txt_files(directory):
	try:
		print(f'--- Removing txt files from {directory}')
		result = subprocess.run(f'rm {directory}*.txt', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print_outputs([result.stdout, result.stderr])
	except:
		print('failed to remove txt files')
	return

def main():
	# check if there is a calendar_dates.txt file on the FTP server
	if ftp_helper.connect_to_ftp(REMOTE_FTP_PATH, FTP_SERVER, FTP_USER, FTP_PW):
		# download the calendar_dates.txt file from the FTP server
		# into the 'temp/ftp/' directory
		if ftp_helper.get_file_from_ftp(CALENDAR_DATES_FILENAME, TEMP_DIR_FTP):
			print('FTP file downloaded successfully')
			gitlab_url = 'https://oauth2:' + GITLAB_TOKEN + '@gitlab.com/LACMTA/gtfs_bus.git'

			# clone [master] branch into temp/master directory
			git_helper.clone_branch(gitlab_url, 'master', TEMP_DIR_MASTER)

			# clone [weekly-updated-service] branch into temp/weekly-updated-service directory
			git_helper.clone_branch(gitlab_url, 'weekly-updated-service', TEMP_DIR_WEEKLY_UPDATED_SERVICE)

			# copy the files from the temp master directory into the temp weekly-updated-service directory
			copy_master_to_weekly_updated_service()
			
			# get the current calendar_dates.txt file as a list
			old_weekly_calendar_dates = f'{TEMP_DIR_WEEKLY_UPDATED_SERVICE}/{GITLAB_REPO}/calendar_dates.txt'
			old_data = list_helper.get_file_as_list(old_weekly_calendar_dates)

			# not sure if this is actually needed
			# add_calendar_dates_to_master()
			
			# get the new calendar_dates.txt file as a list
			new_data = list_helper.get_file_as_list(f'{TEMP_DIR_FTP}/{CALENDAR_DATES_FILENAME}')

			# check if the new calendar_dates.txt file is empty
			if len(new_data) <= 1:
				print('New calendar_dates.txt file is empty')
			else:
				print(f'New calendar_dates.txt file is not empty. Length: {str(len(new_data))}')

			# get the express data as a list
			# express_data = list_helper.get_file_as_list(INPUT_DIR + EXPRESS_FILENAME)
			# print(f'Length of Express entries: {str(len(express_data))}')

			# combine the new calendar_dates.txt file with the express data
			# weekly_express_combined_data = list_helper.combine_list_data(new_data, express_data)
			
			# for now, just use the new calendar_dates.txt file. The GTFS was provided with the DSE data already included.
			weekly_express_combined_data = new_data
			
			# combine the old calendar_dates.txt file with the newly combined data 
			result = list_helper.combine_list_data(old_data, weekly_express_combined_data)
			result = list_helper.sort_list(result)

			# remove duplicate lines
			result = list_helper.remove_duplicates(result)

			# write the final combined results to the temp weekly-updated-service directory
			list_helper.write_data_to_file(result, f'{TEMP_DIR_WEEKLY_UPDATED_SERVICE}/{GITLAB_REPO}/calendar_dates.txt')
			
			zip_gtfs(f'{TEMP_DIR_WEEKLY_UPDATED_SERVICE}/{GITLAB_REPO}/')

			remove_txt_files(f'{TEMP_DIR_WEEKLY_UPDATED_SERVICE}/{GITLAB_REPO}/')

			git_helper.commit_and_push(str(datetime.datetime.now()) + ' weekly update', f'{TEMP_DIR_WEEKLY_UPDATED_SERVICE}/{GITLAB_REPO}/')
			
			# Not sure if we actually want to keep udpating the master branch
			# git_helper.commit_and_push(str(datetime.date.today()) + ' weekly update', 'temp/master/gtfs_bus/')

		else:
			print('FTP file - failure')
		
		ftp_helper.disconnect_from_ftp()
	
main()
