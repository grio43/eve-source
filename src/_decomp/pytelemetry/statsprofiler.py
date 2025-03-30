#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pytelemetry\statsprofiler.py
import blue
import sys
import warnings

class StatisticsProfiler(object):

    def __init__(self):
        warnings.warn('StatisticsProfiler is deprecated. Use blue.statistics.isPythonCaptureEnabled to capture Pyton profile', DeprecationWarning)

    def trace_dispatch_call(self, frame, arg):
        fcode = frame.f_code
        fn = '%s:%d %s' % (fcode.co_filename, fcode.co_firstlineno, fcode.co_name)
        blue.statistics.EnterZone(fn)

    def trace_dispatch_c_call(self, frame, arg):
        blue.statistics.EnterZone(arg.__name__)

    def trace_dispatch_return(self, frame, t):
        blue.statistics.LeaveZone()

    dispatch = {'call': trace_dispatch_call,
     'exception': trace_dispatch_return,
     'return': trace_dispatch_return,
     'c_call': trace_dispatch_c_call,
     'c_exception': trace_dispatch_return,
     'c_return': trace_dispatch_return}

    def dispatcher(self, frame, event, arg):
        self.dispatch[event](self, frame, arg)

    @classmethod
    def Start(cls):
        sys.setprofile(cls().dispatcher)

    @classmethod
    def Stop(cls):
        sys.setprofile(None)
