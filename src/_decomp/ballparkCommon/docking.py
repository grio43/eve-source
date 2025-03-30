#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\ballparkCommon\docking.py
import math
import random
from eve.common.lib.appConst import SMALL_UNDOCKPOINT_CATEGORY, LARGE_UNDOCKPOINT_CATEGORY, CAPITAL_UNDOCKPOINT_CATEGORY, SUPERCAPITAL_UNDOCKPOINT_CATEGORY
import evetypes
import collections
from inventorycommon import const as inventoryconst
from dogma import const as dogmaconst
from fsdBuiltData.common.graphicLocations import GetDirectionalLocators
from fsdBuiltData.common.graphicIDs import GetGraphicLocationID
from structures.types import IsFlexStructure
DEFAULT_DIRECTION = ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
DEFAULT_MAPPING = SMALL_UNDOCKPOINT_CATEGORY
GROUP_MAPPING = {inventoryconst.groupFreighter: LARGE_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupIndustrial: LARGE_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupTransportShip: LARGE_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupBlockadeRunner: LARGE_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupJumpFreighter: LARGE_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupBattleship: LARGE_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupEliteBattleship: LARGE_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupBlackOps: LARGE_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupMarauders: LARGE_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupIndustrialCommandShip: LARGE_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupCarrier: CAPITAL_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupForceAux: CAPITAL_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupDreadnought: CAPITAL_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupLancerDreadnought: CAPITAL_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupCapitalIndustrialShip: CAPITAL_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupTitan: SUPERCAPITAL_UNDOCKPOINT_CATEGORY,
 inventoryconst.groupSupercarrier: SUPERCAPITAL_UNDOCKPOINT_CATEGORY}
VELOCITY_MULTIPLIER = 1.75
VELOCITY_MAXIMUM = 700
ONE_WAY_UNDOCKS_BY_STRUCTURE_TYPE = {inventoryconst.typeEngineeringComplexRaitaru: [CAPITAL_UNDOCKPOINT_CATEGORY, SUPERCAPITAL_UNDOCKPOINT_CATEGORY],
 inventoryconst.typeEngineeringComplexAzbel: [CAPITAL_UNDOCKPOINT_CATEGORY, SUPERCAPITAL_UNDOCKPOINT_CATEGORY],
 inventoryconst.typeEngineeringComplexSotiyo: [SUPERCAPITAL_UNDOCKPOINT_CATEGORY]}
EXCLUDED_DOCKS_BY_STRUCTURE_TYPE = {inventoryconst.typeRefineryTatara: [inventoryconst.groupCarrier,
                                     inventoryconst.groupForceAux,
                                     inventoryconst.groupDreadnought,
                                     inventoryconst.groupLancerDreadnought],
 inventoryconst.typeInsurgencyFOBAngel: [inventoryconst.groupFreighter, inventoryconst.groupJumpFreighter],
 inventoryconst.typeInsurgencyFOBGuristas: [inventoryconst.groupFreighter, inventoryconst.groupJumpFreighter]}

def GetUndockCategoryByType(typeID):
    try:
        return GROUP_MAPPING[evetypes.GetGroupID(typeID)]
    except (KeyError, evetypes.TypeNotFoundException):
        return DEFAULT_MAPPING


def LocationToTuples(location):
    return ((location.position.x, location.position.y, location.position.z), (location.direction.x, location.direction.y, location.direction.z))


def GetUndockDirections(typeID):
    try:
        graphicID = evetypes.GetGraphicID(typeID)
        graphicLocationID = GetGraphicLocationID(graphicID)
    except evetypes.TypeNotFoundException:
        return {}
    except KeyError:
        return {}

    directions = collections.defaultdict(list)
    for location in GetDirectionalLocators(graphicLocationID, default=[]):
        directions[location.category].append(LocationToTuples(location))
        directions[None].append(LocationToTuples(location))

    return dict(directions)


def GetUndockDirection(typeID, shipTypeID = None):
    directions = GetUndockDirections(typeID)
    try:
        return random.choice(directions[GetUndockCategoryByType(shipTypeID)])
    except KeyError:
        return random.choice(directions.get(None, [DEFAULT_DIRECTION]))


def CanDock(typeID, shipTypeID = None):
    directions = GetUndockDirections(typeID)
    undockCategory = GetUndockCategoryByType(shipTypeID)
    if undockCategory not in directions:
        return False
    excludedDocks = EXCLUDED_DOCKS_BY_STRUCTURE_TYPE.get(typeID, [])
    if evetypes.GetGroupID(shipTypeID) in excludedDocks:
        return False
    oneWayUndocks = ONE_WAY_UNDOCKS_BY_STRUCTURE_TYPE.get(typeID, [])
    return undockCategory not in oneWayUndocks


def GetUndockVector(ballpark, ballID, typeID = None):
    import geo2
    ballTypeID = ballpark.GetBallType(ballID)
    position, direction = GetUndockDirection(ballTypeID, typeID)
    rotation = ballpark.GetSlimItemField(ballID, 'dunRotation')
    if rotation:
        rotation = map(math.radians, rotation)
        quaternion = geo2.QuaternionRotationSetYawPitchRoll(*rotation)
        position = geo2.QuaternionTransformVector(quaternion, position)
        direction = geo2.QuaternionTransformVector(quaternion, direction)
    ball = ballpark.CheckBalls(ballID)
    position = [ball.x + position[0], ball.y + position[1], ball.z + position[2]]
    direction = geo2.Vec3Normalize(direction)
    if IsFlexStructure(ballTypeID):
        position = geo2.Vec3AddD(position, geo2.Vec3ScaleD(direction, ball.radius))
    return (tuple(position), direction)


def ShipUndockDirection(direction, jitter = 0.25):
    import geo2
    yaw = random.uniform(-jitter, jitter)
    pitch = random.uniform(-jitter, jitter)
    roll = random.uniform(-jitter, jitter)
    quaternion = geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, roll)
    return geo2.QuaternionTransformVector(quaternion, direction)


def ShipUndockVelocity(direction, dogma, shipID):
    import geo2
    speed = min(VELOCITY_MULTIPLIER * dogma.GetAttributeValue(shipID, dogmaconst.attributeMaxVelocity), VELOCITY_MAXIMUM)
    return geo2.Vec3ScaleD(geo2.Vec3Normalize(direction), speed)
