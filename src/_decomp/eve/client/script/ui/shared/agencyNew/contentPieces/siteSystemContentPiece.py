#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\siteSystemContentPiece.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.siteContentPiece import SiteContentPiece
from eve.common.lib import appConst
from localization import GetByLabel

class SiteSystemContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_SITES
    archetypeID = appConst.dunArchetypeCombatSites

    def __init__(self, dungeonInstances = None, archetypeID = None, *args, **kwargs):
        if archetypeID is not None:
            self.archetypeID = archetypeID
        super(SiteSystemContentPiece, self).__init__(*args, **kwargs)
        self.contentPieces = self._ConstructSiteContentPieces(dungeonInstances)

    def GetName(self):
        return cfg.evelocations.Get(self.solarSystemID).locationName

    def GetNumDungeons(self):
        return len(self.contentPieces)

    def GetEnemyOwnerID(self):
        regionID = cfg.mapSystemCache.Get(self.solarSystemID).regionID
        pirateFactionIDs = sm.GetService('faction').GetPirateFactionsOfRegion(regionID)
        if pirateFactionIDs:
            return pirateFactionIDs[0]

    def GetSiteContentPieces(self):
        return self.contentPieces

    def _ConstructSiteContentPieces(self, dungeonInstances):
        if not dungeonInstances:
            return []
        return [ self._ConstructSiteContentPiece(site) for site in dungeonInstances ]

    def _ConstructSiteContentPiece(self, site):
        if site is None:
            return UnknownSiteContentPiece(solarSystemID=self.solarSystemID)
        else:
            return SiteContentPiece(solarSystemID=self.solarSystemID, enemyOwnerID=site.factionID, itemID=site.siteID, locationID=site.siteID, site=site, dungeonNameID=site.dungeonNameID, position=site.position)

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(self.solarSystemID, appConst.typeSolarSystem)


class UnknownSiteContentPiece(BaseContentPiece):

    def GetName(self):
        return GetByLabel('UI/Agency/UnknownCombatAnomaly')

    def GetSiteLevelText(self):
        return GetByLabel('UI/Common/Unknown')
