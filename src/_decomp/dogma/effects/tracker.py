#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\effects\tracker.py
from eve.common.script.sys import idCheckers
from eveProto.generated.eve.effect.support.remote.pvp_pb2 import ShieldBoostApplied, ArmorRepairApplied, HullRepairApplied, CapacitorTransmissionApplied, TrackingComputerApplied, SensorBoosterApplied
from logging import getLogger
logger = getLogger(__name__)

class DogmaEffectTracker(object):

    @classmethod
    def _track_effect(cls, event_class, *args):
        sm.GetService('externalQueueMgr').PublishEvent(event_class, *args)

    @classmethod
    def track_electronic_warfare_effect(cls, event_class, attacker_char_id, victim_char_id, value, module_type_id):
        if idCheckers.IsEvePlayerCharacter(attacker_char_id) and idCheckers.IsEvePlayerCharacter(victim_char_id):
            cls._track_effect(event_class, attacker_char_id, victim_char_id, int(round(value)), module_type_id)

    @classmethod
    def track_remote_support_effect(cls, event_class, actor_id, actor_ship_id, actor_ship_type_id, target_id, target_ship_id, target_ship_type_id, target_corp_id, target_alliance_id, target_faction_id, change_amount, module_type_id, solar_system_id):
        if not idCheckers.IsEvePlayerCharacter(actor_id) or not idCheckers.IsEvePlayerCharacter(target_id):
            return
        if not idCheckers.IsShipType(actor_ship_type_id) or not idCheckers.IsShipType(target_ship_type_id):
            return
        if not idCheckers.IsModuleType(module_type_id):
            if not idCheckers.IsLogisticDrone(module_type_id):
                return
        if not idCheckers.IsCorporation(target_corp_id):
            return
        if not idCheckers.IsSolarSystem(solar_system_id):
            return
        change_amount = int(round(change_amount)) if change_amount else 0
        event = event_class()
        if event_class == ShieldBoostApplied:
            event.booster.sequential = actor_id
            event.amount_boosted = change_amount
        elif event_class in [ArmorRepairApplied, HullRepairApplied]:
            event.repairer.sequential = actor_id
            event.amount_repaired = change_amount
        elif event_class == CapacitorTransmissionApplied:
            event.transmitter.sequential = actor_id
            event.amount_transmitted = change_amount
        elif event_class in [TrackingComputerApplied, SensorBoosterApplied]:
            event.booster.sequential = actor_id
        event.module_type.sequential = module_type_id
        event.solar_system.sequential = solar_system_id
        event.actor.character.sequential = actor_id
        event.actor.ship.sequential = actor_ship_id
        event.actor.ship_type.sequential = actor_ship_type_id
        event.actor.module_type.sequential = module_type_id
        event.target.character.sequential = target_id
        event.target.ship.sequential = target_ship_id
        event.target.ship_type.sequential = target_ship_type_id
        event.target.corporation.sequential = target_corp_id
        if idCheckers.IsAlliance(target_alliance_id):
            event.target.alliance.sequential = target_alliance_id
        else:
            event.target.no_alliance = True
        if idCheckers.IsFaction(target_faction_id):
            event.target.faction.sequential = target_faction_id
        else:
            event.target.no_faction = True
        sm.GetService('externalQueueMgr').PublishEventPayload(event)
        cls._log_remote_support_effect(event_class, actor_id, actor_ship_id, actor_ship_type_id, target_id, target_ship_id, target_ship_type_id, target_corp_id, target_alliance_id, target_faction_id, change_amount, module_type_id, solar_system_id)

    @classmethod
    def _log_remote_support_effect(cls, event_class, actor_id, actor_ship_id, actor_ship_type_id, target_id, target_ship_id, target_ship_type_id, target_corp_id, target_alliance_id, target_faction_id, change_amount, module_type_id, solar_system_id):
        from evetypes import GetName
        logger.info('Remote Support Effect: event {event_class}, actor {actor_name} (ID {actor_id}) in ship {actor_ship_name} (ID {actor_ship_id}, Type {actor_ship_type_id}), target {target_name} (ID {target_id}) in ship {target_ship_name} (ID {target_ship_id}, Type {target_ship_type_id}) of corp {corp_name} (ID {corp_id}) and alliance {alliance_name} (ID {alliance_id}) and faction {faction_name} (ID: {faction_id}), in solar system {solar_system_name} (ID {solar_system_id}), via module {module_name} (Type {module_type_id}) and change amount {change_amount}'.format(event_class=event_class, actor_name=cfg.eveowners.Get(actor_id).ownerName, actor_id=actor_id, actor_ship_name=GetName(actor_ship_type_id), actor_ship_id=actor_ship_id, actor_ship_type_id=actor_ship_type_id, target_name=cfg.eveowners.Get(target_id).ownerName, target_id=target_id, target_ship_name=GetName(target_ship_type_id), target_ship_id=target_ship_id, target_ship_type_id=target_ship_type_id, corp_name=cfg.eveowners.Get(target_corp_id).ownerName, corp_id=target_corp_id, alliance_name=cfg.eveowners.Get(target_alliance_id).ownerName if target_alliance_id else '-', alliance_id=target_alliance_id or '-', faction_name=cfg.eveowners.Get(target_faction_id).ownerName if target_faction_id else '-', faction_id=target_faction_id or '-', solar_system_name=cfg.evelocations.Get(solar_system_id).name, solar_system_id=solar_system_id, module_name=GetName(module_type_id), module_type_id=module_type_id, change_amount=change_amount))

    @classmethod
    def track_command_burst_effect(cls, event_class, activator_char_id, buff_duration_seconds, module_type, num_ships_affected):
        if idCheckers.IsEvePlayerCharacter(activator_char_id):
            cls._track_effect(event_class, activator_char_id, int(round(buff_duration_seconds)), module_type, num_ships_affected)
