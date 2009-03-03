#-------------------------------------------------------------------

import core
from core import *

#-------------------------------------------------------------------

class DMBuildInfo(wx.TextCtrl):
	""" Widget for displaying errors and compiling information """

#-------------------------------------------------------------------

	def __init__(self, parent):
		wx.TextCtrl.__init__(self, parent, ID_BUILDINFORMATION, style = wx.NO_BORDER)

#-------------------------------------------------------------------