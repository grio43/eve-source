#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\mercDenContentPiece.py
from eve.client.script.ui.const import buttonConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from localization import GetByLabel

class MercDenContentPiece(BaseContentPiece):

    def GetButtonLabel(self):
        if self.buttonState == buttonConst.STATE_SETDESTINATION:
            return GetByLabel('UI/Agency/MercDen/SetDestinationToZarzakh')
        if self.buttonState == buttonConst.STATE_DESTINATIONSET:
            return GetByLabel('UI/Agency/MercDen/DestinationSetToZarzakh')
        return super(MercDenContentPiece, self).GetButtonLabel()
