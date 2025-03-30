#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\geo2\__init__.py
import blue
import sys
try:
    from _geo2_stub import *
except ImportError:
    pass

sys.modules[__name__] = blue.LoadExtension('_geo2')
