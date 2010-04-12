import os
import sys
import glob

"""wxselect selects an appropriate wxPython module and adds it to sys.path
Version selection is implemented with environment variables"
Order of precedence is:
  WXPYTHON_PATH
  WXPYTHON_VERSION (looks for a version starting with this - 2.4 or 2.4.2.4 are valid)
  WXPYTHON_MINVERSION (requires at least this version)
Otherwise the latest available version is used
"""

class EnvConfig:
  """reads environment variables of the form MODULE_KEY and stores them as self.key"""
  def __init__(self, modulename, keys):
    for key in keys:
      setattr(self, key, os.getenv("%s_%s" % (modulename.upper(), key.upper())))

class VersionFinder:
  """Finds Versions of a module using module-x.y.z directory names and selects best match for environment variables"""
  keys = ("minversion", "version", "path", "pythonpath")
  def __init__(self, modulename, versionimportlist = None, versionattrlist = ["ver", "version", "VERSION", "VERSION_STRING"]):
    """construct a VersionFinder for the given modulename"""
    self.modulename = modulename
    if versionimportlist:
      self.versionimportlist = versionimportlist
    else:
      self.versionimportlist = [os.path.join(self.modulename, "__version__.py")]
    self.versionattrlist = versionattrlist
    self.findversions()

  def findversions(self):
    """finds all versions of this module by looking at module-x.y.z directories in the Python Path"""
    self.versions = {}
    for path in sys.path:
      filenames = glob.glob(os.path.join(path, '%s-*' % self.modulename))
      for filename in filenames:
        if os.path.isfile(filename) and filename.lower().endswith(os.extsep + "pth"):
          versionname = os.path.splitext(os.path.basename(filename))[0]
          versionpaths = []
          for versiondir in open(filename):
            versionpaths.extend(self.readversionpath(versiondir.strip()))
        elif os.path.isdir(filename):
          versionname = os.path.basename(filename)
          versionpaths = self.readversionpath(filename)
        else:
          continue
        version = versionname[len("%s-" % self.modulename):]
        if version not in self.versions:
          self.versions[version] = versionpaths
    return self.versions

  def readversionpath(self, versiondir):
    """reads any .pth files in the versiondir and returns the path required for the version"""
    versionpaths = [versiondir]
    versionpthfiles = glob.glob(os.path.join(versiondir, '*.pth'))
    for pthfile in versionpthfiles:
      for line in open(pthfile, "r"):
        versionpath = line.strip()
        if not versionpath: continue
        if not os.path.isabs(versionpath):
          versionpath = os.path.join(os.path.dirname(versiondir), versionpath)
        versionpaths.append(versionpath)
    return versionpaths

  def readpathversion(self, versionpath):
    """reads the module version from the given path"""
    import imp
    for versionimportpath in self.versionimportlist:
      versionfilename = os.path.join(versionpath, versionimportpath)
      if os.path.isfile(versionfilename):
        versionmodule = imp.load_source(os.path.basename(versionfilename), versionfilename, open(versionfilename, 'r'))
        if versionmodule is not None:
          for versionattrname in self.versionattrlist:
            version = getattr(versionmodule, versionattrname, None)
            if version is not None:
              return version
    return None

  def getversionpath(self, version):
    """looks up the pathsep-joined path for the given version"""
    return os.path.pathsep.join(self.versions[version])

  def listversions(self):
    """lists known versions"""
    return self.versions.keys()

  def getbestversion(self, possibleversions):
    """finds the best version out of the possibilities"""
    if possibleversions:
      return max(possibleversions)

  def getconfig(self, path=None, version=None, minversion=None):
    """reads the environment variables and intelligently chooses version and path"""
    config = EnvConfig(self.modulename, self.keys)
    if path:
      config.path = path
    if version:
      config.version = version
    if minversion:
      config.minversion = minversion
    if config.path:
      config.version = self.readpathversion(config.path)
    else:
      if config.version:
        possibleversions = [version for version in self.listversions() if version.startswith(config.version)]
      elif config.minversion:
        possibleversions = [version for version in self.listversions() if version >= config.minversion]
      else:
        possibleversions = self.listversions()
      config.version = self.getbestversion(possibleversions)
      if config.version:
        config.path = self.getversionpath(config.version)
    return config

  def setpath(self, path=None, version=None, minversion=None):
    """removes other versions from the path and appends the selected path"""
    allpaths = []
    map(allpaths.extend, self.versions.values())
    self.removefrompath(allpaths)
    config = self.getconfig(path, version, minversion)
    self.appendtopath(config.path)

  def appendtopath(self, paths):
    """takes a pathsep-separated path list and adds elements to the Python path at the end"""
    if paths:
      pathlist = paths.split(os.path.pathsep)
      pathlist = [path for path in pathlist if path and os.path.isdir(path)]
      sys.path.extend(pathlist)

  def prependtopath(self, paths):
    """takes a pathsep-separated path list and adds elements to the Python path at the beginning"""
    if paths:
      pathlist = paths.split(os.path.pathsep)
      pathlist = [path for path in pathlist if path and os.path.isdir(path)]
      sys.path = pathlist + sys.path

  def removefrompath(self, pathlist):
    """removes all known versions from the PythonPath"""
    def normalize(path):
      return os.path.normcase(os.path.normpath(os.path.abspath(path)))
    if pathlist:
      pathlist = [normalize(path) for path in pathlist if path and os.path.isdir(path)]
      sys.path = [path for path in sys.path if normalize(path) not in pathlist]

wx25versionfile = os.path.join("wx", "__version__.py")
wx25versionattr = "VERSION_STRING"
wx24versionfile = os.path.join("wxPython", "__version__.py")
wx24versionattr = "wxVERSION_STRING"
wxversionimportlist = [wx25versionfile, wx24versionfile]
wxversionattrlist = [wx25versionattr, wx24versionattr]
wxVersionFinder = VersionFinder("wxPython", versionimportlist = wxversionimportlist, versionattrlist = wxversionattrlist)

if __name__ == "__main__":
  print "wxPython version selector"
  print "available versions:"
  for version, path in wxVersionFinder.versions.iteritems():
    print "%s: %s" % (version, path)
  print
  config = wxVersionFinder.getconfig()
  print "selected: %s in %s" % (config.version, config.path)
else:
  wxVersionFinder.setpath()
  # wxVersionFinder.appendtopath(wxVersionFinder.getconfig().path)