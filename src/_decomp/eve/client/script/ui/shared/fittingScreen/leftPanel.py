#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\leftPanel.py
from collections import Counter
import eveicon
import eveui
import uthread
import uthread2
from carbonui import AxisAlignment, Density, fontconst
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.button.menu import MenuButton
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.frame import Frame
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
import carbonui.const as uiconst
from eve.client.script.ui.shared.fittingScreen.browsers.browserUtil import AUTO_FITTED_SERVICES_BY_STRUCTURE_TYPE, GetScrollListFromTypeList
from eve.client.script.ui.shared.fittingScreen.browsers.filtering import GetValidModuleTypeIDs
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from eve.client.script.ui.shared.fittingScreen.resourceBtnTooltip import LoadFilterBtnTooltipPanel
from eve.client.script.ui.shared.fittingScreen.skillRequirements import GetAllTypeIDsMissingSkillsForShipAndContent, CopyAllSkills
from eveexceptions import UserError
from shipfitting.fittingDogmaLocationUtil import GetHardware
from eve.client.script.ui.shared.export import ImportLegacyFittingsWindow, ImportFittingsWindow, ExportFittingsWindow
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from eve.client.script.ui.shared.fittingScreen import BROWSE_MODULES, BROWSE_CHARGES, BROWSER_SEARCH_CHARGE, BROWSE_FITTINGS, BROWSE_HARDWARE, HW_BTN_ID_CONFIG, BROWSER_BTN_ID_CONFIG, BTN_TYPE_PERSONAL_FITTINGS, BTN_TYPE_CORP_FITTINGS, BTN_TYPE_ALLIANCE_FITTINGS, BTN_TYPE_RIGSLOT, BTN_TYPE_COMMUNITY_FITTINGS
from eve.client.script.ui.shared.fittingScreen.browsers.chargesBrowserUtil import ChargeBrowserListProvider, GetValidChargeTypeIDs, GetValidSpecialAssetsChargeTypeIDs
from eve.client.script.ui.shared.fittingScreen.browsers.fittingBrowser import FittingBrowserListProvider
from eve.client.script.ui.shared.fittingScreen.browsers.hardwareBrowser import HardwareBrowserListProvider
from eve.client.script.ui.shared.fittingScreen.browsers.searchBrowser import SearchBrowserListProvider, SearchBrowserListProviderCharges
from eve.client.script.ui.shared.fittingScreen.filterBtn import AddFittingFilterButtons, AddHardwareButtons, SetSettingForFilterBtns, BTN_TYPE_RESOURCES, ChangeFilterBtnsStatesSlots
from eve.client.script.ui.shared.fittingScreen.fittingPanels.chargeButtons import ModuleChargeController, ModuleChargeRadioButton
from eve.client.script.ui.shared.fittingScreen.missingItemsPopup import OpenBuyAllBox
from eve.client.script.ui.shared.fittingScreen.searchCont import SearchCont, FITTING_MODE, HARDWARE_MODE, CHARGE_MODE
from eve.client.script.ui.shared.fittingScreen.settingUtil import IsChargeTabSelected, IsHardwareTabSelected, IsModuleTabSelected, IsFittingAndHullsSelected, GetOnlyCurrentShipSetting, GetHwTabSelected, GetBrowserBtnSelected, HardwareFiltersSettingObject, IsBrowserSelected
from eve.client.script.ui.shared.fittingMgmtWindow import FittingMgmt, OpenOrLoadMultiFitWnd
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from signals.signalUtil import ChangeSignalConnect
from eve.common.script.sys.eveCfg import GetActiveShip, IsDocked
import evetypes
import inventorycommon.typeHelpers
from inventorycommon.util import IsModularShip
from localization import GetByLabel, GetByMessageID
import telemetry
from carbonui.uicore import uicore
from eve.common.lib import appConst as const

class LeftPanel(Container):
    default_clipChildren = True
    __notifyevents__ = ['OnFittingsUpdated',
     'OnFittingDeleted',
     'OnSkillFilteringUpdated',
     'OnSessionChanged']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.fittingSvc = sm.GetService('fittingSvc')
        self.ghostFittingSvc = sm.GetService('ghostFittingSvc')
        self.configName = attributes.configName
        self.controller = attributes.controller
        self.ChangeSignalConnection()
        self.loaded = False
        self.refreshRequired = False
        self.ammoShowingForType = None
        self.loadHardwareThread = None
        self.pendingHardwareLoad = False
        self.hwSettingObject = HardwareFiltersSettingObject()
        btnCont = ButtonGroup(parent=self, align=uiconst.TOBOTTOM, padding=(0, 8, 0, 0), button_alignment=AxisAlignment.START, button_size_mode=ButtonSizeMode.DYNAMIC)
        self.fitBtn = Button(parent=btnCont, label=GetByLabel('UI/Fitting/FittingWindow/FitShip'), func=self.FitShip)
        SetFittingTooltipInfo(targetObject=self.fitBtn, tooltipName='FitShip')
        self.builtShipBtn = Button(parent=btnCont, label=GetByLabel('UI/Fitting/FittingWindow/BuildShip'), func=self.BuildShip)
        SetFittingTooltipInfo(targetObject=self.builtShipBtn, tooltipName='BuildFitShip')
        self.saveBtn = Button(parent=btnCont, label=GetByLabel('UI/Fitting/FittingWindow/SaveFitAs'), func=self.SaveFitting)
        SetFittingTooltipInfo(targetObject=self.saveBtn, tooltipName='SaveFitting')
        Button(parent=btnCont, label=GetByLabel('UI/Fitting/FittingWindow/Browse'), hint=GetByLabel('UI/Fitting/FittingWindow/BrowseTooltip'), func=self.LoadFittingSetup)
        self.AdjustButtons()
        self.AddExportImportMenu(btnCont)
        self.btnGroup = ToggleButtonGroup(name='fittingToggleBtnGroup', parent=self, align=uiconst.TOTOP, callback=self.BrowserSelectedBtnClicked, density=Density.COMPACT)
        self.AddSearchFields()
        self.AddFilterCont()
        self.hwBrowserBtns = self.AddHardwareSelcetionCont()
        self.AddFittingFilterButtons()
        self.hardwareFilterBtns = self.AddHardwareFilterButtons()
        self.AddChargeFilterButtons()
        self.browserBtns = {}
        self.moduleChargeButtons = {}
        for btnID, labelPath, uniqueName in ((BROWSE_FITTINGS, 'UI/Fitting/FittingWindow/ShipAndFittings', pConst.UNIQUE_NAME_FITS_IN_FITTING_WND), (BROWSE_HARDWARE, 'UI/Fitting/FittingWindow/Hardware', pConst.UNIQUE_NAME_FITTING_HARDWARE)):
            btn = self.btnGroup.AddButton(btnID, GetByLabel(labelPath), fontSize=fontconst.EVE_MEDIUM_FONTSIZE, uniqueUiName=uniqueName)
            SetFittingTooltipInfo(targetObject=btn, tooltipName='%s_btn' % btnID)
            self.browserBtns[btnID] = btn

        self.scroll = Scroll(parent=self, align=uiconst.TOALL, padTop=2)
        self.scroll.sr.content.OnDropData = self.OnDropData
        sm.RegisterNotify(self)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_new_itemID, self.OnSimulatedShipLoaded),
         (self.controller.on_slots_changed, self.OnSlotsChanged),
         (self.controller.on_simulation_state_changed, self.OnSimulationStateChanged),
         (self.controller.on_subsystem_really_changed, self.OnSubsystemReallyChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def AddExportImportMenu(self, parent):
        MenuButton(parent=parent, hint=GetByLabel('UI/Fitting/FittingWindow/ImportAndExport'), texturePath=eveicon.export, get_menu_func=self._get_import_export_menu)

    def _get_import_export_menu(self):
        menu = MenuData()
        menu.AddEntry(text=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ImportFromClipboard'), hint=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ImportFromClipboardHint'), func=self._paste_fitting_from_clipboard)
        menu.AddEntry(text=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ExportToClipboard'), hint=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ExportToClipboardHint'), func=self._copy_fitting_to_clipboard)
        menu.AddSeparator()
        menu.AddEntry(text=GetByLabel('UI/Fitting/FittingWindow/ImportFromFile'), func=self.ImportFittings)
        menu.AddEntry(text=GetByLabel('UI/Fitting/FittingWindow/ExportToFile'), func=self.ExportFittings)
        menu.AddSeparator()
        menu.AddEntry(text=GetByLabel('UI/Fitting/FittingWindow/CopyAllSkills'), func=self.CopyAllSkills)
        return menu

    def ImportFittings(self, *args):
        ImportFittingsWindow.Open()

    def ExportFittings(self, *args):
        ExportFittingsWindow.Open(ownerID=session.charid)

    def _paste_fitting_from_clipboard(self):
        fitting_service = sm.GetService('fittingSvc')
        fitting_service.ImportFittingFromClipboard()

    def _copy_fitting_to_clipboard(self):
        fitting_service = sm.GetService('fittingSvc')
        fitting = fitting_service.GetFittingForCurrentInWnd()
        fitting_service.ExportFittingToClipboard(fitting, False)

    def CopyAllSkills(self):
        allTypeIDs = GetAllTypeIDsMissingSkillsForShipAndContent(self.controller.dogmaLocation)
        CopyAllSkills(allTypeIDs)

    def Load(self):
        if self.loaded:
            if self.refreshRequired and IsHardwareTabSelected():
                self.LoadHardware()
            return
        if IsHardwareTabSelected():
            hwTabSelected = GetHwTabSelected()
            self.hardwareBtnGroup.SelectByID(hwTabSelected)
        browserBtnSelected = GetBrowserBtnSelected()
        self.btnGroup.SelectByID(browserBtnSelected)
        self.loaded = True

    @telemetry.ZONE_METHOD
    def AddSearchFields(self):
        self.searchparent = SearchCont(name='searchparent', parent=self, align=uiconst.TOTOP, top=4, searchFunc=self.Search, collapseFunc=self.CollapseGroups)

    @eveui.skip_if_destroyed
    def ReloadBrowser(self):
        btnID = GetBrowserBtnSelected()
        self.BrowserSelected(btnID, scrollToPos=True)

    def SetFlagFilter(self, flagID, *args):
        SetSettingForFilterBtns(flagID, self.hardwareFilterBtns)
        self.SwitchToHardwareBrowsers()
        self.ReloadBrowser()

    def SwitchToHardwareBrowsers(self):
        btn = self.browserBtns.get(BROWSE_HARDWARE)
        if not btn.IsSelected():
            btn.OnClick()
        hwBtn = self.hwBrowserBtns.get(BROWSE_MODULES)
        if hwBtn.IsSelected():
            self.ReloadBrowser()
        else:
            hwBtn.OnClick()

    def BrowserSelectedBtnClicked(self, btnID, *args):
        return self.BrowserSelected(btnID)

    @telemetry.ZONE_METHOD
    def BrowserSelected(self, btnID, scrollToPos = False):
        settings.user.ui.Set(BROWSER_BTN_ID_CONFIG, btnID)
        if btnID == BROWSE_FITTINGS:
            self.chargeFilterCont.display = False
            self.hardwareFilterCont.display = False
            self.hardwarSelectionCont.display = False
            self.searchparent.ChangeSearchMode(FITTING_MODE)
            self.ShowOrHideElements(display=False)
            uthread.new(self.LoadFittingsAndShips, scrollToPos)
        elif btnID == BROWSE_HARDWARE:
            self.hardwarSelectionCont.display = True
            self.AddHardwareForChargesButtons()
            self.ShowOrHideElements(display=True)
            self.LoadHardware()

    def ShowOrHideElements(self, display = True):
        self.hardwareFilterCont.display = display
        self.fittingFilterCont.display = not display
        self.fittingFilterCont.display = not display

    def OnFittingDeleted(self, ownerID, fitID):
        self.OnFittingsUpdated()

    def OnFittingsUpdated(self, fitting = None):
        if IsFittingAndHullsSelected():
            self.ReloadBrowser()

    def OnSkillFilteringUpdated(self):
        if IsHardwareTabSelected():
            self.ReloadBrowser()

    def LoadFittingsAndShips(self, scrollToPos = False):
        if not IsFittingAndHullsSelected():
            return
        pos = self.scroll.GetScrollProportion()
        self.scroll.Load(contentList=[], scrolltotop=0)
        self.scroll.ShowLoading()
        try:
            scrolllist = self.GetFittingScrolllist()
            if scrolllist is None:
                return
            self.searchparent.display = True
            self.scroll.Load(contentList=scrolllist)
            if scrollToPos and pos:
                self.scroll.ScrollToProportion(pos)
        finally:
            self.scroll.HideLoading()

    @telemetry.ZONE_METHOD
    def LoadHardware(self, scrollToPos = False):
        if self.destroyed:
            return
        if not IsBrowserSelected():
            self.refreshRequired = True
            return
        self.refreshRequired = False
        self.scroll.HideLoading()
        self.chargeFilterCont.display = False
        self.hardwareFilterCont.display = False
        if IsHardwareTabSelected() and IsChargeTabSelected():
            self.searchparent.ChangeSearchMode(CHARGE_MODE)
            self.AddHardwareForChargesButtons()
            self.LoadChargesScrollList()
            return
        self.searchparent.ChangeSearchMode(HARDWARE_MODE)
        self.hardwareBtnGroup.SetSelectedByID(BROWSE_MODULES)
        self.hardwareFilterCont.display = True
        self.ChangeResourceBtn()
        self.pendingHardwareLoad = True
        hardwareThreadIsRunning = self.IsHardwareThreadRunning()
        if not hardwareThreadIsRunning:
            self.loadHardwareThread = uthread.new(self.LoadHardware_thread, scrollToPos)

    def IsHardwareThreadRunning(self):
        hardwareThreadIsRunning = self.loadHardwareThread and self.loadHardwareThread.alive
        return hardwareThreadIsRunning

    @telemetry.ZONE_METHOD
    def LoadHardware_thread(self, scrollToPos = False):
        self.pendingHardwareLoad = False
        pos = self.scroll.GetScrollProportion()
        self.scroll.Load(contentList=[])
        self.scroll.ShowLoading()
        resourceBtn = None
        if self.hwSettingObject.GetHwResourcesSetting():
            resourceBtn = self.hardwareFilterBtns.get(BTN_TYPE_RESOURCES, None)
            if resourceBtn:
                resourceBtn.ShowLoading()
        scrolllist = self._GetHardwareScrollList()
        if IsModuleTabSelected() and IsHardwareTabSelected():
            self.scroll.Load(contentList=scrolllist, scrolltotop=0, noContentHint=GetByLabel('UI/Fitting/FittingWindow/NoModulesFound'))
        self.scroll.HideLoading()
        if scrollToPos:
            self.scroll.ScrollToProportion(pos)
        if resourceBtn:
            resourceBtn.HideLoading()
        if self.pendingHardwareLoad:
            self.LoadHardware_thread()

    def _GetHardwareScrollList(self):
        if self.hwSettingObject.GetTextFilter():
            scrolllist = self.GetSearchResults()
        else:
            hardwareBrowserListProvider = HardwareBrowserListProvider(self.fittingSvc.searchFittingHelper, self.OnDropData, bannedMarketGroups=[const.marketGroupMutaplasmids], hwSettingObject=self.hwSettingObject)
            scrolllist = hardwareBrowserListProvider.GetGroupListForBrowse(marketGroupID=const.marketCategoryShipEquipment)
            scrolllist += hardwareBrowserListProvider.GetGroupListForBrowse(marketGroupID=const.marketCategoryShipModifications)
            scrolllist += self.GetDroneGroup(hardwareBrowserListProvider)
            scrolllist += self.GetStructureGroup()
            specialAssetHardwareListProvider = HardwareBrowserListProvider(self.fittingSvc.searchFittingHelper, self.OnDropData, GetValidModuleTypeIDs, hwSettingObject=self.hwSettingObject)
            specialScrollList = specialAssetHardwareListProvider.GetGroupListForBrowse(marketGroupID=const.marketCategorySpecialEditionAssets)
            scrolllist += specialScrollList
        return scrolllist

    def GetDroneGroup(self, hardwareBrowserListProvider):
        droneScrolllist = hardwareBrowserListProvider.GetGroupListForBrowse(marketGroupID=const.marketCategoryDrones, sublevel=1)
        if not droneScrolllist:
            return []
        typeIDs = set()
        for eachNode in droneScrolllist:
            if eachNode.typeIDs:
                typeIDs.update(eachNode.typeIDs)

        return [GetFromClass(ListGroup, {'GetSubContent': self.GetDroneGroupSubContent,
          'label': GetByLabel('UI/Drones/Drones'),
          'id': ('ghostfitting_group', 'drones'),
          'showlen': 0,
          'sublevel': 0,
          'showicon': 'ui_11_64_16',
          'state': 'locked',
          'BlockOpenWindow': True,
          'droneScrolllist': droneScrolllist,
          'hint': GetByMessageID(64514),
          'typeIDs': typeIDs})]

    def GetDroneGroupSubContent(self, nodedata, *args):
        return nodedata.droneScrolllist

    def GetStructureGroup(self):
        hardwareBrowserListProvider = HardwareBrowserListProvider(self.fittingSvc.searchFittingHelper, self.OnDropData, hwSettingObject=self.hwSettingObject)
        structureScrolllist = hardwareBrowserListProvider.GetGroupListForBrowse(marketGroupID=const.marketCategoryStructureEquipment, sublevel=1)
        structureScrolllist += hardwareBrowserListProvider.GetGroupListForBrowse(marketGroupID=const.marketCategoryStructureModifications, sublevel=1)
        structureScrolllist += self.GetAutoFittedServiceModulesGroup()
        if not structureScrolllist:
            return []
        typeIDs = set()
        for eachNode in structureScrolllist:
            if eachNode.typeIDs:
                typeIDs.update(eachNode.typeIDs)

        return [GetFromClass(ListGroup, {'GetSubContent': self.GetStructureGroupSubContent,
          'label': GetByLabel('UI/Common/LocationTypes/Structures'),
          'id': ('ghostfitting_group', 'structure'),
          'showlen': 0,
          'sublevel': 0,
          'showicon': 'ui_40_64_14',
          'state': 'locked',
          'BlockOpenWindow': True,
          'structureScrolllist': structureScrolllist,
          'typeIDs': typeIDs})]

    def GetStructureGroupSubContent(self, nodedata, *args):
        return nodedata.structureScrolllist

    def GetAutoFittedServiceModulesGroup(self):
        validTypeIDs = GetValidModuleTypeIDs(AUTO_FITTED_SERVICES_BY_STRUCTURE_TYPE.values(), self.fittingSvc.searchFittingHelper)
        scrollList = GetScrollListFromTypeList(validTypeIDs, 1, self.OnDropData)
        if not scrollList:
            return []
        return [GetFromClass(ListGroup, {'GetSubContent': self.GetAutoFittedSubContent,
          'label': GetByLabel('UI/Fitting/FittingWindow/AutoFittedServiceModule'),
          'id': ('ghostfitting_group', 'autoFittedModules'),
          'showlen': 0,
          'sublevel': 1,
          'showicon': 'ui_40_64_14',
          'state': 'locked',
          'BlockOpenWindow': True,
          'serviceScrollList': scrollList,
          'typeIDs': validTypeIDs})]

    def GetAutoFittedSubContent(self, nodedata, *args):
        return nodedata.serviceScrollList

    def ExitSimulation(self, *args):
        sm.GetService('fittingSvc').SetSimulationState(False)
        shipID = GetActiveShip()
        self.ghostFittingSvc.SendOnSimulatedShipLoadedEvent(shipID, None)

    def LoadCurrentShip(self, *args):
        self.ghostFittingSvc.LoadCurrentShip()

    def SaveFitting(self, *args):
        name = self.ghostFittingSvc.GetShipName()
        return self.fittingSvc.DoSaveFitting(name=name)

    def FitShip(self, *args):
        fittingSvc = sm.GetService('fittingSvc')
        if not fittingSvc.IsShipSimulated():
            return
        clientDL = sm.GetService('clientDogmaIM').GetDogmaLocation()
        fittingDL = sm.GetService('clientDogmaIM').GetFittingDogmaLocation()
        actualShip = clientDL.GetShip()
        simulatedShip = fittingDL.GetShip()
        if actualShip.typeID != simulatedShip.typeID:
            UserError('CustomNotify', {'notify': "Actual ship and simulated ship don't match"})
        fitting = fittingSvc.GetFittingForCurrentInWnd(putModuleAmmoInCargo=False)
        failedToLoad = fittingSvc.LoadFitting(fitting, getFailedDict=True) or {}
        failedToLoadCounter = Counter({x[0]:x[1] for x in failedToLoad})
        simulated_chargeTypesAndQtyByFlagID = fittingSvc.GetChargesAndQtyByFlag(simulatedShip.GetFittedItems().values())
        ammoFailedToLoad = fittingSvc.RemoveAndLoadChargesFromSimulatedShip(clientDL, actualShip.itemID, simulated_chargeTypesAndQtyByFlagID)
        faildToLoadInfo = failedToLoadCounter + Counter(ammoFailedToLoad)
        if faildToLoadInfo:
            OpenBuyAllBox(faildToLoadInfo, fitting)
        else:
            self.ghostFittingSvc.TryExitSimulation(askQuestion=False)

    def BuildShip(self, *args):
        fitting = sm.GetService('fittingSvc').GetFittingForCurrentInWnd()
        if not fitting.fitData:
            eve.Message('uiwarning03')
            return
        wnd = OpenOrLoadMultiFitWnd(fitting)
        wnd.Maximize()

    def GetFittingScrolllist(self, *args):
        fittingListProvider = FittingBrowserListProvider(self.OnDropData)
        ship = self.controller.dogmaLocation.GetShip()
        return fittingListProvider.GetFittingScrolllist(ship.typeID)

    @telemetry.ZONE_METHOD
    def Search(self, settingConfig, searchString):
        settings.user.ui.Set(settingConfig, searchString)
        self.ReloadBrowser()

    def CollapseGroups(self, *args):
        self.scroll.CollapseAll()

    def LoadFittingSetup(self, *args):
        if sm.GetService('fittingSvc').HasLegacyClientFittings():
            wnd = ImportLegacyFittingsWindow.Open()
        else:
            wnd = FittingMgmt.Open()
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()

    def OnSessionChanged(self, isRemote, sess, change):
        if 'shipid' in change or 'solarsystemid' in change or 'structureid' in change:
            uthread2.call_after_wallclocktime_delay(self.AdjustButtons, 0.5)

    @eveui.skip_if_destroyed
    def OnSimulatedShipLoaded(self, *args):
        self.AdjustButtons()
        self.ReloadBrowser()

    def AdjustButtons(self):
        self._SetBtnStates()
        self.fitBtn.display = False
        self.builtShipBtn.display = False
        if self.controller.IsSimulated():
            if self.ghostFittingSvc.IsSimulatingCurrentShipType():
                self.fitBtn.display = True
            else:
                self.builtShipBtn.display = True

    def ReloadFittingsIfNeeded(self):
        if IsFittingAndHullsSelected() and GetOnlyCurrentShipSetting():
            self.ReloadBrowser()

    def _SetBtnStates(self):
        shipItem = self.controller.dogmaLocation.GetShipItem()
        if shipItem is None:
            return
        shipTypeID = shipItem.typeID
        self.fitBtn.Disable()
        self.builtShipBtn.Disable()
        if IsDocked():
            self.fitBtn.Enable()
            if evetypes.GetCategoryID(shipTypeID) != const.categoryStructure:
                self.builtShipBtn.Enable()

    @telemetry.ZONE_METHOD
    def AddHardwareForChargesButtons(self):
        if self.destroyed:
            return
        self.chargeFilterCont.display = True
        self.hardwareFilterCont.display = False
        self.chargeFilterCont.Flush()
        hardware = self.GetHardware()
        self.moduleChargeButtons.clear()
        infoSvc = sm.GetService('info')
        currentlySelectedTypeID = self.chargeBtnController.GetSelectModuleTypeID()
        if currentlySelectedTypeID not in hardware:
            self.chargeBtnController.ResetSelected()
        for moduleTypeID in hardware:
            chargeTypeIDs = infoSvc.GetUsedWithTypeIDs(moduleTypeID)
            if not chargeTypeIDs:
                continue
            moduleName = evetypes.GetName(moduleTypeID)
            cont = ModuleChargeRadioButton(parent=self.chargeFilterCont, pos=(0, 0, 32, 32), align=uiconst.NOALIGN, state=uiconst.UI_NORMAL, typeID=moduleTypeID, usedWithChargesIDs=chargeTypeIDs, controller=self.chargeBtnController, isSelected=moduleTypeID == currentlySelectedTypeID)
            cont.hint = moduleName
            self.moduleChargeButtons[moduleTypeID] = cont

        if IsChargeTabSelected():
            self.LoadChargesScrollList()

    def LoadChargesScrollList(self, *args):
        if self.destroyed:
            return
        chargeTypeIDs = self.chargeBtnController.GetUsedWithForSelectedModule()
        if chargeTypeIDs:
            moduleTypeID = self.chargeBtnController.GetSelectModuleTypeID()
            provider = ChargeBrowserListProvider(dblClickFunc=self.TryFit, onDropDataFunc=self.OnDropData, reloadFunc=self.ReloadBrowser)
            validChargeTypeIDs = GetValidChargeTypeIDs(chargeTypeIDs, self.fittingSvc.searchFittingHelper)
            scrolllist = provider.GetChargesScrollList(moduleTypeID, validChargeTypeIDs)
        elif settings.user.ui.Get(BROWSER_SEARCH_CHARGE, ''):
            scrolllist = self.GetSearchChargeResults()
        else:
            hardwareBrowserListProvider = HardwareBrowserListProvider(self.fittingSvc.searchFittingHelper, self.OnDropData, GetValidChargeTypeIDs, hwSettingObject=self.hwSettingObject)
            scrolllist = hardwareBrowserListProvider.GetGroupListForBrowse(marketGroupID=const.marketCategoryAmmunitionAndCharges)
            specialChargeListProvider = HardwareBrowserListProvider(self.fittingSvc.searchFittingHelper, self.OnDropData, GetValidSpecialAssetsChargeTypeIDs, hwSettingObject=self.hwSettingObject)
            scrolllist += specialChargeListProvider.GetGroupListForBrowse(marketGroupID=const.marketCategorySpecialEditionAssets)
        self.scroll.Load(contentList=scrolllist, noContentHint=GetByLabel('UI/Fitting/FittingWindow/NoChargesFound'))

    def TryFit(self, entry, moduleTypeID, ammoTypeID):
        self.ghostFittingSvc.TryFitAmmoTypeToAll(moduleTypeID, ammoTypeID)

    def GetHardware(self):
        dogmaLocation = self.controller.GetDogmaLocation()
        return GetHardware(dogmaLocation)

    def OnSlotsChanged(self):
        if not IsHardwareTabSelected():
            return
        if IsChargeTabSelected():
            self.AddHardwareForChargesButtons()
        if IsModuleTabSelected() and self.controller.IsSimulated():
            if not self.controller.GetPreviewFittedItem() and self.hwSettingObject.GetHwResourcesSettingResourcesLeftActive():
                self.LoadHardware(scrollToPos=True)

    def OnSubsystemReallyChanged(self, *args):
        if self.hwSettingObject.GetHwShipCanUseSetting():
            self.ReloadBrowser()

    def OnSimulationStateChanged(self):
        if IsModuleTabSelected() and IsHardwareTabSelected() and self.hwSettingObject.GetHwResourcesSetting():
            self.LoadHardware()
        self.ChangeResourceBtn()

    def OnDropData(self, dragObj, nodes):
        node = nodes[0]
        itemKey = getattr(node, 'itemID', None)
        if itemKey is None:
            return
        self.ghostFittingSvc.UnfitModule(itemKey)
        self.ghostFittingSvc.SendFittingSlotsChangedEvent()

    @telemetry.ZONE_METHOD
    def AddFilterCont(self):
        self.filterCont = ContainerAutoSize(name='filterCont', parent=self, align=uiconst.TOTOP, padding=(0, 0, 0, 0))

    @telemetry.ZONE_METHOD
    def AddHardwareSelcetionCont(self):
        self.hardwarSelectionCont = ContainerAutoSize(name='hardwarSelectionCont', parent=self, align=uiconst.TOTOP, padding=(0, 4, 0, 4))
        btnDict = {}
        self.hardwareBtnGroup = ToggleButtonGroup(name='fittingToggleBtnGroup', parent=self.hardwarSelectionCont, align=uiconst.TOTOP, callback=self.ChangeHardwareGroupSelected, density=Density.COMPACT)
        for btnID, label in ((BROWSE_MODULES, 'UI/Fitting/FittingWindow/Modules'), (BROWSE_CHARGES, 'UI/Fitting/FittingWindow/Charges')):
            btn = self.hardwareBtnGroup.AddButton(btnID, GetByLabel(label))
            SetFittingTooltipInfo(targetObject=btn, tooltipName='%s_btn' % btnID)
            btnDict[btnID] = btn

        return btnDict

    def ChangeHardwareGroupSelected(self, btnID, *args):
        settings.user.ui.Set(HW_BTN_ID_CONFIG, btnID)
        self.LoadHardware()

    @telemetry.ZONE_METHOD
    def AddHardwareFilterButtons(self):
        self.hardwareFilterCont = FlowContainer(name='hardwareFilterCont', parent=self.filterCont, align=uiconst.TOTOP, top=4, contentSpacing=uiconst.BUTTONGROUPMARGIN)
        return AddHardwareButtons(self.hardwareFilterCont, self.HardwareFilterClicked, hintFunc=self.LoadFilterBtnTooltipPanel)

    @telemetry.ZONE_METHOD
    def AddChargeFilterButtons(self):
        settingName = self.hwSettingObject.GetChargeSettingName()
        self.chargeBtnController = ModuleChargeController(settingName)
        self.chargeBtnController.on_selected_changed.connect(self.LoadChargesScrollList)
        self.chargeFilterCont = FlowContainer(name='chargeFilterCont', parent=self.filterCont, align=uiconst.TOTOP, padTop=4, contentSpacing=uiconst.BUTTONGROUPMARGIN)

    @telemetry.ZONE_METHOD
    def AddFittingFilterButtons(self):
        self.fittingFilterCont = FlowContainer(name='fittingFilterCont', parent=self.filterCont, align=uiconst.TOTOP, top=4, contentSpacing=uiconst.BUTTONGROUPMARGIN)
        btnDict = AddFittingFilterButtons(self.fittingFilterCont, self.FittingFilterClicked, hintFunc=self.LoadFilterBtnTooltipPanel)
        if BTN_TYPE_CORP_FITTINGS in btnDict:
            btnDict[BTN_TYPE_CORP_FITTINGS].uniqueUiName = pConst.UNIQUE_NAME_CORP_FIT_FILTER
        if BTN_TYPE_ALLIANCE_FITTINGS in btnDict:
            btnDict[BTN_TYPE_ALLIANCE_FITTINGS].uniqueUiName = pConst.UNIQUE_NAME_ALLIANCE_FIT_FILTER
        if BTN_TYPE_COMMUNITY_FITTINGS in btnDict:
            btnDict[BTN_TYPE_COMMUNITY_FITTINGS].uniqueUiName = pConst.UNIQUE_NAME_COMMUNITY_FIT_FILTER

    def FittingFilterClicked(self, filterBtn, buttonType):
        self.FilterButtonClicked(filterBtn)
        self.LoadFittingsAndShips()

    def HardwareFilterClicked(self, filterBtn, buttonType):
        self.FilterButtonClicked(filterBtn)
        self.LoadHardware()

    def LoadFilterBtnTooltipPanel(self, tooltipPanel, filterBtn):
        if filterBtn.buttonType not in (BTN_TYPE_RESOURCES,
         BTN_TYPE_PERSONAL_FITTINGS,
         BTN_TYPE_CORP_FITTINGS,
         BTN_TYPE_ALLIANCE_FITTINGS):
            return
        hintText = None
        if filterBtn.buttonType == BTN_TYPE_RESOURCES:
            isSimulated = self.controller.IsSimulated()
            LoadFilterBtnTooltipPanel(tooltipPanel, filterBtn.hintLabelPath, self.hwSettingObject, self.LoadHardware, isSimulated)
            return
        if filterBtn.buttonType == BTN_TYPE_PERSONAL_FITTINGS:
            personalFittings = self.fittingSvc.GetFittings(session.charid)
            numFittings = '(%s/%s)' % (len(personalFittings), const.maxCharFittings)
            hintText = GetByLabel(filterBtn.hintLabelPath, numFittings=numFittings)
        elif filterBtn.buttonType == BTN_TYPE_CORP_FITTINGS:
            corpFittings = self.fittingSvc.GetFittings(session.corpid)
            numFittings = '(%s/%s)' % (len(corpFittings), const.maxCorpFittings)
            hintText = GetByLabel(filterBtn.hintLabelPath, numFittings=numFittings)
        elif session.allianceid and filterBtn.buttonType == BTN_TYPE_ALLIANCE_FITTINGS:
            allianceFittings = self.fittingSvc.GetFittings(session.allianceid)
            numFittings = '(%s/%s)' % (len(allianceFittings), const.maxAllianceFittings)
            hintText = GetByLabel(filterBtn.hintLabelPath, numFittings=numFittings)
        if hintText:
            tooltipPanel.LoadGeneric1ColumnTemplate()
            tooltipPanel.AddLabelMedium(text=hintText, wrapWidth=200)

    def ToggleHardwareSetting(self, *args):
        currentValue = self.hwSettingObject.GetFilterModeForResource()
        newValue = not currentValue
        self.hwSettingObject.SetFilterModeForResource(newValue)
        self.LoadHardware()

    def FilterButtonClicked(self, filterBtn):
        btnSettingConfig = filterBtn.btnSettingConfig
        filterOn = filterBtn.IsChecked()
        settings.user.ui.Set(btnSettingConfig, filterOn)

    def GetSearchResults(self):
        listProvider = SearchBrowserListProvider(self.fittingSvc.searchFittingHelper, self.OnDropData, hwSettingObject=self.hwSettingObject)
        scrolllist = listProvider.GetSearchResults()
        return scrolllist

    def GetSearchChargeResults(self):
        listProvider = SearchBrowserListProviderCharges(self.fittingSvc.searchFittingHelper, self.OnDropData, hwSettingObject=self.hwSettingObject)
        scrolllist = listProvider.GetSearchResults()
        return scrolllist

    def FindTypeInList(self, typeID):
        self._ResetModuleSearchField()
        ChangeFilterBtnsStatesSlots(self.hardwareFilterBtns, None)
        self.SwitchToHardwareBrowsers()
        uthread2.call_after_wallclocktime_delay(self.BrowserToTypeID_thread, 0.5, typeID)

    def _ResetModuleSearchField(self):
        self.hwSettingObject.SetTextFiltering('')
        self.searchparent.searchInput.SetValue('')

    def BrowserToTypeID_thread(self, typeID):
        while self.IsHardwareThreadRunning():
            uthread2.sleep(0.2)

        uthread.new(self.OpenOnTypeID, typeID)

    def OpenOnTypeID(self, typeID, groupsToSkip = [], *args):
        for node in self.scroll.GetNodes():
            if typeID in node.get('typeIDs', []) and node.id not in groupsToSkip:
                if self.scroll.scrollingRange:
                    position = node.scroll_positionFromTop / float(self.scroll.scrollingRange)
                    self.scroll.ScrollToProportion(position, threaded=False)
                groupsToSkipCopy = groupsToSkip[:] + [node.id]
                if not node.open:
                    if node.panel is not None:
                        node.panel.OnClick()
                    else:
                        uicore.registry.SetListGroupOpenState(node.id, True)
                    import blue
                    blue.synchro.Yield()
                    return self.OpenOnTypeID(typeID, groupsToSkipCopy)
            elif node.get('typeID', None) == typeID:
                if self.scroll.scrollingRange:
                    position = node.scroll_positionFromTop / float(self.scroll.scrollingRange)
                    self.scroll.ScrollToProportion(position, threaded=False)
                self.scroll.SelectNode(node)
                break

    def CreateCurrentShipCont(self):
        self.shipCont.Flush()
        Frame(parent=self.shipCont, color=(1, 1, 1, 0.1))
        activeShip = GetActiveShip()
        clientDogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        shipDogmaItem = clientDogmaLocation.GetShip()
        shipTypeID = shipDogmaItem.typeID
        icon = Icon(parent=self.shipCont, pos=(0, 0, 40, 40), ignoreSize=True, state=uiconst.UI_DISABLED)
        if self.fittingSvc.IsShipSimulated():
            self.shipCont.OnClick = self.ExitSimulation
            icon.LoadIconByTypeID(shipTypeID)
        else:
            self.shipCont.OnClick = self.LoadCurrentShip
            hologramTexture = inventorycommon.typeHelpers.GetHoloIconPath(shipTypeID)
            icon.LoadTexture(hologramTexture)
        shipName = cfg.evelocations.Get(activeShip).name
        text = '%s<br>%s' % (evetypes.GetName(shipTypeID), shipName)
        self.shipnametext = EveLabelMedium(text=text, parent=self.shipCont, align=uiconst.TOTOP, top=2, padLeft=48)

    def ChangeResourceBtn(self):
        btn = self.hardwareFilterBtns.get(BTN_TYPE_RESOURCES, None)
        if not btn:
            return
        if self.controller.IsSimulated():
            btn.Enable()
        else:
            btn.Disable()

    def ChangeRigBtn(self):
        btn = self.hardwareFilterBtns.get(BTN_TYPE_RIGSLOT, None)
        if not btn:
            return
        shipItem = self.controller.dogmaLocation.GetShipItem()
        if shipItem is None or not IsModularShip(shipItem.typeID):
            btn.texturePath = btn.texturePath
        else:
            btn.texturePath = 'res:/UI/Texture/classes/Fitting/filterIconRigSlot.png'

    def Close(self):
        with EatSignalChangingErrors(errorMsg='fitting wnd'):
            if self.chargeBtnController:
                self.chargeBtnController.ClearSignals()
                self.chargeBtnController = None
            self.ChangeSignalConnection(connect=False)
        Container.Close(self)
