#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\metadata.py
from datadog.api.resources import GetableAPIResource, UpdatableAPIResource

class Metadata(GetableAPIResource, UpdatableAPIResource):
    _class_url = '/metrics'
    _json_name = 'metrics'

    @classmethod
    def get(cls, metric_name):
        if not metric_name:
            raise KeyError("'metric_name' parameter is required")
        return super(Metadata, cls).get(metric_name)

    @classmethod
    def update(cls, metric_name, **params):
        if not metric_name:
            raise KeyError("'metric_name' parameter is required")
        return super(Metadata, cls).update(id=metric_name, **params)
