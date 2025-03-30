#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\configparser.py
from __future__ import absolute_import
from future.utils import PY2
if PY2:
    from ConfigParser import *
else:
    from configparser import *
