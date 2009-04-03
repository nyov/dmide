import wx
import dmf
import wx.lib.buttons as buttons
import unicodedata


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

		self.SetBackgroundColour(widget.background_color)
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

		if self._dmide_widget.border == 'line':
			dc.SetPen(wx.BLACK_PEN)
			x, y = self.GetPosition()
			w, h = self.GetSize()
			dc.DrawRectangle(0, 0, w, h)


if __name__ == '__main__':
	a = wx.App(0)

	windows = [x for x in dmf.DMFREAD('default.dmf') if isinstance(x, dmf.DMFWindowGroup)]

	for window in windows:
		if window.name != 'dmide':
			continue

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

	a.MainLoop()