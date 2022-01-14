import ftplib
import os

RUNNING_LOCALLY = None
FTP_SERVER = None
FTP_USER = None
FTP_PW = None

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

if RUNNING_LOCALLY:
    FTP_SERVER = Config.SERVER
    FTP_USER = Config.USERNAME
    FTP_PW = Config.PASS

ftp_client = None

def connect_to_ftp(remote_dir):
	global ftp_client 
	
	ftp_client = ftplib.FTP(FTP_SERVER)
	login_result = ftp_client.login(FTP_USER, FTP_PW)
	
	if '230' in login_result:
		print("Connected to " + FTP_SERVER)
		ftp_client.cwd(remote_dir)
		print("Remote directory: " + ftp_client.pwd())
		return True
	else:
		print("Failed to connect to " + FTP_SERVER)
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
	print("Disconnected from " + FTP_SERVER)