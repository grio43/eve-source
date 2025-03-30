#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderAgency.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.agencyContentPiece import AgencyContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProvider import BaseContentProvider
import telemetry

class ContentProviderAgency(BaseContentProvider):
    contentType = agencyConst.CONTENTTYPE_AGENCY
    __notifyevents__ = BaseContentProvider.__notifyevents__ + ['OnSeasonDataChanged']

    @telemetry.ZONE_METHOD
    def _ConstructContentPieces(self):
        seasonSvc = sm.GetService('seasonService')
        if not seasonSvc.is_season_visible_in_agency():
            return
        self.AppendContentPiece(AgencyContentPiece())

    def OnSeasonDataChanged(self):
        self.InvalidateContentPieces()
