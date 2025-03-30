#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\spawning.py
from ballpark.entities.spawndataforentities import get_spawn_data_for_entities_with_custom_behavior_overrides
from ballpark.entities.spawndataforentities import get_spawn_data_for_entities
from ballparkCommon.docking import GetUndockVector
from behaviors.const.blackboardchannels import UNDOCK_DIRECTION_CHANNEL_NAME
from behaviors.utility import security
from behaviors.utility.ballparks import get_slim_item
from behaviors.utility.blackboards import get_response_thresholds
from behaviors.utility.context import get_extra_context
from behaviors.utility.entity_groups import entity_group_exists
from behaviors.utility.owner import get_owner_id
from ccpProfile import TimedFunction
from npcs.server.npcspawning.npcgrouping import generate_grouping
from npcs.server.npcspawning.spawn_const import DEFAULT_DEPLOYMENT_OFFSET_METERS
from npcs.server.npcspawning.spawntableloader import SpawnTableLoader
from spawnlists.data import select_probability_items
try:
    from ballpark.locationgenerator import GetRandomDeepSpaceLocation
except ImportError:

    def GetRandomDeepSpaceLocation():
        return (0, 0, 0)


import logging
logger = logging.getLogger(__name__)

def get_deployment_range(task):
    if getattr(task.attributes, 'deploymentRange', None):
        return task.attributes.deploymentRange
    else:
        return DEFAULT_DEPLOYMENT_OFFSET_METERS


def get_spawn_table_id(task):
    return task.GetLastBlackboardValue(task.attributes.spawnTableIdAddress)


class EntityGetter(object):

    def __init__(self, task):
        self.task = task

    @TimedFunction('behaviors::utility::spawning::EntityGetter::get_entities')
    def get_spawn_data_for_entities(self, max_npc_count = None):
        entities = getattr(self.task.attributes, 'entities', {})
        behavior_override_id = self.task.get_behavior_override_id()
        return self._get_spawn_data_for_entities(entities.iteritems(), behavior_override_id)

    def _get_spawn_data_for_entities(self, entity_types_and_count, behavior_override_id):
        return get_spawn_data_for_entities(entity_types_and_count, None, get_deployment_range(self.task), behavior_override_id)

    def on_spawn_entities(self, entity_group_id):
        pass


class EntityGetterBySpawnlistAndOwner(EntityGetter):

    @TimedFunction('behaviors::utility::spawning::EntityGetterBySpawnlistAndOwner::get_entities')
    def get_spawn_data_for_entities(self, max_npc_count = None):
        spawn_list_id = security.get_spawnlist_by_group_owner_and_security_level(self.task)
        if not spawn_list_id:
            return None
        entity_group_list = select_probability_items(spawn_list_id)
        if not entity_group_list:
            return None
        entity_group_id = entity_group_list.keys()[0]
        entities_iterator = generate_grouping(entity_group_id)
        behavior_override_id = self.task.get_behavior_override_id()
        return self._get_spawn_data_for_entities(entities_iterator, behavior_override_id)


class EntityGetterFromSpawnPointPool(EntityGetter):

    @TimedFunction('behaviors::utility::spawning::EntityGetterFromSpawnPointPool::get_entities')
    def get_spawn_data_for_entities(self, max_npc_count = None):
        spawn_pool_id = self.task.get_spawn_pool_id()
        spawn_point_amount = self._get_spawn_point_amount(spawn_pool_id)
        if not spawn_point_amount > 0:
            logger.error('Bad authoring for behavior type %s - missing spawn points', self.task.context.mySlimItem.typeID)
            return
        if spawn_pool_id is not None:
            npcs_and_remaining_points = self._get_entities_using_spawn_point_pool(spawn_point_amount, spawn_pool_id, max_npc_count)
        else:
            npcs_and_remaining_points = self._pick_entities_from_spawn_table(spawn_point_amount, max_npc_count)
        if npcs_and_remaining_points is None:
            return
        npcs, remaining_points = npcs_and_remaining_points
        logger.debug('Picked from spawn_pool_id=%s with available points=%s npcs=%s remaining points=%s max_npc_count=%s', spawn_pool_id, spawn_point_amount, npcs, remaining_points, max_npc_count)
        return self._get_spawn_data_for_entities(npcs.iteritems(), None)

    def _get_spawn_point_amount(self, spawn_pool_id):
        spawn_points = 0
        if self.task.HasAttribute('spawnPoints'):
            spawn_points = self.task.attributes.spawnPoints
        elif spawn_pool_id:
            spawn_pool_manager = self._get_spawn_point_pool_manager()
            spawn_points = spawn_pool_manager.get_current_spawn_points(spawn_pool_id)
        return spawn_points

    def _get_entities_using_spawn_point_pool(self, spawn_point_amount, spawn_pool_id, max_npc_count):
        spawn_pool_manager = self._get_spawn_point_pool_manager()
        if spawn_pool_id:
            available_spawn_points = spawn_pool_manager.get_current_spawn_points(spawn_pool_id)
            if spawn_point_amount > available_spawn_points:
                logger.debug('Not enough spawn points in pool for spawning new NPCs')
                return
        npc_and_remaining_points = self._pick_entities_from_spawn_table(spawn_point_amount, max_npc_count)
        if npc_and_remaining_points is None:
            logger.debug('No npcs picked spawn_point_amount=%s, spawn_pool_id=%s, max_npc_count=%s', spawn_point_amount, spawn_pool_id, max_npc_count)
            return
        npcs, remaining_points = npc_and_remaining_points
        if spawn_pool_id:
            spawn_pool_manager.consume_spawn_points(spawn_pool_id, spawn_point_amount - remaining_points)
        return npc_and_remaining_points

    def _pick_entities_from_spawn_table(self, spawn_point_amount, max_npc_count):
        spawn_table_picker = self._get_spawn_table_picker()
        required_npc_tags = self.task.get_required_npc_tags()
        spawn_table_id = get_spawn_table_id(self.task)
        npc_and_remaining_points = spawn_table_picker.pick_npcs_from_table_by_points_and_tags(spawn_table_id, spawn_point_amount, required_npc_tags, max_npc_count=max_npc_count)
        return npc_and_remaining_points

    def _get_spawn_point_pool_manager(self):
        return self.task.context.entityLocation.spawnPointPoolManager

    def _get_spawn_table_picker(self):
        return self.task.context.entityLocation.spawnTablePicker

    def on_spawn_entities(self, entity_group_id):
        awareness_manager = self.task.context.entityLocation.GetGroupAwarenessManager()
        awareness_manager.on_entity_group_spawn(self.task.get_spawn_pool_id(), entity_group_id)

    def _get_spawn_data_for_entities(self, entities_iterator, _):
        return get_spawn_data_for_entities_with_custom_behavior_overrides(entities_iterator, None, get_deployment_range(self.task))


class EntitySpawner(object):

    def __init__(self, task):
        self.task = task

    @TimedFunction('behaviors::utility::spawning::EntitySpawner::spawn_new_entities')
    def spawn_new_entities(self, spawn_data_for_entities):
        owner_id = self.get_owner_id()
        group_id = self.get_group_id()
        self._update_spawn_position(spawn_data_for_entities)
        behavior_group_tree_name = self._get_behavior_group_tree_name()
        extra_content = get_extra_context(self.task)
        group, entity_item_ids = self.task.context.entityLocation.DeployBehaviorEntities(owner_id, spawn_data_for_entities, group_id, groupBehaviorTreeName=behavior_group_tree_name, extraContext=extra_content, spawnTags=self.task.get_required_npc_tags(), standingThresholds=get_response_thresholds(self.task), objectiveTargetGroup=self._get_objective_target_group())
        self._register_entity_bounty_multiplier(entity_item_ids)
        self.update_entity_group_id(group.GetID())
        return (group, entity_item_ids)

    def get_owner_id(self):
        return get_owner_id(self.task)

    def _update_spawn_position(self, spawn_data_for_entities):
        spawn_position = self.task.get_spawn_position()
        for entity_spawn_data in spawn_data_for_entities:
            entity_spawn_data.update_spawn_position(spawn_position)

    def _get_spawn_position(self):
        if getattr(self.task.attributes, 'spawnPositionAddress', None):
            return self.task.GetLastBlackboardValue(self.task.attributes.spawnPositionAddress)
        else:
            return GetRandomDeepSpaceLocation(self.task.context.ballpark.solarsystemID)

    def get_group_id(self):
        if self.task.attributes.spawnNewGroup:
            return None
        if self.task.HasAttribute('entityGroupIdAddress'):
            entity_group_id = self.task.GetLastBlackboardValue(self.task.attributes.entityGroupIdAddress)
            if entity_group_exists(self.task, entity_group_id):
                return entity_group_id
            return None
        return self.task.context.myEntityGroupId

    def _get_behavior_group_tree_name(self):
        return getattr(self.task.attributes, 'behaviorTreeGroupName', None)

    def update_entity_group_id(self, entity_group_id):
        if self.task.HasAttribute('entityGroupIdAddress'):
            self.task.SendBlackboardValue(self.task.attributes.entityGroupIdAddress, entity_group_id)

    def _register_entity_bounty_multiplier(self, entity_item_ids):
        bounty_pay_out_multiplier = self.task.get_bounty_pay_out_multiplier()
        if bounty_pay_out_multiplier is None:
            return
        self.task.context.entityLocation.RegisterBountyPayOutMultiplierForEntities(entity_item_ids, bounty_pay_out_multiplier)

    def _get_objective_target_group(self):
        if getattr(self.task.attributes, 'objectiveTargetGroupAddress', None):
            return self.task.GetLastBlackboardValue(self.task.attributes.objectiveTargetGroupAddress)


class EntitySpawnTableSpawner(EntitySpawner):

    def get_owner_id(self):
        spawn_table_id = get_spawn_table_id(self.task)
        return SpawnTableLoader().get_spawn_table(spawn_table_id).npcowner


class EntitySpawnerWithUndock(EntitySpawner):

    @TimedFunction('behaviors::utility::spawning::EntitySpawnerWithUndock::spawn_new_entities')
    def spawn_new_entities(self, spawn_data_for_entities):
        owner_id = get_owner_id(self.task)
        group_id = self.get_group_id()
        direction_by_entity_type = self._update_spawn_parameters_and_get_direction(spawn_data_for_entities)
        behavior_group_tree_name = self._get_behavior_group_tree_name()
        extra_content = get_extra_context(self.task)
        group, entity_item_ids = self.task.context.entityLocation.DeployBehaviorEntities(owner_id, spawn_data_for_entities, group_id, groupBehaviorTreeName=behavior_group_tree_name, extraContext=extra_content, spawnTags=self.task.get_required_npc_tags(), standingThresholds=get_response_thresholds(self.task), objectiveTargetGroup=self._get_objective_target_group())
        self._register_entity_bounty_multiplier(entity_item_ids)
        self.update_entity_group_id(group.GetID())
        self._set_undock_direction(entity_item_ids, direction_by_entity_type)
        return (group, entity_item_ids)

    def _update_spawn_parameters_and_get_direction(self, spawn_data_for_entities):
        structure_id = self._get_structure_id()
        direction_by_entity_type = {}
        for entity_spawn_data in spawn_data_for_entities:
            entity_type_id = entity_spawn_data.entity_type_id
            spawn_position, direction = self._get_spawn_position_and_direction(structure_id, entity_type_id)
            entity_spawn_data.spawn_position = spawn_position
            entity_spawn_data.direction = direction
            direction_by_entity_type[entity_type_id] = direction

        return direction_by_entity_type

    def _get_structure_id(self):
        return self.task.GetLastBlackboardValue(self.task.attributes.structureIdAddress)

    def _get_spawn_position_and_direction(self, structure_id, entity_type_id):
        return GetUndockVector(self.task.context.ballpark, structure_id, entity_type_id)

    def _set_undock_direction(self, entity_ids, direction_by_entity_type):
        for entity_id in entity_ids:
            entity_type_id = get_slim_item(self.task, entity_id).typeID
            direction = direction_by_entity_type[entity_type_id]
            self._post_undock_direction_to_entity(entity_id, direction)

    def _post_undock_direction_to_entity(self, entity_id, directional_position):
        self.task.GetMessageChannelForItemId(entity_id, UNDOCK_DIRECTION_CHANNEL_NAME).SendMessage(directional_position)


def get_spawn_point_pool_manager(task):
    return task.context.entityLocation.spawnPointPoolManager


def get_current_spawn_points(task, spawn_pool_id):
    try:
        return get_spawn_point_pool_manager(task).get_current_spawn_points(spawn_pool_id)
    except:
        logger.exception('failed to get the current spawn pool points')
        raise


def add_spawn_points(task, spawn_pool_id, amount):
    get_spawn_point_pool_manager(task).add_spawn_points(spawn_pool_id, amount)
