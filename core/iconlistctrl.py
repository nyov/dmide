"""
Custom IconList Control
Uses a grid to display a list of like-sized icons.
Icons are arranged left-to-right, top-to-bottom.

Partly based on the wxpython UltimateListCtrl

"""

import wx
import sys

# Import stuff for selection store
from agw.ultimatelistctrl import SelectionStore as ulcSelectionStore
import bisect


class IconListCtrl(wx.PyScrolledWindow):
	""" 
	IconListCtrl
	
	"""
	
	def __init__(self, *args, **kwargs):
		wx.PyScrolledWindow.__init__(self, *args, **kwargs)

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
		
		self._max_rows = sys.maxint
		self._max_cols = sys.maxint

		self.SetScrollRate(8, 8)

		self._mouse_position = (-1, -1)
		self._action_position = (-1, -1)

		# tell the control it needs to redraw
		self.dirty = False
		
		self._current = -1
		self._itemTo = -1
		self._itemFrom = -1
		
		self._buffer = wx.EmptyBitmap(*self.GetVirtualSize())
		dc = wx.BufferedDC(None, self._buffer)
		self.ClearBackground(dc)

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
			##boxwidth, boxheight = self._box_size[0] + self._spacing[0], self._box_size[1] + self._spacing[1]
			
			colwidth = self.GetColWidth()
			rowheight = self.GetRowHeight()
			
			hspace, vspace = self.GetClientSizeTuple()

			cols = min(self._max_cols, max(1, hspace / colwidth))
			rows = min(self._max_rows, self._items / cols + 1)
			#self.SetMinSize((cols * colwidth, rows * rowheight))
			self.SetVirtualSize((cols * colwidth, rows * rowheight))

			if cols != self._cols or rows != self._rows:
				self._cols = cols
				self._rows = rows
				# should this be here?
				self._buffer = wx.EmptyBitmap(*self.GetVirtualSize())
				dc = wx.BufferedDC(None, self._buffer)
				self.ClearBackground(dc)
				return True

	def HitTest(self, x, y):
			# TODO: Make HitTest aware of whitespace between images that should not return an item

			count = self.GetItemCount()

			if not count:
				return wx.NOT_FOUND, None

			# Note: Could also loop through everything and use if rect.Contains((x, y))
			#       in order to check things. Dunno why though.
			x, y = self.CalcUnscrolledPosition(x, y)

			boxwidth, boxheight = self.GetBoxSize()

			# TODO: fix rounding errors, these formulas might be off a bit
			# also add support for onitemright/left and such
			col = x / (boxwidth + self._spacing[0])
			if col >= self._cols:
				return wx.NOT_FOUND, None

			row = y / (boxheight + self._spacing[1])
			if row >= self._rows:
				return wx.NOT_FOUND, None

			# here, do a rect.Contains(x, y)
			# rectx = (col-1)*(boxwidth+_spacing[0])+_spacing[0]/2
			# recty = (row-1)*(boxheight+_spacing[1])+_spacing[1]/2
			# rectw = boxwidth
			# recth = boxheight

			index = ((row) * self._cols) + col

			if index >= count:
				return wx.NOT_FOUND, None

##			rectx = col * self.GetColWidth() + 0.5 * self._spacing[0]
##			recty = row * self.GetRowHeight() + 0.5 * self._spacing[1]

			rectx = self.GetItemX(index) + self._spacing[0]/2
			recty = self.GetItemY(index) + self._spacing[1]/2

			rectw = boxwidth
			recth = boxheight

			testrect = wx.Rect(rectx, recty, rectw, recth)

			if not testrect.Contains((x, y)):
				# Not clicked on the icon itself
				# This is probably the wrong return flag
				return wx.NOT_FOUND, None

			#TODO: Calculate the appropriate wx.LIST flag to be returned
			return index, wx.LIST_HITTEST_ONITEM

	def HighlightAll(self, on=True):
		if self.IsSingleSel():

			if on:
				raise Exception("can't do this in a single sel control")

			# we just have one item to turn off
			if self.HasCurrent() and self.IsHighlighted(self._current):
				self.HighlightItem(self._current, False)
				self.RefreshItem(self._current)

		else: # multi sel
			if not self.IsEmpty():
				self.HighlightItems(0, self.GetItemCount() - 1, on)

	def HighlightItems(self, itemFrom, itemTo, highlight=True):
		itemsChanged = []
		itemsChanged = self._selStore.SelectRange(itemFrom, itemTo, highlight)
		# None - Refresh everything, empty list: refresh nothing
		if itemsChanged==None or (itemsChanged and len(itemsChanged)):
			self.RefreshItems(itemsChanged)
	
	def HighlightItem(self, item, highlight=True):
		changed = False
		changed = self._selStore.SelectItem(item, highlight)
		return changed
	
	def ReverseHighlight(self, item):
		self.HighlightItem(item, not self.IsHighlighted(item))
		self.RefreshItem(item)
	
	def IsHighlighted(self, item):
		return self._selStore.IsSelected(item)
	
	def RefreshItems(self, itemsToRefresh):
		self.Draw(itemsToRefresh)
		self.Refresh(False)

	#TODO: Look at RefreshRect()
	def RefreshItem(self, item):
		self.Draw(item)
		self.Refresh(False)
	
	def ChangeCurrent(self, current):
		self._current = current
		#TODO: event notification
		#self.SendNotify(current, wxEVT_COMMAND_LIST_ITEM_FOCUSED)

	def ResetCurrent(self):
		""" Resets the current item to ``None``. """
		self.ChangeCurrent(-1)

	def HasCurrent(self):
		"""
		Returns ``True`` if the current item has been set, either programmatically
		or by user intervention.
		"""
		return self._current != -1

	def IsSingleSel(self):
		return False

	def ClearBackground(self, dc):
		dc.SetBackground(wx.WHITE_BRUSH)
		dc.Clear()

	def Draw(self, itemsToUpdate=None):
		
		dc = wx.BufferedDC(None, self._buffer)
		gcdc = wx.GCDC(dc)
		
		if itemsToUpdate==None:
			itemsToUpdate = xrange(0, self.GetItemCount())
		
		if not (isinstance(itemsToUpdate, xrange) or isinstance(itemsToUpdate, list)):
			itemsToUpdate = [itemsToUpdate]
		
		boxwidth, boxheight = self.GetBoxSize()
		rowheight = self.GetRowHeight()
		colwidth = self.GetColWidth()
		spacing_width, spacing_height = self.GetBoxSpacing()
		
		for item in itemsToUpdate:
			x = self.GetItemX(item) + spacing_width / 2
			y = self.GetItemY(item) + spacing_height / 2
			
			# TODO: Move this within the item's draw code?
			dc.SetClippingRect( (x, y, boxwidth, boxheight) )
			self.ClearBackground(dc)
			dc.DestroyClippingRegion()
			
			if item < self.GetItemCount():
				itemObj = self.OnGetItem(item)
				
				if isinstance(itemObj, tuple) or isinstance(itemObj, list):
					itemObj = IconListItem(*itemObj)
				
				if not isinstance(itemObj, IconListItem):
					raise AssertionError, 'Item passed from OnGetItem is not a typle or IconListItem'
				
				itemishighlighted = self._selStore.IsSelected(item)
				
				itemObj.Draw(gcdc, (x, y, boxwidth, boxheight), itemishighlighted)

	def OnPaint(self, event):
		temp_buffer = wx.EmptyBitmap(*self.GetClientSize())
		dc = wx.BufferedPaintDC(self, temp_buffer, wx.BUFFER_CLIENT_AREA)
		dc.Clear()
		self.PrepareDC(dc)
		dc.DrawBitmap(self._buffer, 0, 0)

		try:
			if self._action_position != (-1, -1):
				ax, ay = self.CalcScrolledPosition(self._action_position)
				mx, my = self.CalcScrolledPosition(self._mouse_position)
				width = mx - ax
				height = my - ay

				if width < 0:
					ax += width
					width = -width

				if height < 0:
					ay += height
					height = -height

				gcdc = wx.GCDC(dc)
				highlight_colour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
				gcdc.SetPen(wx.Pen(highlight_colour))
				highlight_colour.Set(*highlight_colour.Get(), alpha=64)
				gcdc.SetBrush(wx.Brush(highlight_colour))
				gcdc.DrawRectangle(ax, ay, width, height)
		except Exception, e:
			print e
			
	def OnSize(self, event):
		event.Skip()

		if self.Layout():
			self.dirty = True
			# force an idle event
			idle_event = wx.IdleEvent()
			idle_event.SetEventType(wx.EVT_IDLE.typeId)
			wx.CallAfter(wx.PostEvent, self, idle_event)

	def OnScroll(self, event):
		event.Skip()
		self.Refresh(False)

	def OnMouse(self, event):
		if event.LeftDown():
			self.SetFocusIgnoringChildren()
		
		event.SetEventObject(self.GetParent())
		if self.GetParent().GetEventHandler().ProcessEvent(event) :
			return
		
		if event.GetEventType() == wx.wxEVT_MOUSEWHEEL:
			# let the base handle mouse wheel events.
			self.Refresh(False)
			event.Skip()
			return
		
		if not self.HasCurrent() or self.IsEmpty():
			if event.RightDown():
				#self.SendNotify(-1, wxEVT_COMMAND_LIST_ITEM_RIGHT_CLICK, event.GetPosition())

##				evtCtx = wx.ContextMenuEvent(wx.EVT_CONTEXT_MENU, self.GetParent().GetId(),
##											 self.ClientToScreen(event.GetPosition()))
##				evtCtx.SetEventObject(self.GetParent())
##				self.GetParent().GetEventHandler().ProcessEvent(evtCtx)
				event.Skip()
				return
		
		if not (event.Dragging() or event.ButtonDown() or event.LeftUp() or \
				event.ButtonDClick() or event.Moving() or event.RightUp()):
			return
		
		x = event.GetX()
		y = event.GetY()
		#x, y = self.CalcUnscrolledPosition(x, y)

		# where did we hit it (if we did)?
		hitResult = 0
		newItem = None
		#count = self.GetItemCount()

		newItem, hitResult = self.HitTest(x, y)
		
		# simple click-drag selection: doesn't update until done
		self._mouse_position = self.CalcUnscrolledPosition((x, y))
		if event.LeftDown():
			self._action_position = self._mouse_position
			self.CaptureMouse()
			self.Refresh(False)
			
		elif event.LeftUp():
			if self.HasCapture():
				self.ReleaseMouse()

				boxwidth, boxheight = self.GetBoxSize()

				# TODO: This code is shared with HitTest, so fix that
				startx, starty = self._action_position
				startcol = startx / (boxwidth + self._spacing[0])
				startrow = starty / (boxheight + self._spacing[1])
				
				endx, endy = self._mouse_position
				endcol = endx / (boxwidth + self._spacing[0])
				endrow = endy / (boxheight + self._spacing[1])
					
				rowFrom, rowTo = startrow, endrow
				if rowTo < rowFrom:
					rowTo = rowFrom
					rowFrom = endrow

				if rowFrom < 0:
					rowFrom = 0
				
				colFrom, colTo = startcol, endcol
				if colTo < colFrom:
					colTo = colFrom
					colFrom = endcol
					
				if colFrom < 0:
					colFrom = 0
				
				#enditem = endrow * self.GetCols() + endcol
				#self.ChangeCurrent(enditem)
				
				rowTo = rowTo + 1
				
				rowTo = min(rowTo, self.GetRows())
				colTo = min(colTo, self.GetCols()-1)

				for row in xrange(rowFrom, rowTo):
					row_delta = row * self.GetCols()
					itemFrom = row_delta + colFrom
					itemTo = min(row_delta+colTo, self.GetItemCount()-1)
					self.HighlightItems(itemFrom, itemTo)

				self._action_position = (-1, -1)
				
				self.Refresh(False)
		
		elif event.Dragging():
			self.Refresh(False)
		
		
		if not hitResult:
			# outside of any item
			if event.RightDown():
				#self.SendNotify(-1, wxEVT_COMMAND_LIST_ITEM_RIGHT_CLICK, event.GetPosition())
##				evtCtx = wx.ContextMenuEvent(wx.EVT_CONTEXT_MENU, self.GetParent().GetId(),
##											 self.ClientToScreen(event.GetPosition()))
##				evtCtx.SetEventObject(self.GetParent())
##				self.GetParent().GetEventHandler().ProcessEvent(evtCtx)
				event.Skip()
				self.HighlightAll(False)
			# TODO: Refactor code so that command modifiers aren't done here
			elif event.LeftDown() and not (event.CmdDown() or event.ShiftDown()):
				self.HighlightAll(False)
			return
			
		current = newItem
		
		if event.RightDown():

			#if self.SendNotify(current, wxEVT_COMMAND_LIST_ITEM_RIGHT_CLICK, event.GetPosition()):
			if True:
				# If the item is already selected, do not update the selection.
				# Multi-selections should not be cleared if a selected item is clicked.

				if not self.IsHighlighted(current):
					self.HighlightAll(False)
					self.ChangeCurrent(current)
					self.ReverseHighlight(self._current)

				# Allow generation of context menu event
				# FIXME: Win32 should be getting a contextmenu event, but isn't!!
				event.Skip()

		elif event.MiddleDown():
			event.Skip()
		
		elif event.LeftDown():
			oldCurrent = self._current
			oldWasSelected = self.IsHighlighted(oldCurrent)

			cmdModifierDown = event.CmdDown()
			if self.IsSingleSel() or not (cmdModifierDown or event.ShiftDown()):
				if self.IsSingleSel() or not self.IsHighlighted(current):
					# not currently selected, so unselect all
					# and select self
					self.HighlightAll(False)
					self.ChangeCurrent(current)
					self.ReverseHighlight(self._current)
					
				else: # multi sel & current is highlighted & no mod keys
					self.ChangeCurrent(current) # change focus
					# other items, if selected, remain selected

			else: # multi sel & either ctrl or shift is down
				if cmdModifierDown:
					self.ChangeCurrent(current)
					self.ReverseHighlight(self._current)

				elif event.ShiftDown():
					self.ChangeCurrent(current)
					itemFrom, itemTo = oldCurrent, current

					if itemTo < itemFrom:
						itemTo = itemFrom
						itemFrom = self._current
					
					if itemFrom == -1:
						itemFrom = 0

					self.HighlightItems(itemFrom, itemTo)

				else: # !ctrl, !shift

					# test in the enclosing if should make it impossible
					raise Exception("how did we get here?")
					
			if self._current != oldCurrent:
				if oldCurrent != -1:
					self.RefreshItem(oldCurrent)
		else:
			itemIndex, hitResult = self.HitTest(x, y)

			if itemIndex != -1:
				self.timer = wx.Timer(self)
				self.timer._dmide_pos = (x, y)
				self.timer._dmide_index = itemIndex
				self.timer.Start(500)

		event.Skip()	

		
	def GetRows(self):
		return self._rows

	def GetCols(self):
		return self._cols

	def GetRowHeight(self):
		return self._box_size[1] + self._spacing[1]

	def GetColWidth(self):
		return self._box_size[0] + self._spacing[0]

	def GetBoxSize(self):
		return self._box_size

	def GetBoxSpacing(self):
		return self._spacing

	def GetItemRow(self, item):
		row = item / self.GetCols()
		return row
		
	def GetItemCol(self, item):
		col = item % self.GetCols()
		return col

	def GetItemX(self, item):
		col = self.GetItemCol(item)
		return col * self.GetColWidth()
		
	def GetItemY(self, item):
		row = self.GetItemRow(item)
		return row * self.GetRowHeight()

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
		self.Layout()
		self.Draw()
		self.Refresh(False) # REFRESH EVERYTHING
		#self.Refresh(True) # is refreshing bg necessary?

	def RecalcSpacing(self):
		oldboxsize = self._box_size
		self._box_size = (self._icon_size[0] + self._label_spacing[0], self._icon_size[1] + self._label_spacing[1])

		if self._box_size != oldboxsize:
			self.Layout()
			self.Draw()
			self.Refresh(False)

	def IsEmpty(self):
		return self.GetItemCount()==0

	def GetItemCount(self):
		return self._items

	def SetItemCount(self, items):
		if items >= 0:
			
			# reducing item count, item_diff is +ve
			item_diff = self._items - items
			
			self._items = items
##			self.Layout()
			self._selStore.SetItemCount(items)
##			self.Draw()
##			self.Refresh(False)
			if self.Layout():
				self.dirty = True
			else:
				if item_diff > 0: # reducing item count
					self.Draw(xrange(items, items+item_diff))
					# fixme: inefficient
					#self.dirty = True
##				elif item_diff < 0: # increasing item count
##					self.Draw(xrange(items+item_diff-1, items-1))

	def OnIdle(self, event):
		if self.dirty:
			self.dirty = False
			self.Draw()
			self.Refresh(False)

		event.Skip()

	def OnTimer(self, event):
		timer = event.GetEventObject()
		timer.Stop()

		pos = self.ScreenToClient(wx.GetMousePosition())

		itemIndex, hitResult = self.HitTest(*pos)
		if itemIndex != -1 and itemIndex == timer._dmide_index:
			self.ToolTip(itemIndex, pos)

	def ToolTip(self, index, pos):
		pass


class IconListItem:
	def __init__(self, label = '', image = None):
		self._label = label
		self._image = image

	def Draw(self, dc, rect, highlight=False):
		
		dc.SetClippingRect(rect)
		#dc.SetBrush(wx.RED_BRUSH)
##		dc.SetBackground(wx.WHITE_BRUSH)
##		dc.Clear()
		
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
			dc.SetPen(wx.Pen(highlight_colour))
			highlight_colour.Set(*highlight_colour.Get(), alpha=64)
			dc.SetBrush(wx.Brush(highlight_colour))
			dc.DrawRoundedRectangle(*rect, radius=4)
			dc.SetBrush(old_brush)
			
				
	
		dc.DrawLabel(new_label, rect, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM)
		
		dc.DestroyClippingRegion()





"""
Subclass the ultimatelistctrl selection store to fix a bug
 in SelectRange()
Also to provide differentiation between 'no items changed' and 'many items changed'
"""

class SelectionStore(ulcSelectionStore):
	def __init__(self, *args, **kwargs):
		ulcSelectionStore.__init__(self, *args, **kwargs)
	
	def SelectRange(self, itemFrom, itemTo, select=True):
		"""
		Selects a range of items.

		:param `itemFrom`: the first index of the selection range;
		:param `itemTo`: the last index of the selection range;
		:param `select`: ``True`` to select the items, ``False`` otherwise.
		
		:return: The `itemsChanged` array, unless MANY_ITEMS changed, in
		 which case, return `None`
		"""
	
		# 100 is hardcoded but it shouldn't matter much: the important thing is
		# that we don't refresh everything when really few (e.g. 1 or 2) items
		# change state
		MANY_ITEMS = 100

		# many items (> half) changed state
		itemsChanged = []        

		# are we going to have more [un]selected items than the other ones?
		if itemTo - itemFrom > self._count/2:

			if select != self._defaultState:
			
				# the default state now becomes the same as 'select'
				self._defaultState = select

				# so all the old selections (which had state select) shouldn't be
				# selected any more, but all the other ones should
				selOld = self._itemsSel[:]
				self._itemsSel = []

				# TODO: it should be possible to optimize the searches a bit
				#       knowing the possible range

				for item in xrange(itemFrom):
					if item not in selOld:
						self._itemsSel.append(item)
				
				for item in xrange(itemTo + 1, self._count):
					if item not in selOld:
						self._itemsSel.append(item)
				
				itemsChanged = None

			else: # select == self._defaultState
			
				# get the inclusive range of items between itemFrom and itemTo
				count = len(self._itemsSel)
				#start = bisect.bisect_right(self._itemsSel, itemFrom)
				start = bisect.bisect_left(self._itemsSel, itemFrom)
				end = bisect.bisect_right(self._itemsSel, itemTo)
				
				if start == count or self._itemsSel[start] < itemFrom:
					start += 1
				
				if end == count or self._itemsSel[end] > itemTo:
					end -= 1
					
				if start <= end:
				
					keepCounting = True
				
					# delete all of them (from end to avoid changing indices)
					for i in xrange(end, start-1, -1):
						if keepCounting:
							if len(itemsChanged) > MANY_ITEMS:
								# stop counting (see comment below)
								itemsChanged = None
								keepCounting = False
							else:                            
								itemsChanged.append(self._itemsSel[i])
							
						self._itemsSel.pop(i)
				else:
					self._itemsSel = []

		else: # "few" items change state
		
			keepCounting = True

			# just add the items to the selection
			for item in xrange(itemFrom, itemTo+1):
				#if self.SelectItem(item, select) and itemsChanged:
				if self.SelectItem(item, select) and keepCounting:
					itemsChanged.append(item)
					if len(itemsChanged) > MANY_ITEMS:
						# stop counting them, we'll just eat gobs of memory
						# for nothing at all - faster to refresh everything in
						# this case
						itemsChanged = None
						keepCounting = False

		# we set it to None if there are many items changing state
		return itemsChanged

	def OnItemDelete(self, item):
		"""
		Must be called when an item is deleted.

		:param `item`: the item that is being deleted.
		"""

		count = len(self._itemsSel)
		i = bisect.bisect_left(self._itemsSel, item)

		if i < count and self._itemsSel[i] == item:
			# this item itself was in m_itemsSel, remove it from there
			self._itemsSel.pop(i)
			count -= 1
		
		# and adjust the index of all which follow it
		while i < count-1:

			i += 1        
			self._itemsSel[i] -= 1