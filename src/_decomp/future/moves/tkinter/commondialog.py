#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\tkinter\commondialog.py
from __future__ import absolute_import
from future.utils import PY3
if PY3:
    from tkinter.commondialog import *
else:
    try:
        from tkCommonDialog import *
    except ImportError:
        raise ImportError('The tkCommonDialog module is missing. Does your Py2 installation include tkinter?')
