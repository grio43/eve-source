#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\monitors.py
from datadog.api.resources import GetableAPIResource, CreateableAPIResource, UpdatableAPIResource, ListableAPIResource, DeletableAPIResource, ActionAPIResource

class Monitor(GetableAPIResource, CreateableAPIResource, UpdatableAPIResource, ListableAPIResource, DeletableAPIResource, ActionAPIResource):
    _class_url = '/monitor'

    @classmethod
    def get(cls, id, **params):
        if 'group_states' in params and isinstance(params['group_states'], list):
            params['group_states'] = ','.join(params['group_states'])
        return super(Monitor, cls).get(id, **params)

    @classmethod
    def get_all(cls, **params):
        if 'group_states' in params and isinstance(params['group_states'], list):
            params['group_states'] = ','.join(params['group_states'])
        return super(Monitor, cls).get_all(**params)

    @classmethod
    def mute(cls, id, **params):
        return super(Monitor, cls)._trigger_class_action('POST', 'mute', id, **params)

    @classmethod
    def unmute(cls, id, **params):
        return super(Monitor, cls)._trigger_class_action('POST', 'unmute', id, **params)

    @classmethod
    def mute_all(cls):
        return super(Monitor, cls)._trigger_class_action('POST', 'mute_all')

    @classmethod
    def unmute_all(cls):
        return super(Monitor, cls)._trigger_class_action('POST', 'unmute_all')
