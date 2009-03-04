#-------------------------------------------------------------------

import core
from core import *
from wx import stc as wxStc

#-------------------------------------------------------------------

class DMFrame(wxAui.AuiNotebook):
	''' Overseer of all editors [icon, code, map, and skin] '''

#-------------------------------------------------------------------

	def __init__(self, parent):
		wxAui.AuiNotebook.__init__(self, parent, ID_EDITOR, style = wxAui.AUI_NB_TAB_SPLIT | wxAui.AUI_NB_TAB_MOVE | wxAui.AUI_NB_SCROLL_BUTTONS | wxAui.AUI_NB_CLOSE_ON_ALL_TABS | wx.NO_BORDER)

		self.initBindings()

#-------------------------------------------------------------------

	def initBindings(self):
		pass

#-------------------------------------------------------------------

	def openFile(self, file):
		''' Create a new tab and load the file contents '''

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

		self.Bind(wxStc.EVT_STC_UPDATEUI, self.OnUpdateUI)
		self.initStyle()
		self.SetText(file)

	def initStyle(self):
		self.SetLexer(wxStc.STC_LEX_CPP)

		self.SetViewWhiteSpace(False)
		self.SetBufferedDraw(True)
		self.SetViewEOL(False)
		self.SetEOLMode(wxStc.STC_EOL_CRLF)
		self.SetUseAntiAliasing(False)
		self.SetTabWidth(4)

		self.SetMargins(4, 1)
		self.SetMarginType(1, wxStc.STC_MARGIN_NUMBER)
		self.SetMarginWidth(1, 25)

		def hex(r,g,b): return '#%02.X%02.X%02.X' % (r, g, b)
		keywords = ['break', 'new', 'del', 'for', 'global', 'var', 'proc', 'verb', 'set',
					'static', 'arg', 'const', 'goto', 'if', 'in', 'as', 'continue', 'return',
					'do', 'while', 'else', 'switch', 'tmp', 'to']

		self.SetKeyWords(0, ' '.join(keywords))

		style = {'face': 'Courier',
				 'size': 10,
				 'fore': hex(0, 0, 0),
				 'back': hex(255, 255, 255)
				}

		def getstyle(fore = style['fore'], back = style['back'], face = style['face'], size = style['size']):
			return {'fore': fore, 'back': back, 'face': face, 'size': size}

		self.StyleSetSpec(wxStc.STC_STYLE_DEFAULT,     'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle())
		self.StyleSetSpec(wxStc.STC_STYLE_LINENUMBER,  'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(back = '#888888', size = 8))
		self.StyleSetSpec(wxStc.STC_STYLE_CONTROLCHAR, 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle())
		self.StyleSetSpec(wxStc.STC_STYLE_BRACELIGHT,  'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s,bold' % getstyle())
		self.StyleSetSpec(wxStc.STC_STYLE_BRACEBAD,    'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s,bold' % getstyle())

		self.StyleSetSpec(wxStc.STC_C_DEFAULT, 		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle() )
		self.StyleSetSpec(wxStc.STC_C_COMMENT, 		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(hex(128, 128, 128)) )
		self.StyleSetSpec(wxStc.STC_C_COMMENTLINE,  'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(hex(128, 128, 128)) )
		self.StyleSetSpec(wxStc.STC_C_PREPROCESSOR, 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(hex(0,   128, 0)) )
		self.StyleSetSpec(wxStc.STC_C_STRING, 		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(hex(0,   150, 180)) )
		self.StyleSetSpec(wxStc.STC_C_STRINGEOL, 	 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s,eol' % getstyle(back = hex(0,   150, 180), fore = hex(0, 0, 0)) )
		self.StyleSetSpec(wxStc.STC_C_NUMBER, 		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle('#800000') )
		self.StyleSetSpec(wxStc.STC_C_WORD, 		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(hex(0,   0,   255)) )
		self.StyleSetSpec(wxStc.STC_C_OPERATOR,		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle() )

	def OnUpdateUI(self, evt):
		# check for matching braces
		braceAtCaret = -1
		braceOpposite = -1
		charBefore = None
		caretPos = self.GetCurrentPos()

		if caretPos > 0:
			charBefore = self.GetCharAt(caretPos - 1)
			styleBefore = self.GetStyleAt(caretPos - 1)

		# check before
		if charBefore and chr(charBefore) in "[]{}()" and styleBefore == wxStc.STC_C_OPERATOR:
			braceAtCaret = caretPos - 1

		# check after
		if braceAtCaret < 0:
			charAfter = self.GetCharAt(caretPos)
			styleAfter = self.GetStyleAt(caretPos)

			if charAfter and chr(charAfter) in "[]{}()" and styleAfter == wxStc.STC_C_OPERATOR:
				braceAtCaret = caretPos

		if braceAtCaret >= 0:
			braceOpposite = self.BraceMatch(braceAtCaret)

		if braceAtCaret != -1  and braceOpposite == -1:
			self.BraceBadLight(braceAtCaret)
		else:
			self.BraceHighlight(braceAtCaret, braceOpposite)

#-------------------------------------------------------------------