 
from id import *
import wx.stc as stc
import os

class CodePage(wx.TextCtrl):
  def __init__(self, parent, notebook_page):
    wx.TextCtrl.__init__(self, parent, -1, style = wx.TE_MULTILINE | wx.TE_RICH2)

    self.original_content = ''
    self.notebook_page = notebook_page

    self.Bindings()

  def Bindings(self):
    self.Bind(wx.EVT_TEXT, self.OnChange)

  def OnChange(self, event):
    self.CheckChange()

  def OnSave(self, event):
    self.original_content = self.GetValue()
    self.CheckChange()

  def CheckChange(self):
    if self.GetValue() != self.original_content:
      self.notebook_page.OnChange(True)
      return 0
    else:
      self.notebook_page.OnChange(False)
      return 1