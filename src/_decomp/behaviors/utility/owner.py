#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\owner.py


def get_owner_id(task):
    entity_group = task.context.entityLocation.GetBehaviorEntityGroup(task.context.myEntityGroupId)
    if entity_group is not None:
        return entity_group.GetGroupOwnerId()
    return task.context.mySlimItem.ownerID
