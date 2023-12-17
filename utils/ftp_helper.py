import ftplib
from dateutil import parser
import os
import datetime
import subprocess

ftp_client = None
ftp_server = ''

def connect_to_ftp(remote_dir, server, user, pw):
	global ftp_client 
	global ftp_server
	ftp_server = server
	
	ftp_client = ftplib.FTP(server)
	login_result = ftp_client.login(user, pw)
	
	if '230' in login_result:
		print("Connected to " + server)
		ftp_client.cwd(remote_dir)
		print("Remote directory: " + ftp_client.pwd())
		return True
	else:
		print("Failed to connect to " + server)
		return False
	#ftp.retrlines("LIST")

def get_file_from_ftp(file, local_dir, match_date=datetime.date.today()):
	for filename in ftp_client.nlst(file): # Loop - looking for matching files
		if filename == file:
			timestamp = ftp_client.voidcmd("MDTM " + filename)[4:].strip()
			time = parser.parse(timestamp)
			print("FTP file date: " + str(time.date()))
			print("Current date: " + str(datetime.date.today()))
			print("match_date: " + str(match_date))

			# Only download the file if the modified date is today.
			# Comment out this line for manual runs and run the code in side the block
# 			if(time.date() == match_date):

			# RE-INDENT WHEN DONE
			print("Found file modified: " + str(time.date()))

			subprocess.run(f'if [ -d {local_dir} ]; then rm -rf {local_dir}; fi', shell=True)
			subprocess.run(f'mkdir -p {local_dir}', shell=True)

			filepath = f'{local_dir}/{filename}'

			fhandle = open(filepath, 'wb')
			print(f'Opening remote file: {filename}') # for comfort sake, shows the file that's being retrieved
			transfer_result = ftp_client.retrbinary(f'RETR {filename}', fhandle.write)
			fhandle.close()
			if '226' in transfer_result:
				print(f'Transfer complete: {filepath}')
				return True
			else:
				print('Transfer failed')
				return False
# 			else:
# 				print("File modified " + str(time.date()) + " does not match_date: " + str(match_date))
		else:
			print("File " + filename + " does not match " + file)
	return False

def disconnect_from_ftp():
	ftp_client.quit()
	print("Disconnected from " + ftp_server)
