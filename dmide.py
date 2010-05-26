#!/usr/bin/env python
""" DMIDE by Crashed. """


if __name__ == '__main__':

	try:

		# if possible, optimize with psyco
		try:
			#import psyco
			#psyco.full()
			print 'Optimizing with psyco'
		except ImportError:
			pass

		# all the goodies are in here
		from core import sys, os, wx, DMIDE_Window, DMIDE_ArtFactory

		# create the app and window, and initialize the art factory
		app = wx.App(0)

		def get_dir():
			""" Get the dir DMIDE is in. """

			if hasattr(sys, 'frozen'): return os.path.split(sys.executable)[0]
			return os.path.split(os.path.abspath(sys.argv[0]))[0]

		def get_byond():
			""" Get the dir the BYOND bin is in """

			typical_paths = ['C:\\Program Files\\BYOND\\bin', 'C:\\Program Files (x86)\\BYOND\\bin',
							 ]

		app.get_dir = get_dir
		app.art = DMIDE_ArtFactory()

		print 'DMIDE dir:', get_dir()

		w = DMIDE_Window('DMIDE')
		app.MainLoop()

	except Exception:

		# errors :(
		import traceback
		error = traceback.format_exc()
		open('ERRORS.log', 'w').write(error)
		traceback.print_exc()
