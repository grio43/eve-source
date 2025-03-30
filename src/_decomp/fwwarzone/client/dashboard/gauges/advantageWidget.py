#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\gauges\advantageWidget.py
import uthread2
from carbonui import TextAlign, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveCaptionSmall
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from fwwarzone.client.dashboard.const import FACTION_ID_TO_FLAT_ICON, FACTION_ID_TO_COLOR
from localization import GetByLabel
from signals import Signal

class AdvantageWidget(Container):
    default_animateIn = True
    __notifyevents__ = ['OnSessionChanged', 'OnSolarsystemAdvantageStateUpdated_Local']
    default_height = 58

    def ApplyAttributes(self, attributes):
        super(AdvantageWidget, self).ApplyAttributes(attributes)
        self.systemId = attributes.get('systemId')
        self.animateIn = attributes.get('animateIn', AdvantageWidget.default_animateIn)
        self.fwAdvantageSvc = sm.GetService('fwAdvantageSvc')
        self.fwWarzoneSvc = sm.GetService('fwWarzoneSvc')
        self.attackerGauge = None
        self.defenderGauge = None
        self.deltaGauge = None
        self.updateThread = None
        self.onNetScoreChange = Signal(signalName='OnChangeSignal')
        sm.RegisterNotify(self)
        self.ConstructLayout()

    def GetScoreBreakdownHintText(self, factionID):
        advantageState = self.fwAdvantageSvc.GetAdvantageState(self.systemId)
        contributionText = u'{0:.0%}'.format(advantageState.GetContributionScore(factionID))
        floorText = u'{0:.0%}'.format(advantageState.GetTerrainScore(factionID))
        return GetByLabel('UI/FactionWarfare/advantagebreakdownTooltip', objectives=contributionText, floor=floorText)

    def AdvantageChanged(self):
        self.UpdateAdvantage()

    def UpdateAdvantage(self):
        if self.updateThread and self.updateThread.IsAlive():
            self.updateThread.kill()
            self.updateThread = None
        self.updateThread = uthread2.StartTasklet(self.UpdateAdvantage_thread)

    def UpdateAdvantage_thread(self):
        self.advantageState = self.fwAdvantageSvc.GetAdvantageState(self.systemId)
        occupationState = self.fwWarzoneSvc.GetOccupationState(self.systemId)
        defenderId = occupationState.occupierID
        attackerId = occupationState.attackerID
        netScore = self.advantageState.GetNetAdvantageScore(defenderId, attackerId)
        newWinner = None
        if netScore > 0:
            newWinner = defenderId
        elif netScore < 0:
            newWinner = attackerId
        attackerScore = self.advantageState.GetAdvantageScore(attackerId)
        self.attackerGauge.SetValue(attackerScore, animate=self.animateIn)
        self.attackerGauge.hint = self.GetScoreBreakdownHintText(attackerId)
        defenderScore = self.advantageState.GetAdvantageScore(defenderId)
        self.defenderGauge.SetValue(defenderScore, animate=self.animateIn)
        self.defenderGauge.hint = self.GetScoreBreakdownHintText(defenderId)
        self.onNetScoreChange(netScore, newWinner)

    def OnSessionChanged(self, *args):
        if self.systemId == session.solarsystemid2:
            self.AdvantageChanged()

    def OnSolarsystemAdvantageStateUpdated_Local(self, *args):
        if self.systemId == session.solarsystemid2:
            self.AdvantageChanged()

    def ConstructLayout(self):
        occupationState = self.fwWarzoneSvc.GetOccupationState(self.systemId)
        defenderId = occupationState.occupierID
        attackerId = occupationState.attackerID
        self.deltaGauge = AdvantageDeltaGauge(parent=self, align=uiconst.TORIGHT, width=54, onchange=self.onNetScoreChange, animate=self.animateIn)
        self.attackerGauge = Gauge(parent=self, align=uiconst.TOTOP, gaugeHeight=8, padTop=12, color=FACTION_ID_TO_COLOR[attackerId])
        self.defenderGauge = Gauge(parent=self, align=uiconst.TOBOTTOM, gaugeHeight=8, padBottom=12, color=FACTION_ID_TO_COLOR[defenderId])
        self.UpdateAdvantage()


class AdvantageDeltaGauge(Container):
    default_state = uiconst.UI_NORMAL
    default_animate = True

    def ApplyAttributes(self, attributes):
        self.hintText = ''
        super(AdvantageDeltaGauge, self).ApplyAttributes(attributes)
        self.onChangeSignal = attributes.get('onchange')
        self.animate = attributes.get('animate', AdvantageDeltaGauge.default_animate)
        self.onChangeSignal.connect(self.Update)
        self.ConstructLayout()

    def GetHint(self):
        return self.hintText

    def Update(self, score, factionIDWithAdvantage):
        self.loadingWheel.Hide()
        if score < 0:
            score = score * -1
        self.gauge.SetValue(score, animate=self.animate)
        self.label.SetText(u'{0:.0%}'.format(score))
        if factionIDWithAdvantage is not None:
            self.ShowOneSideHasAdvantage(factionIDWithAdvantage, score)
        else:
            self.ShowNeitherSideHasAdvantage()

    def ShowNeitherSideHasAdvantage(self):
        self.hintText = GetByLabel('UI/FactionWarfare/neitherSideHasAdvantage')
        self.sprite.state = uiconst.UI_HIDDEN
        self.label.state = uiconst.UI_HIDDEN
        self.zeroLabel.state = uiconst.UI_DISABLED

    def ShowOneSideHasAdvantage(self, factionId, score):
        factionName = cfg.eveowners.Get(factionId).name
        percentageBonusText = u'{0:.0%}'.format(score)
        self.hintText = GetByLabel('UI/FactionWarfare/OneSideHasAdvantageBonus', factionName=factionName, percentageText=percentageBonusText)
        self.sprite.SetTexturePath(FACTION_ID_TO_FLAT_ICON[factionId])
        self.sprite.color = FACTION_ID_TO_COLOR[factionId]
        self.sprite.state = uiconst.UI_DISABLED
        self.label.state = uiconst.UI_DISABLED
        self.zeroLabel.state = uiconst.UI_HIDDEN

    def ConstructLayout(self):
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER, pos=(-3,
         0,
         self.width,
         self.width))
        self.gauge = GaugeCircular(parent=self, radius=29, lineWidth=3.5, left=-5, color=eveColor.WHITE, state=uiconst.UI_DISABLED)
        self.label = EveLabelSmall(parent=self, align=uiconst.CENTERBOTTOM, top=9, left=-4, textAlign=TextAlign.LEFT, state=uiconst.UI_DISABLED)
        self.zeroLabel = EveCaptionSmall(text='{0:.0%}'.format(0.0), parent=self, align=uiconst.CENTER, left=-4, textAlign=TextAlign.LEFT, state=uiconst.UI_HIDDEN)
        self.sprite = Sprite(parent=self, width=32, height=32, top=6, left=-4, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED)
