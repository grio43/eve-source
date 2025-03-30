#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\threadstats\events.py
from datadog.util.compat import iteritems

class EventsAggregator(object):

    def __init__(self):
        self._events = []

    def add_event(self, **event):
        event = dict(((k, v) for k, v in iteritems(event) if v is not None))
        self._events.append(event)

    def flush(self):
        events = self._events
        self._events = []
        return events
