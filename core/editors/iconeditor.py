"""
DMIDE Icon Editor
"""

import core
from core import *

import core.iconlistctrl as wxIconList
from draw import Draw

round2 = lambda n,p=2: (n+p/2)/p*p

dir_text = ['South', 'North', 'East', 'West', 'SouthEast', 'SouthWest', 'NorthEast', 'NorthWest']


def wxify(icon):
	icon = icon.copy()
	for dir in xrange(len(icon.icons)):
		icon.icons[dir] = [ImgToWx(x) for x in icon.icons[dir]]
	return icon


class IconEditor(wx.Panel):
	def __init__(self, *args, **kwargs):
		wx.Panel.__init__(self, *args, **kwargs)

		self.icon = None

		self.viewer = FrameViewer(self)
		self.editor = FrameEditor(self)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.editor, 10, wx.EXPAND)
		sizer.Add(self.viewer, 0, wx.ALIGN_BOTTOM | wx.EXPAND)
		self.SetSizer(sizer)

	def Open(self, icon):
		old = icon.icons[0][0]
		self.icon = wxify(icon)

		self.viewer.Open(self.icon)
		self.editor.Open(old)
		w, h = self.GetSize()
		self.SetSize((w, h+1))
		self.SetSize((w, h))


class FrameEditor(wx.ScrolledWindow):

	DEFAULT_IMAGE_SIZE = (32,32)

	def __init__(self, parent):
		wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY, style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.SIMPLE_BORDER)

		self.listeners = []

		self.primary_colour = None # or black or something
		self.secondary_colour = None

		self.SetPrimaryColour((0, 0, 0, 255))

		self.curTool = None # default to pen, once figure out how to do tools right

		self.imageChanged = False # for 'image changed. save?'

		# Dirty image buffer & screen buffer
		self.bufferdirty = False
		self.viewdirty = False

		self.last_box = (0,0,0,0)

		self.zoom_level = 1
		self.zoom_buffer = wx.EmptyBitmapRGBA(self.DEFAULT_IMAGE_SIZE[0], self.DEFAULT_IMAGE_SIZE[1],
			255, 255, 255, 0)

		# Does the DMIPanel need this variable?
		self.pos = wx.Point(0,0)

		self.SetScrollRate(1, 1)

		#self.image = None
		self.image = Image.new('RGBA', self.DEFAULT_IMAGE_SIZE)

		self.initBuffers()
		self.initBinds()

	def Open(self, icon):
		self.image = icon


	def initBuffers(self):
		""" Init pil and zoom buffers. self.image needs to be available.
		Also call init for drawing objects. """

		imageSize = self.GetImageSize()

		self.pil_background = Image.new('RGBA', imageSize, (128, 128, 128, 255))
		self.pil_buffer = Image.new('RGBA', imageSize)
		self.fx_base = Image.new('RGBA', imageSize, (0, 0, 0, 0))
		self.fx_image = Image.new('RGBA', imageSize, (0, 0, 0, 0))
		#self.pil_buffer.paste(self.fx_image)
		self.bufferdirty = True
		#self.viewdirty = True
		self.initDraw()

	def initDraw(self):
		self.draw_image = Draw(self.image)
		self.draw_fx = Draw(self.fx_image)

	def initBinds(self):
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		self.Bind(wx.EVT_MOUSEWHEEL, self.OnMousewheel)
##		self.Bind(wx.EVT_SIZE, self.OnSize)
##		self.Bind(wx.EVT_IDLE, self.OnIdle)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SCROLL, self.OnScroll)
		#self.Bind(wx.EVT_WINDOW_DESTROY, self.Cleanup)

	def ClearFx(self):
		# Should a cache be used here? Any speedup?
		#self.fx_image = Image.new('RGBA', self.GetImageSize(), (0, 0, 0, 0))
		self.fx_image.paste(self.fx_base)
		self.bufferdirty = True # probably?

	def OnScroll(self, event):
		event.Skip()
		wx.CallAfter(self.Refresh, False)

	def SetPrimaryColour(self, colour):
		self.primary_colour = colour
		#self.Notify(DMIPANEL_COLOUR)

	def SetSecondaryColour(self, colour):
		self.secondary_colour = colour
		#self.Notify(DMIPANEL_COLOUR) # maybe secondary colour instead?

	def SetTool(self, tool):
		# pen, etc
		if tool == self.curTool:
			return
		if self.curTool:
			self.curTool.DeselectTool()

		self.curTool = tool
		self.curTool.SelectTool(self)

	def SetImageData(self, image):
		# copy() to get around a possible bug in PIL
		self.image = image.copy()

		# notify here?
		self.imageChanged = False
		# should dirty be set here or by notifying?
		#   currently, dirty is set when buffers reInited anyways

		# should this part be done here??
		self.SetVirtualSize(self.GetImageSize())

		# New image, so make new buffers of the correct size
		self.initBuffers()

		self.Refresh(False)
		self.Notify()

	def GetImageData(self):
		return self.image

	def GetImageSize(self):
		if self.image:
			return self.image.size
		return self.DEFAULT_IMAGE_SIZE

	def OnLeftDown(self, event):
		"""Called when the left mouse button is pressed."""
		#self.pos = event.GetPosition()
		pos = self.ImageCoords(event.GetPosition()+self.GetScroll())
		self.CaptureMouse()

		shift = False
		if self.image and self.curTool:
			self.curTool.StartTool(self.primary_colour, pos, shift)
			if self.bufferdirty:
				wx.CallAfter(self.Refresh, False)

	def OnLeftUp(self, event):
		"""Called when the left mouse button is released."""
		if self.HasCapture():
			# Started clicking while on this control, so handle letting go
			self.ReleaseMouse()

			if self.image and self.curTool:
				self.curTool.StopTool()
				if self.bufferdirty:
					wx.CallAfter(self.Refresh, False)

	def OnRightDown(self, event):
		"""Called when the right mouse button is pressed."""
		# This might be functionaly equivalent to OnLeftDown, except
		#	providing the secondary colour to the tool used

		# Alternately, this might be kept as being purely the eyedropper tool
		# Q: How to handle self.pos? Left vs Right interference?

		self.pos = event.GetPosition()
		self.CaptureMouse

	def OnRightUp(self, event):
		"""Called when the right mouse button is released."""
		# Might be semi-equivalent to OnLeftUp
		# Or might be an instruction to stop sampling with the eyedroppper.
		if self.HasCapture():
			self.ReleaseMouse()

	def OnMotion(self, event):
		"""
		Called when the mouse is in motion. As the mouse moves, various tools,
		like pen, line, and others, either draw on the image, or prepare to draw,
		showing the result of letting go of the mouse button at this point.
		"""

		# Get focus so that mousewheel events fire on win32
		self.SetFocusIgnoringChildren()

		if event.Dragging() :
			if event.LeftIsDown():
				# Do things with dragging. Deal with tools.
				pos = self.ImageCoords(event.GetPosition()+self.GetScroll())

				self.pos = pos
				shift = False # get this right later

				if self.image and self.curTool:
					self.curTool.MoveTool(self.primary_colour, self.pos, shift)
					if self.bufferdirty:
						wx.CallAfter(self.Refresh, False)


	def OnMousewheel(self, event):
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

			#self.viewdirty = True # Might not need this since the box should change
			self.SetScrollRate(self.zoom_level, self.zoom_level)
			self.SetVirtualSize((self.image.size[0] * self.zoom_level, self.image.size[1] * self.zoom_level))
			wx.CallAfter(self.Refresh, False)
			#wx.CallAfter(self.update)

	def DirtyImage(self):
		self.imageChanged = True
		self.bufferdirty = True

	def DirtyFx(self):
		self.bufferdirty = True

##	def OnSize(self, event):
##		"""
##		Called when window is resized. Set a flag so the idle handler
##		will resize the buffer.
##		"""
##		self.reInitBuffers = True
##
##	def OnIdle(self, event):
##		"""
##		If size was changed, then resize the buffer bitmaps?.  Done in idle
##		time so that there is only one refresh after resizing is done (faster?).
##		"""
##		if self.reInitBuffers:
##			self.InitBuffers()
##			self.Refresh(False)


##	def OnSize(self, event):
##		self.ClientWidth, self.ClientHeight = self.GetClientSizeTuple()

	def OnPaint(self, event):
		""" Called when the window is exposed. """
		# Prepare DC for drawing
		# TODO: Use BufferedPaintDC properly instead of like it is now
		dc = wx.BufferedPaintDC(self)
		self.DoPrepareDC(dc)
		dc.Clear()

		# Get box, mapping current view to rect visible of pil image
		scrollx, scrolly = self.GetScroll()
		box = self.GetBox()

		if self.bufferdirty:
			self.UpdateBuffers()

		# Either image has changed, or viewable area has changed
		if self.viewdirty or box != self.last_box:

			# Get cropped image, mapping to visible bit on screen
			cropped = self.pil_buffer.crop(box)

			# Resize image - currently doing with PIL
			# No alpha was faster with DrawBitmap on gtk
			# Change drawbitmap() to blit() later
			#self.zoom_buffer = ImgToWxNoAlpha(cropped.resize((cropped.size[0] * self.zoom_level, cropped.size[1] * self.zoom_level)))
			self.zoom_buffer = ImgToWx(cropped.resize((cropped.size[0] * self.zoom_level, cropped.size[1] * self.zoom_level)))

			self.last_box = box

		# Current dc.Blit() is wrong somehow - crashes on win32

		#blitbox = self.GetBox(False)
		#left, top, width, height = blitbox

		#dcmem = wx.MemoryDC(self.zoom_buffer)

		#dc.Blit(left, top, width, height, dcmem, 0, 0, rop=wx.COPY, useMask=False)

		dc.DrawBitmap(self.zoom_buffer, scrollx, scrolly)

	def OnEraseBackground(self, event):
		# Eliminate some flicker
		pass

	def UpdateBuffers(self):
		""" Update PIL graphics buffer """
		if not self.bufferdirty: return

		self.pil_buffer = self.pil_background.copy()
		self.pil_buffer.paste(self.image, mask=self.image)
		self.pil_buffer.paste(self.fx_image, mask=self.fx_image)
		self.bufferdirty = False
		self.viewdirty = True

	def GetBox(self, zoom=True):
		left, top = self.GetScroll()
		width, height = self.GetClientSizeTuple()
		if zoom:
			z = float(self.zoom_level)
			box = int(round(left / z)), int(round(top / z)), min(self.image.size[0], int(round2((left + width) / z))), min(self.image.size[1], int(round2((top + height) / z)))
			return box
		return (left, top, width, height)

	def GetScroll(self):
		xunits, yunits = self.GetScrollPixelsPerUnit()
		left, top = self.GetScrollPos(wx.HORIZONTAL) * xunits, self.GetScrollPos(wx.VERTICAL) * yunits
		return left, top

	def ImageCoords(self, coords):
		if(self.zoom_level==1): return coords
		return (coords[0] / self.zoom_level, coords[1] / self.zoom_level)

	def AddListener(self, listener):
		self.listeners.append(listener)

	#def Notify(self, notify_type=DMIPANEL_ALL):
	def Notify(self):
		for other in self.listeners:
			other.Update(self.image)



class FrameEditor2(wx.Panel):
	def __init__(self, *args, **kwargs):
		wx.Panel.__init__(self, *args, **kwargs)

		self.icon = None

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)

	def Open(self, icon):
		self.icon = icon
		self.SetSize((icon.icons[0][0].GetWidth(), icon.icons[0][0].GetHeight()))

	def OnPaint(self, event):
		dc = wx.PaintDC(self)
		dc.Clear()

		try:
			dc.DrawBitmap(self.icon.icons[0][0], 0, 0)
		except:
			pass


class FrameViewer(wxIconList.IconListCtrl):
	def __init__(self, *args, **kwargs):
		self.directions = 4
		self.frames = 2

		wxIconList.IconListCtrl.__init__(self, *args, **kwargs)

	def Open(self, icon):
		self.icon = icon
		self._max_cols = icon.dirs
		self.SetItemCount(icon.dirs * icon.frames)

	def OnGetItem(self, index):
		col = index
		row = 0

		if col >= 4:
			col -= 4
			row = 1

		return ('%s %s' % (dir_text[col], row), self.icon.icons[col][row])
