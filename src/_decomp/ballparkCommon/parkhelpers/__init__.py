#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\ballparkCommon\parkhelpers\__init__.py
import math
import random
try:
    import geo2
except ImportError:
    geo2 = None

from eve.common.lib import appConst

def HasWarpInPoint(item, radius):
    if radius >= 90000 and item.categoryID == appConst.categoryCelestial and item.groupID != appConst.groupWreck:
        return True
    return False


def GetNearestPlanet(solarSystemID, position):
    minDist = None
    nearestPlanet = None
    for planetID, planet in GetPlanets(solarSystemID).items():
        dist = geo2.Vec3Distance(position, planet.position.data)
        if minDist is None or minDist > dist:
            nearestPlanet = planet
            minDist = dist

    return nearestPlanet


def GetRandomPlanetID(solarSystemID):
    planets = GetPlanets(solarSystemID)
    planetIDs = planets.keys()
    return random.choice(planetIDs)


def GetLocationNextToPlanet(solarSystemID, planetID, randomize = True):
    planet = GetPlanets(solarSystemID)[planetID]
    planetPos = planet.position.data
    directionFromCenter = geo2.Vec3Normalize(geo2.Vec3Cross(planetPos, (0, 1, 0)))
    offsetFromPlanetCenter = geo2.Vec3Scale(directionFromCenter, planet.radius * 2.5)
    rotationAngle = math.pi / 4
    if randomize:
        rotationAngle *= 1.0 + 0.1 * random.random()
    quat = geo2.QuaternionRotationAxis((0, 1, 0), rotationAngle)
    offsetFromPlanetCenter = geo2.QuaternionTransformVector(quat, offsetFromPlanetCenter)
    return geo2.Vec3Add(planetPos, offsetFromPlanetCenter)


def GetPlanets(solarSystemID):
    return getattr(cfg.mapSolarSystemContentCache[solarSystemID], 'planets', {})
