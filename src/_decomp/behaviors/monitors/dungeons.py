#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\dungeons.py
from ballpark.messenger.const import MESSAGE_ON_DUNGEON_TIMER_EXPIRED, MESSAGE_ON_DUNGEON_TRIGGER
from ballpark.messenger.const import MESSAGE_ON_DUNGEON_TRIGGER_EVENT
from ballpark.messenger.customkeys import dungeon_spawn_key
from behaviors.tasks import MonitorTask
from ccpProfile import TimedFunction

class BaseDungeonMonitorClass(MonitorTask):

    def _get_item_id(self):
        if not hasattr(self.context, 'myDungeonSpawnId') or self.context.myDungeonSpawnId is None:
            return
        return dungeon_spawn_key(self.context.myDungeonSpawnId)


class MonitorDungeonTimerSetBooleanAndReset(BaseDungeonMonitorClass):

    def _get_message(self):
        return MESSAGE_ON_DUNGEON_TIMER_EXPIRED

    def _can_process_message(self, timer_id):
        return self.attributes.timerId == timer_id

    @TimedFunction('behaviors::monitors::entities::InventoryChangeMonitor::_self_process_message')
    def _self_process_message(self, timer_id):
        if self._can_process_message(timer_id):
            self.SendBlackboardValue(self.attributes.messageAddress, True)
            self.behaviorTree.RequestReset(requestedBy=self)


class BaseDungeonTriggerMonitorClass(BaseDungeonMonitorClass):

    def _get_message(self):
        return MESSAGE_ON_DUNGEON_TRIGGER

    def _can_process_message(self, *args):
        trigger, spawn_id, scenario_id, _ = args
        if not self._is_same_trigger_or_trigger_event(trigger):
            return False
        if self.context.myDungeonSpawnId != spawn_id:
            return False
        return self._is_same_room_scenario(scenario_id)

    def _is_same_trigger_or_trigger_event(self, trigger):
        return self.attributes.triggerTypeId == trigger.triggerTypeID

    def _is_same_room_scenario(self, scenario_id):
        if self.HasAttribute('checkRoomScenario') and self.attributes.checkRoomScenario:
            return self.context.myDungeonSpawnScenarioId == scenario_id
        return True


class BaseDungeonTriggerEventMonitorClass(BaseDungeonTriggerMonitorClass):

    def _get_message(self):
        return MESSAGE_ON_DUNGEON_TRIGGER_EVENT

    def _is_same_trigger_or_trigger_event(self, triggerEvent):
        return self.attributes.triggerEventTypeId == triggerEvent.eventTypeID


class DungeonCancelInvulnerableOnTrigger(BaseDungeonTriggerMonitorClass):

    @TimedFunction('behaviors::monitors::dungeon::DungeonCancelInvulnerableOnTrigger::_self_process_message')
    def _self_process_message(self, *args):
        if self._can_process_message(*args):
            self.context.ballpark.CancelCurrentInvulnerability(self.context.myBall.id, self.attributes.reason)


class DungeonSetBlackboardBooleanOnTriggerEvent(BaseDungeonTriggerEventMonitorClass):

    @TimedFunction('behaviors::monitors::dungeon::DungeonSetBlackboardBooleanOnTrigger::_self_process_message')
    def _self_process_message(self, *args):
        if self._can_process_message(*args):
            self.SendBlackboardValue(self.attributes.blackboardAddress, self.attributes.trueOrFalse)
