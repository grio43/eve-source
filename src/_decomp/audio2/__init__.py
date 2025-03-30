#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\audio2\__init__.py
import blue
import sys
try:
    from _audio2_stub import *
except ImportError:
    pass

audio2 = blue.LoadExtension('_audio2')
for memberName in dir(audio2):
    globals()[memberName] = getattr(audio2, memberName)

del audio2
