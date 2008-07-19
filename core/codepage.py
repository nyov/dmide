 
from id import *
import wx.stc as stc

class CodePage(stc.StyledTextCtrl):
  def __init__(self, parent):
    stc.StyledTextCtrl.__init__(self, parent, -1)
