#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\facwarCommon.py
import math
from collections import defaultdict
import eve.common.lib.appConst as const
from caching import Memoize
from characterdata.factions import iter_factions
from eveprefs import boot
ALLY_COLOR_AGENCY = '#538EA6'
HOSTILE_COLOR_AGENCY = '#911E14'
BENEFIT_MARKETREDUCTION = 2
BENEFIT_INDUSTRYCOST = 3
BENEFITS_BY_LEVEL = {0: ((BENEFIT_MARKETREDUCTION, 0), (BENEFIT_INDUSTRYCOST, 0)),
 1: ((BENEFIT_MARKETREDUCTION, 10), (BENEFIT_INDUSTRYCOST, -10)),
 2: ((BENEFIT_MARKETREDUCTION, 20), (BENEFIT_INDUSTRYCOST, -20)),
 3: ((BENEFIT_MARKETREDUCTION, 30), (BENEFIT_INDUSTRYCOST, -30)),
 4: ((BENEFIT_MARKETREDUCTION, 40), (BENEFIT_INDUSTRYCOST, -40)),
 5: ((BENEFIT_MARKETREDUCTION, 50), (BENEFIT_INDUSTRYCOST, -50))}
_OCCUPIER_FW_FACTIONS = frozenset({const.factionAmarrEmpire,
 const.factionCaldariState,
 const.factionGallenteFederation,
 const.factionMinmatarRepublic})
_PIRATE_FW_FACTIONS = frozenset({const.factionAngelCartel, const.factionGuristasPirates})
_ALL_WARFARE_FACTIONS = frozenset(_OCCUPIER_FW_FACTIONS.union(_PIRATE_FW_FACTIONS))
ANTIPIRATE_DUNGEON_CAPTURE_FACTION = const.factionMordusLegion
_ANTI_PIRATE_FW_FACTIONS = frozenset({ANTIPIRATE_DUNGEON_CAPTURE_FACTION, const.factionORE})
_OCCUPATION_ENEMY_BY_FACTION_ID = {}
for factionA, factionB in [(const.factionAmarrEmpire, const.factionMinmatarRepublic), (const.factionCaldariState, const.factionGallenteFederation)]:
    _OCCUPATION_ENEMY_BY_FACTION_ID[factionA] = factionB
    _OCCUPATION_ENEMY_BY_FACTION_ID[factionB] = factionA

_INSURGENCY_ENEMIES_BY_FACTION_ID = {}
for pirateFaction, enemyFactions in {const.factionAngelCartel: [const.factionAmarrEmpire, const.factionMinmatarRepublic],
 const.factionGuristasPirates: [const.factionCaldariState, const.factionGallenteFederation]}.iteritems():
    _INSURGENCY_ENEMIES_BY_FACTION_ID[pirateFaction] = enemyFactions
    for enemyFaction in enemyFactions:
        _INSURGENCY_ENEMIES_BY_FACTION_ID[enemyFaction] = [pirateFaction]

_ALL_ENEMIES_BY_FACTION_ID = defaultdict(list)
for factionA, factionB in _OCCUPATION_ENEMY_BY_FACTION_ID.iteritems():
    _ALL_ENEMIES_BY_FACTION_ID[factionA].append(factionB)

for factionA, otherFactions in _INSURGENCY_ENEMIES_BY_FACTION_ID.iteritems():
    _ALL_ENEMIES_BY_FACTION_ID[factionA].extend(otherFactions)

def GetOccupierFWFactions():
    return _OCCUPIER_FW_FACTIONS


def IsOccupierFWFaction(factionID):
    return factionID in _OCCUPIER_FW_FACTIONS


def GetPirateFWFactions():
    return _PIRATE_FW_FACTIONS


def IsPirateFWFaction(factionID):
    return factionID in _PIRATE_FW_FACTIONS


def IsAntiPirateFaction(factionID):
    return factionID in _ANTI_PIRATE_FW_FACTIONS


def GetAllFWFactions():
    return _ALL_WARFARE_FACTIONS


def IsAnyFWFaction(factionID):
    return factionID in _ALL_WARFARE_FACTIONS


def IsOccupierEnemyFaction(factionIDA, factionIDB):
    occupierEnemyID = _OCCUPATION_ENEMY_BY_FACTION_ID.get(factionIDA, None)
    return occupierEnemyID is not None and factionIDB == occupierEnemyID


def IsInsurgencyEnemyFaction(factionIDA, factionIDB):
    pirateEnemyIDs = _INSURGENCY_ENEMIES_BY_FACTION_ID.get(factionIDA, [])
    return factionIDB in pirateEnemyIDs


def IsCombatEnemyFaction(factionIDA, factionIDB):
    allEnemyIDs = _ALL_ENEMIES_BY_FACTION_ID.get(factionIDA, [])
    return factionIDB in allEnemyIDs


def IsSameFwFaction(factionIDA, factionIDB):
    return factionIDA == factionIDB and factionIDA in _ALL_WARFARE_FACTIONS


def HasPirateVsAntiPirateRelationship(factionIDA, factionIDB):
    if IsPirateFWFaction(factionIDA) and IsAntiPirateFaction(factionIDB):
        return True
    if IsAntiPirateFaction(factionIDA) and IsPirateFWFaction(factionIDB):
        return True
    return False


def GetOccupationEnemyFaction(factionID):
    mainEnemy = _OCCUPATION_ENEMY_BY_FACTION_ID.get(factionID)
    if mainEnemy:
        return mainEnemy
    raise RuntimeError("I don't know who the main enemy of", factionID, "is, are you sure it's a faction that is involved in factional warfare?")


def GetInsurgencyEnemyFactions(factionID):
    return _INSURGENCY_ENEMIES_BY_FACTION_ID.get(factionID, [])


def GetCombatEnemyFactions(factionID):
    return _ALL_ENEMIES_BY_FACTION_ID.get(factionID, [])


def GetAllFwEnemies():
    return {k:v for k, v in _ALL_ENEMIES_BY_FACTION_ID.iteritems()}


def GetSolarSystemUpgradeLevel(solarSystemID, factionID):
    if boot.role == 'client':
        facwarSvc = sm.GetService('facwar')
        lps = facwarSvc.GetSolarSystemLPs(solarSystemID)
        if lps == 0:
            return 0
        if factionID is not None:
            occupierID = facwarSvc.GetSystemOccupier(solarSystemID)
            if occupierID is not None and IsCombatEnemyFaction(factionID, occupierID):
                lps = 0
    else:
        facWarMgr = sm.GetService('facWarMgr')
        lps = facWarMgr.GetSolarSystemLPsEx(solarSystemID)
        if lps == 0:
            return 0
        if factionID is not None:
            fwWarzoneBroker = sm.GetService('fwWarzoneBroker')
            occupationState = fwWarzoneBroker.GetSolarsystemOccupationState(solarSystemID)
            if occupationState is not None and IsCombatEnemyFaction(factionID, occupationState.occupierID):
                lps = 0
    return GetLPUpgradeLevel(lps)


def GetLPUpgradeLevel(loyaltyPoints):
    if loyaltyPoints >= const.facwarSolarSystemMaxLPPool:
        return const.facWarSolarSystemMaxLevel
    if loyaltyPoints == 0:
        return 0
    for i, threshold in enumerate(const.facwarSolarSystemUpgradeThresholds):
        if loyaltyPoints < threshold:
            return i - 1


def GetAdjustedFeePercentage(solarSystemID, factionID, feePercentage):
    level = GetSolarSystemUpgradeLevel(solarSystemID, factionID)
    return feePercentage * (1 - 0.1 * level)


def GetDonationTax(factionID):
    if not IsOccupierFWFaction(factionID):
        return 0.0
    if boot.role == 'client':
        facwarSvc = sm.GetService('facwar')
        zoneInfo = facwarSvc.GetFacWarZoneInfo(factionID)
        percentControlled = zoneInfo.factionPoints / float(zoneInfo.maxWarZonePoints)
    else:
        facWarZoneMgr = sm.GetService('facWarZoneMgr')
        points, maxPoints = facWarZoneMgr.GetZonePoints(factionID)
        percentControlled = points / float(maxPoints)
    rawTax = 5 * math.pow(percentControlled, 3)
    donationTax = round(1 - 1 / (1 + rawTax), 2)
    return donationTax


@Memoize
def GetFwNpcCorpsByFactionID():
    warFactions = {}
    for factionID, faction in iter_factions():
        if faction.militiaCorporationID:
            warFactions[factionID] = faction.militiaCorporationID

    return warFactions


def GetFwFactionIDForNpcCorp(corpID):
    for factionID, militiaCorpID in GetFwNpcCorpsByFactionID().iteritems():
        if militiaCorpID == corpID:
            return factionID


def GetFwCorpIdFromFactionID(factionID):
    return GetFwNpcCorpsByFactionID().get(factionID, 0)


def IsFwNpcCorp(corpID):
    return corpID in GetFwNpcCorpsByFactionID().values()


minStandingsForPirateFactions = {const.factionGuristasPirates: -2.0001,
 const.factionAngelCartel: -2.0001}

def GetMinStandingsForSpecialFactions():
    return minStandingsForPirateFactions


def GetFacwarMinStandingsToJoin(factionID):
    return minStandingsForPirateFactions.get(factionID, const.facwarMinStandingsToJoinDefault)


def GetCaptureFaction(warFactionID):
    if warFactionID in GetOccupierFWFactions():
        return ANTIPIRATE_DUNGEON_CAPTURE_FACTION
    if warFactionID in GetPirateFWFactions():
        return warFactionID
