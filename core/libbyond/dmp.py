import re
import string


def split(line, split = ','):
	quote = '"'
	escape = '\\'
	brace = '('
	brace_close = ')'
	QUOTE = 1
	ESCAPE = 4
	open = 0
	braces = 0
	text = ''
	texts = []

	for index, char in enumerate(line):
		if char == quote and not open & ESCAPE:
			open ^= QUOTE
			text += quote

		elif char == brace and not open & ESCAPE and not open & QUOTE:
			braces += 1
			text += brace

		elif char == brace_close and not open & ESCAPE and not open & QUOTE:
			if braces:
				braces -= 1
			text += brace_close

		elif char == split:
			if open or braces:
				text += split
			else:
				texts.append(text)
				text = ''

		elif char != escape:
			if not len(text) and char in string.whitespace:
				pass
			else:
				text += char

		if open & ESCAPE:
			open ^= ESCAPE

		if char == escape:
			open |= ESCAPE
			text += escape

	if text:
		texts.append(text)

	return texts


class Map:
	def __init__(self):
		self.tiles = [] # 3d list of tiles z, y, x
		self.definitions = {} # dictionary of mapobj definitions

class DMPInstance(object):
	def __init__(self, type):
		self.type = type
		self.attributes = {}

	def setattr(self, attr, value):
		if not value:
			return

		if value[0] == '"' and value[-1] == '"':
			value = (value[1:-1], "string")

		elif value.startswith('list('):
			value = (split(value[5:-1], ','), "list")

		elif value.startswith('newlist('):
			value = (split(value[8:-1], ','), "newlist")

		else:
			try:
				value = (int(value), "int")
			except ValueError:
				value = (value, "other")

		self.attributes[attr] = value

	def __repr__(self):
		return self.type


def DMPREAD(dmp):
	dmppath = dmp
	dmp = open(dmp, 'r').read()

	dmp = dmp.split('\n')
	def_re = re.compile(r'"(.+)" = \((.*)\)')
	z_re = re.compile(r'\((\d),(\d),(\d)\) = \{\"')
	mapobj = Map()

	def get_instance_info(line):
		if not '{' in line or not '}' in line:
			return (line,)

		f, f2 = line.find('{') + 1, line.find('}')
		infos = split(line[f:f2], ';')
		for index, info in enumerate(infos):
			g = info.find(' = ')
			if g < 0: continue
			infos[index] = (info[:g], info[g+3:])
		return (line[:f-1], infos)

	end_definitions = 0

	# grab definitions
	for index, line in enumerate(dmp):
		if not line or line[0] != '"':
			end_definitions = index
			break

		match = def_re.search(line)

		mapobj.definitions[match.group(1)] = []

		for x in split(match.group(2), ','):
			info = get_instance_info(x)

			instance = DMPInstance(info[0])

			if len(info) > 1:
				for attr, value in info[1]:
					instance.setattr(attr, value)

			mapobj.definitions[match.group(1)].append(instance)

	# grab tiles
	start_index = -1
	current_z = -1

	try:
		def_len = len(mapobj.definitions.keys()[0])
	except IndexError:
		# empty map
		print '[DMP] Empty map `%s`' % dmppath
		return []

	y_list = []

	for index, line in enumerate(dmp):
		if index < end_definitions or line == '':
			continue

		new_z = z_re.search(line)

		if new_z:
			current_z = int(new_z.group(3))
			start_index = index
			continue

		elif line == '"}':
			y_list.reverse()
			mapobj.tiles.append(y_list)
			current_z = -1
			y_list = []
			continue

		x = []

		for char_n in xrange(0, len(line), def_len):
			chars = line[char_n : char_n + def_len]
			x.append(chars)

		y_list.append(x)

	return mapobj


def DMPWRITE(mapobj, dmp):
	if isinstance(dmp, str):
		dmp = open(dmp, 'w')

	def python_to_dm(value):
		if value[1] == 'list':
			return 'list(%s)' % (','.join(value[0]))

		if value[1] == 'newlist':
			return 'newlist(%s)' % (','.join(value[0]))

		if value[1] == 'string':
			return '"%s"' % value[0]

		if value[1] == 'int':
			return '%s' % value[0]

		if value[1] == 'other':
			return '%s' % value[0]

	def dosort(a, b):
		return cmp(b, a)

	definitions = mapobj.definitions.keys()
	definitions.sort(dosort)

	for x in definitions:
		dmp.write('"%s" = (' % x)
		for index, o in enumerate(mapobj.definitions[x]):
			if index:
				dmp.write(',')

			dmp.write(o.type)
			if len(o.attributes):
				dmp.write('{')
				dmp.write('; '.join('%s = %s' % (z, python_to_dm(o.attributes[z])) for z in o.attributes))
				dmp.write('}')
		dmp.write(')\n')
	dmp.write('\n')

	for z in xrange(len(mapobj.tiles)):
		dmp.write('(1,1,%i) = {"\n' % (z + 1))
		for y in xrange(len(mapobj.tiles[z])-1, -1, -1):
			for x in mapobj.tiles[z][y]:
				dmp.write(x)
			dmp.write('\n')
		dmp.write('"}\n\n')

	dmp.close()
