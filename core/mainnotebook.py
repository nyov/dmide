
from id import *
import wx.aui as aui
from codepage import CodePage
from paintpage import PaintPage

from random import randint as rand

class MainNotebook(aui.AuiNotebook):
	def __init__(self, parent):
		aui.AuiNotebook.__init__(self, parent, -1, style=aui.AUI_NB_TAB_SPLIT|aui.AUI_NB_TAB_MOVE|aui.AUI_NB_SCROLL_BUTTONS|aui.AUI_NB_CLOSE_ON_ALL_TABS)
		self.OnFileNew(None)

	def OnFileNew(self, event):
		test=PaintPage(self.GetParent())
		self.AddPage(test, 'test.dmi')

	def OnFileOpen(self, event):
		pass

	def OnFileClose(self, event):
		pass

	def OnFileSave(self, event):
		pass

	def OnFileSaveAs(self, event):
		pass
