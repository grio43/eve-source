#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\entityspawning.py
from ballpark.entities.spawndataforentities import get_spawn_data_for_entities
from ballpark.locationgenerator import GetRandomDeepSpaceLocation
from behaviors.const.blackboardchannels import GUARD_OBJECT_ITEM_ID
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task
from behaviors.utility.awareness import get_spawn_pool_id, get_awareness_config
from behaviors.utility.context import get_extra_context
from behaviors.utility.groups import get_entity_group_member_count
from behaviors.utility.owner import get_owner_id
from behaviors.utility.spawning import EntityGetter, EntityGetterBySpawnlistAndOwner, EntityGetterFromSpawnPointPool
from behaviors.utility.spawning import get_spawn_point_pool_manager
from behaviors.utility.spawning import EntitySpawner, EntitySpawnerWithUndock
from behaviors.utility.spawning import EntitySpawnTableSpawner
from ccpProfile import TimedFunction
from npcs.server.npcspawning.reactivespawn_counters import get_npc_fleet_type
from npcs.server.npcspawning.reactivespawning import ReactiveSpawnConfig
import logging
logger = logging.getLogger(__name__)

class RegisterSpawnPool(Task):

    @TimedFunction('behaviors::actions::entityspawning::RegisterSpawnPool::OnEnter')
    def OnEnter(self):
        max_spawn_points = self.attributes.maxSpawnPoints
        if not max_spawn_points:
            self.SetStatusToFailed()
            return
        initial_spawn_points = self._get_initial_spawn_points()
        spawn_point_pool_id = self._assign_spawn_pool(max_spawn_points, initial_spawn_points)
        logger.debug('Registering spawn pool %s', spawn_point_pool_id)
        self._post_spawn_point_pool(spawn_point_pool_id)
        self.SetStatusToSuccess()

    def _get_initial_spawn_points(self):
        return getattr(self.attributes, 'initialSpawnPoints', None)

    def _assign_spawn_pool(self, max_spawn_points, initial_spawn_points):
        spawn_point_pool_manager = self._get_spawn_point_pool_manager()
        spawn_point_pool_id = spawn_point_pool_manager.register_new_spawn_point_pool(max_spawn_points, initial_spawn_points)
        return spawn_point_pool_id

    def _get_spawn_point_pool_manager(self):
        return self.context.entityLocation.GetSpawnPoolManager()

    def _post_spawn_point_pool(self, spawn_point_pool_id):
        self.SendBlackboardValue(self.attributes.spawnPoolIdAddress, spawn_point_pool_id)


class SpawnNewEntities(Task, GroupTaskMixin):

    @TimedFunction('behaviors::actions::entityspawning::SpawnNewEntities::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        entity_getter = self._get_entity_getter()
        entity_spawner = self._get_entity_spawner()
        existing_entity_group_id = entity_spawner.get_group_id()
        max_npc_count = self._get_max_npc_count_for_group(existing_entity_group_id)
        spawn_data_for_entities = entity_getter.get_spawn_data_for_entities(max_npc_count=max_npc_count)
        if spawn_data_for_entities:
            group, entity_item_ids = entity_spawner.spawn_new_entities(spawn_data_for_entities)
            self._update_group(group.GetID(), len(entity_item_ids), existing_entity_group_id)
            entity_getter.on_spawn_entities(group.GetID())
            self.SetStatusToSuccess()
        else:
            logger.debug('No entities to spawn. group_id=%s max_npc_count=%s', existing_entity_group_id, max_npc_count)

    def _get_entity_getter(self):
        return EntityGetter(self)

    def _get_entity_spawner(self):
        return EntitySpawner(self)

    def _update_group(self, entity_group_id, entity_count, existing_entity_group_id):
        self._update_reinforcements_for_group(entity_count, existing_entity_group_id)
        self._register_entity_group_with_blackboard(entity_group_id)
        self._update_group_blackboard_channels(entity_group_id)

    def _update_reinforcements_for_group(self, entity_count, existing_entity_group_id):
        if existing_entity_group_id is None:
            return
        reinforcement_manager = self._get_reinforcement_manager()
        reinforced_group = reinforcement_manager.GetReinforcedGroup(existing_entity_group_id)
        if not reinforced_group:
            return
        old_count = reinforced_group.GetFullStrengthCount()
        reinforced_group.SetEntityUnitCount(old_count + entity_count)

    def _get_reinforcement_manager(self):
        return self.context.entityLocation.reinforcementManager

    def _register_entity_group_with_blackboard(self, entity_group_id):
        if not hasattr(self.attributes, 'entityGroupSetAddress') or not self.attributes.spawnNewGroup:
            return
        entity_groups_set = self.GetLastBlackboardValue(self.attributes.entityGroupSetAddress) or set()
        entity_groups_set.add(entity_group_id)
        self.SendBlackboardValue(self.attributes.entityGroupSetAddress, entity_groups_set)

    def _update_group_blackboard_channels(self, entity_group_id):
        if self.HasAttribute('guardObjectAddress'):
            guard_object_item_id = self.GetLastBlackboardValue(self.attributes.guardObjectAddress)
            self.GetMessageChannelForGroupId(entity_group_id, GUARD_OBJECT_ITEM_ID[1]).SendMessage(guard_object_item_id)

    def get_spawn_pool_id(self):
        if self.HasAttribute('spawnPoolIdAddress'):
            return self.GetLastBlackboardValue(self.attributes.spawnPoolIdAddress)

    def get_spawn_table_id(self):
        if self.HasAttribute('spawnTableIdAddress'):
            return self.GetLastBlackboardValue(self.attributes.spawnTableIdAddress)

    def _get_max_npc_count_for_group(self, group_id):
        if not self.HasAttribute('maxNpcCount'):
            return
        max_npc_count = self.attributes.maxNpcCount
        if group_id is not None:
            group_count = get_entity_group_member_count(self, group_id)
            max_npc_count -= group_count
            if max_npc_count < 0:
                max_npc_count = 0
        return max_npc_count

    def get_bounty_pay_out_multiplier(self):
        return getattr(self.attributes, 'bountyPayOutMultiplier', None)

    def get_behavior_override_id(self):
        return getattr(self.attributes, 'behaviorTreeName', None)

    def get_spawn_position(self):
        if getattr(self.attributes, 'spawnPositionAddress', None):
            return self.GetLastBlackboardValue(self.attributes.spawnPositionAddress)
        else:
            return GetRandomDeepSpaceLocation(self.context.ballpark.solarsystemID)

    def get_required_npc_tags(self):
        return getattr(self.attributes, 'npcTagList', set())


class SpawnNewEntitiesBySpawnlistAndOwnerId(SpawnNewEntities):

    def _get_entity_getter(self):
        return EntityGetterBySpawnlistAndOwner(self)


class SpawnEntitiesFromSpawnTable(SpawnNewEntities):

    def _get_entity_getter(self):
        return EntityGetterFromSpawnPointPool(self)

    def _get_entity_spawner(self):
        return EntitySpawnTableSpawner(self)


class SpawnNewEntitiesAtStructure(SpawnNewEntities):

    def _get_entity_spawner(self):
        return EntitySpawnerWithUndock(self)


class SpawnNewEntitiesAtStructureBySpawnlistAndOwnerId(SpawnNewEntitiesAtStructure):

    def _get_entity_getter(self):
        return EntityGetterBySpawnlistAndOwner(self)


class SpawnNewEntitiesAtStructureFromSpawnTable(SpawnNewEntitiesAtStructure):

    def _get_entity_getter(self):
        return EntityGetterFromSpawnPointPool(self)


class SendSpawnTableIdToBlackboard(Task):

    def OnEnter(self):
        self.SendBlackboardValue(self.attributes.npcSpawnTableIdAddress, self.attributes.npcSpawnTableId)
        self.SetStatusToSuccess()


class SetSpawnPoolAmount(Task):

    def OnEnter(self):
        spawn_pool_id = get_spawn_pool_id(self)
        spawn_point_pool_manager = get_spawn_point_pool_manager(self)
        spawn_point_pool_manager.set_spawn_points(spawn_pool_id, self.attributes.spawnPointAmount)
        self.SetStatusToSuccess()


class SetSelfEntityRespawn(Task, GroupTaskMixin):

    def OnEnter(self):
        entity_types_and_count = [(self.context.mySlimItem.typeID, 1)]
        spawn_data_for_entities = get_spawn_data_for_entities(entity_types_and_count, self.context.myBall.GetPosition(), self.attributes.deploymentRangeMeters, self.behaviorTree.GetBehaviorId())
        self.context.entityLocation.spawnManager.SetRealItemRespawn(self.context.myEntityGroupId, self.context.mySlimItem.ownerID, spawn_data_for_entities, self.attributes.minRespawnDelaySeconds, self.attributes.maxRespawnDelaySeconds)
        self.SetStatusToSuccess()


class DisableRespawnGroup(Task, GroupTaskMixin):

    def OnEnter(self):
        self.context.entityLocation.behaviorRespawnManager.remove_respawn_group(self.context.myEntityGroupId)
        self.SetStatusToSuccess()


class SetSpawnTableOnBlackboardByOwner(Task):

    def OnEnter(self):
        spawn_table_id = self._get_spawn_table_id()
        self.SendBlackboardValue(self.attributes.spawnTableIdAddress, spawn_table_id)
        self.SetStatusToSuccess()

    def _get_spawn_table_id(self):
        owner_id = get_owner_id(self)
        spawn_table_id = self.attributes.ownerToSpawnTableMapping.get(owner_id)
        if spawn_table_id is None:
            raise ValueError('Unable to find a spawn table id for owner %s' % owner_id)
        return spawn_table_id


class ReactiveSpawning(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        owner_id = get_owner_id(self)
        spawn_config = self._get_spawn_config(owner_id)
        reactive_spawn_manager = self.context.entityLocation.reactiveSpawnManager
        reactive_spawn_manager.start_spawner(spawn_config)
        self._post_spawn_pool_id(spawn_config.spawn_point_pool_id)
        reactive_spawn_manager.deregister_when_spawner_is_destroyed(spawn_config, self.context.entityLocation.event_handler_registry)
        logger.debug('behavior::entity_spawning::Behavior=%s initialized reactive spawn task with config=%s', self.behaviorTree.GetBehaviorId(), spawn_config)

    def get_member_collection_id(self):
        return self.context.myEntityGroupId

    def _get_spawn_config(self, owner_id):
        spawn_config = ReactiveSpawnConfig(owner_id, self.get_spawn_table_id(), self.attributes.npcFleetCounterTableId, get_awareness_config(self), initial_point_amount=self.attributes.initialPointAmount, min_point_amount=self.attributes.minPointAmount, max_point_amount=self.attributes.maxPointAmount, extra_context=get_extra_context(self), capped_spawn_points=self.attributes.cappedSpawnPoints, should_spawn_without_threats=self.attributes.spawnWithoutThreats, should_reset_without_threats=self.attributes.resetWithoutThreats, spawn_point_multiplier=self.attributes.spawnPointMultiplier, initial_spawn_npc_fleet_type_id=getattr(self.attributes, 'initialSpawnNpcFleetTypeID', None), min_spawn_interval_seconds=self.attributes.minSpawnIntervalSeconds, max_spawn_interval_seconds=self.attributes.maxSpawnIntervalSeconds, spawner_item_id=self.context.mySlimItem.itemID, bounty_payout_multiplier=self.attributes.bountyPayoutMultiplier, should_match_player_points=self.attributes.shouldMatchPlayerPoints, spawn_point_threshold=self.attributes.spawnPointThreshold)
        return spawn_config

    def get_spawn_table_id(self):
        return self.GetLastBlackboardValue(self.attributes.spawnTableIdAddress)

    def _post_spawn_pool_id(self, spawn_pool_id):
        self.SendBlackboardValue(self.attributes.spawnPoolIdAddress, spawn_pool_id)

    def _has_initial_spawn_npc_fleet_type_id(self):
        return hasattr(self.attributes, 'initialSpawnNpcFleetTypeID') and self.attributes.initialSpawnNpcFleetTypeID is not None

    def _get_initial_spawn_npc_fleet_type(self):
        return get_npc_fleet_type(self.attributes.initialSpawnNpcFleetTypeID)
