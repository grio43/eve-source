#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingWnd.py
import evetypes
import eveui
import locks
import telemetry
import threadutils
import uthread
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_WORLDMOD, ROLE_GML
from carbon.common.script.util.format import FmtAmt
from carbonui import AxisAlignment, const as uiconst, fontconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.window import Window
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.uicore import uicore
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from eve.client.script.ui.control.divider import Divider
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelMedium
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.shared.fitting.cosmeticFittingController import CosmeticFittingController
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors, FTTING_PANEL_SETTING_LEFT_WIDTH, GetBaseShapeSize, GetFittingDragData, GetScaleFactor, GetTypeIDForController, PANEL_WIDTH_DEFAULT, PANEL_WIDTH_MAX, PANEL_WIDTH_MIN, PANEL_WIDTH_RIGHT
from eve.client.script.ui.shared.fittingScreen import TAB_CONFIGNAME_BROWSER, TAB_CONFIGNAME_STATS, TAB_CONFIGNAME_INVENTORY
from eve.client.script.ui.shared.fittingScreen.baseFitting import FittingCont
from eve.client.script.ui.shared.fittingScreen.cosmetics.cosmeticFitting import CosmeticFitting
from eve.client.script.ui.shared.fittingScreen.dronePickerMenu import DronePickerMenu
from eve.client.script.ui.shared.fittingScreen.fighterPickerMenu import FighterBayItemPickerMenu
from eve.client.script.ui.shared.fittingScreen.fittingPanels.minihangar import CargoCargoSlots, CargoDroneSlots, CargoFighterSlots, CargoStructureAmmoBay
from eve.client.script.ui.shared.fittingScreen.fittingUtil import GetColoredText
from eve.client.script.ui.shared.fittingScreen.ghostShipIcon import GhostShipIcon
from eve.client.script.ui.shared.fittingScreen.cosmetics.cosmeticsTab import CosmeticsTab
from eve.client.script.ui.shared.fittingScreen.historyCont import FittingHistoryCont
from eve.client.script.ui.shared.fittingScreen.invPanel import FittingInvPanel
from eve.client.script.ui.shared.fittingScreen.itemPickerMenu import CargoItemPickerMenu
from eve.client.script.ui.shared.fittingScreen.leftPanel import LeftPanel
from eve.client.script.ui.shared.fittingScreen.serviceCont import FittingServiceCont
from eve.client.script.ui.shared.fittingScreen.settingUtil import GetCurrentLeftPanelKey, GetCurrentRightPanelKey, SetCurrentRightPanelKey, SetCurrentLeftPanelKey
from eve.client.script.ui.shared.fittingScreen.sidePanelButtons import SidePanelTabGroup, SidePanelTabGroupSmall
from eve.client.script.ui.shared.fittingScreen.skillRequirements import GetSkillTooltip, GetMissingSkills_HighestLevelByTypeID, GetAllTypeIDsMissingSkillsForShipAndContent
from eve.client.script.ui.shared.fittingScreen.statsPanel import StatsPanel
from eve.client.script.ui.shared.fittingScreen.warningIconCont import WarningIconCont
from eve.client.script.ui.shared.pointerTool import pointerToolConst as pConst
from eve.client.script.ui.shared.traits import HasTraits, TraitsContainer
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
from eve.common.script.sys.eveCfg import GetActiveShip
from eveexceptions import UserError
from eveui.decorators import lock_and_set_pending
from localization import GetByLabel
from shipfitting.fittingWarningConst import WARNING_OVER_CPU, WARNING_OVER_POWERGRID
from shipfitting.fittingWarnings import GetColorForLevel
from signals.signalUtil import ChangeSignalConnect
ANIM_DURATION = 0.25
FITTING_MODE_TAB_GROUP_ANALYTIC_ID = 'FittingModeTabGroup'
LEFT_TABS = [TAB_CONFIGNAME_BROWSER, TAB_CONFIGNAME_INVENTORY]
TAB_ID_FITTING = 'equipment'
TAB_ID_COSMETIC = 'personalization'
WND_NORMAL_HEIGHT_BIG = 676
WND_NORMAL_HEIGHT_SMALL = 676

def OpenFittingWnd(tabID):
    wnd = FittingWindow.GetIfOpen()
    if wnd and not wnd.destroyed:
        wnd.Maximize()
    else:
        wnd = FittingWindow.Open()
    wnd.GoToTab(tabID)


class FittingWindow(Window):
    __guid__ = 'FittingWindow'
    __notifyevents__ = ['OnSetDevice',
     'OnSessionChanged',
     'OnFindTypeInList',
     'OnSimulationChanged',
     'OnUIScalingChange',
     'OnSkillsChanged',
     'OnFittingFlagFilterSet',
     'OnCurrentStructureStateChanged']
    default_fixedHeight = WND_NORMAL_HEIGHT_BIG
    default_windowID = 'fittingWnd'
    default_captionLabelPath = 'Tooltips/StationServices/ShipFittingGhost'
    default_descriptionLabelPath = 'Tooltips/StationServices/ShipFittingGhost_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/fitting.png'
    default_isCollapseable = False
    open_fitting_window_tab = None

    def __init__(self, **kwargs):
        self._left_side_fill = None
        super(FittingWindow, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnResizeable()
        self.windowReady = False
        self._controller = None
        self.cosmeticController = None
        self._layoutLock = locks.Lock()
        itemID = attributes.shipID or GetActiveShip()
        self.LoadFittingController(itemID)
        self.LoadCosmeticController(itemID)
        self.LoadWnd()
        self.on_content_padding_changed.connect(self._on_content_padding_changed)

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, value):
        self._controller = value

    @telemetry.ZONE_METHOD
    @eveui.skip_if_destroyed
    def LoadWnd(self):
        self.ConstructLayout()
        if self.destroyed:
            return
        self.ConstructTabs()
        self.LoadLeftPanel(key=None)

    def LoadFittingController(self, shipID):
        try:
            if self.controller:
                with EatSignalChangingErrors(errorMsg='fitting wnd'):
                    self.ChangeSignalConnection(connect=False)
                self.controller.Close()
            self.controller = sm.GetService('ghostFittingSvc').LoadGhostFittingController(shipID)
        except UserError:
            self.Close()
            raise

        self._fixedHeight = GetFixedWndHeight(self.controller)
        self.ChangeSignalConnection(connect=True)

    def LoadCosmeticController(self, itemID):
        self.cosmeticController = CosmeticFittingController(itemID)

    def GoToTab(self, tabID, cosmeticTabID):
        self.fittingModeTabGroup.SelectByID(tabID)
        if tabID == TAB_ID_COSMETIC and cosmeticTabID is not None:
            self.cosmeticsPanel.GoToTab(cosmeticTabID)

    def OnControllerChanging(self, itemID):
        self.LoadFittingController(itemID)
        if not self.controller.IsSimulated():
            self.LoadCosmeticController(itemID)
        self.LoadWnd()
        if getattr(self, 'warningIconCont', None):
            self.warningIconCont.ChangeController(self.controller)
        sm.GetService('ghostFittingSvc').SendOnSimulatedShipLoadedEvent(itemID, self.controller.GetTypeID())

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_stats_changed, self.UpdateStatsOnSignal),
         (self.controller.on_new_itemID, self.OnNewItem),
         (self.controller.on_should_close, self.Close),
         (self.controller.on_simulation_state_changed, self.OnSimulationStateChanged),
         (self.controller.on_controller_changing, self.OnControllerChanging),
         (self.controller.on_name_changed, self.UpdateShipName),
         (self.controller.on_warning_display_changed, self.ChangeWarningDisplay)]
        ChangeSignalConnect(signalAndCallback, connect)

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader(on_tab_selected=self.OnFittingModeTabChange)
        self.header._line.Hide()

    def ConstructTabs(self):
        self.fittingModeTabGroup.Flush()
        self.fittingModeTabGroup.AddTab(label=GetByLabel('UI/Fitting/FittingWindow/Fitting'), panel=self.moduleFittingModeContainer, tabID=TAB_ID_FITTING, uniqueName=pConst.UNIQUE_NAME_FITTING_EQUIPMENT)
        self.fittingModeTabGroup.AddTab(label=GetByLabel('UI/ShipCosmetics/Personalization'), panel=self.cosmeticFittingModeContainer, tabID=TAB_ID_COSMETIC, tabClass=CosmeticsTab, callback=self.AllowSwitchToCosmeticSection, enabled=not self.controller.ControllerForCategory() == const.categoryStructure, uniqueName=pConst.UNIQUE_NAME_FITTING_PERSONALIZATION)
        self.fittingModeTabGroup.AutoSelect()

    @telemetry.ZONE_METHOD
    def ConstructLayout(self):
        self._fixedHeight = GetFixedWndHeight(self.controller)
        self.height = self._fixedHeight
        with self._layoutLock:
            self.content.Flush()
            width = self.GetLeftPanelWidth() if self.IsLeftPanelExpanded() else 0
            opacity = 1.0 if self.IsLeftPanelExpanded() else 0.0
            padValue = 4
            self.fittingModeTabGroup = self.header.tab_group
            self.fittingModeTabGroup.analyticID = FITTING_MODE_TAB_GROUP_ANALYTIC_ID
            self.fittingModeTabGroup.callback = self.OnFittingModeTabChange
            self.moduleFittingModeContainer = Container(name='moduleFittingModeContainer', parent=self.content, align=uiconst.TOALL)
            self.cosmeticFittingModeContainer = Container(name='cosmeticFittingModeContainer', parent=self.content, align=uiconst.TOALL)
            self.cosmeticFittingModeContainer.Hide()
            self.leftPanelCont = Container(name='leftPanelCont', parent=self.moduleFittingModeContainer, align=uiconst.TOLEFT, width=width, opacity=opacity)
            self.xDivider = Divider(name='xDivider', parent=self.leftPanelCont, align=uiconst.TORIGHT, width=8, state=uiconst.UI_NORMAL, cross_axis_alignment=AxisAlignment.END)
            self.xDivider.Startup(self.leftPanelCont, 'width', 'x', minValue=PANEL_WIDTH_MIN, maxValue=PANEL_WIDTH_MAX)
            self.xDivider.OnSizeChanging = self.OnDividerMove
            self._left_side_fill = PanelUnderlay(bgParent=self.leftPanelCont, padding=self._get_left_side_fill_padding())
            self.leftPanel = LeftPanel(name='leftPanel', parent=self.leftPanelCont, align=uiconst.TOALL, configName=TAB_CONFIGNAME_BROWSER, controller=self.controller)
            self.leftPanel.display = False
            self.invPanel = FittingInvPanel(name='invPanel', parent=self.leftPanelCont, align=uiconst.TOALL, configName=TAB_CONFIGNAME_INVENTORY, controller=self.controller)
            self.invPanel.display = False
            self.leftSubPanels = [self.leftPanel, self.invPanel]
            width = PANEL_WIDTH_RIGHT if self.IsRightPanelExpanded() else 0
            self.rightPanel = StatsPanel(name='rightside', parent=self.moduleFittingModeContainer, align=uiconst.TORIGHT, width=width, controller=self.controller)
            mainCont = Container(name='mainCont', parent=self.moduleFittingModeContainer, top=-8)
            serviceSlots = {}
            if self.controller.ControllerForCategory() == const.categoryStructure:
                self.serviceCont = FittingServiceCont(parent=mainCont, controller=self.controller)
                serviceSlots = self.serviceCont.GetSlotsByFlagID()
                fittingAlignment = uiconst.CENTERTOP
            else:
                fittingAlignment = uiconst.CENTER
            self.controller.UpdateSlotsByFlagID({flagID:slot.controller for flagID, slot in serviceSlots.iteritems()})
            if self.destroyed:
                return
            FittingCont(name='FittingContTrue', parent=mainCont, owner=self, controller=self.controller, align=fittingAlignment, serviceSlots=serviceSlots)
            if self.destroyed:
                return
            overlayWidth, overlayHeight, overlayAlignment = GetOverlayWidthHeightAndAlignment(self.controller)
            self.overlayCont = Container(name='overlayCont', parent=mainCont, align=overlayAlignment, width=overlayWidth, height=overlayHeight)
            self.fighterAndDroneCont = None
            self.ConstructPanelExpanderBtn()
            self.ConstructInventoryIcons()
            self.ConstructPowerAndCpuLabels()
            self.ConstructCurrentGhostIcon(parent=mainCont)
            self.ConstructHistoryBar()
            if self.destroyed:
                return
            self.ConstructNameCaptionAndFittingWarnings(mainCont)
            self.windowReady = True
            self.width = self.GetWindowWidth()
            self.SetFixedWidth(self.width)
            self.ChangeHistoryDisplay()
            self.UpdateStats()
            self.cosmeticsPanel = CosmeticFitting(name='cosmeticsPanel', parent=self.cosmeticFittingModeContainer, align=uiconst.TOALL, cosmeticController=self.cosmeticController, controller=self.controller)

    def AllowSwitchToCosmeticSection(self):
        if sm.GetService('fittingSvc').IsShipSimulated():
            return sm.GetService('ghostFittingSvc').ShouldContinueAfterAskingAboutSwitchingShips(msg='ExitSimulationWarning')
        return True

    def OnFittingModeTabChange(self, newTabID, oldTabID):
        if newTabID != oldTabID:
            self._NotifyFittingTabChange(newTabID)
        if newTabID == TAB_ID_COSMETIC:
            self.cosmeticsPanel.PopulateSkinPanel()
        if not oldTabID:
            self.width = self.GetWindowWidth()
            self.SetFixedWidth(self.width)
            return
        if newTabID != oldTabID:
            if newTabID is TAB_ID_COSMETIC and oldTabID is TAB_ID_FITTING:
                if sm.GetService('fittingSvc').IsShipSimulated():
                    sm.GetService('ghostFittingSvc').ToggleGhostFitting(askQuestion=False)
                self.cosmeticsPanel.PopulateSkinPanel()
                self._AnimateToCosmeticsSection()
            if newTabID is TAB_ID_FITTING and oldTabID is TAB_ID_COSMETIC:
                self._AnimateToEquipmentSection()

    def _NotifyFittingTabChange(self, tabID):
        self.open_fitting_window_tab = tabID
        sm.ScatterEvent('OnFittingWindowTabChange', self.open_fitting_window_tab)

    def _AnimateToCosmeticsSection(self):
        self._fixedWidth = self.GetWindowWidth()
        leftDest = self.left
        if not self.IsLeftPanelExpanded():
            leftDest -= self.GetLeftPanelWidth()
        if not self.IsRightPanelExpanded():
            leftDest -= PANEL_WIDTH_RIGHT
        if self.IsUiScaled():
            self.width = self._fixedWidth
            self.left = leftDest
        else:
            uicore.animations.MorphScalar(self, 'width', self.width, self._fixedWidth, duration=ANIM_DURATION)
            uicore.animations.MorphScalar(self, 'left', self.left, leftDest, duration=ANIM_DURATION)
            uicore.animations.FadeTo(self.cosmeticsPanel.centerParent, startVal=0, endVal=1.0, duration=ANIM_DURATION)

    def _AnimateToEquipmentSection(self):
        self._fixedWidth = self.GetWindowWidth()
        leftDest = self.left
        if not self.IsLeftPanelExpanded():
            leftDest += self.GetLeftPanelWidth()
        if not self.IsRightPanelExpanded():
            leftDest += PANEL_WIDTH_RIGHT
        if self.IsUiScaled():
            self.width = self._fixedWidth
            self.left = leftDest
        else:
            uicore.animations.MorphScalar(self, 'width', self.width, self._fixedWidth, duration=ANIM_DURATION)
            uicore.animations.MorphScalar(self, 'left', self.left, leftDest, duration=ANIM_DURATION)

    def OnDividerMove(self, *args):
        settings.user.ui.Set(FTTING_PANEL_SETTING_LEFT_WIDTH, self.leftPanelCont.width)
        self.width = self.GetWindowWidth()
        self.SetFixedWidth(self.width)

    def LoadLeftPanel(self, key):
        if key is None:
            key = GetCurrentLeftPanelKey()
        for eachPanel in self.leftSubPanels:
            if eachPanel.configName != key:
                eachPanel.display = False

        if key == TAB_CONFIGNAME_BROWSER:
            self.leftPanel.Load()
            self.leftPanel.display = True
        elif key == TAB_CONFIGNAME_INVENTORY:
            self.invPanel.display = True
            self.invPanel.LoadPanel()

    def ConstructInventoryIcons(self):
        cargoDroneCont = ContainerAutoSize(name='cargoDroneCont', parent=self.overlayCont, align=uiconst.BOTTOMLEFT, width=110, left=4)
        structureInFittingWnd = self.controller.ControllerForCategory() == const.categoryStructure
        if structureInFittingWnd:
            cargoSlot = CargoStructureAmmoBay(name='structureCargoSlot', parent=cargoDroneCont, align=uiconst.TOTOP, height=32, controller=self.controller, getMenuFunc=self.GetCargoMenu)
            configName = 'StructureAmmoHold'
            self._SetFittingTooltipInfoForSlot(cargoSlot, configName)
        else:
            cargoSlot = CargoCargoSlots(name='cargoSlot', parent=cargoDroneCont, align=uiconst.TOTOP, height=32, controller=self.controller, getMenuFunc=self.GetCargoMenu)
            self._SetFittingTooltipInfoForSlot(cargoSlot, 'CargoHold')
        self.fighterAndDroneCont = Container(name='fighterAndDroneCont', parent=cargoDroneCont, align=uiconst.TOTOP, height=32)
        self.ContructDroneAndFighterIcons()

    def _SetFittingTooltipInfoForSlot(self, cargoSlot, configName):
        SetFittingTooltipInfo(cargoSlot, configName)
        if cargoSlot.itemUtilMenu:
            SetFittingTooltipInfo(cargoSlot.itemUtilMenu, configName)

    def ContructDroneAndFighterIcons(self):
        self.fighterAndDroneCont.Flush()
        structureInFittingWnd = self.controller.ControllerForCategory() == const.categoryStructure
        if self.controller.HasFighterBay():
            slot = CargoFighterSlots(name='fighterSlot', parent=self.fighterAndDroneCont, align=uiconst.TOTOP, height=32, controller=self.controller, getMenuFunc=self.GetFighterMenu)
            tooltipConfigName = 'FighterBayStructure' if structureInFittingWnd else 'FighterBay'
            self._SetFittingTooltipInfoForSlot(slot, tooltipConfigName)
        else:
            slot = CargoDroneSlots(name='droneSlot', parent=self.fighterAndDroneCont, align=uiconst.TOTOP, height=32, controller=self.controller, getMenuFunc=self.GetDroneMenu)
            tooltipConfigName = 'DroneBayStructure' if structureInFittingWnd else 'DroneBay'
            self._SetFittingTooltipInfoForSlot(slot, tooltipConfigName)
        self.fighterOrDroneSlot = slot

    def ReloadDroneAndFighterIconsIfNeeded(self):
        if self.fighterAndDroneCont is None:
            return
        if self.controller.HasFighterBay() and isinstance(self.fighterOrDroneSlot, CargoFighterSlots):
            return
        if not self.controller.HasFighterBay() and isinstance(self.fighterOrDroneSlot, CargoDroneSlots):
            return
        self.ContructDroneAndFighterIcons()

    def GetDroneMenu(self, menuParent):
        dronePicker = DronePickerMenu(self.controller, menuParent)
        menuParent._OnClose = lambda *args: dronePicker.DisconnectController()
        dronePicker.LoadItemScroll()
        uthread2.StartTasklet(dronePicker.RefrehsScroll)

    def GetCargoMenu(self, menuParent):
        itemPicker = CargoItemPickerMenu(self.controller, menuParent)
        menuParent._OnClose = lambda *args: itemPicker.DisconnectController()
        itemPicker.LoadItemScroll()
        uthread2.StartTasklet(itemPicker.RefrehsScroll)

    def GetFighterMenu(self, menuParent):
        itemPicker = FighterBayItemPickerMenu(self.controller, menuParent)
        menuParent._OnClose = lambda *args: itemPicker.DisconnectController()
        itemPicker.LoadItemScroll()
        uthread2.StartTasklet(itemPicker.RefrehsScroll)

    def ConstructNameCaptionAndFittingWarnings(self, parent):
        cont = Container(name='nameAndWarningsCont', parent=parent, top=8, align=uiconst.TOPLEFT, width=200, height=24)
        nameCont = Container(name='nameCont', parent=cont, align=uiconst.TOTOP, height=24)
        self.infoLink = InfoIcon(left=4, parent=nameCont, align=uiconst.CENTERLEFT)
        self.infoLink.LoadTooltipPanel = self.LoadInfoTooltipPanel
        self.infoLink.GetTooltipPointer = lambda *args: uiconst.POINT_RIGHT_2
        self.fitNameParent = ContainerAutoSize(name='fitNameParent', parent=nameCont, align=uiconst.CENTERLEFT, alignMode=uiconst.TOPLEFT, left=20, uniqueUiName=pConst.UNIQUE_NAME_CURRENT_FIT, state=uiconst.UI_NORMAL)
        self.fitNameParent.OnClick = self.OpenFittingForCurrentShip
        self.fitNameParent.GetDragData = GetFittingDragData
        self.fitNameParent.isDragObject = True
        linkIcon = ButtonIcon(parent=self.fitNameParent, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/classes/HyperNet/hyperlink_icon.png', pos=(0, 0, 16, 16), func=self.OpenFittingForCurrentShip, showGlow=False, state=uiconst.UI_DISABLED)
        nameLeft = linkIcon.left + linkIcon.width
        self.nameCaption = EveLabelMedium(name='nameCaption', parent=self.fitNameParent, text='', align=uiconst.TOPLEFT, left=nameLeft)
        w, h = self.nameCaption.MeasureTextSize(text='Xj')
        nameCont.height = h + 6
        SetTooltipHeaderAndDescription(targetObject=self.fitNameParent, headerText='', descriptionText=GetByLabel('Tooltips/FittingWindow/ShipName_description'))
        self.warningIconCont = WarningIconCont(parent=cont, fittingController=self.controller, align=uiconst.TOTOP, padLeft=6)
        cont.height += self.warningIconCont.height
        self.UpdateShipName()

    def LoadInfoTooltipPanel(self, tooltipPanel, *args):
        typeID = self.controller.GetTypeID()
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelLarge(text='<b>%s</b>' % evetypes.GetName(typeID))
        if HasTraits(typeID):
            tooltipPanel.AddSpacer(width=300, height=1)
            TraitsContainer(parent=tooltipPanel, typeID=typeID, padding=7)

    def LoadSkillTooltip(self, tooltipPanel, *args):
        return GetSkillTooltip(tooltipPanel, self.controller, fitName=self.GetFitName())

    def GetFitName(self):
        itemID = self.controller.GetItemID()
        if isinstance(itemID, long):
            return cfg.evelocations.Get(itemID).name
        else:
            return sm.GetService('ghostFittingSvc').GetShipName()

    def UpdateShipName(self):
        typeID = self.controller.GetTypeID()
        itemID = self.controller.GetItemID()
        name = self.GetFitName()
        self.nameCaption.text = name
        self.fitNameParent.tooltipPanelClassInfo.headerText = name
        self.infoLink.UpdateInfoLink(typeID, itemID)

    @threadutils.throttled(0.5)
    def UpdateSkillIcon(self):
        if getattr(self, 'haveSkillsIcon', None):
            if not self.controller.IsSimulated():
                self.haveSkillsIcon.display = False
                return
            self.haveSkillsIcon.display = True
            allTypeIDs = GetAllTypeIDsMissingSkillsForShipAndContent(self.controller.GetDogmaLocation())
            highestLevelByTypeID, _ = GetMissingSkills_HighestLevelByTypeID(allTypeIDs)
            if highestLevelByTypeID:
                self.haveSkillsIcon.texturePath = 'res:/UI/Texture/Icons/38_16_194.png'
            else:
                self.haveSkillsIcon.texturePath = 'res:/UI/Texture/Icons/38_16_193.png'

    def OnSkillsChanged(self, *args):
        self.UpdateSkillIcon()

    @eveui.skip_if_destroyed
    def OnSimulationChanged(self):
        self.UpdateShipName()

    def GetModeTooltipPointer(self):
        return uiconst.POINT_RIGHT_2

    def ChangeCurrentShipGhostDisplay(self):
        self.currentShipGhost.SetShipTypeID()

    def ConstructCurrentGhostIcon(self, parent):
        shipTypeID = GetTypeIDForController(session.shipid)
        self.currentShipGhost = GhostShipIcon(name='currentShipGhost', parent=parent, controller=self.controller, typeID=shipTypeID, align=uiconst.TOPRIGHT, pos=(11, 15, 64, 64), uniqueUiName=pConst.UNIQUE_NAME_SIMULATE_SHIP)
        self.ChangeCurrentShipGhostDisplay()

    def ConstructHistoryBar(self):
        historyController = sm.GetService('ghostFittingSvc').historyController
        baseSize = GetBaseShapeSize()
        multiplier = 0.5
        if GetScaleFactor() < 0.85:
            multiplier = 0.45
        historyWidth = baseSize * multiplier
        self.historyCont = FittingHistoryCont(parent=self.overlayCont, align=uiconst.CENTERBOTTOM, historyController=historyController, width=historyWidth)

    def ChangeHistoryDisplay(self):
        if self.controller.IsSimulated():
            self.historyCont.Show()
        else:
            self.historyCont.Hide()

    def OnSimulationStateChanged(self):
        if self.destroyed:
            return
        if self.controller.IsSimulated() or self.controller.ControllerForCategory() == const.categoryStructure:
            self._DisableCosmeticTab()
        else:
            self._EnableCosmeticTab()
        self.ChangeCurrentShipGhostDisplay()
        self.ChangeHistoryDisplay()

    def _DisableCosmeticTab(self):
        self.fittingModeTabGroup.CancelAutoSelect()
        self.fittingModeTabGroup.SelectByID(TAB_ID_FITTING)
        tab = self.fittingModeTabGroup.GetTabByID(TAB_ID_COSMETIC)
        if tab:
            tab.Disable()

    def _EnableCosmeticTab(self):
        tab = self.fittingModeTabGroup.GetTabByID(TAB_ID_COSMETIC)
        if tab:
            tab.Enable()

    def IsRightPanelExpanded(self):
        return GetCurrentRightPanelKey() == TAB_CONFIGNAME_STATS

    def IsLeftPanelExpanded(self):
        return GetCurrentLeftPanelKey() in LEFT_TABS

    def GetLeftPanelWidth(self):
        panelWidth = settings.user.ui.Get(FTTING_PANEL_SETTING_LEFT_WIDTH, PANEL_WIDTH_DEFAULT)
        return min(max(PANEL_WIDTH_MIN, panelWidth), PANEL_WIDTH_MAX)

    def ConstructPanelExpanderBtn(self):
        tabBtnData = [(GetByLabel('UI/Fitting/FittingWindow/FittingTab'),
          TAB_CONFIGNAME_BROWSER,
          'res:/UI/Texture/classes/Fitting/tabHardware.png',
          pConst.UNIQUE_NAME_FITTING_BROWSER), (GetByLabel('UI/Fitting/FittingWindow/InvTab'),
          TAB_CONFIGNAME_INVENTORY,
          'res:/UI/Texture/WindowIcons/items.png',
          pConst.UNIQUE_NAME_FITTING_INVENTORY)]
        selectedTab = GetCurrentLeftPanelKey()
        scaleFactor = GetScaleFactor()
        if scaleFactor < 0.8:
            sidePanelClass = SidePanelTabGroupSmall
        else:
            sidePanelClass = SidePanelTabGroup
        self.leftPanelTabs = sidePanelClass(parent=self.overlayCont, align=uiconst.CENTERLEFT, top=-160, tabBtnData=tabBtnData, func=self.LeftPanelToggles, left=0, selectedTab=selectedTab, settingName='fittingLeftPanel')
        btns = self.leftPanelTabs.GetButtons()
        for eachBtnConfig, eachBtn in btns.iteritems():
            SetFittingTooltipInfo(eachBtn, eachBtnConfig)

        tabBtnData = [(GetByLabel('UI/Fitting/FittingWindow/StatsTab'),
          TAB_CONFIGNAME_STATS,
          'res:/UI/Texture/classes/Fitting/filterIconResources.png',
          pConst.UNIQUE_NAME_FITING_STATS)]
        selectedTab = GetCurrentRightPanelKey()
        self.rightPanelTabs = sidePanelClass(parent=self.overlayCont, align=uiconst.CENTERRIGHT, tabBtnData=tabBtnData, top=-140, func=self.ToggleRight, isOnRightOfContent=False, selectedTab=selectedTab, padRight=3, settingName='fittingRightPanel')
        btns = self.rightPanelTabs.GetButtons()
        for eachBtnConfig, eachBtn in btns.iteritems():
            SetFittingTooltipInfo(eachBtn, eachBtnConfig)

    def ToggleRight(self, configName, *args):
        currentlyExpaned = self.IsRightPanelExpanded()
        if currentlyExpaned:
            newValue = ''
        else:
            newValue = configName
        SetCurrentRightPanelKey(newValue)
        self._fixedWidth = self.GetWindowWidth()
        if currentlyExpaned:
            self.CollapseRightPanel()
        else:
            self.ExpandRightPanel()

    def CollapseRightPanel(self):
        self.rightPanelTabs.Disable()
        if self.IsUiScaled():
            self.rightPanel.opacity = 0.0
            self.width = self._fixedWidth
            self.rightPanel.width = 0
        else:
            uicore.animations.FadeTo(self.rightPanel, self.rightPanel.opacity, 0.0, duration=ANIM_DURATION, callback=self.rightPanel.Hide)
            uicore.animations.MorphScalar(self, 'width', self.width, self._fixedWidth, duration=ANIM_DURATION)
            uicore.animations.MorphScalar(self.rightPanel, 'width', self.rightPanel.width, 0, duration=ANIM_DURATION, sleep=True)
        self.rightPanelTabs.Enable()

    def ExpandRightPanel(self):
        self.rightPanelTabs.Disable()
        self.rightPanel.Show()
        if self.IsUiScaled():
            self.rightPanel.opacity = 1.0
            self.width = self._fixedWidth
            self.rightPanel.width = PANEL_WIDTH_RIGHT
        else:
            uicore.animations.FadeTo(self.rightPanel, self.rightPanel.opacity, 1.0, duration=4 * ANIM_DURATION)
            uicore.animations.MorphScalar(self, 'width', self.width, self._fixedWidth, duration=ANIM_DURATION)
            uicore.animations.MorphScalar(self.rightPanel, 'width', self.rightPanel.width, PANEL_WIDTH_RIGHT, duration=ANIM_DURATION, sleep=True)
        self.rightPanelTabs.Enable()

    def LeftPanelToggles(self, configName, *args):
        currentlyShowing = GetCurrentLeftPanelKey()
        newSelected = ''
        if currentlyShowing and not configName:
            SetCurrentLeftPanelKey(newSelected)
            self.ColllapseLeftPanel()
        elif configName in LEFT_TABS:
            newSelected = configName
            SetCurrentLeftPanelKey(newSelected)
            uthread.new(self.LoadLeftPanel, configName)
            if not currentlyShowing:
                self.ExpandLeftPanelTab(configName)

    def ColllapseLeftPanel(self):
        self.leftPanelTabs.Disable()
        self._fixedWidth = self.GetWindowWidth()
        leftPanelWidth = self.GetLeftPanelWidth()
        if self.IsUiScaled():
            self.leftPanelCont.opacity = 0.0
            self.leftPanel.Hide()
            self.width = self._fixedWidth
            self.left = self.left + leftPanelWidth
            self.leftPanelCont.width = 0
        else:
            uicore.animations.FadeTo(self.leftPanelCont, self.leftPanelCont.opacity, 0.0, duration=0.5 * ANIM_DURATION, callback=self.leftPanel.Hide)
            uicore.animations.MorphScalar(self, 'width', self.width, self._fixedWidth, duration=ANIM_DURATION)
            uicore.animations.MorphScalar(self, 'left', self.left, self.left + leftPanelWidth, duration=ANIM_DURATION)
            uicore.animations.MorphScalar(self.leftPanelCont, 'width', self.leftPanelCont.width, 0, duration=ANIM_DURATION, sleep=True)
        self.leftPanelTabs.Enable()

    def ExpandLeftPanelTab(self, configName):
        self.leftPanelTabs.Disable()
        self._fixedWidth = self.GetWindowWidth()
        leftPanelWidth = self.GetLeftPanelWidth()
        self.leftPanel.Show()
        if self.IsUiScaled():
            self.leftPanelCont.opacity = 1.0
            self.width = self._fixedWidth
            self.left = self.left - leftPanelWidth
            self.leftPanelCont.width = leftPanelWidth
        else:
            uicore.animations.FadeTo(self.leftPanelCont, self.leftPanelCont.opacity, 1.0, duration=4 * ANIM_DURATION)
            uicore.animations.MorphScalar(self, 'width', self.width, self._fixedWidth, duration=ANIM_DURATION)
            uicore.animations.MorphScalar(self, 'left', self.left, self.left - leftPanelWidth, duration=ANIM_DURATION)
            uicore.animations.MorphScalar(self.leftPanelCont, 'width', self.leftPanelCont.width, leftPanelWidth, duration=ANIM_DURATION, sleep=True)
        self.leftPanelTabs.Enable()

    def IsUiScaled(self):
        return uicore.desktop.dpiScaling != 1.0

    def GetWindowWidth(self):
        width = GetBaseShapeSize() * fontconst.fontSizeFactor + 8
        cosmeticTabSelected = hasattr(self, 'fittingModeTabGroup') and self.fittingModeTabGroup.GetSelectedID() == TAB_ID_COSMETIC
        if self.IsLeftPanelExpanded() or cosmeticTabSelected:
            width += self.GetLeftPanelWidth()
        if self.IsRightPanelExpanded() or cosmeticTabSelected:
            width += PANEL_WIDTH_RIGHT
        return width

    def OnSetDevice(self):
        if self.controller and self.controller.GetItemID():
            uthread.new(self.LoadWnd)

    def OnSessionChanged(self, *args):
        if self.destroyed:
            return
        if session.shipid:
            self.currentShipGhost.SetShipTypeID()

    def OnUIScalingChange(self, *args):
        if self.controller and self.controller.GetItemID():
            uthread.new(self.LoadWnd)

    def InitializeStatesAndPosition(self, *args, **kw):
        current = self.GetRegisteredPositionAndSize()
        default = self.GetDefaultSizeAndPosition()
        fixedHeight = self._fixedHeight
        fixedWidth = self.GetWindowWidth()
        Window.InitializeStatesAndPosition(self, *args, **kw)
        if fixedWidth is not None:
            self.width = fixedWidth
            self._fixedWidth = fixedWidth
        if fixedHeight is not None:
            self.height = fixedHeight
            self._fixedHeight = fixedHeight
        if list(default) == list(current)[:4]:
            settings.user.ui.Set('defaultFittingPosition', 1)
            dw = uicore.desktop.width
            dh = uicore.desktop.height
            self.left = (dw - self.width) / 2
            self.top = (dh - self.height) / 2

    def _OnClose(self, *args):
        settings.user.ui.Set('defaultFittingPosition', 0)

    def MouseDown(self, *args):
        uthread.new(uicore.registry.SetFocus, self)
        self.SetOrder(0)

    def PreviewFitItem(self, ghostItem = None, force = False):
        if not self.controller:
            return
        self.controller.SetPreviewFittedItem(ghostItem, force)

    def OnStartMinimize_(self, *args):
        sm.ChainEvent('ProcessFittingWindowStartMinimize')

    def OnEndMinimize_(self, *args):
        sm.ChainEvent('ProcessFittingWindowEndMinimize')

    def OnNewItem(self, *args):
        if not self.windowReady:
            return
        self.currentShipGhost.state = uiconst.UI_DISABLED
        self.currentShipGhost.EnableButtonWithDelay()
        self.currentShipGhost.SetShipTypeID()
        self.UpdateStats()
        self.UpdateShipName()

    def UpdateStatsOnSignal(self):
        uthread.new(self.UpdateStats)

    @lock_and_set_pending()
    def UpdateStats(self):
        if not self.windowReady or not self.controller.CurrentShipIsLoaded():
            return
        self.UpdateCPU()
        self.UpdatePower()
        self.ReloadDroneAndFighterIconsIfNeeded()
        self.UpdateSkillIcon()
        if getattr(self, 'warningIconCont', None):
            self.warningIconCont.UpdateIcon(self.controller)

    def ConstructPowerAndCpuLabels(self):
        powerGridAndCpuCont = LayoutGrid(name='powerGridAndCpuCont', parent=self.overlayCont, columns=1, state=uiconst.UI_PICKCHILDREN, align=uiconst.BOTTOMRIGHT, left=4)
        cpu_statustextHeader = EveLabelMediumBold(text=GetByLabel('UI/Fitting/FittingWindow/CPUStatusHeader'), name='cpu_statustextHeader', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        SetFittingTooltipInfo(targetObject=cpu_statustextHeader, tooltipName='CPU')
        powerGridAndCpuCont.AddCell(cpu_statustextHeader)
        self.cpu_statustext = EveLabelMedium(text='', name='cpu_statustext', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        SetFittingTooltipInfo(targetObject=self.cpu_statustext, tooltipName='CPU')
        cell = powerGridAndCpuCont.AddCell(self.cpu_statustext)
        self.cpu_warningFrame = self.BuildFrame(cpu_statustextHeader, cell)
        powerGridAndCpuCont.AddCell(cellObject=Container(name='spacer', align=uiconst.TOTOP, height=10))
        power_statustextHeader = EveLabelMediumBold(text=GetByLabel('UI/Fitting/FittingWindow/PowergridHeader'), name='power_statustextHeader', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        SetFittingTooltipInfo(targetObject=power_statustextHeader, tooltipName='PowerGrid')
        powerGridAndCpuCont.AddCell(power_statustextHeader)
        self.power_statustext = EveLabelMedium(text='', name='power_statustext', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        cell = powerGridAndCpuCont.AddCell(self.power_statustext)
        self.power_warningFrame = self.BuildFrame(power_statustextHeader, cell)
        SetFittingTooltipInfo(targetObject=self.power_statustext, tooltipName='PowerGrid')
        self.calibration_statustext = EveLabelMedium(text='', parent=self.overlayCont, name='calibrationstatustext', pos=(8, 54, 0, 0), state=uiconst.UI_NORMAL)
        SetFittingTooltipInfo(targetObject=self.calibration_statustext, tooltipName='Calibration')

    def BuildFrame(self, textAbove, cell):
        topPadding = -(textAbove.textheight + 3)
        f = Frame(parent=cell, frameConst=uiconst.FRAME_BORDER1_CORNER9, padding=(-6,
         topPadding,
         -6,
         -2))
        f.display = False
        return f

    def UpdateCPU(self):
        cpuLoadInfo = self.controller.GetCPULoad()
        cpuOutputInfo = self.controller.GetCPUOutput()
        cpuDiff = cpuOutputInfo.value - cpuLoadInfo.value
        coloredCpuLoadText = self._GetColoredDiffForCpuOrPower(cpuLoadInfo.isBetterThanBefore, cpuDiff)
        cpuOutputText = FmtAmt(cpuOutputInfo.value, showFraction=1)
        coloredCpuOutputText = GetColoredText(isBetter=cpuOutputInfo.isBetterThanBefore, text=cpuOutputText)
        self.SetCpuOrPowerLabel(self.cpu_statustext, cpuDiff, coloredCpuLoadText, coloredCpuOutputText)

    def UpdatePower(self):
        powerLoadInfo = self.controller.GetPowerLoad()
        powerOutputInfo = self.controller.GetPowerOutput()
        powerDiff = powerOutputInfo.value - powerLoadInfo.value
        coloredPowerLoadText = self._GetColoredDiffForCpuOrPower(powerLoadInfo.isBetterThanBefore, powerDiff)
        powerOutputText = FmtAmt(powerOutputInfo.value, showFraction=1)
        coloredPowerOutputText = GetColoredText(isBetter=powerOutputInfo.isBetterThanBefore, text=powerOutputText)
        self.SetCpuOrPowerLabel(self.power_statustext, powerDiff, coloredPowerLoadText, coloredPowerOutputText)

    def _GetColoredDiffForCpuOrPower(self, betterThanBefore, diff):
        loadText = FmtAmt(diff, showFraction=1)
        if betterThanBefore is None and diff < 0:
            betterThanBefore = False
        coloredCpuLoadText = GetColoredText(isBetter=betterThanBefore, text=loadText)
        return coloredCpuLoadText

    def SetCpuOrPowerLabel(self, labelObject, diff, loadText, outputText):
        labelObject.text = '%s/%s' % (loadText, outputText)
        if diff < 0:
            uicore.animations.FadeTo(labelObject.parent, 0.25, 1.0, duration=0.5, loops=uiconst.ANIM_REPEAT)
        else:
            labelObject.parent.StopAnimations()
            labelObject.parent.opacity = 1.0

    def OnFindTypeInList(self, typeID):
        self.TryExpandLeftSide()
        if GetCurrentLeftPanelKey() == TAB_CONFIGNAME_INVENTORY:
            self.invPanel.FindTypeInInventory(typeID)
        else:
            self.leftPanel.FindTypeInList(typeID)

    def OnFittingFlagFilterSet(self, flagID):
        self.TryExpandLeftSide()
        if GetCurrentLeftPanelKey() == TAB_CONFIGNAME_INVENTORY:
            self.invPanel.SetFlagFilter(flagID)
        else:
            self.leftPanel.SetFlagFilter(flagID)

    def TryExpandLeftSide(self):
        currentlyShowing = GetCurrentLeftPanelKey()
        if currentlyShowing not in (TAB_CONFIGNAME_BROWSER, TAB_CONFIGNAME_INVENTORY):
            btns = self.leftPanelTabs.GetButtons()
            browserBtn = btns.get(TAB_CONFIGNAME_BROWSER)
            if browserBtn:
                browserBtn.OnClick()

    def GetMenu(self, *args):
        m = Window.GetMenu(self, *args)
        m += [None]
        if session.role & (ROLE_GML | ROLE_WORLDMOD):
            m += [('Debug: Reset all search variables', self.ResetAllSearchVariables, ())]
            m += [('Debug: Clear resources dictionary', self.ClearResoureDict, ())]
            m += [('Debug: Reload ghostfitting DL', self.ReloadFittingDogmaLocation, ())]
        return m

    def ClearResoureDict(self):
        sm.GetService('fittingSvc').searchFittingHelper.ResetCpuAndPowergridDicts()

    def ResetAllSearchVariables(self):
        sm.GetService('fittingSvc').searchFittingHelper.ResetAllVariables()

    def ReloadFittingDogmaLocation(self):
        sm.GetService('ghostFittingSvc').ResetFittingDomaLocation(force=True)
        sm.GetService('fittingSvc').SetSimulationState(simulationOn=False)
        itemID = GetActiveShip()
        self.OnControllerChanging(itemID)

    def Close(self, setClosed = False, *args, **kwds):
        fittingSvc = sm.GetService('fittingSvc')
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        if fittingSvc.IsShipSimulated():
            if not ghostFittingSvc.ShouldContinueAfterAskingAboutSwitchingShips(msg='ExitSimulationWarning'):
                return
        with EatSignalChangingErrors(errorMsg='ghost fitting wnd'):
            if self.controller:
                self.ChangeSignalConnection(connect=False)
        try:
            ghostFittingSvc.ResetGhostFittingController()
            if self.controller:
                self.controller.Close()
        finally:
            Window.Close(self, setClosed, *args, **kwds)
            fittingSvc.SetSimulationState(False)
            ghostFittingSvc.ResetSimulationChangedFlag()

    def OpenFittingForCurrentShip(self, *args):
        sm.GetService('fittingSvc').DoSaveFitting()

    def ChangeWarningDisplay(self, warningModuleSlotDict, *args):
        for frame, warningID in ((self.cpu_warningFrame, -WARNING_OVER_CPU), (self.power_warningFrame, -WARNING_OVER_POWERGRID)):
            warningLevel = warningModuleSlotDict.get(warningID, None)
            if warningLevel:
                color = GetColorForLevel(warningLevel)
                frame.display = True
                frame.SetRGBA(*color)
            else:
                frame.display = False

    def OnBack(self):
        if GetCurrentLeftPanelKey() == TAB_CONFIGNAME_INVENTORY:
            self.invPanel.OnBack()

    def OnForward(self):
        if GetCurrentLeftPanelKey() == TAB_CONFIGNAME_INVENTORY:
            self.invPanel.OnForward()

    def _on_content_padding_changed(self, window):
        if self.cosmeticsPanel:
            self.cosmeticsPanel.AdjustErrorScreenPadding(self.content_padding)
        if self._left_side_fill is not None:
            self._left_side_fill.padding = self._get_left_side_fill_padding()

    def _get_left_side_fill_padding(self):
        pad_left, pad_top, _, pad_bottom = self.content_padding
        return (-pad_left,
         -pad_top,
         0,
         -pad_bottom)


def GetFixedWndHeight(controller):
    if GetScaleFactor() > 0.85:
        normalHeight = WND_NORMAL_HEIGHT_BIG
    else:
        normalHeight = WND_NORMAL_HEIGHT_SMALL
    baseSize = GetBaseShapeSize()
    if controller.ControllerForCategory() == const.categoryStructure:
        return max(baseSize + 85, normalHeight)
    return normalHeight


def GetOverlayWidthHeightAndAlignment(controller):
    fixedHeight = GetFixedWndHeight(controller)
    baseSize = GetBaseShapeSize()
    if controller.ControllerForCategory() == const.categoryStructure:
        width = baseSize * fontconst.fontSizeFactor - 28
        height = min(fixedHeight - 12, baseSize)
        overlayAlignment = uiconst.CENTERTOP
    else:
        height = 0
        width = 0
        overlayAlignment = uiconst.TOALL
    return (width, height, overlayAlignment)
