import core
from core import *

import thread


class DMIDE_ClassTree(wx.TreeCtrl):
	def __init__(self, parent):
		wx.TreeCtrl.__init__(self, parent, ID_CLASSTREE, style = wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.NO_BORDER)

	def UpdateObjTree(self):
		thread.start_new_thread(self.run, ())

	def run(self):
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

		def populate(items, root, types=(obj.DMIDE_Atom,)):
			for object in items:
				try:
					object.name
				except AttributeError:
					print >> sys.stderr, '[class] objectect without a name?', object
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

					populate(object.children, new_root)

				if hasattr(object, 'vars') and len(object.vars):
					if not new_root:
						new_root = self.AppendItem(root, object.name)
					vars_root = self.AppendItem(new_root, 'vars')
					populate(object.vars, vars_root, (obj.DMIDE_Var,))

				if hasattr(object, 'verbs') and len(object.verbs):
					if not new_root:
						new_root = self.AppendItem(root, object.name)

					verbs_root = self.AppendItem(new_root, 'verbs')
					populate(object.verbs, verbs_root, (obj.DMIDE_Verb,))

				if hasattr(object, 'procs') and len(object.procs):
					if not new_root:
						new_root = self.AppendItem(root, object.name)

					procs_root = self.AppendItem(new_root, 'procs')
					populate(object.procs, procs_root, (obj.DMIDE_Proc,))

				if not new_root:
					new_root = self.AppendItem(root, object.name)

		root = self.AddRoot(os.path.split(dme_path)[-1])
		populate(objs, root)
