import core
from core import *


class DMCodeEditor(wxStc.StyledTextCtrl):
	""" Handles code editing. """

	styles = {wxStc.STC_STYLE_DEFAULT:      ['Courier', 10, '#000000', '#FFFFFF', False, False, False],
			   wxStc.STC_STYLE_LINENUMBER:  ['Courier',  8, '#000000', '#888888', False, False, False],
			   wxStc.STC_STYLE_CONTROLCHAR: ['Courier', 10, '#000000', '#FFFFFF', False, False, False],
			   wxStc.STC_STYLE_BRACELIGHT:  ['Courier', 10, '#000000', '#FFFFFF', True, False, False],
			   wxStc.STC_C_DEFAULT:         ['Courier', 10, '#000000', '#FFFFFF', False, False, False],
			   wxStc.STC_C_COMMENT:         ['Courier', 10, '#808080', '#FFFFFF', False, False, False],
			   wxStc.STC_C_COMMENTLINE:     ['Courier', 10, '#808080', '#FFFFFF', False, False, False],
			   wxStc.STC_C_PREPROCESSOR:    ['Courier', 10, '#008000', '#FFFFFF', False, False, False],
			   wxStc.STC_C_STRING:          ['Courier', 10, '#0096B4', '#FFFFFF', False, False, False],
			   wxStc.STC_C_STRINGEOL:       ['Courier', 10, '#000000', '#0096B4', False, False, False],
			   wxStc.STC_C_NUMBER:          ['Courier', 10, '#800000', '#FFFFFF', False, False, False],
			   wxStc.STC_C_WORD:            ['Courier', 10, '#0000FF', '#FFFFFF', False, False, False],
			   wxStc.STC_C_OPERATOR:        ['Courier', 10, '#000000', '#FFFFFF', False, False, False]
			  }

	def __init__(self, parent, file):
		wxStc.StyledTextCtrl.__init__(self, parent)

		self.initBinds()
		self.initStyle()
		self.save_text = file
		self.SetText(file)
		self.EmptyUndoBuffer()
		self.setSavePoint()

	def initBinds(self):
		""" Assign event handlers. """

		self.Bind(wxStc.EVT_STC_UPDATEUI, self.OnUpdateUI)
		self.Bind(wxStc.EVT_STC_CHANGE, self.OnChange)

	def initStyle(self):
		""" Set the STC styling. """

		self.SetLexer(wxStc.STC_LEX_CPP)

		self.SetViewWhiteSpace(False)
		self.SetBufferedDraw(True)
		self.SetIndentationGuides(True)
		self.SetViewEOL(False)
		self.SetEOLMode(wxStc.STC_EOL_CRLF)
		self.SetUseAntiAliasing(False)
		self.SetTabWidth(4)

		self.SetMargins(4, 0)
		self.SetMarginType(1, wxStc.STC_MARGIN_NUMBER)
		self.SetMarginWidth(1, 25)

		#def hex(r,g,b): return '#%02.X%02.X%02.X' % (r, g, b)
		keywords = ['break', 'new', 'del', 'for', 'global', 'var', 'proc', 'verb', 'set',
					'static', 'arg', 'const', 'goto', 'if', 'in', 'as', 'continue', 'return',
					'do', 'while', 'else', 'switch', 'tmp', 'to']

		self.SetKeyWords(0, ' '.join(keywords))

		'''
		style = {'face': wx.SystemSettings.GetFont(wx.SYS_ANSI_FIXED_FONT).GetFaceName(),
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
		'''

	def updateAllStyles(self):
		""" Used to tell the general editor to update all code editor styles. """

		wx.FindWindowById(ID_EDITOR).updateAllStyles()

	def updateStyle(self, obj):
		""" Copy the STC styling from the empty code editor that the general editor owns. """

		if obj:
			self.SetViewWhiteSpace(obj.GetViewWhiteSpace())
			self.SetBufferedDraw(obj.GetBufferedDraw())
			self.SetIndentationGuides(obj.GetIndentationGuides())
			self.SetViewEOL(obj.GetViewEOL())
			self.SetUseAntiAliasing(obj.GetUseAntiAliasing())
			self.SetMarginWidth(1, obj.GetMarginWidth(1))

		def getstyle(style):
			s = self.styles[style]
			style = 'face:%s,size:%s,fore:%s,back:%s' % (s[0], s[1], s[2], s[3])
			if s[4]: style += ',bold'
			if s[5]: style += ',italic'
			if s[6]: style += ',underline'
			return style

		for style in self.styles:
			#self.StyleSetSpec(style, getstyle(style))

			values = self.styles[style]
			self.StyleSetFaceName(style, values[0])
			self.StyleSetSize(style, values[1])
			self.StyleSetForeground(style, values[2])
			self.StyleSetBackground(style, values[3])
			self.StyleSetBold(style, values[4])
			self.StyleSetItalic(style, values[5])
			self.StyleSetUnderline(style, values[6])

	def setSavePoint(self):
		""" Update the code editor's save point. """

		self.SetSavePoint()
		self.save_text = self.GetText()
		self.OnChange(None)

	def OnChange(self, event):
		""" Update the modified state. """

		editor = wx.FindWindowById(ID_EDITOR)

		if self.GetText() != self.save_text:
			editor.isEdited(self)
		else:
			editor.isEdited(self, False)

	def OnUpdateUI(self, evt):
		""" Highlight matching braces. """

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

	def save(self, path):
		""" Save the code to the path specified. """

		open(path, 'w').write(self.GetText())
		self.setSavePoint()
