#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\util\weakrefutil.py
import types
import weakref

def CallableWeakRef(function):
    if not callable(function):
        raise TypeError('Function must be callable.')
    if isinstance(function, types.FunctionType):
        return weakref.ref(function)
    if hasattr(function, 'im_self'):
        subref = weakref.ref(function.im_self)
        name = function.im_func.func_name
        ret = lambda : getattr(subref(), name, None)
    elif hasattr(function, '__inst__'):
        subref = weakref.ref(function.__inst__)
        name = function.__func__.func_name
        ret = lambda : getattr(subref(), name, None)
    elif hasattr(function, '__self__'):
        subref = weakref.ref(function.__self__)
        name = function.__name__
        ret = lambda : getattr(subref(), name, None)
    else:
        if type(function) == types.InstanceType:
            return weakref.ref(function)
        raise RuntimeError('%s not supported!' % type(function))
    ret.isWeakRef = 1
    return ret
