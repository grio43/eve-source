#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\brennivin\compat.py
import sys
import threading
if sys.version_info[0] > 2:
    PY3K = True
    long = int
    StringTypes = (str,)

    def reraise(e, v, tb):
        raise e(v).with_traceback(tb)


    TimerCls = threading.Timer
    xrange = range
    from io import StringIO
else:
    PY3K = False
    long = long
    from types import StringTypes
    exec 'def reraise(e, v, tb):\n    raise e, v, tb'
    TimerCls = threading._Timer
    xrange = xrange
    from cStringIO import StringIO
