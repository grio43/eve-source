#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pirateinsurgency\client\dashboard\dashboard.py
import math
import appConst
import carbonui
import uthread2
from carbonui import uiconst, ButtonFrameType, TextColor, ButtonVariant
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from characterdata.factions import get_faction_name
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.toggleButtonGroupCircular import ToggleButtonGroupCircular
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupPirateIncursionsGuide
from eve.client.script.ui.shared.factionalWarfare.util import OpenEnlistmentFlowIfUnseen
from eve.common.script.util.facwarCommon import GetInsurgencyEnemyFactions
from fwwarzone.client.dashboard.collapsingSection import CollapsingSection
from localization import GetByLabel
from pirateinsurgency.client.dashboard.const import WARZONE_ID_TO_PIRATE_FACTION_ID, GetFactionColor, GetFactionBadgeSmall, GetFactionBadge, GetPirateFactionDisplayOrder, GetPirateFactionIDFromWarzoneID, GetBannerPathFromFactionID
from pirateinsurgency.client.dashboard.map import MapPanel
from pirateinsurgency.client.dashboard.sidepanels.activities import Activities
from pirateinsurgency.client.dashboard.sidepanels.progress import Progress
from pirateinsurgency.client.dashboard.sidepanels.systeminfo import SystemInfo
FRAME_PATH = 'res:/UI/Texture/classes/shipTree/infoPanel/selected.png'

class InsurgentsDashboard(Window):
    __guid__ = 'form.InsurgenceDashboard'
    default_isStackable = False
    default_apply_content_padding = False
    default_clipChildren = True
    default_width = 1631
    default_height = 879
    default_minSize = [1000, 853]
    default_iconNum = 'res:/ui/Texture/WindowIcons/insurgencies.png'
    default_captionLabelPath = 'UI/PirateInsurgencies/dashboardCaption'
    default_descriptionLabelPath = 'UI/PirateInsurgencies/Insurgency_description'
    default_windowID = 'InsurgentsDashboard'
    __notifyevents__ = ['OnJoinMilitia',
     'OnInsurgencyCampaignStartedForLocation_Local',
     'OnInsurgencyCampaignUpdatedForLocation_Local',
     'OnInsurgencyCampaignEndingForLocation_Local']

    def ApplyAttributes(self, attributes):
        super(InsurgentsDashboard, self).ApplyAttributes(attributes)
        self.systemInfo = None
        self.progress = None
        self.insurgencyActivities = None
        self.dashboardSvc = sm.GetService('insurgencyDashboardSvc')
        self.loadingWheel = LoadingWheel(parent=self.sr.main, align=uiconst.CENTER)
        uthread2.StartTasklet(self._AsyncConstructLayout)

    def _AsyncConstructLayout(self):
        if self.dashboardSvc.GetCurrentCampaignSnapshots() == []:
            self.loadingWheel.Hide()
            carbonui.TextHeadline(parent=Container(parent=self.sr.main, align=uiconst.TOALL), align=uiconst.CENTER, text=GetByLabel('UI/PirateInsurgencies/noActiveInsurgency'))
            return
        self.ConstructLayout()
        self.loadingWheel.Hide()
        self.dashboardSvc.SIGNAL_solarSystemSelectedFromMap.connect(self._OnSolarSystemSelectedFromMapCallback)
        OpenEnlistmentFlowIfUnseen()

    def Close(self, *args, **kwargs):
        super(InsurgentsDashboard, self).Close(*args, **kwargs)
        self.dashboardSvc.SIGNAL_solarSystemSelectedFromMap.disconnect(self._OnSolarSystemSelectedFromMapCallback)

    def OnTabButtonSelectCampaign(self, campaignID, _oldCampaignID):
        snapshot = self.dashboardSvc.GetCurrentCampaignSnapshotByID(campaignID)
        self.mapPanel.SetActiveItemID(snapshot.originSolarsystemID)
        self.systemInfo.OnSystemSelected(snapshot.originSolarsystemID)
        self.progress.OnInsurgencySelected(snapshot)

    def _OnSolarSystemSelectedFromMapCallback(self, systemID):
        self.systemInfo.OnSystemSelected(systemID)
        snapshot = None
        for snapshot in self.dashboardSvc.GetCurrentCampaignSnapshots():
            if systemID in snapshot.coveredSolarsystemIDs:
                snapshot = snapshot
                break

        if snapshot is not None:
            self.progress.OnInsurgencySelected(snapshot)
            self.selectorButtons.SetSelectedByID(snapshot.campaignID)

    def ConstructLayout(self):
        allCoveredSystems = []
        for snapshot in self.dashboardSvc.GetCurrentCampaignSnapshots():
            allCoveredSystems = allCoveredSystems + list(snapshot.coveredSolarsystemIDs)

        self.mapPanel = MapPanel(parent=self.sr.main, align=uiconst.TOALL, insurgencySystems=allCoveredSystems, dashboardSvc=self.dashboardSvc, campaignIDs=[ snapshot.campaignID for snapshot in self.dashboardSvc.GetCurrentCampaignSnapshots() ])
        GradientSprite(parent=self.sr.main, align=uiconst.TOBOTTOM_NOPUSH, idx=0, height=117, rgbData=[(0.0, (0.0, 0.0, 0.0))], alphaData=[(0.0, 0.0), (0.75, 0.75), (1.0, 1.0)], state=uiconst.UI_DISABLED, rotation=-math.pi / 2)
        tabGroupsCont = ContainerAutoSize(parent=self.sr.main, name='tabGroupsCont', align=uiconst.CENTERBOTTOM, height=48, top=30, alignMode=uiconst.TOLEFT, idx=0)
        self.selectorButtons = ToggleButtonGroupCircular(name='myToggleBtnGroup', parent=tabGroupsCont, align=uiconst.TOLEFT, callback=self.OnTabButtonSelectCampaign)
        Line(parent=tabGroupsCont, align=uiconst.TOLEFT, opacity=0.6, weight=1, padding=(12, 16, 12, 16))
        self.warzoneButtonGroup = ToggleButtonGroupCircular(name='warzoneButtonGroup', parent=tabGroupsCont, align=uiconst.TOLEFT, callback=self.OnFWButtonSelected)
        self.warzoneButtonGroup.AddButton(0, iconPath='res:/UI/Texture/classes/pirateinsurgencies/empires_icon.png')
        sortedSnapshots = sorted(self.dashboardSvc.GetCurrentCampaignSnapshots(), key=self._SnapshotSortFun)
        ids = []
        for snapshot in sortedSnapshots:
            ids.append(snapshot.campaignID)
            self.selectorButtons.AddButton(snapshot.campaignID, iconPath=GetFactionBadgeSmall(GetPirateFactionIDFromWarzoneID(snapshot.warzoneID)))

        if len(ids) > 0:
            self.selectorButtons.SetSelectedByID(self.mapPanel.systemIDToCampaignID[self.mapPanel.initialInterestID])
        self.ConstructRightView()
        self.ConstructLeftView()

    def _SnapshotSortFun(self, snapshot):
        return GetPirateFactionDisplayOrder(WARZONE_ID_TO_PIRATE_FACTION_ID[snapshot.warzoneID])

    def ConstructRightView(self):
        panelWidth = 300
        rightCont = ScrollContainer(parent=self.sr.main, name='rightCont', align=uiconst.TORIGHT_NOPUSH, width=panelWidth, idx=0, clipChildren=True)
        Fill(bgParent=rightCont, color=eveColor.BLACK, opacity=0.5)
        self.systemInfo = SystemInfo(height=295, dashboardSvc=self.dashboardSvc)
        CollapsingSection(name='systemInformationSection', parent=rightCont, section=self.systemInfo, headerText=GetByLabel('UI/PirateInsurgencies/systemInformation'), collapsed=False, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, headerTextIndentation=16)
        self.systemInfo.OnSystemSelected(self.mapPanel.initialInterestID)
        self.progress = Progress(height=315, dashboardSvc=self.dashboardSvc)
        CollapsingSection(name='insuregenceProgressSection', parent=rightCont, section=self.progress, isContainerAutoSize=True, headerText=GetByLabel('UI/PirateInsurgencies/insurgencyProgress'), collapsed=False, align=uiconst.TOTOP, headerTextIndentation=16)
        snapshot = self.dashboardSvc.GetCurrentCampaignSnapshotByID(self.mapPanel.systemIDToCampaignID[self.mapPanel.initialInterestID])
        self.progress.OnInsurgencySelected(snapshot)
        self.insurgencyActivities = Activities(height=160, dashboardSvc=self.dashboardSvc)
        CollapsingSection(name='insurgenceActivitiesSection', parent=rightCont, section=self.insurgencyActivities, headerText=GetByLabel('UI/PirateInsurgencies/insurgencyObjectives'), collapsed=False, align=uiconst.TOTOP, headerTextIndentation=16)
        self.insurgencyActivities.ConstructLayout()

    def ConstructLeftView(self):
        if session.warfactionid is None:
            self.ConstructUnenlistedView()
        else:
            self.ConstructEnlistedView()

    def ConstructEnlistedView(self):
        panelWidth = 309
        leftCont = Container(parent=self.sr.main, name='leftCont', align=uiconst.TOLEFT_NOPUSH, width=panelWidth, idx=0)
        myFactionID = session.warfactionid
        Frame(bgParent=Container(parent=leftCont, align=uiconst.TOBOTTOM_NOPUSH, height=804), texturePath=GetBannerPathFromFactionID(myFactionID))
        Fill(bgParent=leftCont, color=eveColor.BLACK, opacity=0.5)
        contentCont = Container(name='contentCont', parent=leftCont, padding=(64, 0, 64, 104), align=uiconst.TOBOTTOM, height=804, width=200)
        Sprite(parent=contentCont, align=uiconst.CENTERTOP, texturePath=GetFactionBadge(myFactionID), width=96, height=96, top=210, left=0, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.5)
        Button(parent=contentCont, align=uiconst.TOBOTTOM, padTop=16, label=GetByLabel('UI/PirateInsurgencies/unenlist'), frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT, func=self._OpenEnlistmentWnd)
        Button(parent=contentCont, align=uiconst.TOBOTTOM, padTop=32, label=GetByLabel('UI/PirateInsurgencies/learnMore'), frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT, func=self._OpenInsurgencyAgencySection, varient=ButtonVariant.PRIMARY)
        self.statsCont = Container(parent=contentCont, align=uiconst.TOBOTTOM, padTop=24, height=63, padBottom=32)
        rankName, _rankDescription = self.dashboardSvc.GetCurrentRank()
        carbonui.TextBody(padTop=5, parent=self.statsCont, align=uiconst.TOTOP, text=GetByLabel('UI/PirateInsurgencies/rank', rank=rankName))
        self.statsLoadingWheel = LoadingWheel(parent=self.statsCont, align=uiconst.CENTER)
        atWarWithCont = ContainerAutoSize(name='atWarWithCont', parent=Container(parent=contentCont, align=uiconst.TOBOTTOM, height=32), align=uiconst.CENTER, height=32, alignMode=uiconst.TOLEFT)
        carbonui.TextBody(parent=atWarWithCont, align=uiconst.TOLEFT, text=GetByLabel('UI/PirateInsurgencies/atWarWith'), color=TextColor.HIGHLIGHT)
        enemies = GetInsurgencyEnemyFactions(myFactionID)
        for enemy in enemies:
            Sprite(parent=Transform(parent=atWarWithCont, width=20, height=20, align=uiconst.TOLEFT, top=-6, padLeft=5), texturePath=GetFactionBadgeSmall(enemy), color=eveColor.WHITE, state=uiconst.UI_NORMAL, hint=cfg.eveowners.Get(enemy).name, width=20, height=20, align=uiconst.CENTER)

        alignedWithCont = Container(name='alignedWithCont', parent=contentCont, align=uiconst.TOBOTTOM, height=32, opacity=1, padTop=26)
        carbonui.TextBody(parent=alignedWithCont, align=uiconst.CENTER, text=GetByLabel('UI/PirateInsurgencies/alignedWith', factionName=get_faction_name(myFactionID)), color=TextColor.HIGHLIGHT)
        self.FillStatsCont(self.statsCont, self.statsLoadingWheel)

    def FillStatsCont(self, statsCont, loadingWheel):
        stats = self.dashboardSvc.GetPersonalStats()
        loadingWheel.Hide()
        data = stats['data']
        killsYesterday = data['killsY']['you']
        killsLastWeek = data['killsLW']['you']
        killsYesterdayRow = ContainerAutoSize(name='killsYesterdayRow', parent=statsCont, alignMode=uiconst.TOPLEFT, align=uiconst.TOTOP)
        carbonui.TextBody(parent=killsYesterdayRow, align=uiconst.TOPLEFT, text=GetByLabel('UI/PirateInsurgencies/killsYesterday'), padTop=8)
        carbonui.TextBody(parent=killsYesterdayRow, align=uiconst.TOPRIGHT, text=killsYesterday, padTop=8)
        killsLastWeekRow = ContainerAutoSize(parent=statsCont, alignMode=uiconst.TOPLEFT, align=uiconst.TOTOP)
        carbonui.TextBody(padTop=8, parent=killsLastWeekRow, align=uiconst.TOPLEFT, text=GetByLabel('UI/PirateInsurgencies/killsLastWeek'))
        carbonui.TextBody(parent=killsLastWeekRow, align=uiconst.TOPRIGHT, text=killsLastWeek, padTop=8)

    def ConstructUnenlistedView(self):
        panelWidth = 308
        Container(parent=self.sr.main, name='bcCont', align=uiconst.TOLEFT_NOPUSH, width=panelWidth, idx=0, bgColor=eveColor.BLACK, opacity=0.5)
        leftCont = Container(parent=self.sr.main, name='leftCont', align=uiconst.TOLEFT_NOPUSH, width=panelWidth, idx=0)
        Frame(bgParent=Container(parent=leftCont, align=uiconst.TOTOP_NOPUSH, height=850), texturePath='res:/UI/Texture/classes/pirateinsurgencies/banners/invitation_banner.png')
        buttonContentCont = ContainerAutoSize(name='buttonContentCont', parent=leftCont, padding=(27, 0, 27, 80), align=uiconst.TOBOTTOM, alignMode=uiconst.TOTOP, height=308, idx=0)
        carbonui.TextHeadline(parent=Container(parent=buttonContentCont, align=uiconst.TOTOP, height=30), align=uiconst.CENTER, text=GetByLabel('UI/PirateInsurgencies/joinTheInsurgency'))
        carbonui.TextBody(parent=buttonContentCont, align=uiconst.TOTOP, padTop=32, text=GetByLabel('UI/PirateInsurgencies/joinTheInsurgencyFlavourText'))
        Button(parent=buttonContentCont, align=uiconst.TOTOP, padTop=24, label=GetByLabel('UI/PirateInsurgencies/openFactionSelection'), frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT, variant=ButtonVariant.PRIMARY, func=self._OpenEnlistmentWnd)
        Button(parent=buttonContentCont, align=uiconst.TOTOP, padTop=12, label=GetByLabel('UI/PirateInsurgencies/learnMoreAboutTheInsurgency'), frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT, func=self._OpenInsurgencyAgencySection)

    def _OpenEnlistmentWnd(self, *args):
        uicore.cmd.OpenFwEnlistment()

    def _OpenInsurgencyAgencySection(self, *args):
        sm.GetService('agencyNew').OpenWindow(contentGroupID=contentGroupPirateIncursionsGuide)

    def OnInsurgencyCampaignStartedForLocation_Local(self, _campaignSnapshot):
        self.sr.main.Flush()
        self.loadingWheel = LoadingWheel(parent=self.sr.main, align=uiconst.CENTER)
        uthread2.StartTasklet(self._AsyncConstructLayout)

    def OnInsurgencyCampaignUpdatedForLocation_Local(self, _campaignSnapshot):
        self.sr.main.Flush()
        self.loadingWheel = LoadingWheel(parent=self.sr.main, align=uiconst.CENTER)
        uthread2.StartTasklet(self._AsyncConstructLayout)

    def OnInsurgencyCampaignEndingForLocation_Local(self):
        self.sr.main.Flush()
        self.loadingWheel = LoadingWheel(parent=self.sr.main, align=uiconst.CENTER)
        uthread2.StartTasklet(self._AsyncConstructLayout)

    def OnJoinMilitia(self, *args):
        self.sr.main.Flush()
        self.loadingWheel = LoadingWheel(parent=self.sr.main, align=uiconst.CENTER)
        uthread2.StartTasklet(self._AsyncConstructLayout)

    def OnFWButtonSelected(self, newBtn, _oldBtn):
        if newBtn is None:
            return
        sm.GetService('cmd').OpenMilitia()
        self.warzoneButtonGroup.DeselectAll()
