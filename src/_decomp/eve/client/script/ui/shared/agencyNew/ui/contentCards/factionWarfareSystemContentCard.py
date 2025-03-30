#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\factionWarfareSystemContentCard.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveIcon import LogoIcon
from eve.client.script.ui.control.eveLabel import EveCaptionSmall
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from eve.client.script.ui.shared.factionalWarfare.captureGauge import CaptureGauge
from eve.client.script.ui.control import eveLabel
from fwwarzone.client.dashboard.gauges.contestedGauge import ContestedFWSystemGauge

class FactionWarfareSystemContentCard(BaseContentCard):
    default_name = 'FactionWarfareSystemContentCard'

    def ApplyAttributes(self, attributes):
        super(FactionWarfareSystemContentCard, self).ApplyAttributes(attributes)
        self.UpdateCaptureGauge()

    def ConstructContent(self):
        super(FactionWarfareSystemContentCard, self).ConstructContent()
        self.ConstructAdjencyLabel()
        self.ConstructCaptureGaugeContainer()
        self.ConstructSystemCaptureGauge()
        self.ConstructFactionIcon()

    def ConstructFactionIcon(self):
        Sprite(parent=self.mainCont, align=uiconst.TOPRIGHT, texturePath=LogoIcon.GetFactionIconTexturePath(self.contentPiece.ownerID), width=32, height=32, hint=cfg.eveowners.Get(self.contentPiece.ownerID).name)

    def ConstructTitleLabel(self):
        self.titleLabel = EveCaptionSmall(name='cardTitleLabel', parent=self.mainCont, align=uiconst.TOTOP)

    def ConstructAdjencyLabel(self):
        padTopBottom = self.bottomLabel.padTop
        self.bottomLabel.padBottom = 0
        self.adjacencyLabel = eveLabel.EveLabelMedium(name='adjacencyLabel', parent=self.bottomCont, align=uiconst.TOTOP, padding=(self.bottomLabel.padLeft,
         0,
         self.bottomLabel.padRight,
         padTopBottom))

    def ConstructCaptureGaugeContainer(self):
        self.systemCaptureGaugeContainer = Container(name='systemCaptureGaugeContainer', parent=self.bottomCont, align=uiconst.TOLEFT, width=20, idx=0, padLeft=4)

    def ConstructSystemCaptureGauge(self):
        self.controlGauge = ContestedFWSystemGauge(parent=self.systemCaptureGaugeContainer, align=uiconst.CENTERLEFT, systemId=self.contentPiece.solarSystemID, radius=10, displayAdjacencyIcon=False)
        self.controlGauge.DelegateEvents(self)

    def UpdateCaptureGauge(self):
        attackerColor, defenderColor = self.contentPiece.GetAttackerDefenderColors()
        self.controlGauge.SetGaugeColors(attackerColor, defenderColor)
        contestedFraction = self.contentPiece.GetContestedFraction()
        self.systemCaptureGaugeContainer.display = bool(contestedFraction)
        self.controlGauge.UpdateChart(contestedFraction)

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetSystemAndSecurityText())
        self.subtitleLabel.SetText(self.contentPiece.GetNumJumpsText())
        self.UpdateCaptureStatusLabel()
        self.UpdateAdjacency()

    def UpdateCaptureStatusLabel(self):
        self.bottomLabel.SetText(self.contentPiece.GetSystemStatusText())
        captureStatusColor = self.contentPiece.GetSystemCaptureStatusColor()
        self.bottomLabel.SetRGBA(*captureStatusColor)

    def UpdateAdjacency(self):
        self.adjacencyLabel.SetText(self.contentPiece.GetAdjacencyText())
        self.controlGauge.SetAdjacency(self.contentPiece.GetAdjacencyState())
