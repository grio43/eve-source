#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithmetrics\_prometheus.py
import re
import sys
import logging
from monolithconfig import on_client
prometheus_client = None
prometheus_registry = None
prometheus_port = 0
logger = logging.getLogger(__name__)
metric_name_regex = re.compile('[^a-zA-Z0-9_:]')
label_name_regex = re.compile('[^a-zA-Z0-9_]')
_declared_metrics = {}

def ugly_unittest_import_hack():
    import blue
    import imp
    import os
    import platform
    platform_name = 'Windows' if platform.system() == 'Windows' else 'macOS'
    platform_arch = 'universal' if platform.system() == 'Darwin' else 'x64'
    platform_toolset = 'v141' if platform.system() == 'Windows' else 'AppleClang'
    module_name = 'prometheus_module.so' if platform.system() == 'Darwin' else 'prometheus_module.pyd'
    module_path = os.path.join(blue.paths.ResolvePath(u'root:/'), '..', 'vendor', 'CCP', 'eve-monolith-prometheus', 'd419815d2f41bef32ecd342f7e6c9fee1a8f475f', 'bin', platform_name, platform_arch, platform_toolset, module_name)
    return imp.load_dynamic('prometheus_module', module_path)


if not on_client():
    try:
        import prometheus_module
        prometheus_client = prometheus_module
    except ImportError:
        prometheus_client = ugly_unittest_import_hack()

    prometheus_registry = prometheus_client.MetricRegistry()
    for i in range(9100, 10000):
        serving = prometheus_registry.Serve(str(i))
        if serving:
            prometheus_port = i
            break

    if prometheus_port == 0:
        msg = 'Prometheus client failed to open a port'
        logger.error(msg)
        print msg
    else:
        msg = 'Prometheus client available on port {}'.format(prometheus_port)
        logger.info(msg)
        print msg

def _format_metric_name(metric):
    return metric_name_regex.sub('_', metric)


def _format_label_name(tag):
    return label_name_regex.sub('_', tag)


def _tags_to_label_dict(tags):
    result = {}
    if tags:
        for tag in tags:
            split = tag.split(':')
            name = split[0]
            name = _format_label_name(name)
            result[name] = split[1]

    return result


def _get_metric_hash(metric, labels = None):
    keys = [ label for sublist in labels.keys() for label in sublist ]
    keys.append(metric)
    keys.sort()
    return hash(frozenset(keys))


def _get_prometheus_data(metric, tags):
    labels = _tags_to_label_dict(tags)
    metric_id = _get_metric_hash(metric, labels)
    name = _format_metric_name(metric)
    return (metric_id, name, labels)


def gauge(metric, value, tags = None):
    if not prometheus_client:
        return
    try:
        metric_id, name, labels = _get_prometheus_data(metric, tags)
        if metric_id not in _declared_metrics:
            new_gauge = prometheus_registry.MakeGauge(name, labels=labels.keys())
            _declared_metrics[metric_id] = new_gauge
        prom_gauge = _declared_metrics[metric_id]
        prom_gauge.WithLabelValues(labels).Set(value)
    except Exception:
        logger.error('[prom] gauge metric failed', exc_info=sys.exc_info(), extra={'metric': metric,
         'value': value,
         'tags': tags})


def increment(metric, value = 1, tags = None):
    if not prometheus_client:
        return
    try:
        metric_id, name, labels = _get_prometheus_data(metric, tags)
        if metric_id not in _declared_metrics:
            new_counter = prometheus_registry.MakeCounter(name, labels=labels.keys())
            _declared_metrics[metric_id] = new_counter
        prom_counter = _declared_metrics[metric_id]
        prom_counter.WithLabelValues(labels).Increment(value)
    except Exception:
        logger.error('[prom] counter metric failed', exc_info=sys.exc_info(), extra={'metric': metric,
         'value': value,
         'tags': tags})


def histogram(metric, value, tags = None, buckets = None):
    if not prometheus_client:
        return
    try:
        metric_id, name, labels = _get_prometheus_data(metric, tags)
        if metric_id not in _declared_metrics:
            new_histogram = prometheus_registry.MakeHistogram(name, labels=labels.keys(), boundaries=list(buckets) or [0.1,
             0.5,
             1.0,
             10.0])
            _declared_metrics[metric_id] = new_histogram
        prom_histogram = _declared_metrics[metric_id]
        prom_histogram.WithLabelValues(labels).Observe(value)
    except Exception:
        logger.error('[prom] histogram metric failed', exc_info=sys.exc_info(), extra={'metric': metric,
         'value': value,
         'tags': tags})


def event(title, text = '', tags = None):
    pass
