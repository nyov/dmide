import re


class DMFMacroGroup:
	def __init__(self, name):
		self.name = name
		self.macros = []

	def save(self):
		sav = 'macro "%s"\n' % self.name
		for macro in self.macros:
			sav += macro.save()
		return sav + '\n'

class DMFMacro:
	def __init__(self, _parent, id):
		self._parent = _parent
		self._parent.macros.append(self)
		if id:
			self.id = id
		self.alt_modifier = False
		self.shift_modifier = False
		self.ctrl_modifier = False
		self.repeat_modifier = False
		self.release_modifier = False
		self.key = None
		self.command = None
		self.disabled = False

	def __repr__(self):
		key = self.key
		if self.ctrl_modifier:
			key = 'CTRL+%s' % key
		if self.shift_modifier:
			key = 'SHIFT+%s' % key
		if self.alt_modifier:
			key = 'ALT+%s' % key
		if self.repeat_modifier:
			key += '+REP'
		if self.release_modifier:
			key += '+UP'
		return key

	def setattr(self, attr, value):
		if attr == 'name':
			value = value[1:-1]
			args = value.split('+')
			for arg in args:
				if arg == 'ALT':
					self.alt_modifier = True
				elif arg == 'SHIFT':
					self.shift_modifier = True
				elif arg == 'CTRL':
					self.ctrl_modifier = True
				elif arg == 'REP':
					self.repeat_modifier = True
				elif arg == 'UP':
					self.release_modifier = True
				else:
					self.key = arg

		elif attr == 'command':
			self.command = value[1:-1]

		elif attr == 'is-disabled':
			self.disabled = {'true': True, 'false': False, 'none': None}[value]

	def save(self):
		id = ''
		try:
			id = '"%s"' % self.id
		except AttributeError:
			pass
		sav = '\telem %s\n' % id
		key = self.key
		if self.ctrl_modifier:
			key = 'CTRL+%s' % key
		if self.shift_modifier:
			key = 'SHIFT+%s' % key
		if self.alt_modifier:
			key = 'ALT+%s' % key
		if self.repeat_modifier:
			key += '+REP'
		if self.release_modifier:
			key += '+UP'
		sav += '\t\tname = "%s"\n' % key
		sav += '\t\tcommand = "%s"\n' % self.command
		sav += '\t\tis-disabled = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.disabled]
		return sav


class DMFMenuGroup:
	def __init__(self, name):
		self.name = name
		self.menus = []

	def save(self):
		sav = 'menu "%s"\n' % self.name
		for menu in self.menus:
			sav += menu.save()
		return sav + '\n'

class DMFMenu:
	def __init__(self, _parent, id):
		self._parent = _parent
		self._parent.menus.append(self)
		if id:
			self.id = id
		self.name = None
		self.command = None
		self.category = None
		self.is_checked = False
		self.can_check = False
		self.group = None
		self.is_disabled = None
		self.saved_params = None

	def setattr(self, attr, value):
		if attr == 'name':
			self.name = value[1:-1]

		elif attr == 'command':
			self.command = value[1:-1]

		elif attr == 'category':
			self.category = value[1:-1]

		elif attr == 'is-checked':
			self.is_checked = {'true': True, 'false': False, 'none': None}[value]

		elif attr == 'can-check':
			self.can_check = {'true': True, 'false': False, 'none': None}[value]

		elif attr == 'group':
			self.group = value[1:-1]

		elif attr == 'is-disabled':
			self.is_disabled = {'true': True, 'false': False, 'none': None}[value]

		elif attr == 'saved-params':
			self.saved_params = value[1:-1]

	def save(self):
		id = ''
		try:
			id = '"%s"' % self.id
		except AttributeError:
			pass
		sav = '\telem %s\n' % id
		sav += '\t\tname = "%s"\n' % self.name
		sav += '\t\tcommand = "%s"\n' % self.command
		sav += '\t\tcategory = "%s"\n' % self.category
		sav += '\t\tis-checked = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_checked]
		sav += '\t\tcan-check = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.can_check]
		sav += '\t\tgroup = "%s"\n' % self.group
		sav += '\t\tis-disabled = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_disabled]
		sav += '\t\tsaved-params = "%s"\n' % self.saved_params
		return sav


class DMFWindowGroup:
	def __init__(self, name):
		self.name = name
		self.windows = []

	def save(self):
		sav = 'window "%s"\n' % self.name
		for window in self.windows:
			sav += window.save()
		return sav + '\n'

	def get_main(self):
		for window in self.windows:
			if window.type == 'MAIN':
				return window
		return -1

class DMFWindow:
	def __init__(self, _parent, id):
		self._parent = _parent
		self._parent.windows.append(self)
		self.id = id
		self.type = None
		self.pos = None
		self.size = None
		self.anchor1 = None
		self.anchor2 = None
		self.font_family = None
		self.font_size = None
		self.font_style = None
		self.text_color = None
		self.background_color = None
		self.is_visible = None
		self.is_disabled = None
		self.is_transparent = None
		self.is_default = None
		self.border = None
		self.drop_zone = None
		self.right_click = None
		self.saved_params = None

		self._dmide_comment = None
		self._dmide_parent = None

	def setattr(self, attr, value):
		if attr == '_dmide_comment':
			self._dmide_comment = value[1:-1]

		elif attr == '_dmide_parent':
			self._dmide_parent = value

		if attr == 'type':
			self.type = value

		elif attr == 'pos':
			self.pos = (int(value[0:value.find(',')]), int(value[value.find(',')+1:]))

		elif attr == 'size':
			self.size = (int(value[0:value.find('x')]), int(value[value.find('x')+1:]))

		elif attr == 'anchor1':
			if value != 'none':
				self.anchor1 = (int(value[0:value.find(',')]), int(value[value.find(',')+1:]))

		elif attr == 'anchor2':
			if value != 'none':
				self.anchor2 = (int(value[0:value.find(',')]), int(value[value.find(',')+1:]))

		elif attr == 'font-family':
			self.font_family = value[1:-1]

		elif attr == 'font-size':
			self.font_size = int(value)

		elif attr == 'font-style':
			self.font_style = value[1:-1].split(' ')

		elif attr == 'text-color':
			self.text_color = value

		elif attr == 'background-color':
			self.background_color = value

		elif attr == 'is-visible':
			self.is_visible = {'true': True, 'false': False, 'none': None}[value]

		elif attr == 'is-disabled':
			self.is_disabled = {'true': True, 'false': False, 'none': None}[value]

		elif attr == 'is-transparent':
			self.is_transparent = {'true': True, 'false': False, 'none': None}[value]

		elif attr == 'is-default':
			self.is_default = {'true': True, 'false': False, 'none': None}[value]

		elif attr == 'border':
			self.border = value

		elif attr == 'drop-zone':
			self.drop_zone = {'true': True, 'false': False, 'none': None}[value]

		elif attr == 'right-click':
			self.right_click = {'true': True, 'false': False, 'none': None}[value]

		elif attr == 'saved-params':
			self.saved_params = value[1:-1]

		elif self.type == 'MAIN':
			if attr == 'title':
				self.title = value[1:-1]

			elif attr == 'titlebar':
				self.titlebar = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'statusbar':
				self.statusbar = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'can-close':
				self.can_close = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'can-minimize':
				self.can_minimize = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'can-resize':
				self.can_resize = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'is-pane':
				self.is_pane = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'is-minimized':
				self.is_minimized = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'is-maximized':
				self.is_maximized = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'can-scroll':
				self.can_scroll = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'icon':
				self.icon = value[1:-1]

			elif attr == 'image':
				self.image = value[1:-1]

			elif attr == 'image-mode':
				self.image_mode = value

			elif attr == 'keep-aspect':
				self.keep_aspect = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'transparent-color':
				self.transparent_color = value

			elif attr == 'alpha':
				self.alpha = int(value)

			elif attr == 'macro':
				self.macro = value[1:-1]

			elif attr == 'menu':
				self.menu = value[1:-1]

			elif attr == 'on-close':
				self.on_close = value[1:-1]

		elif self.type == 'LABEL':
			if attr == 'text':
				self.text = value[1:-1]

			elif attr == 'image':
				self.image = value[1:-1]

			elif attr == 'stretch':
				self.stretch = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'keep-aspect':
				self.keep_aspect = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'align':
				self.align = value

			elif attr == 'text-wrap':
				self.text_wrap = {'true': True, 'false': False, 'none': None}[value]

		elif self.type == 'BUTTON':
			if attr == 'text':
				self.text = value[1:-1]

			elif attr == 'image':
				self.image = value[1:-1]

			elif attr == 'command':
				self.command = value[1:-1]

			elif attr == 'is-flat':
				self.is_flat = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'stretch':
				self.stretch = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'is-checked':
				self.is_checked = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'group':
				self.group = value[1:-1]

			elif attr == 'button-type':
				self.button_type = value

		elif self.type == 'INPUT':
			if attr == 'command':
				self.command = value[1:-1]

			elif attr == 'multi-line':
				self.multi_line = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'is-password':
				self.is_password = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'no-command':
				self.no_command = {'true': True, 'false': False, 'none': None}[value]

		elif self.type == 'OUTPUT':
			if attr == 'link-color':
				self.link_color = value

			elif attr == 'visited-color':
				self.visited_color = value

			elif attr == 'style':
				self.style = value[1:-1]

			elif attr == 'enable-http-images':
				self.enable_http_images = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'max-lines':
				self.max_lines = int(value)

			elif attr == 'image':
				self.image = value[1:-1]

		elif self.type == 'BROWSER':
			if attr == 'show-history':
				self.show_history = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'show-url':
				self.show_url = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'auto-format':
				self.auto_format = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'use-title':
				self.use_title = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'on-show':
				self.on_show = value[1:-1]

			elif attr == 'on-hide':
				self.on_hide = value[1:-1]

		elif self.type == 'MAP':
			if attr == 'icon-size':
				self.icon_size = int(value)

			elif attr == 'text-mode':
				self.text_mode = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'on-show':
				self.on_show = value[1:-1]

			elif attr == 'on-hide':
				self.on_hide = value[1:-1]

		elif self.type == 'INFO':
			if attr == 'highlight-color':
				self.highlight_color = value

			elif attr == 'tab-text-color':
				self.tab_text_color = value

			elif attr == 'tab-background-color':
				self.tab_background_color = value

			elif attr == 'tab-font-family':
				self.tab_font_family = value[1:-1]

			elif attr == 'tab-font-size':
				self.tab_font_size = int(value)

			elif attr == 'tab-font-style':
				self.tab_font_style = value[1:-1]

			elif attr == 'allow-html':
				self.allow_html = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'multi-line':
				self.multi_line = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'on-show':
				self.on_show = value[1:-1]

			elif attr == 'on-hide':
				self.on_hide = value[1:-1]

			elif attr == 'on-tab':
				self.on_tab = value[1:-1]

		elif self.type == 'CHILD':
			if attr == 'left':
				self.left = value[1:-1]

			elif attr == 'right':
				self.right = value[1:-1]

			elif attr == 'is-vert':
				self.is_vert = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'splitter':
				self.splitter = int(value)

			elif attr == 'show-splitter':
				self.show_splitter = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'lock':
				self.lock = value

		elif self.type == 'TAB':
			if attr == 'tabs':
				self.tabs = value[1:-1]

			elif attr == 'current-tab':
				self.current_tab = value[1:-1]

			elif attr == 'multi-line':
				self.multi_line = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'on-tab':
				self.on_tab = value[1:-1]

		elif self.type == 'GRID':
			if attr == 'cells':
				self.cells = (value[:value.find('x')], value[value.find('x')+1:])

			elif attr == 'current-cell':
				self.current_cell = (value[:value.find(',')], value[value.find(',')+1:])

			elif attr == 'show-lines':
				self.show_lines = value

			elif attr == 'small-icons':
				self.small_icons = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'show-names':
				self.show_names = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'enable-http-images':
				self.enable_http_images = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'link-color':
				self.link_color = value

			elif attr == 'visited-color':
				self.visited_color = value

			elif attr == 'line-color':
				self.line_color = value

			elif attr == 'style':
				self.style = value[1:-1]

			elif attr == 'is-list':
				self.is_list = {'true': True, 'false': False, 'none': None}[value]

		elif self.type == 'BAR':
			if attr == 'bar-color':
				self.bar_color = value

			elif attr == 'is-slider':
				self.is_slider = {'true': True, 'false': False, 'none': None}[value]

			elif attr == 'width':
				self.width = int(value)

			elif attr == 'dir':
				self.dir = value

			elif attr == 'angle1':
				self.angle1 = int(value)

			elif attr == 'angle2':
				self.angle2 = int(value)

			elif attr == 'value':
				self.value = int(value)

			elif attr == 'on-change':
				self.on_change = value[1:-1]


	def save(self):
		sav = '\telem "%s"\n' % self.id

		if self._dmide_comment:
			sav += '\t\t_dmide_comment = "%s"\n' % self._dmide_comment
		if self._dmide_parent:
			sav += '\t\t_dmide_parent = %s\n' % self._dmide_parent

		sav += '\t\ttype = %s\n' % self.type
		sav += '\t\tpos = %s,%s\n' % (self.pos[0], self.pos[1])
		sav += '\t\tsize = %sx%s\n' % (self.size[0], self.size[1])
		anchor = self.anchor1
		if anchor == None:
			anchor = 'none'
		else:
			anchor = '%s,%s' % (self.anchor1[0], self.anchor1[1])
		sav += '\t\tanchor1 = %s\n' % anchor
		anchor = self.anchor2
		if anchor == None:
			anchor = 'none'
		else:
			anchor = '%s,%s' % (self.anchor2[0], self.anchor2[1])
		sav += '\t\tanchor2 = %s\n' % anchor
		sav += '\t\tfont-family = "%s"\n' % self.font_family
		sav += '\t\tfont-size = %s\n' % self.font_size
		sav += '\t\tfont-style = "%s"\n' % ''.join(self.font_style)
		sav += '\t\ttext-color = %s\n' % self.text_color
		sav += '\t\tbackground-color = %s\n' % self.background_color
		sav += '\t\tis-visible = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_visible]
		sav += '\t\tis-disabled = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_disabled]
		sav += '\t\tis-transparent = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_transparent]
		sav += '\t\tis-default = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_default]
		sav += '\t\tborder = %s\n' % self.border
		sav += '\t\tdrop-zone = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.drop_zone]
		sav += '\t\tright-click = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.right_click]
		sav += '\t\tsaved-params = "%s"\n' % self.saved_params

		if self.type == 'MAIN':
			sav += '\t\ttitle = "%s"\n' % self.title
			sav += '\t\ttitlebar = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.titlebar]
			sav += '\t\tstatusbar = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.statusbar]
			sav += '\t\tcan-close = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.can_close]
			sav += '\t\tcan-minimize = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.can_minimize]
			sav += '\t\tcan-resize = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.can_resize]
			sav += '\t\tis-pane = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_pane]
			sav += '\t\tis-minimized = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_minimized]
			sav += '\t\tis-maximized = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.is_maximized]
			sav += '\t\tcan-scroll = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.can_scroll]
			sav += '\t\ticon = "%s"\n' % self.icon
			sav += '\t\timage = "%s"\n' % self.image
			sav += '\t\timage-mode = %s\n' % self.image_mode
			sav += '\t\tkeep-aspect = %s\n' % {True: 'true', False: 'false', None: 'none'}[self.keep_aspect]
			sav += '\t\ttransparent-color = %s\n' % self.transparent_color
			sav += '\t\talpha = %s\n' % self.alpha
			sav += '\t\tmacro = "%s"\n' % self.macro
			sav += '\t\tmenu = "%s"\n' % self.menu
			sav += '\t\ton-close = "%s"\n' % self.on_close

		elif self.type == 'LABEL':
			sav += '\t\ttext = "%s"\n' % self.text
			sav += '\t\timage = "%s"\n' % self.image
			sav += '\t\tstretch = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.stretch]
			sav += '\t\tkeep-aspect = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.keep_aspect]
			sav += '\t\talign = %s\n' % self.align
			sav += '\t\ttext-wrap = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.text_wrap]

		elif self.type == 'BUTTON':
			sav += '\t\ttext = "%s"\n' % self.text
			sav += '\t\timage = "%s"\n' % self.image
			sav += '\t\tcommand = "%s"\n' % self.command
			sav += '\t\tis-flat = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.is_flat]
			sav += '\t\tstretch = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.stretch]
			sav += '\t\tis-checked = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.is_checked]
			sav += '\t\tgroup = "%s"\n' % self.group
			sav += '\t\tbutton-type = %s\n' % self.button_type

		elif self.type == 'INPUT':
			sav += '\t\tcommand = "%s"\n' % self.command
			sav += '\t\tmulti-line = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.multi_line]
			sav += '\t\tis-password = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.is_password]
			sav += '\t\tno-command = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.no_command]

		elif self.type == 'OUTPUT':
			sav += '\t\tlink-color = %s\n' % self.link_color
			sav += '\t\tvisited-color = %s\n' % self.visited_color
			sav += '\t\tstyle = "%s"\n' % self.style
			sav += '\t\tenable-http-images = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.enable_http_images]
			sav += '\t\tmax-lines = %s\n' % self.max_lines
			sav += '\t\timage = "%s"\n' % self.image

		elif self.type == 'BROWSER':
			sav += '\t\tshow-history = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.show_history]
			sav += '\t\tshow-url = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.show_url]
			sav += '\t\tauto-format = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.auto_format]
			sav += '\t\tuse-title = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.use_title]
			sav += '\t\ton-show = "%s"\n' % self.on_show
			sav += '\t\ton-hide = "%s"\n' % self.on_hide

		elif self.type == 'MAP':
			sav += '\t\ticon-size = %s\n' % self.icon_size
			sav += '\t\ttext-mode = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.text_mode]
			sav += '\t\ton-show = "%s"\n' % self.on_show
			sav += '\t\ton-hide = "%s"\n' % self.on_hide

		elif self.type == 'INFO':
			sav += '\t\thighlight-color = %s\n' % self.highlight_color
			sav += '\t\ttab-text-color = %s\n' % self.tab_text_color
			sav += '\t\ttab-background-color = %s\n' % self.tab_background_color
			sav += '\t\ttab-font-family = "%s"\n' % self.tab_font_family
			sav += '\t\ttab-font-size = %s\n' % self.tab_font_size
			sav += '\t\ttab-font-style = "%s"\n' % self.tab_font_style
			sav += '\t\tallow-html = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.allow_html]
			sav += '\t\tmulti-line = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.multi_line]
			sav += '\t\ton-show = "%s"\n' % self.on_show
			sav += '\t\ton-hide = "%s"\n' % self.on_hide
			sav += '\t\ton-tab = "%s"\n' % self.on_tab

		elif self.type == 'CHILD':
			sav += '\t\tleft = "%s"\n' % self.left
			sav += '\t\tright = "%s"\n' % self.right
			sav += '\t\tis-vert = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.is_vert]
			sav += '\t\tsplitter = %s\n' % self.splitter
			sav += '\t\tshow-splitter = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.show_splitter]
			sav += '\t\tlock = %s\n' % self.lock

		elif self.type == 'TAB':
			sav += '\t\ttabs = "%s"\n' % self.tabs
			sav += '\t\tcurrent-tab = "%s"\n' % self.current_tab
			sav += '\t\tmulti-line = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.multi_line]
			sav += '\t\ton-tab = "%s"\n' % self.on_tab

		elif self.type == 'GRID':
			sav += '\t\tcells = %sx%s\n' % (self.cells[0], self.cells[1])
			sav += '\t\tcurrent-cell = %s,%s\n' % (self.current_cell[0], self.current_cell[1])
			sav += '\t\tshow-lines = %s\n' % self.show_lines
			sav += '\t\tsmall-icons = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.small_icons]
			sav += '\t\tshow-names = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.show_names]
			sav += '\t\tenable-http-images = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.enable_http_images]
			sav += '\t\tlink-color = %s\n' % self.link_color
			sav += '\t\tvisited-color = %s\n' % self.visited_color
			sav += '\t\tline-color = %s\n' % self.line_color
			sav += '\t\tstyle = "%s"\n' % self.style
			sav += '\t\tis-list = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.is_list]

		elif self.type == 'BAR':
			sav += '\t\tbar-color = %s\n' % self.bar_color
			sav += '\t\tis-slider = %s\n' % {False: 'false', True: 'true', None: 'none'}[self.is_slider]
			sav += '\t\twidth = %s\n' % self.width
			sav += '\t\tdir = %s\n' % self.dir
			sav += '\t\tangle1 = %s\n' % self.angle1
			sav += '\t\tangle2 = %s\n' % self.angle2
			sav += '\t\tvalue = %s\n' % self.value
			sav += '\t\ton-change = "%s"\n' % self.on_change
		return sav


def DMFREAD(dmf):

	type_re = re.compile(r'\A(\w+) "(.*)"')
	elem_re = re.compile(r'\A\telem( "(.*)"|)')
	value_re = re.compile(r'\A\t\t(\S+) = (.*)')

	line_n = -1
	parent = None
	node = None
	nodes = []

	if isinstance(dmf, str) or isinstance(dmf, unicode):
		if not '\n' in dmf:
			dmf = open(dmf, 'r').read()

		dmf = dmf.split('\n')

	while line_n < len(dmf)-1:
		line_n += 1
		line = dmf[line_n]

		if len(line) and line[-1] == '\r':
			line = line[:-1]

		regex = type_re.search(line)
		if regex:
			if regex.group(1) == 'window':
				parent = DMFWindowGroup(regex.group(2))
			elif regex.group(1) == 'macro':
				parent = DMFMacroGroup(regex.group(2))
			elif regex.group(1) == 'menu':
				parent = DMFMenuGroup(regex.group(2))

			nodes.append(parent)
			node = None
			continue

		regex = elem_re.search(line)
		if regex and parent:
			if isinstance(parent, DMFWindowGroup):
				node = DMFWindow(parent, regex.group(2))
			elif isinstance(parent, DMFMacroGroup):
				node = DMFMacro(parent, regex.group(2))
			elif isinstance(parent, DMFMenuGroup):
				node = DMFMenu(parent, regex.group(2))

			continue

		regex = value_re.search(line)
		if regex and node:
			node.setattr(regex.group(1), regex.group(2))
			continue

		if line == '':
			node = None
			parent = None

	return nodes


def DMFWRITE(nodes, dmf):
	save = ''

	for node in nodes:
		save += node.save()

	open(dmf, 'w').write(save)
