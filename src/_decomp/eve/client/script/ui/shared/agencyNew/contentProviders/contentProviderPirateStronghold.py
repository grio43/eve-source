#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderPirateStronghold.py
import logging
from collections import defaultdict
from agency.client.custom_content import get_custom_content_by_content_type
from carbon.common.lib import telemetry
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyUtil
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.pirateStrongholdSystemContentPiece import PirateStrongholdSystemContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProvider import BaseContentProvider
from talecommon.const import FOB_TEMPLATES
logger = logging.getLogger(__name__)

class ContentProviderPirateStronghold(BaseContentProvider):
    contentType = agencyConst.CONTENTTYPE_PIRATE_STRONGHOLD
    contentGroup = contentGroupConst.contentGroupPirateStrongholds
    __notifyevents__ = BaseContentProvider.__notifyevents__ + ['OnTaleRemove']

    def OnTaleRemove(self, taleID, templateClassID, templateID):
        if templateID in FOB_TEMPLATES:
            sm.GetService('objectCaching').InvalidateCachedMethodCall('custom_agency_provider', 'get_content_data')
            self.InvalidateContentPieces()

    @telemetry.ZONE_METHOD
    def _ConstructContentPieces(self):
        for solarSystemID, contentDataList in self.GetContentDataBySolarSystemID().iteritems():
            if self.CheckDistanceCriteria(solarSystemID) and self.CheckSecurityStatusFilterCriteria(solarSystemID):
                self.AddContentPiece(solarSystemID, contentDataList)

        self.contentPieces = sorted(self.contentPieces, key=self._GetSortKey)

    def _GetSortKey(self, contentPiece):
        return contentPiece.GetJumpsToSelfFromCurrentLocation()

    def GetContentDataBySolarSystemID(self):
        ret = defaultdict(list)
        for contentData in self.GetPirateStrongholds():
            ret[contentData.solar_system_id].append(contentData)

        return ret

    def AddContentPiece(self, solarSystemID, contentDataList):
        contentPiece = PirateStrongholdSystemContentPiece(itemID=solarSystemID, solarSystemID=solarSystemID, contentDataList=contentDataList)
        self.AppendContentPiece(contentPiece)

    def GetPirateStrongholds(self):
        return get_custom_content_by_content_type(self.contentType)
