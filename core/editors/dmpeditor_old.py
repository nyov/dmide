import core
from core import *


class DMIDE_DMPEditor(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		wx.EVT_PAINT(self, self.OnDraw)

		self.map = None

	def Open(self, file):
		self.map = dmp.DMPREAD(file)
		self.Load()

	def Save(self, path=None):
		pass

	def Load(self):
		if not self.map:
			return

		path = wx.FindWindowById(ID_FILETREE).path
		self.images = {}

		for definition in self.map.definitions.keys():
			for instance in self.map.definitions[definition]:
				if instance.type in self.images:
					continue
				try:
					wx.FindWindowById(ID_OBJTREE).GetIconFromTypePath(instance.type)
				except:
					traceback.print_exc()
				if instance.type == '/area':
					self.images[instance.type] = ImgToWx(dmi.DMIREAD(os.path.join(path, 'area.dmi'))[0].icons[0][0])
				elif instance.type == '/turf':
					self.images[instance.type] = ImgToWx(dmi.DMIREAD(os.path.join(path, 'turf.dmi'))[0].icons[0][0])
				elif instance.type == '/obj':
					self.images[instance.type] = ImgToWx(dmi.DMIREAD(os.path.join(path, 'obj.dmi'))[0].icons[0][0])
				elif instance.type == '/mob':
					self.images[instance.type] = ImgToWx(dmi.DMIREAD(os.path.join(path, 'mob.dmi'))[0].icons[0][0])
				else:
					self.images[instance.type] = wx.EmptyBitmap(32, 32)

		for definition in self.map.definitions:
			print definition, '=', self.map.definitions[definition]

	def OnDraw(self, event):
		if self.map:
			dc = wx.PaintDC(self)

			for y, tiles in enumerate(self.map.tiles[0][::-1]):
				for x, tile in enumerate(tiles):
					if not tile in self.map.definitions:
						print 'no %s in definitions?' % tile
						continue

					for object in self.map.definitions[tile][::-1]:
						dc.DrawBitmap(self.images[object.type], x * 32, y * 32)

	def OnSize(self, event):
		try:
			width, height = event.GetSize()
		except:
			width = event.GetSize().width
			height = event.GetSize().height

		self.Refresh()
		self.Update()

	def OnMouseMotion(self, event):
		x = event.GetX()
		y = event.GetY()

