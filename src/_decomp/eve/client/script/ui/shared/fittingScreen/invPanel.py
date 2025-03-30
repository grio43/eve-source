#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\invPanel.py
import eveicon
import evetypes
import itertoolsext
import localization
import telemetry
import threadutils
import uthread
import uthread2
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.comboEntryData import ComboEntryData
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.historyBuffer import HistoryBuffer
from eve.client.script.ui.shared.container import InvContQuickFilter, InvContViewBtns
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors, IsCharge
from eve.client.script.ui.shared.fittingScreen import BTN_TYPE_RESOURCES, CHARGE_FILTER_ALL_CHARGES, CHARGE_FILTER_NONE
from eve.client.script.ui.shared.fittingScreen.browsers.filtering import GetValidTypeIDs
from eve.client.script.ui.shared.fittingScreen.filterBtn import AddHardwareButtons, ChangeFilterBtnsStatesSlots, DropdownFilter, SetSettingForFilterBtns
from eve.client.script.ui.shared.fittingScreen.fittingPanels.chargeButtons import ModuleChargeController
from eve.client.script.ui.shared.fittingScreen.invPanelSettings import _GetComboPrefsKey, GetInvComboSettingValue
from eve.client.script.ui.shared.fittingScreen.resourceBtnTooltip import LoadFilterBtnTooltipPanel
from eve.client.script.ui.shared.fittingScreen.settingUtil import HardwareFiltersSettingObject, IsInventorySelected
from eve.client.script.ui.shared.inventory.invConst import GetInventoryContainerClass, ContainerType
from eve.client.script.ui.shared.inventory.invFilters import InvFilters
from eve.client.script.ui.shared.inventory.treeData import TreeDataShipHangar, TreeDataStructure, TreeDataItemHangar, TreeDataShip
from eve.common.script.sys.eveCfg import InShipInSpace, IsControllingStructure
import inventorycommon.const as invConst
from inventorycommon.const import VIEWMODE_ICONS, VIEWMODE_DETAILS, VIEWMODE_LIST, VIEWMODE_CARDS
from localization import GetByLabel
import blue
from eve.common.lib import appConst
from carbonui.uicore import uicore
from shipfitting.fittingDogmaLocationUtil import GetHardware
from signals.signalUtil import ChangeSignalConnect
from uthread2 import BufferedCall
validCategoryIDs = (appConst.categoryCharge,
 appConst.categoryCelestial,
 appConst.categoryCommodity,
 appConst.categoryDeployable,
 appConst.categoryDrone,
 appConst.categoryFighter,
 appConst.categoryImplant,
 appConst.categoryModule,
 appConst.categoryShipSkin,
 appConst.categoryShip,
 appConst.categorySkill,
 appConst.categoryStructureModule,
 appConst.categorySubSystem)
HISTORY_LENGTH = 50
BTN_OPACITY_ACTIVE = 1.0
BTN_OPACITY_INACTIVE = 0.25
FILTER_TYPE_INV = 'inv'

class FittingInvPanel(Container):
    default_clipChildren = True
    default_padding = (0, 8, 0, 0)
    default_availableViewModes = (VIEWMODE_ICONS, VIEWMODE_DETAILS, VIEWMODE_LIST)
    __notifyevents__ = ['OnSessionChanged', 'OnInvFiltersChanged', 'OnItemNameChange']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.configName = attributes.configName
        self.controller = attributes.controller
        self.invCont = None
        self.invController = None
        self.refreshRequired = False
        self.comboLoaded = False
        self.refreshThread = None
        self.pendingRefresh = False
        self.chargeFilterCont = None
        self.hwBtns = {}
        self.history = HistoryBuffer(HISTORY_LENGTH)
        self.hwSettingObject = HardwareFiltersSettingObject(FILTER_TYPE_INV)
        self.chargeController = ModuleChargeController(self.hwSettingObject.GetChargeSettingName(), isToggle=False)
        self.chargeController.on_selected_changed.connect(self.OnChargeSeletedChanged)
        self.availableViewModes = attributes.get('availableViewModes', self.default_availableViewModes)
        windowID = 'fittingInv'
        self.invFilterCont = InvFilters(parent=self, settingsID='invFiltersHeight_%s' % windowID, minSize=100, maxSize=0.5, defaultSize=150, windowID=windowID, padBottom=2)
        self.invFilterCont.on_filters_updated.connect(self.UpdateFilters)
        prefsKey = _GetComboPrefsKey()
        self.invCombo = Combo(parent=self, align=uiconst.TOTOP, options=[], callback=self.LoadInventoryLocationFromCombo, prefskey=prefsKey, select=None, maxVisibleEntries=Combo.default_maxVisibleEntries)
        self.invCombo.GetScrollEntry = self.GetInvScrollEntry
        self.filterCont = ContainerAutoSize(name='filterCont', parent=self, align=uiconst.TOTOP, padding=(0, 8, 0, 0))
        self.AddHardwareFilterButtons()
        self.controlCont = Container(name='controlCont', parent=self, align=uiconst.TOTOP, height=24, padTop=8, clipChildren=True)
        self.ConstructControls()
        self.invContParent = Container(name='invContParent', parent=self, padTop=8)
        self.invFilterCont.ExpandOrCollapeFilters()
        sm.RegisterNotify(self)
        sm.GetService('inv').Register(self)
        self.ChangeSignalConnection(connect=True)
        uthread2.start_tasklet(self.PopulateControls)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_new_itemID, self.OnSimulatedShipLoaded),
         (self.controller.on_slots_changed, self.OnSlotsChanged),
         (self.controller.on_simulation_state_changed, self.OnSimulationStateChanged),
         (self.controller.on_subsystem_really_changed, self.OnSubsystemReallyChanged),
         (self.controller.on_slots_updated, self.OnSlotsUpdated)]
        ChangeSignalConnect(signalAndCallback, connect)

    def PopulateControls(self):
        self.ConstructFilters()

    def ConstructControls(self):
        self.quickFilter = InvContQuickFilter(parent=self.controlCont, align=uiconst.TORIGHT, width=120)
        self.quickFilter.quickFilterInputBox.SetValue(self.hwSettingObject.GetTextFilter())
        self.quickFilter._SetQuickFilterInput = self.SetQuickFilterInput
        self.viewBtns = InvContViewBtns(parent=self.controlCont, align=uiconst.TOLEFT, controller=self)
        self.goBackBtn = ButtonIcon(name='goBackBtn', parent=self.controlCont, align=uiconst.TOLEFT, left=8, width=24, iconSize=16, texturePath=eveicon.navigate_back, func=self.OnBack, hint=GetByLabel('UI/Control/EveWindow/Previous'))
        self.goForwardBtn = ButtonIcon(name='goForwardBtn', parent=self.controlCont, align=uiconst.TOLEFT, width=24, iconSize=16, padRight=8, texturePath=eveicon.navigate_forward, func=self.OnForward, hint=GetByLabel('UI/Control/EveWindow/Next'))
        self.UpdateHistoryButtons()

    def SetInvContViewMode(self, value):
        if self.invCont:
            self.invCont.SetInvContViewMode(value)

    @threadutils.throttled(2)
    def UpdateComboThrottled(self):
        if self.comboLoaded:
            self.UpdateCombo()

    @BufferedCall(2000)
    def UpdateComboBuffered(self):
        if self.comboLoaded:
            self.UpdateCombo()

    @telemetry.ZONE_METHOD
    def UpdateCombo(self):
        if InShipInSpace():
            allowedNodes = (TreeDataShip,)
        else:
            allowedNodes = (TreeDataShip,
             TreeDataStructure,
             TreeDataItemHangar,
             TreeDataShipHangar)
        treeData = sm.GetService('inv').GetInvLocationTreeData()
        rootNodes = treeData.GetChildren()
        sortedRootNodes = []
        for data in rootNodes:
            if not isinstance(data, allowedNodes):
                continue
            idx = None
            for i, nodeClass in enumerate(allowedNodes):
                if isinstance(data, nodeClass):
                    idx = i
                    break

            sortedRootNodes.append((idx, data))

        sortedRootNodes = SortListOfTuples(sortedRootNodes)
        options = []
        for data in sortedRootNodes:
            clsName = getattr(data, 'clsName', None)
            entryData = ComboEntryData(label=data.GetLabel(), returnValue=(clsName, data.invController.itemID), icon=data.GetIcon())
            options.append(entryData)
            if isinstance(data, TreeDataShipHangar):
                continue
            for child in data.GetChildren():
                childClsName = getattr(child, 'clsName', None)
                if not childClsName:
                    continue
                entryData = ComboEntryData(label=child.GetLabel(), returnValue=(childClsName, child.invController.itemID), icon=child.GetIcon(), indentLevel=1)
                options.append(entryData)

        select = self._FindSelectedOptionForCombo(options)
        selectedBefore = self.invCombo.GetValue()
        self.invCombo.LoadOptions(options, select)
        if selectedBefore != self.invCombo.GetValue():
            self.invCombo.Confirm()
        self.comboLoaded = True

    def _FindSelectedOptionForCombo(self, options):
        validInvIDs = [ x.returnValue for x in options if x.returnValue[0] is not None ]
        if not validInvIDs:
            return
        selected = GetInvComboSettingValue()
        if selected and selected in validInvIDs:
            return selected
        defaultOptions = (invConst.INVENTORY_ID_STATION_ITEMS, invConst.INVENTORY_ID_STRUCTURE_ITEMS)
        defaultSelection = itertoolsext.first_or_default(validInvIDs, lambda x: x[0] in defaultOptions, None)
        if defaultSelection:
            return defaultSelection
        return validInvIDs[0]

    def AddHardwareFilterButtons(self):
        self.hardwareFilterCont = FlowContainer(name='hardwareFilterCont', parent=self.filterCont, align=uiconst.TOTOP, padTop=4, contentSpacing=uiconst.BUTTONGROUPMARGIN)
        self.hwBtns = AddHardwareButtons(self.hardwareFilterCont, self.HardwareFilterClicked, hintFunc=self.LoadFilterBtnTooltipPanel, prefix=self.hwSettingObject.GetHwPrefix())
        self.AddChargeFilter()
        self.UpdateHardwareBtns()

    def AddChargeFilter(self):
        hardwareList, options = self._GetChargeOptions()
        options.insert(0, (GetByLabel('UI/Fitting/FittingWindow/All Charges'), CHARGE_FILTER_ALL_CHARGES))
        options.insert(0, (GetByLabel('UI/Fitting/FittingWindow/DeactivateFilter'), CHARGE_FILTER_NONE))
        self.chargeFilterCont = DropdownFilter(parent=self.hardwareFilterCont, align=uiconst.NOALIGN, hardwareList=hardwareList, options=options, chargeController=self.chargeController, select=self.chargeController.GetSelectModuleTypeID(), maxVisibleEntries=10)
        if self.chargeFilterCont.GetValue() != self.chargeController.GetSelectModuleTypeID():
            self.chargeFilterCont.SetSelectedLook(CHARGE_FILTER_NONE)

    def _GetChargeOptions(self):
        hardwareList = GetHardware(self.controller.GetDogmaLocation())
        infoSvc = sm.GetService('info')
        options = []
        for moduleTypeID in hardwareList:
            chargeTypeIDs = infoSvc.GetUsedWithTypeIDs(moduleTypeID)
            if not chargeTypeIDs:
                continue
            moduleName = evetypes.GetName(moduleTypeID)
            options.append((moduleName, moduleTypeID))

        options = localization.util.Sort(options, key=lambda x: x[0])
        return (hardwareList, options)

    def HardwareFilterClicked(self, filterBtn, buttonType):
        isChargeFilterActive = self.chargeController.IsFilterActive()
        if isChargeFilterActive:
            self.chargeController.SetActiveState(False)
            self.UpdateHardwareBtns()
        self.FilterButtonClicked(filterBtn)
        self.Reload()

    def FilterButtonClicked(self, filterBtn):
        btnSettingConfig = filterBtn.btnSettingConfig
        filterOn = filterBtn.IsChecked()
        settings.user.ui.Set(btnSettingConfig, filterOn)

    def LoadPanel(self):
        if self.refreshRequired:
            self.Reload()
        if not self.comboLoaded:
            self.UpdateCombo()

    def Reload(self):
        if not IsInventorySelected():
            self.refreshRequired = True
            return
        self.refreshRequired = False
        self.pendingRefresh = True
        refreshThreadIsRunning = self.IsRefreshThreadRunning()
        if not refreshThreadIsRunning:
            self.refreshThread = uthread.new(self._Refresh_thread)

    def _Refresh_thread(self):
        self.pendingRefresh = False
        if self.invCont and not self.invCont.destroyed:
            self.invCont.Refresh()
            if self.pendingRefresh:
                self._Refresh_thread()

    def IsRefreshThreadRunning(self):
        refreshThreadIsRunning = self.refreshThread and self.refreshThread.alive
        return refreshThreadIsRunning

    def LoadInventoryLocationFromCombo(self, cb, key, val):
        if not val:
            if self.invCont:
                self.invCont.Hide()
                self.filterCont.Hide()
                self.controlCont.Hide()
            return
        if not self.invCont or self.invCont.invController.GetInvID() != val:
            self.LoadInventory(invID=val)

    def LoadInventory(self, invID, updateHistory = True):
        invType, itemID = invID
        self.filterCont.display = invType != ContainerType.STATION_SHIPS
        self.controlCont.Show()
        if updateHistory:
            self.history.Append(invID)
        self.invContParent.Flush()
        invClass = GetInventoryContainerClass(invType)
        self.invCont = invClass(name='fittingInv_%s' % itemID, parent=self.invContParent, itemID=itemID, activeFilters=self.GetActiveFilters())
        self.invController = self.invCont.invController
        self.invCont.FilterItems = self.FilterItems
        self.quickFilter.invCont = self.invCont
        oldItemDataFunc = self.invCont.GetItemData
        self.invCont.GetItemData = lambda *args, **kwargs: self.GetItemDataForInvCont(oldItemDataFunc, *args, **kwargs)
        self.invCombo.SelectItemByValue(invID)
        self.invCombo.UpdateSettings()
        self.UpdateHistoryButtons()
        self.ChangeResourceBtn()

    def FilterItems(self, items):
        if self.hwSettingObject.GetHwShipCanUseSetting():
            itemTypeIDs = {x.typeID for x in items if evetypes.GetCategoryID(x.typeID) in validCategoryIDs}
        else:
            itemTypeIDs = {x.typeID for x in items}
        if self.chargeController.IsFilterActive():
            validTypeIDs = self.FilterForCharges(itemTypeIDs)
        else:
            searchFittingHelper = sm.GetService('fittingSvc').searchFittingHelper
            validTypeIDs = GetValidTypeIDs(itemTypeIDs, searchFittingHelper, self.hwSettingObject)
        validItems = [ x for x in items if x.typeID in validTypeIDs ]
        itemFilterSvc = sm.GetService('itemFilter')
        for filter in self.GetActiveFilters():
            validItems = itemFilterSvc.FilterItems(validItems, filter)

        if self.invCont.invController.filtersEnabled:
            validItems = sm.GetService('itemFilter').ApplyTempFilter(validItems)
        return validItems

    def FilterForCharges(self, typeIDs):
        selectedModuleTypeID = self.chargeController.GetSelectModuleTypeID()
        if selectedModuleTypeID > 0:
            usedWith = self.chargeController.GetUsedWithForSelectedModule()
            return {x for x in typeIDs if x in usedWith}
        if selectedModuleTypeID == CHARGE_FILTER_ALL_CHARGES:
            return {x for x in typeIDs if IsCharge(x)}
        return typeIDs

    def GetItemDataForInvCont(self, oldItemDataFunc, rec, *args, **kwargs):
        itemData = oldItemDataFunc(rec, *args, **kwargs)
        itemData.openContainerFunc = self.OpenContainerFunc
        return itemData

    def OpenContainerFunc(self, invID, *args):
        self.LoadInventory(invID)
        uicore.registry.SetFocus(self)

    def GetInvScrollEntry(self, entryData):
        data = Combo.GetScrollEntry(self.invCombo, entryData)
        if entryData.returnValue is not None:
            clsName, itemID = entryData.returnValue
            if clsName is None:
                data['selectable'] = False
                data['OnClick'] = None
        return data

    def OnInvChangeAny(self, item = None, change = None):
        if not item or not change:
            return
        if item.categoryID != appConst.categoryCelestial:
            return
        if self._IsOldOrNewLocationInCombo(item, change):
            self.UpdateComboThrottled()

    def _IsOldOrNewLocationInCombo(self, item, change):
        if not self.comboLoaded:
            return False
        if self.IsItemInCombo(item.locationID):
            return True
        oldLocationID = change.get(appConst.ixLocationID, None)
        if oldLocationID and self.IsItemInCombo(oldLocationID):
            return True
        return False

    def LoadFilterBtnTooltipPanel(self, tooltipPanel, filterBtn):
        if filterBtn.buttonType != BTN_TYPE_RESOURCES:
            return
        isSimulated = self.controller.IsSimulated()
        LoadFilterBtnTooltipPanel(tooltipPanel, filterBtn.hintLabelPath, self.hwSettingObject, self.Reload, isSimulated)

    def SetQuickFilterInput(self, filterTxt):
        if filterTxt:
            blue.synchro.SleepWallclock(300)
        self.hwSettingObject.SetTextFiltering(filterTxt)
        self.Reload()
        self.quickFilter.inputThread = None

    def OnBack(self):
        invID = self.history.GoBack()
        if invID:
            self.LoadInventory(invID, updateHistory=False)
            self.UpdateHistoryButtons()

    def OnForward(self):
        invID = self.history.GoForward()
        if invID:
            self.LoadInventory(invID, updateHistory=False)
            self.UpdateHistoryButtons()

    def UpdateHistoryButtons(self):
        if self.history.IsBackEnabled():
            self.goBackBtn.Enable()
        else:
            self.goBackBtn.Disable()
        if self.history.IsForwardEnabled():
            self.goForwardBtn.Enable()
        else:
            self.goForwardBtn.Disable()

    def OnSessionChanged(self, isRemote, sess, change):
        if 'stationid' in change or 'structureid' in change or 'shipid' in change:
            currentlySelected = self.invCombo.GetIndex()
            self.UpdateCombo()
            if currentlySelected == 0 and 'shipid' in change and not IsControllingStructure():
                self.invCombo.SelectItemByIndex(0)
                self.invCombo.Confirm(0)

    def OnInvFiltersChanged(self):
        self.ConstructFilters()
        self.UpdateFilters()

    def OnItemNameChange(self, itemID, *args):
        if self.IsItemInCombo(itemID):
            self.UpdateComboBuffered()

    def IsItemInCombo(self, itemID):
        if not self.comboLoaded:
            return False
        for entryData in self.invCombo.GetSelectableEntries():
            if not entryData.returnValue:
                continue
            if len(entryData.returnValue) > 1 and entryData.returnValue[1] == itemID:
                return True

        return False

    def OnSlotsChanged(self):
        self.UpdateChargeFilters()

    def UpdateChargeFilters(self):
        if self.chargeFilterCont and not self.chargeFilterCont.destroyed:
            self.chargeFilterCont.Close()
        self.AddChargeFilter()
        if self.controller.IsSimulated():
            if not self.controller.GetPreviewFittedItem() and self.hwSettingObject.GetHwResourcesSettingResourcesLeftActive():
                self.Reload()

    def OnSlotsUpdated(self):
        _, options = self._GetChargeOptions()
        if self.chargeFilterCont.entries[2:] != options:
            self.UpdateChargeFilters()

    def OnSimulationStateChanged(self):
        if self.hwSettingObject.GetHwResourcesSetting():
            self.Reload()
        self.ChangeResourceBtn()

    def OnSimulatedShipLoaded(self, *args):
        if IsInventorySelected():
            self.Reload()

    def OnSubsystemReallyChanged(self, *args):
        if self.hwSettingObject.GetHwShipCanUseSetting():
            self.Reload()

    def UpdateFilters(self):
        if self.invCont:
            self.SetActiveFilters(self.GetActiveFilters())

    def SetActiveFilters(self, filters):
        self.invCont.SetFilters(filters)
        self.invFilterCont.SetActiveFilters(filters)

    def GetActiveFilters(self):
        filters = self.invFilterCont.GetActiveFilters()
        return filters

    def ConstructFilters(self):
        self.invFilterCont.ConstructFilters()

    def OnChargeSeletedChanged(self, selectedTypeID):
        self.Reload()
        self.UpdateHardwareBtns()

    def UpdateHardwareBtns(self):
        isChargeFilterActive = self.chargeController.IsFilterActive()
        for btn in self.hwBtns.itervalues():
            if isChargeFilterActive:
                btn.opacity = BTN_OPACITY_INACTIVE
            else:
                btn.opacity = BTN_OPACITY_ACTIVE

        if isChargeFilterActive:
            chargeToShow = self.chargeController.GetSelectModuleTypeID()
        else:
            chargeToShow = CHARGE_FILTER_NONE
        self.chargeFilterCont.SetSelectedLook(chargeToShow, False)

    def ChangeResourceBtn(self):
        btn = self.hwBtns.get(BTN_TYPE_RESOURCES, None)
        if not btn:
            return
        if self.controller.IsSimulated():
            btn.Enable()
        else:
            btn.Disable(opacity=0.3)

    def FindTypeInInventory(self, typeID):
        ChangeFilterBtnsStatesSlots(self.hwBtns, None)
        typeName = evetypes.GetName(typeID)
        self.quickFilter.quickFilterInputBox.SetValue(typeName)

    def SetFlagFilter(self, flagID, *args):
        self.quickFilter.ClearFilter()
        SetSettingForFilterBtns(flagID, self.hwBtns)
        self.Reload()

    def Close(self):
        with EatSignalChangingErrors(errorMsg='fitting wnd'):
            if self.controller:
                self.ChangeSignalConnection(connect=False)
        self.invController = None
        Container.Close(self)

    def GetViewModeIcon(self, viewMode):
        if viewMode == VIEWMODE_ICONS:
            return eveicon.grid_view
        if viewMode == VIEWMODE_DETAILS:
            return eveicon.details_view
        if viewMode == VIEWMODE_LIST:
            return eveicon.list_view
        if viewMode == VIEWMODE_CARDS:
            return eveicon.edit

    def GetViewModeName(self, viewMode):
        if viewMode == VIEWMODE_ICONS:
            return localization.GetByLabel('UI/Inventory/Icons')
        if viewMode == VIEWMODE_DETAILS:
            return localization.GetByLabel('UI/Inventory/Details')
        if viewMode == VIEWMODE_LIST:
            return localization.GetByLabel('UI/Inventory/List')
        if viewMode == VIEWMODE_CARDS:
            return localization.GetByLabel('UI/Inventory/CardsViewMode')
        return localization.GetByLabel('UI/Generic/Unknown')
