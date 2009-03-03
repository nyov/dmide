#-------------------------------------------------------------------

import core
from core import *
from wx import stc as wxStc

#-------------------------------------------------------------------

class DMFrame(wxAui.AuiNotebook):
	""" Overseer of all editors [icon, code, map, and skin] """

#-------------------------------------------------------------------

	def __init__(self, parent):
		wxAui.AuiNotebook.__init__(self, parent, ID_EDITOR, style = wxAui.AUI_NB_TAB_SPLIT | wxAui.AUI_NB_TAB_MOVE | wxAui.AUI_NB_SCROLL_BUTTONS | wxAui.AUI_NB_CLOSE_ON_ALL_TABS | wx.NO_BORDER)

		self.initBindings()

#-------------------------------------------------------------------

	def initBindings(self):
		pass

#-------------------------------------------------------------------

	def openFile(self, file):
		""" Create a new tab and load the file contents """

		if not os.path.isfile(file):
			return

		def newPage(file):
			dm_art = wx.GetApp().dm_art

			for x in xrange(self.GetPageCount()):
				if self.GetPage(x).file_path == file:
					return

			name = os.path.split(file)[-1]
			icon = dm_art.getFromExt(os.path.splitext(name)[-1])
			page = DMDemo(self, open(file).read())
			page.file_path = file

			if type(icon) == int:
				icon = dm_art.getFromWx(wx.ART_NORMAL_FILE)

			self.AddPage(page, name, True, icon)

		extension = os.path.splitext(file)[-1]
		if extension in ['.dm', '.dmm', '.dmp', '.dms', '.dmf', '.dme']:
			newPage(file)

		elif not '\0' in open(file).read():
			newPage(file)

#-------------------------------------------------------------------

class DMDemo(wxStc.StyledTextCtrl):
	def __init__(self, parent, file):
		wxStc.StyledTextCtrl.__init__(self, parent)

		self.SetMargins(4, 1)

		self.SetViewWhiteSpace(False)
		
		self.SetEdgeMode(wxStc.STC_EDGE_BACKGROUND)
		self.SetEdgeColumn(78)

		self.SetMarginType(1, wxStc.STC_MARGIN_NUMBER)
		self.SetMarginWidth(1, 25)

		self.StyleSetSpec(wxStc.STC_STYLE_DEFAULT, 'face:%s,size:%s' % ('Courier', 10))

		self.SetText(file)