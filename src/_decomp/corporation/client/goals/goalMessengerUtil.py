#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\client\goals\goalMessengerUtil.py
import eveProto.generated.eve_public.corporationgoal.contribution.configuration_pb2 as CorpGoalContributionConfiguration
import evetypes
import logging
import shipgroup
import uuid
from eve.common.script.sys import idCheckers
from eveProto.generated.eve_public.goal.goal_pb2 import ContributionConfiguration
from eveProto.monolith_converters.units import get_single_value_from_split_precision_message
from goals.common.errors import ContributionMethodTypeNotSupported
from goals.common.goalConst import ConflictType
from goals.common.goalConst import ContributionMethodTypes, OrganizationType, CAREER_PATH_IDS, ON_BEHALF_OF_SELF, ON_BEHALF_OF_CORP
from localization import GetByMessageID
logger = logging.getLogger('corporation_goals')

def add_owner_identity_to_proto(identity_type, matcher):
    if identity_type is None:
        matcher.identity.any = True
    elif idCheckers.IsCharacter(identity_type):
        matcher.identity.match_character_value.sequential = identity_type
    elif idCheckers.IsCorporation(identity_type):
        matcher.identity.match_corporation_value.sequential = identity_type
    elif idCheckers.IsAlliance(identity_type):
        matcher.identity.match_alliance_value.sequential = identity_type
    elif idCheckers.IsFaction(identity_type):
        matcher.identity.match_faction_value.sequential = identity_type


def add_owner_identities_to_proto(identities, set_matcher):
    if not identities:
        set_matcher.all = True
        return
    for identity_id in identities:
        if idCheckers.IsCharacter(identity_id):
            matcher = set_matcher.sets.characters.add()
            matcher.character.sequential = identity_id
        elif idCheckers.IsCorporation(identity_id):
            matcher = set_matcher.sets.characters.add()
            matcher.corporation.sequential = identity_id
        elif idCheckers.IsAlliance(identity_id):
            matcher = set_matcher.sets.characters.add()
            matcher.alliance.sequential = identity_id
        elif idCheckers.IsFaction(identity_id):
            matcher = set_matcher.sets.characters.add()
            matcher.faction.sequential = identity_id


def get_owner_identity_from_proto(identity):
    if identity.HasField('match_character_value'):
        return int(identity.match_character_value.sequential)
    if identity.HasField('match_corporation_value'):
        return int(identity.match_corporation_value.sequential)
    if identity.HasField('match_alliance_value'):
        return int(identity.match_alliance_value.sequential)
    if identity.HasField('match_faction_value'):
        return int(identity.match_faction_value.sequential)


def get_owner_identities_from_proto(identities):
    if not identities.HasField('sets'):
        return None
    result = set()
    for entry in identities.sets.characters:
        if entry.HasField('character'):
            result.add(int(entry.character.sequential))
        elif entry.HasField('corporation'):
            result.add(int(entry.corporation.sequential))
        elif entry.HasField('alliance'):
            result.add(int(entry.alliance.sequential))
        elif entry.HasField('faction'):
            result.add(int(entry.faction.sequential))

    if result:
        return list(result)


def add_conflict_type_to_proto(conflict_type, matcher):
    if conflict_type == ConflictType.ALL:
        matcher.all = True
    elif conflict_type == ConflictType.PVP:
        matcher.pvp = True
    elif conflict_type == ConflictType.PVE:
        matcher.pve = True


def get_conflict_type_from_proto(conflict_type):
    if conflict_type.HasField('all'):
        return ConflictType.ALL
    if conflict_type.HasField('pvp'):
        return ConflictType.PVP
    if conflict_type.HasField('pve'):
        return ConflictType.PVE


def add_corporations_to_proto(corporations, set_matcher):
    if not corporations:
        set_matcher.all = True
        return
    for corporation_id in corporations:
        if idCheckers.IsCorporation(corporation_id):
            matcher = set_matcher.set.ids.add()
            matcher.sequential = corporation_id


def get_corporations_from_proto(identities):
    if not identities.HasField('set'):
        return None
    result = set()
    for entry in identities.set.ids:
        result.add(int(entry.sequential))

    if result:
        return list(result)


def add_ship_type_to_proto(ship_type, matcher):
    if ship_type is None:
        matcher.ship_type.any = True
    else:
        matcher.ship_type.match_value.sequential = ship_type


def add_ships_to_proto(ships, set_matcher):
    if not ships:
        set_matcher.all = True
        return
    for entry_type, entry_id in ships:
        if entry_type == 'ship_type':
            if idCheckers.IsShipType(entry_id):
                matcher = set_matcher.sets.ships.add()
                matcher.ship_type.sequential = entry_id
        elif entry_type == 'ship_class':
            if entry_id in shipgroup.ALL_GROUPS:
                matcher = set_matcher.sets.ships.add()
                matcher.ship_class.sequential = entry_id


def get_ship_type_from_proto(ship_type):
    if ship_type.HasField('match_value'):
        return int(ship_type.match_value.sequential)


def get_ships_from_proto(ships):
    if not ships.HasField('sets'):
        return None
    result = set()
    for entry in ships.sets.ships:
        if entry.HasField('ship_type'):
            result.add(('ship_type', int(entry.ship_type.sequential)))
        elif entry.HasField('ship_class'):
            result.add(('ship_class', int(entry.ship_class.sequential)))

    if result:
        return list(result)


def add_ores_to_proto(ores, set_matcher):
    if not ores:
        set_matcher.all = True
        return
    allowed_type_ids = evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_ALL_MINABLE_TYPES)
    allowed_group_ids = {evetypes.GetGroupID(type_id) for type_id in allowed_type_ids}
    for entry_type, entry_id in ores:
        if entry_type == 'item_type':
            if entry_id in allowed_type_ids:
                matcher = set_matcher.sets.ores.add()
                matcher.ore_type.sequential = entry_id
        elif entry_type == 'item_group':
            if entry_id in allowed_group_ids:
                matcher = set_matcher.sets.ores.add()
                matcher.ore_group.sequential = entry_id


def get_ores_from_proto(ores):
    if not ores.HasField('sets'):
        return None
    result = set()
    for entry in ores.sets.ores:
        if entry.HasField('ore_type'):
            result.add(('item_type', int(entry.ore_type.sequential)))
        elif entry.HasField('ore_group'):
            result.add(('item_group', int(entry.ore_group.sequential)))

    if result:
        return list(result)


def add_solar_system_to_proto(solar_system, matcher):
    if solar_system is None:
        matcher.solar_system.any = True
    else:
        matcher.solar_system.match_value.sequential = solar_system


def add_solar_systems_to_proto(solar_systems, set_matcher):
    if not solar_systems:
        set_matcher.all = True
        return
    for location_id in solar_systems:
        if idCheckers.IsSolarSystem(location_id):
            matcher = set_matcher.sets.systems.add()
            matcher.solar_system.sequential = location_id
        elif idCheckers.IsConstellation(location_id):
            matcher = set_matcher.sets.systems.add()
            matcher.constellation.sequential = location_id
        elif idCheckers.IsRegion(location_id):
            matcher = set_matcher.sets.systems.add()
            matcher.region.sequential = location_id


def get_solar_system_from_proto(solar_system):
    if solar_system.HasField('match_value'):
        return int(solar_system.match_value.sequential)


def get_solar_systems_from_proto(solar_systems):
    if not solar_systems.HasField('sets'):
        return None
    result = set()
    for entry in solar_systems.sets.systems:
        if entry.HasField('solar_system'):
            result.add(entry.solar_system.sequential)
        elif entry.HasField('constellation'):
            result.add(entry.constellation.sequential)
        elif entry.HasField('region'):
            result.add(entry.region.sequential)

    if result:
        return list(result)


def construct_generic_ship_dict_from_proto(data, as_multi_value = False):
    solar_system_id = get_solar_system_from_proto(data.solar_system)
    ship_type = get_ship_type_from_proto(data.ship_type)
    organization_type = get_owner_identity_from_proto(data.identity)
    if as_multi_value:
        return {'solar_system': [solar_system_id] if solar_system_id else None,
         'ship': [('ship_type', ship_type)] if ship_type else None,
         'organization': [organization_type] if organization_type else None}
    else:
        return {'solar_system': solar_system_id,
         'ship': ship_type,
         'organization': organization_type}


def add_generic_ship_matchers(method, solar_system, ship, organization_type):
    matcher = method.contribution_methods.add()
    add_solar_system_to_proto(solar_system, matcher)
    add_ship_type_to_proto(ship, matcher)
    add_owner_identity_to_proto(organization_type, matcher)


def construct_deliver_item_proto(item_type, office_id):
    method = ContributionConfiguration.DeliverItemContributionConfiguration()
    matcher = method.contribution_methods.add()
    matcher.delivered_item_type.sequential = item_type
    if office_id is None:
        matcher.free_office = True
    else:
        matcher.office.sequential = office_id
    return method


def construct_deliver_item_dict_from_proto(data):
    office = None
    if data.HasField('office'):
        office = data.office.sequential
    return {'item_type': int(data.delivered_item_type.sequential),
     'office': office}


def construct_kill_npc_proto(solar_system_id):
    method = ContributionConfiguration.KillNPCContributionConfiguration()
    matcher = method.contribution_methods.add()
    if solar_system_id is None:
        matcher.free_solar_system = True
    else:
        matcher.solar_system.sequential = solar_system_id
    return method


def construct_kill_npc_dict_from_proto(data):
    solar_system_id = None
    if data.HasField('solar_system'):
        solar_system_id = int(data.solar_system.sequential)
    return {'solar_system': solar_system_id}


def construct_damage_ship_proto(solar_systems, ships, identities):
    method = CorpGoalContributionConfiguration.DamageShip()
    add_solar_systems_to_proto(solar_systems, method.solar_systems)
    add_ships_to_proto(ships, method.ships)
    add_owner_identities_to_proto(identities, method.attacked_identities)
    return method


def construct_deprecated_damage_ship_dict_from_proto(data):
    solar_system_id = None
    if data.HasField('solar_system'):
        solar_system_id = [int(data.solar_system.sequential)]
    ship_type = None
    if data.HasField('ship_type'):
        ship_type = [('ship_type', int(data.ship_type.sequential))]
    organization_type = None
    if data.HasField('character'):
        organization_type = [int(data.character.sequential)]
    elif data.HasField('corporation'):
        organization_type = [int(data.corporation.sequential)]
    elif data.HasField('alliance'):
        organization_type = [int(data.alliance.sequential)]
    elif data.HasField('faction'):
        organization_type = [int(data.faction.sequential)]
    return {'solar_system': solar_system_id,
     'ship': ship_type,
     'organization': organization_type}


def construct_damage_ship_dict_from_proto(data):
    return {'solar_system': get_solar_systems_from_proto(data.solar_systems),
     'ship': get_ships_from_proto(data.ships),
     'organization': get_owner_identities_from_proto(data.attacked_identities)}


def construct_mine_ore_proto(solar_systems, ores):
    method = CorpGoalContributionConfiguration.MineOre()
    add_solar_systems_to_proto(solar_systems, method.solar_systems)
    add_ores_to_proto(ores, method.ores)
    return method


def construct_deprecated_mine_ore_dict_from_proto(data):
    solar_system_id = None
    if data.HasField('solar_system'):
        solar_system_id = [int(data.solar_system.sequential)]
    ore_type = None
    if data.HasField('ore'):
        ore_type = [('item_type', int(data.ore.sequential))]
    return {'solar_system': solar_system_id,
     'ore': ore_type}


def construct_mine_ore_dict_from_proto(data):
    return {'solar_system': get_solar_systems_from_proto(data.solar_systems),
     'ore': get_ores_from_proto(data.ores)}


def construct_destroy_player_ship_proto(solar_systems, ships, identities):
    method = CorpGoalContributionConfiguration.DestroyPlayerShip()
    add_solar_systems_to_proto(solar_systems, method.solar_systems)
    add_ships_to_proto(ships, method.ships)
    add_owner_identities_to_proto(identities, method.destroyed_identities)
    return method


def construct_deprecated_destroy_player_ship_dict_from_proto(data):
    return construct_generic_ship_dict_from_proto(data, as_multi_value=True)


def construct_destroy_player_ship_dict_from_proto(data):
    return {'solar_system': get_solar_systems_from_proto(data.solar_systems),
     'ship': get_ships_from_proto(data.ships),
     'organization': get_owner_identities_from_proto(data.destroyed_identities)}


def construct_capture_fw_complex_dict_from_proto(data):
    solar_system_id = get_solar_system_from_proto(data.solar_system)
    faction = None
    if data.previous_owner.HasField('match_value'):
        faction = int(data.previous_owner.match_value.sequential)
    complex_type = None
    if data.archetype.HasField('match_value'):
        complex_type = data.archetype.match_value.sequential
    return {'solar_system': solar_system_id,
     'faction': faction,
     'complex_type': complex_type}


def construct_capture_fw_complex_proto(previous_owner, solar_system_id, archetype):
    method = ContributionConfiguration.CaptureFacWarComplex()
    matcher = method.contribution_methods.add()
    if previous_owner is None:
        matcher.previous_owner.any = True
    else:
        matcher.previous_owner.match_value.sequential = previous_owner
    add_solar_system_to_proto(solar_system_id, matcher)
    if archetype is None:
        matcher.archetype.any = True
    else:
        matcher.archetype.match_value.sequential = archetype
    return method


def construct_defend_fw_complex_dict_from_proto(data):
    solar_system_id = get_solar_system_from_proto(data.solar_system)
    faction = None
    if data.owner.HasField('match_value'):
        faction = int(data.owner.match_value.sequential)
    complex_type = None
    if data.archetype.HasField('match_value'):
        complex_type = data.archetype.match_value.sequential
    return {'solar_system': solar_system_id,
     'faction': faction,
     'complex_type': complex_type}


def construct_defend_fw_complex_proto(owner, solar_system_id, archetype):
    method = ContributionConfiguration.DefendFacWarComplex()
    matcher = method.contribution_methods.add()
    if owner is None:
        matcher.owner.any = True
    else:
        matcher.owner.match_value.sequential = owner
    add_solar_system_to_proto(solar_system_id, matcher)
    if archetype is None:
        matcher.archetype.any = True
    else:
        matcher.archetype.match_value.sequential = archetype
    return method


def construct_remote_repair_shield_proto(solar_system, ship, organization_type):
    method = ContributionConfiguration.RemoteShieldRepair()
    add_generic_ship_matchers(method, solar_system=solar_system, ship=ship, organization_type=organization_type)
    return method


def construct_remote_repair_armor_proto(solar_system, ship, organization_type):
    method = ContributionConfiguration.RemoteArmorRepair()
    add_generic_ship_matchers(method, solar_system=solar_system, ship=ship, organization_type=organization_type)
    return method


def construct_ship_lost_pvp_proto(solar_system, ship, organization_type):
    method = ContributionConfiguration.ShipLostPVP()
    add_generic_ship_matchers(method, solar_system=solar_system, ship=ship, organization_type=organization_type)
    return method


def construct_scan_signature_dict_from_proto(data):
    solar_system_id = get_solar_system_from_proto(data.solar_system)
    signature_type = None
    if data.signature_type.HasField('match_value'):
        signature_type = data.signature_type.match_value.sequential
    return {'solar_system': solar_system_id,
     'signature_type': signature_type}


def construct_scan_signature_proto(solar_system, signature_type):
    method = ContributionConfiguration.ScanSignature()
    matcher = method.contribution_methods.add()
    add_solar_system_to_proto(solar_system, matcher)
    if signature_type is None:
        matcher.signature_type.any = True
    else:
        matcher.signature_type.match_value.sequential = signature_type
    return method


def construct_manufacture_items_dict_from_proto(data):
    item_type = None
    if data.item_type.HasField('item_type'):
        item_type = int(data.item_type.item_type.sequential)
    owner = ON_BEHALF_OF_CORP
    if data.job_owner_type.HasField('match_any_character'):
        owner = ON_BEHALF_OF_SELF
    job_location = None
    if data.job_location.HasField('station'):
        job_location = data.job_location.station.sequential
    elif data.job_location.HasField('structure'):
        job_location = data.job_location.structure.sequential
    return {'item_type': item_type,
     'owner': owner,
     'facility_location': job_location}


def construct_manufacture_items_proto(item_type, owner, facility_location):
    method = ContributionConfiguration.InstallManufacturingJob()
    matcher = method.contribution_methods.add()
    if item_type:
        matcher.item_type.item_type.sequential = item_type
    else:
        matcher.item_type.any = True
    if owner == ON_BEHALF_OF_SELF:
        matcher.job_owner_type.match_any_character = True
    elif owner == ON_BEHALF_OF_CORP:
        matcher.job_owner_type.match_any_corporation = True
    if facility_location is None:
        matcher.job_location.any = True
    elif idCheckers.IsStation(facility_location):
        matcher.job_location.station.sequential = facility_location
    else:
        matcher.job_location.structure.sequential = facility_location
    return method


def construct_salvage_wreck_dict_from_proto(data):
    solar_system_id = get_solar_system_from_proto(data.solar_system)
    return {'solar_system': solar_system_id}


def construct_salvage_wreck_proto(solar_system):
    method = ContributionConfiguration.SalvageWreck()
    matcher = method.contribution_methods.add()
    add_solar_system_to_proto(solar_system, matcher)
    return method


def construct_earn_loyalty_points_proto(corporations):
    method = CorpGoalContributionConfiguration.EarnLoyaltyPoints()
    add_corporations_to_proto(corporations, method.corporations)
    return method


def construct_deprecated_earn_loyalty_points_dict_from_proto(data):
    corporation_id = None
    if data.corporation.HasField('match_value'):
        corporation_id = [int(data.corporation.match_value.sequential)]
    return {'corporation_id': corporation_id}


def construct_earn_loyalty_points_dict_from_proto(data):
    return {'corporation_id': get_corporations_from_proto(data.corporations)}


def construct_ship_insurance_proto(solar_systems, ships, identities, conflict_type, cover_implants):
    method = CorpGoalContributionConfiguration.ShipInsurance()
    add_solar_systems_to_proto(solar_systems, method.solar_systems)
    add_ships_to_proto(ships, method.ships)
    add_owner_identities_to_proto(identities, method.killer_identities)
    add_conflict_type_to_proto(conflict_type, method.conflict_type)
    method.include_implants = cover_implants
    return method


def construct_ship_insurance_dict_from_proto(data):
    return {'solar_system': get_solar_systems_from_proto(data.solar_systems),
     'ship': get_ships_from_proto(data.ships),
     'organization': get_owner_identities_from_proto(data.killer_identities),
     'conflict_type': get_conflict_type_from_proto(data.conflict_type),
     'cover_implants': data.include_implants}


def add_contribution_method(request, method_id, data = None):
    if method_id == ContributionMethodTypes.MANUAL:
        config = ContributionConfiguration.ManualContributionConfiguration()
        request.contribution_configuration.manual.CopyFrom(config)
    elif ContributionMethodTypes.DELIVER_ITEM == method_id:
        method = construct_deliver_item_proto(item_type=data.get('item_type'), office_id=data.get('office'))
        request.contribution_configuration.deliver_item.CopyFrom(method)
    elif method_id == ContributionMethodTypes.KILL_NPC:
        method = construct_kill_npc_proto(solar_system_id=data.get('solar_system'))
        request.contribution_configuration.kill_npc.CopyFrom(method)
    elif method_id == ContributionMethodTypes.MINE_ORE:
        method = construct_mine_ore_proto(solar_systems=data.get('solar_system'), ores=data.get('ore'))
        request.contribution_configuration.mined_ore.CopyFrom(method)
    elif method_id == ContributionMethodTypes.DAMAGE_SHIP:
        method = construct_damage_ship_proto(solar_systems=data.get('solar_system'), ships=data.get('ship'), identities=data.get('organization'))
        request.contribution_configuration.damaged_ship.CopyFrom(method)
    elif method_id == ContributionMethodTypes.DESTROY_PLAYER_SHIP:
        method = construct_destroy_player_ship_proto(solar_systems=data.get('solar_system'), ships=data.get('ship'), identities=data.get('organization'))
        request.contribution_configuration.pvp_destroyed_ship.CopyFrom(method)
    elif method_id == ContributionMethodTypes.CAPTURE_FACWAR_COMPLEX:
        method = construct_capture_fw_complex_proto(previous_owner=data.get('faction'), solar_system_id=data.get('solar_system'), archetype=data.get('complex_type'))
        request.contribution_configuration.fw_capture.CopyFrom(method)
    elif method_id == ContributionMethodTypes.DEFEND_FACWAR_COMPLEX:
        method = construct_defend_fw_complex_proto(owner=data.get('faction'), solar_system_id=data.get('solar_system'), archetype=data.get('complex_type'))
        request.contribution_configuration.fw_defend.CopyFrom(method)
    elif method_id == ContributionMethodTypes.REMOTE_REPAIR_SHIELD:
        method = construct_remote_repair_shield_proto(solar_system=data.get('solar_system'), ship=data.get('ship'), organization_type=data.get('organization'))
        request.contribution_configuration.remote_shield_repair.CopyFrom(method)
    elif method_id == ContributionMethodTypes.REMOTE_REPAIR_ARMOR:
        method = construct_remote_repair_armor_proto(solar_system=data.get('solar_system'), ship=data.get('ship'), organization_type=data.get('organization'))
        request.contribution_configuration.remote_armor_repair.CopyFrom(method)
    elif method_id == ContributionMethodTypes.MANUFACTURE_ITEM:
        method = construct_manufacture_items_proto(item_type=data.get('item_type'), owner=data.get('owner'), facility_location=data.get('facility_location'))
        request.contribution_configuration.install_manufacturing_job.CopyFrom(method)
    elif method_id == ContributionMethodTypes.SCAN_SIGNATURE:
        method = construct_scan_signature_proto(solar_system=data.get('solar_system'), signature_type=data.get('signature_type'))
        request.contribution_configuration.scan_signature.CopyFrom(method)
    elif method_id == ContributionMethodTypes.COMPLETE_GOAL:
        config = ContributionConfiguration.CompleteGoal()
        request.contribution_configuration.complete_goal.CopyFrom(config)
    elif method_id == ContributionMethodTypes.SALVAGE_WRECK:
        method = construct_salvage_wreck_proto(solar_system=data.get('solar_system'))
        request.contribution_configuration.salvage_wreck.CopyFrom(method)
    elif method_id == ContributionMethodTypes.EARN_LOYALTY_POINTS:
        method = construct_earn_loyalty_points_proto(corporations=data.get('corporation_id'))
        request.contribution_configuration.earned_loyaltypoints.CopyFrom(method)
    elif method_id == ContributionMethodTypes.SHIP_LOSS:
        method = construct_ship_lost_pvp_proto(solar_system=data.get('solar_system'), ship=data.get('ship'), organization_type=data.get('organization'))
        request.contribution_configuration.ship_lost_pvp.CopyFrom(method)
    elif method_id == ContributionMethodTypes.SHIP_INSURANCE:
        method = construct_ship_insurance_proto(solar_systems=data.get('solar_system'), ships=data.get('ship'), identities=data.get('organization'), conflict_type=data.get('conflict_type'), cover_implants=data.get('cover_implants'))
        request.contribution_configuration.ship_insurance.CopyFrom(method)
    else:
        raise ContributionMethodTypeNotSupported(u'Method type {} not supported'.format(method_id))


def _find_contribution_method_id(config):
    if config.HasField('manual'):
        return (ContributionMethodTypes.MANUAL, config.manual)
    if config.HasField('deliver_item'):
        field_dict = construct_deliver_item_dict_from_proto(config.deliver_item.contribution_methods[0])
        return (ContributionMethodTypes.DELIVER_ITEM, field_dict)
    if config.HasField('kill_npc'):
        field_dict = construct_kill_npc_dict_from_proto(config.kill_npc.contribution_methods[0])
        return (ContributionMethodTypes.KILL_NPC, field_dict)
    if config.HasField('mine_ore'):
        field_dict = construct_deprecated_mine_ore_dict_from_proto(config.mine_ore.contribution_methods[0])
        return (ContributionMethodTypes.MINE_ORE, field_dict)
    if config.HasField('mined_ore'):
        field_dict = construct_mine_ore_dict_from_proto(config.mined_ore)
        return (ContributionMethodTypes.MINE_ORE, field_dict)
    if config.HasField('damage_ship'):
        field_dict = construct_deprecated_damage_ship_dict_from_proto(config.damage_ship.contribution_methods[0])
        return (ContributionMethodTypes.DAMAGE_SHIP, field_dict)
    if config.HasField('damaged_ship'):
        field_dict = construct_damage_ship_dict_from_proto(config.damaged_ship)
        return (ContributionMethodTypes.DAMAGE_SHIP, field_dict)
    if config.HasField('destroy_player_ship'):
        field_dict = construct_deprecated_destroy_player_ship_dict_from_proto(config.destroy_player_ship.contribution_methods[0])
        return (ContributionMethodTypes.DESTROY_PLAYER_SHIP, field_dict)
    if config.HasField('pvp_destroyed_ship'):
        field_dict = construct_destroy_player_ship_dict_from_proto(config.pvp_destroyed_ship)
        return (ContributionMethodTypes.DESTROY_PLAYER_SHIP, field_dict)
    if config.HasField('fw_capture'):
        field_dict = construct_capture_fw_complex_dict_from_proto(config.fw_capture.contribution_methods[0])
        return (ContributionMethodTypes.CAPTURE_FACWAR_COMPLEX, field_dict)
    if config.HasField('fw_defend'):
        field_dict = construct_defend_fw_complex_dict_from_proto(config.fw_defend.contribution_methods[0])
        return (ContributionMethodTypes.DEFEND_FACWAR_COMPLEX, field_dict)
    if config.HasField('remote_shield_repair'):
        field_dict = construct_generic_ship_dict_from_proto(config.remote_shield_repair.contribution_methods[0])
        return (ContributionMethodTypes.REMOTE_REPAIR_SHIELD, field_dict)
    if config.HasField('remote_armor_repair'):
        field_dict = construct_generic_ship_dict_from_proto(config.remote_armor_repair.contribution_methods[0])
        return (ContributionMethodTypes.REMOTE_REPAIR_ARMOR, field_dict)
    if config.HasField('scan_signature'):
        field_dict = construct_scan_signature_dict_from_proto(config.scan_signature.contribution_methods[0])
        return (ContributionMethodTypes.SCAN_SIGNATURE, field_dict)
    if config.HasField('install_manufacturing_job'):
        field_dict = construct_manufacture_items_dict_from_proto(config.install_manufacturing_job.contribution_methods[0])
        return (ContributionMethodTypes.MANUFACTURE_ITEM, field_dict)
    if config.HasField('complete_goal'):
        return (ContributionMethodTypes.COMPLETE_GOAL, config.complete_goal)
    if config.HasField('salvage_wreck'):
        field_dict = construct_salvage_wreck_dict_from_proto(config.salvage_wreck.contribution_methods[0])
        return (ContributionMethodTypes.SALVAGE_WRECK, field_dict)
    if config.HasField('earn_loyalty_points'):
        field_dict = construct_deprecated_earn_loyalty_points_dict_from_proto(config.earn_loyalty_points.contribution_methods[0])
        return (ContributionMethodTypes.EARN_LOYALTY_POINTS, field_dict)
    if config.HasField('earned_loyaltypoints'):
        field_dict = construct_earn_loyalty_points_dict_from_proto(config.earned_loyaltypoints)
        return (ContributionMethodTypes.EARN_LOYALTY_POINTS, field_dict)
    if config.HasField('ship_lost_pvp'):
        field_dict = construct_generic_ship_dict_from_proto(config.ship_lost_pvp.contribution_methods[0])
        return (ContributionMethodTypes.SHIP_LOSS, field_dict)
    if config.HasField('ship_insurance'):
        field_dict = construct_ship_insurance_dict_from_proto(config.ship_insurance)
        return (ContributionMethodTypes.SHIP_INSURANCE, field_dict)


def format_payments(payments):
    if not payments:
        return None
    payment = payments[0]
    return {'amount_per_unit': get_single_value_from_split_precision_message(payment.unit.amount),
     'asset_id': uuid.UUID(bytes=payment.asset.uuid)}


def _format_organization(org_data):
    if org_data.HasField('corporation'):
        return (OrganizationType.CORPORATION, org_data.corporation.sequential)
    elif org_data.HasField('character'):
        return (OrganizationType.CHARACTER, org_data.character.sequential)
    else:
        return (None, None)


def goal_formatter(goal_id, goal):
    client_method_id, contribution_fields = _find_contribution_method_id(goal.contribution_config)
    reward = format_payments(goal.payment)
    assigner_type, assigner_id = _format_organization(goal.assigner)
    assignee_type, assignee_id = _format_organization(goal.assignee)
    if goal.HasField('user_input_name'):
        name = goal.user_input_name
    elif goal.HasField('name_message'):
        name = GetByMessageID(goal.name_message)
    else:
        name = None
    if goal.HasField('user_input_description'):
        description = goal.user_input_description
    elif goal.HasField('description_message'):
        description = GetByMessageID(goal.description_message)
    else:
        description = None
    return {'goal_id': goal_id,
     'created': goal.created.ToDatetime(),
     'name': name,
     'description': description,
     'state': goal.state,
     'desired_progress': goal.progress.desired,
     'current_progress': goal.progress.current,
     'creator': goal.creator.sequential,
     'assigner_organization_type': assigner_type,
     'assigner_organization_id': assigner_id,
     'assignee_organization_type': assignee_type,
     'assignee_organization_id': assignee_id,
     'method_id': client_method_id,
     'contribution_fields': contribution_fields,
     'career_path': CAREER_PATH_IDS[goal.career],
     'finish_time': goal.finished.ToDatetime() if goal.HasField('finished') else None,
     'due_time': goal.due.ToDatetime() if goal.HasField('due') else None,
     'reward': reward,
     'ui_annotations': {x.key:x.value for x in goal.ui_annotations},
     'participation_limit': None if goal.HasField('unlimited') else goal.limit,
     'coverage_limit': None if goal.HasField('contribution_unlimited') else goal.contribution_limit,
     'multiplier': None if not goal.HasField('scalar') else goal.scalar}
