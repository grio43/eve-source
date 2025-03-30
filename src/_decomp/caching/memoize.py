#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\caching\memoize.py
import numbers, time
try:
    from locks import Lock
except ImportError:
    Lock = None

CACHE_FOREVER = 108000

def Memoize(minutes):
    cache_seconds = CACHE_FOREVER

    def deco(fn):
        _cache = _MemoizeCache(cache_seconds)

        def inner_deco(*args, **kwargs):
            key = _cache.make_key(*args, **kwargs)
            try:
                value = _cache.get_value_if_key_is_present_and_not_expired(key)
            except KeyError:
                value = fn(*args, **kwargs)
                _cache.store(key, value)

            return value

        inner_deco.clear_memoized = _cache.clear_cache
        return inner_deco

    if callable(minutes):
        return deco(minutes)
    if isinstance(minutes, numbers.Number):
        cache_seconds = minutes * 60
        return deco
    raise ValueError("Wrong usage of 'Memoized' decorator. Either use no arguments or specify a number of minutes.")


def MemoizeWithLock(minutes):
    if Lock is None:
        raise RuntimeError('MemoizeWithLock requires a Stackless execution environment')
    cache_seconds = CACHE_FOREVER

    def deco(fn):
        _cache = _MemoizeCache(cache_seconds)
        _lock = Lock('MemoizeWithLock._lock %s' % fn)

        def inner_deco_with_lock(*args, **kwargs):
            key = _cache.make_key(*args, **kwargs)
            try:
                value = _cache.get_value_if_key_is_present_and_not_expired(key)
            except KeyError:
                with _lock:
                    try:
                        value = _cache.get_value_if_key_is_present_and_not_expired(key)
                    except KeyError:
                        value = fn(*args, **kwargs)
                        _cache.store(key, value)

            return value

        inner_deco_with_lock.clear_memoized = _cache.clear_cache
        return inner_deco_with_lock

    if callable(minutes):
        return deco(minutes)
    if isinstance(minutes, numbers.Number):
        cache_seconds = minutes * 60
        return deco
    raise ValueError("Wrong usage of 'MemoizeWithLock' decorator. Either use no arguments or specify a number of minutes.")


class _MemoizeCache(object):

    def __init__(self, cache_seconds):
        self._cache = {}
        self._cache_seconds = cache_seconds

    @staticmethod
    def make_key(*args, **kwargs):
        hargs = []
        for a in args:
            if getattr(a, '__hash__', None):
                hargs.append(a)
            elif hasattr(a, 'iteritems'):
                hargs.append(frozenset(a.iteritems()))
            else:
                hargs.append(tuple(a) if hasattr(a, '__iter__') else repr(a))

        return (tuple(hargs) if hargs else None, frozenset(kwargs.iteritems()) if kwargs else None)

    def get_value_if_key_is_present_and_not_expired(self, key):
        value, saved_time = self._cache[key]
        if saved_time + self._cache_seconds < time.time():
            raise KeyError
        return value

    def store(self, key, value):
        saved_time = time.time()
        self._cache[key] = (value, saved_time)

    def clear_cache(self, *args, **kwargs):
        if not args and not kwargs:
            self._cache.clear()
        else:
            try:
                del self._cache[self.make_key(*args, **kwargs)]
            except KeyError:
                pass
