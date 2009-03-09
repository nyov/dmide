import wx
import wx.lib.colourselect as wxCSel
import wx.combo as wxCombo
import wx.stc as wxStc

def hex(r,g,b,a=0): return '#%02.X%02.X%02.X' % (r, g, b)

class FormatsPage(wx.Panel):
	def __init__(self, parent, stc):
		wx.Panel.__init__(self, parent)

		self.stc = stc
		self.initAll()
		self.initDefaults()
		self.initBinds()
		self.initConstraints()

	def initAll(self):
		labels = ['View Whitespace', 'Buffered Draw', 'Indentation Guides', 'View EOL', 'Antialiasing', 'Margin Width']
		self.labels = []

		for label in labels:
			self.labels.append(wx.StaticText(self, wx.ID_ANY, label))

		self.view_whitespace = wx.ComboBox(self, wx.ID_ANY, 'x', choices = ['Yes', 'No'], style = wx.CB_READONLY)
		self.buffered_draw = wx.ComboBox(self, wx.ID_ANY, 'x', choices = ['Yes', 'No'], style = wx.CB_READONLY)
		self.indentation_guides = wx.ComboBox(self, wx.ID_ANY, 'x', choices = ['Yes', 'No'], style = wx.CB_READONLY)
		self.view_eol = wx.ComboBox(self, wx.ID_ANY, 'x', choices = ['No', 'CR', 'LF', 'CRLF'], style = wx.CB_READONLY)
		self.antialiased = wx.ComboBox(self, wx.ID_ANY, 'x', choices = ['Yes', 'No'], style = wx.CB_READONLY)
		self.margin_width = wx.SpinCtrl(self, wx.ID_ANY, '0')
		self.margin_width.SetRange(0, 50)

		self.ctrls = [self.view_whitespace, self.buffered_draw, self.indentation_guides, self.view_eol, self.antialiased,
					  self.margin_width]

	def initDefaults(self):
		if self.stc.GetViewWhiteSpace():
			self.view_whitespace.SetValue('Yes')
		else:
			self.view_whitespace.SetValue('No')

		if self.stc.GetBufferedDraw():
			self.buffered_draw.SetValue('Yes')
		else:
			self.buffered_draw.SetValue('No')

		if self.stc.GetIndentationGuides():
			self.indentation_guides.SetValue('Yes')
		else:
			self.indentation_guides.SetValue('No')

		if self.stc.GetViewEOL():
			if self.stc.GetEOLMode() == wxStc.STC_EOL_CRLF:
				self.view_eol.SetValue('CRLF')
			elif self.stc.GetEOLMode() == wxStc.STC_EOL_LF:
				self.view_eol.SetValue('CR')
			elif self.stc.GetEOLMode() == wxStc.STC_EOL_CR:
				self.view_eol.SetValue('LF')
			else:
				self.view_eol.SetValue('No')
		else:
			self.view_eol.SetValue('No')

		if self.stc.GetUseAntiAliasing():
			self.antialiased.SetValue('Yes')
		else:
			self.antialiased.SetValue('No')

		self.margin_width.SetValue(self.stc.GetMarginWidth(1))

	def initBinds(self):
		self.view_whitespace.Bind(wx.EVT_COMBOBOX, self.OnChange)
		self.buffered_draw.Bind(wx.EVT_COMBOBOX, self.OnChange)
		self.indentation_guides.Bind(wx.EVT_COMBOBOX, self.OnChange)
		self.view_eol.Bind(wx.EVT_COMBOBOX, self.OnChange)
		self.antialiased.Bind(wx.EVT_COMBOBOX, self.OnChange)
		self.margin_width.Bind(wx.EVT_SPINCTRL, self.OnChange)

	def initConstraints(self):
		sizer = wx.GridBagSizer(2, 2)

		for index, label in enumerate(self.labels):
			sizer.Add(label, (index, 0), (1, 1), wx.ALL | wx.ALIGN_CENTER, 2)

		for index, ctrl in enumerate(self.ctrls):
			sizer.Add(ctrl, (index, 1), (1, 1), wx.ALL | wx.EXPAND, 2)

		self.SetSizerAndFit(sizer)

	def OnChange(self, event):
		if event.EventObject == self.view_whitespace:
			self.stc.SetViewWhiteSpace({'Yes': True, 'No': False}[str(self.view_whitespace.GetValue())])

		elif event.EventObject == self.buffered_draw:
			self.stc.SetBufferedDraw({'Yes': True, 'No': False}[str(self.buffered_draw.GetValue())])

		elif event.EventObject == self.indentation_guides:
			self.stc.SetIndentationGuides({'Yes': True, 'No': False}[str(self.indentation_guides.GetValue())])

		elif event.EventObject == self.view_eol:
			values = {'CRLF': wxStc.STC_EOL_CRLF, 'CR': wxStc.STC_EOL_CR, 'LF': wxStc.STC_EOL_LF, 'No': 0}
			self.stc.SetViewEOL(values[str(self.view_eol.GetValue())])

		elif event.EventObject == self.antialiased:
			self.stc.SetUseAntiAliasing({'Yes': True, 'No': False}[str(self.antialiased.GetValue())])

		elif event.EventObject == self.margin_width:
			self.stc.SetMarginWidth(1, int(self.margin_width.GetValue()))

		self.stc.updateAllStyles()


class StylesPage(wx.Panel):
	def __init__(self, parent, stc):
		wx.Panel.__init__(self, parent)

		self.stc = stc
		self.specs = {'Line Number': wxStc.STC_STYLE_LINENUMBER, 'Control Character': wxStc.STC_STYLE_CONTROLCHAR, 'Brace': wxStc.STC_STYLE_BRACELIGHT,
					   'Main': wxStc.STC_C_DEFAULT, 'Block Comment': wxStc.STC_C_COMMENT, 'Line Comment': wxStc.STC_C_COMMENTLINE, 'Preprocessor': wxStc.STC_C_PREPROCESSOR,
					   'String': wxStc.STC_C_STRING, 'String EOL': wxStc.STC_C_STRINGEOL, 'Number': wxStc.STC_C_NUMBER, 'Keyword': wxStc.STC_C_WORD,
					   'Operator': wxStc.STC_C_OPERATOR}
		self.initAll()
		self.initBinds()
		self.initConstraints()

	def initAll(self):
		self.style_chooser = wx.ComboBox(self, wx.ID_ANY, 'Main', choices = ['', 'Line Number', 'Control Character', 'Brace', '', 'Main', 'Block Comment', 'Line Comment', 'Preprocessor',
																			  'String', 'String EOL', 'Number', 'Keyword', 'Operator'], style = wx.CB_READONLY)
		self.style_ctrl = StyleCtrl(self, self.stc)
		self.style_ctrl.initDefaults(self.specs['Main'])

	def initBinds(self):
		self.style_chooser.Bind(wx.EVT_COMBOBOX, self.OnChange)

	def initConstraints(self):
		sizer = wx.BoxSizer(wx.VERTICAL)

		sizer.Add(self.style_chooser, 0, wx.ALL | wx.EXPAND, 2)
		sizer.Add(self.style_ctrl, 1, wx.ALL | wx.EXPAND, 2)

		self.SetSizerAndFit(sizer)

	def OnChange(self, event):
		if event.EventObject == self.style_chooser:
			value = self.style_chooser.GetValue()
			if value in self.specs:
				self.style_ctrl.initDefaults(self.specs[value])


class StyleCtrl(wx.Panel):
	def __init__(self, parent, stc):
		wx.Panel.__init__(self, parent)

		self.stc = stc
		self.initAll()
		self.initBinds()
		self.initConstraints()

	def initAll(self):

		class FancyFontFaceChooser(wxCombo.OwnerDrawnComboBox):
			def __init__(self, parent):
				self.fonts = wx.FontEnumerator().GetFacenames()
				self.fonts.sort()
				self.sizes = []

				dc = wx.MemoryDC()
				for font in self.fonts:
					dc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, font))
					self.sizes.append(dc.GetTextExtent(font))

				wxCombo.OwnerDrawnComboBox.__init__(self, parent, choices = self.fonts)

			def OnDrawItem(self, dc, rect, item, flags):
				if item >= len(self.fonts) or item < 0:
					dc.DrawText('* font not found *', rect.x + 2, rect.y)
	
				else:
					font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, self.fonts[item])	
					dc.SetFont(font)
					dc.DrawText(self.fonts[item], rect.x + 2, rect.y)

			def OnMeasureItem(self, item):
				if item >= len(self.fonts) or item < 0:
					return -1
				return self.sizes[item][1]

			def OnMeasureItemWidth(self, item):
				if item >= len(self.fonts) or item < 0:
					return -1
				return self.sizes[item][0]

		self.bold_check = wx.CheckBox(self, wx.ID_ANY, 'Bold')
		self.italic_check = wx.CheckBox(self, wx.ID_ANY, 'Italic')
		self.underline_check = wx.CheckBox(self, wx.ID_ANY, 'Underline')

		self.foreground_label = wx.StaticBox(self, wx.ID_ANY, 'Foreground')
		#self.foreground_default = wx.CheckBox(self, wx.ID_ANY, 'Default')
		self.foreground_chooser = wxCSel.ColourSelect(self, wx.ID_ANY, 'Choose...')

		self.background_label = wx.StaticBox(self, wx.ID_ANY, 'Background')
		#self.background_default = wx.CheckBox(self, wx.ID_ANY, 'Default')
		self.background_chooser = wxCSel.ColourSelect(self, wx.ID_ANY, 'Choose...')

		self.font_label = wx.StaticBox(self, wx.ID_ANY, 'Font')
		#self.font_default = wx.CheckBox(self, wx.ID_ANY, 'Default')
		self.font_chooser = FancyFontFaceChooser(self)

		self.size_label = wx.StaticBox(self, wx.ID_ANY, 'Size')
		#self.size_default = wx.CheckBox(self, wx.ID_ANY, 'Default')
		self.size_chooser = wx.SpinCtrl(self, wx.ID_ANY, '10')
		self.size_chooser.SetRange(1, 100)

	def initDefaults(self, style):
		self.style = style
		styles = self.stc.styles[style]

		self.font_chooser.SetValue(styles[0])
		self.size_chooser.SetValue(styles[1])
		self.foreground_chooser.SetColour(styles[2])
		self.background_chooser.SetColour(styles[3])
		self.bold_check.SetValue(styles[4])
		self.italic_check.SetValue(styles[5])
		self.underline_check.SetValue(styles[6])

	def initBinds(self):
		self.foreground_chooser.Bind(wxCSel.EVT_COLOURSELECT, self.OnChange)
		self.background_chooser.Bind(wxCSel.EVT_COLOURSELECT, self.OnChange)
		self.font_chooser.Bind(wx.EVT_COMBOBOX, self.OnChange)
		self.size_chooser.Bind(wx.EVT_SPINCTRL, self.OnChange)
		self.bold_check.Bind(wx.EVT_CHECKBOX, self.OnChange)
		self.italic_check.Bind(wx.EVT_CHECKBOX, self.OnChange)
		self.underline_check.Bind(wx.EVT_CHECKBOX, self.OnChange)

	def initConstraints(self):
		sizer = wx.BoxSizer(wx.VERTICAL)

		#
		sizer2 = wx.BoxSizer(wx.HORIZONTAL)
		sizer2.Add(self.bold_check, 0, wx.ALIGN_CENTER)
		sizer2.Add(self.italic_check, 0, wx.ALIGN_CENTER)
		sizer2.Add(self.underline_check, 0, wx.ALIGN_CENTER)
		sizer.Add(sizer2, 0, wx.ALIGN_CENTER)

		#
		sizer0 = wx.BoxSizer(wx.HORIZONTAL)

		sizer2 = wx.StaticBoxSizer(self.foreground_label, wx.VERTICAL)
		#sizer2.Add(self.foreground_default, 1, wx.ALIGN_CENTER, 2)
		sizer2.Add(self.foreground_chooser, 1, wx.ALL | wx.EXPAND, 2)
		sizer0.Add(sizer2, 1, 0, 2)

		sizer2 = wx.StaticBoxSizer(self.background_label, wx.VERTICAL)
		#sizer2.Add(self.background_default, 1, wx.ALIGN_CENTER, 2)
		sizer2.Add(self.background_chooser, 1, wx.ALL | wx.EXPAND, 2)
		sizer0.Add(sizer2, 1, 0, 2)

		sizer.Add(sizer0, 1, wx.ALL | wx.EXPAND, 2)

		#
		sizer0 = wx.BoxSizer(wx.HORIZONTAL)

		sizer2 = wx.StaticBoxSizer(self.font_label, wx.VERTICAL)
		#sizer2.Add(self.font_default, 1, wx.ALIGN_CENTER, 2)
		sizer2.Add(self.font_chooser, 1, wx.ALL | wx.EXPAND, 2)
		sizer0.Add(sizer2, 1, 0, 2)

		sizer2 = wx.StaticBoxSizer(self.size_label, wx.VERTICAL)
		#sizer2.Add(self.size_default, 1, wx.ALIGN_CENTER, 2)
		sizer2.Add(self.size_chooser, 1, wx.ALL | wx.EXPAND, 2)
		sizer0.Add(sizer2, 1, wx.ALL | wx.EXPAND, 2)

		sizer.Add(sizer0, 1, wx.ALL | wx.EXPAND, 2)

		#
		self.SetSizerAndFit(sizer)

	def OnChange(self, event):
		style = [self.font_chooser.fonts[self.font_chooser.GetSelection()], int(self.size_chooser.GetValue()),
				 hex(*self.foreground_chooser.GetValue()), hex(*self.background_chooser.GetValue()),
				 self.bold_check.IsChecked(), self.italic_check.IsChecked(), self.underline_check.IsChecked()]

		self.stc.styles[self.style] = style
		self.stc.updateAllStyles()


class CodeOptions(wx.Notebook):
	def __init__(self, parent, stc):
		wx.Notebook.__init__(self, parent)

		self.formats_page = FormatsPage(self, stc)
		self.styles_page = StylesPage(self, stc)

		self.AddPage(self.formats_page, 'Settings')
		self.AddPage(self.styles_page, 'Styles')

		size1 = self.formats_page.GetSize()
		size2 = self.styles_page.GetSize()

		self.SetSize((max(size1[0], size2[0]), max(size1[1], size2[1]) + 40))