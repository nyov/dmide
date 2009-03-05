import zlib
import base64
import os


for img in os.listdir('.'):
    if os.path.isfile(img) and os.path.splitext(img)[-1] == '.png':
        print 'converting %s' % img
        fp = open(img, 'rb')
        x = base64.b64encode(zlib.compress(fp.read()))
        fp.close()

        fp = open(os.path.splitext(img)[0] + '.txt', 'w')
        fp.write(x)
        fp.close()