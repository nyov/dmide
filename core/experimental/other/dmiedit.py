import wx

class Test(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
 
        self.Bind(wx.EVT_PAINT, self.OnPaint)
 
    def OnPaint(self, event):
        pdc = wx.PaintDC(self)
        test_bg = wx.BitmapFromImage(wx.Image('bg.png').Rescale(256, 256))
        test_img = wx.BitmapFromImage(wx.Image('example.png').Rescale(256, 256))

        m = wx.MemoryDC()
        m.SelectObject(test_img)
        dc = wx.GCDC(m)
        dc.DrawLine(0, 0, 256, 256)

        del m

        pdc.SetPen(wx.BLACK_PEN)
        pdc.DrawBitmap(test_bg, 0, 0)
        pdc.DrawBitmap(test_img, 0, 0, True)
 
 
 
if __name__ == '__main__':
    app = wx.App(0)
 
    win = wx.Frame(None)
    win.Show(True)
 
    panel = Test(win)
 
    win.SetSize((300, 300))
 
    app.MainLoop()