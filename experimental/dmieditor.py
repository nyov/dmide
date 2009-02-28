import wx



class DMIEditor(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None)

		self.SetTitle('DMI Editor Demo')
		self.SetBackgroundColour('WHITE')
		self.Show(True)

		self.init()
		self.initSizer()

	def init(self):
		self.dmi_canvas = DMICanvas(self)

		self.status_bar = wx.StatusBar(self)
		self.status_bar.SetFieldsCount(4)
		self.SetStatusBar(self.status_bar)
		self.UpdateStatusBar()

	def initSizer(self):
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.dmi_canvas, 1, wx.ALL | wx.EXPAND, 10)
		self.SetSizerAndFit(sizer)

	def UpdateStatusBar(self):
		size = self.dmi_canvas.buffer.GetSize()
		zoom = self.dmi_canvas.zoom_level
		action = self.dmi_canvas.TrueCoords(self.dmi_canvas.action_mouse_position)
		mouse = self.dmi_canvas.TrueCoords(self.dmi_canvas.current_mouse_position)

		self.SetStatusText('Size: %i, %i' % (size[0], size[1]), 0)
		self.SetStatusText('Zoom: %ix' % zoom, 1)
		self.SetStatusText('Mouse: %i, %i' % (mouse[0] + 1, mouse[1] + 1), 2)
		self.SetStatusText('Action: %i, %i' % (action[0] + 1, action[1] + 1), 3)



class DMICanvas(wx.Panel):
	def __init__(self, root):
		wx.Panel.__init__(self, root, style = wx.SIMPLE_BORDER)

		self.init()
		self.initBinds()

	def init(self):
		self.buffer = wx.Bitmap('./imgs/dmieditor/example.png')
		self.background = wx.Bitmap('./imgs/dmieditor/bg.png')

		self.action_mouse_position = (-1, -1)
		self.current_mouse_position = (-1, -1)

		self.zoom_level = -1
		self.SetZoom(10)

	def initBinds(self):
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseAction)
		self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseAction)

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
		self.SetMinSize((self.buffer.GetWidth() * self.zoom_level + 2, self.buffer.GetHeight() * self.zoom_level + 2))
		self.Refresh(True)

	def OnMouseAction(self, event):
		self.current_mouse_position = event.GetPosition()

		# Zoom into the canvas
		if event.GetWheelRotation() and self.action_mouse_position == (-1, -1):
			if event.GetWheelRotation() > 0:
				self.SetZoom(self.zoom_level + 1)
			else:
				self.SetZoom(self.zoom_level - 1)

		elif event.LeftDown():
			# action_mouse_position is where the initial click happened
			self.action_mouse_position = event.GetPosition()
			self.CaptureMouse()

		elif event.LeftUp():
			# finish action
			self.action_mouse_position = (-1, -1)
			self.Refresh(False)
			if self.GetCapture() == self:
				self.ReleaseMouse()

		elif event.Dragging() and event.LeftIsDown():
			# update action
			self.Refresh(False)

		self.GetParent().UpdateStatusBar()

	def TrueCoords(self, coords):
		# rescale the coordinates according to zoom
		return (coords[0] / self.zoom_level, coords[1] / self.zoom_level)



if __name__ == '__main__':
	a = wx.App(0)
	DMIEditor()
	a.MainLoop()