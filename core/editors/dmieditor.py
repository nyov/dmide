
"""

DMIDE Icon Editor

"""
import sys

if not hasattr(sys, 'frozen'):
	import wxversion
	wxversion.select("2.8")

import wx

import thread


import core
from core import *

import core.iconlistctrl as wxIconList


from draw import Draw


class DMIDE_DMIEditor(wx.Panel):
	def __init__(self, root):
		wx.Panel.__init__(self, root)

		#self.palette = DMIPalette(self)
		self.viewer = IconViewer(self)
		self.editor = DMIEditor(self)

		sizer = wx.BoxSizer(wx.VERTICAL)
		#sizer.Add(self.palette, 1, wx.ALL|wx.EXPAND)
		sizer.Add(self.viewer, 1, wx.ALL|wx.EXPAND)
		sizer.Add(self.editor, 1, wx.ALL|wx.EXPAND)
		self.SetSizer(sizer)

		self.modified = False

		self.editor.Hide()
		sizer.Hide(self.editor)
		self.Layout()

	def TitlePage(self, text):
		self.GetParent().TitlePage(text)

	def SetTitle(self, text):
		pass

	def Open(self, image):
		self.dmi_path = image
		self.viewer.Open(image)

	def selected(self, img):
		self.GetSizer().Hide(self.viewer)
		self.viewer.Hide()
		self.GetSizer().Show(self.editor)
		self.editor.Show()
		self.editor.Open(img.icons[0][0])
		self.Layout()


class DMIPalette(wx.Panel):
	def __init__(self, root):
		wx.Panel.__init__(self, root)

	def update(self, img):
		colors = img.getcolors(img.size[0]*img.size[1])
		print len(colors)
		print colors


round2 = lambda n,p=2: (n+p/2)/p*p


class DMIEditor(wx.ScrolledWindow):
	def __init__(self, parent, ):
		wx.ScrolledWindow.__init__(self, parent, style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN)

		self.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))
		self.init()
		self.init_binds()

	def Open(self, img):
		self.image = img
		#wx.CallAfter(self.GetParent().palette.update, img)

	def init(self):
		self.image = Image.new('RGBA', (32, 32)) # actual image
		self.zoom_buffer = None # zoomed wxBitmap image
		self.background = wx.Brush('WHITE')
		self.background.SetStipple(wx.EmptyBitmapRGBA(32,32,0,0,0,0))

		self.cursor = wx.EmptyBitmapRGBA(1, 1, 115, 140, 226, 128)

		self.show_grid = True
		self.show_cursor = True
		self.zoom_level = 1

		self.mouse_position = 0, 0
		self.action_position = -1, -1
		self.last_box = -1, -1
		self.dirty = False

		self.update()

	def init_binds(self):
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_SCROLLWIN, self.OnScroll)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseAction)
		self.Bind(wx.EVT_MOTION, self.OnMouseAction)
		self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseAction)

	def update(self):
		self.SetScrollRate(self.zoom_level, self.zoom_level)
		self.SetVirtualSize((self.image.size[0] * self.zoom_level, self.image.size[1] * self.zoom_level))
		self.Refresh(False)

		def update_title(win, zoom):
			win.SetTitle('DMI Editor - zoom: %ix' % zoom)

		wx.CallAfter(update_title, self.GetParent(), self.zoom_level)

	def get_scroll(self):
		xunits, yunits = self.GetScrollPixelsPerUnit()
		left, top = self.GetScrollPos(wx.HORIZONTAL) * xunits, self.GetScrollPos(wx.VERTICAL) * yunits

		return left, top

	def get_box(self, zoom=True):
		left, top = self.get_scroll()
		width, height = self.GetClientSizeTuple()

		if zoom:
			z = float(self.zoom_level)
			box = int(round(left / z)), int(round(top / z)), min(self.image.size[0], int(round2((left + width) / z))), min(self.image.size[1], int(round2((top + height) / z)))

			return box

		return (left, top, width, height)

	def OnEraseBackground(self, event):
		pass # eliminate some flicker

	def OnPaint(self, event):
		zoom_width, zoom_height = self.image.size[0] * self.zoom_level, self.image.size[1] * self.zoom_level

		dc = wx.BufferedPaintDC(self)
		self.DoPrepareDC(dc)
		dc.Clear()

		dc.SetPen(wx.TRANSPARENT_PEN)
		dc.SetBrush(self.background)

		dc.DrawRectangle(0, 0, zoom_width, zoom_height)

		if self.action_position != (-1, -1):
			# get real coords, not zoomed coords
			pos1, pos2 = self.TrueCoords(self.action_position), self.TrueCoords(self.mouse_position)
			image = self.image.copy()
			draw = Draw(image)
			#draw.rectangle(pos1, pos2, False, (192, 0, 192, 128))
			draw.ellipse(pos1, pos2) # draw an ellipse
			#draw.floodfill(pos1, (255, 0, 0, 255))
			self.dirty = image

		box = self.get_box()
		if self.dirty or box != self.last_box:
			self.last_box = box
			if type(self.dirty) != bool:
				cropped = self.dirty.crop(self.get_box())
			else:
				cropped = self.image.crop(self.get_box())
			cropped = cropped.resize((cropped.size[0] * self.zoom_level, cropped.size[1] * self.zoom_level))
			self.zoom_buffer = ImgToWx(cropped)
			self.dirty = False

		scroll_x, scroll_y = self.get_scroll()
		dc.DrawBitmap(self.zoom_buffer, scroll_x, scroll_y)

		if self.show_cursor and 0:
			dc.SetUserScale(1.0 * self.zoom_level, 1.0 * self.zoom_level)
			x = self.mouse_position[0] / self.zoom_level
			y = self.mouse_position[1] / self.zoom_level
			dc.DrawBitmap(self.cursor, x, y)
			dc.SetUserScale(1.0, 1.0)

		if self.show_grid and self.zoom_level > 1:
			# big enough to draw a grid!
			dc.SetPen(wx.Pen((60, 60, 60)))

			for x in xrange(0, zoom_width+1, int(zoom_width / self.image.size[0])):
				if x == 0: continue
				dc.DrawLine(x, 0, x, zoom_height)
			for y in xrange(0, zoom_height+1, int(zoom_height / self.image.size[1])):
				if y == 0: continue
				dc.DrawLine(0, y, zoom_width, y)

	def OnMouseAction(self, event):
		last_position = self.mouse_position
		self.mouse_position = self.CalcUnscrolledPosition(event.GetX(), event.GetY())

		self.SetFocusIgnoringChildren()

		if event.GetWheelRotation():
			if event.GetWheelRotation() > 0:
				if self.zoom_level < 2:
					self.zoom_level += 1
				else:
					self.zoom_level += 2
			else:
				if self.zoom_level > 1:
					if self.zoom_level > 2:
						self.zoom_level -= 2
					else:
						self.zoom_level -= 1

			self.dirty = True
			wx.CallAfter(self.Refresh, False)
			wx.CallAfter(self.update)

		elif event.LeftDown():
			self.action_position = self.mouse_position
			self.CaptureMouse()
			wx.CallAfter(self.Refresh, False)

		elif event.LeftUp():
			self.action_position = -1, -1
			if self.HasCapture():
				self.ReleaseMouse()

		elif event.Dragging() and event.LeftIsDown():
			if self.TrueCoords(last_position) == self.TrueCoords(self.mouse_position):
				return

			wx.CallAfter(self.Refresh, False)

	def OnSize(self, event):
		event.Skip()
		wx.CallAfter(self.Refresh, False)

	def OnScroll(self, event):
		event.Skip()
		wx.CallAfter(self.Refresh, False)

	def TrueCoords(self, coords):
		return (coords[0] / self.zoom_level, coords[1] / self.zoom_level)





"""
Note: This class could also be done as a panel.
It would have its own child IconListCtrl, but would (probably?) need a few callbacks.

For an IconViewer that only shows a list of states, this works well, but
any future designs that move away from how DreamMaker displys icons could mean 
that this code will need to be changed a lot.
"""
class IconViewer(wxIconList.IconListCtrl):
	""" Displays the contents of a DMI file for editing. """
	def __init__(self, root, *args, **kwargs):
		wxIconList.IconListCtrl.__init__(self, root, *args, **kwargs)
		
		# use Crashed's IconList widget to display icons
		#self.iconlist = wxIconList.IconListCtrl(self)
		
		#self.SetItemCount(100)
		
		#self.iconlist = MyIconListCtrl(self)
		
		# Layout maybe not necessary, but not hurting anything?
		#self.Layout()
		
		self.initAll()
		self.initBinds()
		
		#self.modified_callback = root.TitlePage
		
		
	
	def initAll(self):
		# Is last_pos really needed at all?
		#self.last_pos = -1
		
		# TODO: Make these comments better
		# TODO: Maybe give an 'image' attribute to each icon rather than an extra list?
		# Replace this  with DMIIconState objects?
		# Is the seperate list necessary?
		self.icons = [] # The icon_states from the DMI File
		self.images = [] # The wxBitmap (immediately dispalyable) version of icons
		
##		#image_list contains the graphical rep. of the states that go in the iconlist
##		self.image_list = None
		
		self.select_callback = self.GetParent()
		
		self.undo_buffer = None
		self.redo_buffer = None
		self.copy_buffer = None

		self.modified = False

		self.modified_callback = None
	
	def initBinds(self):
		##self.Bind(wx.EVT_SIZE, self.OnSize)
		
		#self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnIconSelect)
		#self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnIconStateEdit)
		
		self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
		self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
		
	def update(self):
		
		# TODO: Do IconViewer update() more efficiently
		# 		no need to re-update the whole set of icons if only 1 changed
		self.images = []
		if not len(self.icons):
			self.SetItemCount(len(self.icons))
			return
	
		#TODO: Store the width and height variables
		width, height = self.icons[0].icons[0][0].size
		
		for icon in self.icons:
			img = ImgToWx(icon.icons[0][0])
			self.images.append(img)

		self.SetItemCount(len(self.icons))
		
		# TODO: Make this virtual and pythonic somehow
		self.SetIconSize(width, height)
		
		# Window needs updating, so update it
		self.Layout()
		self.Draw()
		self.Refresh(False)
		
	
	def Open(self, path):
		# Is doing threading here safe?
		thread.start_new_thread(self._open, (path,))
		#self._open(path)
		
	def _open(self, path):
		self.dmi_path = path
		self.redo_buffer = None
		self.undo_buffer = None
		self.icons = cache.read(path, self) #dmi.DMIREAD(path)
		
		self.modified = False
		if self.modified_callback:
			self.modified_callback(self)
		wx.CallAfter(self.update)
		#self.update()
	
	def Save(self, path):
		if not path:
			if not self.dmi_path:
				return
			path = self.dmi_path
		else:
			self.dmi_path = path
		dmi.DMIWRITE(self.icons, path)
		self.modified = False
		if self.modified_callback:
			self.modified_callback(self)
	
	
	def New(self, path):
		self.dmi_path = path
		self.redo_buffer = None
		self.undo_buffer = None
		self.icons = cache.read(path, self) #dmi.DMIREAD(path)
		self.modified = False
		if self.modified_callback:
			self.modified_callback(self)
		self.update()
	
	def Close(self):
		# TODO: Look at all this stuff
		if self.modified:
			file = os.path.split(self.dmi_path)[-1]
			dlg = wx.MessageDialog(self, 'Save changes to %s?' % file, 'Save DMI', wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
			value = dlg.ShowModal()
			if value == wx.ID_YES:
				if self.dmi_path[-4:] != '.dmi':
					dlg2 = wx.FileDialog(self, message='Save a DMI', defaultDir=self.dmi_path, wildcard=dmicard, style=wx.SAVE|wx.CHANGE_DIR)
					if dlg2.ShowModal() == wx.ID_OK:
						dmipath = dlg2.GetPath()
						self.Save(dmipath)
					dlg2.Destroy()
				else:
					self.Save(self.dmi_path)
			elif value == wx.ID_CANCEL:
				return -1



		def CopyIcons(self, icons):
			copy = []
			for icon in icons:
				new_icon = dmi.Icon()
				new_icon.state = icon.state
				new_icon.dirs = icon.dirs
				new_icon.frames = icon.frames
				for x in icon.icons:
					new_icon.icons.append([y.copy() for y in x])
				new_icon.delays = icon.delays
				new_icon.loops = icon.loops
				new_icon.rewind = icon.rewind
				copy.append(new_icon)
			return copy

		def register_undo(self):
			self.modified = True
			if self.modified_callback:
				self.modified_callback(self)
			self.undo_buffer = self.CopyIcons(self.icons)
			self.redo_buffer = None

		def register_redo(self):
			self.modified = True
			if self.modified_callback:
				self.modified_callback(self)
			self.redo_buffer = self.CopyIcons(self.icons)

		def Redo(self, event=None):
			if self.redo_buffer != None:
				buffer = self.redo_buffer
				self.register_undo()
				self.icons = buffer
				self.update()

		def Undo(self, event=None):
			if self.undo_buffer != None:
				self.register_redo()
				self.icons = self.undo_buffer
				self.undo_buffer = None
				self.update()

		def Cut(self, event=None):
			selection = self.GetIconSelection()
			if len(selection):
				self.register_undo()
				self.Copy()
				for icon in selection:
					self.icons.remove(icon)
				for x in self.GetSelection():
					self.Select(x, 0)
				self.update()

		def Copy(self, event=None):
			if self.icons:
				self.copy_buffer = self.CopyIcons(self.GetIconSelection())
				try:
					clip_img = self.copy_buffer[0].icons[0][0]
				except:
					return

				clip_obj = wx.BitmapDataObject()
				clip_obj.SetBitmap(ImgToWx(clip_img))
				wx.TheClipboard.Open()
				wx.TheClipboard.SetData(clip_obj)
				wx.TheClipboard.Close()

		def Paste(self, event=None):
			if not self.dmi_path:
				return

			clip_obj = wx.BitmapDataObject()
			wx.TheClipboard.Open()
			success = wx.TheClipboard.GetData(clip_obj)
			wx.TheClipboard.Close()

			def paste_buffer():
				if not self.copy_buffer:
					return

				self.register_undo()
				for icon in self.copy_buffer:
					self.icons.append(icon)
				self.update()

			def paste_clip(img):
				self.register_undo()
				new_icon = dmi.Icon()
				new_icon.icons = [[img]]
				self.icons.append(new_icon)
				self.update()

			if success:
				clip_img = clip_obj.GetBitmap()
				img = WxToImg(clip_img)

				if self.copy_buffer:
					test = 0
					try:
						test = WxToImg(ImgToWx(self.copy_buffer[0].icons[0][0]))
					except:
						pass

					if test:
						if list(test.getdata()) == list(img.getdata()):
							paste_buffer()
						else:
							paste_clip(img)
					else:
						paste_clip(img)

				else:
					paste_clip(img)

			else:
				paste_buffer()

		def Delete(self, event=None):
			if not self.icons or not len(self.icons):
				return

			self.register_undo()
			icons = [self.icons[index] for index in self.GetSelection()]

			for x in self.GetSelection():
				self.Select(x, 0)

			for icon in icons:
				self.icons.remove(icon)

			self.update()
			self.Refresh(True)


	def GetSelection(self):
		return self._selStore._itemsSel

##	# TODO: Look at if this old version is of any use
##
##	def GetSelection(self):
##		selected = []
##		
##		for o in xrange(self.GetSelectedItemCount()):
##			sel = -1
##			if len(selected): sel = selected[-1]
##			x = self.GetNextSelected(sel)
##			if x == -1:
##				break;
##			selected.append(x)
##		
##		return selected

	# What is this procedure for?
	def GetIconSelection(self):
		selected = self.GetSelection()
		icons = []
		for index in selected:
			icons.append(self.icons[index])
		return icons

##	def OnSize(self, event):
##		# Is self.Refresh() needed?
##		self.Refresh()
##		
##		#Layout() IS needed if OnSize is bound
##		self.Layout()
		
	def OnIconSelect(self, event):
		pass
		#index = event.GetIndex()

		#if self.select_callback:
		#	self.select_callback.selected(self.icons[index])

	def OnIconStateEdit(self, event):
		if event.IsEditCancelled():
			event.Veto()
			return

		state, index = event.GetText(), event.GetIndex()

		self.register_undo()
		self.icons[index].state = state
		self.RefreshItem(index)
		self.OnIconSelect(event)
		
		
	def OnDoubleClick(self, event):
		
		pos = event.GetPosition()
		# print pos.x, ", ", pos.y

		#item, where = self.HitTest(pos)
		# Currently splitting up pos, since HitTest takes same as ULC one does
		item, where = self.HitTest(pos.x, pos.y)
		# print "item: ", item
		if item < 0 or item >= self.GetItemCount():
			return

		if self.select_callback:
			self.select_callback.selected(self.icons[item])
	
	def OnContextMenu(self, event):
		
		if not len(self.GetSelection()):
				return

		if not hasattr(self, 'menu_ids'):
			self.menu_ids = [ID_EDIT_UNDO, ID_EDIT_REDO, ID_EDIT_CUT, ID_EDIT_COPY, ID_EDIT_PASTE, ID_EDIT_DELETE]
			#[wx.NewId(), wx.NewId(), wx.NewId(), wx.NewId(), wx.NewId(), wx.NewId()]

			self.Bind(wx.EVT_MENU, self.Undo, id=self.menu_ids[0])
			self.Bind(wx.EVT_MENU, self.Redo, id=self.menu_ids[1])
			self.Bind(wx.EVT_MENU, self.Cut, id=self.menu_ids[2])
			self.Bind(wx.EVT_MENU, self.Copy, id=self.menu_ids[3])
			self.Bind(wx.EVT_MENU, self.Paste, id=self.menu_ids[4])
			self.Bind(wx.EVT_MENU, self.Delete, id=self.menu_ids[5])

		def make_menu_item(parent, id, text):
			item = wx.MenuItem(parent, id, text)
			if dmide_menu_type == 'fancy':
				bmp = wx.NullBitmap
				if str(id) in idn_to_art:
					bmp = wx.GetApp().art.getFromWx(idn_to_art[str(id)], (dmide_menu_art_size, dmide_menu_art_size), wx.ART_MENU)
				item.SetBitmap(bmp)
			return item

		menu = wx.Menu()
		menu.AppendItem(make_menu_item(menu, self.menu_ids[0], 'Undo'))
		menu.AppendItem(make_menu_item(menu, self.menu_ids[1], 'Redo'))
		menu.AppendSeparator()
		menu.AppendItem(make_menu_item(menu, self.menu_ids[2], 'Cut'))
		menu.AppendItem(make_menu_item(menu, self.menu_ids[3], 'Copy'))
		menu.AppendItem(make_menu_item(menu, self.menu_ids[4], 'Paste'))
		menu.AppendSeparator()
		menu.AppendItem(make_menu_item(menu, self.menu_ids[5], 'Delete'))

		self.PopupMenu(menu)
		menu.Destroy()

##	def OnGetItem(self, index):
##		try:
##				return (self.icons[index].state, self.images[index], self.icons[index].movement)
##		except IndexError:
##				return 'IndexError'


##		def OnGetItemText(self, index, col):
##			try:
##				return self.icons[index].state
##			except IndexError:
##				return 'IndexError'
##
##		def OnGetItemImage(self, index):
##			try:
##				return self.images[index]
##			except IndexError:
##				return 'IndexError'
##
##		def OnGetItemAttr(self, index):
##			return None

	def OnGetItem(self, index):
			#return (self.icons[index].state, self.icons[index].icons[0][0])
			try:
				return IconListItem(self.icons[index].state, self.images[index], self.icons[index].movement)
			except IndexError:
				# TODO: Put correct return value here
				return 'IndexError'



class IconListItem(wxIconList.IconListItem):
	def __init__(self, label, image, movement):
		self._label = label
		self._image = image
		self._movement = movement

	def Draw(self, dc, rect, highlight=False):
		wxIconList.IconListItem.Draw(self, dc, rect, highlight)

		if self._movement:
			prev_font = dc.GetFont()
			dc.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD, False, 'verdana'))
			rect = rect[0] - 4, rect[1] - 4, rect[2], rect[3]
			dc.DrawLabel('m', rect, wx.ALIGN_TOP | wx.ALIGN_LEFT)
			dc.SetFont(prev_font)




# TODO: Make this able to work as a standalone editor by running the .py directly

### Not-working code to use this as a standalone icon editor

##class StandaloneDMIEditor(wx.Frame):
##	"""Standalone Icon Editor frame for testing."""
##	def __init__(self, *args, **kwargs):
##		"""Create the standalone frame."""
##		wx.Frame.__init__(self, *args, **kwargs)
##		
##		#Build the menu bar
##		menubar = wx.MenuBar()
##		
##		filemenu = wx.Menu()
##
##		item = filemenu.Append(wx.ID_NEW, "&New", "Create a new DMI")
##		self.Bind(wx.EVT_MENU, self.OnNew, item)
##		item = filemenu.Append(wx.ID_OPEN, "&Open", "Open a DMI")
##		self.Bind(wx.EVT_MENU, self.OnOpen, item)
##		item = filemenu.Append(wx.ID_CLOSE, "&Close", "Close a DMI")
##		self.Bind(wx.EVT_MENU, self.OnClose, item)
##
##		filemenu.AppendSeparator()
##		
##		item = filemenu.Append(wx.ID_EXIT, text="&Quit")
##		self.Bind(wx.EVT_MENU, self.OnQuit, item)
##		
##		menubar.Append(filemenu, "&File")
##		self.SetMenuBar(menubar)
##		
##		#self.Panel = DemoPanel(self)
##		
##		self.iconviewer = DMIDE_IconViewer(self)
####		sizer = wx.BoxSizer(wx.VERTICAL)
####		sizer.Add(self.Panel, 1, wx.EXPAND | wx.ALL)
####		self.SetSizer(sizer)
####		self.Layout()
##		
##		#self.Fit()
##		
##	def OnQuit(self, event=None):
##		"""Exit application."""
##		self.Close()
##		
##	def OnNew(self, event=None):
##		"""Exit application."""
##		self.Close()
##		
##	def OnOpen(self, event=None):
##		"""Open a DMI File."""
##		
##		dlg = wx.FileDialog(self, 'Open File', os.getcwd(), '', imagefiles_wildcard, wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST)
##		if dlg.ShowModal() == wx.ID_OK:
##			path = dlg.GetPath()
##			dlg.Destroy()
##			self.Open(path)
##		
##	def Open(self, image):
##		self.dmi_path = image
##		self.iconviewer.Open(image)
##		#self.GetSizer().Fit(self)
##		#self.Layout()
##		
##	def OnClose(self, event=None):
##		"""Exit application."""
##		self.Close()
##
##
##
### strange way of importing core
### FIXME: do this better somehow
### Had to add dmide to the pythonpath for this to work
##
##if __name__ == '__main__':
##
##	import sys, os
##	if hasattr(sys, 'frozen'): 
##		mypath = os.path.split(sys.executable)[0]
##		
##	else: 
##		mypath = os.path.split(os.path.abspath(sys.argv[0]))[0]
##
##	mypath = os.path.join(mypath, "..")
##	mypath = os.path.join(mypath, "..")
##	mypath = os.path.normpath(mypath)
##	sys.path.append(mypath)
##	#print mypath
##
#### FIXME: dmide's package setup is bad
#### dmide itself needs to be a package too??
#### import of a module just called 'core' seems like a bad idea
##
##
##
##
##
##if __name__ == '__main__':
##	
##	# TODO: Come up with a standard/nice-ish way of getting a full shiny interface here
##
##	# if possible, optimize with psyco
##	try:
##		import psyco
##		psyco.full()
##	except ImportError:
##		pass	
##	
##	app = wx.App(redirect = 0) #stdio will stay at the console
##	frame = StandaloneDMIEditor(None, title="DMIDE Icon Editor (standalone)")
##	frame.Show()
##	app.MainLoop()
##	