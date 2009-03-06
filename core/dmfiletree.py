#-------------------------------------------------------------------

import core
from core import *

#-------------------------------------------------------------------

class DMFileTree(wx.TreeCtrl):
	""" Handles displaying the files in a project """

#-------------------------------------------------------------------

	def __init__(self, parent):
		wx.TreeCtrl.__init__(self, parent, ID_FILETREE, style = wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.NO_BORDER)

		self.initBindings()
		self.selection = ()

#-------------------------------------------------------------------

	def initBindings(self):
		self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnTreeItemActivated)

#-------------------------------------------------------------------

	def OnTreeItemActivated(self, event):
		""" When a file or folder is activated [double clicked, expanded] """

		item = event.GetItem()
		path, name = self.getItem(item)

		wx.FindWindowById(ID_EDITOR).openFile(os.path.join(path, name))

		event.Skip()

#-------------------------------------------------------------------

	def getItem(self, item):

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

#-------------------------------------------------------------------

	def loadProject(self, project_dir):
		""" Reset the tree and populate it with all the files in a directory """

		if os.path.splitext(project_dir)[-1] != '.dme':
			return

		project_dir = os.path.split(project_dir)[0]

		self.DeleteAllItems()

		dm_art = wx.GetApp().dm_art
		path = os.path.realpath(project_dir)
		self.path = path
		dir_name = os.path.split(path)[-1]
		icon_size = 16

		#-------------------------------------------------------------------

		def step_dir(dir):
			""" grab a dictionary of all the files and folders in a dir """

			files = []
			for item in os.listdir(dir):
				path = os.path.join(dir, item)
				if os.path.isdir(path):
					if item[0] == '.':
						continue
					files.append({item: step_dir(path)})
				elif os.path.isfile(path):
					files.append(item)
			return files

		#-------------------------------------------------------------------

		def get_images(collection, images):
			""" build a dictionary consisting of {ext: icon} """

			for item in collection:
				if type(item) == dict:
					get_images(item[item.keys()[0]], images)
				else:
					ext = os.path.splitext(item)[-1]
					icon = dm_art.getFromExt(ext)
					if type(icon) != int:
						images[ext] = icon

			return images

		#-------------------------------------------------------------------

		def dosort(a, b):
			""" sort the project files and folders! """

			if type(a) == unicode:
				a = str(a)
			if type(b) == unicode:
				b = str(b)

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

		#-------------------------------------------------------------------

		def populate(files, root, images):
			""" populate the file tree with the files and folders and icons gathered """

			first = None
			files.sort(dosort)
			for file in files:
				if type(file) == dict:
					new_root = self.AppendItem(root, file.keys()[0])
					
					self.SetItemImage(new_root, images['dir-closed'], wx.TreeItemIcon_Normal)
					self.SetItemImage(new_root, images['dir-open'], wx.TreeItemIcon_Expanded) 
					populate(file[file.keys()[0]], new_root, images)
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

		#-------------------------------------------------------------------

		root = self.AddRoot(dir_name)
		collection = step_dir(path)

		images = get_images(collection, {})
		images_keys = {}
		image_list = wx.ImageList(icon_size, icon_size)

		for key in images:
			images_keys[key] = image_list.Add(images[key])

		dm_art = wx.GetApp().dm_art

		images_keys['dir-closed'] = image_list.Add(dm_art.getFromWx(wx.ART_FOLDER))
		images_keys['dir-open'] = image_list.Add(dm_art.getFromWx(wx.ART_FOLDER_OPEN))
		images_keys['default'] = image_list.Add(dm_art.getFromWx(wx.ART_NORMAL_FILE))

		del images

		self.AssignImageList(image_list)
		self.SelectItem(populate(collection, root, images_keys))

#-------------------------------------------------------------------

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
