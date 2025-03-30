#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\incursionContentCard.py
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from eve.client.script.ui.shared.agencyNew.ui.controls.incursionStateCont import IncursionStateCont
from eve.client.script.ui.shared.infoPanels.infoPanelIncursions import SystemInfluenceBar, IncursionFinalEncounterIcon

class IncursionContentCard(BaseContentCard):
    default_name = 'IncursionContentCard'

    def ConstructContent(self):
        super(IncursionContentCard, self).ConstructContent()
        self.ConstructIncursionStateCont()
        self.ConstructGauge()
        self.ConstructMothershipIcon()

    def ConstructMothershipIcon(self):
        icon = IncursionFinalEncounterIcon(parent=self, align=uiconst.TOPRIGHT, hasSpawned=self.contentPiece.HasFinalEncounter(), idx=0)
        icon.DelegateEvents(self)

    def ConstructIncursionStateCont(self):
        IncursionStateCont(parent=self.bottomCont, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, activeState=self.contentPiece.GetIncursionState(), padding=(4, 0, 0, 4))

    def ConstructGauge(self):
        statusBar = SystemInfluenceBar(parent=self.bottomCont, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=8, padding=(4, 4, 8, 8))
        statusBar.SetInfluence(self.contentPiece.GetInfluence(), None, animate=False)

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetConstellationName())
        text = self.contentPiece.GetSolarSystemAndSecurityAndNumJumpsText()
        self.subtitleLabel.SetText(text)
