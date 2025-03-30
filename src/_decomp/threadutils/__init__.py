#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\threadutils\__init__.py
import functools
import threading
import time
import types
import warnings
from brennivin.threadutils import *
from brennivin.threadutils import ChunkIter as _ChunkIter
from brennivin.threadutils import Token as _Token
from threadutils.be_nice import be_nice, be_nice_iter
from threadutils.highlander import highlander_threaded
import uthread2 as uthread

class ChunkIter(_ChunkIter):

    @classmethod
    def start_thread(cls, target, name):
        try:
            import blue, stacklesslib.replacements.threading
            cls.threading = stacklesslib.replacements.threading
            cls.sleep = lambda sec: blue.synchro.Sleep(sec * 1000)
            cls.benice = blue.pyos.BeNice
        except ImportError:
            cls.threading = threading
            cls.benice = lambda : None

        thread = cls.threading.Thread(target=target, name=name)
        thread.daemon = True
        thread.start()
        return thread


class SimpleSignal(Signal):

    def __init__(self, *args, **kwargs):
        super(SimpleSignal, self).__init__(*args, **kwargs)
        warnings.warn('SimpleSignal is deprecated, use Signal instead.', DeprecationWarning)

    Connect = Signal.connect
    Disconnect = Signal.disconnect
    Emit = Signal.emit


class Token(_Token):

    def __init__(self):
        super(Token, self).__init__()
        self.Set = self.set
        self.IsSet = self.is_set


class throttle(object):

    def __init__(self, f, interval_seconds, time_func = None):
        self.f = f
        self.wait_seconds = interval_seconds
        self.time_since_step = 0.0
        self.next_call = None
        self.next_call_args = None
        self.next_call_kwargs = None
        self._init_time_func(time_func)

    def _init_time_func(self, time_func):
        if time_func is None:
            self.time_func = time.time
        else:
            self.time_func = time_func

    def trigger_next_call_if_exists(self):
        uthread.sleep(self.wait_seconds)
        if self.next_call is not None:
            self.next_call(*self.next_call_args, **self.next_call_kwargs)
            self.next_call = None
            self.next_call_args = None
            self.next_call_kwargs = None

    def __call__(self, *args, **kwargs):
        dt = self.time_func() - self.time_since_step
        if dt > self.wait_seconds:
            self.time_since_step = 0.0
        if self.time_since_step == 0.0:
            self.time_since_step = self.time_func()
            self.f(*args, **kwargs)
            uthread.start_tasklet(self.trigger_next_call_if_exists)
            return
        self.next_call = self.f
        self.next_call_args = args
        self.next_call_kwargs = kwargs

    def __get__(self, instance, owner):
        if instance is None:
            return self

        @functools.wraps(self.f)
        def wrapper(*args, **kwargs):
            return self.__call__(*args, **kwargs)

        bound_wrapper = types.MethodType(wrapper, instance, instance.__class__)
        setattr(instance, self.f.__name__, bound_wrapper)
        return bound_wrapper


Throttle = throttle

def throttled(interval_seconds, **kwargs):

    def deco(func):
        return throttle(func, interval_seconds, **kwargs)

    return deco


Throttled = throttled

def threaded(f):

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return uthread.start_tasklet(f, *args, **kwargs)

    return wrapper


def be_nice_every(interval = 100, sequence = None):
    for i, item in enumerate(sequence):
        if (i + 1) % interval == 0:
            BeNice()
        yield item


try:
    import multiprocessing.pool
    _threadpool = multiprocessing.pool.ThreadPool()

    def PMapMaybe(func, iterable):
        return _threadpool.map(func, iterable)


except ImportError:
    PMapMaybe = map

TimeoutJoin = join_timeout
Memoize = memoize
ExpiringMemoize = expiring_memoize
BeNice = be_nice
