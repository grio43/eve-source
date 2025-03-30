#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\comments.py
from datadog.api.resources import CreateableAPIResource, UpdatableAPIResource, DeletableAPIResource

class Comment(CreateableAPIResource, UpdatableAPIResource, DeletableAPIResource):
    _class_name = 'comment'
    _class_url = '/comments'
    _json_name = 'comment'
