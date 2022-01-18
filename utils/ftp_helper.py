import ftplib
import os

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

def get_file_from_ftp(file, local_dir):
	for filename in ftp_client.nlst(file): # Loop - looking for matching files
		if filename == file:
			fhandle = open(local_dir + filename, 'wb')
			print('Opening remote file: ' + filename) #for comfort sake, shows the file that's being retrieved
			transfer_result = ftp_client.retrbinary('RETR ' + filename, fhandle.write)
			fhandle.close()
			if '226' in transfer_result:
				print('Transfer complete: ' + local_dir + filename)
				return True
			else:
				print('Transfer failed')
				return False

def disconnect_from_ftp():
	ftp_client.quit()
	print("Disconnected from " + ftp_server)