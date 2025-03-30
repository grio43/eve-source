#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderOreAnomalies.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.oreAnomalySystemContentPiece import OreAnomalySystemContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProviderCosmicAnomalies import BaseContentProviderCosmicAnomaliesWithUnknown
from eve.common.lib import appConst
from evedungeons.client.oreTypesInDungeons.data import get_ore_types_in_dungeon

class ContentProviderOreAnomalies(BaseContentProviderCosmicAnomaliesWithUnknown):
    contentGroup = contentGroupConst.contentGroupOreAnomalies
    DUNGEON_TRACKER_ID = 'ore_anomalies'

    def ConstructContentPiece(self, solarSystemID, dungeonInstances):
        return OreAnomalySystemContentPiece(solarSystemID=solarSystemID, dungeonInstances=dungeonInstances, resourceTypeIDs=self.GetResourceTypeIDsInSystem(dungeonInstances), itemID=solarSystemID, typeID=appConst.typeSystem)

    def GetResourceTypeIDsInSystem(self, sites):
        resourceTypeIDs = set()
        for site in sites:
            if site and site.dungeonID:
                resourceTypeIDs.update(get_ore_types_in_dungeon(site.dungeonID))

        return resourceTypeIDs
