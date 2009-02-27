import wx

class Frame(wx.Frame):
	def __init__(self, *args, **kwargs):
		wx.Frame.__init__(self, *args, **kwargs)

		self.bg = wx.Window(self, wx.ID_ANY)
		self.SetAutoLayout(True)
		self.initCanvas()
		self.Show(True)
		#self.SetSizerAndFit(self.GetSizer())

	def initCanvas(self):
		panel = wx.Window(self, wx.ID_ANY, style = wx.SIMPLE_BORDER)
		panel.SetSize((250, 250))
		panel.SetBackgroundColour(wx.BLUE)

		lc = wx.LayoutConstraints()
		#lc.centreX.SameAs(self, wx.CentreX)
		lc.centreX.PercentOf(self, wx.Width, 50)
		lc.centreY.SameAs(self, wx.CentreY)
		lc.width.AsIs()
		lc.height.AsIs()
		panel.SetConstraints(lc)


if __name__ == '__main__':
	app = wx.App(0)
	Frame(None, wx.ID_ANY, title = 'Paint Test')
	app.MainLoop()