#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\tags.py
from datadog.api.resources import CreateableAPIResource, UpdatableAPIResource, DeletableAPIResource, GetableAPIResource, ListableAPIResource

class Tag(CreateableAPIResource, UpdatableAPIResource, GetableAPIResource, ListableAPIResource, DeletableAPIResource):
    _class_name = 'tags'
    _class_url = '/tags/hosts'
    _plural_class_name = 'tags'

    @classmethod
    def create(cls, host, **body):
        params = {}
        if 'source' in body:
            params['source'] = body['source']
        return super(Tag, cls).create(id=host, params=params, **body)

    @classmethod
    def update(cls, host, **body):
        params = {}
        if 'source' in body:
            params['source'] = body['source']
        return super(Tag, cls).update(id=host, params=params, **body)
