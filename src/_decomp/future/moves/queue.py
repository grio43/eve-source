#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\queue.py
from __future__ import absolute_import
from future.utils import PY3
if PY3:
    from queue import *
else:
    __future_module__ = True
    from Queue import *
