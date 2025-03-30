#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\tkinter\constants.py
from __future__ import absolute_import
from future.utils import PY3
if PY3:
    from tkinter.constants import *
else:
    try:
        from Tkconstants import *
    except ImportError:
        raise ImportError('The Tkconstants module is missing. Does your Py2 installation include tkinter?')
