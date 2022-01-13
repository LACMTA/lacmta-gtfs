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

# for running locally (comment out for production)
# from import Config

WORKSPACE = os.environ.get('GITHUB_WORKSPACE')
CALENDAR_DATES_WEEKLY = "calendar_dates.txt"
CALENDAR_DATES_SHAKEUP = "https://gitlab.com/LACMTA/gtfs_bus/-/raw/master/calendar_dates.txt"
CALENDAR_DATES_EXPRESS = "../inputs/dse-sofi-express.csv"

REMOTEPATH = '/nextbus/prod/'
directory = REMOTEPATH

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

def shift_date_to_wednesday(date):
	while date.strftime('%A') != 'Wednesday':
		date = date + datetime.timedelta(days=-1)
	if date.strftime('%A') == 'Wednesday':
		return date

def get_start_and_end_dates():
	start_date = ''
	
	with open(CALENDAR_DATES_WEEKLY, 'r') as file_with_dates:
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
			start_date = shift_date_to_wednesday(start_date)

	start_end_date = {"start_date": start_date, "end_date": start_date + datetime.timedelta(weeks=2)}
	return start_end_date

def add_extra_lines(date_range):
	with open(CALENDAR_DATES_WEEKLY, 'a') as resulting_file:
		with open(CALENDAR_DATES_EXPRESS, 'r') as f:
			print(resulting_file)
			lines = f.readlines()
			for line in lines:
				if (compare_line_to_date(line, date_range)):
					resulting_file.write(line)
	return

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

def get_shakeup_calendar_dates(url):
	response = requests.get(url)
	csv_response = csv.reader(response.text.splitlines())
	return csv_response

def update_shakeup_calendar_dates(data, date_range):
	# loop through `data` and check the dates, removing any that are in the date range

	result_csv = []
	next(data)
	count = 0 
	for row in data:
		if convert_text_to_date(row[1]) >= date_range['start_date'] and convert_text_to_date(row[1]) <= date_range['end_date']:
			# print("this row was removed: "+str(row))
			count += 1
			continue
		else:
			result_csv.append(row)
	print("removed "+str(count)+" lines")
	#print(result_csv)
	return

def main():
	connect_to_ftp(directory, "data/")
	if get_file_from_ftp(CALENDAR_DATES_WEEKLY):
		date_range = get_start_and_end_dates()
		add_extra_lines(date_range)
		print(date_range)
	shakeup_data = get_shakeup_calendar_dates(CALENDAR_DATES_SHAKEUP)
	update_shakeup_calendar_dates(shakeup_data, date_range)
	update_rss()

main()

# add_extra_lines()

# push_to_github()
