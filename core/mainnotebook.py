
from id import *
import wx.aui as aui
from codepage import CodePage
from paintpage import PaintPage

from random import randint as rand

import os

dmfiles_wildcard = "DM Code File (*.dm)|*.dm|" \
				   "DM Map File (*.dmp;*.dmm)|*.dmp;*.dmm|" \
				   "DM Icon File (*.dmi)|*.dmi|" \
				   "DM Interface File (*.dmf)|*.dmf|" \
				   "DM Script File (*.dms)|*.dms|" \
				   "All Files (*.*)|*.*"


class MainNotebook(aui.AuiNotebook):
	def __init__(self, parent):
		aui.AuiNotebook.__init__(self, parent, -1, style = aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_SCROLL_BUTTONS | aui.AUI_NB_CLOSE_ON_ALL_TABS)
		
		self.pages = {}
		self.new_pages = 0

		self.OnFileNew(None)

	def OnFileNew(self, event):
		self.new_pages += 1

		cp = CodePage(self.GetParent())
		cp.auinotebook = self

		self.AddPage(cp, 'Untitled #%s' % self.new_pages)

	def OnFileOpen(self, event):
		dialog = wx.FileDialog(self, message = 'Choose a file...', defaultDir = os.getcwd(),
							   defaultFile = '', wildcard = dmfiles_wildcard, style = wx.OPEN | wx.CHANGE_DIR)

		if dialog.ShowModal() == wx.ID_OK:
			paths = dialog.GetPaths()
			dialog.Destroy()

			if not len(paths):
				return
			path = paths[0]

			if not os.path.exists(path):
				dialog = wx.MessageDialog(self, 'File `%s` does not exist.' % path,
										  'File Open', style = wx.OK | wx.ICON_INFORMATION)

				dialog.ShowModal()
				dialog.Destroy()

	def OnFileClose(self, event):
		page = self.GetPage(self.GetSelection())

		if not page.CheckChange():
			dialog = wx.MessageDialog(self, '%s has been modified. Save changes?' % self.GetPageText(self.GetSelection()),
									  'Save Changes', wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)
			result = dialog.ShowModal()
			dialog.Destroy()

			if result == wx.ID_YES:
				self.OnFileSave(event)
			elif result == wx.ID_NO:
				pass
			elif result == wx.ID_CANCEL:
				return

		self.DeletePage(self.GetSelection())

	def OnFileSave(self, event):
		pass

	def OnFileSaveAs(self, event):
		pass
