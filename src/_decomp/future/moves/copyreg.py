#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\copyreg.py
from __future__ import absolute_import
from future.utils import PY3
if PY3:
    import copyreg, sys
    sys.modules['future.moves.copyreg'] = copyreg
else:
    __future_module__ = True
    from copy_reg import *
