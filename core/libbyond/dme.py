import core
from core import *

import os
import re
import sys


preprocessors = ['#define', '#if', '#elif', '#ifdef', '#ifndef', '#else', '#else', '#endif', '#include', '#error']


class DME:
    def __init__(self):
        self.internals = []
        self.file_dirs = []
        self.preferences = []
        self.includes = []
        self.path = None
        self.dir = None

        self.files = []

    def read(self, path):
        self.internals, self.file_dirs, self.preferences, self.includes = DMEREAD(path)
        self.path = os.path.abspath(path)
        self.dir = os.path.split(self.path)[0]

    def save(self):
        DMEWRITE(self.internals, self.file_dirs, self.preferences, self.includes, self.path)

    def get_files(self):
        for type, dir in self.file_dirs:
            absdir = os.path.abspath(os.path.join(self.dir, dir))

            for file in os.listdir(absdir):
                absfile = os.path.join(absdir, file)

                if os.path.isfile(absfile):
                    self.files.append(absfile)

        for type, file in self.includes:
            self.files.append(os.path.abspath(os.path.join(self.dir, file)))

    def get_file_path(self, name, case=False):
        path = None

        if not case:
            name = name.lower()

        for file in self.files:
            if case:
                if file.endswith(name):
                    path = file
            else:
                if file.lower().endswith(name):
                    path = file

        return path


def DMEREAD(dme):
    internals = []
    file_dirs = []
    preferences = []
    includes = []

    if isinstance(dme, str) or isinstance(dme, unicode):
        dme = open(dme)

    #print dme

    for line in dme:
        if line.startswith('// INTERNALS'):
            for line in dme:
                if line.startswith('// END_INTERNALS'):
                    break

                internals.append(('RAW', line))

        elif line.startswith('// BEGIN_INTERNALS'):
            for line in dme:
                if line.startswith('// END_INTERNALS'):
                    break

        elif line.startswith('// BEGIN_FILE_DIR'):
            for line in dme:
                if line.startswith('// END_FILE_DIR'):
                    break

                if line.startswith('#define '):
                    match = re.match('#define FILE_DIR (\.)', line)
                    if not match:
                        match = re.match('#define FILE_DIR "(.*)"', line)

                    if match:
                        file_dirs.append(('FILE_DIR', match.group(1)))
                    else:
                        file_dirs.append(('RAW', line))

        elif line.startswith('// PREFERENCES'):
            for line in dme:
                if line.startswith('// END_PREFERENCES'):
                    break

                preferences.append(('RAW', line))

        elif line.startswith('// BEGIN_INCLUDE'):
            for line in dme:
                if line.startswith('// END_INCLUDE'):
                    break

                if line.startswith('#include '):
                    match = re.match('#include <(.*)>', line)
                    if not match:
                        match = re.match('#include "(.*)"', line)

                    if match:
                        includes.append(('FILE_INCLUDE', match.group(1)))
                    else:
                        includes.append(('RAW', line))
    dme.close()

    return internals, file_dirs, preferences, includes


def DMEWRITE(internals, file_dirs, preferences, includes, path):
    try:
        dme = open(path, 'w')
    except OSError:
        print >> sys.stderr, traceback.format_exc()
        print >> sys.stderr, '[DME] unable to open `%s` for writing' % path
        return

    def write_block(block, dme):
        for type, line in block:
            if type == 'RAW':
                dme.write(line)
            elif type == 'FILE_INCLUDE':
                if line == '.':
                    dme.write('#include .')
                elif line.startswith('<') and line.endswith('>'):
                    dme.write('#include %s' % line)
                else:
                    dme.write('#include "%s"' % line)
            elif type == 'FILE_DIR':
                if line == '.':
                    dme.write('#define FILE_DIR .')
                elif line.startswith('<') and line.endswith('>'):
                    dme.write('#define FILE_DIR %s' % line)
                else:
                    dme.write('#define FILE_DIR "%s"' % line)

    dme.write('// DM Environment file for %s.\n' % os.path.split(dme)[-1])
    dme.write('// All manual changes should be made outside the BEGIN_ and END_ blocks.\n')
    dme.write('// New source code should be placed in .dm files: choose File/New --> Code File.\n')
    dme.write('// DME generated by DMIDE\n\n')

    dme.write('// BEGIN_INTERNALS')
    write_block(internals, dme)
    dme.write('// END_INTERNALS\n\n')

    dme.write('// BEGIN_FILE_DIR')
    write_block(file_dirs, dme)
    dme.write('// END_FILE_DIR\n\n')

    dme.write('// BEGIN_PREFERNECES')
    write_block(preferences, dme)
    dme.write('// END_PREFERENCES\n\n')

    dme.write('// BEGIN_INCLUDE')
    write_block(includes, dme)
    dme.write('// END_INCLUDE\n\n')

    dme.close()
