import core
from core import *

import wx.lib.dragscroller


class DMIDE_DMPEditor(wx.ScrolledWindow):
	def __init__(self, parent):
		wx.ScrolledWindow.__init__(self, parent, style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN)
		self.scroller = wx.lib.dragscroller.DragScroller(self)

		self.tile_size = (32, 32)
		self.map_size = (0, 0)
		self.dimensions = (self.tile_size[0] * self.map_size[0], self.tile_size[1] * self.map_size[1])
		self.map = None
		self.images = {}
		self.show_grid = True
		self.zoom = 1.0

		self.mouse_pos = (-1, -1)

		self.SetVirtualSize(self.dimensions)
		self.SetScrollRate(1, 1)

		self.selection = wx.EmptyBitmapRGBA(self.tile_size[0], self.tile_size[1], 115, 140, 226, 128)

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_SCROLLWIN, self.OnScroll)
		self.Bind(wx.EVT_MIDDLE_DOWN, self.OnMiddleDown)
		self.Bind(wx.EVT_MIDDLE_UP, self.OnMiddleUp)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

		self.buffer = wx.EmptyBitmap(*self.dimensions)
		#self.buffer_zoom = wx.EmptyBitmap(*self.dimensions)
		self.UpdateDrawing()

	def Open(self, path):
		self.map = dmp.DMPREAD(path)
		print 'DEBUG: map is: %s' % self.map
		self.images = {}
		self.map_size = (len(self.map.tiles[0][0]), len(self.map.tiles[0]))
		self.dimensions = (self.tile_size[0] * self.map_size[0], self.tile_size[1] * self.map_size[1])
		self.buffer = wx.EmptyBitmap(*self.dimensions)
		self.SetVirtualSize(self.dimensions)

		empty = wx.EmptyBitmapRGBA(self.tile_size[0], self.tile_size[1], *self.GetBackgroundColour())

		for definition in self.map.definitions.keys():
			for instance in self.map.definitions[definition]:
				if instance.type in self.images:
					continue

				icon = wx.FindWindowById(ID_OBJTREE).GetIconFromTypePath(instance.type)
				if icon:
					self.images[instance.type] = icon
				else:
					self.images[instance.type] = empty

		self.UpdateDrawing()
		self.Refresh(True)

	def CoordToTile(self, x, y):
		return round(x / self.tile_size[0]) * self.tile_size[0], round(y / self.tile_size[1]) * self.tile_size[1]

	def OnPaint(self, event):
		new_buffer = wx.EmptyBitmap(*self.GetClientSizeTuple())
		dc = wx.BufferedPaintDC(self, new_buffer)
		self.PrepareDC(dc)

		dc.DrawBitmap(self.buffer, 0, 0)

		if self.mouse_pos != (-1, -1):
			x, y = self.CoordToTile(*self.CalcUnscrolledPosition(self.mouse_pos[0], self.mouse_pos[1]))
			dc.DrawBitmap(self.selection, x, y)

	def OnMotion(self, event):
		self.mouse_pos = event.GetX(), event.GetY()
		self.Refresh()
		self.SetFocus()

	def OnEraseBackground(self, event):
		pass

	def OnSize(self, event):
		event.Skip()
		self.Refresh(False)

	def OnScroll(self, event):
		event.Skip()
		self.Refresh(False)

	def UpdateDrawing(self, savemap=False):
		dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
		self.Draw(dc, savemap)

		#try:
		#self.buffer_zoom = wx.BitmapFromImage(wx.ImageFromBitmap(self.buffer).Rescale(self.buffer.GetSize()[0] * self.zoom, self.buffer.GetSize()[1] * self.zoom))
		#except:
		#	pass
		#self.buffer_zoom = self.buffer

	def Draw(self, dc, savemap=False):
		dc.SetBackground(wx.Brush(wx.Color(168, 168, 168)))
		dc.Clear()

		if self.map:
			for y, tiles in enumerate(self.map.tiles[0][::-1]):
				for x, tile in enumerate(tiles):
					if not tile in self.map.definitions:
						print '[map] no `%s` in definitions?' % tile
						continue

					for object in self.map.definitions[tile][::-1]:
						if object.type in self.images:
							img = self.images[object.type]
							px, py = x * self.tile_size[0], (y+1) * self.tile_size[1]
							py -= img.GetSize()[1]
							dc.DrawBitmap(self.images[object.type], px, py)

				#self.buffer_zoom = self.buffer
				dc.SelectObject(wx.NullBitmap)
				wx.Yield()
				self.Refresh()
				dc.SelectObject(self.buffer)

		if self.show_grid and not savemap:
			pen = wx.Pen(wx.Color(100, 100, 100), 1, wx.DOT)
			dc.SetPen(pen)

			for x in xrange(0, self.dimensions[0], self.tile_size[0]):
				dc.DrawLine(x, 0, x, self.dimensions[1])
			for y in xrange(0, self.dimensions[1], self.tile_size[1]):
				dc.DrawLine(0, y, self.dimensions[0], y)

	def OnMiddleDown(self, event):
		event.Skip()
		self.scroller.Start(event.GetPosition())

	def OnMiddleUp(self, event):
		event.Skip()
		self.scroller.Stop()

	def OnLeftDown(self, event):
		x, y = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
		x, y = self.CoordToTile(x, y)
		x, y = int(x / self.tile_size[0]), (self.map_size[1] - 1) - int(y / self.tile_size[1])

		definition = self.map.tiles[0][y][x]
		if definition in self.map.definitions:
			print self.map.definitions[definition]

	def OnRightDown(self, event):
		self.UpdateDrawing(savemap=True)
		self.buffer.SaveFile('map.png', wx.BITMAP_TYPE_PNG)

	def OnMouseWheel(self, event):
		if event.ControlDown():
			if event.WheelRotation < 0:
				self.zoom /= 1.25
			else:
				self.zoom *= 1.25

			self.UpdateDrawing()
			self.Refresh()
