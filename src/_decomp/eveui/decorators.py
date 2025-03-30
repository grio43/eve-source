#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\decorators.py
import functools
import weakref
import locks

def skip_if_destroyed(f):

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        self = args[0]
        if self.destroyed:
            return
        f(*args, **kwargs)

    return wrapper


class lazy(object):

    def __init__(self, func):
        self.func = func
        self._cache = weakref.WeakKeyDictionary()

    def __get__(self, obj, type = None):
        if obj is None:
            return self
        element = self._get_cached_element(obj)
        if not element or element.destroyed and not obj.destroyed:
            element = self.func(obj)
            self._cache[obj] = weakref.ref(element)
        return element

    def _get_cached_element(self, obj):
        if obj not in self._cache:
            return None
        element_ref = self._cache[obj]
        return element_ref()


def lock_and_set_pending():

    def Wrapper(func):
        runBoolName = 'locked_%s_running' % func.func_name
        pendingBoolName = 'locked_%s_pending' % func.func_name

        @functools.wraps(func)
        def FuncCalled(uiInstance):
            funcName = func.func_name
            lockName = '%s_%s' % (funcName, id(uiInstance))
            if is_destroyed(uiInstance):
                reset_variables(uiInstance)
                return
            if is_running(uiInstance) and is_pending(uiInstance):
                return
            set_pending_value(uiInstance, True)
            with locks.TempLock(lockName):
                if not is_pending(uiInstance) or is_destroyed(uiInstance):
                    reset_variables(uiInstance)
                    return
                set_pending_value(uiInstance, False)
                try:
                    set_running_value(uiInstance, True)
                    func(uiInstance)
                finally:
                    set_running_value(uiInstance, False)

        def is_destroyed(uiInstance):
            return getattr(uiInstance, 'destroyed', False)

        def set_running_value(uiInstance, value):
            setattr(uiInstance, runBoolName, value)

        def set_pending_value(uiInstance, value):
            setattr(uiInstance, pendingBoolName, value)

        def is_running(uiInstance):
            return getattr(uiInstance, runBoolName, False)

        def is_pending(uiInstance):
            return getattr(uiInstance, pendingBoolName, False)

        def reset_variables(uiInstance):
            set_running_value(uiInstance, False)
            set_pending_value(uiInstance, False)

        return FuncCalled

    return Wrapper
