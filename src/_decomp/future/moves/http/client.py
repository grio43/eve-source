#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\http\client.py
from future.utils import PY3
if PY3:
    from http.client import *
else:
    from httplib import *
    from httplib import HTTPMessage
    __future_module__ = True
