#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\destiny\__init__.py
import blue
import decometaclass
try:
    from _destiny_stub import *
except ImportError:
    pass

_destiny = blue.LoadExtension('_destiny')
_destiny.Ball = decometaclass.WrapBlueClass('destiny.Ball')
_destiny.Ballpark = decometaclass.WrapBlueClass('destiny.Ballpark')
_destiny.ClientBall = decometaclass.WrapBlueClass('destiny.ClientBall')
for memberName in dir(_destiny):
    if memberName in ('__name__', '__file__'):
        continue
    globals()[memberName] = getattr(_destiny, memberName)
