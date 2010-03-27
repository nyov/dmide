""" DMIDE by Crashed. """


if __name__ == '__main__':

	try:

		# if possible, optimize with psyco
		try:
			import psyco
			psyco.full()
		except ImportError:
			pass

		# all the goodies are in here
		from core import sys, os, wx, DMIDE_Window, DMIDE_ArtFactory

		# create the app and window, and initialize the art factory
		app = wx.App(0)

		def get_dir():
			""" Get the dir DMIDE is in. """

			if hasattr(sys, 'frozen'): return os.path.split(sys.executable)[0]
			return os.path.split(sys.argv[0])[0]

		app.get_dir = get_dir
		app.art = DMIDE_ArtFactory()
		w = DMIDE_Window('DMIDE')
		#wx.CallLater(1000, w.dmide_filetree.Open, 'C:\\Documents and Settings\\Crashed\\Desktop\\crashrpg\\crashrpg.dme')
		#w.dmide_filetree.Open('C:\\Documents and Settings\\Crashed\\Desktop\\EvilResidentsOld\\EvilResidents.dme')
		app.MainLoop()

	except Exception:

		# errors :(
		import traceback
		error = traceback.format_exc()
		open('ERRORS.log', 'w').write(error)
		traceback.print_exc()
