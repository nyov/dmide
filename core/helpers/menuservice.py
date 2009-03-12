

from core import *
import xml.sax
import xml.sax.handler



def installMenuService(window):
	""" Build a MenuBar for the top-level window as read from an XML file """

	if os.path.exists('menubar.xml'):
		handler = MenuBarHandler()
		parser = xml.sax.parse('menubar.xml', handler)
	elif os.path.exists(os.path.join('settings', 'menubar.xml')):
		handler = MenuBarHandler()
		parser = xml.sax.parse(os.path.join('settings', 'menubar.xml'), handler)
	else:
		handler = MenuBarHandler()
		parser = xml.sax.parseString(default_menu, handler)

	menu_bar = wx.MenuBar()

	for menu_name in handler.ordered_list:
		new_menu = wx.Menu()

		for submenu in handler.menu_bars[menu_name]:
			if submenu == 1: 
				new_menu.AppendSeparator()
				continue

			title = submenu[1]
			if submenu[2]: title += '\t%s'%submenu[2]

			if submenu[4]:
				new_menu.Append(globals()[submenu[0]], title, submenu[3], globals()[submenu[4]])
			else:
				new_menu.Append(globals()[submenu[0]], title, submenu[3])

		menu_bar.Append(new_menu, menu_name)

	window.SetMenuBar(menu_bar)



class MenuBarHandler(xml.sax.handler.ContentHandler):
	""" Handler for reading the XML """



	def __init__(self):
		self.menu_bars = {}
		self.ordered_list = []
		self.current = None



	def startElement(self, name, attributes):
		if name == 'menu_bar':
			menu_title = attributes['title']
			self.ordered_list.append(menu_title)
			self.menu_bars[menu_title] = []
			self.current = menu_title

		elif name == 'menu':
			if not self.current: return

			if 'type' in attributes:
				if attributes['type'] == 'separator':
					self.menu_bars[self.current].append(1)
				return

			id = attributes['id']
			title = attributes['title']
			macro = ''
			desc = ''
			flags = ''

			if 'macro' in attributes:
				macro = attributes['macro']
			if 'desc' in attributes:
				desc = attributes['desc']
			if 'flags' in attributes:
				flags = attributes['flags']

			self.menu_bars[self.current].append([id, title, macro, desc, flags])



	def endElement(self, name):
		pass



default_menu = '''
<menu_list>
	<menu_bar title="File">
		<menu id="ID_FILE_NEW"    title="New"     macro="Ctrl+N"       desc="Create a new file." />
		<menu id="ID_FILE_OPEN"   title="Open"    macro="Ctrl+O"       desc="Open a file." />
		<menu id="ID_FILE_CLOSE"  title="Close"   macro="Ctrl+Shift+C" desc="Close the current file." />
		<menu id="ID_FILE_SAVE"   title="Save"    macro="Ctrl+S"       desc="Save the current file." />
		<menu id="ID_FILE_SAVEAS" title="Save As" macro="Ctrl+Shift+S" desc="Save the current file in a different title." />
		<menu type="separator" />
		<menu id="ID_FILE_NEWENVIRONMENT" title="New Environment" macro="Ctrl+Shift+N" desc="Create a new environment." />
		<menu id="ID_FILE_OPENENVIRONMENT" title="Open Environment" macro="Ctrl+Shift+O" desc="Open an environment." />
		<menu type="separator" />
		<menu id="ID_EXIT"        title="Exit"    macro="Ctrl+Q"       desc="Exit DMIDE." />
	</menu_bar>

	<menu_bar title="Edit">
		<menu id="ID_EDIT_UNDO"      title="Undo"       macro="Ctrl+Z" desc="Undo last change." />
		<menu id="ID_EDIT_REDO"      title="Redo"       macro="Ctrl+Y" desc="Redo last undo change." />
		<menu type="separator" />
		<menu id="ID_EDIT_CUT"       title="Cut"        macro="Ctrl+X" desc="Cut the selected text." />
		<menu id="ID_EDIT_COPY"      title="Copy"       macro="Ctrl+C" desc="Copy the selected text." />
		<menu id="ID_EDIT_PASTE"     title="Paste"      macro="Ctrl+V" desc="Paste the text in clipboard." />
		<menu id="ID_EDIT_DELETE"    title="Delete"     macro="Del"    desc="Delete the selected text." />
		<menu type="separator" />
		<menu id="ID_EDIT_FIND"      title="Find"       macro="Ctrl+F" desc="Find text in this document." />
		<menu id="ID_EDIT_FINDNEXT"  title="Find Next"  macro="F3"     desc="Find the next text in this document." />
		<menu id="ID_EDIT_FINDPREV"  title="Find Previous"  macro="Shift+F3"     desc="Find the previous text in this document." />
		<menu id="ID_EDIT_REPLACE"   title="Replace"    macro="Ctrl+H" desc="Replace text in this document." />
		<menu type="separator" />
		<menu id="ID_EDIT_GOTOLINE"  title="Goto Line"  macro="Ctrl+G" desc="Go to specified line." />
		<menu id="ID_EDIT_SELECTALL" title="Select All" macro="Ctrl+A" desc="Select all text in this document." />
	</menu_bar>

	<menu_bar title="View">
		<menu id="ID_VIEW_FILETOOLBAR" title="File Toolbar" desc="Toggle view of the file toolbar." flags="ID_ITEM_CHECK" />
		<menu type="separator" />
		<menu id="ID_VIEW_FILETREE"    title="File Tree"    desc="Toggle view of the file tree."    flags="ID_ITEM_CHECK" />
		<menu id="ID_VIEW_EDITOR"  title="Main Editor"      desc="Toggle view of the main editor."  flags="ID_ITEM_CHECK" />
		<menu id="ID_VIEW_BUILDINFORMATION" title="Build Information" desc="Toggle view of the build information." flags="ID_ITEM_CHECK" />
		<menu id="ID_VIEW_CONSOLE" title="Console"          desc="Toggle view of the developer console." flags="ID_ITEM_CHECK" />
	</menu_bar>

	<menu_bar title="Perspective">
		<menu id="ID_PERSPECTIVE_DEFAULT" title="Default" desc="Load default perspective." />
		<menu id="ID_PERSPECTIVE_SAVE"    title="Save"    desc="Save perspective." />
		<menu id="ID_PERSPECTIVE_LOAD"    title="Load"    desc="Load perspective." />
		<menu type="separator" />
	</menu_bar>

	<menu_bar title="Options">
		<menu id="ID_OPTIONS_PERSPECTIVE" title="Perspective" desc="Settings for the look and feel of DMIDE." />
	</menu_bar>

	<menu_bar title="Help">
		<menu type="separator" />
		<menu id="ID_HELP_ABOUT" title="About" desc="About DMIDE." />
	</menu_bar>
</menu_list>
'''

