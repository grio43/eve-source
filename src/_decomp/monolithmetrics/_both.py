#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithmetrics\_both.py
import _statsd
import _prometheus
from monolithconfig import on_client

def gauge(metric, value, tags = None, sample_rate = 1):
    if on_client():
        return
    _statsd.gauge(metric, value, tags=tags, sample_rate=sample_rate)
    _prometheus.gauge(metric, value, tags=tags)


def increment(metric, value = 1, tags = None, sample_rate = 1):
    if on_client():
        return
    _statsd.increment(metric, value, tags=tags, sample_rate=sample_rate)
    _prometheus.increment(metric, value, tags=tags)


def decrement(metric, value = 1, tags = None, sample_rate = 1):
    if on_client():
        return
    _statsd.decrement(metric, value, tags=tags, sample_rate=sample_rate)


def histogram(metric, value, tags = None, sample_rate = 1, buckets = None):
    if on_client():
        return
    _statsd.histogram(metric, value, tags=tags, sample_rate=sample_rate)
    _prometheus.histogram(metric, value, tags=tags, buckets=buckets)


def timing(metric, value, tags = None, sample_rate = 1, buckets = None):
    if on_client():
        return
    _statsd.timing(metric, value, tags=tags, sample_rate=sample_rate)
    _prometheus.histogram(metric, value, tags=tags, buckets=buckets)


def event(title, text = '', tags = None):
    if on_client():
        return
    _statsd.event(title, text=text, tags=tags)
    _prometheus.event(title, text=text, tags=tags)


def flush():
    if on_client():
        return
    _statsd.flush()
