#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipgroup\__init__.py
from collections import defaultdict
from itertools import chain
import evetypes
from eve.common.lib import appConst
import inventorycommon.const as invConst
import localization
groupUndefined = 0
groupRookie = 4
groupFrigate = 8
groupNavyFrigate = 9
groupInterceptor = 10
groupAssault = 11
groupCovertOps = 12
groupElectronicAttack = 13
groupDestroyer = 14
groupInterdictor = 15
groupCruiser = 16
groupNavyCruiser = 17
groupRecon = 18
groupHeavyAssault = 19
groupHeavyInterdictor = 20
groupLogistics = 21
groupStrategicCruiser = 22
groupBattlecruiser = 23
groupCommandship = 24
groupNavyBattlecruiser = 25
groupBattleship = 26
groupBlackOps = 27
groupMarauder = 28
groupDreadnought = 32
groupCarrier = 33
groupTitan = 34
groupShuttle = 35
groupIndustrial = 36
groupFreighter = 37
groupJumpFreighter = 38
groupTransport = 40
groupMiningFrigate = 41
groupMiningBarge = 42
groupExhumers = 43
groupOreIndustrial = 44
groupIndustrialCommand = 45
groupCapitalIndustrial = 46
groupNavyBattleship = 47
groupExpeditionFrigate = 48
groupTacticalDestroyer = 50
groupCommandDestroyers = 93
groupLogisticsFrigates = 94
groupFlagCruiser = 96
groupNavyDestroyers = 2101
groupNavyDreadnoughts = 2102
groupLancerDreadnought = 2104
groupCapsule = 2107
ALL_GROUPS = [groupCapsule,
 groupRookie,
 groupFrigate,
 groupNavyFrigate,
 groupInterceptor,
 groupAssault,
 groupCovertOps,
 groupElectronicAttack,
 groupDestroyer,
 groupInterdictor,
 groupCruiser,
 groupNavyCruiser,
 groupRecon,
 groupHeavyAssault,
 groupHeavyInterdictor,
 groupLogistics,
 groupStrategicCruiser,
 groupBattlecruiser,
 groupCommandship,
 groupNavyBattlecruiser,
 groupBattleship,
 groupBlackOps,
 groupMarauder,
 groupDreadnought,
 groupCarrier,
 groupTitan,
 groupShuttle,
 groupIndustrial,
 groupFreighter,
 groupJumpFreighter,
 groupTransport,
 groupMiningFrigate,
 groupMiningBarge,
 groupExhumers,
 groupOreIndustrial,
 groupIndustrialCommand,
 groupCapitalIndustrial,
 groupNavyBattleship,
 groupExpeditionFrigate,
 groupTacticalDestroyer,
 groupCommandDestroyers,
 groupLogisticsFrigates,
 groupFlagCruiser,
 groupNavyDestroyers,
 groupNavyDreadnoughts,
 groupLancerDreadnought]
GROUPS_BY_SIZE = [groupCapsule,
 groupRookie,
 groupShuttle,
 groupFrigate,
 groupMiningFrigate,
 groupDestroyer,
 groupCruiser,
 groupBattlecruiser,
 groupMiningBarge,
 groupIndustrial,
 groupOreIndustrial,
 groupIndustrialCommand,
 groupCapitalIndustrial,
 groupBattleship,
 groupFreighter,
 groupDreadnought,
 groupCarrier,
 groupTitan]
SUB_GROUPS_BY_SHIP_GROUP = {groupFrigate: (groupNavyFrigate,
                groupInterceptor,
                groupAssault,
                groupCovertOps,
                groupElectronicAttack,
                groupLogisticsFrigates),
 groupDestroyer: (groupNavyDestroyers,
                  groupInterdictor,
                  groupCommandDestroyers,
                  groupTacticalDestroyer),
 groupCruiser: (groupNavyCruiser,
                groupRecon,
                groupHeavyAssault,
                groupHeavyInterdictor,
                groupLogistics,
                groupStrategicCruiser),
 groupBattlecruiser: (groupNavyBattlecruiser, groupCommandship),
 groupBattleship: (groupNavyBattleship, groupBlackOps, groupMarauder),
 groupDreadnought: (groupNavyDreadnoughts, groupLancerDreadnought),
 groupIndustrial: (groupTransport,),
 groupFreighter: (groupJumpFreighter,),
 groupMiningFrigate: (groupExpeditionFrigate,),
 groupMiningBarge: (groupExhumers,)}
SUB_GROUPS = list(chain(*SUB_GROUPS_BY_SHIP_GROUP.values()))
EVE_GROUP_TO_SHIP_TREE_GROUP = {invConst.groupCapsule: groupCapsule,
 invConst.groupCorvette: groupRookie,
 invConst.groupFrigate: groupFrigate,
 invConst.groupPrototypeExplorationShip: groupFrigate,
 invConst.groupAssaultFrigate: groupAssault,
 invConst.groupLogisticsFrigate: groupLogisticsFrigates,
 invConst.groupExpeditionFrigate: groupExpeditionFrigate,
 invConst.groupInterceptor: groupInterceptor,
 invConst.groupCovertOps: groupCovertOps,
 invConst.groupStealthBomber: groupCovertOps,
 invConst.groupElectronicAttackShips: groupElectronicAttack,
 invConst.groupDestroyer: groupDestroyer,
 invConst.groupCommandDestroyer: groupCommandDestroyers,
 invConst.groupTacticalDestroyer: groupTacticalDestroyer,
 invConst.groupInterdictor: groupInterdictor,
 invConst.groupHeavyInterdictors: groupHeavyInterdictor,
 invConst.groupCruiser: groupCruiser,
 invConst.groupLogistics: groupLogistics,
 invConst.groupFlagCruiser: groupFlagCruiser,
 invConst.groupHeavyAssaultCruiser: groupHeavyAssault,
 invConst.groupStrategicCruiser: groupStrategicCruiser,
 invConst.groupCombatReconShip: groupRecon,
 invConst.groupForceReconShip: groupRecon,
 invConst.groupBattlecruiser: groupBattlecruiser,
 invConst.groupAttackBattlecruiser: groupBattlecruiser,
 invConst.groupCommandShip: groupCommandship,
 invConst.groupIndustrialCommandShip: groupIndustrialCommand,
 invConst.groupBattleship: groupBattleship,
 invConst.groupBlackOps: groupBlackOps,
 invConst.groupMarauders: groupMarauder,
 invConst.groupDreadnought: groupDreadnought,
 invConst.groupLancerDreadnought: groupLancerDreadnought,
 invConst.groupCarrier: groupCarrier,
 invConst.groupSupercarrier: groupCarrier,
 invConst.groupForceAux: groupCarrier,
 invConst.groupTitan: groupTitan,
 invConst.groupShuttle: groupShuttle,
 invConst.groupFreighter: groupFreighter,
 invConst.groupJumpFreighter: groupJumpFreighter,
 invConst.groupTransportShip: groupTransport,
 invConst.groupBlockadeRunner: groupTransport,
 invConst.groupMiningBarge: groupMiningBarge,
 invConst.groupExhumer: groupExhumers,
 invConst.groupIndustrial: groupIndustrial,
 invConst.groupCapitalIndustrialShip: groupCapitalIndustrial}
_type_ids_by_faction_and_group_id = None
_type_ids_by_group_id = None
_ship_group_id_by_type_id = None

def _init_ship_type_id_dict():
    global _type_ids_by_faction_and_group_id
    global _type_ids_by_group_id
    _type_ids_by_faction_and_group_id = defaultdict(list)
    _type_ids_by_group_id = defaultdict(list)
    for group_id in evetypes.GetGroupIDsByCategory(appConst.categoryShip):
        if not evetypes.IsGroupPublishedByGroup(group_id):
            continue
        for type_id in evetypes.GetTypeIDsByGroup(group_id):
            try:
                if evetypes.IsPublished(type_id):
                    faction_id = evetypes.GetFactionID(type_id)
                    ship_group_id = evetypes.GetShipGroupID(type_id)
                    _type_ids_by_faction_and_group_id[faction_id, ship_group_id].append(type_id)
                    _type_ids_by_group_id[ship_group_id].append(type_id)
            except (KeyError, AttributeError):
                pass


def get_type_ids(ship_group_id, faction_id = None):
    if not _type_ids_by_faction_and_group_id:
        _init_ship_type_id_dict()
    if faction_id:
        return _type_ids_by_faction_and_group_id.get((faction_id, ship_group_id), [])
    else:
        return _type_ids_by_group_id.get(ship_group_id, [])


def _init_ship_group_id_dict():
    global _ship_group_id_by_type_id
    if _type_ids_by_faction_and_group_id is None:
        _init_ship_type_id_dict()
    _ship_group_id_by_type_id = {}
    for (_, ship_group_id), type_ids in _type_ids_by_faction_and_group_id.items():
        for typeID in type_ids:
            _ship_group_id_by_type_id[typeID] = ship_group_id


def get_ship_group_id(type_id):
    if _ship_group_id_by_type_id is None:
        _init_ship_group_id_dict()
    return _ship_group_id_by_type_id.get(type_id, None)


def get_type_ids_by_ship_group(faction_id = None):
    if _type_ids_by_faction_and_group_id is None:
        _init_ship_type_id_dict()
    ret = defaultdict(list)
    for (_faction_id, ship_group_id), type_ids in _type_ids_by_faction_and_group_id.items():
        if faction_id and faction_id != _faction_id:
            continue
        if ship_group_id in SUB_GROUPS:
            continue
        ret[ship_group_id].extend(type_ids)

    return ret


def get_ship_group_ids(ship_group_id = None, faction_id = None):
    if ship_group_id is not None:
        return SUB_GROUPS_BY_SHIP_GROUP.get(ship_group_id, [])
    else:
        return get_type_ids_by_ship_group(faction_id).keys()


def get_ship_class_id(type_id):
    ship_group_id = get_ship_group_id(type_id)
    if ship_group_id:
        return ship_group_id
    else:
        eve_group_id = evetypes.GetGroupID(type_id)
        return EVE_GROUP_TO_SHIP_TREE_GROUP.get(eve_group_id, groupUndefined)


def get_ship_group_name(type_id):
    ship_class_id = get_ship_class_id(type_id)
    if ship_class_id:
        return get_ship_tree_group_name(ship_class_id)
    else:
        return evetypes.GetGroupName(type_id)


def get_ship_tree_group_name(ship_group_id):
    return localization.GetByMessageID(cfg.infoBubbleGroups[ship_group_id]['nameID'])


def get_ship_tree_group_icon(ship_group_id):
    return cfg.infoBubbleGroups[ship_group_id]['icon']


def get_ship_tree_group_icon_small(ship_group_id):
    return cfg.infoBubbleGroups[ship_group_id]['iconSmall']
