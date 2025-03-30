#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\tkinter\scrolledtext.py
from __future__ import absolute_import
from future.utils import PY3
if PY3:
    from tkinter.scrolledtext import *
else:
    try:
        from ScrolledText import *
    except ImportError:
        raise ImportError('The ScrolledText module is missing. Does your Py2 installation include tkinter?')
