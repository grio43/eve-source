#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\screenboards.py
from datadog.api.resources import GetableAPIResource, CreateableAPIResource, UpdatableAPIResource, DeletableAPIResource, ActionAPIResource, ListableAPIResource

class Screenboard(GetableAPIResource, CreateableAPIResource, UpdatableAPIResource, DeletableAPIResource, ActionAPIResource, ListableAPIResource):
    _class_name = 'screen'
    _class_url = '/screen'
    _json_name = 'board'

    @classmethod
    def share(cls, board_id):
        return super(Screenboard, cls)._trigger_action('GET', 'screen/share', board_id)

    @classmethod
    def revoke(cls, board_id):
        return super(Screenboard, cls)._trigger_action('DELETE', 'screen/share', board_id)
