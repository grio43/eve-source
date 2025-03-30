#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\structures\deployment.py
import math
import evetypes
import inventorycommon.const
from moonmining.const import MAXIMUM_MINING_BEACON_DISTANCE, MOONMINING_NOT_POSSIBLE, MOONMINING_POSSIBLE, MOONMINING_NEVER_AVAILABLE
from moonmining.miningBeacons import GetMiningBeaconPositionForMoon, FindMoonBeaconInRangeOfPosition
from eveprefs import boot
GROUP_DISTANCE = {inventorycommon.const.groupMoonMiningBeacon: 0,
 inventorycommon.const.groupBiomass: 5000,
 inventorycommon.const.groupWreck: 5000,
 inventorycommon.const.groupCargoContainer: 5000,
 inventorycommon.const.groupSpawnContainer: 5000,
 inventorycommon.const.groupSecureCargoContainer: 5000,
 inventorycommon.const.groupAuditLogSecureContainer: 5000,
 inventorycommon.const.groupFreightContainer: 5000,
 inventorycommon.const.groupIndustrialSupportFacility: 5000,
 inventorycommon.const.groupStationConversionMonument: 100000,
 inventorycommon.const.groupLargeCollidableObject: 100000,
 inventorycommon.const.groupEncounterSurveillanceSystem: 1000000,
 inventorycommon.const.groupStructureNpcEngineeringComplex: 2000000,
 inventorycommon.const.groupControlBunker: 1000000,
 inventorycommon.const.groupStructureJumpBridge: 500000,
 inventorycommon.const.groupStructureCynoJammer: 500000,
 inventorycommon.const.groupStructureCynoBeacon: 200000,
 inventorycommon.const.groupInfrastructureHub: 10000000}
CATEGORY_DISTANCES = {inventorycommon.const.categoryEntity: 5000,
 inventorycommon.const.categoryShip: 5000,
 inventorycommon.const.categoryDrone: 5000,
 inventorycommon.const.categoryFighter: 5000,
 inventorycommon.const.categoryDeployable: 5000,
 inventorycommon.const.categoryAsteroid: 5000,
 inventorycommon.const.categoryCelestial: 1000000,
 inventorycommon.const.categoryOrbital: 1000000,
 inventorycommon.const.categorySovereigntyStructure: 1000000,
 inventorycommon.const.categoryStation: 1000000,
 inventorycommon.const.categoryStarbase: 1000000,
 inventorycommon.const.categoryStructure: 1000000}
GROUP_MIN_DISTANCE_TO_STARGATE = {inventorycommon.const.groupStructureJumpBridge: 100000000}
GROUPS_REQUIRING_CONQUERABLE_SYSTEM = {inventorycommon.const.groupStructureJumpBridge, inventorycommon.const.groupStructureCynoJammer, inventorycommon.const.groupStructureCynoBeacon}
MAX_GROUP_PER_SOLARSYSTEM = {inventorycommon.const.groupStructureJumpBridge: 1,
 inventorycommon.const.groupStructureCynoJammer: 3,
 inventorycommon.const.groupStructureCynoBeacon: 1}
MAX_ADM_FOR_HOSTILE_DEPLOYMENT_BY_TYPE = {inventorycommon.const.typeCitadelAstrahus: 4,
 inventorycommon.const.typeEngineeringComplexRaitaru: 4,
 inventorycommon.const.typeRefineryAthanor: 4}
MINIMUM_MOON_DISTANCE = 4000000
WARPIN_POINT = 1
REAL_BALL = 2
JUMP_BRIDGE_LINK_CHARACTER = u'\xbb'
AUTOMOONMINER_DESIGNATED_SPOTS = 0
AUTOMOONMINER_BEACON = 1
DEPLOY_DIST_MAX = 800000

def GetDeploymentDistance(typeID):
    import evetypes
    groupID = evetypes.GetGroupID(typeID)
    categoryID = evetypes.GetCategoryID(typeID)
    return GROUP_DISTANCE.get(groupID, CATEGORY_DISTANCES.get(categoryID, 0))


def GetDeploymentConflictForBalls(ballpark, ballsAndItems, typeID, position):
    balls = [ (item.itemID,
     item.typeID,
     (ball.x, ball.y, ball.z),
     ball.radius,
     REAL_BALL) for ball, item in ballsAndItems ]
    balls += [ (item.itemID,
     item.typeID,
     xyz,
     0,
     WARPIN_POINT) for ball, item, xyz in ballpark.GetWarpinPoints() ]
    conflict = FindDeploymentConflict(ballpark.solarsystemID, typeID, position, balls)
    return conflict


def FindDeploymentConflict(solarSystemID, typeID, location, balls):
    import evetypes
    from eve.common.script.sys import idCheckers
    groupID = evetypes.GetGroupID(typeID)
    typeRadius = evetypes.GetRadius(typeID)
    isDrillingPlatform = IsDrillingPlatform(typeID)
    hasGroupStargateRestriction = HasGroupStargateRestriction(groupID)
    myDeploymentDistance = GetDeploymentDistance(typeID)
    if idCheckers.IsAutoMoonMiner(typeID):
        moonID = FindMoonBeaconInRangeOfPosition(solarSystemID, location, MAXIMUM_MINING_BEACON_DISTANCE)
        if not moonID:
            return (inventorycommon.const.typeMoonMiningBeacon, -MAXIMUM_MINING_BEACON_DISTANCE, REAL_BALL)
    for ballID, ballTypeID, position, radius, pointType in balls:
        distanceBetween = DistanceBetween(location, position)
        if _IsBallMoon(ballTypeID, pointType) and distanceBetween < MINIMUM_MOON_DISTANCE + typeRadius + radius:
            canDeployNearMoon = False
            if isDrillingPlatform:
                miningBeaconPosition = GetMiningBeaconPositionForMoon(ballID)
                if miningBeaconPosition is not None:
                    if DistanceBetween(miningBeaconPosition, location) < MAXIMUM_MINING_BEACON_DISTANCE:
                        canDeployNearMoon = True
            if not canDeployNearMoon:
                return (ballTypeID, MINIMUM_MOON_DISTANCE, pointType)
        if hasGroupStargateRestriction and IsStargate(ballTypeID):
            minimumDistance = GROUP_MIN_DISTANCE_TO_STARGATE[groupID]
            if distanceBetween < minimumDistance + typeRadius + radius:
                return (ballTypeID, minimumDistance, pointType)
        minimum = GetDeploymentDistance(ballTypeID)
        if evetypes.GetCategoryID(ballTypeID) == inventorycommon.const.categoryStructure:
            minimum = min(minimum, myDeploymentDistance)
        if minimum and distanceBetween < minimum + typeRadius + radius:
            return (ballTypeID, minimum, pointType)


def _IsBallMoon(ballTypeID, pointType):
    isBallMoon = pointType == REAL_BALL and evetypes.GetGroupID(ballTypeID) == inventorycommon.const.groupMoon
    return isBallMoon


def IsDrillingPlatform(typeID):
    return evetypes.GetGroupID(typeID) in (inventorycommon.const.groupStructureDrillingPlatform, inventorycommon.const.groupUpwellMoonDrill)


def HasGroupStargateRestriction(groupID):
    return groupID in GROUP_MIN_DISTANCE_TO_STARGATE


def IsStargate(typeID):
    return evetypes.GetGroupID(typeID) == inventorycommon.const.groupStargate


def GetMoonminingAvailabilityValueForBalls(ballsAndItems, typeID, location):
    if not IsDrillingPlatform(typeID):
        return MOONMINING_NEVER_AVAILABLE
    balls = [ (item.itemID,
     item.typeID,
     (ball.x, ball.y, ball.z),
     ball.radius,
     REAL_BALL) for ball, item in ballsAndItems ]
    typeRadius = evetypes.GetRadius(typeID)
    for ballID, ballTypeID, position, radius, pointType in balls:
        if not _IsBallMoon(ballTypeID, pointType):
            continue
        distanceBetween = DistanceBetween(location, position)
        if distanceBetween < MINIMUM_MOON_DISTANCE + typeRadius + radius:
            miningBeaconPosition = GetMiningBeaconPositionForMoon(ballID)
            if not miningBeaconPosition:
                return MOONMINING_NEVER_AVAILABLE
            if DistanceBetween(miningBeaconPosition, location) < MAXIMUM_MINING_BEACON_DISTANCE:
                return MOONMINING_POSSIBLE

    return MOONMINING_NOT_POSSIBLE


def DistanceBetween(a, b):
    return math.sqrt(sum([ (a - b) ** 2 for a, b in zip(a, b) ]))


def GetStructureNamePrefix(structureTypeID, solarSystemID, extraConfig = None):
    solarSystemName = GetUntranslatedSolarSystemName(solarSystemID)
    if evetypes.IsUpwellStargate(structureTypeID):
        if extraConfig is None:
            raise RuntimeError("Shouldn't be here without destinationSolarsystemID")
        destinationSolarsystemID = extraConfig.get('destinationSolarsystemID', None)
        if not destinationSolarsystemID:
            raise RuntimeError("Shouldn't be here without destinationSolarsystemID")
        destinationSystemName = GetUntranslatedSolarSystemName(destinationSolarsystemID)
        return '%s %s %s - ' % (solarSystemName, JUMP_BRIDGE_LINK_CHARACTER, destinationSystemName)
    else:
        return '%s - ' % solarSystemName


def GetUntranslatedSolarSystemName(solarsystemID):
    import localization
    from localization import CleanImportantMarkup
    if boot.region == 'optic':
        languageID = localization.const.LOCALE_SHORT_CHINESE
    else:
        languageID = localization.const.LOCALE_SHORT_ENGLISH
    solarSystemInfo = cfg.mapSystemCache.get(solarsystemID, None)
    return CleanImportantMarkup(localization.GetByMessageID(solarSystemInfo.nameID, languageID=languageID))
