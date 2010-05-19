
""" Required libraries """
import sys
import traceback
import os
import platform
import unicodedata
import Image
import re
import subprocess
import time
import shutil
import xml.sax
import xml.sax.handler
from xml.dom.minidom import parseString as xmlParseString

if not hasattr(sys, 'frozen'):
	import wxversion
	wxversion.select("2.8")

import wx
import agw
import agw.aui as wxAui
import agw.flatmenu as wxFlatMenu
from wx import stc as wxStc
from wx import gizmos as wxGizmos

from icache import IconCache
cache = IconCache()


""" Window and event IDs """
from id import *


""" Useful functions """
def ImgToWx(img, size=(-1, -1)):
	wximage = wx.EmptyImage(img.size[0], img.size[1])
	wximage.SetData(img.convert('RGB').tostring())
	wximage.SetAlphaData(img.convert('RGBA').tostring()[3::4])
	if size != (-1, -1):
		wximage.Rescale(size[0], size[1], quality=wx.IMAGE_QUALITY_HIGH)

	return wx.BitmapFromImage(wximage)

def WxToImg(img):
	img = img.ConvertToImage()
	pilimg = Image.new('RGB', (img.GetWidth(), img.GetHeight()))
	pilimg.fromstring(img.GetData())
	return pilimg


""" Settings """
dmide_art_quality = wx.IMAGE_QUALITY_HIGH
dmide_menu_type = 'fancy'
dmide_menu_art_size = 16
dmide_filetree_icon_size = 16
dmide_objtree_icon_size = 16
dmide_editor_icon_size = 16
dmide_editor_tab_art = wxAui.AuiDefaultTabArt #AuiDefaultTabArt AuiSimpleTabArt VC71TabArt FF2TabArt VC8TabArt ChromeTabArt
dmide_editor_style = wxAui.AUI_NB_SMART_TABS|wxAui.AUI_NB_SCROLL_BUTTONS|\
                     wxAui.AUI_NB_WINDOWLIST_BUTTON|wxAui.AUI_NB_TAB_SPLIT|\
                     wxAui.AUI_NB_TAB_MOVE|wxAui.AUI_NB_CLOSE_ON_ACTIVE_TAB|wxAui.AUI_NB_USE_IMAGES_DROPDOWN|wx.NO_BORDER
dmide_tree_dmi_tree = True


""" Art """
from art import DMIDE_ArtFactory, id_to_art, idn_to_art


""" dmi, dmf, dmp, rsc readers and writers """
from libbyond import dmi, dmf, dmp, dme, rsc, obj, PngImagePlugin #PIL patch for reading zTXT chunks


""" Definitions for file types """
dmfiles_wildcard = 'DM Files (*.dm;*.dmp;*.dmm;*.dmi;*.dmf;*.dms;*.dme)|*.dm;*.dmp;*.dmm;*.dmi;*.dmf;*.dms;*.dme|' \
				   'All Files (*.*)|*.*'

environment_wildcard = 'DM Environment (*.dme)|*.dme|' \
					   'All Files (*.*)|*.*'

imagefiles_wildcard = 'Image Files (*.dmi;*.png)|*.dmi;*.png' \
					'All Files (*.*)|*.*'


""" dm, dmi, dmf, dmp, rsc editors """
from editors.dmeditor import DMIDE_DMEditor
from editors.dmieditor import DMIDE_DMIEditor
from editors.rsceditor import DMIDE_RSCEditor
from editors.dmpeditor import DMIDE_DMPEditor
from editors.oggeditor import DMIDE_OGGEditor


""" Panels """
from panels.menubar import DMIDE_MenuBar, DMIDE_FancyMenuBar
from panels.buildinfo import DMIDE_BuildInfo
from panels.editor import DMIDE_Editor
from panels.filetree import DMIDE_FileTree
from panels.objtree import DMIDE_ObjTree
from panels.classtree import DMIDE_ClassTree
from panels.painter import DMIDE_Painter
from panels.window import DMIDE_Window
