#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderHomefrontSites.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.siteSystemContentPiece import SiteSystemContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProviderCosmicAnomalies import BaseContentProviderCosmicAnomalies
from eve.common.lib import appConst

class ContentProviderHomefrontSites(BaseContentProviderCosmicAnomalies):
    contentType = agencyConst.CONTENTTYPE_HOMEFRONT_SITES
    contentGroup = contentGroupConst.contentGroupHomefrontSites
    DUNGEON_TRACKER_ID = 'homefront_operations'

    def ConstructContentPiece(self, solarSystemID, dungeonInstances):
        return SiteSystemContentPiece(solarSystemID=solarSystemID, dungeonInstances=dungeonInstances, itemID=solarSystemID, typeID=appConst.typeSystem, archetypeID=appConst.dunArchetypeHomefrontSites)
