import wx
import dmi



class IconExtendedPreview(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.SetBackgroundColour(wx.Colour(188, 188, 188))

		self.initAll()
		self.initConstraints()

	def initAll(self):
		self.delay_text = wx.StaticText(self, wx.ID_ANY, 'Delay')
		self.arrow_down = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_down.png')))
		self.arrow_up = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_up.png')))
		self.arrow_right = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_right.png')))
		self.arrow_left = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_left.png')))
		self.arrow_bottomright = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_bottomright.png')))
		self.arrow_bottomleft = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_bottomleft.png')))
		self.arrow_topright = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_topright.png')))
		self.arrow_topleft = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(wx.Image('./imgs/viewer/arrow_topleft.png')))

		self.direction_images = [self.arrow_down, self.arrow_up, self.arrow_right, self.arrow_left, 
								 self.arrow_bottomright, self.arrow_bottomleft, self.arrow_topright, self.arrow_topleft]

		for img in self.direction_images:
			img.Hide()

		self.icon = None

	def initConstraints(self, dirs = 0):
		if self.GetSizer():
			self.GetSizer().Clear(False)
			sizer = self.GetSizer()

		else:
			sizer = wx.GridBagSizer(16, 16)

		for img in self.direction_images:
			img.Hide()

		if dirs > 0:
			sizer.Add(self.delay_text, (0, 0), border = 2)
			sizer.Add(self.arrow_down, (1, 0), border = 2)
			if dirs > 3:
				sizer.Add(self.arrow_up, (2, 0), border = 2)
				sizer.Add(self.arrow_right, (3, 0), border = 2)
				sizer.Add(self.arrow_left, (4, 0), border = 2)
				if dirs > 7:
					sizer.Add(self.arrow_bottomright, (5, 0), border = 2)
					sizer.Add(self.arrow_bottomleft, (6, 0), border = 2)
					sizer.Add(self.arrow_topright, (7, 0), border = 2)
					sizer.Add(self.arrow_topleft, (8, 0), border = 2)

		for img_n in xrange(dirs):
			try:
				self.direction_images[img_n].Show()
			except Exception:
				pass

		self.SetSizerAndFit(sizer)

	def displayIcon(self, icon):
		self.icon = icon
		self.initConstraints(icon.dirs)
		sizer = self.GetSizer()

		for dir in xrange(icon.dirs):
			for frame in xrange(icon.frames):
				image = icon.icons[dir][frame]
				sizer.Add(wx.StaticBitmap(self, wx.ID_ANY, self.ImageToBitmap(image)), (dir + 1, frame + 1))

		sizer.Layout()
		self.SetSizerAndFit(sizer)

	def ImageToBitmap(self, pil_img):
		wx_img = wx.EmptyImage(pil_img.size[0], pil_img.size[1])
		wx_img.SetData(pil_img.convert('RGB').tostring())
		wx_img.SetAlphaData(pil_img.convert('RGBA').tostring()[3::4])
		return wx_img.ConvertToBitmap()



if __name__ == '__main__':
	app = wx.App(0)

	Window = wx.Frame(None, wx.ID_ANY, 'IconExtendedPreview Test')

	sizer = wx.BoxSizer(wx.VERTICAL)
	sizer.Add(IconExtendedPreview(Window), 1, wx.ALL | wx.EXPAND)
	Window.SetSizerAndFit(sizer)

	Window.Show(True)

	app.MainLoop()