import os
import subprocess

def commit_and_push(message, directory):
	try:
		result = subprocess.run('git -C ' + directory + ' pull  --progress', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print('Output: ' + result.stdout)
		print('Errors: ' + result.stderr)
		
		result = subprocess.run('git -C ' + directory + ' commit -am "' + message + '"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print('Output: ' + result.stdout)
		print('Errors: ' + result.stderr)
		
		result = subprocess.run('git -C ' + directory + ' push  --progress', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print('Output: ' + result.stdout)
		print('Errors: ' + result.stderr)

		print('Committed and pushed: ' + directory)		
	except:
		print('Error committing and pushing: ' + directory)
		return
	return

def reset_temp_folder(directory):
	try:
		# can set to `output =`
		# subprocess.run('if [ -d ' + directory + ' ]; then rm -rf ' + directory + '; fi', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		result = subprocess.run('if [ -d ' + directory + ' ]; then rm -rf ' + directory + '; fi', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print('Output: ' + result.stdout)
		print('Errors: ' + result.stderr)

		# subprocess.run('mkdir ' + directory, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		result = subprocess.run('mkdir -p ' + directory, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print('Output: ' + result.stdout)
		print('Errors: ' + result.stderr)
		
		print('Reset temp folder: ' + directory)
	except:
		print('Temp folder: ' + directory + ' couldn\'t be reset')
	return

def clone_branch(url, branch, destination):
	try:
		reset_temp_folder(destination)

		# we only need a single branch at depth 1 (implies --single-branch)
		# subprocess.run('git -C ' + destination + ' clone --depth 1 --branch ' + branch + ' ' + url, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		result = subprocess.run('git -C ' + destination + ' clone --progress --depth 1 --branch ' + branch + ' ' + url, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print('Output: ' + result.stdout)
		print('Errors: ' + result.stderr)

		# configure git
		result = subprocess.run('git -C ' + destination + ' config user.email "kinn@metro.net"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print('Output: ' + result.stdout)
		print('Errors: ' + result.stderr)

		result = subprocess.run('git -C ' + destination + ' config user.name "Nina Kin"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print('Output: ' + result.stdout)
		print('Errors: ' + result.stderr)
		
		print('Branch "' + branch + '" cloned from ' + url + ' to ' + destination)
	except:
		print('Error cloning branch "' + branch + '" from ' + url + ' to ' + destination)
		raise Exception('Branch could not be cloned.')

	return

def push_to_gitlab():
	repo_dir = 'gtfs_bus'
	target_gitlab = 'LACMTA/gtfs_bus.git'

	target_dir = 'temp/' + repo_dir
	
	
	output = subprocess.run('cp data/calendar_dates.txt ' + target_dir + '/calendar_dates/calendar_dates.txt', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	# log('Copy calendar_dates.txt')
	# log('Output: ' + output.stdout)
	# log('Errors: ' + output.stderr)

	output = subprocess.run('git -C ' + target_dir + ' commit -am "Auto update calendar_dates"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	# log('Commit calendar_dates.txt')
	# log('Output: ' + output.stdout)
	# log('Errors: ' + output.stderr)

	output = subprocess.run('git -C ' + target_dir + ' push', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	# log('Push calendar_dates.txt')
	# log('Output: ' + output.stdout)
	# log('Errors: ' + output.stderr)
	
	# log('End push to GitLab')
	return
