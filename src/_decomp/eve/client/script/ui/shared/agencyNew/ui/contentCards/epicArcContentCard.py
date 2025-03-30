#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\epicArcContentCard.py
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from eve.client.script.ui.shared.agencyNew.ui.controls.standingThresholdCont import StandingThresholdCont
from eve.client.script.ui.shared.epicArcs import epicArcConst

class EpicArcContentCard(BaseContentCard):
    default_name = 'EpicArcContentCard'

    def ConstructStandingThresholdCont(self):
        StandingThresholdCont(parent=self.bottomCont, align=uiconst.BOTTOMRIGHT, contentPiece=self.contentPiece)

    def ConstructContent(self):
        self.ConstructStandingThresholdCont()
        self.ConstructTitleLabel()
        self.ConstructSubtitleLabel()
        if self.contentPiece.epicArc.GetState() == epicArcConst.ARC_STARTED:
            self.ConstructGauge()
        self.ConstructBottomLabel()

    def ConstructGauge(self):
        Gauge(name='progressGauge', parent=self.mainCont, value=self.contentPiece.GetEpicArcProgressRatio(), align=uiconst.TOBOTTOM, padding=(0, 2, 60, 0), gaugeHeight=7)

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetEpicArcName())
        self.subtitleLabel.SetText(self.contentPiece.GetOwnerName())
        text = self.contentPiece.GetSolarSystemAndSecurityAndNumJumpsText()
        stateTxt = self.contentPiece.GetEpicArcStateText()
        if stateTxt:
            text += '\n' + stateTxt
        self.bottomLabel.SetText(text)

    def ConstructIcon(self):
        iconSize = 50
        Sprite(name='icon', parent=self.iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0,
         0,
         iconSize,
         iconSize), texturePath=self.contentPiece.GetIconTexturePath())
