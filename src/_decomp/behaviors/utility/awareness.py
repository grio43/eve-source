#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\awareness.py
import evetypes
import logging
from ballpark.entities.awareness.groupawareness import GroupAwarenessConfig
from behaviors.utility.blackboards import get_response_thresholds
from behaviors.utility.context import get_extra_context
from behaviors.utility.owner import get_owner_id
logger = logging.getLogger(__name__)

def get_spawn_pool_id(task):
    return task.GetLastBlackboardValue(task.attributes.spawnPoolIdAddress)


def get_awareness_manager(task):
    return task.context.entityLocation.GetGroupAwarenessManager()


def get_fleet_awareness(task, spawn_pool_id):
    return get_awareness_manager(task).get_spawn_pool_fleet_awareness(spawn_pool_id)


def get_fleet_awareness_members_ids(task, spawn_pool_id):
    awareness = get_fleet_awareness(task, spawn_pool_id)
    return awareness.get_member_ids()


def get_awareness_config(task):
    config = GroupAwarenessConfig(task.get_member_collection_id())
    config.threat_range = task.attributes.threatRange
    config.threat_timeout_seconds = task.attributes.threatTimeoutSeconds
    if task.HasAttribute('includedCategories'):
        config.included_categories = task.attributes.includedCategories
    if task.HasAttribute('excludedGroups'):
        config.excluded_groups = task.attributes.excludedGroups
    config.max_sensor_drift = task.attributes.maxSensorDrift
    config.update_time_seconds = task.attributes.updateTimeSeconds
    config.standing_thresholds = get_response_thresholds(task)
    if config.standing_thresholds is None:
        logger.error('awareness::failed getting proper standing thresholds for behavior=%s - might be missing from type or group blackboards', task.behaviorTree.GetBehaviorId())
    config.combat_targets_set_address = task.attributes.combatTargetsSetAddress
    config.owner_id = get_owner_id(task)
    config.context = get_extra_context(task)
    if task.HasAttribute('trackedTypeListID'):
        config.tracked_type_list_id = task.attributes.trackedTypeListID
    return config
