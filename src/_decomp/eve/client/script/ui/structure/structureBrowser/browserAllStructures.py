#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\browserAllStructures.py
import evetypes
import gametime
import uthread
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.scrollUtil import TabFinder
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.structureBrowser import browserUIConst
from eve.client.script.ui.structure.structureBrowser.controllers.filterContController import FilterContControllerAllStructures
from eve.client.script.ui.structure.structureBrowser.filterCont import FilterContAllStructures
from eve.client.script.ui.structure.structureBrowser.entries.structureEntry import StructureEntry
from eve.client.script.ui.structure.structureBrowser.controllers.structureEntryController import StructureEntryController
from eve.client.script.ui.structure.structureBrowser.filterContUtil import STATION_TYPE_CONFIGID, IsFilteredOutByText, IsFilteredOutByServices
from inventorycommon.util import IsNPC
from localization import GetByLabel
import log
OWNER_ANY = 1
OWNER_NPC = 2
OWNER_CORP = 3

class BrowserAllStructures(Container):
    default_name = 'BrowserAllStructures'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.structureBrowserController
        self.filterContController = FilterContControllerAllStructures()
        self.ChangeSignalConnection(connect=True)
        self.isInitialized = False
        self.serviceChangedTimer = None
        self.serviceChangedTimestamp = gametime.GetWallclockTimeNow()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_structures_changed, self.OnStructuresChanged),
         (self.filterContController.on_change_location_range, self.OnLocationRangeChanged),
         (self.filterContController.on_change_owner_value, self.OnOwnerValueChanged),
         (self.filterContController.on_text_filter_changed, self.OnTextFilterChanged),
         (self.filterContController.on_structure_type_changed, self.OnStructureTypeChanged),
         (self.filterContController.structureTypeFilterController.on_filter_changed, self.OnStructuresChanged),
         (self.filterContController.serviceFilterController.on_filter_changed, self.OnServiceSettingsChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnTabSelect(self):
        self.LoadPanel()

    def LoadPanel(self):
        self.display = True
        if self.isInitialized:
            self.UpdateScroll()
            return
        self.isInitialized = True
        self.comboCont = FilterContAllStructures(name='filterCont', parent=self, filterContController=self.filterContController, padBottom=8)
        self.scroll = Scroll(parent=self, id='AllStructuresScroll')
        self.scroll.GetTabStops = self.GetTabStops
        self.scroll.sr.fixedColumns = StructureEntry.GetFixedColumns()
        self.scroll.OnSelectionChange = self.OnScrollSelectionChange
        self.UpdateScroll()

    def GetTabStops(self, headertabs, idx = None):
        return TabFinder().GetTabStops(self.scroll.sr.nodes, headertabs, StructureEntry, idx=idx)

    def UpdateScroll(self):
        if not self.isInitialized:
            return
        if self.filterContController.AreServiceFiltersDisbled():
            structureServicesChecked = browserUIConst.ALL_SERVICES
        else:
            structureServicesChecked = self.filterContController.GetServicesChecked()
        self.scroll.ShowLoading()
        scrollList, somethingFilteredOut = self.GetScrollList(structureServicesChecked)
        if somethingFilteredOut:
            noContentHint = GetByLabel('UI/Structures/Browser/NoStructuresFoundWithFilters')
        else:
            noContentHint = GetByLabel('UI/Structures/Browser/NoStructuresFound')
        self.scroll.LoadContent(contentList=scrollList, headers=StructureEntry.GetHeaders(structureServicesChecked), noContentHint=noContentHint)
        self.scroll.HideLoading()

    def IsFilteredOut(self, structureController):
        if self._IsFilteredByOwner(structureController):
            return True
        if self._IsFilteredOutByStructureType(structureController):
            return True
        if self._IsFilteredOutByText(structureController):
            return True
        if self._IsFilteredOutByServices(structureController):
            return True
        return False

    def _IsFilteredByOwner(self, structureController):
        ownerValue = self.filterContController.GetStructureOwnerValue()
        if ownerValue == browserUIConst.OWNER_ANY:
            return False
        ownerID = structureController.GetOwnerID()
        if ownerValue == browserUIConst.OWNER_CORP:
            if ownerID == session.corpid:
                return False
            else:
                return True
        if ownerValue == browserUIConst.OWNER_NPC:
            if IsNPC(ownerID):
                return False
            else:
                return True
        return False

    def _IsFilteredOutByStructureType(self, structureController):
        if not self.filterContController.structureTypeFilterController.IsActive():
            return False
        groupingsChecked = self.filterContController.GetStructureTypesChecked()
        structureTypeID = structureController.GetTypeID()
        if evetypes.GetCategoryID(structureTypeID) == const.categoryStation:
            structureTypeID = STATION_TYPE_CONFIGID
        if structureTypeID in groupingsChecked:
            return False
        else:
            return True

    def _IsFilteredOutByText(self, structureController):
        filterText = self.filterContController.GetTextFilter()
        return IsFilteredOutByText(structureController, filterText)

    def _IsFilteredOutByServices(self, structureController):
        filterContController = self.filterContController
        return IsFilteredOutByServices(structureController, filterContController)

    def GetScrollList(self, structureServicesChecked):
        scrollList = []
        rangeSelected = self.filterContController.GetRange()
        structureControllers = self.controller.GetAllStructures(rangeSelected)
        somethingFilteredOut = False
        for controller in structureControllers:
            if self.IsFilteredOut(controller):
                somethingFilteredOut = True
                continue
            node = Bunch(controller=controller, decoClass=StructureEntry, columnSortValues=StructureEntry.GetColumnSortValues(controller, structureServicesChecked), charIndex=controller.GetName(), structureServicesChecked=structureServicesChecked, GetSortValue=StructureEntry.GetSortValue)
            scrollList.append(node)

        return (scrollList, somethingFilteredOut)

    def OnScrollSelectionChange(self, entries):
        pass

    def OnOwnerCombo(self, *args):
        self.UpdateScroll()

    def OnServiceSettingsChanged(self, *args):
        uthread.new(self.OnServiceSettingsChanged_thread)

    def OnServiceSettingsChanged_thread(self):
        DELAY = 500
        recentlyLoaded = gametime.GetTimeDiff(self.serviceChangedTimestamp, gametime.GetWallclockTimeNow()) / const.MSEC < DELAY
        if recentlyLoaded:
            self.serviceChangedTimer = AutoTimer(DELAY, self.DoUpdateScroll)
        else:
            self.DoUpdateScroll()

    def DoUpdateScroll(self):
        self.serviceChangedTimestamp = gametime.GetWallclockTimeNow()
        self.serviceChangedTimer = None
        self.UpdateScroll()

    def OnOwnerValueChanged(self, value):
        self.UpdateScroll()

    def OnLocationRangeChanged(self, value):
        self.UpdateScroll()

    def OnTextFilterChanged(self):
        self.UpdateScroll()

    def OnStructureTypeChanged(self, value):
        self.UpdateScroll()

    def OnStructuresChanged(self, *args):
        self.UpdateScroll()

    def Close(self):
        try:
            self.ChangeSignalConnection(connect=False)
        except Exception as e:
            log.LogError('Failed at closing all structures browser, e = ', e)
        finally:
            self.controller = None
            self.filterContController = None
            Container.Close(self)
