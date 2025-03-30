#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\format\show_info.py
SCHEME = 'showinfo'

def format_show_info_url(type_id, item_id = None):
    if item_id is not None:
        return u'{}:{}//{}'.format(SCHEME, type_id, item_id)
    else:
        return u'{}:{}'.format(SCHEME, type_id)


def format_blueprint_show_info_url(type_id, item_id = None, runs = None, isCopy = None, te = None, me = None):
    return u'{}:{}//{}//{}//{}//{}//{}'.format(SCHEME, type_id, item_id, runs, isCopy, te, me)


def format_ship_show_info_url(type_id, item_id = None, owner_id = None):
    if owner_id is not None:
        return u'{}:{}//{}//{}'.format(SCHEME, type_id, item_id, owner_id)
    elif item_id is not None:
        return u'{}:{}//{}'.format(SCHEME, type_id, item_id)
    else:
        return u'{}:{}'.format(SCHEME, type_id)
