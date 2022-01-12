import ftplib
import os
import re
import datetime
import csv
from typing import Dict
import pytz
import PyRSS2Gen

# for running locally (comment out for production)
# from import Config

WORKSPACE = os.environ.get('GITHUB_WORKSPACE')
CALENDAR_DATES_FILE = "calendar_dates.txt"

REMOTEPATH = '/nextbus/prod/'
directory = REMOTEPATH

# for production
USER = os.environ.get('FTP_USERNAME')
PASS = os.environ.get('FTP_PASS')
SERVER = os.environ.get('SERVER')
ftp = ftplib.FTP(SERVER)
ftp.login(USER, PASS)

# for running locally (comment out for production)
# ftp = ftplib.FTP(Config.SERVER)
# ftp.login(Config.USERNAME, Config.PASS)


ftp.cwd(directory)
ftp.retrlines("LIST")
os.chdir("data/")


def convert_text_to_date(date_text):
	year = date_text[0:4]
	month = date_text[4:6]
	day = date_text[6:8]
	return datetime.date(int(year), int(month), int(day))

def compare_line_to_date(line, date_range):
	if line == '':
		return line
	else:
		line_date = line.split(',')[1]
		line_date = convert_text_to_date(line_date)
		if line_date >= date_range['start_date'] and line_date <= date_range['end_date']:
			return line
		else:
			return None

def shift_time_to_wednesday(date):
	while date.strftime('%A') != 'Wednesday':
		date = date + datetime.timedelta(days=-1)
	if date.strftime('%A') == 'Wednesday':
		return date

def get_start_and_end_dates():
	start_date = ''
	
	with open(CALENDAR_DATES_FILE, 'r') as file_with_dates:
		next(file_with_dates, None) # skip the header
		lines = file_with_dates.readlines()
		print(lines)

		for line in lines:
			row = line.split(',')
			row_date = convert_text_to_date(row[1])

			if start_date == '':
				start_date = row_date
			if row_date < start_date:
				start_date = row_date
			print('row_date: ' + str(row_date))
		print('start_date: ' + str(start_date))
		if start_date.strftime('%A') != 'Wednesday':
			print('not a Wednesday')
			start_date = shift_time_to_wednesday(start_date)

	start_end_date = {"start_date": start_date, "end_date": start_date + datetime.timedelta(weeks=2)}
	return start_end_date

def add_extra_lines(date_range):
	with open(CALENDAR_DATES_FILE, 'a') as resulting_file:
		with open('../inputs/dse-sofi-express.csv', 'r') as f:
			print(resulting_file)
			lines = f.readlines()
			for line in lines:
				if (compare_line_to_date(line, date_range)):
					resulting_file.write(line)
	return


def get_file_from_ftp():
	for filename in ftp.nlst(CALENDAR_DATES_FILE): # Loop - looking for matching files
		if filename == CALENDAR_DATES_FILE:
			print("Found file: " + filename)
			fhandle = open(filename, 'wb')
			print('Opening Remote file: ' + filename) #for comfort sake, shows the file that's being retrieved
			transfer_result = ftp.retrbinary('RETR ' + filename, fhandle.write)
			fhandle.close()
			if transfer_result == '226 Transfer complete.':
				print('Transfer complete')
				return True
			else:
				print('Transfer failed')
				return False


def push_to_github():
	os.system('git pull')
	os.system('git add .')
	os.system('git commit -m "Auto update"')
	os.system('git push')

def update_rss():
	rss = PyRSS2Gen.RSS2(
		title = "LACMTA Bus GTFS Updates",
		link = "https://gitlab.com/LACMTA/gtfs_bus",
		description = "This RSS feed updates when the LA Metro Bus GTFS data is updated.",
		lastBuildDate = datetime.datetime.now(),
		items = [
			PyRSS2Gen.RSSItem(
				title = "Weekly calendar_dates.txt update",
				link = "https://gitlab.com/LACMTA/gtfs_bus",
				description = "The weekly calendar_dates.txt file has been updated.",
				pubDate = datetime.datetime.now()
			)])

	rss.write_xml(open("rss.xml", "w"))

def main():
	if get_file_from_ftp():
		date_range = get_start_and_end_dates()
		add_extra_lines(date_range)
		print(date_range)
	update_rss()

main()

# add_extra_lines()

# push_to_github()
