DMIDE (DreamMaker IDE)

About dmide
-------------------------------------------------------------------------------

dmide is a multiplatform open source IDE for [BYOND].

(The original googlecode project can be found [here](https://code.google.com/p/dmide/).)

It is written in Python and using the wxPython GUI toolkit.
Unlike the original BYOND Dream Maker, it is not limited to Windows and also
works on Linux and possibly FreeBSD, MacOS X and others.

Running dmide
-------------------------------------------------------------------------------

dmide is a python project, the base requirements are python (2.6 should work)
and wxPython.

Then simply executing the main python file should get you runnning.
No fancy installer exists. Copy it where needed.

Note: dmide still requires the original BYOND binaries for your platform,
in particular the DreamMaker command line compiler, which can be found at
http://www.byond.com/download/.
Currently dmide looks for them in hardcoded paths at /usr/local/byond/bin or
C:\\Program Files\\BYOND\\bin -- search and replace them to your needs (ugh).

Also note that the BYOND binaries are only available for 32bit systems at
this time, so on 64bit posix platforms, some 32bit libraries need to be
available (on debian or derivatives use multi-arch).

State of the software
-------------------------------------------------------------------------------

Development has been abandoned or on hold for quite some time.
Code quality is not especially great and there are known bugs and missing
features.
Using dmide as anything more than a plain code editor is currently not
recommended (editing map files, compiling projects), unless you
know what you're doing and can fix the code when it breaks for your project.

It is still a great tool to visualize maps and view a projects object tree.

(This repository here does not constitute a renewed development effort --
unless you help make that happen or would like to pay for it. It only exists
to share some bugfixes. Feel free to work on it and send patches, though.)

License
-------------------------------------------------------------------------------

This software is licensed under the New BSD License,
unless where noted otherwise.

The software contains the AGW library and uses the wxPython GUI toolkit,
both of which are licensed under the wxPython license.


[BYOND]: http://www.byond.com/
