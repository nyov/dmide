import core
from core import *


class DMIDE_DMEditor(wxStc.StyledTextCtrl):
	""" Handles code editing. """

	DM_STYLE_DEFAULT = 0
	NOTYPE_STYLE_DEFAULT = DM_STYLE_DEFAULT
	DM_STYLE_COMMENT = 1
	DM_STYLE_COMMENTLINE = 2
	DM_STYLE_PREPROCESSOR = 3
	DM_STYLE_STRING = 4
	DM_STYLE_MULTISTRING = 5
	DM_STYLE_NUMBER = 6
	DM_STYLE_KEYWORD = 7
	DM_STYLE_OPERATOR = 8
	DM_STYLE_EMBEDDED_STRING = 9
	DM_STYLE_EMBEDDED_MULTISTRING = 10
	DM_STYLE_BADSTRING = 11
	DM_STYLE_SINGLESTRING = 12

	styles = {wxStc.STC_STYLE_DEFAULT:		  ['Courier', 10, '#000000', '#FFFFFF', False, False, False],
			   wxStc.STC_STYLE_LINENUMBER:	  ['Courier',  8, '#000000', '#888888', False, False, False],
			   wxStc.STC_STYLE_CONTROLCHAR:	  ['Courier', 10, '#000000', '#FFFFFF', False, False, False],
			   wxStc.STC_STYLE_BRACELIGHT:	  ['Courier', 10, '#000000', '#FFFFFF', True, False, False],
			   DM_STYLE_DEFAULT:			  ['Courier', 10, '#000000', '#FFFFFF', False, False, False],
			   DM_STYLE_COMMENT:			  ['Courier', 10, '#808080', '#FFFFFF', False, False, False],
			   DM_STYLE_COMMENTLINE:		  ['Courier', 10, '#808080', '#FFFFFF', False, False, False],
			   DM_STYLE_PREPROCESSOR:		  ['Courier', 10, '#008000', '#FFFFFF', False, False, False],
			   DM_STYLE_STRING:				  ['Courier', 10, '#0096B4', '#FFFFFF', False, False, False],
			   DM_STYLE_MULTISTRING:		  ['Courier', 10, '#000000', '#0096B4', False, False, False],
			   DM_STYLE_NUMBER:				  ['Courier', 10, '#800000', '#FFFFFF', False, False, False],
			   DM_STYLE_KEYWORD:			  ['Courier', 10, '#FF0000', '#FFFFFF', False, False, False],
			   DM_STYLE_OPERATOR:			  ['Courier', 10, '#000000', '#FFFFFF', False, False, False],
			   DM_STYLE_EMBEDDED_STRING:	  ['Courier', 10, '#004B5A', '#FFFFFF', False, False, False],
			   DM_STYLE_EMBEDDED_MULTISTRING: ['Courier', 10, '#004B5A', '#FFFFFF', False, False, False],
			   DM_STYLE_BADSTRING:			  ['Courier', 10, '#000000', '#FF0000', False, False, False],
			   DM_STYLE_SINGLESTRING:		  ['Courier', 10, '#0096B4', '#FFFFFF', False, False, False],
			  }

	keyword_text = ''

	file_type = ""

	StylingFunc = ""

	def clearErrors(self):
		self.StartStyling(0, wxStc.STC_INDICS_MASK)
		self.SetStyling(self.GetLength(), 0)

	def addError(self, line):
		line -= 1
		start = self.PositionFromLine(line)
		self.StartStyling(start, wxStc.STC_INDIC2_MASK)
		self.SetStyling(self.LineLength(line), 0xFF)

	def __init__(self, parent, type):
		wxStc.StyledTextCtrl.__init__(self, parent, style=wx.NO_BORDER)

		self.file_type = type

		if type == "dm": self.StylingFunc = self.StyleDM
		elif type == "dmf": self.StylingFunc = self.StyleDMF
		else: self.StylingFunc = self.StyleNone

		self.initBinds()
		self.initStyle()

	def initBinds(self):
		""" Assign event handlers. """

		self.Bind(wxStc.EVT_STC_UPDATEUI, self.OnUpdateUI)
		self.Bind(wxStc.EVT_STC_CHANGE, self.OnChange)
		self.Bind(wxStc.EVT_STC_CHARADDED, self.OnCharAdd)
		self.Bind(wxStc.EVT_STC_STYLENEEDED, self.OnStyleNeededDM)
		self.Bind(wxStc.EVT_STC_MARGINCLICK, self.onMarginClick)

	def initStyle(self):
		""" Set the STC styling. """

		self.SetLexer(wxStc.STC_LEX_CONTAINER)

		self.SetLayoutCache(wxStc.STC_CACHE_DOCUMENT)

		self.SetViewWhiteSpace(False)
		self.SetBufferedDraw(True)
		self.SetIndentationGuides(True)
		self.SetViewEOL(False)
		self.SetEOLMode(wxStc.STC_EOL_CRLF)
		self.SetUseAntiAliasing(False)
		self.SetTabWidth(4)

		self.SetMargins(4, 4)

		self.SetMarginType(1, wxStc.STC_MARGIN_SYMBOL)
		self.SetMarginWidth(1, 16)
		self.SetMarginMask(1, wxStc.STC_MASK_FOLDERS)
		self.SetMarginSensitive(1, True)

		self.SetMarginType(0, wxStc.STC_MARGIN_NUMBER)
		self.SetMarginWidth(0, 35)

		def hex(r,g,b): return '#%02.X%02.X%02.X' % (r, g, b)

		if self.file_type == "dm":
			keywords = ['break', 'new', 'del', 'for', 'global', 'var', 'proc', 'verb', 'set',
						'static', 'arg', 'const', 'goto', 'if', 'in', 'as', 'continue', 'return',
						'do', 'while', 'else', 'switch', 'tmp', 'to']
		elif self.file_type == "dmf":
			keywords = ['macro', 'menu', 'window', 'elem', 'false', 'true']

		else: keywords = []

		self.keyword_text = ' ' + ' '.join(keywords) + ' '

		style = {'face': wx.SystemSettings.GetFont(wx.SYS_ANSI_FIXED_FONT).GetFaceName(),
				 'size': 10,
				 'fore': hex(0, 0, 0),
				 'back': hex(255, 255, 255)
				}

		def getstyle(fore = style['fore'], back = style['back'], face = style['face'], size = style['size']):
			return {'fore': fore, 'back': back, 'face': face, 'size': size}

		self.StyleSetSpec(wxStc.STC_STYLE_DEFAULT,	 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle())
		self.StyleSetSpec(wxStc.STC_STYLE_LINENUMBER,  'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(back = '#888888', size = 8))
		self.StyleSetSpec(wxStc.STC_STYLE_CONTROLCHAR, 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle())
		self.StyleSetSpec(wxStc.STC_STYLE_BRACELIGHT,  'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s,bold' % getstyle())
		self.StyleSetSpec(wxStc.STC_STYLE_BRACEBAD,	'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s,bold' % getstyle(fore = hex(255, 0, 0)))

		self.StyleSetSpec(self.DM_STYLE_DEFAULT, 		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle() )
		self.StyleSetSpec(self.DM_STYLE_COMMENT, 		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(hex(128, 128, 128)) )
		self.StyleSetSpec(self.DM_STYLE_COMMENTLINE,  'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(hex(128, 128, 128)) )
		self.StyleSetSpec(self.DM_STYLE_PREPROCESSOR, 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(hex(0,   128, 0)) )
		self.StyleSetSpec(self.DM_STYLE_STRING, 		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(hex(0,   150, 180)) )
		self.StyleSetSpec(self.DM_STYLE_MULTISTRING, 	 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(back = hex(0,   150, 180), fore = hex(0, 0, 0)) )
		self.StyleSetSpec(self.DM_STYLE_NUMBER, 		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle('#800000') )
		self.StyleSetSpec(self.DM_STYLE_KEYWORD, 		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(hex(0,   0,   255)) )
		self.StyleSetSpec(self.DM_STYLE_OPERATOR,		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle('#000000') )
		self.StyleSetSpec(self.DM_STYLE_EMBEDDED_STRING,		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle('#004B5A') )
		self.StyleSetSpec(self.DM_STYLE_EMBEDDED_MULTISTRING,		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle('#004B5A') )
		self.StyleSetSpec(self.DM_STYLE_BADSTRING,		 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(back = hex(255, 0, 0), fore = hex(0, 0, 0)) )
		self.StyleSetSpec(self.DM_STYLE_SINGLESTRING,	 'fore:%(fore)s,back:%(back)s,face:%(face)s,size:%(size)s' % getstyle(hex(0,   150, 180)) )

		self.SetProperty("fold", "1")

		# Now you can define the Folder mark styles...
		foldIconsFG = '#909090'
		foldIconsBG = '#FFFFFF'

		# Top Level Folders...
		self.MarkerDefine(wxStc.STC_MARKNUM_FOLDER, wxStc.STC_MARK_CIRCLEPLUS, foldIconsBG , foldIconsFG) # Collapsed
		self.MarkerDefine(wxStc.STC_MARKNUM_FOLDEROPEN, wxStc.STC_MARK_CIRCLEMINUS, foldIconsBG, foldIconsFG) # Expanded
		self.MarkerDefine(wxStc.STC_MARKNUM_FOLDERTAIL, wxStc.STC_MARK_LCORNERCURVE, foldIconsBG, foldIconsFG) # End of Top Level Folder
		# Nested Folders....
		self.MarkerDefine(wxStc.STC_MARKNUM_FOLDEREND, wxStc.STC_MARK_CIRCLEPLUSCONNECTED, foldIconsBG, foldIconsFG) # Collapsed
		self.MarkerDefine(wxStc.STC_MARKNUM_FOLDEROPENMID, wxStc.STC_MARK_CIRCLEMINUSCONNECTED,  foldIconsBG, foldIconsFG) # Expanded
		self.MarkerDefine(wxStc.STC_MARKNUM_FOLDERMIDTAIL, wxStc.STC_MARK_TCORNERCURVE, foldIconsBG, foldIconsFG) # End of Nested Folder
		# Inside of Folder Marker
		self.MarkerDefine(wxStc.STC_MARKNUM_FOLDERSUB, wxStc.STC_MARK_VLINE, foldIconsBG, foldIconsFG)

	def Open(self, file):
		file = open(file).read()
		self.save_text = file
		self.SetText(file)
		self.EmptyUndoBuffer()
		self.setSavePoint()

		self.StyleDM(0, self.GetLength())

	def updateAllStyles(self):
		""" Used to tell the general editor to update all code editor styles. """

		wx.FindWindowById(ID_EDITOR).updateAllStyles()

	def updateStyle(self, obj):
		""" Copy the STC styling from the empty code editor that the editor notebook owns. """

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
		if charBefore and chr(charBefore) in "[]{}()" and styleBefore == self.DM_STYLE_OPERATOR:
			braceAtCaret = caretPos - 1

		# check after
		if braceAtCaret < 0:
			charAfter = self.GetCharAt(caretPos)
			styleAfter = self.GetStyleAt(caretPos)

			if charAfter and chr(charAfter) in "[]{}()" and styleAfter == self.DM_STYLE_OPERATOR:
				braceAtCaret = caretPos

		if braceAtCaret >= 0:
			braceOpposite = self.BraceMatch(braceAtCaret)

		if braceAtCaret != -1  and braceOpposite == -1:
			self.BraceBadLight(braceAtCaret)
		else:
			self.BraceHighlight(braceAtCaret, braceOpposite)

	def OnCharAdd(self, evt):
		""" Smart indendation """

		char = evt.GetKey()
		current_line = self.GetCurrentLine()
		if char == 10:
			indentation = 0
			if current_line > 0:
				indentation = self.GetLineIndentation(current_line - 1)
			if indentation == 0: return
			self.SetLineIndentation(current_line, indentation)
			self.GotoPos(self.GetLineEndPosition(current_line))

	def Save(self, path):
		""" Save the code to the path specified. """

		open(path, 'w').write(self.GetText())
		self.setSavePoint()

	def highlight_error(self, line):
		#self.SetSelBackground(True, '#FF6464')
		#self.SetSelection(self.PositionFromLine(line-1), self.GetLineEndPosition(line-1))
		#self.SetSelBackground(False, '#FF6464')
		self.SetSelection(self.PositionFromLine(line-1), self.GetLineEndPosition(line-1))
		self.addError(line)

	def FoldDM(self, start, end):
		self.SetFoldFlags(16)
		last_depth = 0
		last_meaningful = 0

		first = True

		linerange = range(self.LineFromPosition(start)-1, self.LineFromPosition(end)+1)
		for line_number in linerange:
			line = self.GetLine(line_number)
			depth = 0
			whitespace = True
			for char in line:
				if not (char in "\t "):
					whitespace = False
					break
				depth += 1

			if not first:
				fold_level = (last_depth + wxStc.STC_FOLDLEVELBASE) & wxStc.STC_FOLDLEVELNUMBERMASK
				if last_depth < depth: fold_level |= wxStc.STC_FOLDLEVELHEADERFLAG
				if whitespace:
					fold_level = ((depth + wxStc.STC_FOLDLEVELBASE) & wxStc.STC_FOLDLEVELNUMBERMASK) | wxStc.STC_FOLDLEVELWHITEFLAG
					self.SetFoldLevel(line_number, fold_level)

				else:
					self.SetFoldLevel(last_meaningful, fold_level)

			first = False
			if not whitespace:
				last_depth = depth
				last_meaningful = line_number

		fold_level = (last_depth + wxStc.STC_FOLDLEVELBASE) & wxStc.STC_FOLDLEVELNUMBERMASK
		self.SetFoldLevel(last_meaningful, fold_level)

	def StyleNone(self, start, end):
		self.StartStyling(start, 31)
		self.SetStyling(end - start, self.NOTYPE_STYLE_DEFAULT)

	def StyleDMF(self, start, end):
		self.StyleDM(start, end)
		self.FoldDM(start, end)

	def StyleDM(self, start, end):
		STATE_DEFAULT = 0
		STATE_STRING = 1
		STATE_MULTISTRING = 2
		STATE_COMMENT = 3
		STATE_MULTICOMMENT = 4
		STATE_PREPROCESSOR = 5
		STATE_NUMBER = 6
		STATE_EMBEDDED_STRING = 7
		STATE_EMBEDDED_MULTISTRING = 8
		STATE_SINGLESTRING = 9

		LINE_STATE_DEFAULT = 0
		LINE_STATE_ESCAPED = 1

		state_style_dict = {
							STATE_DEFAULT: self.DM_STYLE_DEFAULT,
							STATE_STRING: self.DM_STYLE_STRING,
							STATE_MULTISTRING: self.DM_STYLE_MULTISTRING,
							STATE_COMMENT: self.DM_STYLE_COMMENT,
							STATE_MULTICOMMENT: self.DM_STYLE_COMMENTLINE,
							STATE_PREPROCESSOR: self.DM_STYLE_PREPROCESSOR,
							STATE_NUMBER: self.DM_STYLE_NUMBER,
							STATE_EMBEDDED_STRING: self.DM_STYLE_EMBEDDED_STRING,
							STATE_EMBEDDED_MULTISTRING: self.DM_STYLE_EMBEDDED_MULTISTRING,
							STATE_SINGLESTRING: self.DM_STYLE_SINGLESTRING
							}

		state = STATE_DEFAULT
		last_style = self.GetStyleAt(start - 1)
		
		while self.GetLineState( max((self.LineFromPosition(start)-1), 0) ) == LINE_STATE_ESCAPED or last_style == self.DM_STYLE_MULTISTRING or last_style == self.DM_STYLE_COMMENTLINE:
			start = self.PositionFromLine(max((self.LineFromPosition(start) - 1), 0))
			last_style = self.GetStyleAt(start - 1)

		self.StartStyling(start, 31)
		last_styled = start - 1
		escaped = False
		last_escaped = False
		could_be_keyword = True
		word_end = self.WordEndPosition(start, False)

		current_char = chr(self.GetCharAt(start - 1))
		next_char = chr(self.GetCharAt(start))
		word = ''
		embed_count = 0

		linerange = range(start, end)
		for pos in linerange:
			last_char = current_char
			current_char = next_char
			next_char = chr(self.GetCharAt(pos+1))

			if(current_char == '\r' and next_char == '\n'):
				current_char = last_char
				continue

			last_escaped = escaped
			if (not escaped) and last_char == '\\': escaped = True
			else: escaped = False

			self.SetLineState(self.LineFromPosition(pos), LINE_STATE_DEFAULT)

			if state == STATE_DEFAULT:
				if current_char == '{' and next_char == '"' and (not escaped): state = STATE_MULTISTRING
				elif current_char == '"' and (not escaped): state = STATE_STRING
				elif current_char == "'" and (not escaped): state = STATE_SINGLESTRING

				elif (current_char in "0123456789") and not (last_char.isalpha() or last_char == "_" or (last_char in "0123456789")):
					state = STATE_NUMBER
					if not (next_char in ".0123456789"):
						state = STATE_DEFAULT
						self.SetStyling(pos - last_styled, self.DM_STYLE_NUMBER)
						last_styled = pos

				elif current_char == "/" and next_char == "/" and (not escaped): state = STATE_COMMENT
				elif current_char == "/" and next_char == "*" and (not escaped): state = STATE_MULTICOMMENT

				elif current_char in "./:~!-+*%<=>&^|?()[]":
					self.SetStyling(pos - last_styled, self.DM_STYLE_OPERATOR)
					last_styled = pos
					word = ''
					word_end = self.WordEndPosition(pos+1, False)
					
				elif current_char == '#': state = STATE_PREPROCESSOR

				else:
					word += current_char

					if pos >= word_end - 1:
						if self.keyword_text.find(' '+word+' ') == -1:
							self.SetStyling(pos - last_styled, self.DM_STYLE_DEFAULT)
							last_styled = pos

						else:
							self.SetStyling(pos - last_styled, self.DM_STYLE_KEYWORD)
							last_styled = pos

						word_end = self.WordEndPosition(pos+1, False)
						word = ''

			elif state == STATE_STRING:
				if (current_char == '"' or current_char == '\n') and (not escaped):
					if current_char == '\n' and self.GetCurrentLine() != self.LineFromPosition(pos): self.SetStyling(pos - last_styled, self.DM_STYLE_BADSTRING)
					else: self.SetStyling(pos - last_styled, self.DM_STYLE_STRING)
					state = STATE_DEFAULT
					last_styled = pos
				elif current_char == '\n' and escaped: self.SetLineState(self.LineFromPosition(pos), LINE_STATE_ESCAPED)
				elif (current_char == "[") and (not escaped):
					state = STATE_EMBEDDED_STRING
					embed_count = 1
					self.SetStyling(pos - last_styled - 1, self.DM_STYLE_STRING)
					last_styled = pos - 1
					
			elif state == STATE_SINGLESTRING:
				if (current_char == "'" or current_char == '\n') and (not escaped):
					if current_char == '\n': self.SetStyling(pos - last_styled, self.DM_STYLE_BADSTRING)
					else: self.SetStyling(pos - last_styled, self.DM_STYLE_SINGLESTRING)
					state = STATE_DEFAULT
					last_styled = pos
				elif current_char == '\n' and escaped: self.SetLineState(self.LineFromPosition(pos), LINE_STATE_ESCAPED)

			elif state == STATE_MULTISTRING:
				if current_char == '}' and last_char == '"' and (not last_escaped):
					state = STATE_DEFAULT
					self.SetStyling(pos - last_styled, self.DM_STYLE_MULTISTRING)
					last_styled = pos
				elif (current_char == "[") and (not escaped):
					state = STATE_EMBEDDED_MULTISTRING
					self.SetStyling(pos - last_styled - 1, self.DM_STYLE_MULTISTRING)
					last_styled = pos - 1
					embed_count = 1

			elif state == STATE_EMBEDDED_STRING:
				if (current_char == '[') and (not escaped): embed_count += 1
				if (current_char == ']') and (not escaped): embed_count -= 1
				if embed_count == 0 or (current_char == '\n' and (not escaped)):
					if current_char == '\n': state = STATE_DEFAULT
					else: state = STATE_STRING
					self.SetStyling(pos - last_styled, self.DM_STYLE_EMBEDDED_STRING)
					last_styled = pos
					embed_count = 0
				elif current_char == '\n' and escaped: self.SetLineState(self.LineFromPosition(pos), LINE_STATE_ESCAPED)

			elif state == STATE_EMBEDDED_MULTISTRING:
				if (current_char == '[') and (not escaped): embed_count += 1
				if (current_char == ']') and (not escaped): embed_count -= 1
				if embed_count == 0 or (current_char == '\n' and (not escaped)):
					state = STATE_MULTISTRING
					self.SetStyling(pos - last_styled, self.DM_STYLE_EMBEDDED_MULTISTRING)
					last_styled = pos
				elif current_char == '\n' and escaped: self.SetLineState(self.LineFromPosition(pos), LINE_STATE_ESCAPED)

			elif state == STATE_NUMBER:
				if not (next_char in ".0123456789"):
					state = STATE_DEFAULT
					self.SetStyling(pos - last_styled, self.DM_STYLE_NUMBER)
					last_styled = pos

			elif state == STATE_COMMENT:
				if current_char == '\n':
					if not escaped:
						state = STATE_DEFAULT
						self.SetStyling(pos - last_styled, self.DM_STYLE_COMMENT)
						last_styled = pos
					else: self.SetLineState(self.LineFromPosition(pos), LINE_STATE_ESCAPED)

			elif state == STATE_MULTICOMMENT:
				if current_char == '/' and last_char == '*':
					state = STATE_DEFAULT
					self.SetStyling(pos - last_styled, self.DM_STYLE_COMMENTLINE)
					last_styled = pos

			elif state == STATE_PREPROCESSOR:
				if current_char == '\n':
					if not escaped:
						state = STATE_DEFAULT
						self.SetStyling(pos - last_styled, self.DM_STYLE_PREPROCESSOR)
						last_styled = pos
					else: self.SetLineState(self.LineFromPosition(pos), LINE_STATE_ESCAPED)

		self.SetStyling(end - last_styled, state_style_dict[state])

		self.FoldDM(start, end)

	def OnStyleNeededDM(self, e):
		start = self.PositionFromLine(self.LineFromPosition(self.GetEndStyled()))
		end = e.GetPosition()

		self.StylingFunc(start, end)

	def onMarginClick(self, evt):
		# fold and unfold as needed
		if evt.GetMargin() == 1:
			if evt.GetShift() and evt.GetControl():
				self.foldAll()
			else:
				lineClicked = self.LineFromPosition(evt.GetPosition())
				if self.GetFoldLevel(lineClicked) & wxStc.STC_FOLDLEVELHEADERFLAG:
					if evt.GetShift():
						self.SetFoldExpanded(lineClicked, True)
						self.expand(lineClicked, True, True, 1)
					elif evt.GetControl():
						if self.GetFoldExpanded(lineClicked):
							self.SetFoldExpanded(lineClicked, False)
							self.expand(lineClicked, False, True, 0)
						else:
							self.SetFoldExpanded(lineClicked, True)
							self.expand(lineClicked, True, True, 100)
					else:
						self.ToggleFold(lineClicked)

	def foldAll(self):
		"""folding folds, marker - to +"""
		lineCount = self.GetLineCount()
		expanding = True
		# find out if folding or unfolding
		for lineNum in range(lineCount):
			if self.GetFoldLevel(lineNum) & wxStc.STC_FOLDLEVELHEADERFLAG:
				expanding = not self.GetFoldExpanded(lineNum)
				break;
		lineNum = 0
		while lineNum < lineCount:
			level = self.GetFoldLevel(lineNum)
			if level & wxStc.STC_FOLDLEVELHEADERFLAG and (level & wxStc.STC_FOLDLEVELNUMBERMASK) == wxStc.STC_FOLDLEVELBASE:
				if expanding:
					self.SetFoldExpanded(lineNum, True)
					lineNum = self.expand(lineNum, True)
					lineNum = lineNum - 1
				else:
					lastChild = self.GetLastChild(lineNum, -1)
					self.SetFoldExpanded(lineNum, False)
					if lastChild > lineNum:
						self.HideLines(lineNum+1, lastChild)
			lineNum = lineNum + 1

	def expand(self, line, doexpand, force=False, visLevels=0, level=-1):
		"""expanding folds, marker + to -"""
		lastChild = self.GetLastChild(line, level)
		line = line + 1
		while line <= lastChild:
			if force:
				if visLevels > 0:
					self.ShowLines(line, line)
				else:
					self.HideLines(line, line)
			else:
				if doexpand:
					self.ShowLines(line, line)
			if level == -1:
				level = self.GetFoldLevel(line)
			if level & wxStc.STC_FOLDLEVELHEADERFLAG:
				if force:
					if visLevels > 1:
						self.SetFoldExpanded(line, True)
					else:
						self.SetFoldExpanded(line, False)
					line = self.expand(line, doexpand, force, visLevels-1)
				else:
					if doexpand and self.GetFoldExpanded(line):
						line = self.expand(line, True, force, visLevels-1)
					else:
						line = self.expand(line, False, force, visLevels-1)
			else:
				line = line + 1;
		return line
