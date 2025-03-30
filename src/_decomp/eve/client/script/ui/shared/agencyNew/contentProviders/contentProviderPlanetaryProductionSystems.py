#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderPlanetaryProductionSystems.py
import telemetry
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.planetaryProductionSystemContentPiece import PlanetaryProductionSystemContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProvider import BaseContentProvider
from eve.common.lib import appConst
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem

class ContentProviderPlanetaryProductionSystems(BaseContentProvider):
    contentType = agencyConst.CONTENTTYPE_PLANETARYPRODUCTION
    contentGroup = contentGroupConst.contentGroupPlanetaryProduction
    __notifyevents__ = BaseContentProvider.__notifyevents__ + ['OnSessionChanged']

    @telemetry.ZONE_METHOD
    def __init__(self):
        self.starMapSvc = sm.GetService('starmap')
        self.knownSolarSystems = self.starMapSvc.GetKnownUniverseSolarSystems()
        self.validSolarSystemIDs = []
        self.desiredPlanetTypes = []
        super(ContentProviderPlanetaryProductionSystems, self).__init__()

    def OnSessionChanged(self, isRemote, sess, change):
        if 'solarsystemid' in change:
            self.validSolarSystemIDs = []

    @telemetry.ZONE_METHOD
    def _ConstructContentPieces(self):
        if not self.validSolarSystemIDs:
            self.UpdateValidSolarSystemIDs()
        systemContentPieces = [ self.ConstructSystemContentPiece(solarSystemID) for solarSystemID in self.validSolarSystemIDs ]
        self.ExtendContentPieces(systemContentPieces)

    def UpdateValidSolarSystemIDs(self):
        self.validSolarSystemIDs = self.GetValidSolarSystemIDs()[:agencyConst.MAX_CONTENT_PIECES_MAX]

    def OnAgencyFilterChanged(self, contentGroupID, filterType, value):
        if contentGroupID != self.contentGroup:
            return
        if filterType == agencyConst.FILTERTYPE_PLANETTYPES:
            self.UpdateDesiredPlanetTypes()
        self.validSolarSystemIDs = []
        super(ContentProviderPlanetaryProductionSystems, self).OnAgencyFilterChanged(contentGroupID, filterType, value)

    def UpdateDesiredPlanetTypes(self):
        self.desiredPlanetTypes = self.GetDesiredPlanetTypes()

    @telemetry.ZONE_METHOD
    def GetValidSolarSystemIDs(self):
        if not self.desiredPlanetTypes:
            self.UpdateDesiredPlanetTypes()
        return [ solarSystemID for solarSystemID in self.GetAllSolarSystemIDsWithinJumpRange() if self.CheckSystemCriteria(solarSystemID, self.desiredPlanetTypes) ]

    @telemetry.ZONE_METHOD
    def ConstructSystemContentPiece(self, solarSystemID):
        planetItemIDsInSystem = self.GetPlanetItemIDsInSystem(solarSystemID)
        return PlanetaryProductionSystemContentPiece(solarSystemID=solarSystemID, typeID=appConst.typeSolarSystem, itemID=solarSystemID, planetItemIDsInSystem=planetItemIDsInSystem, desiredPlanetTypes=self.desiredPlanetTypes)

    @telemetry.ZONE_METHOD
    def GetPlanetItemIDsInSystem(self, solarSystemID):
        if solarSystemID not in self.knownSolarSystems:
            wormholePlanets = self.GetWormholePlanets()
            if not wormholePlanets:
                return []
            return wormholePlanets.keys()
        return self.knownSolarSystems[solarSystemID].planetItemIDs

    @telemetry.ZONE_METHOD
    def GetPlanetTypesInSystem(self, solarSystemID):
        if solarSystemID not in self.knownSolarSystems:
            wormholePlanets = self.GetWormholePlanets()
            if not wormholePlanets:
                return []
            return [ planet.typeID for planet in wormholePlanets.values() ]
        solarSystemInfo = self.knownSolarSystems[solarSystemID]
        planetsInSystem = solarSystemInfo.planetCountByType.keys()
        return planetsInSystem

    def GetWormholePlanets(self):
        systemCache = cfg.mapSolarSystemContentCache[session.solarsystemid2]
        wormholePlanets = getattr(systemCache, 'planets')
        return wormholePlanets

    @telemetry.ZONE_METHOD
    def CheckSystemCriteria(self, solarSystemID, desiredPlanetTypes):
        return self.CheckDistanceCriteria(solarSystemID) and self.CheckPlanetTypeCriteria(solarSystemID, desiredPlanetTypes) and self.CheckSecurityStatusFilterCriteria(solarSystemID)

    @telemetry.ZONE_METHOD
    def CheckPlanetTypeCriteria(self, solarSystemID, desiredPlanetTypes):
        planetsInSystem = self.GetPlanetTypesInSystem(solarSystemID)
        systemHasDesiredPlanets = any((desiredPlanetType in planetsInSystem for desiredPlanetType in desiredPlanetTypes))
        return systemHasDesiredPlanets

    @telemetry.ZONE_METHOD
    def GetDesiredPlanetTypes(self):
        planetTypesFilterValue = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_PLANETTYPES)
        desiredPlanetTypes = [ planetType for planetType, filterValue in planetTypesFilterValue.iteritems() if filterValue is True ]
        return desiredPlanetTypes
