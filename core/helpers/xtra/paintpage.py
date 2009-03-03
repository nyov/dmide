#from id import *
import wx

palette=[(192, 192, 192), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (64, 64, 64), (128, 128, 128), (192, 192, 192), (255, 255, 255), (255, 255, 255), (204, 255, 255), (153, 255, 255), (102, 255, 255), (51, 255, 255), (0, 255, 255), (0, 255, 204), (51, 255, 204), (102, 255, 204), (153, 255, 204), (204, 255, 204), (255, 255, 204), (255, 204, 255), (204, 204, 255), (153, 204, 255), (102, 204, 255), (51, 204, 255), (0, 204, 255), (0, 204, 204), (51, 204, 204), (102, 204, 204), (153, 204, 204), (204, 204, 204), (255, 204, 204), (255, 153, 255), (204, 153, 255), (153, 153, 255), (102, 153, 255), (51, 153, 255), (0, 153, 255), (0, 153, 204), (51, 153, 204), (102, 153, 204), (153, 153, 204), (204, 153, 204), (255, 153, 204), (255, 102, 255), (204, 102, 255), (153, 102, 255), (102, 102, 255), (51, 102, 255), (0, 102, 255), (0, 102, 204), (51, 102, 204), (102, 102, 204), (153, 102, 204), (204, 102, 204), (255, 102, 204), (255, 51, 255), (204, 51, 255), (153, 51, 255), (102, 51, 255), (51, 51, 255), (0, 51, 255), (0, 51, 204), (51, 51, 204), (102, 51, 204), (153, 51, 204), (204, 51, 204), (255, 51, 204), (255, 0, 255), (204, 0, 255), (153, 0, 255), (102, 0, 255), (51, 0, 255), (0, 0, 255), (0, 0, 204), (51, 0, 204), (102, 0, 204), (153, 0, 204), (204, 0, 204), (255, 0, 204), (255, 0, 153), (204, 0, 153), (153, 0, 153), (102, 0, 153), (51, 0, 153), (0, 0, 153), (0, 0, 102), (51, 0, 102), (102, 0, 102), (153, 0, 102), (204, 0, 102), (255, 0, 102), (255, 51, 153), (204, 51, 153), (153, 51, 153), (102, 51, 153), (51, 51, 153), (0, 51, 153), (0, 51, 102), (51, 51, 102), (102, 51, 102), (153, 51, 102), (204, 51, 102), (255, 51, 102), (255, 102, 153), (204, 102, 153), (153, 102, 153), (102, 102, 153), (51, 102, 153), (0, 102, 153), (0, 102, 102), (51, 102, 102), (102, 102, 102), (153, 102, 102), (204, 102, 102), (255, 102, 102), (255, 153, 153), (204, 153, 153), (153, 153, 153), (102, 153, 153), (51, 153, 153), (0, 153, 153), (0, 153, 102), (51, 153, 102), (102, 153, 102), (153, 153, 102), (204, 153, 102), (255, 153, 102), (255, 204, 153), (204, 204, 153), (153, 204, 153), (102, 204, 153), (51, 204, 153), (0, 204, 153), (0, 204, 102), (51, 204, 102), (102, 204, 102), (153, 204, 102), (204, 204, 102), (255, 204, 102), (255, 255, 153), (204, 255, 153), (153, 255, 153), (102, 255, 153), (51, 255, 153), (0, 255, 153), (0, 255, 102), (51, 255, 102), (102, 255, 102), (153, 255, 102), (204, 255, 102), (255, 255, 102), (255, 255, 51), (204, 255, 51), (153, 255, 51), (102, 255, 51), (51, 255, 51), (0, 255, 51), (0, 255, 0), (51, 255, 0), (102, 255, 0), (153, 255, 0), (204, 255, 0), (255, 255, 0), (255, 204, 51), (204, 204, 51), (153, 204, 51), (102, 204, 51), (51, 204, 51), (0, 204, 51), (0, 204, 0), (51, 204, 0), (102, 204, 0), (153, 204, 0), (204, 204, 0), (255, 204, 0), (255, 153, 51), (204, 153, 51), (153, 153, 51), (102, 153, 51), (51, 153, 51), (0, 153, 51), (0, 153, 0), (51, 153, 0), (102, 153, 0), (153, 153, 0), (204, 153, 0), (255, 153, 0), (255, 102, 51), (204, 102, 51), (153, 102, 51), (102, 102, 51), (51, 102, 51), (0, 102, 51), (0, 102, 0), (51, 102, 0), (102, 102, 0), (153, 102, 0), (204, 102, 0), (255, 102, 0), (255, 51, 51), (204, 51, 51), (153, 51, 51), (102, 51, 51), (51, 51, 51), (0, 51, 51), (0, 51, 0), (51, 51, 0), (102, 51, 0), (153, 51, 0), (204, 51, 0), (255, 51, 0), (255, 0, 51), (204, 0, 51), (153, 0, 51), (102, 0, 51), (51, 0, 51), (0, 0, 51), (0, 0, 0), (51, 0, 0), (102, 0, 0), (153, 0, 0), (204, 0, 0), (255, 0, 0), (0, 0, 0), (7, 7, 7), (14, 14, 14), (21, 21, 21), (28, 28, 28), (35, 35, 35), (42, 42, 42), (49, 49, 49), (56, 56, 56), (63, 63, 63), (70, 70, 70), (77, 77, 77), (84, 84, 84), (91, 91, 91), (98, 98, 98), (105, 105, 105), (112, 112, 112), (119, 119, 119), (126, 126, 126), (133, 133, 133), (140, 140, 140), (147, 147, 147), (154, 154, 154), (161, 161, 161), (168, 168, 168), (175, 175, 175), (182, 182, 182), (189, 189, 189), (196, 196, 196), (203, 203, 203), (210, 210, 210), (217, 217, 217), (224, 224, 224), (231, 231, 231), (238, 238, 238), (245, 245, 245)]

pen_styles=["Solid", "Dot", "Long Dash", "Short Dash",
						"Dot Dash", "Back Diag Hatch", "Cross-Diag Hatch",
						"Front Diag Hatch", "Cross Hatch", "Horizontal Hatch",
						"Vertical Hatch"]

pen_styles_id=[wx.SOLID, wx.DOT, wx.LONG_DASH, wx.SHORT_DASH,
							 wx.DOT_DASH, wx.BDIAGONAL_HATCH, wx.CROSSDIAG_HATCH,
							 wx.FDIAGONAL_HATCH, wx.CROSS_HATCH, wx.HORIZONTAL_HATCH,
							 wx.VERTICAL_HATCH]

palette_box_width = 10
palette_width=12 * palette_box_width
palette_height=22 * palette_box_width

wxPENBLACK=None
wxPENWHITE=None
wxPENGRAY=None

ID_TOOL_BRUSH=wx.NewId()
ID_TOOL_LINE=wx.NewId()


class PaintPage(wx.ScrolledWindow):
	def __init__(self, parent):
		wx.ScrolledWindow.__init__(self, parent, -1)
		self.SetScrollRate(20, 20)

		global wxPENBLACK, wxPENWHITE, wxPENGRAY
		wxPENBLACK=wx.Pen('BLACK', 1)
		wxPENWHITE=wx.Pen('WHITE', 1)
		wxPENGRAY=wx.Pen('GRAY', 1)

		self.paint_canvas=PaintCanvas(self)
		self.control_panel=ControlPanel(self)
		self.paint_canvas.control_panel=self.control_panel
		self.control_panel.paint_canvas=self.paint_canvas

		sizer=wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.control_panel, 0, wx.EXPAND)
		sizer.AddSpacer(2)
		sizer2=wx.BoxSizer(wx.VERTICAL)
		sizer2.AddSpacer(2)
		sizer2.Add(self.paint_canvas, 1, wx.ALL | wx.EXPAND)
		sizer.Add(sizer2, 1, wx.ALL | wx.EXPAND)
		self.SetSizer(sizer)


class PaintCanvas(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)

		self.buffer=wx.EmptyBitmap(256, 256)

		self.left_down=False
		self.right_down=False
		self.last_x=0
		self.last_y=0
		self.selected_x=-1
		self.selected_y=-1

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
		self.Bind(wx.EVT_MOTION, self.OnMotion)

	def UpdateCoords(self, event):
		self.last_x=event.GetX()
		self.last_y=event.GetY()

	def Draw(self, event, tool=-1):
		if tool==-1: 
			tool=self.control_panel.selected_tool

		try:
			x, y=event.GetX(), event.GetY()
		except AttributeError, e:
			x, y=self.last_x, self.last_y

		dc=wx.BufferedDC(wx.ClientDC(self), self.buffer)
		dc.DrawBitmap(self.buffer, 0, 0)

		colour=wx.Colour(*self.control_panel.GetColour())
		colour2=wx.Colour(*self.control_panel.GetColour(1))

		if self.right_down and not self.left_down:
			colour, colour2=colour2, colour

		dc.SetPen(wx.Pen(colour, self.control_panel.line_width))
		dc.SetBrush(wx.Brush(colour))

		if tool==ID_TOOL_BRUSH:
			dc.DrawLine(self.last_x, self.last_y, x, y)

		elif tool==ID_TOOL_LINE:
			if self.selected_x==-1 or self.selected_y==-1:
				self.selected_x=x
				self.selected_y=y
			else:
				#dc.DrawLine(self.selected_x, self.selected_y, self.last_x, self.last_y)
				self.Refresh(True)

	def OnLeftDown(self, event):
		self.left_down=True
		self.SetFocus()
		self.UpdateCoords(event)
		self.Draw(event)

	def OnLeftUp(self, event):
		self.left_down=False
		self.UpdateCoords(event)
		self.selected_x=-1
		self.selected_y=-1

	def OnRightDown(self, event):
		self.right_down=True
		self.SetFocus()
		self.UpdateCoords(event)
		self.Draw(event)

	def OnRightUp(self, event):
		self.right_down=False
		self.UpdateCoords(event)
		self.selected_x=-1
		self.selected_y=-1

	def OnMotion(self, event):
		if self.left_down or self.right_down:
			self.Draw(event)
			self.UpdateCoords(event)
		self.last_x=event.GetX()
		self.last_y=event.GetY()

	def OnPaint(self, event):
		#dc=wx.BufferedPaintDC(self, self.buffer)
		dc=wx.PaintDC(self)
		dc.DrawBitmap(self.buffer, 0, 0)

		colour=wx.Colour(*self.control_panel.GetColour())
		colour2=wx.Colour(*self.control_panel.GetColour(1))

		if self.right_down and not self.left_down:
			colour, colour2=colour2, colour

		dc.SetPen(wx.Pen(colour, self.control_panel.line_width))
		dc.SetBrush(wx.Brush(colour))

		if self.control_panel.selected_tool==ID_TOOL_LINE and self.selected_x > -1:
			dc.DrawLine(self.selected_x, self.selected_y, self.last_x, self.last_y)


class ControlPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1, size=(palette_width+8, palette_height+4), style=wx.RAISED_BORDER)

		self.palette=wx.EmptyBitmap(palette_width, palette_height)
		self.InitializePalette()

		self.width_spin=wx.SpinCtrl(self, -1, size=(30, -1))
		self.width_spin.SetRange(1, 50)
		self.width_spin.SetValue(1)

		self.primary_colour=0
		self.secondary_colour=0
		self.selected_tool=ID_TOOL_LINE
		self.line_width=1

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.Bind(wx.EVT_SCROLL, self.OnWidthSpin, self.width_spin)

		sizer=wx.BoxSizer(wx.VERTICAL)
		sizer.AddSpacer(palette_width)
		sizer.AddSpacer(palette_height / 2)
		sizer.AddSpacer(12 + 32 + 24 + 4)
		sizer.Add(self.width_spin, 0, wx.EXPAND)
		self.SetSizer(sizer)

	def InitializePalette(self):
		dc=wx.MemoryDC()
		dc.SelectObject(self.palette)
		pix_x=0
		pix_y=0
		for colour in palette:
			dc.SetBrush(wx.Brush(wx.Colour(*colour)))
			dc.SetPen(wx.TRANSPARENT_PEN)
			dc.DrawRectangle(pix_x * palette_box_width, pix_y * palette_box_width, palette_box_width, palette_box_width)
			pix_x+=1
			if pix_x>=palette_width / palette_box_width:
				pix_x-=palette_width / palette_box_width
				pix_y+=1
		dc.SelectObject(wx.NullBitmap)

	def GetColour(self, right=0):
		if right:
			return self.IndexToRGB(self.secondary_colour)
		return self.IndexToRGB(self.primary_colour)

	def IndexToRGB(self, index): #Get RGB from index (13) or grid coords (0, 1)
		if isinstance(index, int):
			return palette[index]
		elif isinstance(index, tuple):
			return palette[self.IndexConversion(index)]

	def IndexConversion(self, index): #Convert between index (13) and grid coords (0, 1)
		if isinstance(index, int):
			return (index % (palette_width / palette_box_width), index / (palette_width / palette_box_width))
		elif isinstance(index, tuple):
			return index[0] + index[1] * palette_width / palette_box_width

	def SelectColour(self, index, primary=1):
		if isinstance(index, tuple): index=self.IndexConversion(index)

		if primary:
			self.primary_colour=index
		else:
			self.secondary_colour=index
		self.Refresh(False)

	def PreviewTool(self, dc):
		if self.selected_tool==ID_TOOL_BRUSH:
			dc.SetPen(wx.Pen(wx.Colour(*self.IndexToRGB(self.primary_colour)), self.line_width))
			dc.SetBrush(wx.Brush(wx.Colour(*self.IndexToRGB(self.primary_colour))))
			dc.DrawLine(20 + 32 + 4 + self.line_width / 2, palette_height + 12 + 32, 20 + 32 + 64 - self.line_width / 2 - 1, palette_height + 12 + 32)

	def OnPaint(self, event):
		dc=wx.PaintDC(self)
		dc.DrawBitmap(self.palette, 0, 0)
		dc.SetBrush(wx.TRANSPARENT_BRUSH)

		x, y=self.IndexConversion(self.primary_colour)
		x2, y2=self.IndexConversion(self.secondary_colour)

		#Primary colour indicator
		dc.SetPen(wxPENBLACK)
		dc.DrawRectangle(x * palette_box_width, y * palette_box_width, palette_box_width, palette_box_width)
		dc.SetPen(wxPENWHITE)
		dc.DrawRectangle(1 + x * palette_box_width, 1 + y * palette_box_width, palette_box_width - 2, palette_box_width - 2)

		#Secondary colour indicator
		dc.SetPen(wxPENBLACK)
		dc.DrawRoundedRectangle(x2 * palette_box_width, y2 * palette_box_width, 10, 10, 4)
		dc.SetPen(wxPENWHITE)
		dc.DrawRoundedRectangle(1 + x2 * palette_box_width, 1 + y2 * palette_box_width, palette_box_width - 2, palette_box_width - 2, 4)

		#Colour and tool preview
		dc.SetPen(wxPENGRAY)
		dc.SetBrush(wx.Brush(wx.Colour(*self.IndexToRGB(self.secondary_colour))))
		dc.DrawRectangle(2 + 18, palette_height + 12 + 18, 32, 32) #36 x
		dc.SetBrush(wx.Brush(wx.Colour(*self.IndexToRGB(self.primary_colour))))
		dc.DrawRectangle(2, palette_height + 12, 32, 32)

		colour=wx.Colour(*self.GetBackgroundColour())
		dc.SetBrush(wx.Brush(colour))
		dc.DrawRectangle(20 + 32 + 2, palette_height + 12, 64, 64)

		self.PreviewTool(dc)

	def OnLeftDown(self, event):
		x, y=event.GetX(), event.GetY()
		if x < palette_width and y < palette_height:
			index=self.IndexConversion((x / 10, y / 10))
			self.SelectColour(index)

	def OnRightDown(self, event):
		x, y=event.GetX(), event.GetY()
		if x < palette_width and y < palette_height:
			index=self.IndexConversion((x / 10, y / 10))
			self.SelectColour(index, 0)

	def OnWidthSpin(self, event):
		self.line_width=event.GetPosition()
		self.Refresh(False)
