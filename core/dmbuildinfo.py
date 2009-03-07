#-------------------------------------------------------------------

import core
from core import *

#-------------------------------------------------------------------

class DMBuildInfo(wx.TextCtrl):
	""" Widget for displaying errors and compiling information """

#-------------------------------------------------------------------

	def __init__(self, parent):
		wx.TextCtrl.__init__(self, parent, ID_BUILDINFORMATION, style = wx.NO_BORDER | wx.TE_MULTILINE)

		self.SetEditable(False)

#-------------------------------------------------------------------

	def compile(self):
		filetree = wx.FindWindowById(ID_FILETREE)

		try:
			dme_path = filetree.project_path
		except AttributeError:
			return

		build_path = ''

		if os.name in ['posix', 'os2', 'mac', 'ce']:
			build_path = '/usr/local/byond/bin'
			dm_path = os.path.join(build_path, 'DreamMaker')

		elif os.name in ['dos', 'nt']:
			build_path = 'C:\\Program Files\\BYOND\\bin'
			dm_path = os.path.join(build_path, 'dm.exe')

		self.SetEditable(True)

		self.SetValue('')

		import subprocess, popen2

		p = subprocess.Popen([dm_path, dme_path], stdout=subprocess.PIPE)

		while 1:
			output = p.stdout.readline()
			if not output and p.poll() != None: return
			self.AppendText(output)

		p.close()

		self.SetEditable(False)

#-------------------------------------------------------------------