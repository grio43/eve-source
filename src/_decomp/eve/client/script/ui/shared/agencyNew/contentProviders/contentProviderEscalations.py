#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderEscalations.py
from collections import defaultdict
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.escalationContentPiece import EscalationContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.escalationSystemContentPiece import EscalationSystemContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProvider import BaseContentProvider
import telemetry
from localization import GetByLabel

class ContentProviderEscalations(BaseContentProvider):
    __notifyevents__ = BaseContentProvider.__notifyevents__ + ['OnEscalatingPathMessage', 'OnEscalationsDataUpdated']
    contentType = agencyConst.CONTENTTYPE_ESCALATION
    contentGroup = contentGroupConst.contentGroupEscalations
    contentTypeFilters = (agencyConst.CONTENTTYPE_SUGGESTED, agencyConst.CONTENTTYPE_COMBAT)

    def __init__(self):
        super(ContentProviderEscalations, self).__init__()
        sm.RegisterNotify(self)

    @telemetry.ZONE_METHOD
    def _ConstructContentPieces(self):
        contentPieces = []
        for solarSystemID, systemContentPieces in self.GetContentPiecesBySolarSystemID().iteritems():
            contentPiece = self.AppendEscalationSystemContentPiece(solarSystemID, systemContentPieces)
            contentPieces.append(contentPiece)

        contentPieces = sorted(contentPieces, key=self._GetSortKey)
        self.ExtendContentPieces(contentPieces)

    def _GetSortKey(self, contentPiece):
        return contentPiece.GetJumpsToSelfFromCurrentLocation()

    def AppendEscalationSystemContentPiece(self, solarSystemID, contentPieces):
        contentPiece = EscalationSystemContentPiece(itemID=solarSystemID, solarSystemID=solarSystemID, contentPieces=contentPieces)
        return contentPiece

    def GetContentPiecesBySolarSystemID(self):
        ret = defaultdict(list)
        for contentPiece in self.GetEscalationContentPieces():
            ret[contentPiece.solarSystemID].append(contentPiece)

        return ret

    @telemetry.ZONE_METHOD
    def GetEscalationContentPieces(self):
        escalations = sm.GetService('journal').GetEscalations()
        contentPieces = [ self.ConstructEscalationContentPiece(escalation) for escalation in escalations if escalation.destDungeon ]
        return [ contentPiece for contentPiece in contentPieces if not contentPiece.IsExpired() ]

    def ConstructEscalationContentPiece(self, escalationSite):
        return EscalationContentPiece(solarSystemID=escalationSite.dungeon.solarSystemID, itemID=escalationSite.dungeon.instanceID, locationID=escalationSite.dungeon.solarSystemID, escalationSite=escalationSite, isNew=True)

    def OnEscalatingPathMessage(self, instanceID):
        if instanceID:
            sm.GetService('neocom').Blink('agency', GetByLabel('UI/Neocom/Blink/NewEscalationMissionAvailable'))

    def OnEscalationsDataUpdated(self):
        self.InvalidateContentPieces()
