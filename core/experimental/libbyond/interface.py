import wx
import dmf
import sys


keys = {wx.WXK_BACK: 'BACK',
		wx.WXK_TAB: 'TAB',
		wx.WXK_RETURN: 'RETURN',
		wx.WXK_ESCAPE: 'ESCAPE',
		wx.WXK_SPACE: 'SPACE',
		wx.WXK_DELETE: 'DELETE',
		wx.WXK_LBUTTON: 'LBUTTON',
		wx.WXK_RBUTTON: 'RBUTTON',
		wx.WXK_CANCEL: 'CANCEL',
		wx.WXK_MBUTTON: 'MBUTTON',
		wx.WXK_CLEAR: 'CLEAR',
		wx.WXK_SHIFT: 'SHIFT',
		wx.WXK_ALT: 'ALT',
		wx.WXK_CONTROL: 'CTRL',
		wx.WXK_MENU: 'MENU',
		wx.WXK_PAUSE: 'PAUSE',
		wx.WXK_CAPITAL: 'CAPITAL',
		wx.WXK_PRIOR: 'PRIOR',
		wx.WXK_NEXT: 'NEXT',
		wx.WXK_END: 'SOUTHWEST',
		wx.WXK_HOME: 'NORTHWEST',
		wx.WXK_LEFT: 'WEST',
		wx.WXK_UP: 'NORTH',
		wx.WXK_RIGHT: 'EAST',
		wx.WXK_DOWN: 'SOUTH',
		wx.WXK_SELECT: 'SELECT',
		wx.WXK_PRINT: 'PRINT',
		wx.WXK_EXECUTE: 'EXECUTE',
		wx.WXK_SNAPSHOT: 'SNAPSHOT',
		wx.WXK_INSERT: 'INSERT',
		wx.WXK_HELP: 'HELP',
		wx.WXK_NUMPAD0: 'NUMPAD0',
		wx.WXK_NUMPAD1: 'NUMPAD1',
		wx.WXK_NUMPAD2: 'NUMPAD2',
		wx.WXK_NUMPAD3: 'NUMPAD3',
		wx.WXK_NUMPAD4: 'NUMPAD4',
		wx.WXK_NUMPAD5: 'NUMPAD5',
		wx.WXK_NUMPAD6: 'NUMPAD6',
		wx.WXK_NUMPAD7: 'NUMPAD7',
		wx.WXK_NUMPAD8: 'NUMPAD8',
		wx.WXK_NUMPAD9: 'NUMPAD9',
		wx.WXK_MULTIPLY: 'MULTIPLY',
		wx.WXK_ADD: 'ADD',
		wx.WXK_SEPARATOR: 'SEPARATOR',
		wx.WXK_SUBTRACT: 'SUBTRACT',
		wx.WXK_DECIMAL: 'DECIMAL',
		wx.WXK_DIVIDE: 'DIVIDE',
		wx.WXK_NUMLOCK: 'NUMLOCK',
		wx.WXK_SCROLL: 'SCROLL',
		wx.WXK_PAGEUP: 'NORTHEAST',
		wx.WXK_PAGEDOWN: 'SOUTHEAST',
		wx.WXK_F1: 'F1',
		wx.WXK_F2: 'F2',
		wx.WXK_F3: 'F3',
		wx.WXK_F4: 'F4',
		wx.WXK_F5: 'F5',
		wx.WXK_F6: 'F6',
		wx.WXK_F7: 'F7',
		wx.WXK_F8: 'F8',
		wx.WXK_F9: 'F9',
		wx.WXK_F10: 'F10',
		wx.WXK_F11: 'F11',
		wx.WXK_F12: 'F12',
		wx.WXK_F13: 'F13',
		wx.WXK_F14: 'F14',
		wx.WXK_F15: 'F15',
		wx.WXK_F16: 'F16',
		wx.WXK_F17: 'F17',
		wx.WXK_F18: 'F18',
		wx.WXK_F19: 'F19',
		wx.WXK_F21: 'F21',
		wx.WXK_F22: 'F22',
		wx.WXK_F23: 'F23',
		wx.WXK_F24: 'F24'
		}


class Window(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, wx.ID_ANY, title = 'Macro Editor')

		menu = wx.MenuBar()

		file = wx.Menu()
		file.Append(wx.ID_OPEN, 'Load DMF')
		file.Append(wx.ID_SAVE, 'Save DMF')
		file.Append(wx.ID_EXIT, '&Exit')

		menu.Append(file, '&File')

		self.SetMenuBar(menu)

		self.macro = Macros(self)

		self.Bind(wx.EVT_MENU, self.on_event)

	def on_event(self, event):
		if event.Id == wx.ID_EXIT:
			self.Destroy()

		elif event.Id == wx.ID_OPEN:
			dlg = wx.FileDialog(self, 'Choose an interface', wildcard = 'DM Interface(*.dmf)|*.dmf', style = wx.OPEN | wx.CHANGE_DIR)
			if dlg.ShowModal() == wx.ID_OK:
				path = dlg.GetPath()
				self.macro.load_dmf(path)
			dlg.Destroy()

		elif event.Id == wx.ID_SAVE:
			try:
				self.macro.dmf_macros
			except AttributeError:
				return

			dlg = wx.FileDialog(self, 'Save where', wildcard = 'DM Interface(*.dmf)|*.dmf', style = wx.SAVE | wx.CHANGE_DIR)
			if dlg.ShowModal() == wx.ID_OK:
				path = dlg.GetPath()
				dmf.DMFWRITE(self.macro.macro_list.macros, path)
			dlg.Destroy()


class Macros(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		sizer = wx.BoxSizer(wx.VERTICAL)
		self.macro_list = MacroList(self)
		sizer.Add(self.macro_list, 1, wx.ALL | wx.EXPAND)
		self.def_list = MacroDefList(self)
		sizer.Add(self.def_list, 1, wx.ALL | wx.EXPAND)
		self.SetSizer(sizer)

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selection)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activation)

	def on_selection(self, event):
		if event.EventObject == self.macro_list:
			index = event.GetIndex()
			self.def_list.macros = self.dmf_macros[index].macros
			self.def_list.SetItemCount(len(self.def_list.macros))
			self.def_list.Refresh(False)

	def on_activation(self, event):
		if event.EventObject == self.def_list:
			index = event.GetIndex()
			dlg = MacroEditDialog(self)
			macro = self.def_list.macros[index]
			dlg.set_macro(macro)
			if dlg.ShowModal() == wx.ID_OK:
				data = dlg.get_data()
				macro.id = data['id']
				macro.key = data['key']
				macro.command = data['command']
				macro.alt_modifier = data['alt']
				macro.ctrl_modifier = data['ctrl']
				macro.shift_modifier = data['shift']
				macro.release_modifier = data['release']
				macro.repeat_modifier = data['repeat']
				self.Refresh(False)
			dlg.Destroy()

	def load_dmf(self, dmf_path):
		interface = dmf.DMFREAD(dmf_path)
		self.dmf_macros = [x for x in interface if isinstance(x, dmf.DMFMacroGroup)]
		self.macro_list.reset()
		self.macro_list.macros = self.dmf_macros

		for index, macro in enumerate(self.dmf_macros):
			self.macro_list.add_macro(macro.name)


class MacroList(wx.ListCtrl):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style = wx.LC_EDIT_LABELS | wx.LC_ICON)

		self.image_list = wx.ImageList(32, 32)
		self.image_indexes = []
		self.image_indexes.append(self.image_list.Add(wx.Bitmap('keyboard.png')))
		self.SetImageList(self.image_list, wx.IMAGE_LIST_NORMAL)

		self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.on_edit)
		self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
		self.Bind(wx.EVT_RIGHT_UP, self.on_right_up)

	def reset(self):
		self.DeleteAllItems()

	def add_macro(self, macro):
		self.InsertImageStringItem(sys.maxint, macro, self.image_indexes[0])

	def on_edit(self, event):
		index = event.GetIndex()
		text = str(event.GetText())

		for macro in self.macros:
			if macro.name == text:
				event.Veto()
				return

		self.macros[index].name = text
		event.Skip()

	def on_right_down(self, event):
		event.Skip()

	def on_right_up(self, event):
		def get_selection():
			selection = []
			for x in xrange(self.GetSelectedItemCount()):
				selection.append(self.GetFirstSelected())
			return selection
		print get_selection()
		menu = wx.Menu()
		menu.Append(wx.ID_NEW, 'New')
		menu.Append(wx.ID_CUT, 'Cut')
		menu.Append(wx.ID_COPY, 'Copy')
		menu.Append(wx.ID_PASTE, 'Paste')
		menu.Append(wx.ID_DELETE, 'Delete')
		self.PopupMenu(menu)
		menu.Destroy()


class MacroDefList(wx.ListCtrl):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style = wx.LC_VIRTUAL | wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES)

		self.macros = []
		self.InsertColumn(0, 'ID')
		self.InsertColumn(1, 'Macro')
		self.InsertColumn(2, 'Command')

		self.SetColumnWidth(1, 150)
		self.SetColumnWidth(2, 250)

	def OnGetItemText(self, row, col):
		if row >= len(self.macros):
			return

		if col == 0:
			try:
				return self.macros[row].id
			except AttributeError:
				return ''

		elif col == 1:
			return repr(self.macros[row])

		elif col == 2:
			return self.macros[row].command

	def OnItemGetImage(self, row, col):
		return -1

	def OnItemGetAttr(self, row, col):
		return None


class MacroEditDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, 'Macro Editor')

		self.id_label = wx.StaticText(self, wx.ID_ANY, 'ID')
		self.id_ctrl = wx.TextCtrl(self, size = (200, -1))

		self.key_label = wx.StaticText(self, wx.ID_ANY, 'Key')
		self.key_ctrl = wx.TextCtrl(self, size = (200, -1))

		self.alt_modifier = wx.CheckBox(self, wx.ID_ANY, 'ALT')
		self.ctrl_modifier = wx.CheckBox(self, wx.ID_ANY, 'CTRL')
		self.shift_modifier = wx.CheckBox(self, wx.ID_ANY, 'Shift')
		self.repeat_modifier = wx.RadioButton(self, wx.ID_ANY, 'Repeat')
		self.release_modifier = wx.RadioButton(self, wx.ID_ANY, 'Release')

		self.command_label = wx.StaticText(self, wx.ID_ANY, 'Command')
		self.command_ctrl = wx.TextCtrl(self, size = (200, -1))

		self.ok_button = wx.Button(self, wx.ID_OK)
		self.cancel_button = wx.Button(self, wx.ID_CANCEL)

		sizer0 = wx.BoxSizer(wx.VERTICAL)

		sizer = wx.GridBagSizer(8, 4)
		sizer.Add(self.id_label, (0, 0))
		sizer.Add(self.id_ctrl, (1, 1), (1, 1), wx.ALL | wx.EXPAND)

		sizer.Add(self.key_label, (2, 0))
		sizer.Add(self.key_ctrl, (3, 1), (1, 1), wx.ALL | wx.EXPAND)

		sizer2 = wx.BoxSizer(wx.VERTICAL)
		sizer2.Add(self.alt_modifier)
		sizer2.Add(self.ctrl_modifier)
		sizer2.Add(self.shift_modifier)
		sizer2.Add(self.repeat_modifier)
		sizer2.Add(self.release_modifier)
		sizer.Add(sizer2, (4, 1))

		sizer.Add(self.command_label, (5, 0))
		sizer.Add(self.command_ctrl, (6, 1), (1, 1), wx.ALL | wx.EXPAND)

		sizer2 = wx.BoxSizer(wx.HORIZONTAL)
		sizer2.Add(self.ok_button)
		sizer2.Add(self.cancel_button)
		sizer.Add(sizer2, (7, 1), (1, 2))

		sizer0.Add(sizer, 1, wx.EXPAND | wx.ALL, border = 8)

		self.SetSizerAndFit(sizer0)
		self.key_ctrl.Bind(wx.EVT_KEY_DOWN, self.test)

	def set_macro(self, macro):
		try:
			self.id_ctrl.SetValue(macro.id)
		except AttributeError:
			pass

		self.key_ctrl.SetValue(macro.key)

		if macro.alt_modifier:
			self.alt_modifier.SetValue(True)
		if macro.ctrl_modifier:
			self.ctrl_modifier.SetValue(True)
		if macro.shift_modifier:
			self.shift_modifier.SetValue(True)
		if macro.release_modifier:
			self.release_modifier.SetValue(True)
		if macro.repeat_modifier:
			self.repeat_modifier.SetValue(True)

		self.command_ctrl.SetValue(macro.command)

	def get_data(self):
		return {'id': self.id_ctrl.GetValue(), 'key': self.key_ctrl.GetValue(),
				'command': self.command_ctrl.GetValue(), 'alt': self.alt_modifier.GetValue(),
				'ctrl': self.ctrl_modifier.GetValue(), 'shift': self.shift_modifier.GetValue(),
				'release': self.release_modifier.GetValue(), 'repeat': self.repeat_modifier.GetValue()}


	def test(self, event):
		print dir(event)

		if event.GetKeyCode() in keys:
			print keys[event.GetKeyCode()]

if __name__ == '__main__':
	a = wx.App(0)
	w = Window()
	w.Show(True)
	w.SetSize((500, 400))
	w.Center()
	a.MainLoop()
