#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uthread2\debounce.py
import functools
import time
import types
import weakref
import uthread2

def debounce(wait = 1.0, leading = False, trailing = True, max_wait = None):
    func = None
    if callable(wait):
        func = wait
        wait = 1.0
    if wait < 0:
        raise ValueError('Wait must be positive')
    if max_wait is not None and wait > max_wait:
        raise ValueError('Wait is greater than max_wait')
    if max_wait is not None and max_wait < 0:
        raise ValueError('max_wait must be None or positive')
    if not leading and not trailing:
        raise ValueError('Either leading or trailing must be True')

    def deco(f):
        return Debounce(f, wait, leading, trailing, max_wait)

    if func is None:
        return deco
    return deco(func)


class Debounce(object):

    def __init__(self, func, wait, leading, trailing, max_wait):
        self._configuration = DebounceConfiguration(func, wait, leading, trailing, max_wait)
        self._state = None
        self._state_by_obj = weakref.WeakKeyDictionary()
        if hasattr(func, '__doc__'):
            self.__doc__ = func.__doc__

    def cancel(self):
        if self._state:
            self._state.cancel()

    def flush(self):
        if self._state:
            self._state.flush()

    def __call__(self, *args, **kwargs):
        if self._state is None:
            self._state = DebounceState(self._configuration)
        self._state(*args, **kwargs)

    def __get__(self, obj, obj_type):
        if obj is None:
            return self
        if obj not in self._state_by_obj:
            self._state_by_obj[obj] = DebounceState(self._configuration)
        return self._create_wrapper(obj, obj_type, self._state_by_obj[obj])

    def _create_wrapper(self, obj, obj_type, state):
        if state.call_wrapper is None:
            state_ref = weakref.ref(state)

            @functools.wraps(self._configuration.func)
            def wrapper(*args, **kwargs):
                _state = state_ref()
                if _state:
                    _state(*args, **kwargs)

            def cancel():
                _state = state_ref()
                if _state:
                    _state.cancel()

            def flush():
                _state = state_ref()
                if _state:
                    _state.flush()

            wrapper.cancel = cancel
            wrapper.flush = flush
            state.call_wrapper = wrapper
        return types.MethodType(state.call_wrapper, obj, obj_type)


class DebounceConfiguration(object):

    def __init__(self, func, wait, leading, trailing, max_wait):
        self.func = func
        self.wait = wait
        self.leading = leading
        self.trailing = trailing
        self.max_wait = max_wait


class DebounceState(object):

    def __init__(self, configuration):
        self.configuration = configuration
        self.last_invoke_time = None
        self.next_call_args = None
        self.wait_tasklet = None
        self.cancel_token = None
        self.call_wrapper = None

    def reset(self):
        self.last_invoke_time = None
        self.next_call_args = None
        self.wait_tasklet = None
        self.cancel_token = None

    def cancel(self):
        if self.cancel_token is not None:
            self.cancel_token.set()
            self.reset()

    def flush(self):
        call_args = self.next_call_args
        self.cancel()
        if call_args is not None:
            args, kwargs = call_args
            self.configuration.func(*args, **kwargs)

    def start_wait_tasklet(self):
        start_time = time.time()
        self.cancel_token = Token()
        self.wait_tasklet = uthread2.start_tasklet(self.wait_tasklet_func, start_time, self.cancel_token)

    def invoke(self):
        if self.next_call_args is None:
            return
        args, kwargs = self.next_call_args
        self.next_call_args = None
        self.last_invoke_time = time.time()
        self.configuration.func(*args, **kwargs)

    def wait_tasklet_func(self, start_time, cancel_token):
        try:
            while True:
                wait = self.remaining_wait(start_time)
                if wait <= 0 or cancel_token.is_set:
                    break
                uthread2.sleep(wait)

            if self.configuration.trailing and not cancel_token.is_set:
                self.invoke()
        finally:
            if not cancel_token.is_set:
                self.reset()

    def remaining_wait(self, start_time):
        now = time.time()
        wait = self.configuration.wait
        if self.last_invoke_time is not None:
            wait -= now - self.last_invoke_time
        if self.configuration.max_wait:
            wait = min(wait, self.configuration.max_wait - (now - start_time))
        return wait

    def __call__(self, *args, **kwargs):
        self.next_call_args = (args, kwargs)
        self.last_invoke_time = time.time()
        is_waiting = self.wait_tasklet is not None
        if not is_waiting:
            self.start_wait_tasklet()
        if self.configuration.leading and not is_waiting:
            self.invoke()


class Token(object):

    def __init__(self):
        self._is_set = False

    @property
    def is_set(self):
        return self._is_set

    def set(self):
        self._is_set = True
