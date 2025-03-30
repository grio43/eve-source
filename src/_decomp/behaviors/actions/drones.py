#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\drones.py
from behaviors.actions.entityspawning import SpawnNewEntities
from behaviors.const.blackboardchannels import DRONE_CONTROLLER_ADDRESS, GROUP_PRIMARY_TARGET_CHANNEL_NAME
from behaviors.const.blackboardchannels import SELF_DESTRUCT_DRONE_ON_CONTROLLER_DEATH_ADDRESS
from behaviors.tasks import Task
from behaviors.utility.entity_groups import entity_group_exists
from behaviors.utility.spawning import EntitySpawner, EntityGetter
from ccpProfile import TimedFunction

class SpawnDrones(SpawnNewEntities):

    def _get_entity_getter(self):
        return DroneGetter(self)

    def _get_entity_spawner(self):
        return DroneSpawner(self)

    def _update_reinforcements_for_group(self, entity_count, existing_entity_group_id):
        pass

    def _register_entity_group_with_blackboard(self, drone_group_id):
        existing_drone_group_id = self.GetLastBlackboardValue(self.attributes.droneGroupIdAddress)
        if existing_drone_group_id is None:
            self.SendBlackboardValue(self.attributes.droneGroupIdAddress, drone_group_id)

    def _update_group_blackboard_channels(self, drone_group_id):
        drone_group_id_channel = self.GetMessageChannelForGroupId(drone_group_id, DRONE_CONTROLLER_ADDRESS[1])
        if drone_group_id_channel.GetLastMessage() is None:
            drone_group_id_channel.SendMessage(self.context.myItemId)
        self_destruct_channel = self.GetMessageChannelForGroupId(drone_group_id, SELF_DESTRUCT_DRONE_ON_CONTROLLER_DEATH_ADDRESS[1])
        self_destruct_channel.SendMessage(self.attributes.shouldSelfDestructOnControllerDeath)

    def get_spawn_position(self):
        return (self.context.myBall.x, self.context.myBall.y, self.context.myBall.z)


class DroneGetter(EntityGetter):

    def get_spawn_data_for_entities(self, max_npc_count = None):
        drone_type_id = self.task.attributes.droneTypeId
        drones_spawned_total = self.task.GetLastBlackboardValue(self.task.attributes.dronesSpawnedCountAddress)
        max_drones = self._get_max_drones(drones_spawned_total)
        active_drone_count = self._get_active_drone_count()
        drone_count_for_spawning = int(max_drones - active_drone_count)
        drones = {int(drone_type_id): drone_count_for_spawning}
        self._reduce_drone_capacity(drones_spawned_total + drone_count_for_spawning)
        behavior_override_id = self.task.get_behavior_override_id()
        return self._get_spawn_data_for_entities(drones.iteritems(), behavior_override_id)

    def _get_max_drones(self, drones_spawned_total):
        max_drone_count = self.task.GetLastBlackboardValue(self.task.attributes.maxDroneCountAddress)
        max_drone_active_count = self.task.GetLastBlackboardValue(self.task.attributes.maxDroneActiveCountAddress)
        return min(max_drone_count - drones_spawned_total, max_drone_active_count)

    def _get_active_drone_count(self):
        group_manager = self.task.context.entityLocation.GetGroupManager()
        drone_group_id = self.task.GetLastBlackboardValue(self.task.attributes.droneGroupIdAddress)
        if drone_group_id is None:
            return 0
        if not entity_group_exists(self.task, drone_group_id):
            self.task.SendBlackboardValue(self.task.attributes.droneGroupIdAddress, None)
            return 0
        drone_group = group_manager.GetGroup(drone_group_id)
        return drone_group.Count()

    def _reduce_drone_capacity(self, drones_spawned_total):
        self.task.SendBlackboardValue(self.task.attributes.dronesSpawnedCountAddress, drones_spawned_total)


class DroneSpawner(EntitySpawner):

    def get_group_id(self):
        drone_group_id = self.task.GetLastBlackboardValue(self.task.attributes.droneGroupIdAddress)
        if entity_group_exists(self.task, drone_group_id):
            return drone_group_id


class AssignTargetToDroneGroup(Task):

    @TimedFunction('behaviors::actions::drones::AssignTargetToDroneGroup::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        drone_group_id = self.GetLastBlackboardValue(self.attributes.droneGroupIdAddress)
        if drone_group_id is not None and entity_group_exists(self, drone_group_id):
            target_id = self.GetLastBlackboardValue(self.attributes.targetIdAddress)
            message_channel = self.GetMessageChannelForGroupId(drone_group_id, GROUP_PRIMARY_TARGET_CHANNEL_NAME)
            message_channel.SendMessage(target_id)
            self.SetStatusToSuccess()
