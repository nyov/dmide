import sys
import os
import pstats
import cProfile
import time


def run():
    from core import sys, os, wx, DMIDE_Window, DMIDE_ArtFactory

    app = wx.App(0)

    def get_dir():
        """ Get the dir DMIDE is in. """

        if hasattr(sys, 'frozen'): return os.path.split(sys.executable)[0]
        return os.path.split(os.path.abspath(sys.argv[0]))[0]

    app.get_dir = get_dir
    app.art = DMIDE_ArtFactory()
    w = DMIDE_Window('DMIDE')
    #wx.CallAfter(app.Exit)
    app.MainLoop()


start = time.time()
cProfile.run('run()', 'profile')
end = time.time()

print 'total time: %0.3fs' % (end-start)

sys.stdout = open('profile.txt', 'w')

p = pstats.Stats('profile')
p.strip_dirs().sort_stats('time', 'calls').print_stats()

os.remove('profile')
