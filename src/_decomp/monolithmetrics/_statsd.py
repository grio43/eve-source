#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithmetrics\_statsd.py
import logging
import monolithconfig
import _datadog
log = logging.getLogger('monolithmetrics._statsd')
aggregation_key = monolithconfig.get_value('clusterName', 'prefs') or 'Unknown'
running_client = monolithconfig.on_client()

def gauge(metric, value, tags = None, sample_rate = 1):
    if running_client:
        return
    try:
        _datadog.client.gauge(metric_name=metric, value=value, tags=tags, sample_rate=sample_rate)
    except Exception as e:
        msg = 'Gauge metric failed'
        log.error(msg, exc_info=1, extra={'metric': metric,
         'value': value,
         'tags': tags,
         'sample_rate': sample_rate})


def increment(metric, value = 1, tags = None, sample_rate = 1):
    if running_client:
        return
    try:
        _datadog.client.increment(metric_name=metric, value=value, tags=tags, sample_rate=sample_rate)
    except Exception as e:
        msg = 'Increment metric failed'
        log.error(msg, exc_info=1, extra={'metric': metric,
         'value': value,
         'tags': tags,
         'sample_rate': sample_rate})


def decrement(metric, value = 1, tags = None, sample_rate = 1):
    if running_client:
        return
    try:
        _datadog.client.decrement(metric_name=metric, value=value, tags=tags, sample_rate=sample_rate)
    except Exception as e:
        msg = 'Decrement metric failed'
        log.error(msg, exc_info=1, extra={'metric': metric,
         'value': value,
         'tags': tags,
         'sample_rate': sample_rate})


def histogram(metric, value, tags = None, sample_rate = 1):
    if running_client:
        return
    try:
        _datadog.client.histogram(metric_name=metric, value=value, tags=tags, sample_rate=sample_rate)
    except Exception as e:
        msg = 'Histogram metric failed'
        log.error(msg, exc_info=1, extra={'metric': metric,
         'value': value,
         'tags': tags,
         'sample_rate': sample_rate})


def timing(metric, value, tags = None, sample_rate = 1):
    if running_client:
        return
    try:
        _datadog.client.timing(metric_name=metric, value=value, tags=tags, sample_rate=sample_rate)
    except Exception as e:
        msg = 'Timing metric failed'
        log.error(msg, exc_info=1, extra={'metric': metric,
         'value': value,
         'tags': tags,
         'sample_rate': sample_rate})


def event(title, text = '', tags = None):
    if running_client:
        return
    try:
        _datadog.client.event(title=title, text=text, tags=tags, aggregation_key=aggregation_key)
    except Exception as e:
        msg = 'Event metric failed'
        log.error(msg, exc_info=1, extra={'title': title,
         'text': text,
         'tags': tags})


def flush():
    if running_client:
        return
    try:
        _datadog.client.flush()
    except Exception as e:
        log.error('Manual flush failed')
