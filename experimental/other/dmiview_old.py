# --------------------------------------------------------------------

import sys, os
import wx
import wx.lib.scrolledpanel as wxScrolled
import dmi
import Image
from extend import IconExtendedPreview

# --------------------------------------------------------------------

class IconView(wxScrolled.ScrolledPanel):
	def __init__(self, *args, **kwargs):
		wxScrolled.ScrolledPanel.__init__(self, *args, **kwargs)

		self.initAll()
		self.initBinds()

		self.SetupScrolling()

	def initAll(self):
		self.SetBackgroundColour(wx.WHITE)

		self.last_fit = -1
		self.icons = []
		self.selected = None

	def initBinds(self):
		self.Bind(wx.EVT_SIZE, self.OnResize)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

	def readDMI(self, path):
		icons = dmi.DMIREAD(path)
		name = os.path.split(path)[-1]
		self.GetParent().SetTitle('DMI Viewer - %s' % name)

		self.Freeze()

		for icon in icons:
			self.icons.append(IconViewItem(self, icon))

		self.Thaw()

		# callng self.updateDisplay directly hangs the program for a bit for mysterious reasons
		size = self.GetSize()
		self.SetSize((size[0] + 1, size[1]))
		self.last_fit = -1
		self.SetSize(size)

	def die(self):
		self.icons = []
		self.selected = None
		if self.GetSizer():
			self.GetSizer().Clear(True)

	def updateDisplay(self):
		width = self.GetSize()[0]
		fit = width / (60 + 20)
		if fit <= 0: fit = 1
		if self.last_fit == fit:
			return
		self.last_fit = fit

		self.Freeze()

		sizer = wx.GridBagSizer(12, 12)
		sizer.AddMany([(item, (index / fit, index % fit), (1, 1), wx.EXPAND | wx.ALL, 4) for index, item in enumerate(self.icons)])

		self.Thaw()
		self.SetSizer(sizer)

	def Select(self, selected = None):
		if self.selected:
			self.selected.Select(False)
		self.selected = selected

	def OnResize(self, event):
		event.Skip()
		self.updateDisplay()

	def OnLeftUp(self, event):
		event.Skip()
		self.GetParent().icon_preview.previewIcon(0)
		self.Select()

# --------------------------------------------------------------------

class IconViewItem(wx.Panel):
	def __init__(self, parent, icon):
		wx.Panel.__init__(self, parent)

		self.SetBackgroundColour(wx.WHITE)
		self.icon = icon
		self.SetMinSize((60, 47))

		self.initAll()
		self.initConstraints()
		self.initBinds()

	def initAll(self):
		label = self.icon.state
		if len(label) > 10: label = label[:7] + '...'
		self.label = wx.StaticText(self, wx.ID_ANY, label)

		image = self.ImageToBitmap(self.icon.icons[0][0])
		self.image = wx.StaticBitmap(self, wx.ID_ANY, image)

	def initConstraints(self):
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.image, 0, wx.ALIGN_CENTER, border = 2)
		sizer.Add(self.label, 0, wx.ALIGN_CENTER)
		self.SetSizer(sizer)

	def initBinds(self):
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
		self.image.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
		self.label.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

	def ImageToBitmap(self, pil_img):
		wx_img = wx.EmptyImage(pil_img.size[0], pil_img.size[1])
		wx_img.SetData(pil_img.convert('RGB').tostring())
		wx_img.SetAlphaData(pil_img.convert('RGBA').tostring()[3::4])
		return wx_img.ConvertToBitmap()

	def Select(self, selected = True):
		if selected:
			self.GetParent().Select(self)
			self.Refresh()
		else:
			self.Refresh()

	def OnLeftUp(self, event):
		event.Skip()

		self.GetParent().GetParent().icon_preview.previewIcon(self)
		self.Select()

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

	def initAll(self):
		self.empty_icon = wx.BitmapFromImage(wx.EmptyImage(128, 128, True))
		self.default_font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, False, 'Arial')

		self.icon = wx.StaticBitmap(self, wx.ID_ANY, self.empty_icon, style = wx.SIMPLE_BORDER)

		self.icon_state = wx.StaticText(self, wx.ID_ANY, '', style = wx.ALIGN_CENTER | wx.TEXT_ALIGNMENT_CENTER)
		self.icon_state.SetMinSize((100, -1))
		self.icon_state.SetFont(self.default_font)

		self.icon_state_edit = wx.TextCtrl(self, wx.ID_ANY, '', style = wx.TE_PROCESS_ENTER)
		self.icon_state_edit.Hide()

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

		for hide in self.hide_list:
			hide.Hide()

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

	def initBinds(self):
		self.icon_state.Bind(wx.EVT_LEFT_DOWN, self.OnIconStateLeftDown)
		self.icon_state_edit.Bind(wx.EVT_KEY_DOWN, self.OnIconStateKeyDown)
		self.icon_state_edit.Bind(wx.EVT_KILL_FOCUS, self.OnIconStateLoseFocus)
		self.expand_icon.Bind(wx.EVT_BUTTON, self.OnExpandIconPress)
		self.load_dmi.Bind(wx.EVT_BUTTON, self.OnLoadDmiPress)

	def previewIcon(self, iconItem):
		self.Freeze()

		if iconItem == 0:
			self.icon.SetBitmap(self.empty_icon)
			self.icon.Refresh()
			self.icon_state.SetLabel('')
			self.icon_state_edit.SetValue('')
			self.icon_state.Show()
			self.icon_state_edit.Hide()

			for hide in self.hide_list:
				hide.Hide()

		else:
			icon = iconItem.icon.icons[0][0]
			icon = icon.resize((128, 128), Image.NEAREST)
			self.icon.SetBitmap(iconItem.ImageToBitmap(icon))

			self.icon_state.SetLabel(iconItem.icon.state)
			self.icon_state_edit.SetValue(iconItem.icon.state)

			dirs = {'1': 'One', '4': 'Four', '8': 'Eight'}
			self.directions.SetValue('One')
			if str(iconItem.icon.dirs) in dirs:
				self.directions.SetValue(dirs[str(iconItem.icon.dirs)])

			self.frames.SetValue(iconItem.icon.frames)

			self.loops.SetValue(iconItem.icon.loops)

			self.rewind.SetValue(iconItem.icon.rewind)

			for hide in self.hide_list:
				hide.Show()

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

			window = self.GetParent()
			window.icon_view.die()
			window.icon_view.readDMI(path)

	def OnIconStateLeftDown(self, event):
		self.icon_state.Hide()
		self.icon_state_edit.Show()
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
		wx.Frame.__init__(self, None, wx.ID_ANY, 'DMI Viewer')

		self.SetMinSize((200 + 300, 370))
		self.initAll()
		self.initConstraints()
		self.Show(True)

	def initAll(self):
		self.icon_preview = IconPreview(self)
		self.icon_view = IconView(self)
		self.icon_extend = IconExtendedPreview(self)

	def initConstraints(self):
		if self.GetSizer():
			self.GetSizer().Destroy()

		sizer = wx.BoxSizer(wx.HORIZONTAL)

		flag = wx.SizerFlags(0).Expand().Border(wx.LEFT | wx.TOP | wx.BOTTOM, 8)

		sizer.AddF(self.icon_preview, flag)
		sizer.Add(self.icon_view, 1, wx.ALL | wx.EXPAND, 8)
		sizer.Add(self.icon_extend, 1, wx.ALL | wx.EXPAND, 8)

		sizer.Hide(self.icon_extend, True)

		self.SetSizer(sizer)
		self.SetSize((850, 600))

	def initBinds(self):
		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def OnClose(self, event):
		self.icon_preview.Destroy()
		self.icon_view.die()
		self.Destroy()
		event.Skip()

	def SwapPreviews(self):
		sizer = self.GetSizer()

		if sizer.IsShown(self.icon_view):
			sizer.Hide(self.icon_view, True)
			sizer.Show(self.icon_extend, True, True)
			icon = self.icon_view.selected.icon
			self.icon_extend.displayIcon(icon)
		else:
			sizer.Hide(self.icon_extend, True)
			sizer.Show(self.icon_view, True, True)

		self.Layout()

# --------------------------------------------------------------------

if __name__ == '__main__':
	app = wx.App(0)

	DMIViewer()

	app.MainLoop()

# --------------------------------------------------------------------