#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uthread2\callthrottlers.py
from . import sleep, start_tasklet

class CallCombiner(object):

    def __init__(self, func, throttleTime):
        self.isBeingCalled = set()
        self.func = func
        self.throttleTime = throttleTime

    def __call__(self, *args, **kwargs):
        key = (args, frozenset(kwargs.iteritems()))
        if key in self.isBeingCalled:
            return
        self.isBeingCalled.add(key)
        try:
            sleep(self.throttleTime)
            return self.func(*args, **kwargs)
        finally:
            self.isBeingCalled.remove(key)


class NonBlockingCallCombiner(CallCombiner):

    def __call__(self, *args, **kwargs):
        start_tasklet(super(NonBlockingCallCombiner, self).__call__, *args, **kwargs)


def BufferedCall(delay = 1000):

    def BufferedCallDecorator(method):
        buffering = set()

        def BufferedCallThread(key, *args, **kwargs):
            try:
                sleep(delay / 1000.0)
                method(*args, **kwargs)
            finally:
                buffering.remove(key)

        def BufferedCallWrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.iteritems()))
            if key not in buffering:
                buffering.add(key)
                start_tasklet(BufferedCallThread, key, *args, **kwargs)

        return BufferedCallWrapper

    if callable(delay):
        return BufferedCallDecorator(delay)
    return BufferedCallDecorator
