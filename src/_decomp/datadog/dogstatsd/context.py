#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\dogstatsd\context.py
from functools import wraps
from time import time
from datadog.util.compat import is_higher_py35, iscoroutinefunction
if is_higher_py35():
    from datadog.dogstatsd.context_async import _get_wrapped_co
else:

    def _get_wrapped_co(self, func):
        raise NotImplementedError(u'Decorator `timed` compatibility with coroutine functions requires Python 3.5 or higher.')


class TimedContextManagerDecorator(object):

    def __init__(self, statsd, metric = None, tags = None, sample_rate = 1, use_ms = None):
        self.statsd = statsd
        self.metric = metric
        self.tags = tags
        self.sample_rate = sample_rate
        self.use_ms = use_ms
        self.elapsed = None

    def __call__(self, func):
        if not self.metric:
            self.metric = '%s.%s' % (func.__module__, func.__name__)
        if iscoroutinefunction(func):
            return _get_wrapped_co(self, func)

        @wraps(func)
        def wrapped(*args, **kwargs):
            start = time()
            try:
                return func(*args, **kwargs)
            finally:
                self._send(start)

        return wrapped

    def __enter__(self):
        if not self.metric:
            raise TypeError('Cannot used timed without a metric!')
        self.start = time()
        return self

    def __exit__(self, type, value, traceback):
        self._send(self.start)

    def _send(self, start):
        elapsed = time() - start
        use_ms = self.use_ms if self.use_ms is not None else self.statsd.use_ms
        elapsed = int(round(1000 * elapsed)) if use_ms else elapsed
        self.statsd.timing(self.metric, elapsed, self.tags, self.sample_rate)
        self.elapsed = elapsed

    def start(self):
        self.__enter__()

    def stop(self):
        self.__exit__(None, None, None)
