'''
AUTHOR:
  Created by Crashed on Feb 07 2009.


USAGE:
  DMIREAD(path)
	returns a list of Icons retrieved from the DMI

  DMIWRITE(icons[], path)
	given a list of Icons, this method will save the data to a dmi you specify (path)

  Icon
	How to get images from the icon:
	  Icon.icons is a map of all the images the icon holds.
	  Icon.icons[DMI_WEST][3] - fourth frame in the west direction.
	  Images without multiple frames and directions are still grabbed the same:
		  Icon.icons[DMI_SOUTH][0]

	How to get delay for each frame:
	  Delays are stored in a list, Icon.delays.
	  If there are 5 frames, there are 5 delays.
	  [1, 1, 1, 1, 1] by default.


TODO:
  Assuming reading DMIs is working flawlessly, saving DMIs would be the next task. [x]
  Reading and writing appears to work great, so what's left to do is to find bugs. [ ]
'''


import Image
import re
import os
import sys
sys.path.insert(0, os.path.split(__file__)[0])
import math
import zlib
import thread
import subprocess
import PngImagePlugin
import traceback
import copy

optipng = os.getcwd()


DMI_SOUTH = 0
DMI_NORTH = 1
DMI_EAST = 2
DMI_WEST = 3
DMI_SOUTHEAST = 4
DMI_SOUTHWEST = 5
DMI_NORTHEAST = 6
DMI_NORTHWEST = 7


class Icon:
	# Each Icon holds the information for each icon in a DMI - which includes each dir and frame

	def __init__(self):
		self.state = '' #icon state
		self.dirs = 1   #number of dirs
		self.frames = 1 # number of frames
		self.icons = [] # contains all the icons for dirs and frames
		self.delays = [] # delay numbers, one for each frame
		self.loops = 0 # times to loop
		self.rewind = 0 # rewind flag
		self.movement = 0 # movement flag

	def __str__(self):
		return 'State: "%s", dirs: %i, frames: %i, icons: %i,\n  delays: %s, loops: %i, rewind: %i' % (self.state, self.dirs, self.frames, len(flatten_array(self.icons)),
																																			  self.delays, self.loops, self.rewind)

	def copy(self, deep=True):
		icon = Icon()
		icon.state = self.state
		icon.dirs = self.dirs
		icon.frames = self.frames

		if not deep:
			# original and copied icon will share delay list and icon image objects
			# a change to one will change both
			icon.icons = self.icons
			icon.delays = self.delays
		else:
			icon.icons = [[]] * self.dirs
			for dir in xrange(self.dirs):
				icon.icons[dir] = [x.copy() for x in self.icons[dir]]
			icon.delays = copy.copy(self.delays)

		icon.loops = self.loops
		icon.rewind = self.rewind
		icon.movement = self.movement

		return icon


def DMIINFOREAD(path):
	# Return DMI metadata without cropping images

	try:
		try:
			states, (width, height) = DMIINFO(Image.open(path).info['Description'])
			return states, (width, height)

		except IOError:
			return None

		except KeyError:
			dmif = open(path, 'rb')
			if dmif.read(4).endswith('DMI'):
				print >> sys.stderr, '[DMIREAD] Failed to load icon `%s`\n\Unable to load DMI v3 icons.\n' % path
			return None

	except IOError:
		print >> sys.stderr, '[DMIREAD] File `%s` non existant.' % path
		print >> sys.stderr, traceback.format_exc()

	except Exception:
		print >> sys.stderr, '[DMIREAD]', traceback.format_exc()

	return None


def DMIINFO(info):
	# Parses DMI information.

	icon_states = [] #[(name, dirs, frames), ]
	width = -1
	height = -1

	if len(info) < 11: return -1
	if info[0:11] != '# BEGIN DMI': return -2

	groups = re.findall('(.+) = (.+)', info)
	if not groups or not len(groups): return -3

	def split_delays(delay):
		# delays are saved as 1,2,1,1 - we want to split this into a list
		if not ',' in delay and str(int(delay)) == delay:
			return delay

		return [int(x) for x in delay.split(',')]

	for x in xrange(len(groups)):
		index, value = groups[x]
		if index == 'version':
			if value != '4.0':
				return -4

			if groups[x + 1][0] == '\twidth':
				x += 1
				width = int(groups[x][1])

			if groups[x + 1][0] == '\theight':
				x += 1
				height = int(groups[x][1])

		if index == 'state':
			try:
				state = unicode(value, 'utf-8')
			except:
				value
			x += 1
			dirs = int(groups[x][1])
			x += 1
			frames = int(groups[x][1])
			delays = [1]
			if len(groups) > x + 1 and groups[x + 1][0] == '\tdelay':
				x += 1
				delays = split_delays(groups[x][1])
			loops = 0
			if len(groups) > x + 1 and groups[x + 1][0] == '\tloop':
				x += 1
				loops = int(groups[x][1])
			rewind = 0
			if len(groups) > x + 1 and groups[x + 1][0] == '\trewind':
				x += 1
				rewind = int(groups[x][1])
			movement = 0
			if len(groups) > x + 1 and groups[x + 1][0] == '\tmovement':
				x += 1
				movement = int(groups[x][1])

			icon_states.append( (state, dirs, frames, delays, rewind, loops, movement) )

	return icon_states, (width, height)


def DMIREAD(path):
	# Takes a path to a dmi file and splits it up into multiple Icon objects

	def DMIICON(dmi, width=-1, height=-1):
		# Splits up the DMI/PNG into multiple bitmaps.

		dmis = []

		if width < 0 or height < 0:
			width, height = dmi.size[1], dmi.size[1]

		for x in xrange(0, dmi.size[0], width):
			dmis.append(dmi.crop((x, 0, x + width, height)))

		return dmis

	try:
		print 'DMIREAD:', os.path.split(path)[-1]
		try:
			dmi = Image.open(path).convert('RGBA')
			#print dmi.info['Description']
			states, (width, height) = DMIINFO(dmi.info['Description'])

			if width == -1:
				frames = 0
				for state in states:
					frames += state[1] * state[2]
				width = dmi.size[0] / frames
			if height == -1:
				height = dmi.size[1]

			dmis = DMIICON(dmi, width, height)
			if type(states) == int:
				return []

		except IOError:
			return []

		except KeyError:
			dmif = open(path, 'rb')
			if dmif.read(4).endswith('DMI'):
				print >> sys.stderr, '[DMIREAD] Failed to load icon `%s`\n\Unable to load DMI v3 icons.\n' % path
			else:
				dmi = Image.open(path).convert('RGBA')
				icon = Icon()
				icon.icons = [[dmi]]
				icon.state = ''
				icon.dirs = 1
				return [icon]
			return []

		icons = []

		dmi_counter = 0
		if states != -1:
			for index in xrange(len(states)):
				image = dmis[dmi_counter]
				state = states[index]

				icon = Icon()
				icon.icons = [[image]]
				icon.state = state[0][1:-1]
				icon.dirs = state[1]
				icon.frames = state[2]
				icon.delays = state[3]
				icon.rewind = state[4]
				icon.loops = state[5]
				icon.movement = state[6]

				if icon.dirs > 1:
					for x in xrange(1, icon.dirs):
						dmi_counter += 1
						image = dmis[dmi_counter]
						icon.icons.append([image])

				if icon.frames > 1:
					for x in xrange(0, icon.frames - 1):
						for y in xrange(0, icon.dirs):
							dmi_counter += 1
							image = dmis[dmi_counter]
							icon.icons[y].append(image)

				icons.append(icon)

				dmi_counter += 1

		return icons

	except IOError:
		print >> sys.stderr, '[DMIREAD] File `%s` non existant.' % path
		print >> sys.stderr, traceback.format_exc()

	except Exception:
		print >> sys.stderr, '[DMIREAD]', traceback.format_exc()

	return []


def DMIWRITE(icons, path=None, crush=None):
	# Saves a list of icons to a DMI.

	MAX_WIDTH = 40000 # very important, the maximum allowed width for the generated png
					  # PIL doesn't like large widths

	def DMIICON(icons):
		# Takes a list of icons and flattens them to a long bitmap strip

		if not len(icons): return -1

		frames = []
		for icon in icons:
			for y in xrange(icon.frames):
				for x in xrange(icon.dirs):
					frames.append(icon.icons[x][y])

		width, height = icons[0].icons[0][0].size # size of frames

		'''
		icons_per_row = math.ceil(math.sqrt(len(frames)))
		png_width = icons_per_row * size

		bitmap = Image.new('RGBA', (png_width, png_width))

		for index, icon in enumerate(frames):
			pos_x = index
			pos_y = 0

			while pos_x > icons_per_row:
				pos_x -= icons_per_row + 1
				pos_y += 1

			bitmap.paste(icon, (pos_x * size, pos_y * size))
		'''

		bitmap = Image.new('RGBA', (len(frames) * width, height))

		for index, icon in enumerate(frames):
			bitmap.paste(icon, (index * width, 0))

		return bitmap

	def DMIINFO(icons):
		# Format the icons information in standard DMI metadata format

		if not len(icons): return -1

		metadata = '# BEGIN DMI'
		metadata += '\nversion=4.0'
		for icon in icons:
			metadata += '\nstate = "%s"' % icon.state
			metadata += '\n\tdirs = %i' % icon.dirs
			metadata += '\n\tframes = %i' % icon.frames

			# only write the next values if they're not the default values, keep the size of the file down
			if icon.delays != [1]:
				metadata += '\n\tdelay = %s' % (','.join([str(x) for x in icon.delays]))
			if icon.loops != 0:
				metadata += '\n\tloop = %i' % icon.loops
			if icon.rewind != 0:
				metadata += '\n\trewind = %i' % icon.rewind
			if icon.movement != 0:
				metadata += '\n\tmovement = %i' % icon.movement
		metadata += '\n# END DMI'

		return metadata

	def pngsave(im, file):
		# Borrowed from: http://blog.modp.com/2007/08/python-pil-and-png-metadata-take-2.html - thanks! :)

		# these can be automatically added to Image.info dict
		# they are not user-added metadata
		reserved = ('interlace', 'gamma', 'dpi', 'transparency', 'aspect')

		# undocumented class
		meta = PngImagePlugin.PngInfo()

		# copy metadata into new object
		for k,v in im.info.iteritems():
			if k in reserved: continue
			meta.add_text(k, v, 1)

		# and save
		im.save(file, 'PNG', pnginfo=meta)

	image = DMIICON(icons)
	metadata = DMIINFO(icons)
	if type(image) == int and not len(icons):
		image = Image.new('RGBA', (1, 1))
		metadata = ''
	if path:
		image.info['Description'] = metadata
		pngsave(image, path)

		def optimize_optipng(path):
			curdir = os.getcwd()
			os.chdir(optipng)
			os.system('optipng.exe "%s" -out "%s"' % (path, path)) #-o1 -quiet -force
			os.chdir(curdir)

		if crush:
			thread.start_new_thread(optimize_optipng, (path,))

	else:
		return image, metadata


def flatten_array(lst):
	# cheap way to flatten all the elements in an array to a single list

	def count(lst):
		c = []
		for i in lst:
			if type(i) == list:
				c += count(i)
			else:
				c.append(i)
		return c

	return count(lst)
