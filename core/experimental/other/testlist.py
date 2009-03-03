import wx



class Window(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, wx.ID_ANY, 'Virtual List Test')
		self.Show(True)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(VirtualList(self), 1, wx.EXPAND | wx.ALL)
		self.SetSizerAndFit(sizer)
		self.Center()



class VirtualList(wx.ListCtrl):
	def __init__(self, root):
		wx.ListCtrl.__init__(self, root, wx.ID_ANY, style = wx.LC_ICON | wx.LC_VIRTUAL | wx.LC_EDIT_LABELS | wx.LC_SINGLE_SEL)

		self.SetMinSize((400, 200))
		self.InsertColumn(0, 'Test', width = -1)
		self.SetItemCount(1000)

		self.last_pos = -1

		self.img = wx.BitmapFromImage(wx.Image('./test.png'))
		self.imglist = wx.ImageList(32, 32)
		self.a = self.imglist.Add(self.img)
		self.AssignImageList(self.imglist, wx.IMAGE_LIST_NORMAL)

		self.Bind(wx.EVT_SIZE, self.OnSize)

	def OnGetItemText(self, row, col):
		return 'test'

	def OnGetItemImage(self, index):
		return self.a

	def OnGetItemAttr(self, index):
		return None

	def OnSize(self, event):
		event.Skip()
		last_pos = self.GetItemRect(self.GetItemCount() - 1)
		if self.last_pos != last_pos:
			self.last_pos = last_pos
			self.Refresh()



if __name__ == '__main__':
	app = wx.App(0)
	win = Window()
	app.MainLoop()