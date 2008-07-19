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
		self.main_notebook.OnFileOpen(event)

	def OnFileClose(self, event):
		self.main_notebook.OnFileClose(event)

	def OnFileSave(self, event):
		self.main_notebook.OnFileSave(event)

	def OnFileSaveAs(self, event):
		self.main_notebook.OnFileSaveAs(event)
