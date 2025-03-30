#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\urllib\response.py
from future import standard_library
from future.utils import PY3
if PY3:
    from urllib.response import *
else:
    __future_module__ = True
    with standard_library.suspend_hooks():
        from urllib import addbase, addclosehook, addinfo, addinfourl
