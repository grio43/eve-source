#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\default\categories.py
import eveicon
import localization
CATEGORY_NAME_LABELS = {1: 'Overview/Default/CategoryNames/General',
 2: 'Overview/Default/CategoryNames/WarpTo',
 3: 'Overview/Default/CategoryNames/TargetCapsuleer',
 4: 'Overview/Default/CategoryNames/Friendly',
 5: 'Overview/Default/CategoryNames/Mining'}
CATEGORY_ICONS = {1: eveicon.star,
 2: eveicon.warp_to,
 3: eveicon.target,
 4: eveicon.user_plus,
 5: eveicon.mining}
CATEGORY_NONE = 0
CATEGORY_ORDER = [0,
 1,
 2,
 3,
 4,
 5]

def get_name(category_id):
    label = CATEGORY_NAME_LABELS.get(category_id)
    if label:
        return localization.GetByLabel(label)


def get_icon(category_id):
    return CATEGORY_ICONS.get(category_id, None)
