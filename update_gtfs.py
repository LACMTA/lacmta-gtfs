import ftplib
import os
import re

USER = os.environ.get('FTP_USERNAME')
PASS = os.environ.get('FTP_PASS')
SERVER = os.environ.get('SERVER')
print(SERVER)
REMOTEPATH = '/nextbus/prod/'

ftp = ftplib.FTP(SERVER)
ftp.login(USER, PASS)

directory = REMOTEPATH
filematch = '*.txt'
ftp.cwd(directory)
ftp.retrlines("LIST")
os.chdir("data/")

for filename in ftp.nlst(filematch): # Loop - looking for matching files
    fhandle = open(filename, 'wb')
    print('Getting ' + filename) #for confort sake, shows the file that's being retrieved
    ftp.retrbinary('RETR ' + filename, fhandle.write)
    fhandle.close()