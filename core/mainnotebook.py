
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
		
		self.pages = []
		self.new_pages = 0

		self.Bindings()

		self.OnFileNew(None)

	def Bindings(self):
		pass

	def OnFileNew(self, event):
		dialog = wx.FileDialog(self, message = 'Save file where...', defaultDir = os.getcwd(),
							   defaultFile = 'untitled.dm', wildcard = dmfiles_wildcard, style = wx.SAVE)
		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPath()
			dialog.Destroy()

			for page in self.pages:
				if page.path == path:
					self.SetSelection(self.GetPageIndex(page.page))
					return

			if os.path.exists(path):
				dialog = wx.MessageDialog(self, '%s already exists. Overwrite?' % path,
										  'Overwrite?', wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)
				result = dialog.ShowModal()
				dialog.Destroy()

				if result == wx.ID_YES:
					pass
				elif result == wx.ID_NO:
					return
				elif result == wx.ID_CANCEL:
					return

			open(path, 'w').write('')

			name = os.path.split(path)[1]
			new_page = NotebookPage(self, path, name)

			if not new_page.page:
				return

			self.AddPage(new_page.page, name)
			self.pages.append(new_page)

	def OnFileOpen(self, event):
		dialog = wx.FileDialog(self, message = 'Choose a file...', defaultDir = os.getcwd(),
							   defaultFile = '', wildcard = dmfiles_wildcard, style = wx.OPEN | wx.CHANGE_DIR)

		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPath()
			dialog.Destroy()

			for page in self.pages:
				if page.path == path:
					self.SetSelection(self.GetPageIndex(page.page))
					return

			if not os.path.exists(path):
				dialog = wx.MessageDialog(self, 'File `%s` does not exist.' % path,
										  'File Open', style = wx.OK | wx.ICON_INFORMATION)

				dialog.ShowModal()
				dialog.Destroy()
				return

			name = os.path.split(path)[1]
			new_page = NotebookPage(self, path, name)

			if not new_page.page:
				return

			new_page.page.SetValue(open(path, 'r').read())
			self.AddPage(new_page.page, name)
			self.pages.append(new_page)

	def OnFileClose(self, event):
		page = self.GetPage(self.GetSelection())

		if not page.CheckChange():
			dialog = wx.MessageDialog(self, '%s has been modified. Save changes?' % os.path.split(page.notebook_page.path)[1],
									  'Save Changes', wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)
			result = dialog.ShowModal()
			dialog.Destroy()

			if result == wx.ID_YES:
				self.OnFileSave(None, page.notebook_page)
			elif result == wx.ID_NO:
				pass
			elif result == wx.ID_CANCEL:
				return

		self.pages.remove(page.notebook_page)
		self.DeletePage(self.GetSelection())

	def OnFileSave(self, event, page = None):
		if not page:
			page = self.GetPage(self.GetSelection()).notebook_page

		if page:
			open(page.path, 'w').write(page.page.GetValue())
			page.page.original_content = open(page.path, 'r').read()
			

	def OnFileSaveAs(self, event):
		pass


class NotebookPage:
	def __init__(self, auinotebook, path = '', title = ''):
		self.auinotebook = auinotebook
		self.path = path
		self.title = title
		self.page = None
		self.Create()

	def Create(self):
		if os.path.splitext(self.path)[1] in ['.dm', '.txt', '.dms', '.dmf']:
			self.page = CodePage(self.auinotebook, self)

	def OnChange(self, changed = False):
		pos = self.auinotebook.GetPageIndex(self.page)
		if not changed:
			self.auinotebook.SetPageText(pos, os.path.split(self.path)[1])
		else:
			self.auinotebook.SetPageText(pos, '%s *' % os.path.split(self.path)[1])