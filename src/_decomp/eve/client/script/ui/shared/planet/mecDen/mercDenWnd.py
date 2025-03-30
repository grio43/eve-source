#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\mecDen\mercDenWnd.py
import appConst
import eveicon
import uthread2
from ballparkCommon.parkhelpers.warpSubjects import WarpSubjects
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbon.common.script.util.format import FmtAmt
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import Align, ButtonStyle, TextColor, TextAlign, ButtonFrameType
from carbonui.control.button import Button
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.control.scroll import Scroll
from carbonui.control.window import Window
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.loadingContainer import LoadingContainer
from eve.client.script.ui.control.scrollUtil import TabFinder
from eve.client.script.ui.control.statefulButton import StatefulButton
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupMercDens
from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
from eve.client.script.ui.shared.cloneGrade import ORGIN_MY_MERCDENS
from eve.client.script.ui.shared.planet.mecDen.btnController import MercDenButtonController
from eve.client.script.ui.shared.planet.mecDen.mercDenEntry import MerDenEntry, GetMercDenEntry, GetEmptySlotEntry, MerDenEmptySlotEntry, GetMercDenEntryData, BaseMerDenEntry
from eve.client.script.ui.shared.planet.mecDen.mercDenUiController import MercDenUiController
from eve.client.script.ui.shared.sov.threadedLoader import ThreadedLoader
from eveexceptions import ExceptionEater
from eveservices.menu import GetMenuService
from inventorycommon.const import typeMercenaryDenManagementSkill
from localization import GetByLabel
import carbonui
from menu import MenuLabel
from signals.signalUtil import ChangeSignalConnect
from sovereignty.mercenaryden.client.mercenary_den_signals import on_mercenary_den_removed, on_mercenary_den_added, on_mercenary_den_changed
from sovereignty.mercenaryden.client.ui.containers.management import ManagementContainerWithTabs
from sovereignty.mercenaryden.client.ui.containers.summary import SummaryContainer
from sovereignty.mercenaryden.client.ui.controller import MercenaryDenController
from carbonui.uicore import uicore
RIGHT_WIDTH = 416

class MyMercDensWnd(Window):
    __notifyevents__ = ['OnSkillsChanged', 'OnSubscriptionChanged_Local']
    default_width = 900
    default_height = 572
    default_minSize = (650, 572)
    default_windowID = 'myMercDensWnd'
    default_captionLabelPath = 'UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/MyMercenaryDens'
    default_descriptionLabelPath = 'UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/MyMercenaryDensDesc'
    default_iconNum = eveicon.mercenary_den_product_icon

    def DebugReload(self, *args):
        self.Reload(self)

    def GetMenuMoreOptions(self):
        menu_data = super(MyMercDensWnd, self).GetMenuMoreOptions()
        if session.role & ROLE_PROGRAMMER:
            menu_data.AddEntry('QA Reload', self.DebugReload)
        return menu_data

    def ApplyAttributes(self, attributes):
        self.threadedLoader = ThreadedLoader()
        self.statefulBtn = None
        self._btnUpdateThread = None
        self._selectedMercDenController = None
        super(MyMercDensWnd, self).ApplyAttributes(attributes)
        self.uiController = MercDenUiController()
        self.ConstructUI()
        self.LoadWindow()
        self.ChangeSignalConnection(connect=True)
        sm.RegisterNotify(self)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(on_mercenary_den_removed, self.OnMercenaryDenAddedOrRemoved), (on_mercenary_den_added, self.OnMercenaryDenAddedOrRemoved), (on_mercenary_den_changed, self.OnMercenaryDenChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def ConstructUI(self):
        self.rightCont = Container(name='rightCont', parent=self.content, align=Align.TORIGHT, width=RIGHT_WIDTH, padLeft=16)
        self.loadingCont = LoadingContainer(parent=self.content, failureStateMessage=GetByLabel('UI/Sovereignty/SovHub/HubWnd/FailedToFetchData'), retryBtnLabel=GetByLabel('UI/Personalization/PaintTool/ErrorRetry'))
        self.leftCont = Container(name='leftCont', parent=self.loadingCont)
        self.ConstructLeft()
        self.ConstructRight()

    def ConstructLeft(self):
        bgColor = eveColor.WHITE[:3] + (0.05,)
        deployedCont = ContainerAutoSize(parent=self.leftCont, align=Align.TOTOP, bgColor=bgColor, alignMode=Align.CENTERLEFT, top=16)
        self.noDeployedContainer = ContainerAutoSize(parent=self.leftCont, align=Align.TOTOP, alignMode=Align.TOTOP, top=16)
        self.noDeployedLabel = carbonui.TextBody(parent=self.noDeployedContainer, text=GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/NoDensMessage'), padding=8, align=Align.TOTOP, textAlign=TextAlign.CENTER)
        buttonCont = ContainerAutoSize(parent=self.noDeployedContainer, align=Align.TOTOP, alignMode=Align.CENTERTOP)
        self.noDeployedButton = Button(parent=buttonCont, align=Align.CENTERTOP, label=GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/OpenAgencyButton'), func=lambda *args: self.OpenAgency(), frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT, texturePath='res:/UI/Texture/classes/agency/icons/agency.png')
        self.noDeployedContainer.display = False
        self.skillCont = Container(name='skillCont', parent=self.leftCont, align=Align.TOBOTTOM, top=8)
        self.skillBntCont = Container(name='skillBntCont', parent=self.skillCont, align=Align.TORIGHT)
        self.skillTextCont = Container(name='skillTextCont', parent=self.skillCont, align=Align.TOALL, clipChildren=True, padLeft=8)
        textPadding = 8
        text = GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/DeployedDens')
        carbonui.TextBody(parent=deployedCont, text=text, padding=textPadding, align=Align.CENTERLEFT)
        self.numDensLabel = carbonui.TextBody(parent=deployedCont, text='', padding=textPadding, align=Align.CENTERRIGHT, pickState=carbonui.PickState.ON)
        self.numDensLabel.LoadTooltipPanel = self.LoadNumDensTooltipPanel
        self.scroll = Scroll(parent=self.leftCont, top=16, id='myMercDenScroll')
        self.scroll.GetTabStops = self.GetTabStops

    def ConstructRight(self):
        PanelUnderlay(bgParent=self.rightCont)
        self.buttonCont = Container(name='buttonCont', parent=self.rightCont, align=Align.TOBOTTOM, height=50)
        self.summaryParentCont = ContainerAutoSize(name='summaryParentCont', parent=self.rightCont, align=Align.TOTOP)
        self.mgmtParentCont = ContainerAutoSize(name='mgmtParentCont', parent=self.rightCont, align=Align.TOTOP, padding=(16, 16, 16, 0))

    def LoadWindow(self):
        self.loadingCont.LoadContent(loadCallback=self.LoadLeftSide)

    def OnMercenaryDenAddedOrRemoved(self, mercDenID):
        delaySec = 3
        uthread2.call_after_wallclocktime_delay(self.LoadLeftSide, delaySec)

    def OnMercenaryDenChanged(self, mercDenID):
        selectedNodes = self.scroll.GetSelected()
        if selectedNodes:
            mercDenEntryInfo = selectedNodes[0].mercDenEntryInfo
            if mercDenEntryInfo and mercDenEntryInfo.item_id == mercDenID:
                self.LoadRightSide(mercDenEntryInfo)

    def LoadLeftSide(self):
        if self.destroyed:
            return
        myMercDens = self.uiController.GetEntryInfosForMyMercDens()
        myMaxDens = self.uiController.myMaxDenNum
        scrollList = []
        selectedItemID = self.uiController.GetSelectedItemID()
        denIDs = {x.item_id for x in myMercDens}
        if not selectedItemID or selectedItemID not in denIDs:
            if myMercDens:
                selectedItemID = myMercDens[0].item_id
        for eachDen in myMercDens:
            isSelected = eachDen.item_id == selectedItemID
            entry = GetMercDenEntry(self, eachDen, isSelected)
            scrollList.append(entry)

        numMercDens = len(myMercDens)
        if numMercDens == 0:
            self.noDeployedContainer.display = True
        if myMaxDens is not None and myMaxDens > numMercDens and numMercDens > 0:
            for x in xrange(myMaxDens - numMercDens):
                entry = GetEmptySlotEntry()
                scrollList.append(entry)

        self.threadedLoader.StartLoading(self.UpdateDenNum, self)
        self.threadedLoader.StartLoading(self.LoadSkillsCont, self)
        headers = MerDenEntry.GetHeaders()
        self.scroll.Load(contentList=scrollList, headers=headers)
        self.UpdateHeaderHints()
        if myMercDens:
            self.rightCont.Show()
            self.LoadRightSideFromScrollSelection()
        else:
            self.rightCont.Hide()

    def UpdateHeaderHints(self):
        for i, eachHeaderChild in enumerate(self.scroll.GetHeadersChildren()):
            eachHeaderChild.GetHint = lambda idx = i: self.GetHeaderHint(idx)

    def GetHeaderHint(self, idx, *args):
        hint = None
        headerHint = BaseMerDenEntry.GetHeadersHint(idx)
        if headerHint:
            hint = headerHint
        if hint:
            from carbonui.uicore import uicore
            uicore.uilib.auxiliaryTooltip = None
        return hint

    def GetTabStops(self, headertabs, idx = None):
        return TabFinder().GetTabStops(self.scroll.sr.nodes, headertabs, BaseMerDenEntry, idx=idx)

    def OnMercDenClicked(self, entry):
        node = entry.sr.node
        mercDenEntryInfo = node.mercDenEntryInfo
        self.uiController.SelectEntry(mercDenEntryInfo.item_id)
        self.LoadRightSide(mercDenEntryInfo)

    def GetMercDenMenu(self, entry):
        node = entry.sr.node
        m = MenuData()
        if not node.mercDenEntryInfo.has_complete_info:
            m = MenuData()
            text = GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/ReloadData')
            m.AddEntry(text, func=lambda : self.ReloadEntry(entry))
            return m
        itemID = node.mercDenEntryInfo.item_id
        typeID = node.mercDenEntryInfo.type_id
        solarSystemID = node.mercDenEntryInfo.solar_system_id
        m.append(MenuEntryData(MenuLabel('UI/Common/Location'), subMenuData=GetMenuService().CelestialMenu(solarSystemID, typeID=appConst.groupSolarSystem)))
        m += GetMenuService().GetMenuFromItemIDTypeID(itemID, typeID)
        return m

    def LoadMotTooltipPanel(self, tooltipPanel, node, *args):
        numStarted = len({x for x in node.mercDenEntryInfo.activities if x.is_started})
        numActivities = len(node.mercDenEntryInfo.activities)
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 2
        tooltipPanel.AddTextBodyLabel(text=GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/AvailableMtoTooltip'), colSpan=tooltipPanel.columns, wrapWidth=200, color=TextColor.SECONDARY)
        tooltipPanel.AddTextBodyLabel(text=GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/StartedActivities'))
        tooltipPanel.AddTextBodyLabel(text=FmtAmt(numStarted), align=Align.CENTERRIGHT)
        tooltipPanel.AddTextBodyLabel(text=GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/AvailableActivities'))
        tooltipPanel.AddTextBodyLabel(text=numActivities, align=Align.CENTERRIGHT)

    def ReloadEntry(self, entry):
        node = entry.sr.node
        isSelected = node.isSelected
        mercDenEntryInfo = self.uiController.GetMercDenEntryInfo(node.mercDenEntryInfo.item_id)
        newNode = GetMercDenEntryData(self, mercDenEntryInfo, isSelected)
        node.update(newNode)
        entry.Load(node)
        self.scroll.UpdateTabStops()

    def UpdateDenNum(self):
        numDens = len([ x for x in self.scroll.GetNodes() if x.decoClass != MerDenEmptySlotEntry ])
        self.numDensLabel.text = self.uiController.GetDeployedDensText(numDens)

    def LoadNumDensTooltipPanel(self, tooltipPanel, *args):
        numDens = len([ x for x in self.scroll.GetNodes() if x.decoClass != MerDenEmptySlotEntry ])
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 2
        tooltipPanel.AddTextBodyLabel(text=GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/DeployedDens'))
        tooltipPanel.AddTextBodyLabel(text=numDens, align=Align.CENTERRIGHT)
        myMax = self.uiController.myMaxDenNum
        absoluteMax = self.uiController.absoluteMaxDenNum
        if myMax is not None:
            tooltipPanel.AddTextBodyLabel(text=GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/MyMaxDeployable'))
            tooltipPanel.AddTextBodyLabel(text=myMax, align=Align.CENTERRIGHT)
            if self.uiController.IsAlpha():
                if numDens:
                    text = GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/AlphaMaxWithDensDeployed')
                else:
                    text = GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/AlphaMaxWithoutDensDeployed')
                tooltipPanel.AddTextDetailsLabel(text=text, colSpan=tooltipPanel.columns, color=eveColor.OMEGA_YELLOW, wrapWidth=200)
            elif myMax < absoluteMax:
                text = GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/MaxDeployedWithFullSkills', numDens=absoluteMax)
                tooltipPanel.AddTextDetailsLabel(text=text, colSpan=tooltipPanel.columns, color=TextColor.SECONDARY, wrapWidth=200)

    def LoadSkillsCont(self):
        self.skillBntCont.Flush()
        self.skillTextCont.Flush()
        if self.uiController.IsAlpha():
            btn = Button(parent=self.skillBntCont, label=GetByLabel('Tooltips/SkillPlanner/UpgradeToOmega'), texturePath=eveicon.omega, style=ButtonStyle.MONETIZATION, func=self.OnOmegaBtnClicked, align=Align.CENTERRIGHT)
            text = GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/OmegaText')
        elif self.uiController.CanTrainMoreSkills():
            btn = Button(name='skillTrainingBtn', parent=self.skillBntCont, texturePath=eveicon.skill_book, label=GetByLabel('UI/Agency/MercDen/OpenSkillTraining'), func=self.OpenSkillTraining, align=Align.CENTERRIGHT)
            text = GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/UnlockSlotsWithTraining')
        else:
            return
        self.skillCont.height = btn.height
        self.skillBntCont.width = btn.width
        carbonui.TextDetail(parent=self.skillTextCont, text=text, align=Align.CENTERLEFT, color=TextColor.SECONDARY, pickState=carbonui.PickState.ON, autoFadeSides=16)

    def OnOmegaBtnClicked(self, *args):
        uicore.cmd.OpenCloneUpgradeWindow(origin=ORGIN_MY_MERCDENS)

    def OpenSkillTraining(self, *args):
        uicore.cmd.OpenSkillsWindow()

    def OpenAgency(self, *args):
        AgencyWndNew.OpenAndShowContentGroup(contentGroupMercDens)

    def LoadRightSideFromScrollSelection(self):
        selectedNodes = self.scroll.GetSelected()
        if selectedNodes:
            mercDenEntryInfo = selectedNodes[0].mercDenEntryInfo
        else:
            mercDenEntryInfo = None
        self.LoadRightSide(mercDenEntryInfo)

    def LoadRightSide(self, denEntryInfo):
        self.summaryParentCont.Flush()
        self.mgmtParentCont.Flush()
        self.buttonCont.Flush()
        if denEntryInfo is None or not denEntryInfo.has_complete_info:
            return
        denTypeID = denEntryInfo.type_id
        self.ClearSelectedMercDenController()
        self._selectedMercDenController = MercenaryDenController(denEntryInfo.item_id, denTypeID, denEntryInfo.mercenary_den_info)
        summary_header_container = SummaryContainer(name='summary_header_container', parent=self.summaryParentCont, align=Align.TOTOP, controller=self._selectedMercDenController, should_show_owner=True, should_show_skyhook_owner=True, should_show_infomorphs_collected=False, should_show_workforce_cost=True, should_show_bg=False)
        summary_header_container.load_controller(self._selectedMercDenController)
        mgmtCont = ManagementContainerWithTabs(name='mgmtCont', parent=self.mgmtParentCont, align=Align.TOTOP, controller=self._selectedMercDenController)
        mgmtCont.load_controller(self._selectedMercDenController)
        mgmtCont.set_width(RIGHT_WIDTH - self.mgmtParentCont.padLeft)
        locationBtnController = MercDenButtonController(dockabeLocationID=None, solarSystemID=denEntryInfo.solar_system_id, typeID=denEntryInfo.type_id, itemID=denEntryInfo.item_id, warpSubject=WarpSubjects.MERCENARY_DEN)
        self.statefulBtn = StatefulButton(name='stationButton', parent=self.buttonCont, align=Align.BOTTOMRIGHT, iconAlign=Align.TORIGHT, controller=locationBtnController, pos=(8, 8, 0, 0))
        self._btnUpdateThread = AutoTimer(1000, self.UpdateBtn_thread)

    def ClearSelectedMercDenController(self):
        if self._selectedMercDenController:
            self._selectedMercDenController.clear()

    def UpdateBtn_thread(self):
        if self.statefulBtn is None or self.statefulBtn.destroyed or self.destroyed:
            self._btnUpdateThread = None
            return
        if not self.statefulBtn.controller.IsInCurrentSolarSystem():
            return
        if session.stationid or session.structureid:
            return
        self.statefulBtn.UpdateState()

    def OnSkillsChanged(self, skills):
        if typeMercenaryDenManagementSkill in skills:
            self._UpdateOnChangedNumbers()

    def OnSubscriptionChanged_Local(self):
        self._UpdateOnChangedNumbers()

    def _UpdateOnChangedNumbers(self):
        self.uiController.ClearMyMaxDens()
        self.LoadLeftSide()

    def Close(self, *args, **kwds):
        with ExceptionEater('Closing MyMercDenWnd'):
            self.ChangeSignalConnection(connect=False)
            self.ClearSelectedMercDenController()
            self.uiController = None
        super(MyMercDensWnd, self).Close(*args, **kwds)
