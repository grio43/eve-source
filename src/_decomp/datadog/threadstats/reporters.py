#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\threadstats\reporters.py
from datadog import api

class Reporter(object):

    def flush(self, metrics):
        raise NotImplementedError()


class HttpReporter(Reporter):

    def flush_metrics(self, metrics):
        api.Metric.send(metrics)

    def flush_events(self, events):
        for event in events:
            api.Event.create(**event)


class GraphiteReporter(Reporter):

    def flush(self, metrics):
        pass
