import core
from core import *

dmide_objtree_icon_size = 32


class DMIDE_ObjTree(wx.ListCtrl):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, ID_OBJTREE, style = wx.LC_ICON | wx.LC_VIRTUAL | wx.LC_EDIT_LABELS | wx.NO_BORDER)

		self.last_pos = -1
		self.icons = []
		self.Bind(wx.EVT_SIZE, self.OnSize)

	def OnSize(self, event):
		event.Skip()
		last_pos = self.GetItemRect(self.GetItemCount() - 1)
		if self.last_pos != last_pos:
			self.last_pos = last_pos
			self.Refresh(False)

	def UpdateObjTree(self, nObj=None):
		if not nObj:
			filetree = wx.FindWindowById(ID_FILETREE)
			self.DeleteAllItems()

			try:
				dme_path = filetree.project_path
			except AttributeError:
				return

			build_path = ''

			if os.name in ['posix', 'os2', 'mac', 'ce']:
				build_path = '/usr/local/byond/bin'
				dm_path = os.path.join(build_path, 'DreamMaker')

			elif os.name in ['dos', 'nt']:
				build_path = 'C:\\Program Files\\BYOND\\bin'
				dm_path = os.path.join(build_path, 'dm.exe')

			p = subprocess.Popen([dm_path, '-o', dme_path], stdout=subprocess.PIPE)

			objs = obj.OBJREAD(p.stdout)
			self.objects = objs

		else:
			self.objects = nObj

		def get_icon(object, images):
			if isinstance(object, obj.DMIDE_Datum):
				icon = object.get_inherited_val('icon')
				icon_state = object.get_inherited_val('icon_state')

				if icon_state:
					icon_state = icon_state.get_value()
				else:
					icon_state = ''

				if icon:
					icon = icon.get_value()
					icon_path = filetree.dme.get_file_path(icon)
					if icon_path:
						icon = dmi.DMIREAD(icon_path)
						for i in icon:
							if i.state == icon_state:
								return images.Add(ImgToWx(i.icons[0][0], (dmide_objtree_icon_size, dmide_objtree_icon_size)))

			return 0

		def populate(items, root, images, types=(obj.DMIDE_Atom,)):
			for object in items:
				try:
					object.name
				except AttributeError:
					print >> sys.stderr, '[object] object without a name?', object
					continue

				found = False
				for type in types:
					if isinstance(object, type):
						found = True
						break

				if not found:
					continue

				root.icons.append((object.name, get_icon(object, images)))

				if hasattr(object, 'children') and len(object.children):
					populate(object.children, root, images)

		image_list = wx.ImageList(dmide_objtree_icon_size, dmide_objtree_icon_size)
		image_list.Add(wx.EmptyBitmapRGBA(dmide_objtree_icon_size, dmide_objtree_icon_size, 128, 128, 128, 128))

		populate(objs, self, image_list)
		self.AssignImageList(image_list, wx.IMAGE_LIST_NORMAL)
		self.SetItemCount(len(self.icons))

	def OnGetItemText(self, index, col):
		try:
			return self.icons[index][0]
		except IndexError:
			return 'IndexError'

	def OnGetItemImage(self, index):
		try:
			return self.icons[index][1]
		except IndexError:
			return 'IndexError'

	def OnGetItemAttr(self, index):
		return None

	def GetIconFromTypePath(self, path):
		hierarchy = path.split('/')
		filetree = wx.FindWindowById(ID_FILETREE)

		def get_obj(object, match):
			if ('/%s' % object.name) == match:
				return object

			elif object.name == match.split('/')[1]:
				for child in object.children:
					value = get_obj(child, match[match.find('/', 2):])
					if value:
						return value

		for object in self.objects:
			value = get_obj(object, path)
			object = value
			if value:
				if isinstance(object, obj.DMIDE_Datum):
					icon = object.get_inherited_val('icon')
					icon_state = object.get_inherited_val('icon_state')

					if icon_state:
						icon_state = icon_state.get_value()
					else:
						icon_state = ''

					if icon:
						icon = icon.get_value()
						icon_path = filetree.dme.get_file_path(icon)
						if icon_path:
							icon = dmi.DMIREAD(icon_path)
							for i in icon:
								if i.state == icon_state:
									return ImgToWx(i.icons[0][0])

	def GetVisualAttributesFromPath(self, path):
		hierarchy = path.split('/')
		filetree = wx.FindWindowById(ID_FILETREE)

		def get_obj(object, match):
			if ('/%s' % object.name) == match:
				return object

			elif object.name == match.split('/')[1]:
				for child in object.children:
					value = get_obj(child, match[match.find('/', 2):])
					if value:
						return value

		for object in self.objects:
			value = get_obj(object, path)
			object = value
			if value:
				if isinstance(object, obj.DMIDE_Datum):
					icon = object.get_inherited_val('icon')
					icon_state = object.get_inherited_val('icon_state')

					icon = '' or icon.get_value()
					icon_state = '' or icon_state.get_value()

					return [icon, icon_state]