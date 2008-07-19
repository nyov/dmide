 
from id import *
import wx.stc as stc

class CodePage(wx.TextCtrl):
  def __init__(self, parent):
    wx.TextCtrl.__init__(self, parent, -1, style = wx.TE_MULTILINE | wx.TE_RICH2)

    self.original_content = ''
    self.auinotebook = None

    self.Bindings()

  def Bindings(self):
    self.Bind(wx.EVT_TEXT, self.OnChange)

  def OnChange(self, event):
    self.CheckChange()

  def OnSave(self, event):
    self.original_content = self.GetValue()
    self.CheckChange()

  def CheckChange(self):
    name = self.auinotebook.GetPageText(self.auinotebook.GetSelection())
  
    if self.GetValue() != self.original_content:
      if name[-2:] != ' *':
        self.auinotebook.SetPageText(self.auinotebook.GetSelection(), '%s *' % name)
      return 0
    else:
      if name[-2:] == ' *':
        self.auinotebook.SetPageText(self.auinotebook.GetSelection(), name[:-2])
      return 1