#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacemouse\__init__.py
import blue
import sys
try:
    from _spacemouse_stub import *
except ImportError:
    pass

sys.modules[__name__] = blue.LoadExtension('_spacemouse')
