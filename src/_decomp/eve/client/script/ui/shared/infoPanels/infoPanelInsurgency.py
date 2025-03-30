#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelInsurgency.py
from carbonui import TextColor
from carbonui.uianimations import animations
from eve.client.script.ui.services.insurgenceDashboardSvc import WrapCallbackWithErrorHandling
from functools import partial
import eveicon
import gametime
import localization
import uthread2
from carbonui.primitives.line import Line
from carbonui.primitives.fill import Fill
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.infoPanels.warehouseRaidUI.scoreboard import ScoreRow
from eve.common.script.util.facwarCommon import IsPirateFWFaction
from localization import GetByLabel
import carbonui
import carbonui.const as uiconst
import evelink
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst
from pirateinsurgency.client.dashboard.const import GetCorruptionIconForStage, GetSuppressionIconForStage
from pirateinsurgency.client.dashboard.widgets.gauge import SuppressionGauge, CorruptionGauge
from pirateinsurgency.const import CAMPAIGN_STATE_FORECASTING

class InfoPanelInsurgency(InfoPanelBase):
    default_name = 'InfoPanelInsurgency'
    default_iconTexturePath = eveicon.pirate_insurgencies
    default_state = uiconst.UI_PICKCHILDREN
    default_height = 120
    label = 'UI/PirateInsurgencies/dashboardCaption'
    hasSettings = False
    panelTypeID = infoPanelConst.PANEL_INSURGENCY
    __notifyevents__ = InfoPanelBase.__notifyevents__ + ['OnCorruptionValueChanged_Local', 'OnSuppressionValueChanged_Local']
    ICE_HEIST_PIRATE_WIN_MESSAGE_ID = 706338
    ICE_HEIST_EMPIRE_WIN_MESSAGE_ID = 706334

    def ApplyAttributes(self, attributes):
        self.dashboardSvc = sm.GetService('insurgencyDashboardSvc')
        self.towGameSvc = sm.GetService('towGameSvc')
        self.corruptionStages = None
        self.suppressionsStages = None
        self.snapshot = None
        self.scoreRowsCont = None
        self.currentNumerator = None
        self.currentDenominator = None
        self.currentVanguardNumerator = None
        self.currentVanguardDenominator = None
        InfoPanelBase.ApplyAttributes(self, attributes)
        snapshot = None
        for snapshot in self.dashboardSvc.GetCurrentCampaignSnapshots():
            if session.solarsystemid2 in snapshot.coveredSolarsystemIDs:
                snapshot = snapshot
                break

        self.snapshot = snapshot
        if self.snapshot is not None:
            if self.snapshot.fsmState == CAMPAIGN_STATE_FORECASTING:
                self.PredictionState(self.snapshot)
            else:
                self.ActiveInsurgencyState()
        self.empireHeistScoreRow = None
        self.pirateHeistScoreRow = None
        self.scoreboardCont = ContainerAutoSize(name='scoreboardCont', parent=self.mainCont, align=uiconst.TOTOP)
        self.currentTowGameSnapshot = self.towGameSvc.GetCurrentTowGame()
        if self.currentTowGameSnapshot is not None:
            self.OnTowGameAdded(self.currentTowGameSnapshot)
        self.towGameSvc.SIGNAL_OnTowGameAdded.connect(self.OnTowGameAdded)
        self.towGameSvc.SIGNAL_OnTowGameRemoved.connect(self.OnTowGameRemoved)
        self.towGameSvc.SIGNAL_OnTowGameUpdated.connect(self.OnTowGameScoreUpdated)

    def Close(self):
        super(InfoPanelInsurgency, self).Close()
        self.towGameSvc.SIGNAL_OnTowGameAdded.disconnect(self.OnTowGameAdded)
        self.towGameSvc.SIGNAL_OnTowGameRemoved.disconnect(self.OnTowGameRemoved)
        self.towGameSvc.SIGNAL_OnTowGameUpdated.disconnect(self.OnTowGameScoreUpdated)

    def PredictionState(self, snapshot):
        self.headerTextCont = ContainerAutoSize(name='headerTextCont', parent=self.headerCont, align=uiconst.CENTERLEFT, height=23, alignMode=uiconst.TOLEFT)
        link = evelink.local_service_link(method='OpenInsurgencyDashboard', text=GetByLabel('UI/PirateInsurgencies/dashboardCaption'))
        self.title = self.headerCls(name='title', text=link, parent=self.headerTextCont, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        cont = Container(parent=self.mainCont, align=uiconst.TOTOP, height=100, width=50, state=uiconst.UI_NORMAL, hint=GetByLabel('UI/PirateInsurgencies/forecastingTooltip'))
        carbonui.TextDetail(parent=cont, align=uiconst.TOTOP, text=GetByLabel('UI/PirateInsurgencies/nextInsurgencyIn'), top=5)
        timerCont = ContainerAutoSize(parent=cont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        timeString = localization.formatters.FormatTimeIntervalShort(max(0, snapshot.stateExpiryTimestamp - gametime.GetWallclockTime()), showFrom='hour', showTo='second')
        time = carbonui.TextHeadline(parent=timerCont, align=uiconst.TOTOP, text=timeString)

        def update_loop():
            while not self.destroyed:
                timeString = localization.formatters.FormatTimeIntervalShort(max(0, snapshot.stateExpiryTimestamp - gametime.GetWallclockTime()), showFrom='hour', showTo='second')
                time.SetText(timeString)
                uthread2.Sleep(1)

        uthread2.StartTasklet(update_loop)

    def ActiveInsurgencyState(self):
        self.headerTextCont = ContainerAutoSize(name='headerTextCont', parent=self.headerCont, align=uiconst.CENTERLEFT, height=23, alignMode=uiconst.TOLEFT)
        link = evelink.local_service_link(method='OpenInsurgencyDashboard', text=GetByLabel('UI/PirateInsurgencies/dashboardCaption'))
        self.title = self.headerCls(name='title', text=link, parent=self.headerTextCont, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        self.headerCorruptionGauge = CorruptionGauge(parent=self.headerTextCont, name='CorruptionGauge', align=uiconst.TOLEFT, width=20, height=20, systemID=session.solarsystemid2, stages=[0.15,
         0.35,
         0.55,
         0.75,
         1.0], dashboardSvc=self.dashboardSvc, drawSprite=False, left=10)
        self.headerSuppressionGauge = SuppressionGauge(parent=self.headerTextCont, name='SuppressionGauge', align=uiconst.TOLEFT, width=20, height=20, systemID=session.solarsystemid2, stages=[0.15,
         0.35,
         0.55,
         0.75,
         1.0], dashboardSvc=self.dashboardSvc, drawSprite=False, left=10)
        self.headerCorruptionGauge.Hide()
        self.headerSuppressionGauge.Hide()
        contWidth = 180
        self.cont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, height=64, maxWidth=contWidth, padTop=10, alignMode=uiconst.TOPLEFT)
        self.corruptionCont = Container(name='CorruptionCont', parent=self.cont, align=uiconst.TOPLEFT, width=contWidth / 2, height=120)
        self.suppressionCont = Container(name='suppressionCont', parent=self.cont, align=uiconst.TOPLEFT, width=contWidth / 2, left=contWidth / 2, height=120)
        self.corruptionLoadingWheel = LoadingWheel(parent=ContainerAutoSize(parent=self.corruptionCont, align=uiconst.TOTOP), align=uiconst.TOTOP)
        self.dashboardSvc.RequestCorruptionStages(WrapCallbackWithErrorHandling(self.CorruptionStagesCallback, parentContainer=self.corruptionCont, onErrorCallback=self.corruptionLoadingWheel.Hide))
        self.suppressionLoadingWheel = LoadingWheel(parent=ContainerAutoSize(parent=self.suppressionCont, align=uiconst.TOTOP), align=uiconst.TOTOP)
        self.dashboardSvc.RequestSuppressionStages(WrapCallbackWithErrorHandling(self.SuppressionStagesCallback, parentContainer=self.suppressionCont, onErrorCallback=self.suppressionLoadingWheel.Hide))

    def OnTowGameAdded(self, towGameSnapshot):
        self.scoreboardCont.Flush()
        Fill(bgParent=self.scoreboardCont, color=eveColor.BLACK, opacity=0.15)
        carbonui.TextHeader(parent=self.scoreboardCont, align=uiconst.TOTOP, padding=(8, 3, 8, 8), text=GetByLabel('UI/PirateInsurgencies/warehouseRaid/warehouseRaidCaption'))
        self.scoreRowsCont = ContainerAutoSize(parent=self.scoreboardCont, align=uiconst.TOTOP)
        self.pirateHeistScoreRow = ScoreRow(iconTexturePath=eveicon.pirate_insurgencies, parent=self.scoreRowsCont, label=GetByLabel('UI/PirateInsurgencies/warehouseRaid/piratesProgress'), align=uiconst.TOTOP, padding=(8, 3, 8, 0), denominator=towGameSnapshot.winThreshold)
        self.empireHeistScoreRow = ScoreRow(iconTexturePath=eveicon.factional_warfare, parent=self.scoreRowsCont, label=GetByLabel('UI/PirateInsurgencies/warehouseRaid/empiresProgress'), align=uiconst.TOTOP, padding=(8, 0, 8, 0), denominator=towGameSnapshot.winThreshold)
        self.OnTowGameScoreUpdated(towGameSnapshot)

    def OnTowGameRemoved(self, *args):
        self.scoreboardCont.Flush()

    def OnTowGameScoreUpdated(self, towGameSnapshot):
        if self.scoreRowsCont is None or self.scoreRowsCont.destroyed:
            return
        self.currentTowGameSnapshot = towGameSnapshot
        score = towGameSnapshot.scoreByFactionID
        callback = None
        for k, v in score.iteritems():
            if v == towGameSnapshot.winThreshold:
                callback = partial(self.SetTowGameWinner, k)
            if IsPirateFWFaction(k):
                if self.pirateHeistScoreRow:
                    self.pirateHeistScoreRow.SetValue(v, callback=callback)
            elif self.empireHeistScoreRow:
                self.empireHeistScoreRow.SetValue(v, callback=callback)

    def SetTowGameWinner(self, factionID):

        def _setWinnerText():
            if self.scoreRowsCont is not None:
                if IsPirateFWFaction(factionID):
                    message = localization.GetByMessageID(self.ICE_HEIST_PIRATE_WIN_MESSAGE_ID)
                else:
                    message = GetByLabel(self.ICE_HEIST_EMPIRE_WIN_MESSAGE_ID)
                self.scoreRowsCont.Flush()
                self.scoreRowsCont = None
                label = EveLabelSmall(parent=self.scoreboardCont, align=uiconst.TOTOP, text=message, padding=(16, 3, 8, 8), opacity=0, color=TextColor.NORMAL)
                animations.FadeTo(label, endVal=TextColor.NORMAL.opacity, duration=uiconst.TIME_ENTRY)

        if self.scoreRowsCont is not None:
            animations.FadeOut(self.scoreRowsCont, callback=_setWinnerText)

    def CorruptionStagesCallback(self, stages):
        self.corruptionStages = stages
        self.corruptionLoadingWheel.Hide()
        self.corruptionGaugeCont = CorruptionGaugeCont(parent=self.corruptionCont, align=uiconst.TOTOP, height=64, stages=self.corruptionStages)
        self.corruptionStageLabelCont = Container(parent=self.corruptionCont, align=uiconst.TOTOP, height=20)
        self.corruptionLabelCont = Container(parent=self.corruptionCont, align=uiconst.TOTOP, height=20)

        def SetCorruptionText(data):
            self.currentNumerator = data.numerator
            self.currentDenominator = data.denominator
            self.currentVanguardNumerator = data.vanguardNumerator
            self.currentVanguardDenominator = data.vanguardDenominator
            self.SetCorruptionText(self.currentNumerator, self.currentDenominator, self.currentVanguardNumerator, self.currentVanguardDenominator, data.stage)

        self.dashboardSvc.RequestLocalSystemCorruption(WrapCallbackWithErrorHandling(SetCorruptionText, parentContainer=None))

    def SetCorruptionText(self, currentCorruption, maxCorruption, vanguardNumerator, vanguardDenominator, stage):
        percentageText = '{:.1%}'.format(float(currentCorruption) / float(maxCorruption))
        self.corruptionStageLabelCont.Flush()
        self.corruptionLabelCont.Flush()
        self.corruptionStageLabel = carbonui.TextBody(parent=self.corruptionStageLabelCont, align=uiconst.CENTERTOP, text=GetByLabel('UI/PirateInsurgencies/stageLabel', stage=stage), bold=True)
        carbonui.TextBody(parent=self.corruptionLabelCont, align=uiconst.CENTERTOP, text=GetByLabel('UI/PirateInsurgencies/corruption'))
        self.corruptionGaugeCont.corruptionPercentage.SetText(percentageText)
        self.corruptionGaugeCont.corruptionGauge.SetIcon(GetCorruptionIconForStage(stage))
        systemEffectsTextList = []
        for i in range(1, stage + 1):
            systemEffect = GetByLabel('UI/PirateInsurgencies/SystemEffects/CorruptionStage{}Effect'.format(i))
            if systemEffect == '':
                continue
            systemEffectsTextList.append(systemEffect)

        systemEffectsText = '<br>'.join(systemEffectsTextList)
        vanguardContribution = 0.0
        if vanguardNumerator and vanguardDenominator:
            vanguardContribution = float(vanguardNumerator) / float(vanguardDenominator) * 100
        self.corruptionGaugeCont.SetSystemEffectHintText(systemEffectsText)
        self.corruptionGaugeCont.SetVanguardContribtution(vanguardContribution)

    def SuppressionStagesCallback(self, stages):
        self.suppressionStages = stages
        self.suppressionLoadingWheel.Hide()
        self.suppressionGaugeCont = SuppressionGaugeCont(parent=self.suppressionCont, align=uiconst.TOTOP, height=64, stages=self.suppressionStages)
        self.suppressionStageLabelCont = Container(parent=self.suppressionCont, align=uiconst.TOTOP, height=20)
        self.suppressionLabelCont = Container(parent=self.suppressionCont, align=uiconst.TOTOP, height=20)

        def SetSuppressionText(data):
            self.SetSuppressionText(data.numerator, data.denominator, data.vanguardNumerator, data.vanguardDenominator, data.stage)

        self.dashboardSvc.RequestLocalSystemSuppression(WrapCallbackWithErrorHandling(SetSuppressionText, parentContainer=None))

    def SetSuppressionText(self, currentSuppression, maxSuppression, vanguardNumerator, vanguardDenominator, stage):
        percentageText = '{:.1%}'.format(float(currentSuppression) / float(maxSuppression))
        self.suppressionStageLabelCont.Flush()
        self.suppressionLabelCont.Flush()
        self.suppressionStageLabel = carbonui.TextBody(parent=self.suppressionStageLabelCont, align=uiconst.CENTERTOP, text=GetByLabel('UI/PirateInsurgencies/stageLabel', stage=stage), bold=True)
        carbonui.TextBody(parent=self.suppressionLabelCont, align=uiconst.CENTERTOP, text=GetByLabel('UI/PirateInsurgencies/suppression'))
        self.suppressionGaugeCont.suppressionPercentage.SetText(percentageText)
        self.suppressionGaugeCont.suppressionGauge.SetIcon(GetSuppressionIconForStage(stage))
        systemEffectsTextList = []
        for i in range(1, stage + 1):
            if i == 3:
                systemEffect1 = GetByLabel('UI/PirateInsurgencies/SystemEffects/SuppressionStage{}Effect1'.format(i))
                systemEffect2 = GetByLabel('UI/PirateInsurgencies/SystemEffects/SuppressionStage{}Effect2'.format(i))
                if systemEffect1:
                    systemEffectsTextList.append(systemEffect1)
                if systemEffect2:
                    systemEffectsTextList.append(systemEffect2)
            else:
                systemEffect = GetByLabel('UI/PirateInsurgencies/SystemEffects/SuppressionStage{}Effect'.format(i))
                if systemEffect:
                    systemEffectsTextList.append(systemEffect)

        systemEffectsText = '<br>'.join(systemEffectsTextList)
        vanguardContribution = 0.0
        if vanguardNumerator and vanguardDenominator:
            vanguardContribution = float(vanguardNumerator) / float(vanguardDenominator) * 100
        self.suppressionGaugeCont.SetSystemEffectHintText(systemEffectsText)
        self.suppressionGaugeCont.SetVanguardContribution(vanguardContribution)

    def OnStartModeChanged(self, oldMode):
        if self.snapshot.fsmState is not None and self.snapshot.fsmState != CAMPAIGN_STATE_FORECASTING:
            if self.mode == infoPanelConst.MODE_COMPACT:
                if oldMode:
                    self.headerCorruptionGauge.Show()
                    self.headerSuppressionGauge.Show()
                else:
                    self.headerCorruptionGauge.Show()
                    self.headerSuppressionGauge.Show()
            else:
                self.headerCorruptionGauge.Hide()
                self.headerSuppressionGauge.Hide()

    @staticmethod
    def IsAvailable():
        isinsurgencysystem = sm.GetService('insurgencyDashboardSvc').IsSystemAffectedByInsurgency(session.solarsystemid2)
        return isinsurgencysystem

    def OnSuppressionValueChanged_Local(self, systemID, data):
        if systemID != session.solarsystemid2:
            return
        if self.suppressionStages is None:
            return
        self.SetSuppressionText(data.numerator, data.denominator, data.vanguardNumerator, data.vanguardDenominator, data.stage)

    def OnCorruptionValueChanged_Local(self, systemID, data):
        if systemID != session.solarsystemid2:
            return
        if self.corruptionStages is None:
            return
        self.SetCorruptionText(data.numerator, data.denominator, data.vanguardNumerator, data.vanguardDenominator, data.stage)


class CorruptionGaugeCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.dashboardSvc = sm.GetService('insurgencyDashboardSvc')
        self.stages = attributes.get('stages')
        self.hintText = ''
        self.vanguardContribution = 0
        self.ConstructLayout()

    def ConstructLayout(self):
        self.hintCont = Container(align=uiconst.CENTER, parent=self, state=uiconst.UI_NORMAL, height=64, width=64)
        self.hintCont.LoadTooltipPanel = self.hintContTooltipFun
        self.corruptionPercentage = carbonui.TextBody(parent=self, align=uiconst.CENTER, text='-%')
        self.corruptionGaugeOverlay = Sprite(align=uiconst.CENTER, parent=self, texturePath='res:/UI/Texture/classes/pirateinsurgencies/info_panel/circle.png', state=uiconst.UI_DISABLED, height=58, width=58)
        self.corruptionPercentage.Hide()
        self.corruptionGaugeOverlay.Hide()
        self.corruptionGauge = CorruptionGauge(parent=self, name='CorruptionGauge', align=uiconst.TOTOP, width=64, height=64, systemID=session.solarsystemid2, stages=self.stages, dashboardSvc=self.dashboardSvc)

    def SetSystemEffectHintText(self, hintText):
        self.hintText = hintText

    def SetVanguardContribtution(self, contribution):
        self.vanguardContribution = contribution

    def hintContTooltipFun(self, panel, *args):
        showStagesInformation = self.hintText and self.hintText != ''
        if self.vanguardContribution == 0 and not showStagesInformation:
            return
        panel.LoadGeneric2ColumnTemplate()
        if showStagesInformation:
            panel.AddLabelMedium(text=self.hintText, colSpan=2, rowSpan=1)
        if self.vanguardContribution > 0:
            if showStagesInformation:
                panel.AddCell(Line(weight=1), colSpan=2)
            panel.AddCell(Sprite(texturePath='res:/UI/Texture/classes/pirateinsurgencies/vanguard_logo_v.png', width=32, height=32, cellPadding=0))
            text = GetByLabel('UI/PirateInsurgencies/vanguardCorruptingThisSystemTooltip', contribution=self.vanguardContribution)
            panel.AddLabelMedium(text=text)

    def OnMouseEnter(self, *args):
        self.corruptionPercentage.Show()
        self.corruptionGaugeOverlay.Show()

    def OnMouseExit(self, *args):
        self.corruptionPercentage.Hide()
        self.corruptionGaugeOverlay.Hide()


class SuppressionGaugeCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.dashboardSvc = sm.GetService('insurgencyDashboardSvc')
        self.stages = attributes.get('stages')
        self.hintText = ''
        self.vanguardContribution = 0
        self.ConstructLayout()

    def ConstructLayout(self):
        self.hintCont = Container(align=uiconst.CENTER, parent=self, state=uiconst.UI_NORMAL, height=64, width=64)
        self.hintCont.LoadTooltipPanel = self.hintContTooltipFun
        self.suppressionPercentage = carbonui.TextBody(parent=self, align=uiconst.CENTER, text='-%')
        self.suppressionGaugeOverlay = Sprite(align=uiconst.CENTER, parent=self, texturePath='res:/UI/Texture/classes/pirateinsurgencies/info_panel/circle.png', state=uiconst.UI_DISABLED, height=58, width=58)
        self.suppressionPercentage.Hide()
        self.suppressionGaugeOverlay.Hide()
        self.suppressionGauge = SuppressionGauge(parent=self, name='SuppressionGauge', align=uiconst.TOTOP, width=64, height=64, systemID=session.solarsystemid2, stages=self.stages, dashboardSvc=self.dashboardSvc)

    def SetSystemEffectHintText(self, hintText):
        self.hintText = hintText

    def SetVanguardContribution(self, contribution):
        self.vanguardContribution = contribution

    def hintContTooltipFun(self, panel, *args):
        showStagesInformation = self.hintText and self.hintText != ''
        if self.vanguardContribution == 0 and not showStagesInformation:
            return
        panel.LoadGeneric2ColumnTemplate()
        if showStagesInformation:
            panel.AddLabelMedium(text=self.hintText, colSpan=2, rowSpan=1)
        if self.vanguardContribution > 0:
            if showStagesInformation:
                panel.AddCell(Line(weight=1), colSpan=2)
            panel.AddCell(Sprite(texturePath='res:/UI/Texture/classes/pirateinsurgencies/vanguard_logo_v.png', width=32, height=32, cellPadding=0))
            text = GetByLabel('UI/PirateInsurgencies/vanguardSuppressingThisSystemTooltip', contribution=self.vanguardContribution)
            panel.AddLabelMedium(text=text)

    def OnMouseEnter(self, *args):
        self.suppressionPercentage.Show()
        self.suppressionGaugeOverlay.Show()

    def OnMouseExit(self, *args):
        self.suppressionPercentage.Hide()
        self.suppressionGaugeOverlay.Hide()
