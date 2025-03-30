#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\functoolsext\deco.py


def permacache(ignore_parameters = False):
    real_func = None
    if hasattr(ignore_parameters, '__call__'):
        real_func = ignore_parameters
        ignore_parameters = False
    cache = {}

    def inner(func):

        def innerer(*iargs, **ikwargs):
            if ignore_parameters:
                key = str(func)
            else:
                key = (str(iargs), str(ikwargs))
            if key not in cache:
                cache[key] = func(*iargs, **ikwargs)
            return cache[key]

        innerer.flush_permacache = lambda : cache.clear()
        return innerer

    if real_func:
        return inner(real_func)
    else:
        return inner


def lru_buffered_cache(max_size = 100):
    real_func = None
    if hasattr(max_size, '__call__'):
        real_func = max_size
        max_size = 100
    _max_size = max_size
    _cache_map = {}
    _access_list = []

    def inner(func):

        def innerer(*iargs, **ikwargs):
            key = (str(iargs), str(ikwargs))
            if key not in _cache_map:
                _cache_map[key] = func(*iargs, **ikwargs)
                _access_list.insert(0, key)
                while len(_cache_map) > _max_size:
                    _cache_map.pop(_access_list.pop(-1), None)

            else:
                if key in _access_list:
                    _access_list.remove(key)
                _access_list.insert(0, key)
            return _cache_map[key]

        return innerer

    if real_func:
        return inner(real_func)
    else:
        return inner
