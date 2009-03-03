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
		self.output = wx.TextCtrl(self, style = wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_RICH2)
		self.output.SetEditable(False)

		self.input = wx.TextCtrl(self, style = wx.TE_PROCESS_ENTER)

		self.style_1 = wx.TextAttr('BLACK', wx.NullColour, wx.Font(8, wx.TELETYPE, wx.NORMAL, wx.NORMAL))
		self.style_2 = wx.TextAttr('PURPLE', wx.NullColour, wx.Font(8, wx.TELETYPE, wx.NORMAL, wx.BOLD))
		self.style_3 = wx.TextAttr('RED', wx.NullColour, wx.Font(8, wx.ROMAN, wx.NORMAL, wx.BOLD))

		self.message('INTERACTIVE DEVELOPER CONSOLE. USE CAUTION.', self.style_3)
		self.message('', self.style_3)
		self.message('system\n\t%s' % sys.platform, self.style_1)
		self.message('python\n\t%s' % sys.version, self.style_1)
		self.message('wx\n\t%s' % wx.__version__, self.style_1)
		self.message('', self.style_3)

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

		self.message('>>> %s' % text, self.style_2)

		self.evaluate(text)

#-------------------------------------------------------------------

	def evaluate(self, command):
		text = ''
		try:
			evaluated = eval(command, globals(), locals())
			text = repr(evaluated)
		except Exception, e:
			text = repr(e)

		self.message(text, self.style_1)

#-------------------------------------------------------------------

	def message(self, message, style = None):
		if not len(message) or message[-1] != '\n':
			message = '%s\n' % message

		self.output.SetEditable(True)
		self.output.AppendText(message)

		if style:
			length = len(self.output.GetValue())
			self.output.SetStyle(length - len(message), length, style)

		self.output.SetEditable(False)

#-------------------------------------------------------------------