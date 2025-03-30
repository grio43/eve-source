#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\Alliances\sovHubs\sovHubPage.py
from collections import defaultdict
import carbonui
import locks
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui.control.button import Button
from carbonui.control.scroll import Scroll
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.neocom.Alliances.sovHubs.expandedSovHubEntry import ExpandedSovHubEntry
from eve.client.script.ui.shared.neocom.Alliances.sovHubs.filterCont import HubPageFilterCont, IsFilteredOutByLocation
from eve.client.script.ui.shared.neocom.Alliances.sovHubs.sovHubEntry import SovHubEntry
from eve.client.script.ui.shared.neocom.Alliances.sovHubs.sovHubEntryController import SovHubEntryController, ValueStorage, UNDEFINED
from eveexceptions import ExceptionEater
from expiringdict import ExpiringDict
from inventorycommon.const import typeInfrastructureHub, typeTerritorialClaimUnit
from localization import GetByLabel
from sovereignty.client.quasarCallWrapper import QuasarCallWrapper
from threadutils import throttled

class SovHubPage(Container):
    is_loaded = False
    filterCont = None
    __notifyevents__ = ['OnHubUpgradesStateChanged']

    def __init__(self, **kw):
        super(SovHubPage, self).__init__(**kw)
        self._valueStorageByHubID = ExpiringDict(1000, 300)

    def ApplyAttributes(self, attributes):
        super(SovHubPage, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)

    def DebugReload(self, *args):
        self.is_loaded = False
        self.Flush()
        self.Load()

    def Load(self, *args):
        if self.is_loaded:
            return
        with locks.TempLock('SovHubPage:Load'):
            if self.is_loaded:
                return
            if session.role & ROLE_PROGRAMMER:
                reloadBtn = Button(parent=self, label='Reload', align=carbonui.Align.TOPRIGHT, func=self.DebugReload, top=0, idx=0)
            carbonui.TextHeadline(parent=self, text=GetByLabel('UI/Sovereignty/HubPage/SovereigntyHubs'), align=carbonui.Align.TOTOP)
            self.filterCont = HubPageFilterCont(parent=self, align=carbonui.Align.TOTOP, height=30, top=20, padBottom=16)
            self.filterCont.on_filters_changed.connect(self.OnFilterChanged)
            self.scroll = Scroll(parent=self)
            self.scroll.sortGroups = True
            self.scroll.reverseGroupSortEnabled = True
            self.scroll.sr.id = 'sovhubPage_scroll'
            self.scroll.sr.defaultColumnWidth = SovHubEntry.GetDefaultColumnWidth()
            self.scroll.RefreshSort = self.RefreshSort
            self.LoadScroll()
            self.is_loaded = True

    def RefreshSort(self, *args, **kwargs):
        Scroll.RefreshSort(self.scroll, *args, **kwargs)
        uthread2.call_after_wallclocktime_delay(self.CheckSorted_throttled, 3)

    @throttled(2)
    def CheckSorted_throttled(self):
        if self.destroyed:
            return
        self._CheckSorted()

    def _CheckSorted(self):
        if self.destroyed:
            return
        sortValues = self.GetSortValues()
        if UNDEFINED in sortValues:
            self.scroll.Sort(self.scroll.GetSortBy(), self.scroll.GetSortDirection())

    def GetSortValues(self):
        idx = None
        headers = self.scroll.GetColumns()
        sortBy = self.scroll.GetSortBy()
        if sortBy in headers:
            idx = headers.index(sortBy)
        direction = self.scroll.GetSortDirection()
        sortValues = [ SovHubEntry.GetSortValue(node, sortBy, direction, idx) for node in self.scroll.GetNodes() ]
        return sortValues

    def OnFilterChanged(self):
        self.LoadScroll()

    def LoadScroll(self):
        sovHubsByItemID, solarSystemIDs = self.GetMySovHubsAndSystems()
        self.Prime(solarSystemIDs)
        quasarCallWrapper = QuasarCallWrapper(sm.GetService('sovHubSvc'), sm.GetService('sovereigntyResourceSvc'))
        headers = SovHubEntry.GetHeaders()
        scrollList = []
        for sovHubID, sovHubInfo in sovHubsByItemID.iteritems():
            entryID = ('SovHubEntry', sovHubID)
            uicore.registry.SetListGroupOpenState(entryID, 0)
            controller = SovHubEntryController(sovHubID, sovHubInfo.typeID, sovHubInfo.solarSystemID, sovHubInfo.campaignState, sovHubInfo.vulnerabilityState, sovHubInfo, quasarCallWrapper)
            if self.IsFilteredOut(sovHubID, sovHubInfo, controller):
                continue
            valueStorage = self._valueStorageByHubID.get(sovHubID, None)
            if valueStorage is None:
                valueStorage = ValueStorage()
                self._valueStorageByHubID[sovHubID] = valueStorage
            controller.valueStorage = valueStorage
            entry = GetFromClass(SovHubEntry, {'GetSubContent': self.GetSubContent,
             'entryController': controller,
             'id': entryID,
             'groupItems': [controller],
             'isListEntry': True,
             'ignoreRightClick': True,
             'GetSortValue': SovHubEntry.GetSortValue})
            scrollList.append(entry)

        self.scroll.LoadContent(contentList=scrollList, noContentHint=GetByLabel('UI/Sovereignty/HubPage/NoSovHubs'), headers=headers)

    def IsFilteredOut(self, sovHubID, sovHubInfo, controller):
        if IsFilteredOutByLocation(sovHubID, sovHubInfo, controller):
            return True
        return False

    def GetMySovHubsAndSystems(self):
        structuresPerSolarsystem = sm.GetService('sov').GetSovereigntyStructuresInfoForAlliance()
        tcuByItemID = {}
        sovHubByItemID = {}
        solarSystemIDs = set()
        for ssID, structureList in structuresPerSolarsystem.iteritems():
            for structure in structureList:
                if structure.typeID == typeInfrastructureHub and structure.corporationID == session.corpid:
                    sovHubByItemID[structure.itemID] = structure
                    solarSystemIDs.add(ssID)
                elif structure.typeID == typeTerritorialClaimUnit:
                    tcuByItemID[structure.itemID] = structure

        return ({itemID:hubInfo for itemID, hubInfo in sovHubByItemID.iteritems() if itemID in tcuByItemID}, solarSystemIDs)

    def GetSubContent(self, nodeData, newitems = 0):
        scrolllist = []
        for controller in nodeData.groupItems:
            entry = GetFromClass(ExpandedSovHubEntry, {'entryController': controller})
            scrolllist.append(entry)

        return scrolllist

    def Prime(self, solarSystemIDs):
        cfg.evelocations.Prime(solarSystemIDs)
        cfg.evelocations.Prime({cfg.mapSystemCache.Get(solarsystemID).regionID for solarsystemID in solarSystemIDs})
        cfg.evelocations.Prime({cfg.mapSystemCache.Get(solarsystemID).constellationID for solarsystemID in solarSystemIDs})

    def OnHubUpgradesStateChanged(self, hubID, installedUpgrades):
        self._valueStorageByHubID.pop(hubID, None)

    def Close(self):
        with ExceptionEater('SovHubPage:Failed to disconnect signal'):
            if self.filterCont:
                self.filterCont.on_filters_changed.disconnect(self.OnFilterChanged)
        super(SovHubPage, self).Close()
