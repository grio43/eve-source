#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\tkinter\ttk.py
from __future__ import absolute_import
from future.utils import PY3
if PY3:
    from tkinter.ttk import *
else:
    try:
        from ttk import *
    except ImportError:
        raise ImportError('The ttk module is missing. Does your Py2 installation include tkinter?')
