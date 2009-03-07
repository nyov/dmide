#-------------------------------------------------------------------

import core
from core import *

#-------------------------------------------------------------------

class DMWindow(wx.Frame):
	""" The top-level window, handles events not widget-specific """

#-------------------------------------------------------------------

	def __init__(self, title = 'DMIDE'):
		wx.Frame.__init__(self, None, ID_WINDOW, title)

		self.Freeze()
		self.SetInitialSize((800, 600))

		self.initAll()
		self.initBindings()

		installMenuService(self)
		self.SetIcon(wx.GetApp().dm_art.byond_icon)
		self.updateViewMenu()
		self.OnDefaultPerspective(None)
		self.Show(True)
		self.Center()
		self.Thaw()

#-------------------------------------------------------------------

	def initAll(self):
		""" Initialize all the UI parts and display them """

		dm_art = wx.GetApp().dm_art

		#-------------------------------------------------------------------

		self.aui_manager = wxAui.AuiManager()
		self.aui_manager.SetManagedWindow(self)

		#-------------------------------------------------------------------

		self.dm_frame = core.DMFrame(self)
		self.aui_manager.AddPane(self.dm_frame, wxAui.AuiPaneInfo().CentrePane().Name(NAME_EDITOR))

		#-------------------------------------------------------------------

		self.dm_build_info = core.DMBuildInfo(self)
		self.aui_manager.AddPane(self.dm_build_info, wxAui.AuiPaneInfo().Name(NAME_BUILDINFORMATION).Caption('Build Information').Bottom().BestSize((-1, 100)).FloatingSize((800, 110)).MaximizeButton(True))

		#-------------------------------------------------------------------

		self.dm_console = core.DMConsole(self)
		self.aui_manager.AddPane(self.dm_console, wxAui.AuiPaneInfo().Name(NAME_CONSOLE).Caption('Console').Bottom().BestSize((-1, 100)).FloatingSize((500, 300)).MaximizeButton(True))
		self.aui_manager.GetPane(NAME_CONSOLE).Hide()

		#-------------------------------------------------------------------

		self.dm_file_tree = core.DMFileTree(self)
		self.aui_manager.AddPane(self.dm_file_tree, wxAui.AuiPaneInfo().Name(NAME_FILETREE).Caption('File Tree').Left().BestSize((200, -1)).FloatingSize((200, 400)).MaximizeButton(True))

		#-------------------------------------------------------------------

		file_toolbar = wx.ToolBar(self, ID_FILETOOLBAR, style = wx.TB_FLAT | wx.TB_NODIVIDER)
		file_toolbar.SetToolBitmapSize(wx.Size(16, 16))
		file_toolbar.AddLabelTool(ID_FILE_NEW, 'New', dm_art.getFromWx(wx.ART_NEW), shortHelp = 'New', longHelp = 'Create a new file.')
		file_toolbar.AddLabelTool(ID_FILE_OPEN, 'Open', dm_art.getFromWx(wx.ART_FILE_OPEN), shortHelp = 'Open', longHelp = 'Open a file or environment.')
		file_toolbar.AddLabelTool(ID_FILE_CLOSE, 'Close', dm_art.getFromWx(wx.ART_DELETE), shortHelp = 'Close', longHelp = 'Close the active file.')
		file_toolbar.AddLabelTool(ID_FILE_SAVE, 'Save', dm_art.getFromWx(wx.ART_FILE_SAVE), shortHelp = 'Save', longHelp = 'Save the active file.')
		file_toolbar.AddLabelTool(ID_FILE_SAVEAS, 'Save As', dm_art.getFromWx(wx.ART_FILE_SAVE_AS), shortHelp = 'Save As', longHelp = 'Save the active file as another name.')
		file_toolbar.AddSeparator()
		file_toolbar.AddLabelTool(ID_EXIT, 'Exit', dm_art.getFromWx(wx.ART_QUIT), shortHelp = 'Exit', longHelp = 'Exit DMIDE.')
		file_toolbar.Realize()
		self.file_toolbar = file_toolbar
		self.aui_manager.AddPane(file_toolbar, wxAui.AuiPaneInfo().Name(NAME_FILETOOLBAR).Caption('File Toolbar').ToolbarPane().Top())

		#-------------------------------------------------------------------

		self.perspective_options = PerspectiveOptions(self, self)
		self.aui_manager.AddPane(self.perspective_options, wxAui.AuiPaneInfo().Name(NAME_PERSPECTIVEOPTIONS).Caption('Options').Dockable(False).Float().Hide().CloseButton(True).Resizable(False))

		self.aui_manager.Update()

#-------------------------------------------------------------------

	def initBindings(self):
		self.Bind(wx.EVT_MENU, self.OnFile, id = ID_FILE_NEW)
		self.Bind(wx.EVT_MENU, self.OnFile, id = ID_FILE_OPEN)
		self.Bind(wx.EVT_MENU, self.OnFile, id = ID_FILE_CLOSE)
		self.Bind(wx.EVT_MENU, self.OnFile, id = ID_FILE_SAVE)
		self.Bind(wx.EVT_MENU, self.OnFile, id = ID_FILE_SAVEAS)
		self.Bind(wx.EVT_MENU, self.OnFile, id = ID_FILE_NEWENVIRONMENT)
		self.Bind(wx.EVT_MENU, self.OnFile, id = ID_FILE_OPENENVIRONMENT)

		#-------------------------------------------------------------------

		self.Bind(wx.EVT_MENU, self.OnEdit, id = ID_EDIT_UNDO)
		self.Bind(wx.EVT_MENU, self.OnEdit, id = ID_EDIT_REDO)
		self.Bind(wx.EVT_MENU, self.OnEdit, id = ID_EDIT_CUT)
		self.Bind(wx.EVT_MENU, self.OnEdit, id = ID_EDIT_COPY)
		self.Bind(wx.EVT_MENU, self.OnEdit, id = ID_EDIT_PASTE)
		self.Bind(wx.EVT_MENU, self.OnEdit, id = ID_EDIT_DELETE)
		self.Bind(wx.EVT_MENU, self.OnEdit, id = ID_EDIT_FIND)
		self.Bind(wx.EVT_MENU, self.OnEdit, id = ID_EDIT_FINDNEXT)
		self.Bind(wx.EVT_MENU, self.OnEdit, id = ID_EDIT_FINDPREV)
		self.Bind(wx.EVT_MENU, self.OnEdit, id = ID_EDIT_REPLACE)
		self.Bind(wx.EVT_MENU, self.OnEdit, id = ID_EDIT_GOTOLINE)
		self.Bind(wx.EVT_MENU, self.OnEdit, id = ID_EDIT_SELECTALL)

		#-------------------------------------------------------------------

		self.Bind(wx.EVT_MENU, self.OnView, id = ID_VIEW_FILETOOLBAR)
		self.Bind(wx.EVT_MENU, self.OnView, id = ID_VIEW_FILETREE)
		self.Bind(wx.EVT_MENU, self.OnView, id = ID_VIEW_EDITOR)
		self.Bind(wx.EVT_MENU, self.OnView, id = ID_VIEW_BUILDINFORMATION)
		self.Bind(wx.EVT_MENU, self.OnView, id = ID_VIEW_CONSOLE)

		#-------------------------------------------------------------------

		self.Bind(wx.EVT_MENU, self.OnDefaultPerspective, id = ID_PERSPECTIVE_DEFAULT)
		self.Bind(wx.EVT_MENU, self.OnSavePerspective, id = ID_PERSPECTIVE_SAVE)
		self.Bind(wx.EVT_MENU, self.OnLoadPerspective, id = ID_PERSPECTIVE_LOAD)

		#-------------------------------------------------------------------

		self.Bind(wx.EVT_MENU, self.OnOptionsMenu, id = ID_OPTIONS_PERSPECTIVE)

		#-------------------------------------------------------------------

		self.Bind(wxAui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)

		#-------------------------------------------------------------------

		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.EVT_MENU, self.OnClose, id = ID_EXIT)

#-------------------------------------------------------------------

	def OnFile(self, event):
		""" Event handler for File menu and toolbar events """

		self.dm_frame.OnFile(event)

#-------------------------------------------------------------------

	def OnEdit(self, event):
		""" Pass the Edit menu events to the DMFrame """

		self.dm_frame.OnEdit(event)

#-------------------------------------------------------------------

	def OnView(self, event):
		""" Toggle the visibility of a control """

		self.updateViewMenu(False)

#-------------------------------------------------------------------

	def OnClose(self, event):
		""" Close DMIDE :( """

		event.Skip()
		self.Destroy()

#-------------------------------------------------------------------

	def updateViewMenu(self, update = True):
		""" Update the View menubar, or update the visibility of the controls """

		menubar = self.GetMenuBar()

		if update:
			""" Update the menubar """

			menubar.FindItemById(ID_VIEW_FILETOOLBAR).Check(self.aui_manager.GetPane(NAME_FILETOOLBAR).IsShown())
			menubar.FindItemById(ID_VIEW_FILETREE).Check(self.aui_manager.GetPane(NAME_FILETREE).IsShown())
			menubar.FindItemById(ID_VIEW_EDITOR).Check(self.aui_manager.GetPane(NAME_EDITOR).IsShown())
			menubar.FindItemById(ID_VIEW_BUILDINFORMATION).Check(self.aui_manager.GetPane(NAME_BUILDINFORMATION).IsShown())
			menubar.FindItemById(ID_VIEW_CONSOLE).Check(self.aui_manager.GetPane(NAME_CONSOLE).IsShown())

		else:
			""" Update the controls """

			self.aui_manager.GetPane(NAME_FILETOOLBAR).Show(menubar.FindItemById(ID_VIEW_FILETOOLBAR).IsChecked())
			self.aui_manager.GetPane(NAME_FILETREE).Show(menubar.FindItemById(ID_VIEW_FILETREE).IsChecked())
			self.aui_manager.GetPane(NAME_EDITOR).Show(menubar.FindItemById(ID_VIEW_EDITOR).IsChecked())
			self.aui_manager.GetPane(NAME_BUILDINFORMATION).Show(menubar.FindItemById(ID_VIEW_BUILDINFORMATION).IsChecked())
			self.aui_manager.GetPane(NAME_CONSOLE).Show(menubar.FindItemById(ID_VIEW_CONSOLE).IsChecked())
			self.aui_manager.Update()

#-------------------------------------------------------------------

	def OnPaneClose(self, event):
		""" Update the view menu when one of the panels is closed """

		event.Skip()
		wx.CallAfter(self.updateViewMenu)

#-------------------------------------------------------------------

	def OnOptionsMenu(self, event):
		""" Handle the options events """

		if event.Id == ID_OPTIONS_PERSPECTIVE:
			pane = self.aui_manager.GetPane(NAME_PERSPECTIVEOPTIONS).Float()

			if pane.IsShown():
				pane.Hide()

			else:
				pane.Show()
				pane.Centre()
				self.perspective_options.SetFocus()

			self.aui_manager.Update()

#-------------------------------------------------------------------

	def loadPerspective(self, perspectiveData, path = False):
		""" Loads the perspective data or path to perspective file """

		if path == True:
			if os.path.exists(perspectiveData):
				perspectiveData = open(perspectiveData, 'r').read()
			else:
				return

		self.perspective_options.load(self.aui_manager, perspectiveData)
		self.updateViewMenu()

#-------------------------------------------------------------------

	def savePerspective(self, path, perspectiveData):
		""" Loads the perspective data to a file """

		perspectiveData += self.perspective_options.save(perspectiveData)
		open(path, 'w+').write(perspectiveData)

#-------------------------------------------------------------------

	def OnLoadPerspective(self, event):
		""" Opens the dialog to load a perspective. """

		options = 'DM Perspectives (*.dmvw)|*.dmvw|All files (*.*)|*.*'
		path = wx.GetApp().get_dir()
		dlg = wx.FileDialog(self, 'Load which perspective?', os.path.join(path, 'settings'), '', options, wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST)
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.loadPerspective(open(path, 'r').read())
		dlg.Destroy()

#-------------------------------------------------------------------

	def OnSavePerspective(self, event):
		""" Opens the dialog to save a perspective. """

		options = 'DM Perspectives (*.dmvw)|*.dmvw|All files (*.*)|*.*'
		path = wx.GetApp().get_dir()
		dlg = wx.FileDialog(self, 'Save perspective where?', os.path.join(path, 'settings'), '', options, wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			data = self.aui_manager.SavePerspective()
			self.savePerspective(path, data)
		dlg.Destroy()

#-------------------------------------------------------------------

	def OnDefaultPerspective(self, event):
		""" Load the default perspective. """

		path = wx.GetApp().get_dir()

		self.loadPerspective(os.path.join(os.path.split(path)[0], 'settings', 'views', 'default.dmvw'), True)

#-------------------------------------------------------------------