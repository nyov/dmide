import wx
from random import randint


class DMICanvas(wx.Panel):
	def __init__(self, root):
		wx.Panel.__init__(self, root)

		self.init()
		self.initBinds()

	def init(self, width = 32, height = 32):
		self.buffer = wx.Image('example.png', wx.BITMAP_TYPE_PNG)
		self.buffer.InitAlpha()
		self.background = None
		self.background_img = wx.Image('bg.png')

		self.mouse_position = (-1, -1)
		self.zoom_level = -1
		self.setZoom(10)

	def initBinds(self):
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseAction)
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyAction)
		self.Bind(wx.EVT_KEY_UP, self.OnKeyAction)

	def OnPaint(self, dc):
		width, height = self.buffer.GetWidth(), self.buffer.GetHeight()
		zoom_width, zoom_height = width * self.zoom_level, height * self.zoom_level

		tmp = self.buffer.Copy()
		tmp = wx.BitmapFromImage(tmp)

		dc = wx.MemoryDC(tmp)
		dc.SetPen(wx.Pen(wx.Colour(255, 0, 0, 255), 1))
		dc.DrawCircle(16, 16, 8)
		dc.SelectObject(wx.NullBitmap)

		tmp = tmp.ConvertToImage()
		tmp.Rescale(zoom_width, zoom_height)
		tmp = wx.BitmapFromImage(tmp)

		dc = wx.BufferedPaintDC(self, self.background)
		dc.DrawBitmap(tmp, 0, 0)
		dc.EndDrawing()

	def setZoom(self, zoom_level):
		if zoom_level == self.zoom_level or zoom_level <= 0:
			return

		self.zoom_level = zoom_level

		tmp = self.background_img.Copy()
		tmp.Rescale(tmp.GetWidth() * self.zoom_level, tmp.GetHeight() * self.zoom_level)
		self.background = wx.BitmapFromImage(tmp)
		self.GetParent().SetSize((self.buffer.GetWidth() * self.zoom_level + 8, self.buffer.GetHeight() * self.zoom_level + 34))
		self.Refresh(True)

	def OnMouseAction(self, event):
		if event.ButtonDown() or event.Dragging():
			x, y = event.GetX(), event.GetY()
			self.mouse_position = x / self.zoom_level, y / self.zoom_level
			self.Refresh(False)

		if event.GetWheelRotation():
			if event.GetWheelRotation() > 0:
				self.setZoom(self.zoom_level + 1)#* 2)
			else:
				self.setZoom(self.zoom_level - 1)#/ 2)

	def OnKeyAction(self, event):
		pass


if __name__ == '__main__':
	a = wx.App(0)
	w = wx.Frame(None, title = 'DMI Editor', size = (32 * 8 + 8, 32 * 8 + 34))

	DMICanvas(w)

	w.Show(True)
	w.Layout()

	a.MainLoop()