import Image
import re



DMI_NORTH = 0
DMI_SOUTH = 1
DMI_EAST = 2
DMI_WEST = 3
DMI_SOUTHEAST = 4
DMI_SOUTHWEST = 5
DMI_NORTHEAST = 6
DMI_NORTHWEST = 7



class Icon:
    def __init__(self):
        self.state = '' #icon state
        self.dirs = 1   #number of dirs
        self.frames = 1 # number of frames
        self.icons = [] # contains all the icons for dirs and frames
        self.delays = [] # delay numbers, one for each frame


def DMIREAD(dmi):
    dmi = Image.open(dmi)
    print dmi.info['Description']

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


    for icon in icons:
        print 'Icon: state: "%s" || dirs: %i || frames: %i || delays: %s || icons: %i ||' % (icon.state, icon.dirs, icon.frames, icon.delays, counts(icon.icons))


def DMIICON(dmi):
    # Splits up the DMI/PNG into multiple images (wxBitmaps).

    dmis = []

    width, height = dmi.size

    for x in xrange(0, width, height):
        new = dmi.crop((x, 0, x + height, height))
        dmis.append(new)

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
            if len(groups) > x + 1:
                if groups[x + 1][0] == '\tdelay':
                    x += 1
                    delays = split_delays(groups[x][1])
            icon_states.append( (state, dirs, frames, delays) )

    return icon_states


def counts(lst):
    # cheap way to count all elements in a list, multiple lists deep

    def count(lst):
        c = 0
        for i in lst:
            if type(i) == list:
                c += count(i)
            else:
                c += 1
        return c

    return count(lst)


if __name__ == '__main__':
    DMIREAD('C:\\Documents and Settings\\CRASH\\Desktop\\test.dmi')