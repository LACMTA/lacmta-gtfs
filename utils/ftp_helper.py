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

ftp = ftplib.FTP(FTP_SERVER)
ftp.login(FTP_USER, FTP_PW)

def connect_to_ftp(remote_dir, local_dir):
	ftp.cwd(remote_dir)
	ftp.retrlines("LIST")
	os.chdir(local_dir)

def get_file_from_ftp(file):
	for filename in ftp.nlst(file): # Loop - looking for matching files
		if filename == file:
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