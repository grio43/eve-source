#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\tkinter\simpledialog.py
from __future__ import absolute_import
from future.utils import PY3
if PY3:
    from tkinter.simpledialog import *
else:
    try:
        from SimpleDialog import *
    except ImportError:
        raise ImportError('The SimpleDialog module is missing. Does your Py2 installation include tkinter?')
