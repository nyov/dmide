import wx



class Test(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.Bind(wx.EVT_PAINT, self.OnPaint)

	def OnPaint(self, event):
		test_bg = wx.Bitmap('test_bg.png')
		test_img = wx.Bitmap('example.png')

		dc = wx.PaintDC(self)
		dc.DrawBitmap(test_bg, 0, 0)
		dc.DrawBitmap(test_img, 0, 0, True)



if __name__ == '__main__':
	app = wx.App(0)

	win = wx.Frame(None)
	win.Show(True)

	panel = Test(win)

	win.SetSize((400, 300))

	app.MainLoop()