
from id import *
import wx.stc as stc
import os

class CodePage(wx.TextCtrl):
	def __init__(self, parent, notebook_page):
		wx.TextCtrl.__init__(self, parent, -1, style = wx.TE_MULTILINE | wx.TE_RICH2)

		self.original_content = ''
		self.notebook_page = notebook_page

		wx.CallLater(100, self.OnChange)

	def OnChange(self, event = None):
		self.CheckChange()
		if event:
			event.Skip()
		x, y = self.PositionToXY(self.GetInsertionPoint())
		self.GetParent().GetParent().statusbar.SetStatusText('%.4i' % x, 1)
		self.GetParent().GetParent().statusbar.SetStatusText('%.4i' % (y + 1), 2)

		wx.CallLater(25, self.OnChange)

	def OnSave(self, event):
		self.original_content = self.GetValue()
		self.CheckChange()

	def CheckChange(self):
		if self.GetValue() != self.original_content:
			self.notebook_page.OnChange(True)
			return 0
		else:
			self.notebook_page.OnChange(False)
			return 1