#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\fwWarzoneDashboard.py
import math
from carbonui.uicore import uicore
from collections import defaultdict
import blue
import signals
import uthread2
from carbon.common.script.util.format import FmtTimeInterval
from carbonui import Axis, TextAlign, TextColor, uiconst, ButtonVariant
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.line import Line
from carbonui.primitives.transform import Transform
from carbonui.services.setting import UserSettingBool, CharSettingBool
from carbonui.uianimations import animations
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from eve.client.script.ui.control.collapseLine import CollapseLine
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveCaptionLarge, EveLabelMedium
from eve.client.script.ui.control.toggleButtonGroupCircular import ToggleButtonGroupCircular
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupFactionalWarfare
from eve.client.script.ui.shared.factionalWarfare.util import OpenEnlistmentFlowIfUnseen
from eve.common.script.util.facwarCommon import GetOccupationEnemyFaction
from eveexceptions import ExceptionEater
from evegraphics.gateLogoConst import CALDARI_STATE, GALLENTE_FEDERATION, AMARR_EMPIRE, MINMATAR_REPUBLIC
from eveui import Sprite
from fwwarzone.client.dashboard.const import FACTION_ID_TO_COLOR, FACTION_ID_TO_POSTER, FACTION_ID_TO_ENLIST_PROMPT, FACTION_ID_TO_FLAT_ICON
from fwwarzone.client.dashboard.fwInformationTab import FWInformationTab
from fwwarzone.client.dashboard.gauges.warzoneStatusGauge import WarzoneStatusGauge
from fwwarzone.client.dashboard.nearestEnlistmentOfficeCard.nearestEnlistmentOfficeCard import NearestEnlistmentOfficeCard
from fwwarzone.client.dashboard.progression import FWProgressionPanel
from fwwarzone.client.dashboard.statistics import FWStatisticsPanel
from fwwarzone.client.dashboard.warzoneInfoSideCont import WarzoneInfoSideCont
from fwwarzone.client.dashboard.warzoneMapPanel import WarzoneMapPanel
from fwwarzone.client.dashboard.warzoneStats import FWWarzoneStatsPanel
from localization import GetByLabel

class FwWarzoneDashboard(Window):
    __guid__ = 'form.FwWarzoneDashboard'
    default_isStackable = False
    default_apply_content_padding = False
    default_width = 1631
    default_height = 879
    default_minSize = [1000, 879]
    default_iconNum = 'res:/ui/Texture/WindowIcons/factionalwarfare.png'
    default_captionLabelPath = 'Tooltips/StationServices/FactionalWarfare'
    default_descriptionLabelPath = 'Tooltips/StationServices/FactionalWarfare_description'
    default_windowID = 'fwWarzoneDashboard'
    default_openToTabID = 'WarzoneControl'
    __notifyevents__ = ['OnJoinMilitia',
     'OnRankChange',
     'OnSessionChanged',
     'OnUIScalingChange']

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.tabClass = attributes.tabClass
        self.warzoneMap = None
        self.gateLinks = None
        self.showFullWarzone = False
        self.collapseLine = None
        self.showLegendSetting = CharSettingBool('FWWindowShowMapLegend', True)
        self.fwSvc = sm.GetService('facwar')
        factionID = attributes.get('factionID', self.fwSvc.GetPreferredOccupierFactionID())
        self.displayAsFaction = self.fwSvc.EnforceOccupierFaction(factionID)
        self.openToTabID = attributes.get('openToTabID', FwWarzoneDashboard.default_openToTabID)
        self.interstellarShipCasterFactionFocus = signals.Signal(signalName='interstellarShipCasterFactionFocus')
        self.ConstructLayout()
        uthread2.StartTasklet(OpenEnlistmentFlowIfUnseen)

    def GetMenuMoreOptions(self):
        m = MenuData()
        m.AddCheckbox(GetByLabel('UI/FactionWarfare/frontlinesDashboard/showMapLegendSettingName'), setting=self.showLegendSetting)
        return m

    def SelectTab(self, tabID):
        self.tabgroup.SelectByID(tabID)

    def GetWarzoneID(self):
        warzoneID = sm.GetService('fwWarzoneSvc').GetWarzoneIdForFaction(self.displayAsFaction)
        return warzoneID

    def StarSelectedCallbackFunc(self, systemId):
        self.SelectSolarSystem(systemId)

    def SelectSolarSystem(self, systemId, forceExpanded = False):
        if not self.rightPanel.isShowing:
            self.rightPanel.LoadPanel()
        loaded = self.rightPanel.SelectSystem(systemId, None, forceExpanded=forceExpanded)
        if loaded:
            self.collapseLine.SetExpanded()
        else:
            self.collapseLine.SetCollapsed()

    def ConstructLeftPanel(self):
        self.leftPanel.Flush()
        uthread2.StartTasklet(self.AsyncConstructLeftPanel)

    def AsyncConstructLeftPanel(self):
        topCont = Container(name='topCont', parent=self.leftPanel, align=uiconst.TOTOP, height=387)
        factionDescriptionCont = Container(name='factionDescriptionCont', parent=self.leftPanel, align=uiconst.TOTOP, height=80, padTop=15)
        Sprite(name='propaganda', align=uiconst.CENTERTOP, parent=topCont, texturePath=FACTION_ID_TO_POSTER[self.displayAsFaction], pos=(0, 0, 349, 352))
        gaugeCont = Container(name='gaugeCont', height=123, parent=topCont, align=uiconst.TOBOTTOM_NOPUSH, idx=0)
        warzoneStatusGauge = WarzoneStatusGauge(parent=gaugeCont, radius=61, lineWidth=6, align=uiconst.CENTER, warzoneId=self.GetWarzoneID(), animateIn=True, viewingFactionId=self.displayAsFaction)
        opposingFactionID = GetOccupationEnemyFaction(self.displayAsFaction)
        leftLabel = EveCaptionLarge(parent=gaugeCont, align=uiconst.CENTERLEFT, text=u'{}'.format(warzoneStatusGauge.opposingSystemCount), left=65, color=FACTION_ID_TO_COLOR[opposingFactionID], opacity=0.0, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.5, state=uiconst.UI_NORMAL)
        leftLabel.hint = GetByLabel('UI/FactionWarfare/frontlinesDashboard/nSystemsOccupiedBy', systems=warzoneStatusGauge.opposingSystemCount, factionName=cfg.eveowners.Get(opposingFactionID).name)
        rightLabel = EveCaptionLarge(parent=gaugeCont, align=uiconst.CENTERRIGHT, left=65, text=u'{}'.format(warzoneStatusGauge.friendlySystemCount), color=FACTION_ID_TO_COLOR[self.displayAsFaction], opacity=0.0, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.5, state=uiconst.UI_NORMAL)
        rightLabel.hint = GetByLabel('UI/FactionWarfare/frontlinesDashboard/nSystemsOccupiedBy', systems=warzoneStatusGauge.friendlySystemCount, factionName=cfg.eveowners.Get(self.displayAsFaction).name)
        animations.FadeIn(leftLabel, duration=0.5)
        animations.FadeIn(rightLabel, duration=0.5)
        notEnlisted = not session.warfactionid or session.warfactionid != self.displayAsFaction
        text = ''
        if notEnlisted:
            text = FACTION_ID_TO_ENLIST_PROMPT[self.displayAsFaction]
        else:
            text = cfg.eveowners.Get(session.warfactionid).name
        EveCaptionLarge(parent=Container(parent=factionDescriptionCont, align=uiconst.TOTOP, height=30), align=uiconst.CENTER, text=text, bold=True)
        textWithIconsCont = Container(name='textWithIconsCont', parent=factionDescriptionCont, align=uiconst.TOTOP, height=30, padTop=20)
        innerGrowCont = ContainerAutoSize(name='innerGrowCont', parent=textWithIconsCont, align=uiconst.CENTER, height=30, alignMode=uiconst.TOLEFT)
        EveLabelLarge(parent=innerGrowCont, align=uiconst.TOLEFT, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/atWarWith'))
        thisFaction = self.displayAsFaction
        enemyFactionA = GetOccupationEnemyFaction(thisFaction)
        iconPos = (5, -5, 32, 32)
        Sprite(parent=Transform(parent=innerGrowCont, align=uiconst.TOLEFT, width=32, height=32), pos=iconPos, color=FACTION_ID_TO_COLOR[enemyFactionA], texturePath=FACTION_ID_TO_FLAT_ICON[enemyFactionA], state=uiconst.UI_NORMAL, hint=cfg.eveowners.Get(enemyFactionA).name)
        if notEnlisted:
            self.ConstructEnlistCTA()
        else:
            self.ConstructSignedUpInfoCont()

    def ConstructSignedUpInfoCont(self):
        infoCont = ContainerAutoSize(name='infoCont', align=uiconst.TOTOP, padding=(40, 20, 40, 0), parent=self.leftPanel)
        leftLabels = []
        rightLabels = []
        factionRowCont = ContainerAutoSize(name='factionRowCont', parent=infoCont, align=uiconst.TOTOP, alignMode=uiconst.TOPRIGHT)
        factionLabelCls = EveLabelLarge
        factionLabel = factionLabelCls(parent=factionRowCont, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/FactionTitleLabel'), align=uiconst.TOLEFT)
        leftLabels.append(factionLabel)
        factionNameTextWidth, _ = factionLabelCls.MeasureTextSize(cfg.eveowners.Get(session.warfactionid).name)
        factionSpriteCont = Transform(parent=factionRowCont, align=uiconst.TOPRIGHT, left=factionNameTextWidth, width=32, height=32)
        Sprite(parent=factionSpriteCont, width=32, height=32, top=-6, color=FACTION_ID_TO_COLOR[session.warfactionid], texturePath=FACTION_ID_TO_FLAT_ICON[session.warfactionid])
        factionLabelCls(parent=factionRowCont, text=cfg.eveowners.Get(session.warfactionid).name, align=uiconst.TOPRIGHT, padLeft=5)
        lLabel, rLabel = self.GetRowLabels('title', infoCont, GetByLabel('UI/FactionWarfare/frontlinesDashboard/MilitiaTitleLabel'), cfg.eveowners.Get(sm.GetService('facwar').GetFactionMilitiaCorporation(self.displayAsFaction)).name)
        leftLabels.append(lLabel)
        rightLabels.append(rLabel)
        rankName, rankDescription = self._GetCurrentRank()
        lLabel, rLabel = self.GetRowLabels('rank', infoCont, GetByLabel('UI/FactionWarfare/frontlinesDashboard/RankTitleLabel'), rankName)
        leftLabels.append(lLabel)
        rightLabels.append(rLabel)
        if not sm.GetService('facwar').GetCorpFactionalWarStatus():
            lLabel, rLabel = self.GetRowLabels('time', infoCont, GetByLabel('UI/FactionWarfare/frontlinesDashboard/timeServed'), self._GetTimeServed())
            leftLabels.append(lLabel)
            rightLabels.append(rLabel)
        maxWidth = max((x.width for x in leftLabels))
        labelLeft = max(100, maxWidth + 15)
        for eachLabel in rightLabels:
            eachLabel.padLeft = labelLeft

        factionalWarStatus = sm.GetService('facwar').GetCorpFactionalWarStatus()
        buttons = ButtonGroup(parent=self.leftPanel, align=uiconst.TOTOP, orientation=Axis.VERTICAL, button_size_mode=ButtonSizeMode.STRETCH)
        Button(parent=buttons, align=uiconst.TOTOP, label=GetByLabel('UI/FactionWarfare/Retire'), padLeft=39, padRight=55, top=45, func=self._OpenEnlistmentWnd)

    def GetRowLabels(self, configName, parent, leftText, rightText):
        rowCont = ContainerAutoSize(name='%sRowCont' % configName, parent=parent, align=uiconst.TOTOP, alignMode=uiconst.TOPRIGHT, padTop=5)
        leftLabel = EveLabelLarge(name='%sLeftLabel' % configName, parent=rowCont, text=leftText, textAlign=TextAlign.LEFT, align=uiconst.TOPLEFT)
        rightLabel = EveLabelLarge(name='%sRightLabel' % configName, parent=rowCont, text=rightText, textAlign=TextAlign.LEFT, align=uiconst.TOPRIGHT, padLeft=100)
        return (leftLabel, rightLabel)

    def ConstructNearestFWStationContainer(self, enlistmentContainer):
        jumpsToNearestStation, nearestStationID = self.fwSvc.GetNearestFactionWarfareStationData(preferredFaction=self.displayAsFaction)
        if not nearestStationID:
            return
        uiService = sm.GetService('ui')
        stationInfo = uiService.GetStationStaticInfo(nearestStationID)
        stationTypeID = stationInfo.stationTypeID
        solarSystemID = stationInfo.solarSystemID
        stationName = uiService.GetStationName(nearestStationID)
        EveLabelMedium(parent=enlistmentContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/FactionWarfare/nearestMilitiaOffice'), color=TextColor.SECONDARY)
        NearestEnlistmentOfficeCard(uiService=uiService, stationInfo=stationInfo, stationTypeID=stationTypeID, solarSystemID=solarSystemID, stationName=stationName, jumpsToNearestStation=jumpsToNearestStation, nearestStationID=nearestStationID, parent=enlistmentContainer, align=uiconst.TOTOP, height=85, padTop=10)

    def ConstructNearestEnlistmentOfficeContainer(self, callToActionCont):
        if not session.warfactionid:
            self.ConstructNearestFWStationContainer(callToActionCont)

    def ConstructEnlistCTA(self):
        callToActionCont = ContainerAutoSize(align=uiconst.TOTOP, padTop=20, parent=self.leftPanel)
        EveLabelLarge(parent=callToActionCont, align=uiconst.TOTOP, padLeft=39, padRight=39, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/FWExplainer'))
        EveLabelLarge(parent=callToActionCont, align=uiconst.TOTOP, padTop=15, padLeft=39, padRight=39, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/FWConcordNote'))
        enlistCont = ContainerAutoSize(align=uiconst.TOTOP, parent=callToActionCont, alignMode=uiconst.TOTOP, padLeft=39, padRight=39, padTop=25)
        buttons = ButtonGroup(parent=enlistCont, align=uiconst.TOTOP, orientation=Axis.VERTICAL, button_size_mode=ButtonSizeMode.STRETCH)
        Button(parent=buttons, align=uiconst.TOTOP, label=GetByLabel('UI/PirateInsurgencies/openFactionSelection'), variant=ButtonVariant.PRIMARY, func=self._OpenEnlistmentWnd)
        Button(parent=buttons, align=uiconst.TOTOP, label=GetByLabel('UI/PirateInsurgencies/learnMore'), func=self._OpenFWAgencySection)

    def _OpenEnlistmentWnd(self, *args):
        uicore.cmd.OpenFwEnlistment()

    def _OpenFWAgencySection(self, *args):
        sm.GetService('agencyNew').OpenWindow(contentGroupID=contentGroupFactionalWarfare)

    def LoadCharBtnTooltip(self, tooltipPanel, *args):
        tooltipPanel.state = uiconst.UI_NORMAL
        factionName = cfg.eveowners.Get(self.displayAsFaction).name
        linkUrl = '<a href=localsvc:method=ShowCorpDetails>'
        characterHint = GetByLabel('UI/FactionWarfare/CorpRestrictionsPreventDirectEnrollment', factionName=factionName, urlStart=linkUrl, urlEnd='</a>')
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=characterHint, wrapWidth=200, state=uiconst.UI_NORMAL)

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader()

    def ConstructCenterPanel(self):
        self.tabgroup = self.header.tab_group
        GradientSprite(parent=self.centerPanel, align=uiconst.TOBOTTOM_NOPUSH, idx=0, height=117, rgbData=[(0.0, (0.0, 0.0, 0.0))], alphaData=[(0.0, 0.0), (0.75, 0.75), (1.0, 1.0)], state=uiconst.UI_DISABLED, rotation=-math.pi / 2, padRight=20)
        bottomRowTabGroupsCont = ContainerAutoSize(name='bottomRowTabGroupsCont', parent=self.centerPanel, idx=0, height=48, top=30, align=uiconst.CENTERBOTTOM, alignMode=uiconst.TOLEFT)
        empireSelectionButtons = ToggleButtonGroupCircular(name='myToggleBtnGroup', parent=bottomRowTabGroupsCont, align=uiconst.TOLEFT, callback=self.OnFactionToggleButtonClicked)
        Line(parent=bottomRowTabGroupsCont, align=uiconst.TOLEFT, opacity=0.6, weight=1, padding=(12, 16, 12, 16))
        self.insurgencyWindowButtonGroup = ToggleButtonGroupCircular(name='insurgencyWindowButtonGroup', parent=bottomRowTabGroupsCont, align=uiconst.TOLEFT, callback=self.OnInsurgencyToggleButtonClicked)
        self.insurgencyWindowButtonGroup.AddButton(0, iconPath='res:/UI/Texture/classes/pirateinsurgencies/pirates_icon.png')
        factionOptions = [(CALDARI_STATE, FACTION_ID_TO_FLAT_ICON[CALDARI_STATE]),
         (GALLENTE_FEDERATION, FACTION_ID_TO_FLAT_ICON[GALLENTE_FEDERATION]),
         (AMARR_EMPIRE, FACTION_ID_TO_FLAT_ICON[AMARR_EMPIRE]),
         (MINMATAR_REPUBLIC, FACTION_ID_TO_FLAT_ICON[MINMATAR_REPUBLIC])]
        for factionInfo in factionOptions:
            factionID, iconPath = factionInfo
            empireSelectionButtons.AddButton(factionID, iconPath=iconPath)

        empireSelectionButtons.SetSelected(self.displayAsFaction)
        self.collapseLine = CollapseLine(parent=self.centerPanel, collapsingSection=self.rightPanel, useCustomTransition=True, settingKey='FWWarzoneDashboardShowSidePanel')
        self.collapseLine.on_section_expand.connect(self.ExpandSideBar)
        self.collapseLine.on_section_collapse.connect(self.CollapseSideBar)
        if self.collapseLine.isCollapsed:
            self.collapseLine.SetCollapsed(animate=False)
        else:
            self.rightPanel.LoadPanel()
        self.warzoneMap = WarzoneMapPanel(parent=self.centerPanel, warzoneId=self.GetWarzoneID(), showFullWarzone=self.showFullWarzone, starSelectedCallback=self.StarSelectedCallbackFunc, interstellarShipCasterFactionFocusSignal=self.interstellarShipCasterFactionFocus, displayAsFactionID=self.displayAsFaction, showLegendSetting=self.showLegendSetting)
        self.warzoneMap.bgFill.padRight = -self.collapseLine.width / 2
        self.warzoneStatsPanel = FWWarzoneStatsPanel(factionID=self.displayAsFaction, warzoneID=self.GetWarzoneID(), align=uiconst.TOALL, parent=self.centerPanel)
        self.fwInformationTab = FWInformationTab(align=uiconst.TOALL, parent=self.centerPanel)
        self.tabgroup.Flush()
        self.tabgroup.AddTab(label=GetByLabel('UI/FactionWarfare/WarzoneControl'), panel=self.warzoneMap, tabID='WarzoneControl')
        self.tabgroup.AddTab(label=GetByLabel('UI/FactionWarfare/WarzoneDetails'), panel=self.warzoneStatsPanel, tabID='WarzoneStats')
        self.tabgroup.AddTab(label=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/objectives'), panel=self.fwInformationTab, tabID='Objectives')
        if session.warfactionid is not None and session.warfactionid == self.displayAsFaction:
            self.statisticsPanel = FWStatisticsPanel(name='statisticsPanel', parent=self.centerPanel, align=uiconst.TOALL)
            self.progressionPanel = FWProgressionPanel(name='progressionPanel', parent=self.centerPanel, align=uiconst.TOALL, factionId=self.displayAsFaction)
            self.tabgroup.AddTab(label=GetByLabel('UI/FactionWarfare/Statistics'), panel=self.statisticsPanel, tabID='Statistics')
            self.tabgroup.AddTab(label=GetByLabel('UI/FactionWarfare/frontlinesDashboard/Progression'), panel=self.progressionPanel, tabID='Progression')
        self.tabgroup.SelectByID(self.openToTabID)

    def ConstructLayout(self):
        self.main = Container(parent=self.sr.main, align=uiconst.TOALL, clipChildren=True, padding=0)
        self.leftPanel = Container(name='leftPanel', parent=self.main, align=uiconst.TOLEFT, width=350)
        self.ConstructLeftPanel()
        self.rightPanel = WarzoneInfoSideCont(parent=self.main, viewingFactionId=self.displayAsFaction, interstellarShipCasterFactionFocusSignal=self.interstellarShipCasterFactionFocus)
        self.rightPanel.LoadPanel(fadeIn=False)
        self.centerPanel = Container(name='centerPanel', parent=self.main, align=uiconst.TOALL)
        self.ConstructCenterPanel()

    def DEBUG_SelectWrazoneCallback(self, value):
        self.centerPanel.Flush()
        self.ConstructLeftPanel()
        self.centerPanel.Flush()
        self.ConstructCenterPanel()

    def _GetCurrentRank(self):
        currentRank = 1
        currRank = sm.GetService('facwar').GetCharacterRankInfo(session.charid)
        if currRank:
            currentRank = currRank.currentRank
        rankName, rankDescription = sm.GetService('facwar').GetRankLabel(session.warfactionid, currentRank)
        return (rankName, rankDescription)

    def _GetTimeServed(self):
        factionalWarStatus = sm.GetService('facwar').GetCorpFactionalWarStatus()
        try:
            timeInFW = blue.os.GetWallclockTime() - max(factionalWarStatus.startDate, sm.RemoteSvc('corporationSvc').GetEmploymentRecord(session.charid)[0].startDate)
            return FmtTimeInterval(timeInFW, 'day')
        except:
            return GetByLabel('UI/Generic/Unknown')

    def OnJoinMilitia(self, *args):
        if self and not self.destroyed:
            self.sr.main.Flush()
            self.ConstructLayout()

    def OnRankChange(self, oldrank, newrank):
        if not self.destroyed:
            self.ConstructLeftPanel()

    def OnSessionChanged(self, isRemote, sess, change):
        if not self.destroyed:
            self.sr.main.Flush()
            self.ConstructLayout()
        if 'solarsystemid2' in change:
            self.warzoneMap.UpdateCurrentLocation()

    def OnUIScalingChange(self, change, *args):
        if self.warzoneMap:
            self.warzoneMap.ReloadMap()

    def ExpandSideBar(self, animate = True):
        self.rightPanel.FadeIn(animate=animate)

    def CollapseSideBar(self, animate = True):
        self.rightPanel.FadeOut(animate=animate)

    def OnFactionToggleButtonClicked(self, newFactionID, _oldFactionID):
        if newFactionID is None:
            return
        self.SetFaction(newFactionID)

    def OnInsurgencyToggleButtonClicked(self, newID, _OldID):
        if newID is None:
            return
        sm.GetService('cmd').OpenInsurgencyDashboard()
        self.insurgencyWindowButtonGroup.DeselectAll()

    def _SetFaction(self, _Combo, _key, value):
        self.SetFaction(value)

    def SetFaction(self, factionID):
        if self.displayAsFaction == factionID:
            return
        self.displayAsFaction = factionID
        self.sr.main.Flush()
        self.ConstructLayout()

    def Close(self, setClosed = False, *args, **kwds):
        with ExceptionEater('Closing FwWarzoneDashboard'):
            if self.collapseLine:
                self.collapseLine.on_section_collapse.clear()
                self.collapseLine.on_section_expand.clear()
        super(FwWarzoneDashboard, self).Close(setClosed, args, kwds)
