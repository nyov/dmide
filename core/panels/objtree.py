import core
from core import *

import thread


class IconCache:
	def __init__(self):
		self.cache = {}

	def read(self, path):
		if not path in self.cache:
			icons = dmi.DMIREAD(path)
			self.cache[path] = icons
			return icons
		return self.cache[path]


class DMIDE_ObjTree(wx.TreeCtrl):
	def __init__(self, parent):
		wx.TreeCtrl.__init__(self, parent, ID_OBJTREE, style = wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.NO_BORDER)

	def UpdateObjTree(self):
		wx.CallLater(10, thread.start_new_thread, self.run, ())

	def run(self):
		print 'updating obj tree'
		filetree = wx.FindWindowById(ID_FILETREE)
		self.DeleteAllItems()

		try:
			dme_path = filetree.project_path
		except AttributeError:
			return

		build_path = ''

		if os.name in ['posix', 'os2', 'mac', 'ce']:
			build_path = '/usr/local/byond/bin'
			dm_path = 'DreamMaker'

		elif os.name in ['dos', 'nt']:
			build_path = 'C:\\Program Files\\BYOND\\bin'
			dm_path = os.path.join(build_path, 'dm.exe')

		p = subprocess.Popen([dm_path, '-o', dme_path], stdout=subprocess.PIPE)
		#open('test.log', 'w').write(p.stdout.read())
		objs = obj.OBJREAD(p.stdout)
		self.objects = objs

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
						icon = cache.read(icon_path, self)
						for i in icon:
							if i.state == icon_state:
								return images.Add(ImgToWx(i.icons[0][0], (dmide_objtree_icon_size, dmide_objtree_icon_size)))

			elif isinstance(object, obj.DMIDE_Proc):
				return 1

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

				new_root = None

				if hasattr(object, 'children') and len(object.children):
					new_root = self.AppendItem(root, object.name)
					self.SetItemImage(new_root, get_icon(object, images), wx.TreeItemIcon_Normal)

					populate(object.children, new_root, images)

				if not new_root:
					new_root = self.AppendItem(root, object.name)
					self.SetItemImage(new_root, get_icon(object, images), wx.TreeItemIcon_Normal)

		root = self.AddRoot(os.path.split(dme_path)[-1])
		image_list = wx.ImageList(dmide_objtree_icon_size, dmide_objtree_icon_size)
		image_list.Add(wx.EmptyBitmapRGBA(dmide_objtree_icon_size, dmide_objtree_icon_size, 128, 128, 128, 128))
		image_list.Add(wx.GetApp().art.getFromExt('proc', (dmide_objtree_icon_size, dmide_objtree_icon_size)))
		populate(objs, root, image_list)
		self.AssignImageList(image_list)
		print 'done obj tree'
		cache.clear(self)

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
							icon = cache.read(icon_path, self)#dmi.DMIREAD(icon_path)
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
