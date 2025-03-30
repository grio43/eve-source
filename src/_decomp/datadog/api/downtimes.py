#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\downtimes.py
from datadog.api.resources import GetableAPIResource, CreateableAPIResource, UpdatableAPIResource, ListableAPIResource, DeletableAPIResource

class Downtime(GetableAPIResource, CreateableAPIResource, UpdatableAPIResource, ListableAPIResource, DeletableAPIResource):
    _class_url = '/downtime'
