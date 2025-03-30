#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\util.py
import blue
import evetypes

def get_slim_item_kwargs(slim_item = None, item_id = None):
    if not slim_item:
        if item_id:
            slim_item = sm.GetService('michelle').GetItem(item_id)
    if not slim_item:
        return {'item_id': item_id}
    return {'slim_item': slim_item,
     'item_id': slim_item.itemID,
     'type_id': slim_item.typeID,
     'group_id': slim_item.groupID,
     'category_id': slim_item.categoryID,
     'owner_id': slim_item.ownerID,
     'dungeon_object_id': slim_item.dunObjectID}


def get_slim_item_by_dungeon_object_id(dungeon_object_id):
    if not dungeon_object_id:
        return
    michelle_svc = sm.StartService('michelle')
    ballpark = michelle_svc.GetBallpark()
    if not ballpark:
        return
    for ball_id in ballpark.balls:
        slim_item = michelle_svc.GetItem(ball_id)
        if getattr(slim_item, 'dunObjectID', None) == dungeon_object_id:
            return slim_item


def get_item_type_kwargs(type_id = None, item_id = None):
    result = {}
    if item_id:
        result['item_id'] = item_id
        if not type_id:
            item = sm.StartService('michelle').GetItem(item_id)
            if item:
                type_id = item.typeID
    if type_id:
        result['type_id'] = type_id
        result['group_id'] = evetypes.GetGroupID(type_id)
        result['category_id'] = evetypes.GetCategoryID(type_id)
    return result


def get_item_name(**kwargs):
    if not kwargs:
        return ''
    item_id = kwargs.get('item_id', None)
    if item_id:
        return str(item_id)
    type_id = kwargs.get('type_id', None)
    if type_id:
        type_name = evetypes.GetName(type_id)
        return '{} ({})'.format(type_name, type_id)
    group_id = kwargs.get('group_id', None)
    if group_id:
        group_name = evetypes.GetGroupNameByGroup(group_id)
        return '{} ({})'.format(group_name, group_id)
    category_id = kwargs.get('category_id', None)
    if category_id:
        category_name = evetypes.GetCategoryNameByCategory(category_id)
        return '{} ({})'.format(category_name, category_id)
    return ''


def get_ball_ids_by_distance(distance = None, type_id = None, group_id = None, category_id = None, from_id = None):
    ballpark = sm.GetService('michelle').GetBallpark()
    if not ballpark:
        return None
    if type_id:
        predicate = ballpark.GetBallPredicate('typeID', type_id)
    elif group_id:
        predicate = ballpark.GetBallPredicate('groupID', group_id)
    elif category_id:
        predicate = ballpark.GetBallPredicate('categoryID', category_id)
    else:
        return None
    return sorted(ballpark.IterBallIdsByDistance(from_id or session.shipid, distance, predicate=predicate, allowOwnShip=False))


def get_location_name(location_id):
    try:
        location = cfg.evelocations.Get(location_id)
        return u'{} ({})'.format(location.locationName, location_id)
    except:
        return str(location_id) or ''


def wait_for_session():
    while blue.os.GetSimTime() < session.nextSessionChange:
        blue.synchro.Yield()
