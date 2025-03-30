#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\tkinter\tix.py
from __future__ import absolute_import
from future.utils import PY3
if PY3:
    from tkinter.tix import *
else:
    try:
        from Tix import *
    except ImportError:
        raise ImportError('The Tix module is missing. Does your Py2 installation include tkinter?')
