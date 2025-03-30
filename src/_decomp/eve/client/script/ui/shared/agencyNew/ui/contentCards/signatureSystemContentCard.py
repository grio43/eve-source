#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\signatureSystemContentCard.py
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from localization import GetByLabel

class SignatureSystemContentCard(BaseContentCard):
    default_name = 'SignatureSystemContentCard'

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetSystemAndSecurityText())
        self.subtitleLabel.SetText(self.contentPiece.GetNumJumpsText())
        self.bottomLabel.SetText(GetByLabel('UI/Agency/NumberOfSignaturesInSystem', amount=self.contentPiece.GetNumDungeons()))
