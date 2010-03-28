import core
from core import *


class DMIDE_BuildInfo(wxGizmos.TreeListCtrl):
	""" Handles compiling and displaying build errors. """

	def __init__(self, parent):
		wxGizmos.TreeListCtrl.__init__(self, parent, ID_BUILDINFORMATION, style = wx.NO_BORDER | wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_NO_LINES)
		self.AddColumn(' ')
		self.AddColumn('Message')
		self.AddColumn('Error')
		self.AddColumn('File')
		self.SetMainColumn(0)
		self.SetColumnWidth(0, 40)
		self.SetColumnWidth(1, 200)
		self.SetColumnWidth(2, 120)
		self.SetColumnWidth(3, 200)
		self.root = self.AddRoot(' ')
		self.Expand(self.root)

		self.image_list = wx.ImageList(16, 16)
		self.warning_id = self.image_list.Add(wx.ArtProvider_GetBitmap(wx.ART_WARNING, wx.ART_OTHER, (16, 16)))
		self.error_id = self.image_list.Add(wx.ArtProvider_GetBitmap(wx.ART_ERROR, wx.ART_OTHER, (16, 16)))
		self.SetImageList(self.image_list)
		self.compiled = 0

		self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)

	def OnActivate(self, event):
		item = event.GetItem()
		file = self.GetItemText(item, 3)

		if len(file):
			file, line = file.split(':')
			page = wx.FindWindowById(ID_EDITOR).Open(file)
			if page:
				page.highlight_error(int(line))
		else:
			event.Skip()

	def compile(self):
		filetree = wx.FindWindowById(ID_FILETREE)

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

		self.DeleteChildren(self.root)
		self.Refresh(True)

		#p = subprocess.Popen([dm_path, '-v'], stdout=subprocess.PIPE) --grab version

		def compile_after(self):
			self.SetItemText(self.AppendItem(self.root, ' '), 'Compiling...', 1)
			self.error_parent = None
			self.errors = 0
			self.warning_parent = None
			self.warnings = 0

			start = time.time()
			p = subprocess.Popen([dm_path, dme_path], stdout=subprocess.PIPE)

			while 1:
				output = p.stdout.readline()
				if not output and p.poll() != None: break
				self.process_line(output)

			finish = time.time()
			self.SetItemText(self.AppendItem(self.root, ' '), '\nTotal time: %0.3fs' % (finish-start), 1)
			if self.error_parent:
				self.SetItemText(self.error_parent, '%i Errors' % self.errors, 1)
			if self.warning_parent:
				self.SetItemText(self.warning_parent, '%i Warnings' % self.warnings, 1)

			self.get_object_tree()

			return not self.errors

		wx.CallLater(10, compile_after, self)

	def process_line(self, line):
		line = line.strip()
		loading_match = re.match('loading (.+).(dme|dmm|dmf|dmp)', line)
		if loading_match:
			self.SetItemText(self.AppendItem(self.root, ' '), 'Loading %s.%s...OK\n' % (loading_match.group(1), loading_match.group(2)), 1)

		saving_match = re.match('saving (.+).dmb', line)
		if saving_match:
			self.SetItemText(self.AppendItem(self.root, ' '), 'Saving %s.dmb...OK\n' % (saving_match.group(1)), 1)

		return '%s\n' % self.process_error(line)

	def process_error(self, line):
		data = re.match('(.+):(\d+):(error):(.*):(.+)', line)
		if data:
			if not self.error_parent:
				self.error_parent = self.AppendItem(self.root, ' ')
				self.SetItemBackgroundColour(self.error_parent, wx.Color(255, 100, 100))
				self.SetItemImage(self.error_parent, self.error_id)

			child = self.AppendItem(self.error_parent, ' ')
			self.SetItemText(child, data.group(5), 1)
			self.SetItemText(child, data.group(4).strip(), 2)
			self.SetItemText(child,'%s:%s' % (data.group(1), data.group(2)), 3)

			self.SetItemBackgroundColour(child, wx.Color(255, 100, 100))
			self.errors += 1
			return

		data = re.match('(.+):(\d+):(warning):(.*):(.+)', line)
		if data:
			if not self.warning_parent:
				self.warning_parent = self.AppendItem(self.root, ' ')
				self.SetItemBackgroundColour(self.warning_parent, wx.Color(255, 255, 100))
				self.SetItemImage(self.warning_parent, self.warning_id)

			child = self.AppendItem(self.warning_parent, ' ')
			self.SetItemText(child, data.group(5), 1)
			self.SetItemText(child, data.group(3).strip(), 2)
			self.SetItemText(child,'%s:%s' % (data.group(1), data.group(2)), 3)
			self.SetItemBackgroundColour(child, wx.Color(255, 255, 100))
			self.warnings += 1

		return 'unknown: %s' % line

	def get_object_tree(self):
		window = wx.FindWindowById(ID_WINDOW)

		window.Freeze()

		try:
			objtree = wx.FindWindowById(ID_OBJTREE)
			objtree.UpdateObjTree()
			classtree = wx.FindWindowById(ID_CLASSTREE)
			classtree.UpdateObjTree()
		except:
			traceback.print_exc()

		window.Thaw()

	def run(self):
		try:
			dme_path = wx.FindWindowById(ID_FILETREE).project_path
		except AttributeError:
			return

		name = os.path.splitext(os.path.split(dme_path)[-1])[0]
		dmb = name + '.dmb'
		rsc = name + '.rsc'

		if not os.path.exists(dmb):
			return

		try:
			os.mkdir('build')
		except:
			pass

		shutil.move(dmb, os.path.join('build', dmb))
		shutil.move(rsc, os.path.join('build', rsc))

		p = subprocess.Popen(['C:\\Program Files\\BYOND\\bin\\DreamSeeker.exe', os.path.join(os.getcwd(), 'build', dmb)])
