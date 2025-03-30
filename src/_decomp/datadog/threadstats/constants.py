#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\threadstats\constants.py


class MetricType(object):
    Gauge = 'gauge'
    Counter = 'counter'
    Histogram = 'histogram'


class MonitorType(object):
    SERVICE_CHECK = 'service check'
    METRIC_ALERT = 'metric alert'
    QUERY_ALERT = 'query alert'
    ALL = (SERVICE_CHECK, METRIC_ALERT, QUERY_ALERT)
