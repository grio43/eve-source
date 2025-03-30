#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_accounts.py
import sys
import blue
import evetypes
import uthread
import utillib
from evePathfinder.core import IsUnreachableJumpCount
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveScroll
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.item import Item, ItemWithVolume
from eve.client.script.ui.shared.neocom.corporation.corpPanelConst import CorpPanel
from eve.client.script.ui.util import uix
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
import log
import carbonui.const as uiconst
import localization
from carbon.common.script.sys.row import Row
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.uicore import uicore
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.shared.assets.assetSafety import AssetSafetyCont
from eve.client.script.ui.shared.assets.assetSafetyControllers import SafetyControllerCorp
from eve.client.script.util.contractutils import DoParseItemType
from eve.common.lib import appConst as const
from eveformat.client import solar_system_security_status
from eveservices.menu import GetMenuService
from eve.common.script.sys.idCheckers import IsStation, IsSolarSystem, IsRegion, IsWormholeSystem, IsTriglavianSystem
from menu import MenuLabel
SEARCH_FLAGNAME_OFFICES = 'offices'
SEARCH_FLAGNAME_PROPERTY = 'property'
SEARCH_FLAGNAME_DELIVERIES = 'deliveries'
SEARCH_FLAGNAME_IMPOUNDED = 'impounded'
SEARCH_FLAGNAME_ASSETSAFETY = 'assetwraps'
KEYNAME_LOCKDOWN = 'lockdown'
KEYNAME_SAFETY = 'safety'
KEYNAME_SEARCH = 'search'
SEARCH_FLAG_OFFICES = 71
SEARCH_FLAG_IMPOUNDED = 72
SEARCH_FLAG_PROPERTY = 74
SEARCH_FLAG_DELIVERIES = 75
SEARCH_FLAG_ASSETSAFETY = 76
FLAG_TO_FLAGNAME = {SEARCH_FLAG_OFFICES: SEARCH_FLAGNAME_OFFICES,
 SEARCH_FLAG_IMPOUNDED: SEARCH_FLAGNAME_IMPOUNDED,
 SEARCH_FLAG_PROPERTY: SEARCH_FLAGNAME_PROPERTY,
 SEARCH_FLAG_DELIVERIES: SEARCH_FLAGNAME_DELIVERIES,
 SEARCH_FLAG_ASSETSAFETY: SEARCH_FLAGNAME_ASSETSAFETY}
FLAGNAME_TO_FLAG = {SEARCH_FLAGNAME_OFFICES: SEARCH_FLAG_OFFICES,
 SEARCH_FLAGNAME_IMPOUNDED: SEARCH_FLAG_IMPOUNDED,
 SEARCH_FLAGNAME_PROPERTY: SEARCH_FLAG_PROPERTY,
 SEARCH_FLAGNAME_DELIVERIES: SEARCH_FLAG_DELIVERIES,
 SEARCH_FLAGNAME_ASSETSAFETY: SEARCH_FLAG_ASSETSAFETY}

class CorpAccounts(Container):
    __guid__ = 'form.CorpAccounts'
    __nonpersistvars__ = ['assets']
    __notifyevents__ = ['OnCorpAssetChange', 'OnReloadCorpAssets']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sr.journalFromDate = blue.os.GetWallclockTime() - 24 * const.HOUR * 7 + const.HOUR
        self.sr.journalToDate = blue.os.GetWallclockTime() + const.HOUR
        self.sr.viewMode = 'details'
        self.key = None
        self.safetyCont = None
        self.sr.search_inited = 0
        self.searchCont = None
        sm.RegisterNotify(self)

    def OnReloadCorpAssets(self):
        if self.sr.tabs:
            self.sr.tabs.SetSelected(self.sr.tabs.GetSelected())

    def OnCorpAssetChange(self, items, stationID):
        if items[0].locationID != stationID:
            id = ('corpofficeassets', (stationID, items[0].flagID))
            which = SEARCH_FLAGNAME_DELIVERIES
        else:
            id = ('corpassets', stationID)
            which = SEARCH_FLAGNAME_OFFICES
        if not self.sr.Get('inited', 0):
            return
        for node in self.sr.scroll.GetNodes():
            if node.Get('id', 0) == id:
                rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, which)
                for row in rows:
                    if stationID == row.locationID:
                        node.data = self.GetLocationData(row, SEARCH_FLAG_OFFICES, scrollID=self.sr.scroll.sr.id)

                if node.panel:
                    node.panel.Load(node)
                self.sr.scroll.PrepareSubContent(node)
                pos = self.sr.scroll.GetScrollProportion()
                self.sr.scroll.ScrollToProportion(pos)

    def Load(self, panel_id, *args):
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            self.sr.scroll = eveScroll.Scroll(parent=self, padding=(0, 8, 0, 0), display=False)
            self.sr.scroll.adjustableColumns = 1
            self.sr.scroll.sr.id = 'CorporationAssets'
            self.sr.scroll.sr.minColumnWidth = {localization.GetByLabel('UI/Common/Name'): 44}
            self.sr.scroll.SetColumnsHiddenByDefault(uix.GetInvItemDefaultHiddenHeaders())
            self.sr.scroll.Load(contentList=[], headers=uix.GetInvItemDefaultHeaders())
            self.sr.scroll.OnNewHeaders = self.OnNewHeadersSet
            self.sr.scroll.allowFilterColumns = 0
            self.sr.tabs = ToggleButtonGroup(parent=self, idx=0, align=uiconst.TOTOP, callback=self.Refresh, padBottom=8)
            tabs = [[localization.GetByLabel('UI/Corporations/Common/Offices'), SEARCH_FLAGNAME_OFFICES, self.sr.scroll],
             [localization.GetByLabel('UI/Corporations/Assets/Impounded'), SEARCH_FLAGNAME_IMPOUNDED, self.sr.scroll],
             [localization.GetByLabel('UI/Corporations/Assets/InSpace'), SEARCH_FLAGNAME_PROPERTY, self.sr.scroll],
             [localization.GetByLabel('UI/Corporations/Assets/Deliveries'), SEARCH_FLAGNAME_DELIVERIES, self.sr.scroll],
             [localization.GetByLabel('UI/Corporations/Assets/Lockdown'), KEYNAME_LOCKDOWN, self.sr.scroll],
             [localization.GetByLabel('UI/Common/Search'), KEYNAME_SEARCH, self.sr.scroll]]
            if self.IsDirector():
                self.safetyParent = Container(parent=self, display=False)
                tabs.append((localization.GetByLabel('UI/Inventory/AssetSafety/Safety'), KEYNAME_SAFETY, self.safetyParent))
            for label, tabID, panel in tabs:
                self.sr.tabs.AddButton(tabID, label, panel)

            self.sr.tabs.SelectFirst()

    def Refresh(self, panel_id = None, *args, **kwargs):
        if self.searchCont:
            self.searchCont.state = uiconst.UI_HIDDEN
        if panel_id == CorpPanel.ASSETS:
            return
        if panel_id not in (KEYNAME_SEARCH, KEYNAME_SAFETY):
            if not getattr(self, 'filt_inited', False):
                self.InitAssetFilters()
            self.sr.filt_cont.state = uiconst.UI_PICKCHILDREN
        elif self.sr.Get('filt_cont', None):
            self.sr.filt_cont.state = uiconst.UI_HIDDEN
        if panel_id in (KEYNAME_LOCKDOWN,):
            uthread.new(self.ShowLockdown, None, None)
        elif panel_id == KEYNAME_SEARCH:
            self.sr.scroll.OnNewHeaders = self.Search
            uthread.new(self.ShowSearch)
        elif panel_id == KEYNAME_SAFETY:
            if self.safetyCont is None or self.safetyCont.destroyed:
                self.safetyCont = AssetSafetyCont(parent=self.safetyParent, padding=4, controller=SafetyControllerCorp())
            self.safetyCont.display = True
            self.safetyCont.Load()
        else:
            uthread.new(self.ShowAssets, panel_id, None, None)

    def InitAssetFilters(self):
        sortKey = settings.char.ui.Get('corpAssetsSortKey', None)
        self.sr.filt_cont = Container(align=uiconst.TOTOP, height=37, parent=self, top=2, idx=1)
        self.sr.sortcombo = Combo(label=localization.GetByLabel('UI/Common/SortBy'), parent=self.sr.filt_cont, options=[], name='sortcombo', select=sortKey, callback=self.Filter, width=140, pos=(0, 16, 0, 0))
        l = self.sr.sortcombo.width + self.sr.sortcombo.left + const.defaultPadding
        self.sr.filtcombo = Combo(label=localization.GetByLabel('UI/Common/View'), parent=self.sr.filt_cont, options=[], name='filtcombo', select=None, callback=self.Filter, width=140, pos=(l,
         16,
         0,
         0))
        self.sr.filt_cont.height = self.sr.filtcombo.top + self.sr.filtcombo.height
        self.filt_inited = 1

    def UpdateSortOptions(self, currentlySelected, sortKey):
        sortOptions = [(localization.GetByLabel('UI/Common/Name'), 0), (localization.GetByLabel('UI/Common/NumberOfJumps'), 1)]
        if currentlySelected == SEARCH_FLAGNAME_DELIVERIES:
            sortOptions.append((localization.GetByLabel('UI/Common/NumberOfItems'), 2))
        self.sr.sortcombo.LoadOptions(sortOptions, None)
        if sortKey is None:
            sortKey = settings.char.ui.Get('corpAssetsSortKey', None)
        if sortKey is None or sortKey >= len(sortOptions):
            sortKey = 0
        self.sr.sortcombo.SelectItemByIndex(sortKey)
        settings.char.ui.Set('corpAssetsSortKey', sortKey)
        return sortKey

    def Filter(self, *args):
        flagName, regionKey = self.sr.filtcombo.GetValue()
        sortKey = self.sr.sortcombo.GetValue()
        if flagName == KEYNAME_LOCKDOWN:
            self.ShowLockdown(sortKey, regionKey)
        else:
            self.ShowAssets(flagName, sortKey, regionKey)

    def OnNewHeadersSet(self, *args):
        self.sr.tabs.SetSelected(self.sr.tabs.GetSelected())

    def ShowAssets(self, flagName, sortKey, regionKey):
        if self is not None and not self.destroyed:
            sm.GetService('corpui').ShowLoad()
        else:
            return
        sortKey = self.UpdateSortOptions(flagName, sortKey)
        if regionKey is None:
            regionKey = settings.char.ui.Get('corpAssetsKeyID_%s' % flagName, 0)
        settings.char.ui.Set('corpAssetsKeyID_%s' % flagName, regionKey)
        flag = FLAGNAME_TO_FLAG[flagName]
        which = flagName
        rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, which)
        options = self.GetFilterOptions(rows, flagName)
        try:
            self.sr.filtcombo.LoadOptions(options, None)
            if regionKey and regionKey not in (0, 1):
                label = localization.GetByLabel('UI/Common/LocationDynamic', location=regionKey)
                self.sr.filtcombo.SelectItemByLabel(label)
            else:
                self.sr.filtcombo.SelectItemByIndex(regionKey)
        except (Exception,) as e:
            sys.exc_clear()

        def CmpFunc(a, b):
            if sortKey == 0:
                return cmp(a.charIndex, b.charIndex)
            elif sortKey == 1:
                return cmp(a.jumps, b.jumps)
            else:
                return cmp(b.itemCount, a.itemCount)

        if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & eve.session.corprole == 0:
            self.SetHint(localization.GetByLabel('UI/Corporations/Assets/NeedAccountantOrJuniorRole'))
            sm.GetService('corpui').HideLoad()
            return
        self.sr.scroll.allowFilterColumns = 1
        data = []
        scrolllist = []
        for row in rows:
            data.append(self.GetLocationData(row, flag, scrollID=self.sr.scroll.sr.id))

        data.sort(lambda x, y: cmp(x['label'], y['label']))
        for row in data:
            if regionKey == 1:
                scrolllist.append(GetFromClass(ListGroup, row))
            elif regionKey == 0:
                if row['regionID'] == eve.session.regionid:
                    scrolllist.append(GetFromClass(ListGroup, row))
            elif row['regionID'] == regionKey:
                scrolllist.append(GetFromClass(ListGroup, row))
            uicore.registry.SetListGroupOpenState(('corpassets', row['locationID']), 0)

        scrolllist.sort(CmpFunc)
        self.sr.scroll.Load(fixedEntryHeight=42, contentList=scrolllist, sortby='label', headers=uix.GetInvItemDefaultHeaders(), noContentHint=localization.GetByLabel('UI/Corporations/Assets/NoItemsFound'), showCollapseIcon=True)
        sm.GetService('corpui').HideLoad()

    def GetFilterOptions(self, rows, flagName):
        filterOptions = self.GetRegions(rows, flagName)
        options = [(localization.GetByLabel('UI/Corporations/Assets/CurrentRegion'), (flagName, 0)), (localization.GetByLabel('UI/Corporations/Assets/AllRegions'), (flagName, 1))]
        opts = {}
        for r in filterOptions:
            if IsRegion(r):
                label = localization.GetByLabel('UI/Common/LocationDynamic', location=r)
                opts[label] = r

        keys = opts.keys()
        keys.sort()
        for k in keys:
            options.append((k, (flagName, opts[k])))

        return options

    def GetRegions(self, rows, flagName):
        mapSvc = sm.GetService('map')
        regionIDs = []
        solarSystemIDs = set()
        for row in rows:
            if flagName == KEYNAME_LOCKDOWN:
                locationID = row
            else:
                solarSystemID = getattr(row, 'solarsystemID', None)
                if solarSystemID:
                    solarSystemIDs.add(solarSystemID)
                    continue
                locationID = row.locationID
            if IsSolarSystem(locationID):
                solarSystemID = locationID
            else:
                try:
                    solarSystemID = sm.GetService('ui').GetStationStaticInfo(locationID).solarSystemID
                except StandardError:
                    solarSystemID = locationID

            solarSystemIDs.add(solarSystemID)

        for eachSolarsystemID in solarSystemIDs:
            try:
                constellationID = mapSvc.GetParent(eachSolarsystemID)
                regionID = mapSvc.GetParent(constellationID)
                regionIDs.append(regionID)
            except:
                log.LogException()

        return regionIDs

    def GetLocationData(self, row, flag, scrollID = None):
        jumps = -1
        solarSystemID = row.solarsystemID
        locationName = localization.GetByLabel('UI/Common/LocationDynamic', location=row.locationID)
        try:
            mapSvc = sm.GetService('map')
            constellationID = mapSvc.GetParent(solarSystemID)
            regionID = mapSvc.GetParent(constellationID)
            jumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(solarSystemID)
            label = self._GetLocationLabel(solarSystemID, row.locationID, jumps)
        except StandardError:
            log.LogException()
            label = locationName

        numberOfItems = -1
        if hasattr(row, 'itemCount'):
            numberOfItems = row.itemCount
            label = self._GetLocationLabel(solarSystemID, row.locationID, jumps, row.itemCount)
        data = {'GetSubContent': self.GetSubContent,
         'label': label,
         'jumps': jumps,
         'itemCount': numberOfItems,
         'groupItems': None,
         'flag': flag,
         'id': ('corpassets', row.locationID),
         'tabs': [],
         'state': 'locked',
         'locationID': row.locationID,
         'showicon': 'hide',
         'MenuFunction': self.GetLocationMenu,
         'solarSystemID': solarSystemID,
         'regionID': regionID,
         'scrollID': scrollID,
         'locationTypeID': getattr(row, 'typeID', None),
         'charIndex': locationName}
        return data

    def IsLocationStructure(self, node):
        locationTypeID = node.locationTypeID
        if not locationTypeID:
            return False
        categoryID = evetypes.GetCategoryID(locationTypeID)
        return categoryID == const.categoryStructure

    def GetLocationMenu(self, node):
        locationID = node.locationID
        if IsStation(locationID) or self.IsLocationStructure(node):
            if IsStation(locationID):
                stationInfo = sm.GetService('ui').GetStationStaticInfo(locationID)
                typeID = stationInfo.stationTypeID
            else:
                typeID = node.locationTypeID
            solarSystemID = node.solarSystemID
            menu = GetMenuService().CelestialMenu(locationID, typeID=typeID, parentID=solarSystemID)
            checkIsDirector = self.IsDirector()
            if checkIsDirector:
                if node.flag == SEARCH_FLAG_IMPOUNDED:
                    menu.append((MenuLabel('UI/Corporations/Assets/TrashItemsAtLocation'), self.TrashImpoundedItems, (locationID,)))
                if self.IsLocationStructure(node):
                    if IsWormholeSystem(solarSystemID) or IsTriglavianSystem(solarSystemID):
                        label = MenuLabel('UI/Inventory/AssetSafety/MoveItemsToSpace')
                    else:
                        label = MenuLabel('UI/Inventory/AssetSafety/MoveItemsToSafety')
                    menu.append((label, self.MoveItemsToSafety, (solarSystemID, locationID)))
            return menu
        if IsSolarSystem(locationID):
            return GetMenuService().CelestialMenu(locationID)
        return []

    @staticmethod
    def IsDirector():
        checkIsDirector = const.corpRoleDirector == session.corprole & const.corpRoleDirector
        return checkIsDirector

    @staticmethod
    def TrashImpoundedItems(stationID):
        items = sm.RemoteSvc('corpmgr').GetAssetInventoryForLocation(session.corpid, stationID, SEARCH_FLAGNAME_IMPOUNDED)
        itemReport = '<br>'.join([ '<t>- %s' % cfg.FormatConvert(const.UE_TYPEIDANDQUANTITY, item.typeID, item.stacksize) for item in items ])
        question, args = ('ConfirmTrashingPlu', {'items': itemReport}) if len(items) > 1 else ('ConfirmTrashingSin', {'itemWithQuantity': itemReport})
        if itemReport and eve.Message(question, args, uiconst.YESNO) != uiconst.ID_YES:
            return
        sm.GetService('objectCaching').InvalidateCachedMethodCall('corpmgr', 'GetAssetInventoryForLocation', session.corpid, stationID, SEARCH_FLAGNAME_IMPOUNDED)
        sm.GetService('officeManager').TrashImpoundAtStation(stationID)
        sm.ScatterEvent('OnReloadCorpAssets')

    @staticmethod
    def MoveItemsToSafety(solarSystemID, structureID):
        sm.GetService('assetSafety').MoveItemsInStructureToAssetSafetyForCorp(solarSystemID, structureID)

    def GetSubContent(self, nodedata, *args):
        which = FLAG_TO_FLAGNAME[nodedata.flag]
        items = sm.RemoteSvc('corpmgr').GetAssetInventoryForLocation(eve.session.corpid, nodedata.locationID, which)
        scrolllist = []
        if len(items) == 0:
            label = localization.GetByLabel('/Carbon/UI/Controls/Common/NoItem')
            if nodedata.flag == SEARCH_FLAG_OFFICES:
                label = localization.GetByLabel('UI/Corporations/Assets/UnusedCorpOffice')
            return [GetFromClass(Generic, {'label': label,
              'sublevel': nodedata.Get('sublevel', 0) + 1})]
        items.header.virtual += [('groupID', lambda row: evetypes.GetGroupID(row.typeID)), ('categoryID', lambda row: evetypes.GetCategoryID(row.typeID))]
        searchCondition = nodedata.Get('searchCondition', None)
        if which == SEARCH_FLAGNAME_OFFICES and searchCondition is None:
            divisionNames = sm.GetService('corp').GetDivisionNames()
            for flagID in const.flagCorpSAGs:
                divisionID = const.corpDivisionsByFlag[flagID]
                scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetSubContentDivision,
                 'label': divisionNames[divisionID + 1],
                 'groupItems': None,
                 'flag': flagID,
                 'id': ('corpofficeassets', (nodedata.locationID, flagID)),
                 'tabs': [],
                 'state': 'locked',
                 'locationID': nodedata.locationID,
                 'showicon': 'hide',
                 'sublevel': nodedata.Get('sublevel', 0) + 1,
                 'viewMode': self.sr.viewMode,
                 'scrollID': nodedata.scrollID}))
                uicore.registry.SetListGroupOpenState(('corpofficeassets', (nodedata.locationID, flagID)), 0)

        else:
            for each in items:
                if searchCondition is not None:
                    if searchCondition.typeID is not None and searchCondition.typeID != each.typeID or searchCondition.groupID is not None and searchCondition.groupID != each.groupID or searchCondition.categoryID is not None and searchCondition.categoryID != each.categoryID or searchCondition.qty > each.stacksize:
                        continue
                data = uix.GetItemData(each, self.sr.viewMode, viewOnly=1, scrollID=nodedata.scrollID)
                data.id = each.itemID
                data.remote = True
                if nodedata.flag in (SEARCH_FLAG_OFFICES, SEARCH_FLAG_IMPOUNDED) and each.categoryID == const.categoryBlueprint:
                    data.locked = sm.GetService('lockedItems').IsItemLocked(each)
                scrolllist.append(GetFromClass(Item, data=data))

        return scrolllist

    def GetSubContentDivision(self, nodedata, *args):
        items = sm.RemoteSvc('corpmgr').GetAssetInventoryForLocation(eve.session.corpid, nodedata.locationID, SEARCH_FLAGNAME_OFFICES)
        scrolllist = []
        if len(items) == 0:
            return [GetFromClass(Generic, {'label': localization.GetByLabel('UI/Corporations/Assets/UnusedCorpOffice'),
              'sublevel': nodedata.Get('sublevel', 1) + 1,
              'id': nodedata.flag})]
        if not {'groupID', 'categoryID'} & {i[0] for i in items.header.virtual}:
            items.header.virtual += [('groupID', lambda row: evetypes.GetGroupID(row.typeID)), ('categoryID', lambda row: evetypes.GetCategoryID(row.typeID))]
        for each in items:
            if each.flagID != nodedata.flag:
                continue
            data = uix.GetItemData(each, nodedata.viewMode, viewOnly=1, scrollID=nodedata.scrollID)
            data.id = each.itemID
            data.remote = True
            data.sublevel = nodedata.Get('sublevel', 1) + 1
            if each.categoryID == const.categoryBlueprint:
                data.locked = sm.GetService('lockedItems').IsItemLocked(each)
            scrolllist.append(GetFromClass(ItemWithVolume, data))

        return scrolllist

    def OnGetEmptyMenu(self, *args):
        return []

    def OnLockedItemChangeUI(self, itemID, ownerID, locationID):
        self.LogInfo(self.__class__.__name__, 'OnLockedItemChangeUI')
        if self.sr.tabs.GetSelected() == KEYNAME_LOCKDOWN:
            sortKey = settings.char.ui.Get('corpAssetsSortKey', None)
            regionKey = settings.char.ui.Get('corpAssetsKeyID_lockdown', 0)
            self.ShowLockdown(sortKey, regionKey)

    def ShowLockdown(self, sortKey, regionKey, *args):
        if self is not None and not self.destroyed:
            sm.GetService('corpui').ShowLoad()
        else:
            return
        if sortKey is None:
            sortKey = settings.char.ui.Get('corpAssetsSortKey', None)
        settings.char.ui.Set('corpAssetsSortKey', sortKey)
        if regionKey is None:
            regionKey = settings.char.ui.Get('corpAssetsKeyID_lockdown', 0)
        settings.char.ui.Set('corpAssetsKeyID_lockdown', regionKey)
        if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & eve.session.corprole == 0:
            self.SetHint(localization.GetByLabel('UI/Corporations/Assets/NeedAccountantRole'))
            self.sr.scroll.Clear()
            sm.GetService('corpui').HideLoad()
            return
        scrolllistTmp = []
        self.sr.scroll.allowFilterColumns = 1
        locationIDs = sm.GetService('lockedItems').GetLockedItemLocations()
        options = self.GetFilterOptions(locationIDs, KEYNAME_LOCKDOWN)
        try:
            self.sr.filtcombo.LoadOptions(options, None)
            if regionKey and regionKey not in (0, 1):
                self.sr.filtcombo.SelectItemByLabel(cfg.evelocations.Get(regionKey).name)
            else:
                self.sr.filtcombo.SelectItemByIndex(regionKey)
        except (Exception,) as e:
            sys.exc_clear()

        def CmpFunc(a, b):
            if sortKey == 1:
                return cmp(a.jumps, b.jumps)
            else:
                return cmp(a.charIndex, b.charIndex)

        for locationID in locationIDs:
            if IsStation(locationID):
                solarSystemID = sm.GetService('ui').GetStationStaticInfo(locationID).solarSystemID
            else:
                try:
                    solarSystemID = sm.GetService('structureDirectory').GetStructureInfo(locationID).solarSystemID
                except:
                    solarSystemID = cfg.evelocations.Get(locationID).solarSystemID

            try:
                mapSvc = sm.GetService('map')
                jumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(solarSystemID)
                locationName = localization.GetByLabel('UI/Common/LocationDynamic', location=locationID)
                constellationID = mapSvc.GetParent(solarSystemID)
                regionID = mapSvc.GetParent(constellationID)
                label = self._GetLocationLabel(solarSystemID, locationID, jumps)
            except:
                log.LogException()
                label = locationName

            scrolllistTmp.append(GetFromClass(ListGroup, {'label': label,
             'jumps': jumps,
             'GetSubContent': self.ShowLockdownSubcontent,
             'locationID': locationID,
             'regionID': regionID,
             'groupItems': None,
             'id': ('itemlocking', locationID),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide',
             'scrollID': self.sr.scroll.sr.id,
             'charIndex': locationName}))

        scrolllistTmp.sort(lambda x, y: cmp(x['label'], y['label']))
        scrolllist = []
        for row in scrolllistTmp:
            if regionKey == 1:
                scrolllist.append(GetFromClass(ListGroup, row))
            elif regionKey == 0:
                if row['regionID'] == eve.session.regionid:
                    scrolllist.append(GetFromClass(ListGroup, row))
            elif row['regionID'] == regionKey:
                scrolllist.append(GetFromClass(ListGroup, row))
            uicore.registry.SetListGroupOpenState(('corpassets', row['locationID']), 0)

        scrolllist.sort(CmpFunc)
        self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=uix.GetInvItemDefaultHeaders(), noContentHint=localization.GetByLabel('UI/Corporations/Assets/NoItemsFound'), showCollapseIcon=True)
        sm.GetService('corpui').HideLoad()

    def ShowLockdownSubcontent(self, nodedata, *args):
        office = sm.GetService('officeManager').GetCorpOfficeAtLocation(nodedata.locationID)
        locationID = office.officeID if office else nodedata.locationID
        header = ['itemID',
         'typeID',
         'ownerID',
         'groupID',
         'categoryID',
         'quantity',
         'singleton',
         'stacksize',
         'locationID',
         'flagID']
        scrolllist = []
        for item in sm.GetService('lockedItems').GetLockedItemsByLocation(nodedata.locationID).itervalues():
            line = [item.itemID,
             item.typeID,
             eve.session.corpid,
             evetypes.GetGroupID(item.typeID),
             evetypes.GetCategoryID(item.typeID),
             1,
             const.singletonBlueprintOriginal,
             1,
             locationID,
             4]
            fakeItem = Row(header, line)
            data = uix.GetItemData(fakeItem, self.sr.viewMode, viewOnly=1, scrollID=nodedata.scrollID)
            data.GetMenu = self.OnGetEmptyMenu
            scrolllist.append(GetFromClass(Item, data))

        return scrolllist

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def ShowSearch(self, *args):
        if not self.sr.search_inited:
            self.searchCont = Container(name='searchCont', parent=self, height=HEIGHT_NORMAL, align=uiconst.TOTOP, idx=1, padTop=16)
            catOptions = [(localization.GetByLabel('UI/Corporations/Assets/AllCategories'), None)]
            categories = []
            for categoryID in evetypes.IterateCategories():
                if categoryID > 0:
                    categories.append([evetypes.GetCategoryNameByCategory(categoryID), categoryID, evetypes.IsCategoryPublishedByCategory(categoryID)])

            categories.sort()
            for c in categories:
                if c[2]:
                    catOptions.append((c[0], c[1]))

            typeOptions = [(localization.GetByLabel('UI/Corporations/Common/Offices'), SEARCH_FLAGNAME_OFFICES),
             (localization.GetByLabel('UI/Corporations/Assets/Impounded'), SEARCH_FLAGNAME_IMPOUNDED),
             (localization.GetByLabel('UI/Corporations/Assets/InSpace'), SEARCH_FLAGNAME_PROPERTY),
             (localization.GetByLabel('UI/Corporations/Assets/Deliveries'), SEARCH_FLAGNAME_DELIVERIES),
             (localization.GetByLabel('UI/Corporations/Assets/AssetSafety'), SEARCH_FLAGNAME_ASSETSAFETY)]
            left = 0
            top = 0
            self.sr.fltType = c = Combo(label=localization.GetByLabel('UI/Common/Where'), parent=self.searchCont, options=typeOptions, name='flt_type', select=settings.user.ui.Get('corp_assets_filter_type', None), callback=self.ComboChange, width=90, pos=(left,
             top,
             0,
             0))
            left += c.width + 4
            self.sr.fltCategories = c = Combo(parent=self.searchCont, options=catOptions, name='flt_category', select=settings.user.ui.Get('corp_assets_filter_categories', None), callback=self.ComboChange, width=90, pos=(left,
             top,
             0,
             0))
            left += c.width + 4
            grpOptions = [(localization.GetByLabel('UI/Corporations/Assets/AllGroups'), None)]
            self.sr.fltGroups = c = Combo(parent=self.searchCont, options=grpOptions, name='flt_group', select=settings.user.ui.Get('corp_assets_filter_groups', None), callback=self.ComboChange, width=90, pos=(left,
             top,
             0,
             0))
            left += c.width + 4
            self.sr.fltItemType = c = SingleLineEditText(name='flt_exacttype', parent=self.searchCont, label=localization.GetByLabel('UI/Wallet/WalletWindow/ItemType'), setvalue=settings.user.ui.Get('corp_assets_filter_itemtype', ''), width=106, top=top, left=left, isTypeField=True)
            left += c.width + 4
            self.sr.fltQuantity = c = SingleLineEditInteger(name='flt_quantity', parent=self.searchCont, label=localization.GetByLabel('UI/Wallet/WalletWindow/MinQty'), setvalue=str(settings.user.ui.Get('corp_assets_filter_quantity', '')), width=60, top=top, left=left)
            left += c.width + 4
            c = self.sr.fltSearch = Button(parent=self.searchCont, label=localization.GetByLabel('UI/Common/Search'), func=self.Search, pos=(left,
             top,
             0,
             0), btn_default=1)
            self.PopulateGroupCombo(isSel=True)
            self.sr.search_inited = 1
        self.searchCont.state = uiconst.UI_PICKCHILDREN
        self.sr.scroll.Load(fixedEntryHeight=42, contentList=[], sortby='label', headers=uix.GetInvItemDefaultHeaders()[:], noContentHint=localization.GetByLabel('UI/Corporations/Assets/NoItemsFound'), showCollapseIcon=True)
        self.Search()

    def ComboChange(self, wnd, *args):
        if wnd.name == 'flt_category':
            self.PopulateGroupCombo()

    def PopulateGroupCombo(self, isSel = False):
        categoryID = self.sr.fltCategories.GetValue()
        groups = [(localization.GetByLabel('UI/Corporations/Assets/AllGroups'), None)]
        groupToSort = []
        if categoryID and evetypes.CategoryExists(categoryID):
            for groupID in evetypes.GetGroupIDsByCategory(categoryID):
                if evetypes.IsGroupPublishedByGroup(groupID):
                    groupName = evetypes.GetGroupNameByGroup(groupID)
                    groupToSort.append((groupName, (groupName, groupID)))

        groups += SortListOfTuples(groupToSort)
        sel = None
        if isSel:
            sel = settings.user.ui.Get('contracts_filter_groups', None)
        self.sr.fltGroups.LoadOptions(groups, sel)

    def ParseItemType(self, wnd, *args):
        if self.destroyed:
            return
        if not hasattr(self, 'parsingItemType'):
            self.parsingItemType = None
        typeID = DoParseItemType(wnd, self.parsingItemType)
        if typeID:
            self.parsingItemType = evetypes.GetName(typeID)
        return typeID

    def Search(self, *args):
        if self is None or self.destroyed:
            return
        sm.GetService('corpui').ShowLoad()
        self.sr.scroll.Load(fixedEntryHeight=42, contentList=[], sortby='label', headers=uix.GetInvItemDefaultHeaders()[:], showCollapseIcon=True)
        self.SetHint(localization.GetByLabel('UI/Common/Searching'))
        scrolllist = []
        try:
            itemTypeID = None
            itemCategoryID = None
            itemGroupID = None
            txt = self.sr.fltItemType.GetValue()
            if txt != '':
                for t in sm.GetService('contracts').GetMarketTypes():
                    if txt == t.typeName:
                        itemTypeID = t.typeID
                        break

                if not itemTypeID:
                    itemTypeID = self.ParseItemType(self.sr.fltItemType)
            txt = self.sr.fltGroups.GetValue()
            txtc = self.sr.fltCategories.GetValue()
            if txt and int(txt) > 0:
                itemGroupID = int(txt)
            elif txtc and int(txtc) > 0:
                itemCategoryID = int(txtc)
            qty = self.sr.fltQuantity.GetValue() or None
            try:
                qty = int(qty)
                if qty < 0:
                    qty = 0
            except:
                qty = None

            which = self.sr.fltType.GetValue() or None
            settings.user.ui.Set('corp_assets_filter_type', which)
            settings.user.ui.Set('corp_assets_filter_categories', itemCategoryID)
            settings.user.ui.Set('corp_assets_filter_groups', itemGroupID)
            settings.user.ui.Set('corp_assets_filter_itemtype', self.sr.fltItemType.GetValue())
            settings.user.ui.Set('corp_assets_filter_quantity', qty)
            rows = sm.RemoteSvc('corpmgr').SearchAssets(which, itemCategoryID, itemGroupID, itemTypeID, qty)
            ownerStations = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStations().Index('stationID')
            searchCond = utillib.KeyVal(categoryID=itemCategoryID, groupID=itemGroupID, typeID=itemTypeID, qty=qty)
            flag = FLAGNAME_TO_FLAG[which]
            self.SetHint(None)
            self.sr.scroll.allowFilterColumns = 1
            for row in rows:
                if row.locationID in ownerStations:
                    solarSystemID = ownerStations[row.locationID].solarSystemID
                else:
                    solarSystemID = cfg.evelocations.Get(row.locationID).solarSystemID
                    if solarSystemID is None:
                        structureInfo = sm.GetService('structureDirectory').GetStructureInfo(row.locationID)
                        solarSystemID = structureInfo.solarSystemID if structureInfo else row.locationID
                locationName = cfg.evelocations.Get(row.locationID).locationName
                try:
                    jumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(solarSystemID)
                    label = self._GetLocationLabel(solarSystemID, row.locationID, jumps)
                except:
                    log.LogException()
                    label = locationName

                entry = GetFromClass(ListGroup, {'GetSubContent': self.GetSubContent,
                 'label': label,
                 'groupItems': None,
                 'flag': flag,
                 'id': ('corpassets', row.locationID),
                 'tabs': [],
                 'state': 'locked',
                 'locationID': row.locationID,
                 'showicon': 'hide',
                 'MenuFunction': self.GetLocationMenu,
                 'searchCondition': searchCond,
                 'scrollID': self.sr.scroll.sr.id,
                 'charIndex': locationName})
                scrolllist.append((locationName, entry))
                uicore.registry.SetListGroupOpenState(('corpassets', row.locationID), 0)

            scrolllist = SortListOfTuples(scrolllist)
            self.sr.scroll.Load(fixedEntryHeight=42, contentList=scrolllist, sortby='label', headers=uix.GetInvItemDefaultHeaders(), noContentHint=localization.GetByLabel('UI/Corporations/Assets/NoItemsFound'), showCollapseIcon=True)
        finally:
            sm.GetService('corpui').HideLoad()

    def _GetLocationLabel(self, solarSystemID, locationID, jumps, itemCount = None):
        secStatus = solar_system_security_status(solarSystemID)
        isUnreachable = IsUnreachableJumpCount(jumps)
        if itemCount is None:
            if isUnreachable:
                path = 'UI/Corporations/Assets/LocationNoRoute'
            else:
                path = 'UI/Corporations/Assets/LocationAndJumps'
        elif isUnreachable:
            path = 'UI/Inventory/AssetsWindow/LocationDataLabelNoRoute'
        else:
            path = 'UI/Inventory/AssetsWindow/LocationDataLabel'
        return localization.GetByLabel(path, location=locationID, jumps=jumps, itemCount=itemCount, secStatus=secStatus)
