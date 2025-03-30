#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\iceBeltSystemContentPiece.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.iceBeltContentPiece import IceBeltContentPiece
from eve.common.lib import appConst
from localization import GetByLabel

class IceBeltSystemContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_ICEBELTS

    def __init__(self, iceBeltInstances, iceTypesInSystem, *args, **kwargs):
        super(IceBeltSystemContentPiece, self).__init__(*args, **kwargs)
        self.iceTypesInSystem = iceTypesInSystem
        self.contentPieces = self._ConstructIceBeltContentPieces(iceBeltInstances)

    def GetResourceTypeIDs(self):
        return self.iceTypesInSystem

    def ConstructIceBeltContentPiece(self, site):
        if site:
            return IceBeltContentPiece(solarSystemID=self.solarSystemID, enemyOwnerID=site.factionID, itemID=site.siteID, locationID=site.siteID, site=site, dungeonNameID=site.dungeonNameID, position=site.position)
        else:
            return UnknownIceBeltContentPiece(solarSystemID=self.solarSystemID)

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(self.solarSystemID, appConst.typeSolarSystem)

    def _ConstructIceBeltContentPieces(self, dungeonInstances):
        return [ self.ConstructIceBeltContentPiece(site) for site in dungeonInstances ]

    def GetName(self):
        return cfg.evelocations.Get(self.solarSystemID).locationName

    def GetEnemyOwnerID(self):
        regionID = cfg.mapSystemCache.Get(self.solarSystemID).regionID
        pirateFactionIDs = sm.GetService('faction').GetPirateFactionsOfRegion(regionID)
        if pirateFactionIDs:
            return pirateFactionIDs[0]


class UnknownIceBeltContentPiece(BaseContentPiece):

    def GetName(self):
        return GetByLabel('UI/Agency/UnknownIceBelt')
