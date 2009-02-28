#!/usr/bin/env python

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
import sys


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

    def __str__(self):
        return 'State: "%s", dirs: %i, frames: %i, icons: %i,\n  delays: %s, loops: %i, rewind: %i' % (self.state, self.dirs, self.frames, len(flatten_array(self.icons)),
                                                                                                                                              self.delays, self.loops, self.rewind)

    def populate(self):
        # call this if you manually change the dirs or frames num

        while self.dirs > len(self.icons):
            self.icons.append([])

        for dir in xrange(self.dirs):
            while self.frames > len(self.icons[dir]):
                self.icons[dir].append(Image.new('RGBA', (32, 32)))

        while self.frames > len(self.delays):
            self.delays.append(1)


def DMIREAD(path):
    # Takes a path to a dmi file and splits it up into multiple Icon objects

    def DMIICON(dmi):
        # Splits up the DMI/PNG into multiple bitmaps.

        dmis = []

        width, height = dmi.size

        for x in xrange(0, width, height):
            dmis.append(dmi.crop((x, 0, x + height, height)))

        return dmis

    def DMIINFO(info):
        # Parses DMI information.

        icon_states = [] #[(name, dirs, frames), ]

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
            if index == 'version' and value != '4.0': return -4

            if index == 'state':
                state = value
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

                icon_states.append( (state, dirs, frames, delays, rewind, loops) )

        return icon_states

    try:
        dmi = Image.open(path)

        dmis = DMIICON(dmi)
        states = DMIINFO(dmi.info['Description'])
        icons = []

        dmi_counter = 0

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
        print >> sys.stderr, 'File `%s` non existant.' % path

    except Exception, e:
        print >> sys.stderr, 'Unknown exception occured. \n %s' % e

    return []


def DMIWRITE(icons, path):
    # Saves a list of icons to a DMI.

    def DMIICON(icons):
        # Takes a list of icons and flattens them to a long bitmap strip

        if not len(icons): return -1

        frames = []
        for icon in icons:
            for y in xrange(icon.frames):
                for x in xrange(icon.dirs):
                    frames.append(icon.icons[x][y])

        size = icons[0].icons[0][0].size[1]
        bitmap = Image.new('RGBA', (len(frames) * size, size))

        for index, icon in enumerate(frames):
            bitmap.paste(icon, (index * size, 0))

        return bitmap

    def DMIINFO(icons):
        # Format the icons informatoin in standard DMI metadata format

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
        metadata += '\n# END DMI'

        return metadata

    def pngsave(im, file):
        # Borrowed from: http://blog.modp.com/2007/08/python-pil-and-png-metadata-take-2.html - thanks! :)

        # these can be automatically added to Image.info dict                                                                              
        # they are not user-added metadata
        reserved = ('interlace', 'gamma', 'dpi', 'transparency', 'aspect')

        # undocumented class
        from PIL import PngImagePlugin
        meta = PngImagePlugin.PngInfo()

        # copy metadata into new object
        for k,v in im.info.iteritems():
            if k in reserved: continue
            meta.add_text(k, v, 0)

        # and save
        im.save(file, 'PNG', pnginfo=meta, optimize=1)

    image = DMIICON(icons)
    metadata = DMIINFO(icons)
    image.info['Description'] = metadata
    pngsave(image, path)


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


if __name__ == '__main__':
    icons = DMIREAD('C:\\Documents and Settings\\CRASH\\Desktop\\turfs.dmi')

    for icon in icons:
        print icon

    DMIWRITE(icons, 'C:\\Documents and Settings\\CRASH\\Desktop\\turfs2.dmi')