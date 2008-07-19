''' Window Menu Service '''

from id import *
from safe_eval import safe_eval
import xml.sax
import xml.sax.handler

def InstallMenuService(window):
	parser=xml.sax.make_parser()
	handler=MenuBarHandler()
	parser.setContentHandler(handler)
	parser.parse('menubar.xml')

	menu_bar=wx.MenuBar()

	for menu_name in handler.ordered_list:
		new_menu=wx.Menu()
		for submenu in handler.menu_bars[menu_name]:
			if submenu==1: 
				new_menu.AppendSeparator()
				continue
			title=submenu[1]
			if submenu[2]: title+='\t%s'%submenu[2]

			if submenu[4]:
				new_menu.Append(globals()[submenu[0]], title, submenu[3], globals()[submenu[4]])
			else:
				new_menu.Append(globals()[submenu[0]], title, submenu[3])
		menu_bar.Append(new_menu, menu_name)

	window.SetMenuBar(menu_bar)


class MenuBarHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.menu_bars={}
        self.ordered_list=[]
        self.current=None

    def startElement(self, name, attributes):
        if name=='menu_bar':
            menu_title=attributes['title']
            self.ordered_list.append(menu_title)
            self.menu_bars[menu_title]=[]
            self.current=menu_title

        elif name=='menu':
            if not self.current: return

            if 'type' in attributes:
                if attributes['type']=='separator':
                    self.menu_bars[self.current].append(1)
                return

            id=attributes['id']
            title=attributes['title']
            macro=''
            desc=''
            flags=''

            if 'macro' in attributes:
                macro=attributes['macro']
            if 'desc' in attributes:
                desc=attributes['desc']
            if 'flags' in attributes:
                flags=attributes['flags']

            self.menu_bars[self.current].append([id, title, macro, desc, flags])

    def endElement(self, name):
        pass
