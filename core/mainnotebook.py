
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

	def Bindings(self):
		self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnFileClose)
		self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

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

			content = open(path, 'r').read()
			new_page.page.SetValue(content)
			new_page.page.original_content = content
			self.AddPage(new_page.page, name)
			self.pages.append(new_page)

	def OnFileClose(self, event, page = None, veto = True):
		if not page:
			try:
				page = self.GetPage(self.GetSelection())
			except Exception, e:
				return

		if not page.CheckChange():
			dialog = wx.MessageDialog(self, '%s has been modified. Save changes?' % os.path.split(page.notebook_page.path)[1],
									  'Save Changes', wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)
			result = dialog.ShowModal()
			dialog.Destroy()

			if result == wx.ID_YES:
				self.OnFileSave(None, page.notebook_page)
				if veto: event.Veto()
			elif result == wx.ID_NO:
				if veto: event.Veto()
			elif result == wx.ID_CANCEL:
				if veto: event.Veto()
				return -1

		self.pages.remove(page.notebook_page)
		self.DeletePage(self.GetPageIndex(page))

	def OnFileSave(self, event, page = None):
		if not page:
			try:
				page = self.GetPage(self.GetSelection()).notebook_page
			except Exception, e:
				return

		if page:
			open(page.path, 'w').write(page.page.GetValue())
			page.page.original_content = open(page.path, 'r').read()
			

	def OnFileSaveAs(self, event):
		try:
			page = self.GetPage(self.GetSelection()).notebook_page
		except Exception, e:
			return

		dialog = wx.FileDialog(self, message = 'Save file', defaultDir = os.path.split(page.path)[0],
							   defaultFile = os.path.split(page.path)[1], wildcard = dmfiles_wildcard, style = wx.SAVE)
		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPath()
			dialog.Destroy()

			if os.path.exists(path):
				dialog = wx.MessageDialog(self, '%s already exists. Overwrite?' % path,
										  'Overwrite?', wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)
				result = dialog.ShowModal()
				dialog.Destroy()

				if result == wx.ID_NO:
					return
				elif result == wx.ID_CANCEL:
					return

			page.path = path
			self.OnFileSave(event, page)

	def OnPageChanged(self, event):
		page = self.GetPage(self.GetSelection()).notebook_page
		self.GetParent().SetTitle('DMIDE - %s' % page.path)


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