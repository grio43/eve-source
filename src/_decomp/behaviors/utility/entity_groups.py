#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\entity_groups.py


def get_group_manager(task):
    return task.context.entityLocation.GetGroupManager()


def get_entity_group(task, entity_group_id):
    return get_group_manager(task).GetGroup(entity_group_id)


def get_entity_group_member_ids(task, entity_group_id):
    entity_group = get_entity_group(task, entity_group_id)
    if entity_group:
        return entity_group.GetGroupMembers()
    else:
        return []


def entity_group_exists(task, entity_group_id):
    return get_group_manager(task).HasGroup(entity_group_id)


def is_entity_group_initial_spawning_complete(task, entity_group_id):
    return get_entity_group(task, entity_group_id).IsInitialSpawningComplete()
