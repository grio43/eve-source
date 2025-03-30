#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\threadutils\highlander.py
import functools
import types
import weakref
import uthread2

def highlander_threaded(f):
    return HighlanderThreadWrapper(f)


class HighlanderThreadWrapper(object):

    def __init__(self, func):
        self.func = func
        self._thread_store = weakref.WeakKeyDictionary()

    def kill_thread_maybe(self):
        return self._kill_thread_maybe(self.func)

    def join(self):
        self._join(self.func)

    def __call__(self, *args, **kwargs):
        self._kill_thread_maybe(self.func)
        self._thread_store[self.func] = self._inner_call(*args, **kwargs)

    def __get__(self, instance, owner):
        if instance is None:
            return self

        @functools.wraps(self.func)
        def wrapper(_instance, *args, **kwargs):
            self._kill_thread_maybe(_instance)
            self._thread_store[_instance] = self._inner_call(_instance, *args, **kwargs)

        def kill_thread_maybe():
            return self._kill_thread_maybe(instance)

        def join():
            self._join(instance)

        setattr(wrapper, 'kill_thread_maybe', kill_thread_maybe)
        setattr(wrapper, 'join', join)
        bound_wrapper = types.MethodType(wrapper, instance, instance.__class__)
        setattr(instance, self.func.__name__, bound_wrapper)
        return bound_wrapper

    def _inner_call(self, *args, **kwargs):
        return uthread2.start_tasklet(self.func, *args, **kwargs)

    def _kill_thread_maybe(self, key):
        if key in self._thread_store:
            uthread2.start_tasklet(self._thread_store[key].kill)
            return True
        return False

    def _join(self, key):
        if key in self._thread_store:
            self._thread_store[key].get()
