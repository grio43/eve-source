#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\scriber\esp_filters.py


def user_link(user_id, user_name = None):
    if not user_name:
        if not isinstance(user_id, (int,
         long,
         str,
         unicode,
         list,
         dict,
         tuple)):
            user_name = getattr(user_id, 'name', None)
            if not user_name:
                user_name = getattr(user_id, 'username', None)
                if not user_name:
                    user_name = getattr(user_id, 'userName', None)
            if hasattr(user_id, 'user_id'):
                new_user_id = getattr(user_id, 'user_id', None)
                if new_user_id and isinstance(new_user_id, (int, long)):
                    user_id = new_user_id
        elif isinstance(user_id, dict):
            user_name = user_id.get('userName', None)
            if not user_name:
                user_name = getattr(user_id, 'username', None)
                if not user_name:
                    user_name = getattr(user_id, 'name', None)
    if not user_name:
        if isinstance(user_id, (int, long)):
            user_name = 'User #%s' % user_id
        else:
            user_name = '%s' % user_id
    return '<a href="/gm/users.py?action=User&userID={user_id}" class="a-tip" title="{user_name}" rel="/gm/worker_info.py?action=FetchInfo&id={user_id}&idType=2">{user_name}</a>'.format(user_id=user_id, user_name=user_name)


def L(string, *args, **kwargs):
    return string
