#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\users.py
from datadog.api.resources import ActionAPIResource, GetableAPIResource, CreateableAPIResource, UpdatableAPIResource, ListableAPIResource, DeletableAPIResource

class User(ActionAPIResource, GetableAPIResource, CreateableAPIResource, UpdatableAPIResource, ListableAPIResource, DeletableAPIResource):
    _class_name = 'user'
    _class_url = '/user'
    _plural_class_name = 'users'
    _json_name = 'user'

    @classmethod
    def invite(cls, emails):
        print '[DEPRECATION] User.invite() is deprecated. Use `create` instead.'
        if not isinstance(emails, list):
            emails = [emails]
        body = {'emails': emails}
        return super(User, cls)._trigger_action('POST', '/invite_users', **body)
