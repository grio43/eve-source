#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\videoplayer\__init__.py
import blue
import sys
try:
    from _videoplayer_stub import *
except ImportError:
    pass

videoplayer = blue.LoadExtension('_videoplayer')
for each in dir(videoplayer):
    globals()[each] = getattr(videoplayer, each)

del blue
del sys
del videoplayer
del each
