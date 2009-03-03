#-------------------------------------------------------------------

# re-using this code written many years ago! beware!
from core import *
from unrepr import unrepr

#-------------------------------------------------------------------

ID_HINTFADEIN = wx.NewId()
ID_ALLOWFLOATING = wx.NewId()
ID_VENETIANFADEIN = wx.NewId()
ID_TRANSPARENTDRAG = wx.NewId()
ID_ACTIVEPANE = wx.NewId()
ID_HINTTYPE = wx.NewId()
ID_GRADIENTTYPE = wx.NewId()

ID_PaneBorderSize = wx.NewId()
ID_SashSize = wx.NewId()
ID_CaptionSize = wx.NewId()
ID_BackgroundColor = wx.NewId()
ID_SashColor = wx.NewId()
ID_InactiveCaptionColor =  wx.NewId()
ID_InactiveCaptionGradientColor = wx.NewId()
ID_InactiveCaptionTextColor = wx.NewId()
ID_ActiveCaptionColor = wx.NewId()
ID_ActiveCaptionGradientColor = wx.NewId()
ID_ActiveCaptionTextColor = wx.NewId()
ID_BorderColor = wx.NewId()
ID_GripperColor = wx.NewId()

#-------------------------------------------------------------------

ID_DATA={
	'hint-type': {'transparent': wx.aui.AUI_MGR_TRANSPARENT_HINT, 'venetian': wx.aui.AUI_MGR_VENETIAN_BLINDS_HINT,
				  'rectangle': wx.aui.AUI_MGR_RECTANGLE_HINT, 'none': 0},
	'hint-fade-in': {'True': wx.aui.AUI_MGR_HINT_FADE},
	'allow-floating': {'True': wx.aui.AUI_MGR_ALLOW_FLOATING},
	'no-venetian-fade-in': {'True': wx.aui.AUI_MGR_NO_VENETIAN_BLINDS_FADE},
	'transparent-drag': {'True': wx.aui.AUI_MGR_TRANSPARENT_DRAG},
	'active-pane': {'True': wx.aui.AUI_MGR_ALLOW_ACTIVE_PANE},
	'gradient-type': {'vertical': wx.aui.AUI_GRADIENT_VERTICAL, 'horizontal': wx.aui.AUI_GRADIENT_HORIZONTAL,
					  'none': wx.aui.AUI_GRADIENT_NONE}
				}

SETTINGS_DATA={
		'background-color': wx.aui.AUI_DOCKART_BACKGROUND_COLOUR,
		'inactive-caption-color': wx.aui.AUI_DOCKART_INACTIVE_CAPTION_COLOUR,
		'inactive-caption-gradient-color': wx.aui.AUI_DOCKART_INACTIVE_CAPTION_GRADIENT_COLOUR,
		'inactive-caption-text-color': wx.aui.AUI_DOCKART_INACTIVE_CAPTION_TEXT_COLOUR,
		'active-caption-color': wx.aui.AUI_DOCKART_ACTIVE_CAPTION_COLOUR,
		'active-caption-gradient-color': wx.aui.AUI_DOCKART_ACTIVE_CAPTION_GRADIENT_COLOUR,
		'active-caption-text-color': wx.aui.AUI_DOCKART_ACTIVE_CAPTION_TEXT_COLOUR,
		'sash-color': wx.aui.AUI_DOCKART_SASH_COLOUR,
		'border-color': wx.aui.AUI_DOCKART_BORDER_COLOUR,
		'gripper-color': wx.aui.AUI_DOCKART_GRIPPER_COLOUR,
		'pane-border-size': wx.aui.AUI_DOCKART_PANE_BORDER_SIZE,
		'sash-size': wx.aui.AUI_DOCKART_SASH_SIZE,
		'caption-size': wx.aui.AUI_DOCKART_CAPTION_SIZE,
		}

#-------------------------------------------------------------------

class PerspectiveOptions(wx.Panel):
	''' Panel which contains the notebook of option panels. '''

#-------------------------------------------------------------------

	def __init__(self, parent, frame):
		wx.Panel.__init__(self, parent, wx.ID_ANY)

		self._frame = frame

		self.create_options(self._frame)

#-------------------------------------------------------------------

	def load(self, aui_manager, data):
		''' Used to load perspective setting data. '''

		aui_data = data.split('!-options-!')
		aui_manager.LoadPerspective(aui_data[0])
		if len(aui_data) > 1:
			self.options_docking.load(aui_data[1])
			if len(aui_data) > 2:
				self.options_interface.load(aui_data[2])

		aui_manager.Update()
		self.options_docking.Update()
		self.options_interface.Update()

#-------------------------------------------------------------------

	def save(self, perspectiveData):
		''' Used to save perspective setting data. '''

		return self.options_docking.save() + self.options_interface.save()

#-------------------------------------------------------------------

	def create_options(self, frame):
		''' Create the notebook and add the option pages. '''

		notebook = wx.Notebook(self, wx.ID_ANY)
		self.options_interface = Options_Interface(notebook, frame)
		notebook.AddPage(self.options_interface, 'Interface')
		self.options_docking = Options_Docking(notebook, frame)
		notebook.AddPage(self.options_docking, 'Docking')

		options_sizer = wx.BoxSizer(wx.VERTICAL)
		options_sizer.Add(notebook, 1, wx.EXPAND, 0)
		self.SetSizer(options_sizer)
		options_sizer.Fit(self)
		self.Layout()

#-------------------------------------------------------------------

class Options_Docking(wx.Panel):
	''' Holds the options for the docking page. '''

#-------------------------------------------------------------------

	def __init__(self, parent, frame):
		self._frame = frame
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.options_notebook = wx.Notebook(self, wx.ID_ANY, style = 0)
		self.layout_pane = wx.Panel(self.options_notebook, wx.ID_ANY, style = wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN)
		self.sizer_1_staticbox = wx.StaticBox(self.layout_pane, wx.ID_ANY, 'Panel')
		self.hint_fade_in = wx.CheckBox(self.layout_pane, ID_HINTFADEIN, 'Hint Fade-In')
		self.allow_floating = wx.CheckBox(self.layout_pane, ID_ALLOWFLOATING, 'Allow Floating')
		self.venetian_fade = wx.CheckBox(self.layout_pane, ID_VENETIANFADEIN, 'No Venetian Fade-In')
		self.transparent_drag = wx.CheckBox(self.layout_pane, ID_TRANSPARENTDRAG, 'Transparent Drag')
		self.active_pane = wx.CheckBox(self.layout_pane, ID_ACTIVEPANE, 'Active Pane')
		self.hint_radiobox = wx.RadioBox(self.layout_pane, ID_HINTTYPE, 'Hint Type', choices = ['Transparent', 'Venetian', 'Rectangle', 'None'], majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
		self.gradient_radiobox = wx.RadioBox(self.layout_pane, ID_GRADIENTTYPE, 'Gradient Type', choices = ['Vertical', 'Horizontal', 'None'], majorDimension = 1, style = wx.RA_SPECIFY_ROWS)

		self.__set_properties()
		self.__do_layout()
		self.__do_binds()
		self.Update()

#-------------------------------------------------------------------

	def load(self, data):
		''' Load the options for this panel. '''

		aui_manager = self._frame.aui_manager
		auidata = data.split('|')
		data = {}
		for datum in auidata:
			split = datum.split('=')
			if len(split) <= 1: continue
			data[split[0]] = split[1]

		flags = 0
		gflags = 0

		for setting in data:
			if not setting in data:
				continue
			value = data[setting]
			if not setting in ID_DATA:
				continue
			add_flag = ID_DATA[setting]
			if not value in add_flag:
				continue
			if setting == 'gradient-type':
				gflags ^= add_flag[value]
			else:
				flags ^= add_flag[value]

		aui_manager.SetFlags(flags)
		aui_manager.GetArtProvider().SetMetric(wx.aui.AUI_DOCKART_GRADIENT_TYPE, gflags)

#-------------------------------------------------------------------

	def save(self):
		''' Save the options for this panel. '''

		aui_manager = self._frame.aui_manager
		flags = aui_manager.GetFlags()
		save_text = '|!-options-!'

		if flags & wx.aui.AUI_MGR_TRANSPARENT_HINT: save_text += '|hint-type=transparent'
		elif flags & wx.aui.AUI_MGR_VENETIAN_BLINDS_HINT: save_text += '|hint-type=venetian'
		elif flags & wx.aui.AUI_MGR_RECTANGLE_HINT: save_text += '|hint-type=rectangle'
		else: save_text += '|hint-type=none'

		if flags & wx.aui.AUI_MGR_HINT_FADE: save_text += '|hint-fade-in=True'
		if flags & wx.aui.AUI_MGR_ALLOW_FLOATING: save_text += '|allow-floating=True'
		if flags & wx.aui.AUI_MGR_NO_VENETIAN_BLINDS_FADE: save_text += '|no-venetian-fade-in=True'
		if flags & wx.aui.AUI_MGR_TRANSPARENT_DRAG: save_text += '|transparent-drag=True'
		if flags & wx.aui.AUI_MGR_ALLOW_ACTIVE_PANE: save_text += '|active-pane=True'

		gradient_flags = aui_manager.GetArtProvider().GetMetric(wx.aui.AUI_DOCKART_GRADIENT_TYPE)
		if gradient_flags & wx.aui.AUI_GRADIENT_VERTICAL: save_text += '|gradient-type=vertical'
		elif gradient_flags & wx.aui.AUI_GRADIENT_HORIZONTAL: save_text += '|gradient-type=horizontal'
		elif gradient_flags & wx.aui.AUI_GRADIENT_NONE: save_text += '|gradient-type=none'

		return save_text

#-------------------------------------------------------------------

	def __set_properties(self):
		self.hint_radiobox.SetSelection(0)
		self.gradient_radiobox.SetSelection(0)

#-------------------------------------------------------------------

	def __do_layout(self):
		options_sizer = wx.BoxSizer(wx.VERTICAL)
		layout_sizer = wx.BoxSizer(wx.VERTICAL)
		sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
		sizer_1 = wx.StaticBoxSizer(self.sizer_1_staticbox, wx.VERTICAL)
		sizer_1.Add(self.hint_fade_in, 0, wx.EXPAND, 0)
		sizer_1.Add(self.allow_floating, 0, 0, 0)
		sizer_1.Add(self.venetian_fade, 0, 0, 0)
		sizer_1.Add(self.transparent_drag, 0, 0, 0)
		sizer_1.Add(self.active_pane, 0, 0, 0)
		layout_sizer.Add(sizer_1, 0, wx.EXPAND, 0)
		layout_sizer.Add(self.hint_radiobox, 1, wx.ALL | wx.EXPAND, 1)
		layout_sizer.Add(self.gradient_radiobox, 1, wx.ALL | wx.EXPAND, 1)
		self.layout_pane.SetSizer(layout_sizer)
		self.options_notebook.AddPage(self.layout_pane, 'Layout')
		options_sizer.Add(self.options_notebook, 1, wx.EXPAND, 0)
		self.SetSizer(options_sizer)
		options_sizer.Fit(self)
		self.Layout()

#-------------------------------------------------------------------

	def __do_binds(self):
		self.Bind(wx.EVT_CHECKBOX, self.OnApply, id = ID_HINTFADEIN)
		self.Bind(wx.EVT_CHECKBOX, self.OnApply, id = ID_ALLOWFLOATING)
		self.Bind(wx.EVT_CHECKBOX, self.OnApply, id = ID_VENETIANFADEIN)
		self.Bind(wx.EVT_CHECKBOX, self.OnApply, id = ID_TRANSPARENTDRAG)
		self.Bind(wx.EVT_CHECKBOX, self.OnApply, id = ID_ACTIVEPANE)
		self.Bind(wx.EVT_RADIOBOX, self.OnApply, id = ID_HINTTYPE)
		self.Bind(wx.EVT_RADIOBOX, self.OnApply, id = ID_GRADIENTTYPE)

#-------------------------------------------------------------------

	def Update(self):
		flags = self._frame.aui_manager.GetFlags()

		if flags & wx.aui.AUI_MGR_TRANSPARENT_HINT:
			self.hint_radiobox.SetSelection(0)
		elif flags & wx.aui.AUI_MGR_VENETIAN_BLINDS_HINT:
			self.hint_radiobox.SetSelection(1)
		elif flags & wx.aui.AUI_MGR_RECTANGLE_HINT:
			self.hint_radiobox.SetSelection(2)
		else:
			self.hint_radiobox.SetSelection(3)

		if flags & wx.aui.AUI_MGR_HINT_FADE:
			self.hint_fade_in.SetValue(True)
		else:
			self.hint_fade_in.SetValue(False)
		if flags & wx.aui.AUI_MGR_ALLOW_FLOATING:
			self.allow_floating.SetValue(True)
		else:
			self.allow_floating.SetValue(False)
		if flags & wx.aui.AUI_MGR_NO_VENETIAN_BLINDS_FADE:
			self.venetian_fade.SetValue(True)
		else:
			self.venetian_fade.SetValue(False)
		if flags & wx.aui.AUI_MGR_TRANSPARENT_DRAG:
			self.transparent_drag.SetValue(True)
		else:
			self.transparent_drag.SetValue(False)
		if flags & wx.aui.AUI_MGR_ALLOW_ACTIVE_PANE:
			self.active_pane.SetValue(True)
		else:
			self.active_pane.SetValue(False)

		gradient_flags = self._frame.aui_manager.GetArtProvider().GetMetric(wx.aui.AUI_DOCKART_GRADIENT_TYPE)
		if gradient_flags & wx.aui.AUI_GRADIENT_VERTICAL:
			self.gradient_radiobox.SetSelection(0)
		elif gradient_flags & wx.aui.AUI_GRADIENT_HORIZONTAL:
			self.gradient_radiobox.SetSelection(1)
		else:
			self.gradient_radiobox.SetSelection(2)

#-------------------------------------------------------------------

	def OnApply(self,event):
		flags = 0

		hint_type = self.hint_radiobox.GetSelection()
		if hint_type == 0:
			flags ^= wx.aui.AUI_MGR_TRANSPARENT_HINT
		elif hint_type == 1:
			flags ^= wx.aui.AUI_MGR_VENETIAN_BLINDS_HINT
		elif hint_type == 2:
			flags ^= wx.aui.AUI_MGR_RECTANGLE_HINT

		if self.hint_fade_in.GetValue():
			flags ^= wx.aui.AUI_MGR_HINT_FADE
		if self.allow_floating.GetValue():
			flags ^= wx.aui.AUI_MGR_ALLOW_FLOATING
		if self.venetian_fade.GetValue():
			flags ^= wx.aui.AUI_MGR_NO_VENETIAN_BLINDS_FADE
		if self.transparent_drag.GetValue():
			flags ^= wx.aui.AUI_MGR_TRANSPARENT_DRAG
		if self.active_pane.GetValue():
			flags ^= wx.aui.AUI_MGR_ALLOW_ACTIVE_PANE

		gradient_flags = 0
		grad_type = self.gradient_radiobox.GetSelection()
		if grad_type == 0:
			gradient_flags = wx.aui.AUI_GRADIENT_VERTICAL
		elif grad_type ==1 :
			gradient_flags = wx.aui.AUI_GRADIENT_HORIZONTAL
		elif grad_type == 2:
			gradient_flags = wx.aui.AUI_GRADIENT_NONE

		self._frame.aui_manager.SetFlags(flags)
		self._frame.aui_manager.GetArtProvider().SetMetric(wx.aui.AUI_DOCKART_GRADIENT_TYPE, gradient_flags)
		self._frame.aui_manager.Update()

#-------------------------------------------------------------------

class Options_Interface(wx.Panel):
	''' Holds the options for the interface page. '''

	option_border_size = None

#-------------------------------------------------------------------

	def __init__(self, parent, frame):
		wx.Panel.__init__(self, parent, wx.ID_ANY)

		self._frame = frame

		self.create_controls()

#-------------------------------------------------------------------

	def Update(self):
		''' Grab all the options from the AUI Manager and update the options panel. '''

		aui_manager = self._frame.aui_manager
		dockart = aui_manager.GetArtProvider()

		self.UpdateColors()
		self._border_size.SetValue(dockart.GetMetric(wx.aui.AUI_DOCKART_PANE_BORDER_SIZE))
		self._sash_size.SetValue(dockart.GetMetric(wx.aui.AUI_DOCKART_SASH_SIZE))
		self._caption_size.SetValue(dockart.GetMetric(wx.aui.AUI_DOCKART_CAPTION_SIZE))

#-------------------------------------------------------------------

	def save(self):
		''' Saving the options for this panel. '''

		save_text = '|!-options-!'
		save_text += 'background-color=%s|' % self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_BACKGROUND_COLOUR)
		save_text += 'inactive-caption-color=%s|' % self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_INACTIVE_CAPTION_COLOUR)
		save_text += 'inactive-caption-gradient-color=%s|' % self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_INACTIVE_CAPTION_GRADIENT_COLOUR)
		save_text += 'inactive-caption-text-color=%s|' % self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_INACTIVE_CAPTION_TEXT_COLOUR)
		save_text += 'active-caption-color=%s|' % self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_ACTIVE_CAPTION_COLOUR)
		save_text += 'active-caption-gradient-color=%s|' % self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_ACTIVE_CAPTION_GRADIENT_COLOUR)
		save_text += 'active-caption-text-color=%s|' % self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_ACTIVE_CAPTION_TEXT_COLOUR)
		save_text += 'sash-color=%s|' % self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_SASH_COLOUR)
		save_text += 'border-color=%s|' % self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_BORDER_COLOUR)
		save_text += 'gripper-color=%s|' % self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_GRIPPER_COLOUR)
		save_text += 'pane-border-size=%s|' % self._frame.aui_manager.GetArtProvider().GetMetric(wx.aui.AUI_DOCKART_PANE_BORDER_SIZE)
		save_text += 'sash-size=%s|' % self._frame.aui_manager.GetArtProvider().GetMetric(wx.aui.AUI_DOCKART_SASH_SIZE)
		save_text += 'caption-size=%s|' % self._frame.aui_manager.GetArtProvider().GetMetric(wx.aui.AUI_DOCKART_CAPTION_SIZE)
		return save_text

#-------------------------------------------------------------------

	def load(self, data):
		''' Loading the options for this panel. '''

		aui_manager = self._frame.aui_manager
		dockart = aui_manager.GetArtProvider()
		auidata = data.split('|')
		data = {}
		for datum in auidata:
			split = datum.split('=')
			if len(split) <= 1: continue
			data[split[0]] = split[1]

		for d in data:
			value = unrepr(data[d])
			if not d in SETTINGS_DATA:
				continue
			if 'color' in d:
				dockart.SetColour(SETTINGS_DATA[d], value)
			else:
				dockart.SetMetric(SETTINGS_DATA[d], value)

#-------------------------------------------------------------------

	def CreateColorBitmap(self,c):
		image = wx.EmptyImage(25,14)
		for x in xrange(25):
			for y in xrange(14):
				pixcol = c
				if x == 0 or x == 24 or y == 0 or y == 13:
					pixcol = wx.BLACK
				image.SetRGB(x, y, pixcol.Red(), pixcol.Green(), pixcol.Blue())
		return image.ConvertToBitmap()

#-------------------------------------------------------------------

	def UpdateColors(self):
		''' Used to update all the colours on the panel. '''

		bk = self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_BACKGROUND_COLOUR)
		self._background_color.SetBitmapLabel(self.CreateColorBitmap(bk))
		
		cap = self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_INACTIVE_CAPTION_COLOUR)
		self._inactive_caption_color.SetBitmapLabel(self.CreateColorBitmap(cap))
		
		capgrad = self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_INACTIVE_CAPTION_GRADIENT_COLOUR)
		self._inactive_caption_gradient_color.SetBitmapLabel(self.CreateColorBitmap(capgrad))
		
		captxt = self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_INACTIVE_CAPTION_TEXT_COLOUR)
		self._inactive_caption_text_color.SetBitmapLabel(self.CreateColorBitmap(captxt))
		
		acap = self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_ACTIVE_CAPTION_COLOUR)
		self._active_caption_color.SetBitmapLabel(self.CreateColorBitmap(acap))
		
		acapgrad = self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_ACTIVE_CAPTION_GRADIENT_COLOUR)
		self._active_caption_gradient_color.SetBitmapLabel(self.CreateColorBitmap(acapgrad))
		
		acaptxt = self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_ACTIVE_CAPTION_TEXT_COLOUR)
		self._active_caption_text_color.SetBitmapLabel(self.CreateColorBitmap(acaptxt))
		
		sash = self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_SASH_COLOUR)
		self._sash_color.SetBitmapLabel(self.CreateColorBitmap(sash))
		
		border = self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_BORDER_COLOUR)
		self._border_color.SetBitmapLabel(self.CreateColorBitmap(border))
		
		gripper = self._frame.aui_manager.GetArtProvider().GetColour(wx.aui.AUI_DOCKART_GRIPPER_COLOUR)
		self._gripper_color.SetBitmapLabel(self.CreateColorBitmap(gripper))

#-------------------------------------------------------------------

	def OnPaneBorderSize(self,event):
		self._frame.aui_manager.GetArtProvider().SetMetric(wx.aui.AUI_DOCKART_PANE_BORDER_SIZE, event.GetInt())
		self._frame.aui_manager.Update()

#-------------------------------------------------------------------

	def OnSashSize(self,event):
		self._frame.aui_manager.GetArtProvider().SetMetric(wx.aui.AUI_DOCKART_SASH_SIZE, event.GetInt())
		self._frame.aui_manager.Update()

#-------------------------------------------------------------------

	def OnCaptionSize(self,event):
		self._frame.aui_manager.GetArtProvider().SetMetric(wx.aui.AUI_DOCKART_CAPTION_SIZE, event.GetInt())
		self._frame.aui_manager.Update()

#-------------------------------------------------------------------

	def OnSetColor(self,event):
		dlg = wx.ColourDialog(self._frame)
		dlg.SetTitle('Colour Picker')
		if dlg.ShowModal() != wx.ID_OK:
			return
		var = 0
		if event.GetId() == ID_BackgroundColor:
			var = wx.aui.AUI_DOCKART_BACKGROUND_COLOUR
		elif event.GetId() == ID_SashColor:
			var = wx.aui.AUI_DOCKART_SASH_COLOUR
		elif event.GetId() == ID_InactiveCaptionColor:
			var = wx.aui.AUI_DOCKART_INACTIVE_CAPTION_COLOUR
		elif event.GetId() == ID_InactiveCaptionGradientColor:
			var = wx.aui.AUI_DOCKART_INACTIVE_CAPTION_GRADIENT_COLOUR
		elif event.GetId() == ID_InactiveCaptionTextColor:
			var = wx.aui.AUI_DOCKART_INACTIVE_CAPTION_TEXT_COLOUR
		elif event.GetId() == ID_ActiveCaptionColor:
			var = wx.aui.AUI_DOCKART_ACTIVE_CAPTION_COLOUR
		elif event.GetId() == ID_ActiveCaptionGradientColor:
			var = wx.aui.AUI_DOCKART_ACTIVE_CAPTION_GRADIENT_COLOUR
		elif event.GetId() == ID_ActiveCaptionTextColor:
			var = wx.aui.AUI_DOCKART_ACTIVE_CAPTION_TEXT_COLOUR
		elif event.GetId() == ID_BorderColor:
			var = wx.aui.AUI_DOCKART_BORDER_COLOUR
		elif event.GetId() == ID_GripperColor:
			var = wx.aui.AUI_DOCKART_GRIPPER_COLOUR
		else:
			return

		self._frame.aui_manager.GetArtProvider().SetColor(var, dlg.GetColourData().GetColour())
		self._frame.aui_manager.Update()
		self.UpdateColors()

#-------------------------------------------------------------------

	def create_controls(self):
		''' Method that creates all the option controls. '''

		vert = wx.BoxSizer(wx.VERTICAL)

		s1=wx.BoxSizer(wx.HORIZONTAL)
		self._border_size=wx.SpinCtrl(self,ID_PaneBorderSize,'',wx.DefaultPosition,wx.Size(50,20))
		s1.Add((1,1),1,wx.EXPAND); s1.Add(wx.StaticText(self,wx.ID_ANY,'Pane Border Size:'))
		s1.Add(self._border_size); s1.Add((1,1),1,wx.EXPAND)
		s1.SetItemMinSize(1,(180,20))

		s2=wx.BoxSizer(wx.HORIZONTAL)
		self._sash_size=wx.SpinCtrl(self,ID_SashSize,'',wx.DefaultPosition,wx.Size(50,20))
		s2.Add((1,1),1,wx.EXPAND); s2.Add(wx.StaticText(self,-1,'Sash Size:'))
		s2.Add(self._sash_size); s2.Add((1,1),1,wx.EXPAND)
		s2.SetItemMinSize(1,(180,20))

		s3=wx.BoxSizer(wx.HORIZONTAL)
		self._caption_size=wx.SpinCtrl(self,ID_CaptionSize,'',wx.DefaultPosition,wx.Size(50,20))
		s3.Add((1,1),1,wx.EXPAND); s3.Add(wx.StaticText(self,-1,'Caption Size:'))
		s3.Add(self._caption_size); s3.Add((1,1),1,wx.EXPAND)
		s3.SetItemMinSize(1,(180,20))

		b=self.CreateColorBitmap(wx.BLACK)

		s4=wx.BoxSizer(wx.HORIZONTAL)
		self._background_color=wx.BitmapButton(self,ID_BackgroundColor,b,wx.DefaultPosition,wx.Size(50,25))
		s4.Add((1,1),1,wx.EXPAND); s4.Add(wx.StaticText(self,-1,'Background Color:'))
		s4.Add(self._background_color); s4.Add((1,1),1,wx.EXPAND)
		s4.SetItemMinSize(1,(180,20))

		s5=wx.BoxSizer(wx.HORIZONTAL)
		self._sash_color=wx.BitmapButton(self,ID_SashColor,b,wx.DefaultPosition,wx.Size(50,25))
		s5.Add((1,1),1,wx.EXPAND); s5.Add(wx.StaticText(self,-1,'Sash Color:'))
		s5.Add(self._sash_color); s5.Add((1,1),1,wx.EXPAND)
		s5.SetItemMinSize(1,(180,20))

		s6=wx.BoxSizer(wx.HORIZONTAL)
		self._inactive_caption_color=wx.BitmapButton(self,ID_InactiveCaptionColor,b,wx.DefaultPosition,wx.Size(50,25))
		s6.Add((1,1),1,wx.EXPAND); s6.Add(wx.StaticText(self,-1,'Normal Caption:'))
		s6.Add(self._inactive_caption_color); s6.Add((1,1),1,wx.EXPAND)
		s6.SetItemMinSize(1,(180,20))

		s7=wx.BoxSizer(wx.HORIZONTAL)
		self._inactive_caption_gradient_color=wx.BitmapButton(self,ID_InactiveCaptionGradientColor,b,wx.DefaultPosition,wx.Size(50,25))
		s7.Add((1,1),1,wx.EXPAND); s7.Add(wx.StaticText(self,-1,'Normal Caption Gradient:'))
		s7.Add(self._inactive_caption_gradient_color); s7.Add((1,1),1,wx.EXPAND)
		s7.SetItemMinSize(1,(180,20))

		s8=wx.BoxSizer(wx.HORIZONTAL)
		self._inactive_caption_text_color=wx.BitmapButton(self,ID_InactiveCaptionTextColor,b,wx.DefaultPosition,wx.Size(50,25))
		s8.Add((1,1),1,wx.EXPAND); s8.Add(wx.StaticText(self,-1,'Normal Caption Text:'))
		s8.Add(self._inactive_caption_text_color); s8.Add((1,1),1,wx.EXPAND)
		s8.SetItemMinSize(1,(180,20))

		s9=wx.BoxSizer(wx.HORIZONTAL)
		self._active_caption_color=wx.BitmapButton(self,ID_ActiveCaptionColor,b,wx.DefaultPosition,wx.Size(50,25))
		s9.Add((1,1),1,wx.EXPAND); s9.Add(wx.StaticText(self,-1,'Active Caption:'))
		s9.Add(self._active_caption_color); s9.Add((1,1),1,wx.EXPAND)
		s9.SetItemMinSize(1,(180,20))

		s10=wx.BoxSizer(wx.HORIZONTAL)
		self._active_caption_gradient_color=wx.BitmapButton(self,ID_ActiveCaptionGradientColor,b,wx.DefaultPosition,wx.Size(50,25))
		s10.Add((1,1),1,wx.EXPAND); s10.Add(wx.StaticText(self,-1,'Active Caption Gradient:'))
		s10.Add(self._active_caption_gradient_color); s10.Add((1,1),1,wx.EXPAND)
		s10.SetItemMinSize(1,(180,20))

		s11=wx.BoxSizer(wx.HORIZONTAL)
		self._active_caption_text_color=wx.BitmapButton(self,ID_ActiveCaptionTextColor,b,wx.DefaultPosition,wx.Size(50,25))
		s11.Add((1,1),1,wx.EXPAND); s11.Add(wx.StaticText(self,-1,'Active Caption Text:'))
		s11.Add(self._active_caption_text_color); s11.Add((1,1),1,wx.EXPAND)
		s11.SetItemMinSize(1,(180,20))

		s12=wx.BoxSizer(wx.HORIZONTAL)
		self._border_color=wx.BitmapButton(self,ID_BorderColor,b,wx.DefaultPosition,wx.Size(50,25))
		s12.Add((1,1),1,wx.EXPAND); s12.Add(wx.StaticText(self,-1,'Border Color:'))
		s12.Add(self._border_color); s12.Add((1,1),1,wx.EXPAND)
		s12.SetItemMinSize(1,(180,20))

		s13=wx.BoxSizer(wx.HORIZONTAL)
		self._gripper_color=wx.BitmapButton(self,ID_GripperColor,b,wx.DefaultPosition,wx.Size(50,25))
		s13.Add((1,1),1,wx.EXPAND); s13.Add(wx.StaticText(self,-1,'Gripper Color:'))
		s13.Add(self._gripper_color); s13.Add((1,1),1,wx.EXPAND)
		s13.SetItemMinSize(1,(180,20))
		
		grid_sizer=wx.GridSizer(0,2)
		grid_sizer.SetHGap(5)
		grid_sizer.Add(s1); grid_sizer.Add(s4); grid_sizer.Add(s2)
		grid_sizer.Add(s5); grid_sizer.Add(s3); grid_sizer.Add(s13)
		grid_sizer.Add((1,1)); grid_sizer.Add(s12); grid_sizer.Add(s6)
		grid_sizer.Add(s9); grid_sizer.Add(s7); grid_sizer.Add(s10)
		grid_sizer.Add(s8); grid_sizer.Add(s11)
		 
		cont_sizer=wx.BoxSizer(wx.VERTICAL)
		cont_sizer.Add(grid_sizer,1,wx.EXPAND|wx.ALL,5)
		self.SetSizer(cont_sizer)
		self.GetSizer().SetSizeHints(self)

		self.Update()

		self.Bind(wx.EVT_SPINCTRL, self.OnPaneBorderSize, id = ID_PaneBorderSize)
		self.Bind(wx.EVT_SPINCTRL, self.OnSashSize, id = ID_SashSize)
		self.Bind(wx.EVT_SPINCTRL, self.OnCaptionSize, id = ID_CaptionSize)
		self.Bind(wx.EVT_BUTTON, self.OnSetColor, id = ID_BackgroundColor)
		self.Bind(wx.EVT_BUTTON, self.OnSetColor, id = ID_SashColor)
		self.Bind(wx.EVT_BUTTON, self.OnSetColor, id = ID_InactiveCaptionColor)
		self.Bind(wx.EVT_BUTTON, self.OnSetColor, id = ID_InactiveCaptionGradientColor)
		self.Bind(wx.EVT_BUTTON, self.OnSetColor, id = ID_InactiveCaptionTextColor)
		self.Bind(wx.EVT_BUTTON, self.OnSetColor, id = ID_ActiveCaptionColor)
		self.Bind(wx.EVT_BUTTON, self.OnSetColor, id = ID_ActiveCaptionGradientColor)
		self.Bind(wx.EVT_BUTTON, self.OnSetColor, id = ID_ActiveCaptionTextColor)
		self.Bind(wx.EVT_BUTTON, self.OnSetColor, id = ID_BorderColor)
		self.Bind(wx.EVT_BUTTON, self.OnSetColor, id = ID_GripperColor)

#-------------------------------------------------------------------