
def RSCREAD(rscfile, ignoredata=False):
	if type(rscfile) == file:
		pass
	elif type(rscfile) in (str, unicode):
		rscfile = open(rscfile, 'rb')

	rscfile.seek(0, 2)
	rscsize = rscfile.tell()
	rscfile.seek(0)

	files = []

	while rscfile.tell() < rscsize:
		file_size = 0
		file_name = ''
		file_data = ''

		rscfile.seek(18, 1)

		for size_index in xrange(4):
			file_size += ord(rscfile.read(1)) * (256 ** size_index)

		if rscfile.tell() + file_size >= rscsize:
			break

		while True:
			char = rscfile.read(1)
			if char == '\x00':
				rscfile.seek(-1, 1)
				break

			file_name += char

		rscfile.seek(1, 1)
		if ignoredata:
			rscfile.seek(file_size, 1)
		else:
			for data_index in xrange(file_size):
				file_data += rscfile.read(1)

		files.append((file_name, file_size, file_data))

	return files

