import datetime

# Format: YYYYMMDD
def convert_text_to_date(date_text):
	year = date_text[0:4]
	month = date_text[4:6]
	day = date_text[6:8]
	return datetime.date(int(year), int(month), int(day))

def first_wednesday_before_date(date):
	while date.strftime('%A') != 'Wednesday':
		date = date + datetime.timedelta(days=-1)
	if date.strftime('%A') == 'Wednesday':
		return date

def is_in_date_range(date, range):
	if date >= range['start_date'] and date <= range['end_date']:
		return True
	else:
		return False