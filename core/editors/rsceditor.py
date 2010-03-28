import core
from core import *


class DMIDE_RSCEditor(wx.ListCtrl):
		def __init__(self, root):
			wx.ListCtrl.__init__(self, root, style = wx.LC_ICON | wx.LC_VIRTUAL | wx.NO_BORDER | wx.CLIP_CHILDREN)

			self.initAll()
			self.initBinds()

		def initAll(self):
			self.last_pos = -1
			self.files = []
			self.images = None
			self.image_list = None

		def initBinds(self):
			self.Bind(wx.EVT_SIZE, self.OnSize)
			self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

		def Open(self, rscfile):
			self.path = rscfile
			self.files = rsc.RSCREAD(rscfile, True)
			self.update()
			self.Refresh()

		def update(self):
			self.images = []
			self.image_list = wx.ImageList(32, 32)
			art = wx.GetApp().art

			for file in self.files:
				img = art.getFromExt(os.path.splitext(file[0])[-1][1:], (32, 32))

				if type(img) == int:
					img = art.getFromWx(wx.ART_NORMAL_FILE, (32, 32))

				self.images.append(self.image_list.Add(img))

			self.AssignImageList(self.image_list, wx.IMAGE_LIST_NORMAL)
			self.SetItemCount(len(self.files))

		def OnGetItemText(self, index, col):
			try:
				return '%s\n%sB' % (self.files[index][0], self.files[index][1])
			except IndexError:
				return 'IndexError'

		def OnGetItemImage(self, index):
			try:
				return self.images[index]
			except IndexError:
				return 'IndexError'

		def OnGetItemAttr(self, index):
			return None

		def OnSize(self, event):
			event.Skip()
			last_pos = self.GetItemRect(self.GetItemCount() - 1)
			if self.last_pos != last_pos:
				self.last_pos = last_pos
				self.Refresh(False)

		def OnKeyDown(self, event):
			print event.GetKeyCode()
			if event.GetKeyCode() == 72 and event.ControlDown():
				files = rsc.RSCREAD(self.path, False)

				dlg = wx.DirDialog(self, 'Choose a dir to save the files:', style=wx.DD_DEFAULT_STYLE)

				if dlg.ShowModal() == wx.ID_OK:
					path = os.path.abspath(dlg.GetPath())

					if not os.path.exists(path):
						os.mkdir(path)

					for file in files:
						open(os.path.join(path, file[0]), 'wb').write(file[2])

				dlg.Destroy()


if __name__ == '__main__':
	a = wx.App(0)
	w = Window()
	w.Show(True)
	a.MainLoop()
