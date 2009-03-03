#-------------------------------------------------------------------

import re

#-------------------------------------------------------------------

def parseDME(dme):
    if type(dme) == str:
        dme = open(dme, 'r').read()

    include_n1 = dme.find('// BEGIN_INCLUDE')
    include_n2 = dme.find('// END_INCLUDE')

    if include_n1 <= -1 or include_n2 <= -1:
        return -1

    include = dme[include_n1 + 16 : include_n2].strip()
    includes = include.split('\n')

    files_list = []
    libs_list = []

    for line in includes:
        match = re.match('#include "(.+)"', line)
        if match:
            files_list.append(match.groups()[0])
            continue

        match = re.match('#include <(.+)>', line)
        if match:
            libs_list.append(match.groups()[0])
            continue

    return files_list

#-------------------------------------------------------------------