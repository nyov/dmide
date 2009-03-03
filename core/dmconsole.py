#-------------------------------------------------------------------

import core
from core import *

#-------------------------------------------------------------------

class DMConsole(wx.Panel):
	""" Interactive console for people to tinker with the inner objects of DMIDE. Potentially dangerous! """

#-------------------------------------------------------------------

	def __init__(self, parent):
		wx.Panel.__init__(self, parent, ID_CONSOLE)

		self.initAll()
		self.initConstraints()
		self.initBinds()

#-------------------------------------------------------------------

	def initAll(self):
		self.output = wx.TextCtrl(self, style = wx.NO_BORDER | wx.TE_MULTILINE)

		self.input = wx.TextCtrl(self, style = wx.TE_PROCESS_ENTER)

#-------------------------------------------------------------------

	def initConstraints(self):
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.output, 1, wx.ALL | wx.EXPAND)
		sizer.Add(self.input, 0, wx.ALL | wx.EXPAND)
		self.SetSizer(sizer)

#-------------------------------------------------------------------

	def initBinds(self):
		self.input.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)

#-------------------------------------------------------------------

	def OnTextEnter(self, event):
		text = self.input.GetValue()
		self.input.SetValue('')

		self.output.SetValue(self.output.GetValue() + ('>>> %s' % text) + '\n')

		self.evaluate(text)

#-------------------------------------------------------------------

	def evaluate(self, command):
		text = ''
		try:
			evaluated = eval(command, globals(), locals())
			text = repr(evaluated)
		except Exception, e:
			text = repr(e)

		self.output.SetValue(self.output.GetValue() + text + '\n')

#-------------------------------------------------------------------