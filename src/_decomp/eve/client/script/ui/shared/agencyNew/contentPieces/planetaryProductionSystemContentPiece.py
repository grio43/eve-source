#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\planetaryProductionSystemContentPiece.py
import telemetry
import evetypes
import uthread2
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.planetaryProductionPlanetContentPiece import PlanetaryProductionPlanetContentPiece
from signals import Signal

class PlanetaryProductionSystemContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_PLANETARYPRODUCTION

    def __init__(self, planetItemIDsInSystem, desiredPlanetTypes, *args, **kwargs):
        super(PlanetaryProductionSystemContentPiece, self).__init__(*args, **kwargs)
        self.mapSvc = sm.GetService('map')
        self.isSystemColonizedByMe = False
        self.planetContentPieces = None
        self.planetContentPiecesReadySignal = Signal(signalName='planetContentPiecesReadySignal')
        self.isSystemWithinScanRange, self.isSystemUnscannable = sm.GetService('planetSvc').IsSystemWithinScanRange(self.solarSystemID)
        self.planetItemIDsInSystem = planetItemIDsInSystem
        self.desiredPlanetTypes = desiredPlanetTypes
        self.filteredPlanets = []
        uthread2.StartTasklet(self.ConstructPlanetContentPieces)

    @telemetry.ZONE_METHOD
    def ConstructPlanetContentPieces(self):
        self.planetContentPieces = filter(None, [ self.ConstructPlanetContentPiece(planetItemID) for planetItemID in self.planetItemIDsInSystem ])
        self.planetContentPiecesReadySignal()

    @telemetry.ZONE_METHOD
    def ConstructPlanetContentPiece(self, planetItemID):
        planetItem = self.mapSvc.GetItem(planetItemID)
        if planetItem.typeID not in self.desiredPlanetTypes:
            self.filteredPlanets.append(planetItem)
            return
        return PlanetaryProductionPlanetContentPiece(solarSystemID=self.solarSystemID, itemID=planetItem.itemID, locationID=planetItem.locationID, position=(planetItem.x, planetItem.y, planetItem.z), typeID=planetItem.typeID, groupID=evetypes.GetGroupID(planetItem.typeID), planetName=planetItem.itemName)

    @telemetry.ZONE_METHOD
    def IsSystemColonizedByMe(self):
        if not self.isSystemColonizedByMe:
            self.isSystemColonizedByMe = any((planet.IsColonizedByMe() for planet in self.planetContentPieces))
        return self.isSystemColonizedByMe
