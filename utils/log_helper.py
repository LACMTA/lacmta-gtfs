def build_log(flag):
	def print_msg(message):
		if flag:
			print(message)
	return print_msg