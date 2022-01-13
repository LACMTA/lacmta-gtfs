import datetime

# Format: YYYYMMDD
def convert_text_to_date(date_text):
	year = date_text[0:4]
	month = date_text[4:6]
	day = date_text[6:8]
	return datetime.date(int(year), int(month), int(day))
