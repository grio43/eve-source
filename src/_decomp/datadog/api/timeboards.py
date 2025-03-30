#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\timeboards.py
from datadog.api.resources import GetableAPIResource, CreateableAPIResource, UpdatableAPIResource, ListableAPIResource, DeletableAPIResource

class Timeboard(GetableAPIResource, CreateableAPIResource, UpdatableAPIResource, ListableAPIResource, DeletableAPIResource):
    _class_name = 'dash'
    _class_url = '/dash'
    _plural_class_name = 'dashes'
    _json_name = 'dash'
