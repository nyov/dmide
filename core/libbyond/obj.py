import core
from core import *


def OBJREAD(tree, tablevel=0, parentobj=None):
    top_objects = []

    for line in tree:
        line = line.strip('\r\n')

        if not line:
            continue

        if line.startswith('loading '):
            continue

        if re.match('(.+):(\d+):(error):(.*):(.+)', line):
            return []

        object2_re = re.compile('(\t{%s})<(area|turf|obj|mob|obejct|var) file="(.+):(\d+)">(\w+)</(area|turf|obj|mob|obejct|var)>$' % tablevel)
        object_re = re.compile('(\t{%s})<(area|turf|obj|mob|object|var) file="(.+):(\d+)">(.+)$' % tablevel)
        val_re = re.compile('(\t{%s})<val file="(.+):(\d+)">(.+)</val>$' % tablevel)
        var_re = re.compile('(\t{%s})<(var) file="(.+):(\d+)">(.+)</var>$' % tablevel)
        verb_re = re.compile('(\t{%s})<(verb) file="(.+):(\d+)">(.+)</verb>$' % tablevel)
        proc_re = re.compile('(\t{%s})<proc file="(.+):(\d+)">(.+)</proc>$' % tablevel)

        var_match = var_re.match(line)
        if var_match:
            top_objects.append(DMIDE_Var(var_match.group(3), var_match.group(4), var_match.group(5), parentobj))
            continue

        verb_match = verb_re.match(line)
        if verb_match:
            top_objects.append(DMIDE_Verb(verb_match.group(3), verb_match.group(4), verb_match.group(5), parentobj))
            continue

        proc_match = proc_re.match(line)
        if proc_match:
            top_objects.append(DMIDE_Proc(proc_match.group(2), proc_match.group(3), proc_match.group(4), parentobj))
            continue

        inline = object2_re.match(line)
        if inline:
            object_type = inline.group(2)
            object = None
            if object_type in ('area', 'turf', 'obj', 'mob'):
                object = DMIDE_Atom(inline.group(3), inline.group(4), inline.group(5), parentobj, inline.group(2))
            else:
                object = DMIDE_Datum(inline.group(3), inline.group(4), inline.group(5), parentobj, inline.group(2))

            top_objects.append(object)
            continue

        match = object_re.match(line)
        if match:
            if match.group(2) == 'var':
                object = DMIDE_Var(match.group(3), match.group(4), match.group(5), parentobj)
                OBJREAD(tree, tablevel+1, object)
                top_objects.append(object)
            else:
                object_type = match.group(2)
                object = None
                if object_type in ('area', 'turf', 'obj', 'mob'):
                    object = DMIDE_Atom(match.group(3), match.group(4), match.group(5), parentobj, match.group(2))
                else:
                    object = DMIDE_Datum(match.group(3), match.group(4), match.group(5), parentobj, match.group(2))

                for obj in OBJREAD(tree, tablevel+1, object):
                    if isinstance(obj, DMIDE_Proc):
                        object.procs.append(obj)
                    elif isinstance(obj, DMIDE_Var):
                        object.vars.append(obj)
                    elif isinstance(obj, DMIDE_Datum) or isinstance(obj, DMIDE_Atom):
                        object.children.append(obj)
                top_objects.append(object)
                continue

        match = val_re.match(line)
        if match:
            if parentobj and isinstance(parentobj, DMIDE_Var):
                parentobj.value = DMIDE_Val(match.group(2), match.group(3), match.group(4), parentobj)
            else:
                print >> sys.stderr, '[OBJ] no var for val?', DMIDE_Val.name, parentobj
        elif tablevel != 0:
            if re.match('(\t{%i})(?!\t)' % (tablevel-1), line):
                break

    return top_objects


class DMIDE_Base:
    def __init__(self, _file, _line, _name, _parent=None):
        self.file = _file
        self.line = _line
        self.name = _name
        self.parent = _parent

    def __repr__(self):
        return self.name

class DMIDE_Verb(DMIDE_Base):
    pass

class DMIDE_Proc(DMIDE_Base):
    pass

class DMIDE_Val(DMIDE_Base):
    def get_value(self):
        if not len(self.name) or len(self.name) == 1:
            return self.name

        if self.name[0] == '"' and self.name[-1] == '"':
            return self.name[1:-1]

        if self.name[0] == "'" and self.name[-1] == "'":
            return self.name[1:-1]

        return self.name

class DMIDE_Var(DMIDE_Base):
    def __init__(self, _file, _line, _name, _parent=None, _value=None):
        self.file = _file
        self.line = _line
        self.name = _name
        self.parent = _parent
        self.value = _value

class DMIDE_Datum(DMIDE_Base):
    def __init__(self, _file, _line, _name, _parent=None, _type=None):
        self.file = _file
        self.line = _line
        self.name = _name
        self.parent = _parent
        self.type = _type
        self.vars = []
        self.procs = []
        self.verbs = []
        self.children = []

    def get_inherited_val(self, attribute):
        for var in self.vars:
            if var.name == attribute:
                return var.value

        if self.parent:
            return self.parent.get_inherited_val(attribute)

        return None

class DMIDE_Atom(DMIDE_Datum):
    pass
