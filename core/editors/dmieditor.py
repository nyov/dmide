
"""

DMIDE Icon Editor

"""
import sys

if not hasattr(sys, 'frozen'):
	import wxversion
	wxversion.select("2.8")

import wx

#import thread


import core
from core import *

#import core.iconlistctrl as wxIconList


import iconeditor, iconviewer



class DMIDE_DMIEditor(wx.Panel):
	def __init__(self, root):
		wx.Panel.__init__(self, root)

		#self.palette = DMIPalette(self)
		self.viewer = iconviewer.IconViewer(self)
		self.editor = iconeditor.IconEditor(self)

		sizer = wx.BoxSizer(wx.VERTICAL)
		#sizer.Add(self.palette, 1, wx.ALL|wx.EXPAND)
		sizer.Add(self.viewer, 1, wx.ALL|wx.EXPAND)
		sizer.Add(self.editor, 1, wx.ALL|wx.EXPAND)
		self.SetSizer(sizer)

		self.modified = False

		self.editor.Hide()
		sizer.Hide(self.editor)
		self.Layout()

	def TitlePage(self, text):
		self.GetParent().TitlePage(text)

	def SetTitle(self, text):
		pass

	def Open(self, image):
		self.dmi_path = image
		self.viewer.Open(image)

	def selected(self, img):
		self.GetSizer().Hide(self.viewer)
		self.viewer.Hide()
		self.GetSizer().Show(self.editor)
		self.editor.Show()
		self.editor.Open(img)
		self.Layout()









# TODO: Make this able to work as a standalone editor by running the .py directly

### Not-working code to use this as a standalone icon editor

##class StandaloneDMIEditor(wx.Frame):
##	"""Standalone Icon Editor frame for testing."""
##	def __init__(self, *args, **kwargs):
##		"""Create the standalone frame."""
##		wx.Frame.__init__(self, *args, **kwargs)
##
##		#Build the menu bar
##		menubar = wx.MenuBar()
##
##		filemenu = wx.Menu()
##
##		item = filemenu.Append(wx.ID_NEW, "&New", "Create a new DMI")
##		self.Bind(wx.EVT_MENU, self.OnNew, item)
##		item = filemenu.Append(wx.ID_OPEN, "&Open", "Open a DMI")
##		self.Bind(wx.EVT_MENU, self.OnOpen, item)
##		item = filemenu.Append(wx.ID_CLOSE, "&Close", "Close a DMI")
##		self.Bind(wx.EVT_MENU, self.OnClose, item)
##
##		filemenu.AppendSeparator()
##
##		item = filemenu.Append(wx.ID_EXIT, text="&Quit")
##		self.Bind(wx.EVT_MENU, self.OnQuit, item)
##
##		menubar.Append(filemenu, "&File")
##		self.SetMenuBar(menubar)
##
##		#self.Panel = DemoPanel(self)
##
##		self.iconviewer = DMIDE_IconViewer(self)
####		sizer = wx.BoxSizer(wx.VERTICAL)
####		sizer.Add(self.Panel, 1, wx.EXPAND | wx.ALL)
####		self.SetSizer(sizer)
####		self.Layout()
##
##		#self.Fit()
##
##	def OnQuit(self, event=None):
##		"""Exit application."""
##		self.Close()
##
##	def OnNew(self, event=None):
##		"""Exit application."""
##		self.Close()
##
##	def OnOpen(self, event=None):
##		"""Open a DMI File."""
##
##		dlg = wx.FileDialog(self, 'Open File', os.getcwd(), '', imagefiles_wildcard, wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST)
##		if dlg.ShowModal() == wx.ID_OK:
##			path = dlg.GetPath()
##			dlg.Destroy()
##			self.Open(path)
##
##	def Open(self, image):
##		self.dmi_path = image
##		self.iconviewer.Open(image)
##		#self.GetSizer().Fit(self)
##		#self.Layout()
##
##	def OnClose(self, event=None):
##		"""Exit application."""
##		self.Close()
##
##
##
### strange way of importing core
### FIXME: do this better somehow
### Had to add dmide to the pythonpath for this to work
##
##if __name__ == '__main__':
##
##	import sys, os
##	if hasattr(sys, 'frozen'):
##		mypath = os.path.split(sys.executable)[0]
##
##	else:
##		mypath = os.path.split(os.path.abspath(sys.argv[0]))[0]
##
##	mypath = os.path.join(mypath, "..")
##	mypath = os.path.join(mypath, "..")
##	mypath = os.path.normpath(mypath)
##	sys.path.append(mypath)
##	#print mypath
##
#### FIXME: dmide's package setup is bad
#### dmide itself needs to be a package too??
#### import of a module just called 'core' seems like a bad idea
##
##
##
##
##
##if __name__ == '__main__':
##
##	# TODO: Come up with a standard/nice-ish way of getting a full shiny interface here
##
##	# if possible, optimize with psyco
##	try:
##		import psyco
##		psyco.full()
##	except ImportError:
##		pass
##
##	app = wx.App(redirect = 0) #stdio will stay at the console
##	frame = StandaloneDMIEditor(None, title="DMIDE Icon Editor (standalone)")
##	frame.Show()
##	app.MainLoop()
##
