import core
from core import *


class DMIDE_Painter(wx.Panel):
	def __init__(self, root):
		wx.Panel.__init__(self, root, id=ID_PAINTER)

		self.palette = Palette(self)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.AddSpacer((20, 20))
		sizer.Add(self.palette, 1, wx.ALL|wx.EXPAND)
		sizer.AddSpacer((20, 20))
		self.SetSizer(sizer)

	def update(self, icon):
		pass


class Palette(wx.CollapsiblePane):
	def __init__(self, root):
		wx.CollapsiblePane.__init__(self, root, size=(200,200), label='^', style=wx.CP_DEFAULT_STYLE)

	def update(self, icon):
		pass
