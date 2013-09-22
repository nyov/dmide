import core
from core import *

import thread


ID_FILETREE_RENAME = wx.NewId()
ID_FILETREE_DELETE = wx.NewId()


class DMFile(str):
	pass


class DMIDE_FileTree(wx.TreeCtrl):
	""" Handles displaying the files in a project. """

	def __init__(self, parent):
		wx.TreeCtrl.__init__(self, parent, ID_FILETREE, style = wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.NO_BORDER)

		self.initBinds()
		self.selection = ()
		self.files = []
		self.path = None # dir path
		self.dme_path = None # dme path
		self.dme = None

		#self.SetDoubleBuffered(True)

	def initBinds(self):
		""" Assign the event handlers. """

		self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnTreeItemActivated)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
		self.Bind(wx.EVT_MENU, self.OnRename, id=ID_FILETREE_RENAME)
		self.Bind(wx.EVT_MENU, self.OnDelete, id=ID_FILETREE_DELETE)

	def OnTreeItemActivated(self, event):
		""" When a file or folder is activated [double clicked, expanded] """

		item = event.GetItem()
		path, name = self.getItem(item)

		if not wx.FindWindowById(ID_EDITOR).Open(os.path.join(path, name)) and \
			not wx.FindWindowById(ID_EDITOR).Open(os.path.join(path)):
			event.Skip()

	def OnRightDown(self, event):
		""" Display a menu when right clicked. """

		hit, pos = self.HitTest(event.GetPosition())

		if hit.IsOk():
			self.SelectItem(hit, True)
			menu = wx.Menu()
			menu.Append(ID_FILETREE_RENAME, 'Rename')
			menu.Append(ID_FILETREE_DELETE, 'Delete')
			self.PopupMenu(menu)

	def OnRename(self, event):
		pass

	def OnDelete(self, event):
		selection = self.GetSelection()

		if selection:
			path, name = self.getItem(selection)
			file_path = os.path.join(path, name)

			if os.path.exists(file_path):
				os.remove(file_path)
				self.Open(self.project_path)


	def getItem(self, item):
		""" Get an item's path and file name. """

		if item == self.GetRootItem():
			return ('', '')

		name = self.GetItemText(item)

		dirs = []
		parent = item
		while 1:
			parent = self.GetItemParent(parent)
			if parent == self.GetRootItem():
				break
			dirs.append(self.GetItemText(parent))

		dirs.reverse()
		dirs.insert(0, self.path)

		if self.GetFirstChild(item)[0].IsOk():
			dirs.append(name)

		path = ''
		for x in dirs:
			path = os.path.join(path, x)

		return (path, name)

	def Open(self, project_dir):
		""" Reset the tree and populate it with all the files in a directory. """
		if os.path.splitext(project_dir)[-1] != '.dme':
			print >> sys.stderr, '[FileTree] Not a DME `%s`' % project_dir
			return

		if not os.path.exists(project_dir):
			print >> sys.stderr, '[FileTree] Does not exist `%s`' % project_dir
			return

		thread.start_new_thread(self._open, (project_dir,))

	def _open(self, project_dir):

		os.chdir(wx.GetApp().get_dir())
		#wx.FindWindowById(ID_WINDOW).Freeze()
		project_dir = os.path.abspath(project_dir)
		self.project_path = project_dir
		project_dir = os.path.split(project_dir)[0]

		self.DeleteAllItems()

		art = wx.GetApp().art
		path = os.path.realpath(project_dir)
		self.path = path
		self.dme_path = project_dir
		self.dme = dme.DME()
		self.dme.read(self.project_path)
		self.dme.get_files()

		dir_name = os.path.split(path)[-1]
		icon_size = dmide_filetree_icon_size

		def step_dir(dir):
			""" Grab a dictionary of all the files and folders in a dir. """

			files = []
			for item in os.listdir(dir):
				path = os.path.join(dir, item)
				item = DMFile(item)
				item._dmide_path = path
				if os.path.isdir(path):
					if item[0] == '.':
						continue
					files.append({item: step_dir(path)})
				elif os.path.isfile(path):
					files.append(item)
			return files

		def get_images(collection, images):
			""" Build a dictionary consisting of {ext: icon}. """

			for item in collection:
				if type(item) == dict:
					get_images(item[item.keys()[0]], images)
				else:
					ext = os.path.splitext(item)[-1]
					icon = art.getFromExt(ext, (icon_size,icon_size))
					if type(icon) != int:
						images[ext] = icon

			return images

		def dosort(a, b):
			""" Sort the project files and folders! """

			if type(a) == unicode:
				a = unicodedata.normalize('NFKD', a).encode('ascii','ignore')
			if type(b) == unicode:
				b = unicodedata.normalize('NFKD', b).encode('ascii','ignore')

			# weights for different types of files
			sorted_weights = ['.dme', '.dmf', '.dm', '.dmi', '.png', '.bmp', '.gif', '.jpeg', '.jpg', '.dmm', '.dmp', '.dms', '.mod',
							  '.it', '.s3m', '.xm', '.oxm', '.mid', '.midi', '.wav', '.ogg', '.raw', '.wma', '.aiff', dict, '.dmb', '.rsc']

			def get_weight(x):
				if type(x) in sorted_weights:
					return sorted_weights.index(type(x))
				if os.path.splitext(x)[-1].lower() in sorted_weights:
					return sorted_weights.index(os.path.splitext(x)[-1].lower())
				return len(sorted_weights)

			weight_a, weight_b = get_weight(a), get_weight(b)

			if weight_a == weight_b:
				if type(a) == dict and type(b) == dict:
					return cmp(a.keys()[0], b.keys()[0])
				elif type(a) == str and type(b) == str:
					ext_a, ext_b = os.path.splitext(a)[-1], os.path.splitext(b)[-1]
					if ext_a == ext_b:
						return cmp(a, b)
					return cmp(ext_a, ext_b)
				else:
					return 0 #wat?

			return cmp(weight_a, weight_b)

		def populate(files, root, images):
			""" Populate the file tree with the files and folders and icons gathered. """

			first = None
			files.sort(dosort)
			for file in files:
				if type(file) == dict:
					new_root = self.AppendItem(root, file.keys()[0])

					self.SetItemImage(new_root, images['dir-closed'], wx.TreeItemIcon_Normal)
					self.SetItemImage(new_root, images['dir-open'], wx.TreeItemIcon_Expanded)
					populate(file[file.keys()[0]], new_root, images)

				elif dmide_tree_dmi_tree and os.path.splitext(file)[-1] == '.dmi':
					new_root = self.AppendItem(root, file)

					dmi_image = 'default'
					if '.dmi' in images:
						dmi_image = '.dmi'
					dmi_image = images[dmi_image]

					self.SetItemImage(new_root, dmi_image, wx.TreeItemIcon_Normal)
					self.SetItemImage(new_root, dmi_image, wx.TreeItemIcon_Expanded)

					icon_info = dmi.DMIINFOREAD(file._dmide_path)
					if not icon_info:
						continue
					states, (width, height) = icon_info

					for info in states:
						try:
							child = self.AppendItem(new_root, info[0])
							self.SetItemImage(child, dmi_image, wx.TreeItemIcon_Normal)
						except:
							traceback.print_exc()
							continue

				else:
					child = self.AppendItem(root, file)

					if not first:
						first = child

					ext = os.path.splitext(file)[-1]
					if ext in images:
						self.SetItemImage(child, images[ext], wx.TreeItemIcon_Normal)
					else:
						self.SetItemImage(child, images['default'], wx.TreeItemIcon_Normal)

			return first

		root = self.AddRoot(dir_name)
		collection = step_dir(path)
		self.files = collection

		images = get_images(collection, {})
		images_keys = {}
		image_list = wx.ImageList(icon_size, icon_size)

		for key in images:
			images_keys[key] = image_list.Add(images[key])

		art = wx.GetApp().art

		images_keys['dir-closed'] = image_list.Add(art.getFromWx(wx.ART_FOLDER, (icon_size,icon_size)))
		images_keys['dir-open'] = image_list.Add(art.getFromWx(wx.ART_FOLDER_OPEN, (icon_size,icon_size)))
		images_keys['default'] = image_list.Add(art.getFromWx(wx.ART_NORMAL_FILE, (icon_size,icon_size)))

		del images

		self.AssignImageList(image_list)
		self.SelectItem(populate(collection, root, images_keys))
		wx.FindWindowById(ID_WINDOW).updateFileMenu()
		wx.FindWindowById(ID_WINDOW).updateBuildMenu()
		wx.CallAfter(wx.FindWindowById(ID_BUILDINFORMATION).get_object_tree)
		#wx.FindWindowById(ID_WINDOW).Thaw()

'''
sorting, as designed by koil

* Directory (/)
	* Environments (.DME)
	* Interfaces (.DMF)

	* Source Code (.DM)
	* Graphics (.DMI, .PNG, .BMP, .GIF, .JPEG)
	* Maps (.DMM)
	* Scripts (.DMS)
	* Audio (.MOD, .IT, .S3M, .XM, .OXM, .MID, .MIDI, .WAV, .OGG, .RAW, .WMA, .AIFF)

	* Folders
		* Environments (.DME)
		* Interfaces (.DMF)

		* Source Code (.DM)
		* Graphics (.DMI, .PNG, .BMP, .GIF, .JPEG)
		* Maps (.DMM)
		* Scripts (.DMS)
		* Audio (.MOD, .IT, .S3M, .XM, .OXM, .MID, .MIDI, .WAV, .OGG, .RAW, .WMA, .AIFF)

		* Subfolders
			* Etc

		* DM Executables (.DMB)
		* Resource Files (.RSC)

		* Other (*.*)

	* DM Executables (.DMB)
	* Resource Files (.RSC)

	* Other (*.*)

	* Library Files
	* External Files

Each section (*) is organized alphabetically (+ 0-9 A-Z a-z).
'''
