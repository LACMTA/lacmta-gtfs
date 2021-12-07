import ftplib
import os
import re

USER = os.environ.get('FTP_USERNAME')
PASS = os.environ.get('FTP_PASS')
SERVER = os.environ.get('SERVER')
WORKSPACE = os.environ.get('GITHUB_WORKSPACE')
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
    the_file = ftp.retrbinary('RETR ' + filename, fhandle.write)
    fhandle.close()

push_to_github()
    
def push_to_github():
    os.system('git pull')
    os.system('git add .')
    os.system('git commit -m "Auto update"')
    os.system('git push')