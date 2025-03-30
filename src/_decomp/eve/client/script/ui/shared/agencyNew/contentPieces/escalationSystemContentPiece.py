#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\escalationSystemContentPiece.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.agencyUtil import GetTimeRemainingText
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.common.lib import appConst

class EscalationSystemContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_PIRATE_STRONGHOLD

    def __init__(self, contentPieces, *args, **kwargs):
        super(EscalationSystemContentPiece, self).__init__(typeID=appConst.typeSolarSystem, *args, **kwargs)
        self.contentPieces = contentPieces

    def GetSiteContentPieces(self):
        return self.contentPieces

    def GetNumDungeons(self):
        return len(self.contentPieces)

    def GetTimeRemaining(self):
        return min((contentPiece.GetTimeRemaining() for contentPiece in self.contentPieces))

    def GetExpiryTimeText(self):
        return GetTimeRemainingText(self.GetTimeRemaining())
