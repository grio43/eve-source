#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\infrastructure.py
from datadog.api.resources import SearchableAPIResource

class Infrastructure(SearchableAPIResource):
    _class_url = '/search'
    _plural_class_name = 'results'

    @classmethod
    def search(cls, **params):
        return super(Infrastructure, cls)._search(**params)
