import wx


class DMICanvas(wx.Panel):
	def __init__(self, root):
		wx.Panel.__init__(self, root, style = wx.SIMPLE_BORDER)

		self.init()
		self.initBinds()

	def init(self):
		self.buffer = wx.Bitmap('example.png')
		self.background = wx.Bitmap('bg.png')

		self.action_mouse_position = (-1, -1)
		self.current_mouse_position = (-1, -1)

		self.zoom_level = -1
		self.SetZoom(10)

	def initBinds(self):
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseAction)

	def OnPaint(self, dc):

		# sizes to be used
		width, height = self.buffer.GetWidth(), self.buffer.GetHeight()
		zoom_width, zoom_height = width * self.zoom_level, height * self.zoom_level

		# compact the background and buffer together
		temp = wx.EmptyBitmap(width, height)
		dc = wx.MemoryDC(temp)
		dc.DrawBitmap(self.background, 0, 0)
		dc.DrawBitmap(self.buffer, 0, 0, True)

		# draw pending action
		if self.action_mouse_position != (-1, -1):
			pos1, pos2 = self.TrueCoords(self.action_mouse_position), self.TrueCoords(self.current_mouse_position)
			#print 'Draw Line: %i, %i  to  %i, %i' % (pos1[0], pos1[1], pos2[0], pos2[1])
			dc.DrawLine(pos1[0], pos1[1], pos2[0], pos2[1])

		dc.SelectObject(wx.NullBitmap)

		# paint onto screen
		dc = wx.BufferedPaintDC(self, wx.EmptyBitmap(zoom_width, zoom_height))
		dc.SetUserScale(1.0 * self.zoom_level, 1.0 * self.zoom_level)
		dc.DrawBitmap(temp, 0, 0)
		dc.SetUserScale(1.0, 1.0)


	def SetZoom(self, zoom_level):

		# avoid extra calcs
		if zoom_level == self.zoom_level or zoom_level <= 0:
			return

		self.zoom_level = zoom_level
		self.GetParent().SetSize((self.buffer.GetWidth() * self.zoom_level + 8, self.buffer.GetHeight() * self.zoom_level + 34))
		self.Refresh(True)

	def OnMouseAction(self, event):
		self.current_mouse_position = event.GetPosition()

		# Zoom into the canvas
		if event.GetWheelRotation() and self.action_mouse_position == (-1, -1):
			if event.GetWheelRotation() > 0:
				self.SetZoom(self.zoom_level + 1)
				return
			else:
				self.SetZoom(self.zoom_level - 1)
				return

		if event.LeftDown():
			# action_mouse_position is where the initial click happened
			self.action_mouse_position = event.GetPosition()
			self.CaptureMouse()
		elif event.LeftUp():
			# finish action
			self.action_mouse_position = (-1, -1)
			self.Refresh(False)
			self.ReleaseMouse()
		elif event.Dragging() and event.LeftIsDown():
			# update action
			self.Refresh(False)

	def TrueCoords(self, coords):
		# rescale the coordinates according to zoom
		return (coords[0] / self.zoom_level, coords[1] / self.zoom_level)


if __name__ == '__main__':
	a = wx.App(0)
	w = wx.Frame(None, title = 'DMI Editor', size = (32 * 8 + 8, 32 * 8 + 34))
	w.SetBackgroundColour('WHITE')
	c = DMICanvas(w)

	sizer = wx.BoxSizer(wx.VERTICAL)
	sizer.Add(c, 1, wx.ALL | wx.EXPAND, 10)
	w.SetSizerAndFit(sizer)

	w.Show(True)
	a.MainLoop()