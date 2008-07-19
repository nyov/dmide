''' DMIDE '''

if __name__ == '__main__':
	try:
		import wx
		import core.window

		app = wx.App(0)
		w = core.window.Window('DMIDE')
		w.Show(True)
		app.MainLoop()

	except Exception, e:
		import traceback
		open('dmide.log', 'a').write(traceback.format_exc())
