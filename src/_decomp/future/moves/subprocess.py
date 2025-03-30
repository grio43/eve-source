#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\subprocess.py
from __future__ import absolute_import
from future.utils import PY2, PY26
from subprocess import *
if PY2:
    __future_module__ = True
    from commands import getoutput, getstatusoutput
if PY26:
    from future.backports.misc import check_output
