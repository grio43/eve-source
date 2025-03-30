#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderIceBelts.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.iceBeltSystemContentPiece import IceBeltSystemContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProviderCosmicAnomalies import BaseContentProviderCosmicAnomaliesWithUnknown
from eve.common.lib import appConst
from evedungeons.client.iceTypesInDungeon.util import get_consolidated_ice_types_in_dungeon

class ContentProviderIceBelts(BaseContentProviderCosmicAnomaliesWithUnknown):
    contentType = agencyConst.CONTENTTYPE_ICEBELTS
    contentGroup = contentGroupConst.contentGroupIceBelts
    DUNGEON_TRACKER_ID = 'ice_belts'

    def ConstructContentPiece(self, solarSystemID, dungeonInstances):
        return IceBeltSystemContentPiece(solarSystemID=solarSystemID, iceBeltInstances=dungeonInstances, iceTypesInSystem=self.GetIceTypeIDsInSystem(dungeonInstances), itemID=solarSystemID, typeID=appConst.typeSystem)

    def GetIceTypeIDsInSystem(self, iceBeltInstances):
        iceTypeIDs = set()
        for iceBelt in iceBeltInstances:
            if iceBelt and iceBelt.dungeonID:
                iceTypeIDs.update(get_consolidated_ice_types_in_dungeon(iceBelt.dungeonID))

        return iceTypeIDs
