"""

Custom IconList Control
Uses a grid to display a list of like-sized icons.
Icons are arranged left-to-right, top-to-bottom.

"""

import wx
from agw.ultimatelistctrl import SelectionStore



ITEM_STATE_DEFAULT = 0
ITEM_STATE_SELECTED = 1


class IconListCtrl(wx.PyScrolledWindow):
	""" 
	IconListCtrl
	
	"""
	
	def __init__(self, *args, **kwargs):
		wx.ScrolledWindow.__init__(self, *args, **kwargs)

		self._items = 0
		self._selStore = SelectionStore()
		self._buffer = wx.EmptyBitmap(1, 1)

		self._box_size = (32, 32) # total size including label spacing of an item this value is soon replaced anyways
		# label_spacing needs to be based on font and size of leftoficon (M)
		self._label_spacing = (32,20) # extra spacing added below and to the left of the icon, that the label takes up
		self._spacing = (8, 8) # totally empty spacing between 'IconListItem's
		self._icon_size = (32, 32) # size of the actual bitmap that will be drawn
		self.SetLabelFont()

		self._cols = 0
		self._rows = 0

		self._selected_index = -1

		self.SetScrollRate(8, 8)

		self._mouse_position = (-1, -1)
		self._action_position = (-1, -1)

		# tell the control it needs to redraw
		self.dirty = False

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
		self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
		self.Bind(wx.EVT_IDLE, self.OnIdle)
		self.Bind(wx.EVT_SCROLLWIN, self.OnScroll)

		wx.CallAfter(self.Bind, wx.EVT_SIZE, self.OnSize)

		def refresh():
			self.Layout()
			self.Draw()
			self.Refresh(False)

		wx.CallAfter(refresh)

	def Layout(self):
		if self._items > 0:
			boxwidth, boxheight = self._box_size[0] + self._spacing[0], self._box_size[1] + self._spacing[1]
			hspace, vspace = self.GetClientSizeTuple()

			cols = max(1, hspace / boxwidth)
			rows = self._items / cols + 1

			self.SetVirtualSize((cols * boxwidth, rows * boxheight))

			if cols != self._cols or rows != self._rows:
				self._cols = cols
				self._rows = rows
				return True

	def HitTest(self, x, y):
			# TODO: Make HitTest aware of whitespace between images that should not return an item

			count = self.GetItemCount()

			if not count:
				return wx.NOT_FOUND, None

			# Note: Could also loop through everything and use if rect.Contains((x, y))
			#       in order to check things. Dunno why though.
			x, y = self.CalcUnscrolledPosition(x, y)

			boxwidth, boxheight = self._box_size

			# TODO!!: fix rounding errors, these formulas might be off a bit
			# also add support for onitemright/left and such
			col = x / (boxwidth + self._spacing[0]) + 1
			if col > self._cols:
				return wx.NOT_FOUND, None

			row = y / (boxheight + self._spacing[1]) + 1
			if row > self._rows:
				return wx.NOT_FOUND, None

			# here, do a rect.Contains(x, y)
			# rectx = (col-1)*(boxwidth+_spacing[0])+_spacing[0]/2
			# recty = (row-1)*(boxheight+_spacing[1])+_spacing[1]/2
			# rectw = boxwidth
			# recth = boxheight

			index = ((row-1) * self._cols) + col - 1

			# TODO!!: Ensure clicks on space beyond iconbox areas don't count
			# ie, with code as currently, space beyond the right column counts as an
			# increment to the item in the next row. This is incorrect.

			if index >= count:
				return wx.NOT_FOUND, None

			rectx = (col-1) * self.GetColWidth() + 0.5 * self._spacing[0]
			recty = (row-1) * self.GetRowHeight() + 0.5 * self._spacing[1]
			rectw = boxwidth
			recth = boxheight

			testrect = wx.Rect(rectx, recty, rectw, recth)

			if not testrect.Contains((x, y)):
				# Not clicked on the icon itself
				# This is probably the wrong return flag
				return wx.NOT_FOUND, wx.LIST_HITTEST_NOWHERE

			# Should an IconListItem or merely an index be returned?
			#item = self.GetItem(index)
			#TODO: Calculate the appropriate wx.LIST flag to be returned
			return index, wx.LIST_HITTEST_ONITEM

	def Draw(self):
		# TODO: Change draw to be more efficient and not re-draw things that aren't visible
		self._buffer = wx.EmptyBitmap(*self.GetVirtualSize())

		dc = wx.BufferedDC(None, self._buffer)
		gcdc = wx.GCDC(dc)

		dc.SetBrush(wx.WHITE_BRUSH)
		dc.Clear()

		gcdc.SetFont(self._font)

		if not self._items:
			return

		boxwidth, boxheight = self._box_size

		spacing_h = self._spacing[0]
		spacing_v = self._spacing[1]        

		#TODO: move these calcs into Layout() or onsize
		# they don't change unless the size of the drawing space changes
		hspace, vspace = self.GetClientSizeTuple()

		cols = max(1, hspace / (boxwidth + spacing_h))
		rows = self._items / cols + 1

		view_x = self.GetViewStart()[0] * self.GetScrollPixelsPerUnit()[0]
		view_y = self.GetViewStart()[1] * self.GetScrollPixelsPerUnit()[1]
		view_w = view_x + self.GetClientSize()[0]
		view_h = view_y + self.GetClientSize()[1]

		item_count = 0
		max_items = self._items

		for row in xrange(rows):
			for col in xrange(cols):
				item_count += 1
				if item_count > max_items:
					return

				x = col * (boxwidth + spacing_h) + (spacing_h / 2)
				y = row * (boxheight + spacing_v) + (spacing_v / 2)

				item = self.OnGetItem(item_count-1)

				if isinstance(item, tuple) or isinstance(item, list):
					item = IconListItem(*item)

				if not isinstance(item, IconListItem):
					raise AssertionError, 'Item passed from OnGetItem is not a tuple or IconListItem.'

				item.Draw(gcdc, (x, y, boxwidth, boxheight), self._selected_index == item_count-1)

	def OnPaint(self, event):
		temp_buffer = wx.EmptyBitmap(*self.GetClientSize())
		dc = wx.BufferedPaintDC(self, temp_buffer, wx.BUFFER_CLIENT_AREA)
		dc.Clear()
		self.PrepareDC(dc)
		dc.DrawBitmap(self._buffer, 0, 0)

		try:
			if self._action_position != (-1, -1):
				x, y = self.CalcUnscrolledPosition(self._action_position)
				width = self._mouse_position[0] - self._action_position[0]
				height = self._mouse_position[1] - self._action_position[1]

				if width < 0:
					x += width
					width = -width

				if height < 0:
					y += height
					height = -height

				gcdc = wx.GCDC(dc)
				highlight_colour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
				highlight_colour.Set(*highlight_colour.Get(), alpha=64)
				gcdc.SetBrush(wx.Brush(highlight_colour))
				gcdc.DrawRectangle(x, y, width, height)
		except Exception, e:
			print e

	def OnSize(self, event):
		event.Skip()

		if self.Layout():
			self.dirty = True
			idle_event = wx.IdleEvent()
			idle_event.SetEventType(wx.EVT_IDLE.typeId)
			wx.CallAfter(wx.PostEvent, self, idle_event)

	def OnScroll(self, event):
		event.Skip()
		self.Refresh(False)

	def OnMouse(self, event):
		self._mouse_position = event_pos = event.GetX(), event.GetY()

		if event.GetEventType() == wx.EVT_MOUSEWHEEL:
			event.Skip()

		elif event.LeftDown():
			self._action_position = event_pos
			self.CaptureMouse()
			self.Refresh()

		elif event.LeftUp():
			if self.HasCapture():
				self.ReleaseMouse()

			itemIndex, hitResult = self.HitTest(*event_pos)

			self._action_position = (-1, -1)
			self._selected_index = itemIndex

			self.dirty = True
			#self.Draw()
			#self.Refresh(False)

		elif event.Dragging():
			self.Refresh()

		event.Skip()

	def GetRowHeight(self):
		return self._box_size[1] + self._spacing[1]

	def GetColWidth(self):
		return self._box_size[0] + self._spacing[0]

	def GetLabelFont(self):
		""" Returns the font for the icon labels. """
		return self._font

	def SetIconSize(self, width=32, height=32):
		self._icon_size = width, height
		self.RecalcSpacing()

	def SetLabelFont(self, font=None):
		"""
		Sets the font for the icon labels.
		
		'font' takes a 'wx.Font' object
		"""
		if font is None:
			font = wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT)
		self._font = font

		dc = wx.BufferedDC(None, self._buffer)
		dc.SetFont(self._font)
		labelx = self._label_spacing[0]
		labely = dc.GetCharHeight()
		self._label_spacing = (labelx, labely)
		self.RecalcSpacing()
		self.Draw()

	def RecalcSpacing(self):
		oldboxsize = self._box_size
		self._box_size = (self._icon_size[0] + self._label_spacing[0], self._icon_size[1] + self._label_spacing[1])

		if self._box_size != oldboxsize:
			self.Layout()
			self.Draw()
			self.Refresh()

	def GetBoxSize(self):
		return self._box_size

	def GetItemCount(self):
		return self._items

	def SetItemCount(self, items):
		if items >= 0:
			self._items = items
			self.Layout()
			self.Draw()

	def OnIdle(self, event):
		if self.dirty:
			self.dirty = False
			self.Draw()
			self.Refresh(False)


class IconListItem:
	def __init__(self, label = '', image = None):
		self._label = label
		self._image = image

	def Draw(self, dc, rect, highlight=False):

		if self._image:
			dc.DrawBitmap(self._image, rect[0] + (rect[2] - self._image.Width) / 2, rect[1], True)

		new_label = self._label

		if dc.GetTextExtent(self._label)[0] > rect[2]:
			while True:
				new_label = new_label[:-1]
				if dc.GetTextExtent(new_label + '...')[0] > rect[2] and len(new_label):
					continue
				break

			new_label = new_label + '...'

		if highlight:
			old_brush = dc.GetBrush()
			highlight_colour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
			highlight_colour.Set(*highlight_colour.Get(), alpha=64)
			dc.SetBrush(wx.Brush(highlight_colour))
			dc.DrawRoundedRectangle(*rect, radius=4)
			dc.SetBrush(old_brush)

		dc.DrawLabel(new_label, rect, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM)

