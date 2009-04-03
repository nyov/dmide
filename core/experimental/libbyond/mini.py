import wx
import dmf
import wx.lib.buttons as buttons
import unicodedata
import time
import sys


background_type = 1 #1: dots, 2: lines
back_type_width = 8
back_type_height = 8
back_type_colour = wx.Colour(0, 0, 0)


class Window(wx.Frame):
	def __init__(self, title):
		wx.Frame.__init__(self, None, wx.ID_ANY, title, style = wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE)

		self.Bind(wx.EVT_PAINT, self.on_paint)

	def on_paint(self, event):
		event.Skip()

		dc = wx.PaintDC(self)

		dc.SetPen(wx.Pen(back_type_colour))

		w, h = self.GetClientSize()

		if background_type == 1:
			for x in xrange(0, w, back_type_width):
				for y in xrange(0, h, back_type_height):
					dc.DrawPoint(x, y)

		elif background_type == 2:
			for x in xrange(0, w, back_type_width):
				dc.DrawLine(x, 0, x, h)
			for y in xrange(0, h, back_type_height):
				dc.DrawLine(0, y, w, y)



class Widget(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.Bind(wx.EVT_PAINT, self.on_paint)

	def load_widget(self, widget):

		sizer = wx.BoxSizer(wx.VERTICAL)

		ctrl = None
		styles = 0

		#if widget.border:
			#styles = {'none': wx.NO_BORDER, 'line': wx.SIMPLE_BORDER, 'sunken': wx.SUNKEN_BORDER}[widget.border]
		if widget.type == 'BUTTON':
			if widget.is_flat:
				styles |= wx.NO_BORDER

		try:
			align_styles = widget.align.split('-')
			if 'left' in align_styles:
				styles |= wx.ALIGN_LEFT
			if 'right' in align_styles:
				styles |= wx.ALIGN_RIGHT
			if 'top' in align_styles:
				styles |= wx.ALIGN_TOP
			if 'bottom' in align_styles:
				styles |= wx.ALIGN_BOTTOM
			if 'center' in align_styles:
				styles |= wx.ALIGN_CENTER
		except AttributeError:
			pass


		if widget.type == 'LABEL':
			ctrl = wx.StaticText(self, wx.ID_ANY, widget.text.replace('\\"', '"'), style = styles)

		elif widget.type == 'BUTTON':
			if widget.button_type == 'radio':
				ctrl = wx.RadioButton(self, wx.ID_ANY, widget.text, style = styles)
			elif widget.button_type == 'checkbox':
				ctrl = wx.CheckBox(self, wx.ID_ANY, widget.text, style = styles)
			else:
				ctrl = buttons.GenButton(self, wx.ID_ANY, widget.text, style = styles)

		elif widget.type == 'CHILD':
			ctrl = wx.Panel(self, wx.ID_ANY, style = styles)

		elif widget.type == 'BROWSER':
			ctrl = wx.Panel(self, wx.ID_ANY, style = styles)

		elif widget.type == 'INPUT':
			ctrl = wx.TextCtrl(self, wx.ID_ANY, widget.command, style = styles)

		elif widget.type == 'OUTPUT':
			ctrl = wx.TextCtrl(self, wx.ID_ANY, style = styles)

		else:
			return

		#ctrl.SetBackgroundColour(widget.background_color)
		self.SetBackgroundColour(widget.background_color)
		#ctrl.SetBackgroundColour(wx.Colour(0, 0, 0, 255))
		ctrl.SetForegroundColour(widget.text_color)

		font_size, font_family = 9, 'MS Sans Serif'
		if widget.font_size:
			font_size = widget.font_size
		if widget.font_family:
			font_family = widget.font_family
		font = wx.Font(font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, font_family)
		ctrl.SetFont(font)

		sizer.Add(ctrl, 1, wx.ALL | wx.EXPAND, border = 1)

		self.SetSizer(sizer)

		self.SetPosition(widget.pos)
		self.SetSize(widget.size)
		self._dmide_widget = widget
		self.ctrl = ctrl

	def on_paint(self, event):
		event.Skip()

		dc = wx.PaintDC(self)

		try:
			if self._dmide_widget.border == 'line':
				dc.SetPen(wx.BLACK_PEN)
				x, y = self.GetPosition()
				w, h = self.GetSize()
				dc.DrawRectangle(0, 0, w, h)
		except AttributeError:
			pass


class InterfaceEditor(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, wx.ID_ANY, 'Interface Editor')

		self.Show(True)

		self.interface_list = InterfaceList(self)

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.interface_list, 1, wx.ALL | wx.EXPAND)
		self.SetSizerAndFit(sizer)

		self.load_interface('test.dmf')

	def load_interface(self, path):
		nodes = dmf.DMFREAD(path)
		windows = [x for x in nodes if isinstance(x, dmf.DMFWindowGroup)]
		self.interface_list.ClearAll()

		for window in windows:
			self.interface_list.add_widget(window)
			time.sleep(0.01)

		#self.interface_list.SetItemCount(len(self.interface_list.windows))




class InterfaceList(wx.ListCtrl):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size = (300, 200), style = wx.LC_ICON | wx.LC_AUTOARRANGE)

		self.image_list = wx.ImageList(128, 128)
		self.SetImageList(self.image_list, wx.IMAGE_LIST_NORMAL)
		self.image_index = []
		self.windows = []

	def add_widget(self, widget):
		def create(window):
			w = Window(window.name)
			for widget in window.windows:

				if widget.type == 'MAIN':
					w.SetClientSize(widget.size)
					w.SetBackgroundColour(widget.background_color)
					if widget.statusbar:
						w.CreateStatusBar()

				else:
					x = Widget(w)
					x.load_widget(widget)
			return w

		def add_screen(control, size = (128, 128)):
			context = wx.WindowDC(control)
			memory = wx.MemoryDC()
			x, y = control.GetSizeTuple()
			bitmap = wx.EmptyBitmap(x, y)
			memory.SelectObject(bitmap)
			memory.Blit(0, 0, x, y, context, 0, 0)
			memory.SelectObject(wx.NullBitmap)
			image = wx.ImageFromBitmap(bitmap)
			image.SaveFile('debug\\%s.png' % control.GetTitle(), wx.BITMAP_TYPE_PNG)

			w, h = image.GetSize()
			if w > h or 1:
				ratio = w / float(size[0])
				w, h = w / ratio, h / ratio
			else:
				print 1
				ratio = h / float(size[1])
				w, h = w / ratio, h / ratio

			#img = wx.BitmapFromImage(image.Rescale(size[0], size[1], wx.IMAGE_QUALITY_NORMAL))
			img = wx.BitmapFromImage(image.Rescale(w, h, wx.IMAGE_QUALITY_NORMAL))

			img.SaveFile('debug\\%s_2.png' % control.GetTitle(), wx.BITMAP_TYPE_PNG)
			self.image_index.append(self.image_list.Add(img))
			self.SetImageList(self.image_list, wx.IMAGE_LIST_NORMAL)
			control.Destroy()
			self.InsertImageStringItem(sys.maxint, widget.name, self.image_index[-1])

		self.windows.append(widget.name)
		tmp = create(widget)
		tmp.Show(True)
		wx.CallLater(10, add_screen, tmp)

		#self.windows.append(widget.name)

	def OnGetItemText(self, row, col):
		return self.windows[row]

	def OnItemGetImage(self, row, col):
		print row
		return self.image_index[row]

	def OnItemGetAttr(self, row, col):
		return None


if __name__ == '__main__':
	a = wx.App(0)

	'''
	windows = [x for x in dmf.DMFREAD('default.dmf') if isinstance(x, dmf.DMFWindowGroup) if x.name == 'about']

	def screen(control):
		context = wx.WindowDC(control)
		memory = wx.MemoryDC()
		x, y = control.GetSizeTuple()
		bitmap = wx.EmptyBitmap(x, y)
		memory.SelectObject(bitmap)
		memory.Blit(0, 0, x, y, context, 0, 0)
		memory.SelectObject(wx.NullBitmap)
		bitmap.SaveFile('test.bmp', wx.BITMAP_TYPE_BMP)

	for window in windows:
		w = Window(window.name)
		for widget in window.windows:

			if widget.type == 'MAIN':
				w.SetClientSize(widget.size)
				w.SetBackgroundColour(widget.background_color)
				if widget.statusbar:
					w.CreateStatusBar()

			else:
				x = Widget(w)
				x.load_widget(widget)
		w.Show(True)
		wx.CallLater(100, screen, w)
		#screen(w)
	'''

	main = InterfaceEditor()

	a.MainLoop()