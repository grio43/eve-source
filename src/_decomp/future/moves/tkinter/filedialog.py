#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\tkinter\filedialog.py
from __future__ import absolute_import
from future.utils import PY3
if PY3:
    from tkinter.filedialog import *
else:
    try:
        from FileDialog import *
    except ImportError:
        raise ImportError('The FileDialog module is missing. Does your Py2 installation include tkinter?')

    try:
        from tkFileDialog import *
    except ImportError:
        raise ImportError('The tkFileDialog module is missing. Does your Py2 installation include tkinter?')
