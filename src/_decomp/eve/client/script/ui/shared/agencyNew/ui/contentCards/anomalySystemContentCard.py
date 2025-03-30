#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\anomalySystemContentCard.py
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from localization import GetByLabel

class AnomalySystemContentCard(BaseContentCard):
    default_name = 'AnomalySystemContentCard'

    def ConstructContent(self):
        self.ConstructTitleLabel()
        self.ConstructSubtitleLabel()
        self.ConstructBottomLabel()

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetSystemAndSecurityText())
        self.subtitleLabel.SetText(self.contentPiece.GetNumJumpsText())
        self.bottomLabel.SetText(GetByLabel('UI/Agency/NumberOfAnomaliesInSystem', amount=self.contentPiece.GetNumDungeons()))
