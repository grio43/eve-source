#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderIncursions.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.incursionContentPiece import IncursionContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProvider import BaseContentProvider
from eve.common.lib import appConst
import telemetry
from talecommon.const import INCURSION_TEMPLATE_CLASSES

class ContentProviderIncursions(BaseContentProvider):
    contentType = agencyConst.CONTENTTYPE_INCURSIONS
    contentGroup = contentGroupConst.contentGroupIncursions
    contentTypeFilters = (agencyConst.CONTENTTYPE_SUGGESTED, agencyConst.CONTENTTYPE_COMBAT)
    __notifyevents__ = BaseContentProvider.__notifyevents__ + ['OnInfluenceUpdate', 'OnTaleRemove']

    def OnInfluenceUpdate(self, taleID, newInfluenceData):
        self.InvalidateContentPieces()

    def OnTaleRemove(self, taleID, templateClassID, templateID):
        if templateClassID in INCURSION_TEMPLATE_CLASSES:
            self.InvalidateContentPieces()

    @telemetry.ZONE_METHOD
    def _ConstructContentPieces(self):
        incursions = self.GetAllIncursions()
        if not incursions:
            return
        contentPieces = [ self.ConstructContentPiece(incursion) for incursion in incursions ]
        contentPieces = [ contentPiece for contentPiece in contentPieces if self.CheckAllCriteria(contentPiece) ]
        self.ExtendContentPieces(contentPieces)

    def GetAllIncursions(self):
        incursions = sm.RemoteSvc('map').GetIncursionGlobalReport()
        return sorted(incursions, key=self._GetSortKey)

    @telemetry.ZONE_METHOD
    def _GetSortKey(self, incursion):
        return self.GetNumJumpsToSystem(incursion.stagingSolarSystemID)

    def CheckAllCriteria(self, contentPiece):
        if not self.CheckDistanceCriteria(contentPiece.solarSystemID):
            return False
        if not self.CheckSecurityStatusFilterCriteria(contentPiece.solarSystemID):
            return False
        return True

    def ConstructContentPiece(self, incursion):
        return IncursionContentPiece(solarSystemID=incursion.stagingSolarSystemID, ownerID=appConst.factionCONCORDAssembly, enemyOwnerID=int(incursion.aggressorFactionID), incursionData=incursion)
