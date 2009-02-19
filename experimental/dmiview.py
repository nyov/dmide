# --------------------------------------------------------------------

import sys, os
import wx
import dmi
import Image

# --------------------------------------------------------------------

class IconView(wx.ListCtrl):
	def __init__(self, root):
		wx.ListCtrl.__init__(self, root, style = wx.LC_ICON | wx.LC_VIRTUAL | wx.LC_EDIT_LABELS)

		self.initAll()
		self.initBinds()

	def initAll(self):
		self.last_pos = -1
		self.icons = None
		self.images = None
		self.image_list = None

	def initBinds(self):
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnIconStateEdit)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnIconSelect)

	def OnGetItemText(self, index, col):
		try:
			return self.icons[index].state
		except IndexError:
			return 'IndexError'

	def OnGetItemImage(self, index):
		try:
			return self.images[index]
		except IndexError:
			return 'IndexError'

	def OnGetItemAttr(self, index):
		return None

	def OnSize(self, event):
		# List won't refresh itself
		event.Skip()
		last_pos = self.GetItemRect(self.GetItemCount() - 1)
		if self.last_pos != last_pos:
			self.last_pos = last_pos
			self.Refresh(False)

	def OnIconStateEdit(self, event):
		state, index = event.GetText(), event.GetIndex()

		self.icons[index].state = state
		self.RefreshItem(index)

	def OnIconSelect(self, event):
		index = event.GetIndex()

		self.GetParent().icon_preview.previewIcon(self.icons[index])

	def loadDMI(self, DMI):
		self.icons = dmi.DMIREAD(DMI)
		self.images = []
		self.image_list = wx.ImageList(32, 32)

		def ImageToBitmap(pil_img):
			wx_img = wx.EmptyImage(pil_img.size[0], pil_img.size[1])
			wx_img.SetData(pil_img.convert('RGB').tostring())
			wx_img.SetAlphaData(pil_img.convert('RGBA').tostring()[3::4])
			return wx_img.ConvertToBitmap()

		for icon in self.icons:
			img = ImageToBitmap(icon.icons[0][0])
			self.images.append(self.image_list.Add(img))

		self.AssignImageList(self.image_list, wx.IMAGE_LIST_NORMAL)
		self.SetItemCount(len(self.icons))

# --------------------------------------------------------------------

class IconPreview(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.SetBackgroundColour(wx.WHITE)
		self.SetMinSize((200, -1))
		self.SetMaxSize((200, -1))

		self.initAll()
		self.initConstraints()
		self.initBinds()
		self.showAll(False)

	def initAll(self):
		self.empty_icon = wx.BitmapFromImage(wx.EmptyImage(128, 128, True))

		self.icon = wx.StaticBitmap(self, wx.ID_ANY, self.empty_icon, style = wx.SIMPLE_BORDER)

		self.icon_state = wx.StaticText(self, wx.ID_ANY, '', style = wx.ALIGN_CENTER | wx.TEXT_ALIGNMENT_CENTER)

		self.icon_state_edit = wx.TextCtrl(self, wx.ID_ANY, '', style = wx.TE_PROCESS_ENTER)

		self.icon_state.SetMinSize((100, self.icon_state_edit.GetSize()[1]))

		self.static_directions = wx.StaticText(self, wx.ID_ANY, 'Directions:')
		self.directions = wx.ComboBox(self, wx.ID_ANY, size = (75, -1), value = 'One', choices = ['One', 'Four', 'Eight'])

		self.static_frames = wx.StaticText(self, wx.ID_ANY, 'Frames:')
		self.frames = wx.SpinCtrl(self, wx.ID_ANY, size = (75, -1), min = 1, max = 99, initial = 1, style = wx.SP_VERTICAL)

		self.static_loops = wx.StaticText(self, wx.ID_ANY, 'Loops:')
		self.loops = wx.SpinCtrl(self, wx.ID_ANY, size = (75, -1), min = 0, max = 999999, initial = 0, style = wx.SP_VERTICAL)

		self.rewind = wx.CheckBox(self, wx.ID_ANY, 'Rewind')

		self.expand_icon = wx.Button(self, wx.ID_ANY, 'Expand >>>')
		self.load_dmi = wx.Button(self, wx.ID_ANY, 'Open DMI')

		self.hide_list = [self.static_directions, self.directions, self.static_frames, self.frames, self.static_loops, self.loops, self.rewind, self.expand_icon]

	def initConstraints(self):
		sizer = wx.BoxSizer(wx.VERTICAL)

		sizer.AddSpacer((-1, 16))
		sizer.Add(self.icon, 0, wx.ALIGN_CENTER_HORIZONTAL)
		sizer.AddSpacer((-1, 8))
		sizer.Add(self.icon_state, 0, wx.ALIGN_CENTER_HORIZONTAL)
		sizer.Add(self.icon_state_edit, 0, wx.ALIGN_CENTER_HORIZONTAL)
		sizer.AddSpacer((-1, 16))

		sizer2 = wx.GridBagSizer(8, 8)

		sizer2.Add(self.static_directions, (0, 0), flag = wx.ALIGN_CENTER)
		sizer2.Add(self.directions, (0, 1), flag = wx.ALIGN_CENTER)

		sizer2.Add(self.static_frames, (1, 0), flag = wx.ALIGN_CENTER)
		sizer2.Add(self.frames, (1, 1), flag = wx.ALIGN_CENTER)

		sizer2.Add(self.static_loops, (2, 0), flag = wx.ALIGN_CENTER)
		sizer2.Add(self.loops, (2, 1), flag = wx.ALIGN_CENTER)

		sizer2.Add(self.rewind, (3, 0), (1, 2), flag = wx.ALIGN_CENTER)

		sizer2.Add(self.expand_icon, (4, 0), (1, 2), flag = wx.ALIGN_CENTER)
		sizer2.Add(self.load_dmi, (5, 0), (1, 2), flag = wx.ALIGN_CENTER)

		sizer.Add(sizer2, 0, wx.ALIGN_CENTER_HORIZONTAL)

		self.SetSizer(sizer)

		sizer.Hide(self.icon_state_edit, True)

	def initBinds(self):
		self.icon_state.Bind(wx.EVT_LEFT_DOWN, self.OnIconStateLeftDown)
		self.icon_state_edit.Bind(wx.EVT_KEY_DOWN, self.OnIconStateKeyDown)
		self.icon_state_edit.Bind(wx.EVT_KILL_FOCUS, self.OnIconStateLoseFocus)
		self.expand_icon.Bind(wx.EVT_BUTTON, self.OnExpandIconPress)
		self.load_dmi.Bind(wx.EVT_BUTTON, self.OnLoadDmiPress)

	def showAll(self, show = True):
		for hide in self.hide_list:
			if show:
				self.GetSizer().Show(hide, True, True)
			else:
				self.GetSizer().Hide(hide, True)

	def previewIcon(self, icon):
		self.Freeze()

		if icon == 0:
			self.icon.SetBitmap(self.empty_icon)
			self.icon.Refresh()
			self.icon_state.SetLabel('')
			self.icon_state_edit.SetValue('')
			self.GetSizer().Show(self.icon_state, True, True)
			self.GetSizer().Hide(self.icon_state_edit, True)

			self.showAll(False)

		else:
			def ImageToBitmap(pil_img):
				wx_img = wx.EmptyImage(pil_img.size[0], pil_img.size[1])
				wx_img.SetData(pil_img.convert('RGB').tostring())
				wx_img.SetAlphaData(pil_img.convert('RGBA').tostring()[3::4])
				return wx_img.ConvertToBitmap()

			img = icon.icons[0][0].resize((128, 128), Image.NEAREST)
			self.icon.SetBitmap(ImageToBitmap(img))

			self.icon_state.SetLabel(icon.state)
			self.icon_state_edit.SetValue(icon.state)

			dirs = {'1': 'One', '4': 'Four', '8': 'Eight'}
			self.directions.SetValue('One')
			if str(icon.dirs) in dirs:
				self.directions.SetValue(dirs[str(icon.dirs)])

			self.frames.SetValue(icon.frames)

			self.loops.SetValue(icon.loops)

			self.rewind.SetValue(icon.rewind)

			self.showAll(True)

		self.Layout()
		self.Thaw()

	def OnExpandIconPress(self, event):
		self.GetParent().SwapPreviews()

	def OnLoadDmiPress(self, event):
		wildcard = 'DM Icon(*.dmi)|*.dmi|All Files(*.*)|*.*'
		dlg = wx.FileDialog(self, message = 'Open a DMI...', defaultDir = os.getcwd(), wildcard = wildcard, style = wx.OPEN | wx.CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_OK:
			path = str(dlg.GetPaths()[0])

			self.previewIcon(0)
			self.GetParent().icon_view.loadDMI(path)

	def OnIconStateLeftDown(self, event):
		self.GetSizer().Hide(self.icon_state, True)
		self.GetSizer().Show(self.icon_state_edit, True, True)
		self.icon_state_edit.SetFocus()
		self.Layout()

	def OnIconStateLoseFocus(self, event):
		if event: event.Skip()

		self.icon_state.Show()
		self.icon_state_edit.Hide()
		self.icon_state_edit.SetValue(self.icon_state.GetLabel())
		self.Layout()

	def OnIconStateKeyDown(self, event, force = False):
		if event: event.Skip()

		if force or event.GetKeyCode() == 13:
			self.icon_state.SetLabel(self.icon_state_edit.GetValue())
			self.OnIconStateLoseFocus(None)

		elif event.GetKeyCode() == 27:
			self.OnIconStateLoseFocus(None)

# --------------------------------------------------------------------

class DMIViewer(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title = 'DMI Viewer')

		self.initAll()
		self.initConstraints()
		self.Show(True)
		self.Center()

		self.icon_view.loadDMI('../turfs.dmi')

	def initAll(self):
		self.icon_view = IconView(self)
		self.icon_preview = IconPreview(self)

	def initConstraints(self):
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.icon_preview, 0, wx.ALL | wx.EXPAND, 4)
		sizer.Add(self.icon_view, 1, wx.ALL | wx.EXPAND, 4)
		self.SetSizerAndFit(sizer)

		self.SetSize(self.GetSize() + (360, 0))

	def initBinds(self):
		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def OnClose(self, event):
		self.GetSizer().Clear(True)
		self.Destroy()
		event.Skip()

# --------------------------------------------------------------------

if __name__ == '__main__':
	app = wx.App(0)

	DMIViewer()

	app.MainLoop()

# --------------------------------------------------------------------