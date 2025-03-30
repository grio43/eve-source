#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\ui\shipcaster\launcherCont.py
from carbonui import TextAlign, TextColor
from carbonui.control.button import Button
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from dynamicresources.client.ess.bracket.label import Header, MediumInSpaceLabel
from eve.client.script.ui import eveColor
from factionwarfare.client.text import GetSystemCaptureStatusText
from fwwarzone.client.dashboard.const import ADJACENCY_STATE_TO_ICON_PATH_SMALL
from fwwarzone.client.dashboard.fwWarzoneDashboard import FwWarzoneDashboard
from localization import GetByLabel
from menucheckers import CelestialChecker, SessionChecker
from shipcaster.shipcasterUtil import GetFailureTextAndDisabledOption
from spacecomponents.client.ui.shipcaster.launcherContController import LauncherContController
from carbon.common.script.util.format import FmtAmt
from carbon.common.script.util.timerstuff import AutoTimer
from eve.client.script.ui.control.eveLabel import Label, EveLabelMedium
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.eveColor import TUNGSTEN_GREY
from eve.client.script.ui.skillPlan.skillPlanConst import ICON_BY_FACTION_ID

class LauncerCont(Container):
    default_name = 'launcerCont'
    __notifyevents__ = ['OnShipcasterTargetStateChanged']

    def ApplyAttributes(self, attributes):
        super(LauncerCont, self).ApplyAttributes(attributes)
        self.itemID = attributes.itemID
        self.typeID = attributes.typeID
        self.launcherContController = LauncherContController(self.itemID, self.typeID)
        self.ConstructUI()
        sm.RegisterNotify(self)

    def ConstructUI(self):
        self._button = Button(parent=self, align=uiconst.CENTERBOTTOM, label=GetByLabel('UI/FactionWarfare/ShipcasterInitiateLaunch'), func=self.Jump)
        sideOffset = max(self._button.width * 1.3, 180)
        self._ConstructLeftCont(sideOffset)
        self._ConstructRightCont(sideOffset)
        self._ConstructCenterSpriteCont()
        self._ConstructTopCont()
        self._UpdateItemIDAndUI()
        self.infoCont.UpdateInfoCont()
        maxTargets = self.launcherContController.GetMaxTargets()
        if maxTargets < 3:
            self.leftCont.Hide()
        if maxTargets < 2:
            self.rightCont.Hide()

    def _ConstructLeftCont(self, sideOffset):
        self.leftCont = SideCont(name='leftCont', parent=self, pos=(-sideOffset,
         0,
         200,
         50), align=uiconst.CENTERBOTTOM, isRightSide=False)

    def _ConstructRightCont(self, sideOffset):
        self.rightCont = SideCont(name='rightCont', parent=self, pos=(sideOffset,
         0,
         200,
         50), align=uiconst.CENTERBOTTOM, isRightCont=True)

    def _ConstructCenterSpriteCont(self):
        self.centerSpriteCont = Container(name='centerSpriteCont', parent=self, pos=(0, 13, 204, 66), align=uiconst.CENTERBOTTOM)
        Sprite(parent=self.centerSpriteCont, pos=(0, 0, 204, 66), align=uiconst.BOTTOMLEFT, texturePath='res:/UI/Texture/classes/ShipCaster/shipcasterCenter.png', color=TUNGSTEN_GREY, state=uiconst.UI_DISABLED)
        Sprite(parent=self.centerSpriteCont, pos=(0, 0, 26, 26), align=uiconst.CENTERTOP, texturePath='res:/UI/Texture/classes/ShipCaster/shipcasterCenterIcon.png', state=uiconst.UI_DISABLED)

    def _ConstructTopCont(self):
        self.topCont = Container(name='topCont', parent=self, align=uiconst.TOBOTTOM, top=90, height=70)
        self.infoCont = TargetInfoCont(parent=self.topCont, align=uiconst.TOBOTTOM, launcherContController=self.launcherContController)
        self.fwCont, fwInnerCont = self.GetLabelConts(self.topCont, 'topHeaderCont', top=10)
        fwInnerCont.state = uiconst.UI_NORMAL
        MoreInfoIcon(name='moreInfoIcon', parent=fwInnerCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        MediumInSpaceLabel(parent=fwInnerCont, text=GetByLabel('UI/FactionWarfare/OpenSystemInFwWindow'), align=uiconst.CENTERLEFT, left=20)
        fwInnerCont.OnClick = self.OpenFwWndForSystem
        _, topHeaderInnerCont = self.GetLabelConts(self.topCont, 'topHeaderCont')
        self.topHeaderAdjacencySprite = Sprite(parent=topHeaderInnerCont, pos=(0, 0, 20, 20), align=uiconst.CENTERLEFT)
        self.topHeader = Header(parent=topHeaderInnerCont, text='', align=uiconst.CENTERLEFT, left=26)
        _, topLabelInnerCont = self.GetLabelConts(self.topCont, 'topLabelStatusCont')
        self.topLabelStatus = MediumInSpaceLabel(parent=topLabelInnerCont, align=uiconst.CENTERLEFT)

    def GetLabelConts(self, parent, prefsName, top = 0):
        topLabelStatusCont = ContainerAutoSize(name=prefsName, parent=parent, align=uiconst.TOBOTTOM, top=top)
        topLabelInnerCont = ContainerAutoSize(name='%sInner' % prefsName, parent=topLabelStatusCont, align=uiconst.CENTER)
        return (topLabelStatusCont, topLabelInnerCont)

    def Jump(self, *args):
        sm.GetService('menu').JumpThroughShipcaster(self.itemID)

    def OpenFwWndForSystem(self, *args):
        targetSystem, factionID = self.launcherContController.GetTargetAndFactionForDashboard()
        wnd = FwWarzoneDashboard.GetIfOpen()
        if wnd and not wnd.destroyed:
            wnd.Maximize()
            wnd.SetFaction(factionID)
        else:
            wnd = FwWarzoneDashboard.Open(factionID=factionID)
        wnd.SelectSolarSystem(targetSystem, forceExpanded=True)

    def OnShipcasterTargetStateChanged(self, itemID):
        if itemID != self.itemID:
            return
        self._UpdateItemIDAndUI()

    def _UpdateItemIDAndUI(self):
        self.infoCont.UpdateInfoCont()
        self.UpdateUI()
        self.updateTimer = AutoTimer(500, self.UpdateUI)

    def UpdateUI(self):
        if self.destroyed:
            self.updateTimer = None
            return
        self._UpdateButton()
        self._UpdateLeftCont()
        self._UpdateRightCont()
        self._UpdateTopCont()

    def _UpdateButton(self):
        celestialChecker = CelestialChecker((self.itemID, self.typeID), cfg, SessionChecker(session, sm))
        self._button.Disable()
        if celestialChecker.OfferShipcasterJump():
            self._button.Enable()
            self._button.hint = None
        elif celestialChecker.failure_label:
            failureText, _ = GetFailureTextAndDisabledOption(self.itemID, celestialChecker)
            self._button.hint = failureText

    def _UpdateLeftCont(self):
        headerText, timeText, adjacencyState, headerColor, _, _ = self.launcherContController._GetHeaderStatusAndAdjacenyState(2)
        self.leftCont.UpdateSideCont(headerText, timeText, adjacencyState, headerColor)

    def _UpdateRightCont(self):
        headerText, timeText, adjacencyState, headerColor, _, _ = self.launcherContController._GetHeaderStatusAndAdjacenyState(1)
        self.rightCont.UpdateSideCont(headerText, timeText, adjacencyState, headerColor)

    def _UpdateTopCont(self):
        headerText, timeText, adjacencyState, headerColor, timeColor, timeGlow = self.launcherContController._GetHeaderStatusAndAdjacenyState(0)
        self.topHeader.text = headerText
        topLabelStatusLabel = self.topLabelStatus.mainLabel
        topLabelStatusLabel.SetText(timeText)
        topLabelStatusLabel.SetTextColor(timeColor)
        if timeGlow:
            topLabelStatusLabel.outputMode = uiconst.OUTPUT_COLOR_AND_GLOW
        else:
            topLabelStatusLabel.outputMode = uiconst.OUTPUT_COLOR
        nextTarget = self.launcherContController.GetNextTargetSystemID()
        if nextTarget:
            self.fwCont.Show()
        else:
            self.fwCont.Hide()
        if adjacencyState:
            self.topHeaderAdjacencySprite.Show()
            texturePath = ADJACENCY_STATE_TO_ICON_PATH_SMALL.get(adjacencyState, None)
            self.topHeaderAdjacencySprite.SetTexturePath(texturePath)
            self.topHeader.left = 26
        else:
            self.topHeaderAdjacencySprite.Hide()
            self.topHeader.left = 0


class SideCont(Container):

    def ApplyAttributes(self, attributes):
        super(SideCont, self).ApplyAttributes(attributes)
        self.isRightCont = attributes.isRightCont
        self.innerCont = Container(name='innerCont', parent=self, align=uiconst.TOLEFT if self.isRightCont else uiconst.TORIGHT, width=100, left=65, top=6)
        topCont = Container(parent=self.innerCont, align=uiconst.TOTOP_PROP, height=0.5)
        bottomCont = Container(parent=self.innerCont, align=uiconst.TOBOTTOM_PROP, height=0.5)
        topTextCont = ContainerAutoSize(parent=topCont, align=uiconst.BOTTOMLEFT if self.isRightCont else uiconst.BOTTOMRIGHT, alignMode=uiconst.CENTERLEFT, top=2)
        self.adjacencySprite = Sprite(parent=topTextCont, pos=(0, 0, 16, 16), align=uiconst.CENTERLEFT)
        self.labelHeader = Label(parent=topTextCont, text='', align=uiconst.CENTERLEFT, left=16)
        self.labelStatus = Label(parent=bottomCont, text='', align=uiconst.TOPLEFT if self.isRightCont else uiconst.TOPRIGHT, top=4)
        spriteAlign = uiconst.CENTERLEFT if self.isRightCont else uiconst.CENTERRIGHT
        texturePath = 'res:/UI/Texture/classes/ShipCaster/shipcasterRightSide.png' if self.isRightCont else 'res:/UI/Texture/classes/ShipCaster/shipcasterLeftSide.png'
        Sprite(parent=self, pos=(0, 4, 147, 24), align=spriteAlign, texturePath=texturePath, color=TUNGSTEN_GREY, state=uiconst.UI_DISABLED)

    def UpdateSideCont(self, headerText, statusText, adjacencyState, headerColor):
        self.labelHeader.SetText(headerText)
        self.labelHeader.SetTextColor(headerColor)
        self.labelStatus.SetText(statusText)
        if adjacencyState:
            self.adjacencySprite.Show()
            texturePath = ADJACENCY_STATE_TO_ICON_PATH_SMALL.get(adjacencyState, None)
            self.adjacencySprite.SetTexturePath(texturePath)
            self.labelHeader.left = 20
        else:
            self.adjacencySprite.Hide()
            self.labelHeader.left = 0
        self.innerCont.width = self.labelHeader.textwidth + self.labelHeader.left


class TargetInfoCont(ContainerAutoSize):
    default_name = 'targetInfoCont'

    def ApplyAttributes(self, attributes):
        super(TargetInfoCont, self).ApplyAttributes(attributes)
        self.launcherContController = attributes.launcherContController
        self.layoutGrid = LayoutGrid(parent=self, columns=5, margin=6, cellSpacing=(4, 0), align=uiconst.CENTER, bgColor=(0, 0, 0, 0.5))
        self.occupierSprite = Sprite(parent=self.layoutGrid, pos=(0, 0, 16, 16), align=uiconst.CENTER, color=eveColor.SILVER_GREY, state=uiconst.UI_DISABLED)
        self.occupierLabel = EveLabelMedium(text='', parent=self.layoutGrid, color=TextColor.SECONDARY)
        spacer = Container(name='spacer', parent=self.layoutGrid, pos=(0, 0, 12, 12), align=uiconst.TOPLEFT)
        self.advantageSprite = Sprite(parent=self.layoutGrid, pos=(0, 0, 16, 16), align=uiconst.CENTER, color=eveColor.SILVER_GREY, state=uiconst.UI_DISABLED)
        self.advantageLabel = EveLabelMedium(text='', parent=self.layoutGrid, color=TextColor.SECONDARY)
        self.layoutGrid.FillRow()
        self.constestedGauge = GaugeCircular(parent=self.layoutGrid, clockwise=False, showMarker=False, radius=6, lineWidth=2.0, align=uiconst.CENTER, value=0.75, colorStart=eveColor.SILVER_GREY, colorEnd=eveColor.SILVER_GREY, state=uiconst.UI_DISABLED)
        self.contestedLabel = EveLabelMedium(text='', parent=self.layoutGrid, color=TextColor.SECONDARY)
        spacer = Container(name='spacer', parent=self.layoutGrid, pos=(0, 0, 12, 12), align=uiconst.TOPLEFT)
        self.deathSprite = Sprite(parent=self.layoutGrid, pos=(0, 0, 16, 16), align=uiconst.CENTER, color=eveColor.SILVER_GREY, texturePath='res:/UI/Texture/classes/ShipCaster/deathsOnGrid.png', state=uiconst.UI_DISABLED)
        self.deathLabel = EveLabelMedium(text='', parent=self.layoutGrid, color=TextColor.SECONDARY)

    def UpdateInfoCont(self):
        nextTarget = self.launcherContController.GetNextTargetSystemID()
        if not nextTarget:
            self.Hide()
            return
        self.Show()
        occupierID, attackerID, advantageScore, advantageWinner = self.launcherContController.GetTargetOccuppierAndNetScore()
        if occupierID is None or attackerID is None:
            self.layoutGrid.Hide()
            return
        self.layoutGrid.Show()
        self.occupierSprite.SetTexturePath(ICON_BY_FACTION_ID.get(occupierID, None))
        occupierText = cfg.eveowners.Get(occupierID).name if occupierID else ''
        self.occupierLabel.SetText(occupierText)
        self.advantageSprite.SetTexturePath(ICON_BY_FACTION_ID.get(advantageWinner, None))
        percentageText = GetByLabel('UI/FactionWarfare/ShipcasterFwAdvantage', percentage=FmtAmt(abs(advantageScore) * 100, showFraction=True))
        self.advantageLabel.SetText(percentageText)
        victoryPointState = self.launcherContController.GetContestedInfo()
        systemStatusText = GetSystemCaptureStatusText(victoryPointState)
        self.contestedLabel.SetText(systemStatusText)
        if victoryPointState is None:
            self.constestedGauge.SetValue(0)
        else:
            self.constestedGauge.SetValue(1 - victoryPointState.contestedFraction, animate=False)
        numKills = self.launcherContController.GetKillsInTheLastHour(nextTarget)
        text = GetByLabel('UI/FactionWarfare/KillsInHour', numKills=numKills)
        self.deathLabel.SetText(text)
