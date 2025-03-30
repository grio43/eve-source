#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\colonyResourcesAgencySystemContentPiece.py
import log
import telemetry
import evetypes
import uthread2
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.colonyResourcesAgencyPlanetContentPiece import ColonyResourcesAgencyPlanetContentPiece
from signals import Signal

class ColonyResourcesAgencySystemContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_COLONYRESOURCESAGENCY

    def __init__(self, planetLookupPerSolarSystem, solarSystemValues, sovAllianceID, *args, **kwargs):
        super(ColonyResourcesAgencySystemContentPiece, self).__init__(*args, **kwargs)
        self.mapSvc = sm.GetService('map')
        self.sovereigntyResourceSvc = sm.GetService('sovereigntyResourceSvc')
        self.planetLookupPerSolarSystem = planetLookupPerSolarSystem
        self.solarSystemValues = solarSystemValues
        self.sovAllianceID = sovAllianceID
        self.planetContentPieces = None

    @telemetry.ZONE_METHOD
    def ConstructPlanetContentPieces(self):
        expiryByPlanet = self.sovereigntyResourceSvc.GetPlanetIDsAndTheftVulnerabilityExpiry(self.itemID)
        validPlanetValues = self.planetLookupPerSolarSystem.GetValidPlanetResourceValues()
        planetIDs = [ x.itemID for x in validPlanetValues ]
        cfg.evelocations.Prime(planetIDs)
        self.planetContentPieces = filter(None, [ self.ConstructPlanetContentPiece(value.itemID, value, value.itemID in expiryByPlanet, expiryByPlanet.get(value.itemID, None)) for value in validPlanetValues ])
        return self.planetContentPieces

    @telemetry.ZONE_METHOD
    def ConstructPlanetContentPiece(self, planetID, planetValues, hasVulnerableSkyhook, expiry):
        planetItem = self.mapSvc.GetItem(planetID)
        return ColonyResourcesAgencyPlanetContentPiece(planetValues, solarSystemID=self.solarSystemID, itemID=planetItem.itemID, locationID=planetItem.locationID, position=(planetItem.x, planetItem.y, planetItem.z), typeID=planetItem.typeID, groupID=evetypes.GetGroupID(planetItem.typeID), planetName=planetItem.itemName, hasVulnerableSkyhook=hasVulnerableSkyhook, expiry=expiry)

    def GetPlanetContentPieces(self):
        return self.ConstructPlanetContentPieces()
