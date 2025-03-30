#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\util\timerstuff.py
import functools
import logging
import sys
import traceback
import weakref
import blue
import ccpProfile
import stackless
import uthread
from carbon.common.lib import const
log = logging.getLogger(__name__)
ClockThis = sys.ClockThis
ClockThisWithoutTheStars = sys.ClockThisWithoutTheStars

def TimeThis(timer):

    def Helper(func):

        @functools.wraps(func)
        def Wrapper(*args, **kwds):
            t = ccpProfile.PushTimer(timer)
            try:
                return func(*args, **kwds)
            finally:
                ccpProfile.PopTimer(t)

        return Wrapper

    return Helper


class SimpleTimingContext(object):

    def __enter__(self):
        c = stackless.getcurrent()
        self.t = (c.GetWallclockTime(), c.GetRunTime())

    def __exit__(self, exc_type, exc_value, exc_tb):
        a, b = self.t
        c = stackless.getcurrent()
        self.t = (c.GetWallclockTime() - a, c.GetRunTime() - b)

    def GetWallclockTime(self):
        return self.t[0]

    def GetRunTime(self):
        return self.t[1]


class TimerObject:

    def __init__(self, useSimTime = False):
        self.abort = 0
        self.id = 0
        self.aborts = {}
        if useSimTime:
            self.GetTime = blue.os.GetSimTime
            self.Sleep = blue.pyos.synchro.SleepSim
        else:
            self.GetTime = blue.os.GetWallclockTime
            self.Sleep = blue.pyos.synchro.SleepWallclock

    def __del__(self):
        self.abort = 1

    def DelayedCall(self, func, time, *args, **kw):
        self.id += 1
        callID = self.id
        if time - self.GetTime() > const.DAY * 2:
            raise RuntimeError('Cannot sleep for more than 48 hours')
        uthread.new(self.DelayedCall_thread, callID, func, time, args, kw, stackless_tracing_enabled=False)
        return callID

    def DelayedCall_thread(self, callID, func, time, args, kw):
        delay = (time - self.GetTime()) / 10000
        if delay > 0:
            self.Sleep(delay)
        if callID in self.aborts:
            del self.aborts[callID]
        elif not self.abort:
            try:
                func(*args, **kw)
            except:
                log.exception('Error in delayed call')

    def KillDelayedCall(self, id):
        self.aborts[id] = None

    def KillAllDelayedCalls(self):
        self.abort = 1


def OnTimerResync(old, new):
    diff = new - old
    for timer in AutoTimer.autoTimers.keys():
        timer.wakeupAt += diff / 10000


class AutoTimer(object):
    autoTimers = weakref.WeakKeyDictionary()
    __resync_handler_registered = False

    def __init__(self, interval, method, *args, **kw):
        if interval <= 0:
            raise RuntimeError('Invalid interval for AutoTimer')
        if not self.__resync_handler_registered:
            blue.pyos.synchro.timesyncs.append(OnTimerResync)
            self.__resync_handler_registered = True
        self.run = 1
        self.interval = interval
        self.method, self.args, self.kw = method, args, kw
        caller_tb = traceback.extract_stack(limit=2)[0:1]
        caller = traceback.format_list(caller_tb)[0].replace('\n', '')
        methrepr = getattr(method, '__name__', '(no __name__)').replace('<', '&lt;').replace('>', '&gt;')
        ctx = 'AutoTimer::(%s) on %s' % (caller, methrepr)
        self.wakeupAt = blue.os.GetWallclockTime() / 10000 + self.interval
        AutoTimer.autoTimers[self] = None
        uthread.pool(ctx, AutoTimer.Loop, weakref.ref(self), stackless_tracing_enabled=False)

    def KillTimer(self):
        self.run = 0

    def Reset(self, newInterval = None):
        if newInterval is not None:
            if newInterval <= 0:
                raise RuntimeError('Invalid interval for AutoTimer')
            self.interval = newInterval
        self.wakeupAt = blue.os.GetWallclockTime() / 10000 + self.interval

    def Loop(weakSelf):
        self = weakSelf()
        if not self or not self.run:
            return
        nap = self.interval
        del self
        while True:
            blue.pyos.synchro.SleepWallclock(nap)
            self = weakSelf()
            if not self or not self.run:
                return
            now = blue.os.GetWallclockTime() / 10000
            if now < self.wakeupAt:
                nap = self.wakeupAt - now
            else:
                self.method(*self.args, **self.kw)
                n = (now - self.wakeupAt) / self.interval
                self.wakeupAt += (n + 1) * self.interval
                nap = self.wakeupAt - now
            del self

    Loop = staticmethod(Loop)


class Stopwatch:

    def __init__(self):
        self.started = blue.os.GetCycles()[0]

    def __str__(self):
        return '%.3f' % ((blue.os.GetCycles()[0] - self.started) / float(blue.os.GetCycles()[1]))

    def Reset(self):
        self.started = blue.os.GetCycles()[0]
