import core
from core import *
import wx.media


class DMIDE_OGGEditor(wx.Panel):
        def __init__(self, root):
            wx.Panel.__init__(self, root)

            self.media = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER)
            self.media.SetVolume(0.9)
            #self.media.ShowPlayerControls(wx.media.MEDIACTRLPLAYERCONTROLS_STEP | wx.media.MEDIACTRLPLAYERCONTROLS_VOLUME)

            self.slider = wx.Slider(self, wx.ID_ANY, 0, 0, 0)
            self.play = wx.Button(self, wx.ID_ANY, 'Play')
            self.stop = wx.Button(self, wx.ID_ANY, 'Stop')
            self.pause = wx.Button(self, wx.ID_ANY, 'Pause')
            self.volume = wx.Slider(self, wx.ID_ANY, 10.0, 0.0, 11.0)

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.media, 1, wx.EXPAND)
            sizer.Add(self.slider, 0, wx.EXPAND)

            sizer2 = wx.BoxSizer(wx.HORIZONTAL)
            sizer2.Add(self.play, 0, wx.EXPAND)
            sizer2.Add(self.stop, 0, wx.EXPAND)
            sizer2.Add(self.pause, 0, wx.EXPAND)
            sizer2.Add(self.volume, 0, wx.EXPAND)

            sizer.Add(sizer2, 0, wx.EXPAND)
            self.SetSizer(sizer)

            self.Bind(wx.EVT_SLIDER, self.OnSeek, self.slider)
            self.Bind(wx.EVT_BUTTON, self.OnPlay, self.play)
            self.Bind(wx.EVT_BUTTON, self.OnStop, self.stop)
            self.Bind(wx.EVT_BUTTON, self.OnPause, self.pause)
            self.Bind(wx.EVT_SLIDER, self.OnVolume, self.volume)
            self.Bind(wx.media.EVT_MEDIA_LOADED, self.OnMediaLoaded)

            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.OnTimer)
            self.timer.Start(100)

        def Open(self, file):
            if self.media.Load(file):
                self.media.SetInitialSize()
                self.slider.SetRange(0, self.media.Length())

        def OnMediaLoaded(self, event):
            pass

        def OnSeek(self, event):
            self.media.Seek(self.slider.GetValue())

        def OnVolume(self, event):
            self.media.SetVolume(self.volume.GetValue() / 10.0)

        def OnPlay(self, event):
            if self.media.Play():
                self.media.SetInitialSize()
                self.slider.SetRange(0, self.media.Length())

        def OnStop(self, event):
            self.media.Stop()

        def OnPause(self, event):
            self.media.Pause()

        def OnTimer(self, event):
            self.slider.SetValue(self.media.Tell())
