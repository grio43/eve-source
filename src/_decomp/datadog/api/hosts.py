#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\hosts.py
from datadog.api.resources import ActionAPIResource

class Host(ActionAPIResource):
    _class_url = '/host'

    @classmethod
    def mute(cls, host_name, **params):
        return super(Host, cls)._trigger_class_action('POST', 'mute', host_name, **params)

    @classmethod
    def unmute(cls, host_name):
        return super(Host, cls)._trigger_class_action('POST', 'unmute', host_name)
