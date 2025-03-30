#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelFactionalWarfare.py
import carbonui.const as uiconst
import evelink
import localization
import uthread
from carbon.common.script.util import timerstuff
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from characterdata.races import get_race_name
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge, EveLabelSmall
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.factionalWarfare.fwSystemBenefitIcon import FWSystemBenefitIcon
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst
from evelink.client import owner_link
from factionwarfare.client.text import GetSystemCaptureStatusText
from fwwarzone.client.dashboard.const import FACTION_ID_TO_COLOR, ADJACENCY_TO_LABEL_SYSTEM_TEXT
from fwwarzone.client.dashboard.gauges.contestedGauge import ContestedFWSystemGauge
from fwwarzone.client.util import GetAttackerDefenderColors
from spacecomponents.common.componentConst import FW_SCOREBOARD
from spacecomponents.common.data import get_space_component_for_type
from eve.common.lib import appConst

class InfoPanelFactionalWarfare(InfoPanelBase):
    default_name = 'InfoPanelFactionalWarfare'
    default_iconTexturePath = 'res:/UI/Texture/Classes/InfoPanels/FactionalWarfare.png'
    default_state = uiconst.UI_PICKCHILDREN
    default_height = 120
    label = 'UI/Map/StarMap/FactionalWarfare'
    hasSettings = False
    panelTypeID = infoPanelConst.PANEL_FACTIONAL_WARFARE
    COLOR_RED = (0.5, 0.0, 0.0, 1.0)
    COLOR_WHITE = (0.5, 0.5, 0.5, 1.0)
    ICONSIZE = 20
    __notifyevents__ = InfoPanelBase.__notifyevents__ + ['OnWarzoneOccupationStateUpdated_Local',
     'OnSolarsystemAdvantageStateUpdated_Local',
     'OnFwBattlefieldUpdated',
     'OnFwBattlefieldAdded']

    def ApplyAttributes(self, attributes):
        self.fwWarzoneSvc = sm.GetService('fwWarzoneSvc')
        self.fwVictoryPointSvc = sm.GetService('fwVictoryPointSvc')
        self.statusLabel = None
        self.compactTitle = None
        self.adjacencyLabel = None
        InfoPanelBase.ApplyAttributes(self, attributes)
        self.controlGauge = None
        self.isGaugeInitialized = False
        self.benefitIcons = []
        self.headerTextCont = Container(name='headerTextCont', parent=self.headerCont, align=uiconst.TOALL)
        link = evelink.local_service_link(method='OpenMilitia', text=localization.GetByLabel('UI/FactionWarfare/FactionalWarfare'))
        self.title = self.headerCls(name='title', text=link, parent=self.headerTextCont, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
        self.compactTitle = eveLabel.EveLabelMedium(name='compactTitle', text=link, parent=self.headerTextCont, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
        self.compactTitle.Hide()
        topCont = ContainerAutoSize(name='topCont', parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        self.bottomContainer = ContainerAutoSize(parent=self.mainCont, name='bottomContainer', align=uiconst.TOTOP)
        self.scoreboardCont = ContainerAutoSize(parent=self.mainCont, name='scoreboardCont', align=uiconst.TOTOP)
        fwOccupationState = self.fwWarzoneSvc.GetLocalOccupationState()
        adjacencyText = self.GetAdjacencyText()
        textCont = VerticalCenteredContainer(parent=topCont, name='textCont', align=uiconst.TOTOP)
        if fwOccupationState:
            gaugeRadius = 25
            gaugeSizeCont = gaugeRadius * 2
            textCont.padLeft = self.bottomContainer.padLeft = gaugeSizeCont + 10
            gaugeCont = Container(name='gaugeCont', parent=topCont, align=uiconst.CENTERLEFT, pos=(0,
             0,
             gaugeSizeCont,
             gaugeSizeCont))
            topCont.minHeight = gaugeSizeCont
            self.controlGauge = self.AddGauge(fwOccupationState, gaugeCont, uiconst.CENTER, gaugeRadius)
            self.headerControlGauge = self.AddGauge(fwOccupationState, self.headerCont, uiconst.CENTERLEFT, 10, False)
            self.headerControlGauge.chart.state = uiconst.UI_DISABLED
            self.compactTitle.padLeft = self.headerControlGauge.width + 10
            self.headerControlGauge.OnClick = lambda *args: sm.GetService('cmd').OpenMilitia()
            self.headerControlGauge.Hide()
        self.statusLabel = eveLabel.EveLabelMedium(name='statusLabel', parent=textCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.adjacencyLabel = eveLabel.EveLabelMedium(name='adjacencyLabel', parent=textCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, top=2, text=adjacencyText)
        self.netAdvantageLabel = EveLabelSmall(parent=textCont, align=uiconst.TOTOP, text='', state=uiconst.UI_NORMAL, top=10)
        self.ConstructScoreboards()
        self.bottomContainer.EnableAutoSize()
        self.mainCont.EnableAutoSize()
        self.UpdateLabels()
        uthread.new(self.UpdateAdvantageSection_thread)

    def _GetAdvantageTextAndHint(self):
        occupationState = self.fwWarzoneSvc.GetOccupationState(session.solarsystemid2)
        if occupationState is None:
            return (None, None)
        defenderId = occupationState.occupierID
        attackerId = occupationState.attackerID
        advantageState = sm.GetService('fwAdvantageSvc').GetAdvantageState(session.solarsystemid2)
        netScore = advantageState.GetNetAdvantageScore(defenderId, attackerId)
        winner = None
        if netScore > 0:
            winner = defenderId
        elif netScore < 0:
            winner = attackerId
        displayScore = netScore
        if netScore < 0:
            displayScore = netScore * -1
        if winner is not None:
            percentageBonusText = u'{0:.0%}'.format(displayScore)
            winnerName = _GetRaceName(winner)
            winnerNameLink = owner_link(winner, winnerName)
            text = localization.GetByLabel('UI/FactionWarfare/shortAdvantageLine', factionName=winnerNameLink, netAdvantagePercent=percentageBonusText)
            contributionText = u'{0:.0%}'.format(advantageState.GetContributionScore(winner))
            floorText = u'{0:.0%}'.format(advantageState.GetTerrainScore(winner))
            hint = localization.GetByLabel('UI/FactionWarfare/advantagebreakdownTooltip', objectives=contributionText, floor=floorText)
            return (text, hint)
        else:
            return (localization.GetByLabel('UI/FactionWarfare/noFactionHasAdvantageShortLine'), None)

    def UpdateAdvantageSection_thread(self):
        if self.netAdvantageLabel is None:
            return
        text, hint = self._GetAdvantageTextAndHint()
        if text is not None:
            self.netAdvantageLabel.SetText(text)
            self.netAdvantageLabel.hint = hint

    def AddGauge(self, fwOccupationState, parent, align, gaugeRadius, showAdjacency = True):
        occupierID = fwOccupationState.occupierID
        attackerID = fwOccupationState.attackerID
        gauge = ContestedFWSystemGauge(parent=parent, align=align, systemId=session.solarsystemid2, radius=gaugeRadius, attackerColor=FACTION_ID_TO_COLOR[attackerID], defenderColor=FACTION_ID_TO_COLOR[occupierID], adjacencyState=fwOccupationState.adjacencyState, displayAdjacencyIcon=showAdjacency)
        return gauge

    @staticmethod
    def IsAvailable():
        return sm.GetService('fwWarzoneSvc').IsWarzoneSolarSystem(session.solarsystemid2)

    def ConstructNormal(self):
        if not self.IsAvailable():
            return
        self.UpdateLabels()
        upgradeLevel = sm.GetService('facwar').GetSolarSystemUpgradeLevel(session.solarsystemid2)
        self.bottomContainer.Flush()
        self.benefitIcons = []
        if upgradeLevel:
            self.ConstructBenefitIcons(upgradeLevel)
        self.UpdateGauges()

    def ConstructBenefitIcons(self, upgradeLevel):
        iconCont = Container(name='iconCont', align=uiconst.TOTOP, parent=self.bottomContainer, padTop=6, height=36)
        benefits = sm.GetService('facwar').GetSystemUpgradeLevelBenefits(upgradeLevel)
        benefits = list(benefits)
        benefits.reverse()
        for benefitType, benefitValue in benefits:
            benefitIcon = FWSystemBenefitIcon(parent=iconCont, align=uiconst.TOLEFT, padRight=12, benefitType=benefitType, benefitValue=benefitValue, opacity=0.0)
            self.benefitIcons.append(benefitIcon)

    def UpdateLabels(self):
        text = self.GetStatusText()
        if self.statusLabel:
            self.statusLabel.text = text
        if self.compactTitle:
            self.compactTitle.text = text
        if self.adjacencyLabel:
            self.adjacencyLabel.text = self.GetAdjacencyText()

    def GetStatusText(self):
        factionID = self.fwWarzoneSvc.GetSystemOccupier(session.solarsystemid2)
        if factionID is None:
            return ''
        victoryPointState = self.fwVictoryPointSvc.GetVictoryPointState(session.solarsystemid2)
        factionOwnerLink = owner_link(factionID)
        statusText = GetSystemCaptureStatusText(victoryPointState)
        if statusText:
            text = '%s: %s' % (factionOwnerLink, statusText)
        else:
            text = factionOwnerLink
        return text

    def GetAdjacencyText(self):
        fwOccupationState = self.fwWarzoneSvc.GetLocalOccupationState()
        if fwOccupationState:
            adjacencyText = ADJACENCY_TO_LABEL_SYSTEM_TEXT[fwOccupationState.adjacencyState]
        else:
            adjacencyText = ''
        return adjacencyText

    def ConstructCompact(self):
        self.UpdateLabels()
        self.UpdateGauges()

    def OnStartModeChanged(self, oldMode):
        uthread.new(self._OnStartModeChanged, oldMode)

    def OnEndModeChanged(self, oldMode):
        if self.mode == infoPanelConst.MODE_NORMAL and oldMode:
            for i, icon in enumerate(self.benefitIcons):
                uicore.animations.BlinkIn(icon, endVal=0.75, timeOffset=0.2 + i * 0.05)

        else:
            for icon in self.benefitIcons:
                icon.opacity = 0.75

    def _OnStartModeChanged(self, oldMode):
        if self.mode == infoPanelConst.MODE_COMPACT:
            if oldMode:
                uicore.animations.FadeOut(self.title, duration=0.3, sleep=True, callback=self.title.Hide)
                self.headerControlGauge.Show()
                uicore.animations.FadeTo(self.headerControlGauge, 0.0, 1.0, duration=0.3)
                self.compactTitle.Show()
                uicore.animations.FadeTo(self.compactTitle, 0.0, 1.0, duration=0.3)
            else:
                self.title.Hide()
                self.headerControlGauge.Show()
                self.compactTitle.Show()
        elif self.headerControlGauge.display:
            uicore.animations.FadeOut(self.headerControlGauge, duration=0.3, sleep=True, callback=self.headerControlGauge.Hide)
            self.compactTitle.Hide()
            self.title.Show()
            uicore.animations.FadeTo(self.title, 0.0, 1.0, duration=0.3)

    def UpdateGauges(self):
        solarSystemID = session.solarsystemid2
        attackerColor, defenderColor = GetAttackerDefenderColors(solarSystemID)
        self.controlGauge.SetGaugeColors(attackerColor, defenderColor)
        self.headerControlGauge.SetGaugeColors(attackerColor, defenderColor)
        victoryPointState = self.fwVictoryPointSvc.GetVictoryPointState(solarSystemID)
        self.controlGauge.UpdateVictoryPointsState(victoryPointState)
        self.controlGauge.UpdateAdjacencyState(self.fwWarzoneSvc.GetLocalOccupationState().adjacencyState)
        self.headerControlGauge.UpdateVictoryPointsState(victoryPointState)
        self.headerControlGauge.UpdateAdjacencyState(self.fwWarzoneSvc.GetLocalOccupationState().adjacencyState)

    def OnWarzoneOccupationStateUpdated_Local(self):
        self.UpdateLabels()
        self.UpdateGauges()

    def OnSolarsystemAdvantageStateUpdated_Local(self):
        uthread.new(self.UpdateAdvantageSection_thread)

    def OnFwBattlefieldUpdated(self):
        self.ConstructScoreboards()

    def ConstructScoreboards(self):
        self.scoreboardCont.Flush()
        scoreboards = sm.GetService('fwWarzoneSvc').GetBattleFieldScoreboards()
        ballpark = sm.GetService('michelle').GetBallpark()
        if not ballpark:
            return
        for eachScoreboardID in scoreboards:
            slimItem = ballpark.GetInvItem(eachScoreboardID)
            if slimItem:
                BattlefieldSection(name='BattlefieldSection_%s' % eachScoreboardID, parent=self.scoreboardCont, itemID=eachScoreboardID, typeID=slimItem.typeID)

    def OnFwBattlefieldAdded(self, itemID, typeID, score):
        for eachScoreboard in self.scoreboardCont.children:
            if eachScoreboard.itemID == itemID:
                eachScoreboard.SetValue(score)
                return

        b = BattlefieldSection(name='BattlefieldSection_%s' % itemID, parent=self.scoreboardCont, itemID=itemID, typeID=typeID)
        b.SetValue(score)


class VerticalCenteredContainer(ContainerAutoSize):

    def __init__(self, **kwargs):
        kwargs['callback'] = self.on_size_change
        super(VerticalCenteredContainer, self).__init__(**kwargs)

    def on_size_change(self):
        if self.children:
            content_height = 0
            for i, child in enumerate(self.children):
                content_height += child.height + child.padTop + child.padBottom
                if i > 0:
                    content_height += child.top

            minHeight = getattr(self.parent, 'minHeight', 0)
            height = max(self.height, minHeight)
            adjusted_top = int(round((height - content_height) / 2.0))
            self.padTop = adjusted_top


FULL_GAUGE_HEIGHT = 6
SMALL_GAUGE_HEIGHT = 4

class BattlefieldSection(ContainerAutoSize):
    default_padTop = 10
    default_minHeight = 35
    default_align = uiconst.TOTOP
    default_alignMode = uiconst.TOBOTTOM
    __notifyevents__ = ['OnFwScoreboardUpdated']

    def ApplyAttributes(self, attributes):
        super(BattlefieldSection, self).ApplyAttributes(attributes)
        self.itemID = attributes.itemID
        self.typeID = attributes.typeID
        fwObjectiveAttributes = get_space_component_for_type(self.typeID, FW_SCOREBOARD)
        self.defenderThreshold = fwObjectiveAttributes.occupierWinsThreshold
        self.attackerThreshold = fwObjectiveAttributes.attackerWinsThreshold
        fwOccupationState = sm.GetService('fwWarzoneSvc').GetOccupationState(session.solarsystemid2)
        if fwOccupationState:
            self.defenderID = fwOccupationState.occupierID
            self.attackerID = fwOccupationState.attackerID
        else:
            self.defenderID = None
            self.attackerID = None
        battleFieldSpriteCont = Container(parent=self, align=uiconst.BOTTOMLEFT, pos=(0, 0, 60, 35))
        battlefieldSprite = Sprite(name='battlefieldSprite', align=uiconst.CENTER, parent=battleFieldSpriteCont, texturePath='res:/UI/Texture/classes/frontlines/battlefield.png', state=uiconst.UI_DISABLED, pos=(-5, 0, 32, 32))
        rightCont = ContainerAutoSize(name='rightCont', parent=self, align=uiconst.TOBOTTOM, alignMode=uiconst.TOTOP, padLeft=battleFieldSpriteCont.left + battleFieldSpriteCont.width)
        EveLabelMedium(name='label', parent=rightCont, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, text=localization.GetByLabel('UI/FactionWarfare/frontlines/BattlefieldScoreboard'))
        attackerColor, defenderColor = GetAttackerDefenderColors(session.solarsystemid2)
        gaugeCont = Container(name='gaugeCont', parent=rightCont, align=uiconst.TOTOP, height=FULL_GAUGE_HEIGHT, padTop=8, padBottom=2)
        self.leftGauge = Gauge(parent=gaugeCont, align=uiconst.TOTOP_NOPUSH, gaugeHeight=FULL_GAUGE_HEIGHT, state=uiconst.UI_PICKCHILDREN, color=defenderColor)
        self.leftGauge.gauge.LoadTooltipPanel = self.LoadLeftGaugeTooltip
        self.leftGauge.gauge.state = uiconst.UI_NORMAL
        self.leftGauge.gaugeGradient.state = uiconst.UI_DISABLED
        self.leftGauge.gaugeCont.state = uiconst.UI_PICKCHILDREN
        self.leftGauge.HideBackground()
        self.rightGauge = Gauge(parent=gaugeCont, align=uiconst.TOTOP_NOPUSH, height=FULL_GAUGE_HEIGHT, color=attackerColor, gaugeAlign=uiconst.TORIGHT_PROP, state=uiconst.UI_PICKCHILDREN)
        self.rightGauge.gauge.LoadTooltipPanel = self.LoadRightGaugeTooltip
        self.rightGauge.gauge.state = uiconst.UI_NORMAL
        self.rightGauge.gaugeGradient.state = uiconst.UI_DISABLED
        self.rightGauge.gaugeCont.state = uiconst.UI_PICKCHILDREN
        self.rightGauge.HideBackground()
        self.UpdateValueFromSlimItem()
        sm.RegisterNotify(self)

    def UpdateValueFromSlimItem(self):
        slimItem = GetSlimItemForItemID(self.itemID)
        if not slimItem:
            return
        value = slimItem.component_fwScoreboard_score or 0
        self.SetValue(value)

    def SetValue(self, newScore):
        pointsInGauges = float(abs(self.defenderThreshold) + self.attackerThreshold)
        progress = (abs(self.defenderThreshold) + newScore) / pointsInGauges
        self.leftGauge.SetValue(1 - progress, animate=False)
        self.rightGauge.SetValue(progress, animate=False)
        if newScore == 0:
            self.leftGauge.gaugeCont.height = FULL_GAUGE_HEIGHT
            self.rightGauge.gaugeCont.height = FULL_GAUGE_HEIGHT
            self.leftGauge.padTop = 0
            self.rightGauge.padTop = 0
        else:
            self.leftGauge.gaugeCont.height = FULL_GAUGE_HEIGHT if newScore < 0 else SMALL_GAUGE_HEIGHT
            self.rightGauge.gaugeCont.height = FULL_GAUGE_HEIGHT if newScore > 0 else SMALL_GAUGE_HEIGHT
            self.leftGauge.padTop = 0 if newScore < 0 else 1
            self.rightGauge.padTop = 0 if newScore > 0 else 1

    def LoadLeftGaugeTooltip(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        label = tooltipPanel.AddLabelMedium()
        updateArgs = (label, self.leftGauge, self.defenderID)
        tooltipUpdated = self._UpdateTooltip(*updateArgs)
        if tooltipUpdated:
            self.leftGaugeTimer = timerstuff.AutoTimer(1000, self._UpdateTooltipLeftGauge_thread, *updateArgs)

    def _UpdateTooltipLeftGauge_thread(self, label, gauge, ownerID):
        if not self._UpdateTooltip(label, gauge, ownerID):
            self.leftGaugeTimer = None

    def LoadRightGaugeTooltip(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        label = tooltipPanel.AddLabelMedium()
        updateArgs = (label, self.rightGauge, self.attackerID)
        tooltipUpdated = self._UpdateTooltip(*updateArgs)
        if tooltipUpdated:
            self.rightGaugeTimer = timerstuff.AutoTimer(1000, self._UpdateTooltipRightGauge_thread, *updateArgs)

    def _UpdateTooltipRightGauge_thread(self, label, gauge, ownerID):
        if not self._UpdateTooltip(label, gauge, ownerID):
            self.rightGaugeTimer = None

    def _UpdateTooltip(self, label, gauge, ownerID):
        if label.destroyed or gauge.destroyed:
            return False
        text = self._GetTooltipText(ownerID, gauge.value)
        label.SetText(text)
        return True

    def _GetTooltipText(self, ownerID, value):
        textList = []
        if ownerID:
            textList.append(cfg.eveowners.Get(ownerID).name)
        textList.append(localization.GetByLabel('UI/Common/Percentage', percentage=value * 100))
        return '<br>'.join(textList)

    def OnFwScoreboardUpdated(self, itemID, score):
        if itemID == self.itemID:
            self.SetValue(score)


def GetSlimItemForItemID(itemID):
    ballpark = sm.GetService('michelle').GetBallpark()
    if not ballpark:
        return
    return ballpark.GetInvItem(itemID)


def _GetRaceName(factionID):
    raceID = appConst.raceByFaction.get(factionID)
    if not raceID:
        return ''
    occupierRaceName = get_race_name(raceID)
    return occupierRaceName
