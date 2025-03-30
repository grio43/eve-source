#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderSites.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.siteSystemContentPiece import SiteSystemContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProviderCosmicAnomalies import BaseContentProviderCosmicAnomaliesWithUnknown
from eve.common.lib import appConst
SITE_CONTENT_PROVIDER_BLACKLIST = (appConst.dunArchetypeFactionalWarfareComplexNovice,
 appConst.dunArchetypeFactionalWarfareComplexSmall,
 appConst.dunArchetypeFactionalWarfareComplexMedium,
 appConst.dunArchetypeFactionalWarfareComplexLarge,
 appConst.dunArchetypeFactionaWarfareBattlefieldSites)

class ContentProviderSites(BaseContentProviderCosmicAnomaliesWithUnknown):
    contentType = agencyConst.CONTENTTYPE_SITES
    contentGroup = contentGroupConst.contentGroupCombatAnomalies
    DUNGEON_TRACKER_ID = 'combat_anomalies'

    def ConstructContentPiece(self, solarSystemID, dungeonInstances):
        return SiteSystemContentPiece(solarSystemID=solarSystemID, dungeonInstances=dungeonInstances, itemID=solarSystemID, typeID=appConst.typeSystem)
