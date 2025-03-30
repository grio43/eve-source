#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\homefrontSitesContentCard.py
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from localization import GetByLabel

class HomefrontSitesContentCard(BaseContentCard):
    default_name = 'HomefrontSitesContentCard'

    def ConstructContent(self):
        self.ConstructTitleLabel()
        self.ConstructSubtitleLabel()
        self.ConstructBottomLabel()

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetSystemAndSecurityText())
        self.subtitleLabel.SetText(self.contentPiece.GetNumJumpsText())
        self.bottomLabel.SetText(GetByLabel('UI/Agency/NumberOfSitesInSystem', amount=self.contentPiece.GetNumDungeons()))
