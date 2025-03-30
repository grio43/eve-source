#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveuniverse\solar_systems.py
import math
import geo2
from appConst import LIGHTYEAR
from carbon.common.script.util.mathCommon import FloatCloseEnough
from eve.common.script.sys.idCheckers import IsAbyssalSpaceSystem, IsHighSecSystem, IsTriglavianSystem, IsKnownSpaceSystem, IsWormholeSystem, IsNullSecSystem, IsVoidSpaceSystem, IsZarzakh
import sys

def get_solar_system_data(solar_system_id):
    return cfg.mapSolarSystemContentCache[solar_system_id]


def get_celestial_data(celestial_id):
    return cfg.mapSolarSystemContentCache.celestials[celestial_id]


def get_star_id(solar_system_id):
    if is_sunless_solar_system(solar_system_id):
        return None
    else:
        return get_solar_system_data(solar_system_id).star.id


def is_sunless_solar_system(solar_system_id):
    return is_empty_system(solar_system_id)


def has_celestials(solar_system_id):
    return IsKnownSpaceSystem(solar_system_id) or IsWormholeSystem(solar_system_id)


def is_empty_system(solar_system_id):
    return IsAbyssalSpaceSystem(solar_system_id) or IsVoidSpaceSystem(solar_system_id)


def is_hazard_system(solar_system_id):
    return IsZarzakh(solar_system_id)


def is_sensor_overlay_suppressed(solar_system_id):
    if is_scanning_suppressed(solar_system_id):
        return True
    return is_empty_system(solar_system_id)


def is_tactical_camera_suppressed(solar_system_id):
    return is_empty_system(solar_system_id) or is_hazard_system(solar_system_id)


def is_pov_camera_suppressed(solar_system_id):
    return is_empty_system(solar_system_id) or is_hazard_system(solar_system_id)


def is_orbit_camera_range_limited(solar_system_id):
    if is_orbit_camera_range_limited_extreme(solar_system_id):
        return True
    if is_orbit_camera_range_limited_moderate(solar_system_id):
        return True
    return False


def is_orbit_camera_range_limited_extreme(solar_system_id):
    return is_empty_system(solar_system_id)


def is_orbit_camera_range_limited_moderate(solar_system_id):
    return is_hazard_system(solar_system_id)


def is_map_browser_suppressed(solar_system_id):
    return is_empty_system(solar_system_id)


def is_warping_suppressed(solar_system_id):
    return IsAbyssalSpaceSystem(solar_system_id)


def is_emergency_warping_suppressed(solar_system_id):
    return is_warping_suppressed(solar_system_id) or IsVoidSpaceSystem(solar_system_id) or is_hazard_system(solar_system_id)


def is_cloaking_suppressed(solar_system_id):
    return is_empty_system(solar_system_id)


def is_directional_scanner_suppressed(solar_system_id):
    return bool(get_directional_scanner_suppressed_error(solar_system_id))


def get_directional_scanner_suppressed_error(solar_system_id):
    if is_empty_system(solar_system_id):
        return 'CannotScanInAbyssSpace'
    try:
        dscanRange = get_max_directional_scanner_range(solar_system_id)
        if FloatCloseEnough(dscanRange, 0):
            return 'CannotDscanInThisSystem'
    except (AttributeError, KeyError):
        pass


def get_max_directional_scanner_range(solar_system_id):
    try:
        max_dscan_range = 1000 * cfg.mapSolarSystemContentCache[solar_system_id].dscanRange
    except (AttributeError, KeyError):
        max_dscan_range = 1000.0 * float(sys.maxint)

    return max_dscan_range


def is_scanning_suppressed(solar_system_id):
    try:
        return cfg.mapSolarSystemContentCache[solar_system_id].disallowScanning
    except (AttributeError, KeyError):
        pass

    return False


def is_solarsystem_map_suppressed(solar_system_id):
    return IsZarzakh(solar_system_id)


def is_cyno_suppressed(solar_system_id):
    return bool(get_cyno_suppressed_error(solar_system_id))


def get_cyno_suppressed_error(solar_system_id):
    if IsHighSecSystem(solar_system_id):
        return 'JumpCantUseCFG'
    if IsTriglavianSystem(solar_system_id):
        return 'CFGInTriglavianSystem'
    try:
        if cfg.mapSolarSystemContentCache[solar_system_id].disallowCyno:
            return 'CannotLightCynoInSystem'
    except (AttributeError, KeyError):
        pass


def is_bookmarking_suppressed(solar_system_id):
    return is_empty_system(solar_system_id) or is_hazard_system(solar_system_id)


def get_disallowed_categories(solar_system_id):
    try:
        return cfg.mapSolarSystemContentCache[solar_system_id].disallowedAnchorCategories
    except (AttributeError, KeyError):
        return []


def handle_ewarp_suppressed_systems(park):
    if is_emergency_warping_suppressed(park.solarsystemID):
        park.disableWarpIn = 1
        park.disableWarpOut = 1


def is_void_filament_restricted(solar_system_id):
    return is_hazard_system(solar_system_id)


def is_random_jump_filament_restricted(solar_system_id):
    return is_hazard_system(solar_system_id)


def is_abyssal_filament_restricted(solar_system_id):
    return is_hazard_system(solar_system_id)


def GetLightYearDistance(fromSolarsystemID, toSolarsystemID):
    fromSystem = cfg.evelocations.Get(fromSolarsystemID)
    if fromSystem is None:
        raise AttributeError('Invalid fromSolarsystemID')
    toSystem = cfg.evelocations.Get(toSolarsystemID)
    if toSystem is None:
        raise AttributeError('Invalid toSolarsystemID')
    if not IsKnownSpaceSystem(fromSolarsystemID) or not IsKnownSpaceSystem(toSolarsystemID):
        raise AttributeError('Can only measure distances between k-space solar systems')
    dist = math.sqrt((toSystem.x - fromSystem.x) ** 2 + (toSystem.y - fromSystem.y) ** 2 + (toSystem.z - fromSystem.z) ** 2) / LIGHTYEAR
    return dist


def GetSystemsInLightYearDistance(fromSolarsystemID, maxDistance):
    fromSystem = cfg.evelocations.Get(fromSolarsystemID)
    if fromSystem is None:
        raise AttributeError('Invalid fromSolarsystemID')
    if not IsKnownSpaceSystem(fromSolarsystemID):
        raise AttributeError('Can only measure distances between k-space solar systems')
    solarsystemIDs = []
    for solarsystemID, data in cfg.mapSystemCache.iteritems():
        if solarsystemID == fromSolarsystemID:
            continue
        if not IsKnownSpaceSystem(solarsystemID):
            continue
        distance = GetLightYearDistance(fromSolarsystemID, solarsystemID)
        if distance <= maxDistance:
            solarsystemIDs.append((solarsystemID, distance))

    return solarsystemIDs


def GetSystemsInLightYearDistanceDict(solarSystemID, maxDistance):
    nearbySolarsystems = GetSystemsInLightYearDistance(solarSystemID, maxDistance)
    return {x[0]:x[1] for x in nearbySolarsystems}


def GetNonNpcNullSecSystemsInLightYearDistanceDict(solarSystemID, maxDistance):
    nearbySolarsystems = GetSystemsInLightYearDistance(solarSystemID, maxDistance)
    nullNonNpcSolarSystems = {}
    for eachSolarSystemID, dist in nearbySolarsystems:
        if not IsNullSecSystem(eachSolarSystemID):
            continue
        systemInfo = cfg.mapSystemCache[eachSolarSystemID]
        if getattr(systemInfo, 'factionID', None):
            continue
        nullNonNpcSolarSystems[eachSolarSystemID] = dist

    return nullNonNpcSolarSystems


def GetAlignmentYawPitchRadians(fromSolarsystemID, toSolarsystemID):
    sourceLocation = cfg.evelocations.Get(fromSolarsystemID)
    sourcePosition = (sourceLocation.x, sourceLocation.y, sourceLocation.z)
    destinationLocation = cfg.evelocations.Get(toSolarsystemID)
    destinationPosition = (destinationLocation.x, destinationLocation.y, destinationLocation.z)
    direction = geo2.Vec3DirectionD(destinationPosition, sourcePosition)
    orientationQ = geo2.QuaternionRotationArc(direction, (0.0, 0.0, 1.0))
    yawPitchRoll = geo2.QuaternionRotationGetYawPitchRoll(orientationQ)
    return (yawPitchRoll[0], yawPitchRoll[1])
