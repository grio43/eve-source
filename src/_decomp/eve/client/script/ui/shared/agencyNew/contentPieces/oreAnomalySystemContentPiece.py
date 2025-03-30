#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\oreAnomalySystemContentPiece.py
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.oreAnomalyContentPiece import OreAnomalyContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.siteSystemContentPiece import SiteSystemContentPiece
from eve.common.lib import appConst
from evedungeons.client.oreTypesInDungeons.util import get_consolidated_ore_types
from localization import GetByLabel

class OreAnomalySystemContentPiece(SiteSystemContentPiece):
    archetypeID = appConst.dunArchetypeOreAnomaly

    def __init__(self, dungeonInstances, resourceTypeIDs, *args, **kwargs):
        super(OreAnomalySystemContentPiece, self).__init__(dungeonInstances, *args, **kwargs)
        self.resourceTypeIDs = resourceTypeIDs

    def GetResourceTypeIDs(self):
        return get_consolidated_ore_types(self.resourceTypeIDs)

    def _ConstructSiteContentPiece(self, site):
        if site:
            return OreAnomalyContentPiece(solarSystemID=self.solarSystemID, enemyOwnerID=site.factionID, itemID=site.siteID, locationID=site.siteID, site=site, dungeonNameID=site.dungeonNameID, position=site.position)
        else:
            return UnknownOreAnomalyContentPiece(solarSystemID=self.solarSystemID)


class UnknownOreAnomalyContentPiece(BaseContentPiece):

    def GetName(self):
        return GetByLabel('UI/Agency/UnknownOreAnomaly')
