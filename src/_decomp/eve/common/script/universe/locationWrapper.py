#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\universe\locationWrapper.py


class SolarSystemWrapper(object):
    __guid__ = 'universe.SolarSystemWrapper'

    def __init__(self, solarSystemId):
        solarSystem = cfg.mapSystemCache[solarSystemId]
        self.stringRepresentation = solarSystem.__str__()
        self.solarSystemID = solarSystemId
        self.wormholeClassID = getattr(solarSystem, 'wormholeClassID', None)
        self.factionID = getattr(solarSystem, 'factionID', None)
        self.regionID = solarSystem.regionID
        self.constellationID = solarSystem.constellationID
        self.security = solarSystem.securityStatus
        self.securityStatus = solarSystem.securityStatus
        self.solarSystemName = cfg.evelocations[self.solarSystemID].locationName
        self.planetCount = len(solarSystem.planetCountByType)
        self.planetItemIDs = solarSystem.planetItemIDs

    def __str__(self):
        return self.stringRepresentation

    def __repr__(self):
        return self.stringRepresentation
