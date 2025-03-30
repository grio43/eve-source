#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\http\cookies.py
from __future__ import absolute_import
from future.utils import PY3
if PY3:
    from http.cookies import *
else:
    __future_module__ = True
    from Cookie import *
    from Cookie import Morsel
