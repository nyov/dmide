from distutils.core import setup
import py2exe

setup(
	windows=[{
		'script':'dmide.py',
		'icon_resources':[(1,'icon/dm.ico')]
		}],
	data_files=[('',['gdiplus.dll'])],
	)
