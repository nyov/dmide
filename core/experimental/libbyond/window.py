import wx
import dmf

import wx.lib.buttons as buttons


class Window(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, wx.ID_ANY, 'Interface Editor', style = wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE)

		#self.inner = Inner(self)

		#sizer = wx.BoxSizer(wx.HORIZONTAL)
		#sizer.Add(Inner(self), 1, wx.ALL | wx.EXPAND)
		#self.SetSizerAndFit(sizer)

		self.ctrls = []
		self.load_dmf('default.dmf')
		self.Bind(wx.EVT_PAINT, self.on_paint)


	def load_dmf(self, path):
		self.window = [x for x in dmf.DMFREAD(path) if isinstance(x, dmf.DMFWindowGroup) and x.name == 'about'][0]

		main = [x for x in self.window.windows if x.type == 'MAIN'][0]

		self.SetBackgroundColour(main.background_color)
		self.SetClientSize(main.size)

		for widget in self.window.windows:
			self.load_widget(widget)

	def on_paint(self, event):
		event.Skip()

		dc = wx.PaintDC(self)

		#dc.SetBrush(wx.Brush(wx.Color(99, 99, 99), wx.CROSS_HATCH))
		#dc.FloodFill(0, 0, wx.Color(0, 0, 0), wx.FLOOD_BORDER)

		dc.SetPen(wx.Pen(wx.Color(0, 0, 0)))
		for x in xrange(0, self.GetClientSize()[0], 8):
			for y in xrange(0, self.GetClientSize()[1], 8):
				dc.DrawPoint(x, y)
		'''
		for ctrl in self.ctrls:
			if ctrl.__dmide_ctrl.border == 'none':
				dc = wx.WindowDC(self)
				dc.SetPen(wx.BLACK_PEN)
				dc.SetBrush(wx.TRANSPARENT_BRUSH)
				x, y = ctrl.GetPosition()
				w, h = ctrl.GetSize()
				dc.DrawRectangle(x, y, w, h)
		'''


	def on_widget_paint(self, event):
		ctrl = event.EventObject

		ctrl.Freeze()

		event.Skip()

		try:
			ctrl.__dmide_ctrl
		except AttributeError:
			ctrl.Thaw()
			return

		print ctrl.__dmide_ctrl.border

		if ctrl.__dmide_ctrl.border == 'line':
			dc = wx.WindowDC(self)
			dc.SetPen(wx.BLACK_PEN)
			dc.SetBrush(wx.TRANSPARENT_BRUSH)
			x, y = ctrl.GetPosition()
			w, h = ctrl.GetSize()
			dc.DrawRectangle(x + 1, y + 1, w, h)

		ctrl.Thaw()

	def load_widget(self, widget):

		if widget.type == 'MAIN':
			self.SetClientSize(widget.size)
			#self.SetPosition(widget.pos)
			self.SetBackgroundColour(widget.background_color)
			#self.SetForegroundColour(widget.text_color)
			if widget.statusbar:
				self.CreateStatusBar()

			return

		ctrl = None
		style = 0

		if widget.border:
			style = {'none': wx.NO_BORDER, 'line': wx.SIMPLE_BORDER, 'sunken': wx.SUNKEN_BORDER}[widget.border]

		try:
			align_styles = widget.align.split('-')
			if 'left' in align_styles:
				style &= wx.ALIGN_LEFT
			if 'right' in align_styles:
				style &= wx.ALIGN_RIGHT
			if 'top' in align_styles:
				style &= wx.ALIGN_TOP
			if 'bottom' in align_styles:
				style &= wx.ALIGN_BOTTOM
			if 'center' in align_styles:
				style &= wx.TEXT_ALIGNMENT_CENTER
		except AttributeError:
			pass


		if widget.type == 'LABEL':
			ctrl = wx.StaticText(self, wx.ID_ANY, widget.text.replace('\\"', '"'), style = style)

		elif widget.type == 'BUTTON':
			if widget.button_type == 'radio':
				ctrl = wx.RadioButton(self, wx.ID_ANY, widget.text, style = style)
			elif widget.button_type == 'checkbox':
				ctrl = wx.CheckBox(self, wx.ID_ANY, widget.text, style = style)
			else:
				ctrl = buttons.GenButton(self, wx.ID_ANY, widget.text, style = style)

		elif widget.type == 'CHILD':
			ctrl = wx.Panel(self, wx.ID_ANY, style = style)

		elif widget.type == 'BROWSER':
			ctrl = wx.Panel(self, wx.ID_ANY, style = style)

		elif widget.type == 'INPUT':
			ctrl = wx.TextCtrl(self, wx.ID_ANY, widget.command, style = style)

		elif widget.type == 'OUTPUT':
			ctrl = wx.TextCtrl(self, wx.ID_ANY, style = style)

		else:
			return

		ctrl.SetPosition(widget.pos)
		ctrl.SetBackgroundColour(widget.background_color)
		ctrl.SetForegroundColour(widget.text_color)

		font_size, font_family = 9, 'sans-serif'
		if widget.font_size:
			font_size = widget.font_size
		if widget.font_family:
			font_family = widget.font_family
			print font_family
		font = wx.Font(font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, font_family)
		font.SetNoAntiAliasing(True)
		ctrl.SetFont(font)

		ctrl.SetSize(widget.size)

		ctrl.__dmide_ctrl = widget
		self.ctrls.append(ctrl)

		#ctrl.Bind(wx.EVT_PAINT, self.on_widget_paint)



class Inner(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)


		'''
		sav += '\t\tanchor2 = %s\n' % anchor
		sav += '\t\tfont-family = "%s"\n' % self.font_family
		sav += '\t\tfont-size = %s\n' % self.font_size
		sav += '\t\tfont-style = "%s"\n' % ''.join(self.font_style)
		sav += '\t\ttext-color = %s\n' % self.text_color
		sav += '\t\tbackground-color = %s\n' % self.background_color
		sav += '\t\tis-visible = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_visible]
		sav += '\t\tis-disabled = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_disabled]
		sav += '\t\tis-transparent = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_transparent]
		sav += '\t\tis-default = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_default]
		sav += '\t\tborder = %s\n' % self.border
		sav += '\t\tdrop-zone = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.drop_zone]
		sav += '\t\tright-click = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.right_click]
		sav += '\t\tsaved-params = "%s"\n' % self.saved_params
		'''

		'''
		if self.type == 'MAIN':
			sav += '\t\ttitle = "%s"\n' % self.title
			sav += '\t\ttitlebar = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.titlebar]
			sav += '\t\tstatusbar = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.statusbar]
			sav += '\t\tcan-close = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.can_close]
			sav += '\t\tcan-minimize = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.can_minimize]
			sav += '\t\tcan-resize = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.can_resize]
			sav += '\t\tis-pane = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_pane]
			sav += '\t\tis-minimized = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_minimized]
			sav += '\t\tis-maximized = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_maximized]
			sav += '\t\tcan-scroll = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.can_scroll]
			sav += '\t\ticon = "%s"\n' % self.icon
			sav += '\t\timage = "%s"\n' % self.image
			sav += '\t\timage-mode = %s\n' % self.image_mode
			sav += '\t\tkeep-aspect = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.keep_aspect]
			sav += '\t\ttransparent-color = %s\n' % self.transparent_color
			sav += '\t\talpha = %s\n' % self.alpha
			sav += '\t\tmacro = "%s"\n' % self.macro
			sav += '\t\tmenu = "%s"\n' % self.menu
			sav += '\t\ton-close = "%s"\n' % self.on_close

		elif self.type == 'LABEL':
			sav += '\t\ttext = "%s"\n' % self.text
			sav += '\t\timage = "%s"\n' % self.image
			sav += '\t\tstretch = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.stretch]
			sav += '\t\tkeep-aspect = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.keep_aspect]
			sav += '\t\talign = %s\n' % self.align
			sav += '\t\ttext-wrap = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.text_wrap]

		elif self.type == 'BUTTON':
			sav += '\t\ttext = "%s"\n' % self.text
			sav += '\t\timage = "%s"\n' % self.image
			sav += '\t\tcommand = "%s"\n' % self.command
			sav += '\t\tis-flat = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.is_flat]
			sav += '\t\tstretch = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.stretch]
			sav += '\t\tis-checked = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.is_checked]
			sav += '\t\tgroup = "%s"\n' % self.group
			sav += '\t\tbutton-type = %s\n' % self.button_type

			'''


if __name__ == '__main__':
	a = wx.App(0)
	w = Window()
	w.Show(True)
	a.MainLoop()