import core
from core import *


class DMIDE_Window(wx.Frame):
	""" The top-level window, handles events not widget-specific. """

	def __init__(self, title = 'DMIDE'):
		wx.Frame.__init__(self, None, ID_WINDOW, title, style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN)

		self.Freeze()
		self.SetInitialSize((800, 600))

		self.initAll()
		self.initBinds()

		self.updateViewMenu()
		self.updateFileMenu()
		self.updateBuildMenu()
		self.Center()

		self.Show(True)

		wx.CallAfter(self.Thaw)

	def GetMenuBar(self):
		return self.dmide_menubar

	def initAll(self):
		""" Initialize all the UI widgets and display them. """

		self.aui_manager = wxAui.AuiManager()
		self.aui_manager.SetManagedWindow(self)

		if dmide_menu_type == 'fancy':
			self.dmide_menubar = DMIDE_FancyMenuBar(self)
			self.dmide_menubar.PositionAUI(self.aui_manager)
			#self.aui_manager.AddPane(self.dmide_menubar, wxAui.AuiPaneInfo().Top().MinSize((100, -1)).LeftDockable(False).RightDockable(False).ToolbarPane().Gripper(False).Resizable(False).PaneBorder(False))
		else:
			self.dmide_menubar = DMIDE_MenuBar(self)
			self.SetMenuBar(self.dmide_menubar)

		self.dmide_statusbar = wx.StatusBar(self, ID_STATUSBAR, style=wx.NO_BORDER)
		self.dmide_statusbar.SetFieldsCount(3)
		self.dmide_statusbar.SetStatusWidths([-10, -10, -1])

		self.dmide_filetree = DMIDE_FileTree(self)
		self.dmide_editor = DMIDE_Editor(self)
		self.dmide_buildinfo = DMIDE_BuildInfo(self)
		self.dmide_objtree = DMIDE_ObjTree(self)
		self.dmide_classtree = DMIDE_ClassTree(self)
		#self.dmide_painter = DMIDE_Painter(self)

		self.aui_manager.AddPane(self.dmide_editor, wxAui.AuiPaneInfo().Name(NAME_EDITOR).Caption('Editor').CenterPane().CaptionVisible(True).MaximizeButton().CloseButton(True))
		self.aui_manager.AddPane(self.dmide_filetree, wxAui.AuiPaneInfo().Name(NAME_FILETREE).Caption('File Tree').Left().BestSize((200, 200)).FloatingSize((200, 400)).MaximizeButton(True))
		self.aui_manager.AddPane(self.dmide_objtree, wxAui.AuiPaneInfo().Name(NAME_OBJTREE).Caption('Object Tree').Right().BestSize((200, 200)).FloatingSize((200, 400)).MaximizeButton(True))
		self.aui_manager.AddPane(self.dmide_classtree, wxAui.AuiPaneInfo().Name(NAME_CLASSTREE).Caption('Class Tree').Right().BestSize((200, 200)).FloatingSize((200, 400)).MaximizeButton(True))
		#self.aui_manager.AddPane(self.dmide_painter, wxAui.AuiPaneInfo().Name(NAME_PAINTER).Caption('Painter').Right().BestSize((200, 200)).FloatingSize((200, 400)).MaximizeButton(True))
		self.aui_manager.AddPane(self.dmide_buildinfo, wxAui.AuiPaneInfo().Name(NAME_BUILDINFORMATION).Caption('Build Information').Bottom().BestSize((600, 150)).FloatingSize((800, 200)).MaximizeButton(True))

		self.SetStatusBar(self.dmide_statusbar)
		self.dmide_statusbar.Hide()

		self.aui_manager.Update()

	def initBinds(self):
		""" Assign the event handlers. """

		self.Bind(wx.EVT_MENU, self.OnFile, id = ID_FILE_NEW)
		self.Bind(wx.EVT_MENU, self.OnFile, id = ID_FILE_OPEN)
		self.Bind(wx.EVT_MENU, self.OnFile, id = ID_FILE_CLOSE)
		self.Bind(wx.EVT_MENU, self.OnFile, id = ID_FILE_SAVE)
		self.Bind(wx.EVT_MENU, self.OnFile, id = ID_FILE_SAVEAS)
		self.Bind(wx.EVT_MENU, self.OnFile, id = ID_FILE_NEWENVIRONMENT)
		self.Bind(wx.EVT_MENU, self.OnFile, id = ID_FILE_OPENENVIRONMENT)

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

		self.Bind(wx.EVT_MENU, self.OnView, id = ID_VIEW_FILETOOLBAR)
		self.Bind(wx.EVT_MENU, self.OnView, id = ID_VIEW_FILETREE)
		self.Bind(wx.EVT_MENU, self.OnView, id = ID_VIEW_OBJTREE)
		self.Bind(wx.EVT_MENU, self.OnView, id = ID_VIEW_EDITOR)
		self.Bind(wx.EVT_MENU, self.OnView, id = ID_VIEW_BUILDINFORMATION)
		self.Bind(wx.EVT_MENU, self.OnView, id = ID_VIEW_CONSOLE)
		self.Bind(wx.EVT_MENU, self.OnView, id = ID_VIEW_MENUBAR)
		self.Bind(wx.EVT_MENU, self.OnView, id = ID_VIEW_STATUSBAR)
		self.Bind(wx.EVT_MENU, self.OnView, id = ID_VIEW_FULLSCREEN)

		self.Bind(wx.EVT_MENU, self.OnBuild, id = ID_BUILD_COMPILE)
		self.Bind(wx.EVT_MENU, self.OnBuild, id = ID_BUILD_COMPILE_RUN)
		self.Bind(wx.EVT_MENU, self.OnBuild, id = ID_BUILD_RUN)

		#self.Bind(wx.EVT_MENU, self.OnDefaultPerspective, id = ID_PERSPECTIVE_DEFAULT)
		#self.Bind(wx.EVT_MENU, self.OnSavePerspective, id = ID_PERSPECTIVE_SAVE)
		#self.Bind(wx.EVT_MENU, self.OnLoadPerspective, id = ID_PERSPECTIVE_LOAD)

		self.Bind(wx.EVT_MENU, self.OnOptions, id = ID_OPTIONS_PERSPECTIVE)
		self.Bind(wx.EVT_MENU, self.OnOptions, id = ID_OPTIONS_CODE)

		self.Bind(wxAui.EVT_AUI_PANE_CLOSE, self.OnPanelClose)
		self.Bind(wx.EVT_SIZING, self.OnSize)

		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.EVT_MENU, self.OnClose, id = ID_EXIT)

	def OnFile(self, event):
		""" Event handler for File menu and toolbar events. """

		wx.FindWindowById(ID_EDITOR).OnFile(event)

	def OnEdit(self, event):
		""" Event handler for Edit menu and toolbar events. """

		pass

	def OnView(self, event):
		""" Event handler for View menu and toolbar events. """

		if event.GetId() == ID_VIEW_FULLSCREEN:
			self.Freeze()
			self.ShowFullScreen(not self.IsFullScreen())
			self.Thaw()
		else:
			event.Skip()
			self.updateViewMenu(False)

	def OnBuild(self, event):
		""" Event handler for Build menu and toolbar events. """

		build = wx.FindWindowById(ID_BUILDINFORMATION)

		if event.GetId() == ID_BUILD_COMPILE:
			build.compile()

		elif event.GetId() == ID_BUILD_COMPILE_RUN:
			if build.compile():
				build.run()

		elif event.GetId() == ID_BUILD_RUN:
			build.run()

	def OnOptions(self, event):
		""" Event handler for Options menu and toolbar events. """

		pass

	def OnClose(self, event):
		""" Safely close DMIDE. """

		event.Skip()
		self.Destroy()

	def OnPanelClose(self, event):
		""" Update the view menu when one of the panels is closed. """

		event.Skip()
		wx.CallAfter(self.updateViewMenu)

	def OnSize(self, event):
		""" Smoothen the resizing. """

		event.Skip()

	def updateViewMenu(self, update = True):
		""" Update the View menu, or update the visibility of the controls """

		menubar = self.GetMenuBar()
		if not menubar:
			return

		self.Freeze()

		try:
			if update:
				""" Update the menubar """

				menubar.FindItemById(ID_VIEW_FILETREE).Check(self.aui_manager.GetPane(NAME_FILETREE).IsShown())
				menubar.FindItemById(ID_VIEW_OBJTREE).Check(self.aui_manager.GetPane(NAME_OBJTREE).IsShown())
				menubar.FindItemById(ID_VIEW_CLASSTREE).Check(self.aui_manager.GetPane(NAME_CLASSTREE).IsShown())
				menubar.FindItemById(ID_VIEW_EDITOR).Check(self.aui_manager.GetPane(NAME_EDITOR).IsShown())
				menubar.FindItemById(ID_VIEW_BUILDINFORMATION).Check(self.aui_manager.GetPane(NAME_BUILDINFORMATION).IsShown())
				menubar.FindItemById(ID_VIEW_STATUSBAR).Check(wx.FindWindowById(ID_STATUSBAR).IsShown())
				menubar.Refresh()

			else:
				""" Update the controls """

				self.aui_manager.GetPane(NAME_FILETREE).Show(menubar.FindItemById(ID_VIEW_FILETREE).IsChecked())
				self.aui_manager.GetPane(NAME_OBJTREE).Show(menubar.FindItemById(ID_VIEW_OBJTREE).IsChecked())
				self.aui_manager.GetPane(NAME_CLASSTREE).Show(menubar.FindItemById(ID_VIEW_CLASSTREE).IsChecked())
				self.aui_manager.GetPane(NAME_EDITOR).Show(menubar.FindItemById(ID_VIEW_EDITOR).IsChecked())
				self.aui_manager.GetPane(NAME_BUILDINFORMATION).Show(menubar.FindItemById(ID_VIEW_BUILDINFORMATION).IsChecked())
				wx.FindWindowById(ID_STATUSBAR).Show(menubar.FindItemById(ID_VIEW_STATUSBAR).IsChecked())

				self.SendSizeEvent()
				self.aui_manager.Update()

		except:
			print >> sys.stderr, traceback.format_exc()

		wx.CallAfter(self.Thaw)

	def updateFileMenu(self):
		menubar = self.GetMenuBar()
		if not menubar:
			return

		enable = self.dmide_filetree.dme_path is not None

		for id in [ID_FILE_NEW, ID_FILE_SAVE, ID_FILE_SAVEAS, ID_FILE_CLOSE]:
			try:
				menubar.FindItemById(id).Enable(enable)
			except:
				pass

	def updateBuildMenu(self):
		menubar = self.GetMenuBar()
		if not menubar:
			return

		enable = self.dmide_filetree.dme_path is not None

		for id in [ID_BUILD_COMPILE, ID_BUILD_RUN, ID_BUILD_COMPILE_RUN]:
			try:
				menubar.FindItemById(id).Enable(enable)
			except:
				pass
