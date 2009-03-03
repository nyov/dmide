#-------------------------------------------------------------------

""" Required libraries """
import sys
import os
import wx
from wx import aui as wxAui

#-------------------------------------------------------------------

""" Helper modules """
from id import *
from helpers.safe_eval import safe_eval
from helpers.menuservice import installMenuService
from helpers.perspectives import PerspectiveOptions

#-------------------------------------------------------------------

""" Definitions for file types """
dmfiles_wildcard = 'DM Code File (*.dm)|*.dm|' \
				   'DM Map File (*.dmp;*.dmm)|*.dmp;*.dmm|' \
				   'DM Icon File (*.dmi)|*.dmi|' \
				   'DM Interface File (*.dmf)|*.dmf|' \
				   'DM Script File (*.dms)|*.dms|' \
				   'DM Environment File (*.dme)|*.dme|' \
				   'All Files (*.*)|*.*'

environment_wildcard = 'DM Environment (*.dme)|*.dme|' \
					   'All Files (*.*)|*.*'

#-------------------------------------------------------------------

""" DMIDE classes """
from dmartfactory import DMArtFactory
from dmbuildinfo import DMBuildInfo
from dmfiletree import DMFileTree
from dmwindow import DMWindow
from dmframe import DMFrame

#-------------------------------------------------------------------