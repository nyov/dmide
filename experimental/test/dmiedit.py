import wx



class Test(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.Bind(wx.EVT_PAINT, self.OnPaint)

	def OnPaint(self, event):
		test_bg = wx.Bitmap('test_bg.png')
		test_img = wx.Bitmap('example.png')
		test = wx.EmptyBitmapRGBA(128, 128, 255, 255, 255, 155)

		dc = wx.MemoryDC(test)
		dc.SetPen(wx.Pen( wx.Colour(255, 0, 0, 255), 1))
		dc.DrawCircle(16, 64, 32)
		dc.DrawLine(10, 10, 100, 100)
		dc.SelectObject(wx.NullBitmap)

		dc = wx.PaintDC(self)
		dc.DrawBitmap(test_bg, 0, 0)
		dc.DrawBitmap(test_img, 0, 0, True)
		dc.DrawBitmap(test, 0, 0, True)



if __name__ == '__main__':
	app = wx.App(0)

	win = wx.Frame(None)
	win.Show(True)

	panel = Test(win)

	win.SetSize((400, 300))

	app.MainLoop()