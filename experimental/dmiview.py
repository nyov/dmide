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
		self.select_callback = None

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
		self.Freeze()
		event.Skip()
		last_pos = self.GetItemRect(self.GetItemCount() - 1)
		if self.last_pos != last_pos:
			self.last_pos = last_pos
			self.Refresh(False)
		self.Thaw()

	def OnIconStateEdit(self, event):
		if event.IsEditCancelled():
			event.Veto()
			return

		state, index = event.GetText(), event.GetIndex()

		self.icons[index].state = state
		self.RefreshItem(index)
		self.OnIconSelect(event)

	def OnIconSelect(self, event):
		index = event.GetIndex()

		if self.select_callback:
			self.selected = self.icons[index]
			self.select_callback.selected(self.icons[index])

	def loadDMI(self, DMI):
		self.icons = dmi.DMIREAD(DMI)
		self.selected = None
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
		self.load_dmi_callback = None
		self.swap_previews_callback = None

		self.empty_icon = wx.BitmapFromImage(wx.EmptyImage(128, 128, True))

		self.icon = wx.StaticBitmap(self, wx.ID_ANY, self.empty_icon, style = wx.SIMPLE_BORDER)

		self.icon_state = wx.StaticText(self, wx.ID_ANY, '', style = wx.ALIGN_CENTER | wx.TEXT_ALIGNMENT_CENTER)

		self.icon_state_edit = wx.TextCtrl(self, wx.ID_ANY, '', style = wx.TE_PROCESS_ENTER)

		self.icon_state.SetMinSize((100, self.icon_state_edit.GetSize()[1]))

		self.static_directions = wx.StaticText(self, wx.ID_ANY, 'Directions:')
		self.directions = wx.ComboBox(self, wx.ID_ANY, size = (75, -1), value = 'One', choices = ['One', 'Four', 'Eight'])
		self.directions.SetEditable(False)

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
		self.expand_icon.Bind(wx.EVT_BUTTON, self.OnExpandIconPress)
		self.load_dmi.Bind(wx.EVT_BUTTON, self.OnLoadDmiPress)
		self.icon_state.Bind(wx.EVT_LEFT_DOWN, self.OnAttributeChange)
		self.icon_state_edit.Bind(wx.EVT_KEY_DOWN, self.OnAttributeChange)
		self.icon_state_edit.Bind(wx.EVT_KILL_FOCUS, self.OnAttributeChange)
		self.directions.Bind(wx.EVT_COMBOBOX, self.OnAttributeChange)
		self.frames.Bind(wx.EVT_SPINCTRL, self.OnAttributeChange)
		self.loops.Bind(wx.EVT_SPINCTRL, self.OnAttributeChange)
		self.rewind.Bind(wx.EVT_CHECKBOX, self.OnAttributeChange)

	def showAll(self, show = True):
		for hide in self.hide_list:
			if show:
				self.GetSizer().Show(hide, True, True)
			else:
				self.GetSizer().Hide(hide, True)

	def selected(self, icon):
		self.Freeze()
		self.real_icon = icon

		if icon == 0:
			self.Freeze()
			self.icon.SetBitmap(self.empty_icon)
			self.icon.Refresh()
			self.icon_state.SetLabel('')
			self.icon_state_edit.SetValue('')
			self.GetSizer().Show(self.icon_state, True, True)
			self.GetSizer().Hide(self.icon_state_edit, True)

			self.showAll(False)

			self.Thaw()

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
		if self.swap_previews_callback:
			self.swap_previews_callback()

	def OnLoadDmiPress(self, event):
		wildcard = 'DM Icon(*.dmi)|*.dmi|All Files(*.*)|*.*'
		dlg = wx.FileDialog(self, message = 'Open a DMI...', defaultDir = os.getcwd(), wildcard = wildcard, style = wx.OPEN | wx.CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_OK:
			path = str(dlg.GetPaths()[0])

			if self.load_dmi_callback:
				self.selected(0)
				if self.expand_icon.GetLabel() == '<<< Collapse':
					self.OnExpandIconPress(None)
				self.load_dmi_callback.loadDMI(path)

	def OnAttributeChange(self, event):

		# combobox [directions]
		if event.EventObject == self.directions:
			dirs = {'One': 1, 'Four': 4, 'Eight': 8}
			self.real_icon.dirs = dirs[event.GetString()]
			self.real_icon.populate()

		# spin ctrl [frames]
		if event.EventObject == self.frames:
			self.real_icon.frames = event.GetInt()
			self.real_icon.populate()

		# spinctrl [loops]
		elif event.EventObject == self.loops:
			self.real_icon.loops = event.GetInt()

		# checkbox [rewind]
		if event.EventObject == self.rewind:
			self.real_icon.rewind = event.GetInt()

		# icon state label
		if event.EventObject == self.icon_state:
			self.GetSizer().Hide(self.icon_state, True)
			self.GetSizer().Show(self.icon_state_edit, True, True)
			self.icon_state_edit.SetFocus()
			self.Layout()

		# icon state text ctrl
		elif event.EventObject == self.icon_state_edit:

			def Reset(reset = True, update = False):
				self.icon_state.Show()
				self.icon_state_edit.Hide()
				if reset:
					self.icon_state_edit.SetValue(self.icon_state.GetLabel())
				if update:
					self.icon_state.SetLabel(update)
					self.icon_state_edit.SetValue(update)
				self.real_icon.state = self.icon_state_edit.GetValue()
				self.Layout()

			try:
				key = event.GetKeyCode()

				if key == 27:
					Reset(True)
					return

				elif key == 13:
					Reset(False, self.icon_state_edit.GetValue())

			except AttributeError:
				if event.EventType == 10038:
					Reset(False, self.icon_state_edit.GetValue())

			event.Skip()

# --------------------------------------------------------------------

class IconExtendedPreview(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.SetBackgroundColour(wx.Colour(188, 188, 188))

		self.initAll()
		self.initConstraints()

	def initAll(self):
		self.delay_text = wx.StaticText(self, wx.ID_ANY, 'Delay')
		self.arrow_down = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_down.png')))
		self.arrow_up = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_up.png')))
		self.arrow_right = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_right.png')))
		self.arrow_left = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_left.png')))
		self.arrow_bottomright = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_bottomright.png')))
		self.arrow_bottomleft = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_bottomleft.png')))
		self.arrow_topright = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_topright.png')))
		self.arrow_topleft = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_topleft.png')))

		self.direction_images = [self.arrow_down, self.arrow_up, self.arrow_right, self.arrow_left, 
								 self.arrow_bottomright, self.arrow_bottomleft, self.arrow_topright, self.arrow_topleft]

		for img in self.direction_images:
			img.Hide()

		self.icon = None

	def initConstraints(self, dirs = 0, clear = False):
		if self.GetSizer():
			self.GetSizer().Clear(clear)
			sizer = self.GetSizer()

		else:
			sizer = wx.GridBagSizer(16, 16)

		for img in self.direction_images:
			img.Hide()

		if dirs > 0:
			sizer.Add(self.delay_text, (0, 0), border = 2)
			sizer.Add(self.arrow_down, (1, 0), border = 2)
			if dirs > 3:
				sizer.Add(self.arrow_up, (2, 0), border = 2)
				sizer.Add(self.arrow_right, (3, 0), border = 2)
				sizer.Add(self.arrow_left, (4, 0), border = 2)
				if dirs > 7:
					sizer.Add(self.arrow_bottomright, (5, 0), border = 2)
					sizer.Add(self.arrow_bottomleft, (6, 0), border = 2)
					sizer.Add(self.arrow_topright, (7, 0), border = 2)
					sizer.Add(self.arrow_topleft, (8, 0), border = 2)

		for img_n in xrange(dirs):
			try:
				self.direction_images[img_n].Show()
			except Exception:
				pass

		self.SetSizerAndFit(sizer)

	def displayIcon(self, icon):
		self.Freeze()
		sizer = self.GetSizer()

		for dir in self.direction_images:
			sizer.Remove(dir)
		sizer.Remove(self.delay_text)

		self.icon = icon
		self.initConstraints(icon.dirs, True)

		for dir in xrange(icon.dirs):
			for frame in xrange(icon.frames):
				image = icon.icons[dir][frame]
				sizer.Add(wx.StaticBitmap(self, wx.ID_ANY, self.ImageToBitmap(image)), (dir + 1, frame + 1))

		sizer.Layout()
		self.SetSizerAndFit(sizer)

		self.Thaw()

	def ImageToBitmap(self, pil_img):
		wx_img = wx.EmptyImage(pil_img.size[0], pil_img.size[1])
		wx_img.SetData(pil_img.convert('RGB').tostring())
		wx_img.SetAlphaData(pil_img.convert('RGBA').tostring()[3::4])
		return wx_img.ConvertToBitmap()

# --------------------------------------------------------------------

class DMIViewer(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title = 'DMI Viewer')

		self.initAll()
		self.initConstraints()
		self.Show(True)
		self.Center()

		self.icon_view.loadDMI('./imgs/images/player.dmi')

	def initAll(self):
		self.icon_view = IconView(self)
		self.icon_preview = IconPreview(self)
		self.icon_extend = IconExtendedPreview(self)

		self.icon_preview.load_dmi_callback = self.icon_view
		self.icon_preview.swap_previews_callback = self.SwapPreviews
		self.icon_view.select_callback = self.icon_preview

	def initConstraints(self):
		sizer = wx.BoxSizer(wx.HORIZONTAL)

		flag = wx.SizerFlags(0).Expand().Border(wx.LEFT | wx.TOP | wx.BOTTOM, 4)
		sizer.AddF(self.icon_preview, flag)
		sizer.Add(self.icon_view, 1, wx.ALL | wx.EXPAND, 4)
		sizer.Add(self.icon_extend, 1, wx.ALL | wx.EXPAND, 4)
		sizer.Hide(self.icon_extend)
		self.SetSizerAndFit(sizer)

		self.SetSize(self.GetSize() + (360, 0))

	def initBinds(self):
		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def OnClose(self, event):
		self.GetSizer().Clear(True)
		self.Destroy()
		event.Skip()

	def SwapPreviews(self):
		sizer = self.GetSizer()
		self.Freeze()

		if sizer.IsShown(self.icon_view):
			sizer.Hide(self.icon_view, True)
			sizer.Show(self.icon_extend, True, True)
			icon = self.icon_view.selected
			self.icon_extend.displayIcon(icon)
			self.icon_preview.expand_icon.SetLabel('<<< Collapse')
		else:
			sizer.Hide(self.icon_extend, True)
			sizer.Show(self.icon_view, True, True)
			self.icon_preview.expand_icon.SetLabel('Expand >>>')

		self.Layout()
		self.Thaw()

# --------------------------------------------------------------------

if __name__ == '__main__':
	app = wx.App(0)

	DMIViewer()

	app.MainLoop()

# --------------------------------------------------------------------