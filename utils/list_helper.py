import datetime
import requests
import csv
import utils.date_helper as date_helper
import utils.log_helper as log_helper

log = log_helper.build_log(True)

def get_date_range(list_data):
	start_date = ''
	
	for row in list_data:
		if (row[1] == 'date'):
			continue
		row_date = date_helper.convert_text_to_date(row[1])
		if start_date == '' or row_date < start_date:
			start_date = row_date
	
	if start_date.strftime('%A') != 'Wednesday':
		start_date = date_helper.first_wednesday_before_date(start_date)
	
	start_end_date = {
		'start_date': start_date,
		'end_date': start_date + datetime.timedelta(weeks=2)
	}
	return start_end_date

def get_in_date_range(list_data, data_range):
	result_data = []
	count = 0 
	for row in list_data:
		if (row[1] == 'date'):
			continue
		row_date = date_helper.convert_text_to_date(row[1])
		if date_helper.is_in_date_range(row_date, data_range):
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
		row_date = date_helper.convert_text_to_date(row[1])

		if date_helper.is_in_date_range(row_date, date_range):
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