#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\events.py
from datadog.api.resources import GetableAPIResource, CreateableAPIResource, SearchableAPIResource, DeletableAPIResource
from datadog.util.compat import iteritems

class Event(GetableAPIResource, CreateableAPIResource, SearchableAPIResource, DeletableAPIResource):
    _class_name = 'event'
    _class_url = '/events'
    _plural_class_name = 'events'
    _json_name = 'event'
    _timestamp_keys = set(['start', 'end'])

    @classmethod
    def create(cls, **params):
        return super(Event, cls).create(attach_host_name=True, **params)

    @classmethod
    def query(cls, **params):

        def timestamp_to_integer(k, v):
            if k in cls._timestamp_keys:
                return int(v)
            else:
                return v

        params = dict(((k, timestamp_to_integer(k, v)) for k, v in iteritems(params)))
        return super(Event, cls)._search(**params)
