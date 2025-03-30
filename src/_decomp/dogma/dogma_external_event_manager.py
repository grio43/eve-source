#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\dogma_external_event_manager.py
import logging
import monolithconfig
import monolithmetrics
from dogma import const
from eve.server.script.mgt.fighters import GetControlledFighterRegistryForSolarsystem
from externalQueue.events.protobuf import drone as drone_events
from externalQueue.events.protobuf.ship import combat as combat_events
from externalQueue.events.protobuf.ship import module as module_events
stdlog = logging.getLogger(__name__)

class DogmaLocationExternalEventManager(object):

    def __init__(self, externalQueueMgr, solarsystem_id):
        self._external_queue_mgr = externalQueueMgr
        self._solarsystem_id = solarsystem_id
        self._realtime_damage_events = False
        self._fighter_registry = None
        monolithconfig.add_watch_group_callback(self.refresh_config, 'Experimental')
        self.drone_settings_event_callbacks = {const.attributeDroneIsAggressive: self.send_set_drone_aggressive_event,
         const.attributeDroneFocusFire: self.send_drone_focus_fire}

    def refresh_config(self):
        self._realtime_damage_events = monolithconfig.enabled('realtime_damage_events', 'Experimental')

    def _get_fighter_controller_ship_item_id(self, fighter_id):
        if self._fighter_registry is None:
            self._fighter_registry = GetControlledFighterRegistryForSolarsystem(self._solarsystem_id)
        return self._fighter_registry.GetControllerForFighter(fighter_id)

    def send_energy_warfare_event(self, ballpark, item_type_id, ship_id, owner_id, target_id, amount):
        pass

    def send_remote_repair_event(self, ballpark, item_type_id, ship_id, owner_id, target_id, amount):
        pass

    def send_effect_applied_event(self, ballpark, env, effect):
        pass

    def send_drone_settings_event(self, char_id, setting_id):
        self.drone_settings_event_callbacks.get(setting_id, self.handle_unknown_drone_setting)(char_id, setting_id)

    def send_set_drone_aggressive_event(self, char_id, setting_id):
        self._external_queue_mgr.PublishEvent(drone_events.DroneSettingsAppliedEvent, char_id)

    def send_drone_focus_fire(self, char_id, setting_id):
        self._external_queue_mgr.PublishEvent(drone_events.DroneSettingsAppliedEvent, char_id)

    def handle_unknown_drone_setting(self, char_id, setting_id):
        stdlog.error('Attempted to publish event for invalid drone setting: %s' % setting_id, exc_info=1)

    def send_remove_targets_event(self, char_id):
        self._external_queue_mgr.PublishEvent(combat_events.TargetsRemovedEvent, char_id)

    def send_activate_event(self, char_id):
        self._external_queue_mgr.PublishEvent(module_events.ActivatedEvent, char_id)

    def send_deactivate_event(self, char_id):
        self._external_queue_mgr.PublishEvent(module_events.DeactivatedEvent, char_id)

    def send_start_module_repair_event(self, char_id):
        self._external_queue_mgr.PublishEvent(module_events.RepairStartedEvent, char_id)

    def send_load_ammo_event(self, char_id):
        self._external_queue_mgr.PublishEvent(module_events.AmmoLoadedEvent, char_id)


class BaseDogmaExternalEventManager(object):

    def __init__(self, externalQueueMgr):
        self._external_queue_mgr = externalQueueMgr
        self._realtime_damage_events = False
        monolithconfig.add_watch_group_callback(self.refresh_config, 'Experimental')

    def refresh_config(self):
        self._realtime_damage_events = monolithconfig.enabled('realtime_damage_events', 'Experimental')

    def send_damage_event(self, location_id, target_id, source_item, damage_source_item, weapon_item, turret_count, damage_sum):
        monolithmetrics.increment(metric='dogma.send_damage_event', value=1)
