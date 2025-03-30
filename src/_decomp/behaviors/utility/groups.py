#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\groups.py


def get_group_manager(task):
    return task.context.entityLocation.GetGroupManager()


def get_entity_group(task, group_id):
    group_manager = get_group_manager(task)
    return group_manager.GetGroup(group_id)


def get_my_entity_group(task):
    return get_entity_group(task, task.context.myEntityGroupId)


def get_entity_group_member_id_list(task, group_id):
    entity_group = get_entity_group(task, group_id)
    return entity_group.GetGroupMembers()


def get_entity_group_member_count(task, group_id):
    entity_group = get_entity_group(task, group_id)
    return entity_group.Count()


def get_my_entity_group_owner_id(task):
    entity_group = get_my_entity_group(task)
    return entity_group.GetGroupOwnerId()
