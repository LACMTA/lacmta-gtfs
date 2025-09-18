import os
import subprocess

def print_outputs(results):
	for result in results:
		if (result):
			print(result)
	return


def commit_and_push(message, directory):
	try:
		print('--- Commit & push this directory: ' + directory)
		print('--- git pull')
		result = subprocess.run('git -C ' + directory + ' pull  --progress', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print_outputs([result.stdout, result.stderr])
		
		# configure git
		print('--- git config email')
		result = subprocess.run('git -C ' + directory + ' config user.email "matikin9@gmail.com"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print_outputs([result.stdout, result.stderr])

		print('--- git config name')
		result = subprocess.run('git -C ' + directory + ' config user.name "Nina Kin"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print_outputs([result.stdout, result.stderr])

		print('--- git add')
		result = subprocess.run('git -C ' + directory + ' add .', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print_outputs([result.stdout, result.stderr])

		print('--- git commit')
		result = subprocess.run('git -C ' + directory + ' commit -am "' + message + '"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print_outputs([result.stdout, result.stderr])
		
		print('--- git push')
		result = subprocess.run('git -C ' + directory + ' push  --progress', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print_outputs([result.stdout, result.stderr])

		if result.returncode != 0:
			print('Error: git push failed with return code ' + str(result.returncode))
		else:
			print('Committed and pushed: ' + directory)		
	except:
		print('Error committing and pushing: ' + directory)
		return
	return

def reset_temp_folder(directory):
	try:
		print('--- Reset this temp directory: ' + directory)

		print('--- rm directory')
		result = subprocess.run('if [ -d ' + directory + ' ]; then rm -rf ' + directory + '; fi', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print_outputs([result.stdout, result.stderr])

		print('--- mkdir directory')
		result = subprocess.run('mkdir -p ' + directory, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print_outputs([result.stdout, result.stderr])
		
		print('Reset temp folder: ' + directory)
	except:
		print('Temp folder: ' + directory + ' couldn\'t be reset')
	return

def clone_branch(url, branch, destination):
	try:
		reset_temp_folder(destination)

		# we only need a single branch at depth 1 (implies --single-branch)
		# subprocess.run('git -C ' + destination + ' clone --depth 1 --branch ' + branch + ' ' + url, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print('--- Clone the branch: ' + branch)

		print('--- git clone + ' + url)
		result = subprocess.run('git -C ' + destination + ' clone --depth 1 --branch ' + branch + ' ' + url, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		print_outputs([result.stdout, result.stderr])
		
		print('Branch "' + branch + '" cloned from ' + url + ' to ' + destination)
	except:
		print('Error cloning branch "' + branch + '" from ' + url + ' to ' + destination)
		raise Exception('Branch could not be cloned.')

	return
