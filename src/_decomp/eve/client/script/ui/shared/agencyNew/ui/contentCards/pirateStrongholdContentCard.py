#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\pirateStrongholdContentCard.py
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from localization import GetByLabel

class PirateStrongholdContentCard(BaseContentCard):
    default_name = 'PirateStrongholdContentCard'

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetSystemAndSecurityText())
        self.subtitleLabel.SetText(self.contentPiece.GetNumJumpsText())
        text = GetByLabel('UI/Agency/PirateStronghold', amount=self.contentPiece.GetNumDungeons())
        text += '\n' + cfg.eveowners.Get(self.contentPiece.GetEnemyFactionID()).ownerName
        self.bottomLabel.SetText(text)
