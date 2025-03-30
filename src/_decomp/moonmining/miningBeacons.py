#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\moonmining\miningBeacons.py
try:
    import geo2
except ImportError:
    geo2 = None

def GetMiningBeaconPositionForMoon(moonID):
    try:
        moon = cfg.mapSolarSystemContentCache.moons[moonID]
    except KeyError:
        return None

    if hasattr(moon, 'miningBeacon'):
        return moon.miningBeacon.position


def GetMiningBeaconPositionsForSolarsystem(solarsystemID):
    beaconPositions = {}
    systemContents = cfg.mapSolarSystemContentCache[solarsystemID]
    for planet in systemContents.planets.itervalues():
        if not hasattr(planet, 'moons'):
            continue
        for moonID, moon in planet.moons.iteritems():
            if not hasattr(moon, 'miningBeacon'):
                continue
            beaconPositions[moonID] = moon.miningBeacon.position

    return beaconPositions


def FindMoonBeaconInRangeOfPosition(solarsystemID, position, maxRange):
    miningBeaconPositions = GetMiningBeaconPositionsForSolarsystem(solarsystemID)
    for moonID, beaconPosition in miningBeaconPositions.iteritems():
        if geo2.Vec3DistanceD(position, beaconPosition) < maxRange:
            return moonID
