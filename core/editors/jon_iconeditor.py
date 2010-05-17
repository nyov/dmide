"""
DMIDE Icon Editor
"""

import wx
from wx.lib import buttons

# Import modules that can read DMI files
import core
from core import *

from draw import Draw

"""
Misc stuff
"""
round2 = lambda n,p=2: (n+p/2)/p*p



"""
Pallete Objects
"""

"""
TODO: make Palettes wx.Panels (probably)
	they will contain a title button/dropdown/section with commands
	as well as the actual palette grid
	
	palette grid will be implemented inside a scrolledwindow, similar to how 
	entire palette is now
"""

class Palette(wx.ScrolledWindow):
	def __init__(self, parent, ID, dmipanel):
		wx.ScrolledWindow.__init__(self, parent, ID, style=wx.SIMPLE_BORDER)
		self.colours = []
		self.numCols = 8
		self.colourButtons = {}
		self.dmipanel = dmipanel
		self.colour = (-1,-1,-1,-1)
		
	def BuildColours(self):
		pass
		
	def OnSetColour(self, event):
		b = event.GetEventObject()
		colour = b.name
		
		if colour != self.colour:
			if self.colour != (-1,-1,-1,-1):
				self.colourButtons[self.colour].SetToggle(False)
		#print 'colour: ', colour
		self.dmipanel.SetPrimaryColour(colour)
		self.colour = colour


# DMIPalette is a particular class of Palette that contains only colours used in the active icon
class DMIPalette(Palette):
	def __init__(self, parent, ID, dmipanel):
		Palette.__init__(self, parent, ID, dmipanel)
		
		self.BMP_SIZE = 16
		self.BMP_SPACING = 1
		

	def Update(self, img):
		""" Update() is called by the DMIPanel to inform
		listening objects that something they're interested in has changed."""
		if img:
			self.colours = img.getcolors(img.size[0]*img.size[1])
		else:
			self.colours = []
			
		self.BuildColours()
			
		#print len(self.colours)
		#print self.colours
		
	def BuildColours(self):
		
		btnSize = wx.Size(self.BMP_SIZE+self.BMP_SPACING*2,self.BMP_SIZE+self.BMP_SPACING*2)
		self.colourButtons = {}
		
		colourGrid = wx.GridSizer(cols=8, hgap=2, vgap=2)
		#i = 1
		for coltup in self.colours:
			colour = coltup[1]
			r, g, b, a = colour
			#print 'a:', a
			bmp = wx.EmptyBitmapRGBA(self.BMP_SIZE, self.BMP_SIZE, r, g, b, 255)

##			bmp = wx.EmptyBitmap(64, 64)
##			
##			dc = wx.MemoryDC()
##			dc.SelectObject(bmp)
##			dc.SetBackground(wx.Brush((r, g, b)))
##			dc.Clear()
##			dc.SelectObject(wx.NullBitmap)
			
			b = buttons.GenBitmapToggleButton(self, id=wx.ID_ANY,bitmap=bmp, size=btnSize)
			#b.name = i
			b.name = colour
			#i = i + 1
			b.SetBezelWidth(1)
			b.SetUseFocusIndicator(False)
			self.Bind(wx.EVT_BUTTON, self.OnSetColour, b)
			
			colourGrid.Add(b, 0)
			self.colourButtons[b.name]=b
		
		box = wx.BoxSizer(wx.VERTICAL)
		box.Add(colourGrid, 0, wx.ALL, 4)
		self.SetSizer(box)
		self.SetAutoLayout(True)
		box.Fit(self)



"""
Compass Rose
"""

class CompassRose(wx.Panel):
	"""
	CompassRose displays which of the 16 possible icon directions are available, and which is selected.
	"""
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)



"""
Icon Editing Tools
"""

class DMITool(object):
	def __init__(self):
		# init vars here
		#self.pos = wx.Point(0,0)
		self.selected = False
		self.dmipanel = None
	
	def SelectTool(self, dmipanel):
		self.selected = True
		self.dmipanel = dmipanel
		
	def DeselectTool(self):
		# Do deselection cleanup
		if self.active == True:
			self.StopTool()
		self.selected = False
		self.dmipanel = None
		
	def StartTool(self, colour, pos, shift):
		if self.selected == True:
			self.active = True
			
			#working with self.dmipanel.draw_image and self.dmipanel.draw_fx

	def MoveTool(self, colour, pos, shift):
		if self.active == True:
			pass
		
	def StopTool(self):
		self.active = False

class DMITool_Pen(DMITool):
	def __init__(self):
		DMITool.__init__(self)
		#self.colour = (0,0,0,255)

	def StartTool(self, colour, pos, shift):
		if self.selected == True:
			self.active = True

			#self.colour = colour
			#self.pos = pos
			
			draw = self.dmipanel.draw_image
			
			#draw.point(self.pos, fill=colour)
			draw.point(pos, colour)
			self.dmipanel.DirtyImage()
	
	def MoveTool(self, colour, pos, shift):
		if self.active:
			#self.pos = pos
			draw = self.dmipanel.draw_image
			
			#draw.point(self.pos, fill=colour)
			draw.point(pos, colour)
			self.dmipanel.DirtyImage()
		
		else: # Could do hover-y stuff with fx_image here - need mouse focus first
			pass
##			self.dmipanel.ClearFx()
##			
##			draw = self.dmipanel.draw_fx
##			colour[3] = colour[3] / 2
##			
##			
##			draw.point(pos, colour)
##			self.dmipanel.DirtyFx()
			

class DMITool_Arrow(DMITool):
	""" Right now arrow does nothing. Is just a tool here to show tool selection."""
	def __init__(self):
		DMITool.__init__(self)
		self.colour = (0,0,0,255)

class DMITool_Ellipse(DMITool):
	""" Basic ellipse tool. Shows how the current fx_image is not a great idea."""
	def __init__(self):
		DMITool.__init__(self)
		# Is defining them here duplicating too much stuff?
		# Should they be -1, -1??
		self.startPos = wx.Point(0,0)
		self.lastPos = wx.Point(0,0)
		
	def SelectTool(self, dmipanel):
		self.selected = True
		self.dmipanel = dmipanel		
		self.startPos = wx.Point(0,0)
		self.lastPos = wx.Point(0,0)
		
	def StartTool(self, colour, pos, shift):
		if self.selected == True:
			self.active = True
			
			self.startPos = pos
			self.colour = colour
			
			self.dmipanel.ClearFx()
			draw = self.dmipanel.draw_fx
			draw.point(self.startPos, self.colour)
			
			self.dmipanel.DirtyFx()
			
	def MoveTool(self, colour, pos, shift):
		if self.active == True:
			
			self.lastPos = pos
			self.colour = colour
			
			self.dmipanel.ClearFx()
			draw = self.dmipanel.draw_fx
			
			draw.ellipse(self.startPos, self.lastPos, False, self.colour)
			
			self.dmipanel.DirtyFx()
		
	def StopTool(self):
		if self.active:
			
			self.dmipanel.ClearFx()
			
			draw = self.dmipanel.draw_image
			
			draw.ellipse(self.startPos, self.lastPos, False, self.colour)
			
			self.dmipanel.DirtyImage()
			
		self.active = False
"""
Left-side tools control panel
Also may contain other things
"""

class DMIEditorTools(wx.Panel):
	def __init__(self, parent, ID, dmipanel):
		wx.Panel.__init__(self, parent, ID, style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.SIMPLE_BORDER)
		
		numCols = 1
		spacing = 4
		
		self.dmipanel = dmipanel
		
		# get tool icons from artprovider!!
		
		# first, create a grid of tools
		
		tool_classes = DMITool.__subclasses__()
		
		self.tools = {}
		
		for toolclass in tool_classes:
			self.tools[toolclass.__name__] = toolclass()
		
		# get actual list of real tools elsewhere later
		
##		tools = {'pen':'pen', 'eraser':'eraser', 'eyedropper':'eyedropper',
##			'zoom':'zoom'}
		
		toolGrid = wx.GridSizer(cols=numCols, hgap=2, vgap=2) 
		
		# Make a grid of tools.
		for tool in self.tools:
			#bmp = GetBitmapFromArtProviderSomehow()
			#mask = GetAMaskIfItIsNecessary()
			
##			bmp = art.getFromExt('dmi', (32,32))	
##			
##			bmp.SetMask(mask)
##			b = wx.BitmapButton(self, -1, bmp, (20, 20),
##										(bmp.GetWidth()+10, bmp.GetHeight()+10))
##			b.SetToolTipString("This is the %s tool." % tool)
##			self.Bind(wx.EVT_BUTTON, self.OnSetTool, b)

			b = wx.Button(self, -1, tool, (20, 20))
			b.name = tool
			self.Bind(wx.EVT_BUTTON, self.OnSetTool, b)
			
			toolGrid.Add(b, 0)
		
		# Make a compass rose
		# indicates direction of the icon_state currently being worked on
		# also indicates available direction choices
		# possibly has the ability to change the # of directions in the state
		#  this last might not be a good idea from a ui perspective
		cr = CompassRose(self)
		
		# Make an animation frame indicator
		# Displays current frame in a [1]/10 style.
		# Later, make editable
		# Possible scrollbar & play button?
		# Maybe this shouldn't be in this toolbar
		#aniframe = SomethingSublclassingSpinCtrl?
		
		# Make a 1x size preview
		# Displays current icon at 1x scale
		# does not resize so as to fit full icon
		# if the icon doesn't fit, either size the full thing down, or just display what does
		# need to look at this part later
		# Register it as a listener so it will be notified when the icon changes
		#sp = DMIPreview(self)
		#dmipanel.AddListener(sp)
		#dmipanel.Notify()
		
		box = wx.BoxSizer(wx.VERTICAL)
		box.Add(toolGrid, 0, wx.ALL, spacing)
		box.Add(cr, 0, wx.ALL | wx.EXPAND, spacing)
		#box.Add(sp, 0, wx.ALL | wx.EXPAND, spacing)
		
		self.SetSizer(box)
		self.SetAutoLayout(True)
		
		box.Fit(self)
			
	def OnSetTool(self, event):
		"""
		OnSetTool(event)
		Called when a tool button is clicked.
		Calls the associated dmipanel to select the tool for use.
		"""
		b = event.GetEventObject()
		tool = self.tools[b.name]
		self.dmipanel.SetTool(tool)



"""
DMI Panel
Is the surface that displays the current icon state for editing.
Other objects can register as a listener to be informed when something
about the icon state is changed. 
	For example, when drawn upon, notify a half-size preview to update.
"""

# todo: name these better and place within dmipanel
DMIPANEL_COLOUR = 1
DMIPANEL_IMAGE = 2
DMIPANEL_ALL = DMIPANEL_COLOUR | DMIPANEL_IMAGE

class DMIPanel(wx.ScrolledWindow):
	
	DEFAULT_IMAGE_SIZE = (32,32)
	
	def __init__(self, parent, ID):
		wx.ScrolledWindow.__init__(self, parent, ID, style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.SIMPLE_BORDER)
		
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



"""
Icon Editor
Creates and handles the gui interface for icon editing.
Also handles calls to save/load, undo/redo, etc?
"""

class IconEditor(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, 
			style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN | wx.SIMPLE_BORDER)

		self.horiz_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.dmipanel = DMIPanel(self, wx.ID_ANY)
		
		self.tools_panel = DMIEditorTools(self, -1, self.dmipanel)
		self.horiz_sizer.Add(self.tools_panel, 0, wx.EXPAND)
		
		self.palette_sizer = wx.BoxSizer(wx.VERTICAL)
		
		palette = Palette(self, wx.ID_ANY, self.dmipanel)
		dmipalette = DMIPalette(self, wx.ID_ANY, self.dmipanel)
		
		#self.dmipanel.AddListener(palette)
		self.dmipanel.AddListener(dmipalette)
		
		
		self.palette_sizer.Add(dmipalette, 0, wx.EXPAND)
		self.palette_sizer.Add(palette, 0, wx.EXPAND)

		self.horiz_sizer.Add(self.dmipanel, 1, wx.EXPAND)
		self.horiz_sizer.Add(self.palette_sizer, 0, wx.EXPAND)
		
		self.SetSizer(self.horiz_sizer)
		#self.horiz_sizer.Fit(self)
		
	def Open(self, img):
		self.dmipanel.SetImageData(img)
		

