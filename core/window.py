''' Window '''

from id import *
from menuservice import InstallMenuService
from artfactory import getBYONDIcon
from mainnotebook import MainNotebook
import wx.aui as aui

class Window(wx.Frame):
	def __init__(self, title='DMIDE'):
		wx.Frame.__init__(self, None, ID_WINDOW, title)

		self.SetIcon(getBYONDIcon())
		InstallMenuService(self) #Build menus

		self.statusbar=self.CreateStatusBar(3, wx.ST_SIZEGRIP)
		self.statusbar.SetStatusWidths([-10, -1, -1])

		
		self.aui_manager=aui.AuiManager()
		self.aui_manager.SetManagedWindow(self)

		self.main_notebook=MainNotebook(self)

		self.aui_manager.AddPane(self.main_notebook, aui.AuiPaneInfo().CenterPane())

		self.aui_manager.Update()
		

		'''
		sizer=wx.BoxSizer(wx.VERTICAL)
		self.main_notebook=MainNotebook(self)
		sizer.Add(self.main_notebook, 1, wx.ALL|wx.EXPAND)
		self.SetSizer(sizer)
		'''

		self.Bindings()

	def Bindings(self):
		self.Bind(wx.EVT_MENU, self.OnFileNew, id=ID_FILE_NEW)
		self.Bind(wx.EVT_MENU, self.OnFileOpen, id=ID_FILE_OPEN)
		self.Bind(wx.EVT_MENU, self.OnFileClose, id=ID_FILE_CLOSE)
		self.Bind(wx.EVT_MENU, self.OnFileSave, id=ID_FILE_SAVE)
		self.Bind(wx.EVT_MENU, self.OnFileSaveAs, id=ID_FILE_SAVEAS)


	def OnFileNew(self, event):
		self.main_notebook.OnFileNew(event)

	def OnFileOpen(self, event):
		pass

	def OnFileClose(self, event):
		pass

	def OnFileSave(self, event):
		pass

	def OnFileSaveAs(self, event):
		pass
