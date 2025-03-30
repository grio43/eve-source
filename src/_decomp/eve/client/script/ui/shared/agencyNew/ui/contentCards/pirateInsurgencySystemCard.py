#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\pirateInsurgencySystemCard.py
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveIcon import LogoIcon
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from eve.client.script.ui.control import eveLabel

class PirateInsurgencySystemCard(BaseContentCard):
    default_name = 'PirateInsurgencySystemCard'

    def ApplyAttributes(self, attributes):
        super(PirateInsurgencySystemCard, self).ApplyAttributes(attributes)
        self.corruptionSuppressionSvc = sm.GetService('corruptionSuppressionSvc')

    def ConstructContent(self):
        super(PirateInsurgencySystemCard, self).ConstructContent()
        self.ConstructCorruptionSuppressionLabels()
        self.ConstructFactionIcons()

    def ConstructCorruptionSuppressionLabels(self):
        padTopBottom = self.bottomLabel.padTop
        self.bottomLabel.padBottom = 0
        self.corruptionLabel = eveLabel.EveLabelMedium(name='corruptionLabel', parent=self.bottomCont, align=uiconst.TOTOP, padding=(self.bottomLabel.padLeft,
         0,
         self.bottomLabel.padRight,
         padTopBottom))
        self.suppressionLabel = eveLabel.EveLabelMedium(name='suppressionLabel', parent=self.bottomCont, align=uiconst.TOTOP, padding=(self.bottomLabel.padLeft,
         0,
         self.bottomLabel.padRight,
         padTopBottom))

    def ConstructFactionIcons(self):
        self.pirateIcon = Sprite(name='pirateIcon', parent=self.mainCont, align=uiconst.TOPRIGHT, pos=(0, 0, 32, 32), idx=0)
        self.occupierIcon = Sprite(name='occupierIcon', parent=self.mainCont, align=uiconst.TOPRIGHT, pos=(32, 0, 32, 32), idx=0)

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetSystemAndSecurityText())
        self.subtitleLabel.SetText(self.contentPiece.GetNumJumpsText())
        self.corruptionLabel.SetText(self.contentPiece.GetCorruptionStageText())
        self.suppressionLabel.SetText(self.contentPiece.GetSuppressionStageText())
        pirateFactionID = self.contentPiece.GetPirateFactionID()
        texturePath = LogoIcon.GetFactionIconTexturePath(pirateFactionID) if pirateFactionID else ''
        self.pirateIcon.texturePath = texturePath
        self.pirateIcon.hint = cfg.eveowners.Get(pirateFactionID).name if pirateFactionID else ''
        ownerID = self.contentPiece.GetOwnerID()
        texturePath = LogoIcon.GetFactionIconTexturePath(ownerID) if ownerID else ''
        self.occupierIcon.texturePath = texturePath
        self.occupierIcon.hint = cfg.eveowners.Get(ownerID).name if ownerID else ''
