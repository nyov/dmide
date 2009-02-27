import wx
import math


MOUSE_DOWN = wx.NewId()
MOUSE_UP = wx.NewId()

TOOL_LINE = wx.NewId()
TOOL_CIRCLE = wx.NewId()


class PaintCanvas(wx.Panel):
	def __init__(self, master):
		wx.Panel.__init__(self, master, wx.ID_ANY)

		self.mouse_pos = (0, 0)

		
		self.SetSize((256, 256))

		self.buffer = wx.EmptyBitmap(self.GetSize()[0], self.GetSize()[1])

		self.right_mouse_state = MOUSE_UP
		self.left_mouse_state = MOUSE_UP

		self.tool = TOOL_LINE
		self.brush_size = 1
		self.pen = wx.Pen((255, 0, 0), 1)
		self.brush = wx.TRANSPARENT_BRUSH

		self.mouse_pos = (0, 0)
		self.action_mouse_pos = (-1, -1)

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseAction)
		self.Bind(wx.EVT_LEFT_UP, self.OnMouseAction)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseAction)
		self.Bind(wx.EVT_RIGHT_UP, self.OnMouseAction)
		self.Bind(wx.EVT_MOTION, self.OnMouseAction)
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyAction)

	def OnPaint(self, event):
		tmpBuffer = self.buffer.GetSubBitmap((0, 0, self.GetSize()[0], self.GetSize()[1]))

		dc = wx.BufferedPaintDC(self, tmpBuffer)

		if self.left_mouse_state == MOUSE_DOWN:
			self.Draw(dc)		

	def OnMouseAction(self, event):
		self.mouse_pos = (event.GetX(), event.GetY())

		if event.ButtonDown():
			if event.LeftDown():
				self.action_mouse_pos = self.mouse_pos
				self.left_mouse_state = MOUSE_DOWN
			elif event.RightDown():
				if self.tool == TOOL_CIRCLE:
					self.tool = TOOL_LINE
				elif self.tool == TOOL_LINE:
					self.tool = TOOL_CIRCLE

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
		if event.GetKeyCode() == 50:
			if self.brush_size < 100:
				self.brush_size += 1
		elif event.GetKeyCode() == 49:
			if self.brush_size > 1:
				self.brush_size -= 1
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

		dc.SetPen(pen)
		dc.SetBrush(brush)

		if tool == TOOL_LINE:
			dc.DrawLine(point1[0], point1[1], point2[0], point2[1])

		elif tool == TOOL_CIRCLE:
			radius = math.sqrt((point1[0] - point2[0]) ** 2 +
							   (point1[1] - point2[1]) ** 2)

			dc.DrawCircle(point2[0], point2[1], radius)

if __name__ == '__main__':
	app = wx.App(0)
	frame = wx.Frame(None, wx.ID_ANY, title = 'Paint Test')

	sizer = wx.BoxSizer(wx.VERTICAL)

	canvas = PaintCanvas(frame)

	sizer.Add(canvas)

	frame.SetSizerAndFit(sizer)
	frame.SetMinSize((frame.GetSize()[0], frame.GetSize()[1]))
	frame.Show(True)
	app.MainLoop()