import wx
import math


MOUSE_DOWN = wx.NewId()
MOUSE_UP = wx.NewId()

TOOL_LINE = wx.NewId()
TOOL_CIRCLE = wx.NewId()

PAINT_ALWAYS = wx.NewId()
PAINT_CLICK = wx.NewId()


class PaintCanvas(wx.Window):
	def __init__(self, master):
		wx.Window.__init__(self, master, wx.ID_ANY)

		self.master = master
		self.width = 256
		self.height = 256
		self.SetSize((self.width, self.height))
		self.paint_mode = PAINT_ALWAYS

		self.buffer = wx.EmptyBitmap(self.width, self.height)

		self.right_mouse_state = MOUSE_UP
		self.left_mouse_state = MOUSE_UP

		self.tool = TOOL_LINE
		self.brush_size = 1
		self.pen = wx.Pen((255, 0, 0), 1)
		self.brush = wx.TRANSPARENT_BRUSH

		self.mouse_pos = (0, 0)
		self.action_mouse_pos = (-1, -1)
		self.last_action_mouse_pos = (-1, -1)

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseAction)
		self.Bind(wx.EVT_LEFT_UP, self.OnMouseAction)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseAction)
		self.Bind(wx.EVT_RIGHT_UP, self.OnMouseAction)
		self.Bind(wx.EVT_MOTION, self.OnMouseAction)
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyAction)


	def OnPaint(self, event):
		tmpBuffer = self.buffer.GetSubBitmap((0, 0, self.width, self.height))

		dc = wx.BufferedPaintDC(self, tmpBuffer)

		if self.left_mouse_state == MOUSE_DOWN:
			self.Draw(dc)		

	def OnMouseAction(self, event):
		self.mouse_pos = (event.GetX(), event.GetY())

		self.master.UpdateStatusBar(self)

		if event.ButtonDown():
			if event.LeftDown():
				self.action_mouse_pos = self.mouse_pos
				self.left_mouse_state = MOUSE_DOWN
				self.last_action_mouse_pos = self.mouse_pos
			elif event.RightDown():
				if self.tool == TOOL_CIRCLE:
					self.tool = TOOL_LINE
				elif self.tool == TOOL_LINE:
					self.tool = TOOL_CIRCLE
				self.Refresh(False)

		elif event.ButtonUp():
			if event.LeftUp() and self.left_mouse_state == MOUSE_DOWN:
				self.Commit()
				self.action_mouse_pos = (-1, -1)
				self.left_mouse_state = MOUSE_UP
				self.Refresh(False)

		elif event.Moving():
			pass

		elif event.Dragging():
			self.Refresh(False)

	def OnKeyAction(self, event):
		print event.GetKeyCode()

		if event.GetKeyCode() == 50:
			if self.brush_size < 100:
				self.brush_size += 1
		elif event.GetKeyCode() == 49:
			if self.brush_size > 1:
				self.brush_size -= 1

		elif event.GetKeyCode() == 27:
			if self.action_mouse_pos[0] != -1 or self.action_mouse_pos[1] != -1:
				self.action_mouse_pos = (-1, -1)
				self.left_mouse_state = MOUSE_UP
				self.Refresh(False)
		elif event.GetKeyCode() == 32:
			if self.paint_mode == PAINT_ALWAYS:
				self.paint_mode = PAINT_CLICK
			elif self.paint_mode == PAINT_CLICK:
				self.paint_mode = PAINT_ALWAYS

		self.pen = wx.Pen((255, 0, 0), self.brush_size)
		self.Refresh(False)

	def Commit(self):
		dc = wx.MemoryDC()
		dc.SelectObject(self.buffer)
		self.Draw(dc)

	def Draw(self, dc, tool = None, point1 = None, point2 = None, pen = None, brush = None):
		if tool == None:
			tool = self.tool
		if point1 == None:
			point1 = self.mouse_pos
		if point2 == None:
			point2 = self.action_mouse_pos
		if pen == None:
			pen = self.pen
		if brush == None:
			brush = self.brush

		if self.paint_mode == PAINT_CLICK:
			point1 = self.last_action_mouse_pos

		dc.SetPen(pen)
		dc.SetBrush(brush)

		if tool == TOOL_LINE:
			dc.DrawLine(point1[0], point1[1], point2[0], point2[1])

		elif tool == TOOL_CIRCLE:
			radius = math.sqrt((point1[0] - point2[0]) ** 2 +
							   (point1[1] - point2[1]) ** 2)

			dc.DrawCircle(point2[0], point2[1], radius)


class Frame(wx.Frame):
	def __init__(self, *args, **kwargs):
		wx.Frame.__init__(self, *args, **kwargs)

		self.SetAutoLayout(True)
		self.initCanvas()
		self.initStatusBar()
		self.Show(True)

		self.SetMinSize((412, 412))
		self.SetSize((412, 412))

	def initCanvas(self):
		self.canvas = PaintCanvas(self)
		self.canvas.SetBackgroundColour(wx.BLUE)

		lc = wx.LayoutConstraints()
		lc.centreX.PercentOf(self, wx.Width, 50)
		lc.centreY.PercentOf(self, wx.Height, 50)
		lc.width.AsIs()
		lc.height.AsIs()
		self.canvas.SetConstraints(lc)

	def initStatusBar(self):
		self.status_bar = wx.StatusBar(self, wx.ID_ANY)
		self.status_bar.SetFieldsCount(4)
		self.status_bar.SetStatusWidths([-2, -2, -2, -2])
		self.SetStatusBar(self.status_bar)


	def UpdateStatusBar(self, canvas):
		current = '%i,%i' % (canvas.mouse_pos[0], canvas.mouse_pos[1])
		action = '%i,%i - ' % (canvas.action_mouse_pos[0], canvas.action_mouse_pos[1])
		if action == '-1,-1 - ': action = ''
		self.SetStatusText('%s%s' % (action, current), 3)


if __name__ == '__main__':
	app = wx.App(0)
	Frame(None, wx.ID_ANY, title = 'Paint Test')
	app.MainLoop()