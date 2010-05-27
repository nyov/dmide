"""
DMIDE Icon Viewer
(Icon Browser??)
"""

import wx

# Import modules that can read DMI files
import core
from core import *

# Import custom IconList control
import core.iconlistctrl as wxIconList

# Import threading for non-blocking file open
import thread


"""
Note: This class could also be done as a panel.
It would have its own child IconListCtrl, but would (probably?) need a few callbacks.

For an IconViewer that only shows a list of states, this works well, but
any future designs that move away from how DreamMaker displys icons could mean
that this code will need to be changed a lot.
"""
class IconViewer(wxIconList.IconListCtrl):
	""" Displays the contents of a DMI file for editing. """

	stipple = None

	def __init__(self, root, *args, **kwargs):
		if not IconViewer.stipple:
			IconViewer.stipple = wx.Bitmap(os.path.join(wx.GetApp().get_dir(), 'stipple.png'))

		wxIconList.IconListCtrl.__init__(self, root, *args, **kwargs)

		# use Crashed's IconList widget to display icons
		#self.iconlist = wxIconList.IconListCtrl(self)

		#self.SetItemCount(100)

		#self.iconlist = MyIconListCtrl(self)

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

		# TODO: Make this virtual and pythonic somehow
		self.SetIconSize(width, height)

		self.SetItemCount(len(self.icons))

		self.dirty = True
		# Window needs updating, so update it
		#	# Already done by SetItemCount()
##		self.Layout()
##		self.Draw()
##		self.Refresh(False)

	def ClearBackground(self, dc):
		old_brush = dc.GetBrush()

		brush = wx.Brush(wx.Color(0, 0, 0), wx.SOLID)
		brush.SetStipple(IconViewer.stipple)
		dc.SetBrush(brush)
		dc.SetPen(wx.TRANSPARENT_PEN)
		w,h = self.GetVirtualSize()
		dc.DrawRectangle(0, 0, w, h)

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
			# Could also just clear the whole selection, but this code could
			#  also be used when cutting only part of a selection
			itemsSelected = list(self.GetSelection())
			while len(itemsSelected):
				x = itemsSelected.pop()
				self._selStore.OnItemDelete(x)
				self._selStore.SetItemCount(self._selStore._count-1)

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

		# Could also just clear the whole selection, but this code could
		#  also be used when deleting only part of a selection
		itemsSelected = list(self.GetSelection())

		while len(itemsSelected):
			x = itemsSelected.pop()
			self._selStore.OnItemDelete(x)
			self._selStore.SetItemCount(self._selStore._count-1)

		for icon in icons:
			self.icons.remove(icon)

		self.update()

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
			dc.DrawLabel('m', rect, wx.ALIGN_TOP | wx.ALIGN_LEFT)
			dc.SetFont(prev_font)
