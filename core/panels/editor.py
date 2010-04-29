import core
from core import *

DM_FILE_TYPES = ['.dm', '.dmm', '.dmp', '.dms', '.dmf', '.dme', '.rsc', '.dmi']
IMAGE_FILE_TYPES = ['.png', '.bmp', '.gif', '.jpeg', '.jpg', '.dmi']
AUDIO_FILE_TYPES = ['.mod', '.it', '.s3m', '.xm', '.oxm', '.mid', '.midi', '.wav', '.ogg', '.raw', '.wma', '.aiff']
INTERFACE_FILE_TYPES = ['.dmf']

RECOGNIZED_FILE_TYPES = DM_FILE_TYPES + IMAGE_FILE_TYPES + AUDIO_FILE_TYPES


class DMIDE_Editor(wxAui.AuiNotebook):
	""" Overseer of all editors [icon, code, map, and skin] """

	def __init__(self, parent):
		wxAui.AuiNotebook.__init__(self, parent, ID_EDITOR, style=dmide_editor_style | wx.CLIP_CHILDREN)

		self.initBindings()
		self.SetArtProvider(dmide_editor_tab_art())
		self.hidden_codeeditor = DMIDE_DMEditor(self, "")
		self.hidden_codeeditor.Hide()
		self.SetWindowStyleFlag(self._flags | wx.NO_BORDER)

	def initBindings(self):
		""" Assign event handlers. """

		pass

	def TitlePage(self, page):
		title = os.path.split(page.dmi_path)[-1]
		modified = ''
		if page.modified: modified = ' *'
		self.SetPageText(self.GetPageIndex(page), '%s%s' % (title, modified))

	def updateAllStyles(self):
		""" Update all code editor stylings. """

		for x in xrange(self.GetPageCount()):
			self.GetPage(x).updateStyle(self.hidden_codeeditor)

	def Open(self, file):
		""" Create a new tab and load the file contents. """

		if not os.path.isfile(file):
			return

		try:
			def newPage(file):
				self.Freeze()

				art = wx.GetApp().art
				file = os.path.abspath(file)

				for x in xrange(self.GetPageCount()):
					if self.GetPage(x).file_path == file:
						self.SetSelection(x)
						self.Thaw()
						return self.GetPage(x)

				name = os.path.split(file)[-1]
				ext = os.path.splitext(name)[-1].lower()
				icon = art.getFromExt(ext, (dmide_editor_icon_size, dmide_editor_icon_size))

				if ext == '.rsc':
					page = DMIDE_RSCEditor(self)

				elif ext in IMAGE_FILE_TYPES:
					page = DMIDE_DMIEditor(self)

				elif ext == '.dmp' or ext == '.dmm':
					page = DMIDE_DMPEditor(self)

				elif ext in AUDIO_FILE_TYPES:
					page = DMIDE_OGGEditor(self)

				elif ext in INTERFACE_FILE_TYPES:
					page = DMIDE_DMEditor(self, "dmf")
				
				elif ext in DM_FILE_TYPES:
					page = DMIDE_DMEditor(self, "dm")
					
				else:
					page = DMIDE_DMEditor(self, "")

				page.file_path = file
				page.file_name = name
				wx.CallAfter(page.Open, file)

				if type(icon) == int:
					icon = art.getFromWx(wx.ART_NORMAL_FILE, (dmide_editor_icon_size, dmide_editor_icon_size))

				self.AddPage(page, name, True, icon)

				self.Thaw()
				return page

			extension = os.path.splitext(file)[-1]
			if extension in RECOGNIZED_FILE_TYPES:
				return newPage(file)

			elif not '\0' in open(file).read():
				return newPage(file)

		except:
			print >> sys.stderr, traceback.format_exc()

	def New(self, name, path = ''):
		""" Create a new file and open it. """

		if not path:
			path = wx.App().get_dir()

		open(os.path.join(path, name), 'w').write('')
		self.Open(os.path.join(path, name))

	def Close(self, file = None):
		""" Close a file. """

		if not file:
			file = self.GetSelection()
			if file == -1:
				return

		self.DeletePage(file)

	def Save(self, file = None):
		""" Save a file. """

		if not file:
			file = self.GetSelection()
			if file == -1:
				return
			file = self.GetPage(file)

		file.Save(file.file_path)

	def SaveAs(self, file = None):
		""" Save a file under a different name or path. """

		if not file:
			file = self.GetSelection()
			if file == -1:
				return
			file = self.GetPage(file)

		dlg = wx.FileDialog(self, 'Save File', file.file_path, file.file_name, 'All Files (*.*)|*.*', wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			file.Save(path)
		dlg.Destroy()

	def current(self):
		""" Get the currently selected editor. """

		index = self.GetSelection()
		if index == -1: return None
		return self.GetPage(index)

	def isEdited(self, child, edited = True):
		""" Update the modified page text. """

		index = self.GetPageIndex(child)
		if index == -1:
			return

		title = self.GetPageText(index)

		if edited:
			if title == child.file_name:
				self.SetPageText(index, '%s *' % child.file_name)

		else:
			if title == '%s *' % child.file_name:
				self.SetPageText(index, child.file_name)

	def OnFile(self, event):
		""" Event handler for File events. """

		if event.Id == ID_FILE_NEW:
			dm_filetree = wx.FindWindowById(ID_FILETREE)
			path, name = dm_filetree.getItem(dm_filetree.GetSelection())

			dlg = NewFileDialog(self, path)
			if dlg.ShowModal() == wx.ID_OK:
				data = dlg.getData()
				dlg.Destroy()
				full_path = os.path.join(data[1], data[0])

				if os.path.exists(full_path):
					self.Open(full_path)
				else:
					self.New(data[0], data[1])

					dm_filetree.Open(dm_filetree.dme_path)

			dlg.Destroy()

		elif event.Id == ID_FILE_OPEN:
			dlg = wx.FileDialog(self, 'Open File', os.getcwd(), '', dmfiles_wildcard, wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST)
			if dlg.ShowModal() == wx.ID_OK:
				path = dlg.GetPath()
				dlg.Destroy()
				self.Open(path)

		elif event.Id == ID_FILE_CLOSE:
			self.Close()

		elif event.Id == ID_FILE_SAVE:
			self.Save()

		elif event.Id == ID_FILE_SAVEAS:
			self.SaveAs()

		elif event.Id == ID_FILE_NEWENVIRONMENT:
			dm_filetree = wx.FindWindowById(ID_FILETREE)
			path, name = dm_filetree.getItem(dm_filetree.GetSelection())

			dlg = NewFileDialog(self, path, True)
			if dlg.ShowModal() == wx.ID_OK:
				data = dlg.getData()
				dlg.Destroy()
				full_path = os.path.join(data[1], data[0])

				if os.path.exists(full_path):
					self.Open(full_path)
				else:
					self.New(data[0], data[1])
					print full_path

					if os.path.splitext(data[0])[-1] == '.dme':
						dm_filetree.Open(full_path)

		elif event.Id == ID_FILE_OPENENVIRONMENT:
			dlg = wx.FileDialog(self, 'Open Environment', os.getcwd(), '', environment_wildcard, wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST)
			if dlg.ShowModal() == wx.ID_OK:
				path = dlg.GetPath()
				wx.FindWindowById(ID_FILETREE).Open(path)
			dlg.Destroy()

	def OnEdit(self, event):
		""" Event handler for Edit events. """

		current = self.current()
		if not current: return

		if event.Id == ID_EDIT_UNDO:
			current.Undo()

		elif event.Id == ID_EDIT_REDO:
			current.Redo()

		elif event.Id == ID_EDIT_CUT:
			current.Cut()

		elif event.Id == ID_EDIT_COPY:
			current.Copy()

		elif event.Id == ID_EDIT_PASTE:
			current.Paste()

		elif event.Id == ID_EDIT_DELETE:
			selection = current.GetSelection()
			selection = selection[1] - selection[0]

			if selection:
				current.DeleteBack()

			current.CharRight()
			current.DeleteBack()

		elif event.Id == ID_EDIT_FIND or event.Id == ID_EDIT_REPLACE:
			self.OpenFindReplaceDialog(current)

		elif event.Id == ID_EDIT_FINDNEXT:
			self.find(self.find_data)

		elif event.Id == ID_EDIT_FINDPREV:
			self.find(self.find_data, next = False)

		elif event.Id == ID_EDIT_GOTOLINE:
			dlg = GotoLineDialog(self, (current.GetLineCount(), current.GetCurrentLine() + 1))
			if dlg.ShowModal() == wx.ID_OK:
				current.ScrollToLine(dlg.getData() - 1)
			dlg.Destroy()

		elif event.Id == ID_EDIT_SELECTALL:
			current.SelectAll()

	def OpenFindReplaceDialog(self, page):
		""" Display the Find/Replace dialog. """

		if not page:
			return

		dlg = FindReplaceDialog(self, self.find_data)
		if dlg.ShowModal() == wx.ID_OK:

			data = dlg.getData()
			button = data[-1]
			self.find_data = data

			if button == 'find-next':
				self.find(data, page)
			elif button == 'find-prev':
				self.find(data, page, True)
			elif button == 'replace':
				self.replace(data, page)
				wx.CallAfter(self.OpenFindReplaceDialog, page)
			elif button == 'replace-all':
				self.replace(data, page, True)

		dlg.Destroy()

	def Find(self, data, page = None, next = True):
		""" Find previous or next text in a page. """

		if not data:
			return

		if not page:
			page = self.current()

		if not page:
			return

		find, replace, context, case, regex, button = data

		flags = 0
		if case:
			flags ^= wxStc.STC_FIND_MATCHCASE
		if regex:
			flags ^= wxStc.STC_FIND_REGEXP

		pos = -1

		if next:
			if context == 'File':
				pos = page.FindText(page.GetSelectionEnd(), page.GetLength(), find, flags)
			elif context == 'Selection':
				pos = page.FindText(page.GetSelectionStart(), page.GetSelectionEnd(), find, flags)
		else:
			if context == 'File':
				pos = page.FindText(page.GetSelectionStart(), 0, find, flags)
			elif context == 'Selection':
				pos = page.FindText(page.GetSelectionEnd(), page.GetSelectionStart(), find, flags)

		if pos != -1:
			page.SetSelection(pos, pos + len(find))

		return pos

	def Replace(self, data, page = None, all = False):
		""" Replace preview, next, or all text in a page. """

		if not data:
			return

		if not page:
			page = self.current()

		if not page:
			return

		find, replace, context, case, regex, button = data

		flags = 0
		if case:
			flags ^= wxStc.STC_FIND_MATCHCASE
		if regex:
			flags ^= wxStc.STC_FIND_REGEXP

		if context == 'Selection':
			old_select = page.GetSelectionStart(), page.GetSelectionEnd()

		pos = self.Find(data, page)

		if pos != -1:
			page.ReplaceSelection(replace)
			page.SetSelection(pos, pos + len(replace))

			if all:
				if context == 'Selection':
					page.SetSelection(old_select[0], old_select[1] + (len(replace) - len(find)))
	
				self.Replace(data, page, all)

		return pos


class FindReplaceDialog(wx.Dialog):
	""" Custom Find/Replace dialog. """

	def __init__(self, parent, find_data):
		wx.Dialog.__init__(self, parent, title = 'Find/Replace')

		self.initAll(find_data)
		self.initBindings()
		self.initConstraints()

	def initAll(self, find_data):
		""" Build the widgets. """

		self.find_label = wx.StaticText(self, wx.ID_ANY, 'Find')
		self.find = wx.TextCtrl(self, style = wx.TE_MULTILINE, size = (150, 55))

		self.replace_label = wx.StaticText(self, wx.ID_ANY, 'Replace')
		self.replace = wx.TextCtrl(self, style = wx.TE_MULTILINE, size = (150, 55))

		self.context_label = wx.StaticText(self, wx.ID_ANY, 'Context')
		self.context = wx.ComboBox(self, wx.ID_ANY, 'File', choices = ['File', 'Selection', 'Opened Files', 'All Files'], style = wx.CB_READONLY)

		self.match_case = wx.CheckBox(self, wx.ID_ANY, 'Match Case')
		self.regex = wx.CheckBox(self, wx.ID_ANY, 'Regex')

		self.find_next = wx.Button(self, 1337, 'Find Next')
		self.find_prev = wx.Button(self, 1338, 'Find Prev')
		self.find_replace = wx.Button(self, 1339, 'Replace')
		self.find_replace_all = wx.Button(self, 1340, 'Replace All')

		self.button = None


		if find_data:
			find, replace, context, case, regex, button = find_data

			self.find.SetValue(find)
			self.replace.SetValue(replace)
			self.context.SetValue(context)
			if case:
				self.case.SetChecked(True)
			if regex:
				self.regex.SetChecked(True)


	def initBindings(self):
		""" Assign the event handlers. """
		self.find_next.Bind(wx.EVT_BUTTON, self.OnButton)
		self.find_prev.Bind(wx.EVT_BUTTON, self.OnButton)
		self.find_replace.Bind(wx.EVT_BUTTON, self.OnButton)
		self.find_replace_all.Bind(wx.EVT_BUTTON, self.OnButton)

	def initConstraints(self):
		""" Build the sizers. """

		sizer = wx.GridBagSizer(0, 0)

		b = 4

		sizer.Add(self.find_label, (0, 0), (1, 1), wx.ALL | wx.ALIGN_CENTER, b)
		sizer.Add(self.replace_label, (1, 0), (1, 1), wx.ALL | wx.ALIGN_CENTER, b)
		sizer.Add(self.context_label, (2, 0), (1, 1), wx.ALL | wx.ALIGN_CENTER, b)

		sizer.Add(self.find, (0, 1), (1, 1), wx.ALL | wx.EXPAND, b)
		sizer.Add(self.replace, (1, 1), (1, 1), wx.ALL | wx.EXPAND, b)
		sizer.Add(self.context, (2, 1), (1, 1), wx.ALL | wx.EXPAND, b)

		sizer.Add(self.match_case, (3, 0), (1, 2), wx.ALL | wx.EXPAND, b)
		sizer.Add(self.regex, (4, 0), (1, 2), wx.ALL | wx.EXPAND, b)

		sizer.Add(self.find_next, (0, 2), (1, 1), wx.ALL | wx.EXPAND, b)
		sizer.Add(self.find_prev, (1, 2), (1, 1), wx.ALL | wx.EXPAND, b)
		sizer.Add(self.find_replace, (2, 2), (1, 1), wx.ALL | wx.EXPAND, b)
		sizer.Add(self.find_replace_all, (3, 2), (1, 1), wx.ALL | wx.EXPAND, b)

		self.SetSizerAndFit(sizer)

	def getData(self):
		""" Returns (find, replace, context, case, regex, button) data from the dialog. """

		find = str(self.find.GetValue())
		replace = str(self.replace.GetValue())
		context = str(self.context.GetValue())
		case = self.match_case.IsChecked()
		regex = self.regex.IsChecked()
		button = self.button

		return (find, replace, context, case, regex, button)

	def OnButton(self, event):
		""" Event handler for the buttons. """

		if event.Id == 1337:
			self.button = 'find-next'
		if event.Id == 1338:
			self.button = 'find-prev'
		elif event.Id == 1339:
			self.button = 'replace'
		elif event.Id == 1340:
			self.button = 'replace-all'

		self.EndModal(wx.ID_OK)


class GotoLineDialog(wx.Dialog):
	""" Dialog for the goto-line command. """

	def __init__(self, parent, data = None):
		wx.Dialog.__init__(self, parent, title = 'Goto Line')

		self.initAll(data)
		self.initBinds()
		self.initConstraints()

	def initAll(self, data = None):
		""" Build the widgets. """

		self.goto_label = wx.StaticText(self, wx.ID_ANY, 'Line #')
		self.goto = wx.SpinCtrl(self, wx.ID_ANY, '')

		if data:
			self.goto.SetRange(1, data[0])
			self.goto.SetValue(data[1])
		else:
			self.goto.SetRange(1, 1000000)
			self.goto.SetValue(1)

		self.ok_button = wx.Button(self, wx.ID_OK)
		self.cancel_button = wx.Button(self, wx.ID_CANCEL)

	def initBinds(self):
		""" Assign the event handlers. """

		pass

	def initConstraints(self):
		""" Build the sizers. """

		sizer = wx.GridBagSizer(0, 0)

		sizer.Add(self.goto_label, (0, 0), (1, 1), wx.ALIGN_CENTER, 4)
		sizer.Add(self.goto, (0, 1), (1, 2), wx.ALL | wx.EXPAND, 4)

		sizer.Add(self.ok_button, (1, 1), (1, 1), wx.ALL | wx.EXPAND, 4)
		sizer.Add(self.cancel_button, (1, 2), (1, 1), wx.ALL | wx.EXPAND, 4)

		self.SetSizerAndFit(sizer)

	def getData(self):
		""" Get the line number currently selected in the dialog. """

		return int(self.goto.GetValue())


class NewFileDialog(wx.Dialog):
	""" Dialog for creating new files. """

	def __init__(self, parent, default_path = '', dme = False):
		wx.Dialog.__init__(self, parent, title = 'New File', style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

		self.default_path = default_path
		self.initAll(dme)
		self.initConstraints()
		self.Layout()

	def initAll(self, dme = False):
		""" Build the widgets. """

		class DMFileList(wx.VListBox):
			""" Custom list that displays the different DM files available to create. """

			def __init__(self, parent, callback, types = 	['DM Code', 'DM Icon', 'DM Map', 'DM Interface', 'DM Script'], icons = ['.dm', '.dmi', '.dmm', '.dmf', '.dms']):
				wx.VListBox.__init__(self, parent)

				self.types = types
				self.icons = icons

				self.SetItemCount(len(self.icons))

				width = max([self.GetTextExtent(x)[0] for x in self.types]) + 8 + 32 + 2 + 2
				self.SetSize((width, (32 + 5) * self.GetItemCount()))

				self.SetSelection(0)
				self.last_selection = -1
				self.callback = callback

			def OnDrawItem(self, dc, rect, n):
				""" Draw the file image and label. """

				if self.GetSelection() == n:
					c = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
				else:
					c = self.GetForegroundColour()

				dc.SetFont(self.GetFont())
				dc.SetTextForeground(c)

				x, y, width, height = rect

				art = wx.GetApp().art

				dc.DrawBitmap(art.getFromExt(self.icons[n], (32, 32)), x + 2, y + 2, False)
				dc.DrawLabel(self.types[n], (x + 32 + 2 + 2, y, width, height), wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

				if self.GetSelection() == n and self.last_selection != n:
					self.last_selection = n
					self.callback(n)

			def OnMeasureItem(self, n):
				""" Return the measurements for each item. """
	
				return max(self.GetTextExtent(self.types[n])[1] + 5, 32 + 5)

		if not dme:
			self.file_list = DMFileList(self, self.OnSelect)
		else:
			self.file_list = DMFileList(self, self.OnSelect, ['DM Environment'], ['.dme'])

		self.dir_list = wx.GenericDirCtrl(self, size = (200, 150), style = wx.DIRCTRL_DIR_ONLY)
		self.dir_list.SetPath(self.default_path)

		self.file_name = wx.TextCtrl(self)
		self.file_name.SetFocus()

		self.ok_button = wx.Button(self, wx.ID_OK)
		self.cancel_button = wx.Button(self, wx.ID_CANCEL)

	def initConstraints(self):
		""" Build the sizers. """

		sizer = wx.BoxSizer(wx.VERTICAL)

		sizer2 = wx.BoxSizer(wx.HORIZONTAL)
		sizer2.Add(self.file_list, 0, wx.ALL | wx.EXPAND, 2)

		sizer3 = wx.BoxSizer(wx.VERTICAL)
		sizer3.Add(self.dir_list, 1, wx.ALL | wx.EXPAND, 2)
		sizer3.Add(self.file_name, 0, wx.ALL | wx.EXPAND, 2)
		sizer2.Add(sizer3, 1, wx.ALL | wx.EXPAND, 2)

		sizer4 = wx.BoxSizer(wx.HORIZONTAL)
		sizer4.Add(self.ok_button, 1, 0, 3)
		sizer4.Add(self.cancel_button, 1, 0, 3)

		sizer.Add(sizer2, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER, 2)
		sizer.Add(sizer4, 0, wx.ALIGN_CENTER, 2)
		self.SetSizerAndFit(sizer)

	def getData(self):
		""" Get the name of the file to create, and the path. """

		return (str(self.file_name.GetValue()), str(self.dir_list.GetPath()))

	def OnSelect(self, n):
		""" Event handler for when an item in the list is selected. """

		new_ext = self.file_list.icons[n]

		old = os.path.splitext(str(self.file_name.GetValue()))[0]
		self.file_name.SetValue('%s%s' % (old, new_ext))
