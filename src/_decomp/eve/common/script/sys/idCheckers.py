#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\sys\idCheckers.py
import eve.common.lib.appConst as appConst
from eveprefs import boot
from inventorycommon.const import *
from eve.common.lib.appConst import ALSCActionAssemble, ALSCActionRepackage, ALSCActionSetName, ALSCActionMove, ALSCActionSetPassword, ALSCActionAdd, ALSCActionLock, ALSCActionUnlock, ALSCActionEnterPassword, ALSCActionConfigure, locationCharacterGraveyard, locationCorporationGraveyard, locationStructureGraveyard
from caching.memoize import Memoize
from eveuniverse.security import SecurityClassFromLevel, securityClassHighSec, securityClassLowSec, securityClassZeroSec
minDustUser = 1000000000

def IsRegion(itemID):
    return minRegion <= itemID <= maxRegion


def IsConstellation(itemID):
    return minConstellation <= itemID <= maxConstellation


def IsSolarSystem(itemID):
    return minSolarSystem <= itemID <= maxSolarSystem


def IsCelestial(itemID):
    return minUniverseCelestial <= itemID <= maxUniverseCelestial


def IsStation(itemID):
    return minStation <= itemID <= maxStation


def IsUniverseCelestial(itemID):
    return minUniverseCelestial <= itemID <= maxUniverseCelestial


def IsDistrict(itemID):
    return minDistrict <= itemID <= maxDistrict


def IsStargate(itemID):
    return minStargate <= itemID <= maxStargate


def IsTrading(itemID):
    return minTrading <= itemID <= maxTrading


def IsOfficeFolder(itemID):
    return minOfficeFolder <= itemID <= maxOfficeFolder


def IsFactoryFolder(itemID):
    return minFactoryFolder <= itemID <= maxFactoryFolder


def IsUniverseAsteroid(itemID):
    return minUniverseAsteroid <= itemID <= maxUniverseAsteroid


def IsControlBunker(itemID):
    return minControlBunker <= itemID <= maxControlBunker


def IsFakeItem(itemID):
    return itemID > minFakeItem


def IsPlayerItem(itemID):
    return minPlayerItem <= itemID < minFakeItem


def IsKnownSpaceSystem(itemID):
    return mapKnownSpaceSystemMin <= itemID <= mapKnownSpaceSystemMax


def IsKnownSpaceConstellation(itemID):
    return mapKnownSpaceConstellationMin <= itemID <= mapKnownSpaceConstellationMax


def IsKnownSpaceRegion(itemID):
    return mapKnownSpaceRegionMin <= itemID <= mapKnownSpaceRegionMax


def IsWormholeSystem(itemID):
    return mapWormholeSystemMin <= itemID <= mapWormholeSystemMax


def IsWormholeConstellation(itemID):
    return mapWormholeConstellationMin <= itemID <= mapWormholeConstellationMax


def IsWormholeRegion(itemID):
    return mapWormholeRegionMin <= itemID <= mapWormholeRegionMax


def IsZarzakh(itemID):
    return itemID == solarSystemZarzakh


def IsAbyssalSpaceSystem(itemID):
    return mapAbyssalSystemMin <= itemID <= mapAbyssalSystemMax


def IsAbyssalSpaceRegion(itemID):
    return mapAbyssalRegionMin <= itemID <= mapAbyssalRegionMax


def IsVoidSpaceRegion(itemID):
    return mapVoidRegionMin <= itemID <= mapVoidRegionMax


def IsVoidSpaceConstellation(itemID):
    return mapVoidConstellationMin <= itemID <= mapVoidConstellationMax


def IsVoidSpaceSystem(itemID):
    return mapVoidSystemMin <= itemID <= mapVoidSystemMax


def IsLocalIdentity(itemID):
    return IsSystemOrNPC(itemID)


def IsTriglavianSystem(solarSystemID):
    solarSystem = cfg.mapSystemCache.get(solarSystemID, None)
    if solarSystem:
        return getattr(solarSystem, 'factionID', None) == appConst.factionTriglavian
    return False


def IsStationInTriglavianSystem(stationID):
    if not IsStation(stationID):
        return False
    return IsTriglavianSystem(cfg.evelocations.Get(stationID).solarSystemID)


def IsJoveSystem(solarSystemID):
    if solarSystemID:
        region = cfg.mapSystemCache.get(solarSystemID, None).regionID
        if region in (10000017, 10000019, 10000004):
            return True
    return False


def IsStationInJoveSystem(stationID):
    if not IsStation(stationID):
        return False
    return IsJoveSystem(cfg.evelocations.Get(stationID).solarSystemID)


def IsNewbieSystem(solarsystemID):
    default = [30002547,
     30001392,
     30002715,
     30003489,
     30005305,
     30004971,
     30001672,
     30002505,
     30000141,
     30003410,
     30005042,
     30001407]
    return solarsystemID in default


def IsCareerAgentSystem(solarsystemID):
    return solarsystemID in (30013489, 30021672, 30045042, 30030141, 30011392, 30011407, 30014971, 30045305, 30042715, 30012547, 30012505, 30023410)


def IsHighSecSystem(solarsystemID):
    return _GetSecurityClassForSolarSystem(solarsystemID) == securityClassHighSec


def IsLowSecSystem(solarsystemID):
    return _GetSecurityClassForSolarSystem(solarsystemID) == securityClassLowSec


def IsNullSecSystem(solarsystemID):
    return _GetSecurityClassForSolarSystem(solarsystemID) == securityClassZeroSec


def IsEmpireSystem(solarsystemID):
    return _GetSecurityClassForSolarSystem(solarsystemID) in (securityClassHighSec, securityClassLowSec)


@Memoize
def _GetSecurityClassForSolarSystem(solarsystemID):
    return SecurityClassFromLevel(cfg.mapSystemCache[solarsystemID].securityStatus)


def IsCharacter(ownerID):
    if ownerID is None:
        return 0
    if IsNPCCharacter(ownerID):
        return 1
    if IsEvePlayerCharacter(ownerID):
        return 1
    return 0


class CharacterNotFoundError(Exception):

    def __init__(self, characterID):
        self.characterID = characterID

    def __str__(self):
        return 'Failed to find character with ID %s' % self.characterID


def RaiseIfNotACharacter(characterID):
    if not IsCharacter(characterID):
        raise CharacterNotFoundError(characterID)


def IsCorporation(ownerID):
    if IsNPCCorporation(ownerID):
        return 1
    if IsPlayerCorporation(ownerID):
        return 1
    return 0


def IsAlliance(ownerID):
    if minPlayerAlliance <= ownerID <= maxPlayerAlliance:
        return 1
    if minPreInv64Items <= ownerID <= maxPreInv64Items:
        if boot.role == 'server' and sm.GetService('standingMgr').IsKnownToBeAPlayerCorp(ownerID):
            return 0
        try:
            return cfg.eveowners.Get(ownerID).IsAlliance()
        except KeyError:
            return 0

    return 0


def IsOwner(ownerID):
    if IsFaction(ownerID):
        return 1
    if IsNPCCorporation(ownerID):
        return 1
    if IsNPCCharacter(ownerID):
        return 1
    if IsNPC(ownerID):
        return 0
    if IsEvePlayerCharacter(ownerID):
        return 1
    if IsPlayerCorporation(ownerID):
        return 1
    if IsAlliance(ownerID):
        return 1
    return 0


def IsNPC(ownerID):
    return maxSystemItem < ownerID < minPlayerOwner


def IsSystem(ownerID):
    return ownerID <= maxSystemItem


def IsNPCCharacter(ownerID):
    return minAgent <= ownerID <= maxAgent


def IsSystemOrNPC(ownerID):
    return ownerID < minPlayerOwner


def IsFaction(ownerID):
    return minFaction <= ownerID < maxFaction


def IsPirateFaction(factionID):
    return factionID == appConst.factionGallenteFederation


def IsEvePlayerCharacter(ownerID):
    if minPlayerCharacterGen3 <= ownerID <= maxPlayerCharacterGen3:
        return 1
    if minPlayerCharacterGen2 <= ownerID <= maxPlayerCharacterGen2:
        return 1
    if minPreInv64Items <= ownerID <= maxPreInv64Items:
        if boot.role == 'server' and sm.GetService('standingMgr').IsKnownToBeAPlayerCorp(ownerID):
            return 0
        try:
            return cfg.eveowners.Get(ownerID).IsCharacter()
        except KeyError:
            return 0

    return 0


def IsPlayerOwner(ownerID):
    return minPlayerOwner <= ownerID <= maxPlayerOwner


def IsNPCCorporation(ownerID):
    return minNPCCorporation <= ownerID <= maxNPCCorporation


def IsStarterNPCCorporation(ownerID):
    return ownerID in (1000166, 1000165, 1000077, 1000167, 1000045, 1000044, 1000168, 1000115, 1000169, 1000170, 1000172, 1000171)


def IsPlayerCorporation(ownerID):
    if minPlayerCorporation <= ownerID <= maxPlayerCorporation:
        return 1
    if minPreInv64Items <= ownerID <= maxPreInv64Items:
        if boot.role == 'server' and sm.GetService('standingMgr').IsKnownToBeAPlayerCorp(ownerID):
            return 1
        try:
            return cfg.eveowners.Get(ownerID).IsCorporation()
        except KeyError:
            return 0

    return 0


def IsEveUser(userID):
    return userID < minDustUser


def IsDustUser(userID):
    return userID > minDustUser


def IsJunkLocation(locationID):
    if locationID >= 2000:
        return 0
    elif locationID in (6, 8, 10, 23, 25):
        return 1
    elif 1000 < locationID < 2000:
        return 1
    elif locationID == doomheimStationID:
        return 1
    else:
        return 0


def GetLootChanceByAreaOfspace(locationID):
    if IsWormholeSystem(locationID):
        dropChance = 0.5
    elif IsLowSecSystem(locationID):
        dropChance = 0.5
    elif IsHighSecSystem(locationID):
        dropChance = 0.5
    elif IsTriglavianSystem(locationID):
        dropChance = 0.5
    elif IsNullSecSystem(locationID) and not IsWormholeSystem(locationID) and not IsTriglavianSystem(locationID):
        dropChance = 0.5
    else:
        dropChance = 0.5
    return dropChance


def IsDustType(typeID):
    return typeID > minDustTypeID


def IsOrbital(categoryID):
    return categoryID == categoryOrbital


def IsStarbase(categoryID):
    return categoryID == categoryStarbase


def IsShip(categoryID):
    return categoryID == categoryShip


def IsShipType(typeID):
    from evetypes import GetCategoryID
    return IsShip(GetCategoryID(typeID))


def IsDrone(categoryID):
    return categoryID == categoryDrone


def IsDroneType(typeID):
    from evetypes import GetCategoryID
    return IsDrone(GetCategoryID(typeID))


def IsFighter(categoryID):
    return categoryID == categoryFighter


def IsFighterType(typeID):
    from evetypes import GetCategoryID
    return IsFighter(GetCategoryID(typeID))


def IsDroneOrFighter(categoryID):
    return categoryID in [categoryDrone, categoryFighter]


def IsDroneOrFighterType(typeID):
    from evetypes import GetCategoryID
    return IsDroneOrFighter(GetCategoryID(typeID))


def IsLogisticDrone(typeID):
    from evetypes import GetGroupID
    return GetGroupID(typeID) == groupLogisticDrone


def IsSkinType(typeID):
    from evetypes import GetCategoryID, Exists
    if not Exists(typeID):
        return False
    return GetCategoryID(typeID) == categoryShipSkin


def IsStructure(categoryID):
    return categoryID == categoryStructure


def IsStructureType(typeID):
    from evetypes import GetCategoryID
    return IsStructure(GetCategoryID(typeID))


def IsWarpVectorType(typeID):
    from evetypes import GetGroupID
    return GetGroupID(typeID) == groupWarpVectorItems


def IsDockableStructure(typeID):
    from evetypes import GetCategoryID
    from structures.types import IsFlexStructure
    return IsStructure(GetCategoryID(typeID)) and not IsFlexStructure(typeID)


def IsDockableLocationType(typeID):
    from evetypes import GetGroupID, GetCategoryID
    from structures.types import IsFlexStructure
    if GetGroupID(typeID) == groupStation:
        return True
    if GetCategoryID(typeID) == categoryStructure:
        if IsFlexStructure(typeID):
            return False
        return True
    return False


def IsDeprecatedStation(stationTypeID):
    return stationTypeID in [typeCaldariResearchOutpost,
     typeAmarrFactoryOutpost,
     typeGallenteAdministrativeOutpost,
     typeMinmatarServiceOutpost,
     typeStationConquerableOne,
     typeStationConquerableTwo,
     typeStationConquerableThree]


def IsCharge(categoryID):
    return categoryID in [categoryCharge, groupFrequencyCrystal]


def IsChargeType(typeID):
    from evetypes import GetCategoryID
    return IsCharge(GetCategoryID(typeID))


def IsModule(categoryID):
    return categoryID == categoryModule


def IsModuleType(typeID):
    from evetypes import GetCategoryID
    return IsModule(GetCategoryID(typeID))


def IsCapsule(groupID):
    return groupID == groupCapsule


def IsNormalCapsule(typeID):
    return typeID == typeCapsule


def IsGoldenCapsule(typeID):
    return typeID == typeCapsuleGolden


def IsNewbieShip(groupID):
    return groupID == groupCorvette


def IsPlex(typeID):
    return typeID == typePlex


def IsSkyhook(typeID):
    return typeID == typeSkyhook


def IsAutoMoonMiner(typeID):
    return typeID == typeUpwellAutoMoonMiner


def IsMercenaryDen(groupID):
    return groupID == groupMercenaryDen


def IsAssembledShip(categoryID, singleton):
    return singleton and categoryID == categoryShip


def IsALSCActionAssemble(id):
    return id == ALSCActionAssemble


def IsALSCActionRepackage(id):
    return id == ALSCActionRepackage


def IsALSCActionSetName(id):
    return id == ALSCActionSetName


def IsALSCActionMove(id):
    return id == ALSCActionMove


def IsALSCActionSetPassword(id):
    return id == ALSCActionSetPassword


def IsALSCActionAdd(id):
    return id == ALSCActionAdd


def IsALSCActionLock(id):
    return id == ALSCActionLock


def IsALSCActionUnlock(id):
    return id == ALSCActionUnlock


def IsALSCActionEnterPassword(id):
    return id == ALSCActionEnterPassword


def IsALSCActionConfigure(id):
    return id == ALSCActionConfigure


def IsLocationCharacterGraveyard(id):
    return id == locationCharacterGraveyard


def IsLocationCorporationGraveyard(id):
    return id == locationCorporationGraveyard


def IsLocationStructureGraveyard(id):
    return id == locationStructureGraveyard


def IsAssetSafetyWrap(item):
    return item.typeID == typeAssetSafetyWrap


def IsSkinDesignComponent(groupID):
    return groupID == groupShipSkinDesignComponents


def IsSequenceBinder(groupID):
    return groupID == groupSequenceBinders
