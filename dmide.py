#-------------------------------------------------------------------

if __name__ == '__main__':

	try:

		# if possible, optimize with psyco
		try:
			import psyco
			psyco.full()
		except ImportError:
			pass

		#-------------------------------------------------------------------

		# all the goodies are in here
		from core import *

		#-------------------------------------------------------------------

		# create the app and window, and initialize the art factory
		app = wx.App(0)
		app.dm_art = DMArtFactory()

		#-------------------------------------------------------------------

		def get_dir():
			""" Get the dir DMIDE is in. """

			if hasattr(sys, 'frozen'): return sys.executable
			return sys.argv[0]

		#-------------------------------------------------------------------

		app.get_dir = get_dir
		w = DMWindow('DMIDE')
		app.MainLoop()

#-------------------------------------------------------------------

	except Exception:

		# errors :(
		import traceback
		error = traceback.format_exc()
		open('ERRORS.txt', 'w').write(error)

		wx.MessageBox( error, 'DMIDE Fatal Error')

#-------------------------------------------------------------------