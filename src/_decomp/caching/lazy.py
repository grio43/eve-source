#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\caching\lazy.py


class lazy_property(object):

    def __init__(self, func, name = None, doc = None):
        self.__name__ = name or func.__name__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type = None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _MISSING)
        if value is _MISSING:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


class _Missing(object):
    _singleton = None

    def __new__(cls):
        if _Missing._singleton is None:
            _Missing._singleton = super(_Missing, cls).__new__(cls)
        return _Missing._singleton

    def __repr__(self):
        return 'missing'


_MISSING = _Missing()
