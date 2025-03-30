#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\incursionSystemContentCard.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from eve.client.script.ui.shared.infoPanels.infoPanelIncursions import IncursionFinalEncounterIcon
from talecommon.const import scenesTypes

class IncursionSystemContentCard(BaseContentCard):
    default_name = 'IncursionSystemContentCard'

    def ConstructContent(self):
        self.ConstructTitleLabel()
        self.ConstructSubtitleLabel()
        self.ConstructBottomLabel()
        self.CheckConstructMothershipIcon()

    def ConstructBottomLabel(self):
        iconSize = 32
        self.icon = Sprite(parent=self.bottomCont, align=uiconst.CENTERLEFT, pos=(4,
         0,
         iconSize,
         iconSize))
        self.bottomLabel = EveLabelMedium(name='bottomLabel', parent=self.bottomCont, align=uiconst.CENTERLEFT, left=iconSize + 10)

    def ConstructBottomCont(self):
        self.bottomCont = Container(name='bottomCont', parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=40)
        Frame(bgParent=self.bottomCont, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=agencyUIConst.COLOR_BG)

    def CheckConstructMothershipIcon(self):
        if self.contentPiece.GetSceneType() == scenesTypes.headquarters:
            icon = IncursionFinalEncounterIcon(parent=self, align=uiconst.TOPRIGHT, hasSpawned=self.contentPiece.HasFinalEncounter(), idx=0)
            icon.DelegateEvents(self)

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetName())
        self.subtitleLabel.SetText(self.contentPiece.GetNumJumpsText())
        self.bottomLabel.SetText(self.contentPiece.GetSceneTypeName())
        text = self.contentPiece.GetSolarSystemAndSecurityAndNumJumpsText()
        self.subtitleLabel.SetText(text)
        self.icon.SetTexturePath(self.contentPiece.GetSceneTypeIcon())
