#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\assetsWindow.py
import sys
from collections import defaultdict
import blue
import eveicon
import evetypes
import localization
import log
import uthread
import uthread2
import utillib
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.message import ShowQuickMessage
from evePathfinder.core import IsUnreachableJumpCount
from carbonui import TextColor, uiconst
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.dpi import reverse_scale_dpi
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from carbonui.window.settings import WindowMarginMode
from eve.client.script.ui.control import eveScroll
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.control.listgroup import ListGroup
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.control.entries.universe import LocationGroup
from eve.client.script.ui.shared.assets.assetSafety import AssetSafetyCont
from eve.client.script.ui.shared.assets.assetSafetyControllers import SafetyControllerCharacter
from eve.client.script.ui.shared.assetsSearch import SearchBox
from eve.client.script.ui.shared.inventory.invWindow import Inventory as InventoryWindow
from eve.client.script.ui.shared.item import InvAssetItem
from eve.client.script.ui.util import uix
from eve.client.script.ui.util.uix import IsValidNamedItem
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers, eveCfg
from eve.common.script.sys.idCheckers import IsWormholeSystem, IsTriglavianSystem
from eveAssets.assetSearchUtil import SearchNamesHelper, AssetKeywordSearch, IsPartOfText, ParseString
from eveAssets.assetSearching import GetSearchResults, GetFakeRowset
from eveformat.client import solar_system_security_status
from eveservices.menu import GetMenuService, StartMenuService
from localization import GetByLabel
from menu import MenuLabel
from menucheckers.itemCheckers import ItemChecker
SORT_BY_NAME = 0
SORT_BY_JUMPS = 1
SORT_BY_ITEMS = 2
SORT_BY_OPTIONS = [(GetByLabel('UI/Common/Name'), SORT_BY_NAME), (GetByLabel('UI/Common/NumberOfJumps'), SORT_BY_JUMPS), (GetByLabel('UI/Common/NumberOfItems'), SORT_BY_ITEMS)]
TYPE_ALLITEMS = 'allitems'
TYPE_REGION = 'regitems'
TYPE_CONSTELLATION = 'conitems'
TYPE_SYSTEM = 'sysitems'
FILTER_TYPE_OPTIONS = ((GetByLabel('UI/Inventory/AssetsWindow/AllItems'), TYPE_ALLITEMS),
 (GetByLabel('UI/Common/LocationTypes/Region'), TYPE_REGION),
 (GetByLabel('UI/Common/LocationTypes/Constellation'), TYPE_CONSTELLATION),
 (GetByLabel('UI/Common/LocationTypes/SolarSystem'), TYPE_SYSTEM))
WINDOW_CAPTION_LABEL = 'UI/Inventory/AssetsWindow/PersonalAssets'
WINDOW_SUBCAPTION_LABEL = 'UI/Inventory/AssetsWindow/DelayedFiveMinutes'
NO_CONTENT_HIT_BY_KEY = {'allitems': GetByLabel('UI/Inventory/AssetsWindow/NoAssetsAtStation'),
 'regitems': GetByLabel('UI/Inventory/AssetsWindow/NoAssetsInRegion'),
 'conitems': GetByLabel('UI/Inventory/AssetsWindow/NoAssetsInConstellation'),
 'sysitems': GetByLabel('UI/Inventory/AssetsWindow/NoAssetsInSolarSystem')}
IMPORTANCE_NONE = 0
IMPORTANCE_PINNED = 1
IMPORTANCE_HIDDEN = -1

class AssetsWindow(Window):
    __guid__ = 'form.AssetsWindow'
    __notifyevents__ = ['OnDestinationSet']
    default_width = 550
    default_height = 450
    default_minSize = (395, 256)
    default_windowID = 'assets'
    default_captionLabelPath = 'Tooltips/Neocom/PersonalAssets'
    default_descriptionLabelPath = 'Tooltips/Neocom/PersonalAssets_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/assets.png'
    _update_delay_hint = None

    def __init__(self, **kwargs):
        self._loading_thread = None
        super(AssetsWindow, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        super(AssetsWindow, self).ApplyAttributes(attributes)
        self.pathfinder = sm.GetService('clientPathfinderService')
        self.key = None
        self.invalidateOpenState_regitems = 1
        self.invalidateOpenState_allitems = 1
        self.invalidateOpenState_conitems = 1
        self.invalidateOpenState_sysitems = 1
        self.safetyCont = None
        self.searchCont = None
        self.filterCont = None
        self.searchlist = None
        self.stationTabs = None
        self.searchEditBox = None
        self.filterValueCombo = None
        self.pending = None
        self.loading = 0
        self.station_inited = False
        self.search_inited = False
        self.filt_inited = False
        self.nameHelper = SearchNamesHelper(sm.GetService('ui'))
        self.assetKeywordSearch = AssetKeywordSearch(self.nameHelper, sm.GetService('ui'), sm.GetService('map'), sm.GetService('godma'), sm.GetService('structureDirectory'), localization, cfg)
        self.searchKeywords = self.assetKeywordSearch.GetSearchKeywords()
        if attributes.exactTypeID:
            autoSelectTab = False
            self.searchText = self.GetSearchTextForTypeID(attributes.exactTypeID)
        else:
            self.searchText = None
            autoSelectTab = True
        self.scrollPosition = defaultdict(float)
        self.ReconstructLayout(autoSelectTab)
        self._update_delay_hint = UpdateDelayHint(parent=self.header.extra_content, align=uiconst.TORIGHT, padding=self._get_update_delay_hint_padding())
        self.on_margin_mode_changed.connect(self._on_margin_mode_changed)
        self.on_stacked_changed.connect(self._on_stacked_changed)

    def _get_update_delay_hint_padding(self):
        if self.stacked:
            return (0, 0, 0, 0)
        else:
            return (8, 0, 8, 0)

    def _update_update_delay_hint_padding(self):
        if self._update_delay_hint:
            self._update_delay_hint.padding = self._get_update_delay_hint_padding()

    def _on_stacked_changed(self, window):
        self._update_update_delay_hint_padding()

    def OnDestinationSet(self, destinationID = None):
        self.ReconstructLayout()

    def ReloadTabs(self, *args):
        self.tabGroup.ReloadVisible()

    def ReconstructLayout(self, autoSelectTab = True, *args):
        self.station_inited = False
        self.search_inited = False
        self.filt_inited = False
        try:
            self.scrollPosition[self.key] = self.scroll.GetScrollProportion()
        except Exception:
            self.scrollPosition[self.key] = 0.0

        self._RecoverSearchText()
        self.sr.main.Flush()
        self.scroll = eveScroll.Scroll(parent=self.sr.main, padding=(0, 8, 0, 0))
        self.scroll.sr.id = 'assets'
        self.scroll.sr.minColumnWidth = {GetByLabel('UI/Common/Name'): 44}
        self.scroll.allowFilterColumns = 1
        self.scroll.OnNewHeaders = self.ReloadTabs
        self.scroll.sortGroups = True
        self.scroll.SetColumnsHiddenByDefault(uix.GetInvItemDefaultHiddenHeaders())
        self.tabGroup = self.header.tab_group
        self.ReconstructTabs()
        if autoSelectTab:
            self.tabGroup.AutoSelect(silently=True)

    def ReconstructTabs(self):
        tabs = [(GetByLabel(self.default_captionLabelPath),
          self.scroll,
          self,
          'allitems')]
        tabs += [(GetByLabel('UI/Common/Buttons/Search'),
          self.scroll,
          self,
          'search'), (GetByLabel('UI/Inventory/AssetSafety/AssetSafety'),
          self.scroll,
          self,
          'safety',
          None,
          GetByLabel('UI/Inventory/AssetSafety/AssetSafetyHint'))]
        self.tabGroup.Flush()
        for tab in tabs:
            self.tabGroup.AddTab(*tab)

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader()

    def _RecoverSearchText(self):
        assetSearchBox = self.searchEditBox
        if assetSearchBox:
            self.searchText = assetSearchBox.GetValue()

    def Load(self, key, reloadStationID = None):
        if self.loading:
            self.pending = (key, reloadStationID)
            return
        uthread.new(self._Load, key, reloadStationID)

    def _Load(self, key, reloadStationID = None):
        self.loading = 1
        self.pending = None
        if key != self.key:
            self.scrollPosition[self.key] = self.scroll.GetScrollProportion()
        self.key = key
        if self.safetyCont:
            self.safetyCont.display = False
        if key == 'safety':
            self.LoadAssetSafety()
        elif key[:7] == 'station':
            self.LoadCurrStation(key)
        elif key in ('allitems', 'regitems', 'conitems', 'sysitems'):
            self.LoadAssets(key)
        elif key == 'search':
            self.LoadSearch()
        self.loading = 0
        if self.pending:
            self.Load(*self.pending)

    def LoadAssetSafety(self):

        def Hide(cont):
            if cont:
                cont.display = False

        Hide(self.scroll)
        Hide(self.searchCont)
        Hide(self.filterCont)
        Hide(self.stationTabs)
        if self.safetyCont is None or self.safetyCont.destroyed:
            self.safetyCont = AssetSafetyCont(parent=self.sr.main, controller=SafetyControllerCharacter())
        self.safetyCont.display = True
        self.safetyCont.Load()

    def LoadCurrStation(self, key):
        if not self.station_inited:
            self.stationTabs = TabGroup(name='tabparent2', parent=self.sr.main, idx=2)
            tabs = [[GetByLabel('UI/Common/ItemTypes/Ships'),
              self.scroll,
              self,
              '%sships' % key],
             [GetByLabel('UI/Common/ItemTypes/Modules'),
              self.scroll,
              self,
              '%smodules' % key],
             [GetByLabel('UI/Common/ItemTypes/Charges'),
              self.scroll,
              self,
              '%scharges' % key],
             [GetByLabel('UI/Common/ItemTypes/Minerals'),
              self.scroll,
              self,
              '%sminerals' % key],
             [GetByLabel('UI/Common/Other'),
              self.scroll,
              self,
              '%sother' % key]]
            self.station_inited = 1
            self.stationTabs.Startup(tabs, 'assetsatstation', silently=True)
        if self.filterCont:
            self.filterCont.state = uiconst.UI_HIDDEN
        self.stationTabs.state = uiconst.UI_NORMAL
        if self.searchCont:
            self.searchCont.state = uiconst.UI_HIDDEN
        if key != 'station':
            self.ShowStationItems(key[7:])
        else:
            self.stationTabs.AutoSelect(1)

    def LoadAssets(self, key):
        if not self.filt_inited:
            self.ConstructFilterCont()
            self.filt_inited = True
        else:
            self.filterCont.Show()
        if self.stationTabs:
            self.stationTabs.Hide()
        if self.searchCont:
            self.searchCont.Hide()
        key = self.filterTypeCombo.GetValue()
        self.PopulateScroll(key, None, None)

    def ConstructFilterCont(self):
        self.filterCont = Container(name='filterContainer', align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, height=Combo.default_height, parent=self.sr.main, padding=self._get_top_cont_padding(), idx=self.scroll.GetOrder())
        self.sortByCombo = Combo(label=GetByLabel('UI/Common/SortBy'), parent=self.filterCont, options=SORT_BY_OPTIONS, name='sortcombo', align=uiconst.TORIGHT, select=None, callback=self.Filter, width=115, padRight=4)
        self.filterTypeCombo = Combo(name='filterTypeCombo', parent=self.filterCont, align=uiconst.TOLEFT, width=115, padRight=4, options=FILTER_TYPE_OPTIONS, select=settings.char.ui.Get('assets_window_filter_type', None), prefskey=('char', 'ui', 'assets_window_filter_type'), callback=self.OnFilterTypeCombo)
        self.filterValueCombo = Combo(parent=self.filterCont, options=[], name='filtcombo', select=None, callback=self.Filter, width=115, align=uiconst.TOLEFT, padRight=4)
        self.UpdateFilterValueComboVisibility()

    def OnFilterTypeCombo(self, *args):
        self.filterTypeCombo.UpdateSettings()
        self.UpdateFilterValueComboVisibility()
        self.Filter()

    def UpdateFilterValueComboVisibility(self):
        self.filterValueCombo.display = self.filterTypeCombo.GetValue() != TYPE_ALLITEMS

    def _get_top_cont_padding(self):
        if self.margin_mode == WindowMarginMode.COMPACT:
            return (0, 12, 0, 0)
        else:
            return (0, 4, 0, 0)

    def _on_margin_mode_changed(self, window):
        if self.searchCont is not None:
            self.searchCont.padding = self._get_top_cont_padding()
        if self.filterCont is not None:
            self.filterCont.padding = self._get_top_cont_padding()

    def LoadSearch(self):
        if self.stationTabs:
            self.stationTabs.state = uiconst.UI_HIDDEN
        if not self.search_inited:
            self.searchCont = Container(name='searchCont', align=uiconst.TOTOP, height=32, parent=self.sr.main, idx=self.scroll.GetOrder(), padding=self._get_top_cont_padding())
            Container(name='comboCont', align=uiconst.TOLEFT, parent=self.searchCont, width=108)
            self.sortByCombosearch = Combo(label=GetByLabel('UI/Common/SortBy'), parent=self.searchCont, options=SORT_BY_OPTIONS, name='sortcombosearch', select=settings.char.ui.Get('assetsSearchSortKey', None), callback=self.Search, width=100, pos=(0, 0, 0, 0))
            buttonCont = ContainerAutoSize(name='bottonCont', parent=self.searchCont, align=uiconst.TORIGHT)
            infoIcon = MoreInfoIcon(name='infoIcon', parent=buttonCont, align=uiconst.CENTERRIGHT)
            infoIcon.LoadTooltipPanel = self.LoadInfoTooltip
            button = Button(name='searchButton', parent=buttonCont, align=uiconst.CENTERRIGHT, left=infoIcon.left + infoIcon.width + 8, label=GetByLabel('UI/Common/Buttons/Search'), func=self.Search)
            self.searchEditBox = SearchBox(name='assetssearchtype', parent=self.searchCont, align=uiconst.TOALL, width=0, padding=(0, 0, 8, 0), label=GetByLabel('UI/Common/SearchText'), maxLength=100, OnReturn=self.Search, keywords=self.searchKeywords, isTypeField=True)
            self.searchEditBox.SetValueAfterDragging = self.SetSearchTypeValueAfterDragging
            self._RestoreSearchText()
            self.search_inited = 1
        if self.filterCont:
            self.filterCont.state = uiconst.UI_HIDDEN
        self.searchCont.state = uiconst.UI_PICKCHILDREN
        sortKeySearch = settings.char.ui.Get('assetsSearchSortKey', None)
        searchlist = getattr(self, 'searchlist', [])
        if searchlist:
            self._start_loading_thread(self._LoadSearch, sortKeySearch)
        else:
            self.Search()

    def SetSearchTypeValueAfterDragging(self, name, draggedValue):
        name = self.GetSearchTextForTypeID(draggedValue)
        SearchBox.SetValueAfterDragging(self.searchEditBox, name, draggedValue)

    def _RestoreSearchText(self):
        if self.searchText:
            searchBox = self.searchEditBox
            if searchBox:
                searchBox.SetValue(self.searchText)

    def Filter(self, *args):
        key = self.filterTypeCombo.GetValue()
        keyID = self.filterValueCombo.GetValue()
        sortKey = self.sortByCombo.GetValue()
        self.PopulateScroll(key, keyID, sortKey)

    def GetConditions(self, advancedMatches):
        conditions = []
        for word, value in advancedMatches:
            try:
                for kw in self.searchKeywords:
                    if IsPartOfText(kw.keyword, word):
                        kw.matchFunction(conditions, value)
                        break

            except:
                import log
                log.LogException()
                sm.GetService('assets').LogInfo('Failed parsing keyword', word, 'value', value, 'and happily ignoring it')

        return conditions

    def Search(self, *args):
        self._start_loading_thread(self.Search_thread)

    def Search_thread(self, *args):
        self.ShowLoad()
        try:
            if self.tabGroup.GetSelectedArgs() == 'search':
                self.scroll.Load(contentList=[], noContentHint=GetByLabel('UI/Common/GettingData'))
            blue.pyos.synchro.Yield()
            log.LogNotice('Asset Search - fetch items')
            invContainer = sm.GetService('invCache').GetInventory(const.containerGlobal)
            allitems = invContainer.ListIncludingContainers()
            log.LogNotice('Asset Search - items fetched =', len(allitems))
            itemRowset = GetFakeRowset(allitems)
            log.LogNotice('Asset Search - fake rows created')
            blue.pyos.synchro.Yield()
            if self.tabGroup.GetSelectedArgs() == 'search':
                self.scroll.Load(contentList=[], noContentHint=GetByLabel('UI/Common/Searching'))
            blue.pyos.synchro.Yield()
            searchtype = unicode(self.searchEditBox.GetValue() or '').lower()
            searchtype, advancedMatches = ParseString(searchtype)
            conditions = self.GetConditions(advancedMatches)
            self.assetKeywordSearch.ResetPerRunDicts()
            allContainersByItemIDs, itemsByContainerID, stations = GetSearchResults(conditions, itemRowset, searchtype)
            containersInfoByStations = defaultdict(lambda : defaultdict(tuple))
            for containerID, itemsInContainer in itemsByContainerID.iteritems():
                containerItem = allContainersByItemIDs.get(containerID)
                if containerItem and containerItem.typeID == const.typePlasticWrap:
                    continue
                if containerItem:
                    containersInfoByStations[containerItem.locationID][containerID] = (containerItem, itemsInContainer)

            for stationID in containersInfoByStations.iterkeys():
                stations[stationID].extend([])

            sortlocations = []
            ownerStations = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStations().Index('stationID')
            for stationID, stationItems in stations.iteritems():
                stationData = ownerStations.get(stationID, None)
                if stationData is None:
                    continue
                stationsContainersInfo = containersInfoByStations.get(stationID, {})
                sortlocations.append((stationData.solarSystemID,
                 stationID,
                 stationItems,
                 stationsContainersInfo))

            sortlocations.sort()
            sortlocations = sortlocations
            self.searchlist = sortlocations
            sortKey = self.sortByCombosearch.GetValue()
            self._LoadSearch(sortKey)
        finally:
            self.HideLoad()

    def PopulateScroll(self, key, keyID, sortKey, *args):
        if keyID is None:
            keyID = settings.char.ui.Get('assetsKeyID_%s' % key, None)
        oldSortKey = settings.char.ui.Get('assetsSortKey', None)
        if sortKey is not None:
            if oldSortKey != sortKey:
                for k in self.scrollPosition.keys():
                    self.scrollPosition[k] = 0.0

        else:
            sortKey = oldSortKey
        settings.char.ui.Set('assetsKeyID_%s' % key, keyID)
        settings.char.ui.Set('assetsSortKey', sortKey)
        self.ShowLoad()
        self.SetHint()
        closed = [0, 1][getattr(self, 'invalidateOpenState_%s' % key, 0)]
        sortlocations = sm.GetService('assets').GetAll(key, keyID=keyID, sortKey=sortKey)
        try:
            options = self.GetFilterValueComboOptions(key)
            self.filterValueCombo.LoadOptions(options, None)
            if keyID:
                self.filterValueCombo.SelectItemByLabel(cfg.evelocations.Get(keyID).name)
            if sortKey:
                self.sortByCombo.SelectItemByIndex(sortKey)
        except (Exception,):
            sys.exc_clear()

        allImportanceSettings = settings.char.ui.Get('assets_window_importance', {})
        destPathList = sm.GetService('starmap').GetDestinationPath()
        scrolllist = []
        hiddenEntries = []
        for solarsystemID, station in sortlocations:
            importanceValue = allImportanceSettings.get(station.stationID, IMPORTANCE_NONE)
            data = self.GetLocationData(solarsystemID, station, key, forceClosed=closed, scrollID=self.scroll.sr.id, sortKey=sortKey, path=destPathList, importanceValue=importanceValue)
            blue.pyos.BeNice()
            entry = GetFromClass(LocationGroup, data)
            if importanceValue == IMPORTANCE_HIDDEN:
                hiddenEntries.append(entry)
            else:
                scrolllist.append(entry)

        if hiddenEntries:
            scrolllist.append(self.GetHiddenEntry(hiddenEntries))
        if self.destroyed:
            return
        setattr(self, 'invalidateOpenState_%s' % key, 0)
        scrollPosition = self.scrollPosition[key]
        self.scroll.Load(contentList=scrolllist, headers=uix.GetInvItemDefaultHeaders(), noContentHint=NO_CONTENT_HIT_BY_KEY[key], scrollTo=scrollPosition, showCollapseIcon=True)
        self.HideLoad()

    def GetHiddenSubContent(self, nodedata, *args):
        return nodedata.groupItems

    def GetHiddenEntry(self, hiddenEntries):
        data = {'GetSubContent': self.GetHiddenSubContent,
         'label': 'Hidden',
         'groupItems': hiddenEntries,
         'id': 'assetslocations_hiddenEntries',
         'state': 'locked',
         'showicon': eveicon.hidden,
         'showlen': 1,
         'BlockOpenWindow': 1}
        return GetFromClass(ListGroup, data)

    def GetFilterValueComboOptions(self, key):
        key = self.filterTypeCombo.GetValue()
        options = [(GetByLabel('UI/Common/Current'), 0)]
        opts = {}
        for r in sm.GetService('assets').locationCache.iterkeys():
            if key == 'regitems' and idCheckers.IsRegion(r) or key == 'conitems' and idCheckers.IsConstellation(r) or key == 'sysitems' and idCheckers.IsSolarSystem(r):
                opts[cfg.evelocations.Get(r).name] = r

        keys = opts.keys()
        keys.sort()
        for k in keys:
            options.append((k, opts[k]))

        return options

    def ShowStationItems(self, key):
        self.ShowLoad()
        hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
        items = hangarInv.List(const.flagHangar)
        if not len(items):
            self.SetHint(GetByLabel('UI/Inventory/AssetsWindow/NoAssets'))
            return
        assetsList = []
        self.scroll.Load(fixedEntryHeight=42, contentList=[], headers=uix.GetInvItemDefaultHeaders())
        itemname = ' ' + key
        itemSet = set()
        for each in items:
            if each.flagID not in (const.flagHangar, const.flagWallet):
                continue
            if key == 'ships':
                if each.categoryID != const.categoryShip:
                    continue
            elif key == 'modules':
                if not evetypes.IsCategoryHardwareByCategory(evetypes.GetCategoryID(each.typeID)):
                    continue
            elif key == 'minerals':
                if each.groupID != const.groupMineral:
                    continue
            elif key == 'charges':
                if each.categoryID != const.categoryCharge:
                    continue
            else:
                itemname = None
                if each.categoryID == const.categoryShip or evetypes.IsCategoryHardwareByCategory(evetypes.GetCategoryID(each.typeID)) or each.groupID == const.groupMineral or each.categoryID == const.categoryCharge:
                    continue
            itemSet.add(each)

        self.PrimeLocationNames(itemSet)
        for eachItem in itemSet:
            assetsList.append(GetFromClass(InvAssetItem, uix.GetItemData(eachItem, 'details', scrollID=self.scroll.sr.id)))

        locText = {'ships': GetByLabel('UI/Inventory/AssetsWindow/NoShipsAtStation'),
         'modules': GetByLabel('UI/Inventory/AssetsWindow/NoModulesAtStation'),
         'minerals': GetByLabel('UI/Inventory/AssetsWindow/NoMineralsAtStation'),
         'charges': GetByLabel('UI/Inventory/AssetsWindow/NoChargesAtStation')}
        if not assetsList:
            if not itemname:
                self.SetHint(GetByLabel('UI/Inventory/AssetsWindow/NoAssetsInCategoryAtStation'))
            else:
                self.SetHint(locText[key])
        else:
            self.SetHint()
        self.scroll.Load(contentList=assetsList, sortby='label', headers=uix.GetInvItemDefaultHeaders(), noContentHint=GetByLabel('UI/Common/NothingFound'))
        self.HideLoad()

    def GetLocationData(self, solarsystemID, station, key, forceClosed = 0, scrollID = None, sortKey = None, fakeItems = None, path = (), importanceValue = IMPORTANCE_NONE):
        isHidden = importanceValue == IMPORTANCE_HIDDEN
        isPinned = importanceValue == IMPORTANCE_PINNED
        location = cfg.evelocations.Get(station.stationID)
        if forceClosed:
            uicore.registry.SetListGroupOpenState(('assetslocations_%s' % key, location.locationID), 0)
        autopilotNumJumps = self.pathfinder.GetAutopilotJumpCount(session.solarsystemid2, solarsystemID)
        itemCount = fakeItems or station.itemCount
        secStatus = solar_system_security_status(solarsystemID)
        if IsUnreachableJumpCount(autopilotNumJumps):
            label = GetByLabel('UI/Inventory/AssetsWindow/LocationDataLabelNoRoute', location=location.locationID, itemCount=itemCount, secStatus=secStatus)
        elif key is not 'sysitems':
            label = GetByLabel('UI/Inventory/AssetsWindow/LocationDataLabel', location=location.locationID, itemCount=itemCount, jumps=autopilotNumJumps, secStatus=secStatus)
        else:
            label = GetByLabel('UI/Inventory/AssetsWindow/LocationDataLabelNoJump', location=location.locationID, itemCount=itemCount, secStatus=secStatus)
        if sortKey == SORT_BY_JUMPS:
            sortVal = (-isPinned,
             autopilotNumJumps,
             location.name,
             itemCount)
        elif sortKey == SORT_BY_ITEMS:
            sortVal = (-isPinned,
             -itemCount,
             location.name,
             autopilotNumJumps)
        else:
            sortVal = (-isPinned,
             location.name,
             itemCount,
             autopilotNumJumps)
        inMyPath = self._IsInMyPath(path, solarsystemID, location.locationID)
        sublevel = 1 if isHidden else 0
        data = {'GetSubContent': self.GetSubContent,
         'DragEnterCallback': self.OnGroupDragEnter,
         'DeleteCallback': self.OnGroupDeleted,
         'MenuFunction': self.GetMenuLocationMenu,
         'GetDragDataFunc': self.GetLocationDragData,
         'label': label,
         'jumps': autopilotNumJumps,
         'itemCount': station.itemCount,
         'groupItems': [],
         'id': ('assetslocations_%s' % key, location.locationID),
         'tabs': [],
         'state': 'locked',
         'location': location,
         'showicon': 'hide',
         'showlen': 0,
         'key': key,
         'scrollID': scrollID,
         'inMyPath': inMyPath,
         'itemID': station.stationID,
         'upkeepState': getattr(station, 'upkeepState', None),
         'charIndex': location.name,
         'sublevel': sublevel}
        if isPinned:
            data['rightIconInfo'] = (eveicon.pinned, GetByLabel('UI/Inventory/AssetsWindow/PinnedLocation'))
        headers = uix.GetInvItemDefaultHeaders()
        for each in headers:
            data['sort_%s' % each] = sortVal

        return data

    def _IsInMyPath(self, path, solarsystemID, locationID):
        if solarsystemID in path:
            return True
        if locationID in path:
            return True
        if not eveCfg.IsDocked() and solarsystemID == session.solarsystemid2:
            return True
        return False

    def GetLocationDragData(self, node):
        solarSystemID, stationTypeID = self.GetStationSolarSystemIDAndTypeID(node)
        stationInfo = sm.GetService('ui').GetStationStaticInfo(node.itemID)
        if stationInfo:
            node['typeID'] = stationInfo.stationTypeID
            node['genericDisplayLabel'] = cfg.evelocations.Get(node.itemID).name
        elif stationTypeID:
            node['typeID'] = stationTypeID
            node['genericDisplayLabel'] = cfg.evelocations.Get(node.itemID).name
        return [node]

    def GetContainerSubContent(self, nodedata, *args):
        scrollList = []
        self.PrimeLocationNames(nodedata.groupItems)
        for each in nodedata.groupItems:
            data = uix.GetItemData(each, 'details', scrollID=nodedata.scrollID)
            data.sublevel = nodedata.sublevel
            scrollList.append(GetFromClass(InvAssetItem, data))

        return scrollList

    def GetContainerMenu(self, node):
        return GetMenuService().InvItemMenu(node.item)

    def OnDblClickContainer(self, groupEntry):
        nodedata = groupEntry.sr.node
        if ItemChecker(nodedata.item).IsInPilotLocation():
            invID = ('StationContainer', nodedata.itemID)
            InventoryWindow.OpenOrShow(invID=invID, openFromWnd=self)

    def GetContainerGroupEntries(self, containersInfo, scrollID):
        scrollList = []
        cfg.evelocations.Prime(containersInfo.keys())
        for containerID, infoOnContainer in containersInfo.iteritems():
            containerItem, itemsInContainer = infoOnContainer
            scrollList.append(GetFromClass(ListGroup, {'GetSubContent': self.GetContainerSubContent,
             'label': uix.GetItemName(containerItem),
             'MenuFunction': self.GetContainerMenu,
             'groupItems': itemsInContainer,
             'id': ('assetslocations_%s' % containerID, containerID),
             'state': 'locked',
             'showicon': 'hide',
             'showlen': 1,
             'itemID': containerID,
             'item': containerItem,
             'sublevel': 1,
             'scrollID': scrollID,
             'OnDblClick': self.OnDblClickContainer}))

        return scrollList

    def GetSubContent(self, data, *args):
        if data.key == 'search':
            scrolllist = []
            items = []
            containersInfo = {}
            for solarsystemID, stationID, stationItems, stationsContainersInfo in self.searchlist:
                if stationID == data.location.locationID:
                    items = stationItems
                    containersInfo = stationsContainersInfo
                    break

            self.PrimeLocationNames(items)
            groupEntries = self.GetContainerGroupEntries(containersInfo, data.scrollID)
            scrolllist.extend(groupEntries)
            for each in items:
                if each.flagID not in (const.flagHangar, const.flagWallet, const.flagAssetSafety):
                    continue
                scrolllist.append(GetFromClass(InvAssetItem, uix.GetItemData(each, 'details', scrollID=data.scrollID)))
                blue.pyos.BeNice()

            return scrolllist
        sublevel = data.get('sublevel', 0)
        if session.stationid and data.location.locationID in (session.stationid, session.structureid):
            hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
            items = hangarInv.List()
            scrolllist = []
            self.PrimeLocationNames(items)
            for each in items:
                if each.flagID not in (const.flagHangar, const.flagWallet, const.flagAssetSafety):
                    continue
                scrolllist.append(GetFromClass(InvAssetItem, uix.GetItemData(each, 'details', scrollID=data.scrollID, sublevel=sublevel)))

            return scrolllist
        items = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStationItems(data.location.locationID)
        badLocations = [const.locationTemp, const.locationSystem, eve.session.charid]
        scrolllist = []
        self.PrimeLocationNames(items)
        for each in items:
            if idCheckers.IsJunkLocation(each.locationID) or each.locationID in badLocations:
                continue
            if each.stacksize == 0:
                continue
            data = uix.GetItemData(each, 'details', scrollID=data.scrollID, sublevel=sublevel)
            if idCheckers.IsStation(each.locationID):
                station = sm.GetService('ui').GetStationStaticInfo(each.locationID)
                if station:
                    data.factionID = sm.GetService('faction').GetFactionOfSolarSystem(station.solarSystemID)
            scrolllist.append(GetFromClass(InvAssetItem, data))

        return scrolllist

    def PrimeLocationNames(self, items):
        itemLocationToPrime = set()
        for each in items:
            if IsValidNamedItem(each):
                itemLocationToPrime.add(each.itemID)

        cfg.evelocations.Prime(itemLocationToPrime)

    def UpdateLite(self, stationID, key, fromID):
        if not self or self.destroyed:
            return
        self.ShowLoad()
        try:
            destPathList = sm.GetService('starmap').GetDestinationPath()
            assetStations = sm.GetService('assets').GetStations().Index('stationID')
            searchKey = 'assetslocations_%s' % key
            affectedNodes = [ node for node in self.scroll.GetNodes() if node.Get('id', None) in ((searchKey, stationID), (searchKey, fromID)) ]
            for node in affectedNodes:
                locationID = node.Get('id')[1]
                station = assetStations.get(locationID, None)
                if station is None:
                    station = utillib.KeyVal(solarSystemID=node.location.solarSystemID, stationID=locationID, itemCount=node.itemCount)
                node.data = self.GetLocationData(station.solarSystemID, station, key, scrollID=self.scroll.sr.id, path=destPathList)
                if node.panel:
                    node.panel.Load(node)
                self.scroll.PrepareSubContent(node)
                self.scroll.ScrollToProportion(self.scroll.GetScrollProportion())

        finally:
            self.ReconstructLayout()
            self.HideLoad()

    def ShowSearch(self, sortKey = None, *args):
        uthread2.start_tasklet(self._LoadSearch, sortKey)

    def _LoadSearch(self, sortKey):
        if sortKey is None:
            sortKey = settings.char.ui.Get('assetsSearchSortKey', None)
        settings.char.ui.Set('assetsSearchSortKey', sortKey)
        if sortKey:
            self.sortByCombosearch.SelectItemByIndex(sortKey)
        self.SetHint()
        self.scroll.ShowLoading()
        try:
            scrolllist = []
            searchlist = getattr(self, 'searchlist', []) or []
            sortedList = []
            for solarsystemID, stationID, items, stationsContainersInfo in searchlist:
                numContainerItems = sum([ len(y) for x, y in stationsContainersInfo.values() ])
                station = utillib.KeyVal()
                station.stationID = stationID
                station.solarsystemID = solarsystemID
                station.stationName = cfg.evelocations.Get(stationID).name
                station.itemCount = len(items) + numContainerItems
                sortedList.append(station)

            allImportanceSettings = settings.char.ui.Get('assets_window_importance', {})
            destPathList = sm.GetService('starmap').GetDestinationPath()
            hiddenEntries = []
            for station in sortedList:
                importanceValue = allImportanceSettings.get(station.stationID, IMPORTANCE_NONE)
                data = self.GetLocationData(station.solarsystemID, station, 'search', scrollID=self.scroll.sr.id, sortKey=sortKey, path=destPathList, importanceValue=importanceValue)
                entry = GetFromClass(LocationGroup, data)
                if importanceValue == IMPORTANCE_HIDDEN:
                    hiddenEntries.append(entry)
                else:
                    scrolllist.append(entry)
                blue.pyos.BeNice()

            if hiddenEntries:
                scrolllist.append(self.GetHiddenEntry(hiddenEntries))
            scrollPosition = 0
            if self.tabGroup.GetSelectedArgs() == 'search':
                scrollPosition = self.scrollPosition.get('search', 0)
            self.scroll.Load(contentList=scrolllist, headers=uix.GetInvItemDefaultHeaders(), noContentHint=GetByLabel('UI/Common/NothingFound'), scrollTo=scrollPosition, showCollapseIcon=True)
        finally:
            self.scroll.HideLoading()
            self.HideLoad()

    def GetMenuLocationMenu(self, node):
        locationID = node.location.locationID
        solarSystemID, stationTypeID = self.GetStationSolarSystemIDAndTypeID(node)
        menu = StartMenuService().CelestialMenu(node.location.locationID, typeID=stationTypeID, parentID=solarSystemID)
        menu += self._GetImportanceMenu(locationID, solarSystemID)
        if not idCheckers.IsStation(locationID):
            if session.structureid != locationID:
                if IsWormholeSystem(solarSystemID) or IsTriglavianSystem(solarSystemID):
                    label = MenuLabel('UI/Inventory/AssetSafety/MoveItemsToSpace')
                else:
                    label = MenuLabel('UI/Inventory/AssetSafety/MoveItemsToSafety')
                menu.append((label, self.MoveItemsInStructureToAssetSafety, (solarSystemID, locationID)))
        return menu

    def _GetImportanceMenu(self, locationID, solarSystemID):
        m = MenuData()
        importanceSetting = settings.char.ui.Get('assets_window_importance', {}).get(locationID, None)
        if importanceSetting == IMPORTANCE_PINNED:
            label = MenuLabel('UI/Inventory/AssetsWindow/UnpinPersonalAssets')
            m.AddEntry(label, lambda : self.Unpin(locationID), texturePath=eveicon.unpin)
        elif importanceSetting == IMPORTANCE_HIDDEN:
            label = MenuLabel('UI/Inventory/AssetsWindow/UnhidePersonalAssets')
            m.AddEntry(label, lambda : self.Unhide(locationID), texturePath=eveicon.hidden)
        else:
            label = MenuLabel('UI/Inventory/AssetsWindow/PinPersonalAssets')
            m.AddEntry(label, lambda : self.Pin(locationID), texturePath=eveicon.pinned)
            label = MenuLabel('UI/Inventory/AssetsWindow/HidePersonalAssets')
            m.AddEntry(label, lambda : self.Hide(locationID), texturePath=eveicon.visibility)
        return m

    def Pin(self, locationID, *args):
        if self._SetLocationImportance(locationID, IMPORTANCE_PINNED):
            ShowQuickMessage(GetByLabel('UI/Inventory/AssetsWindow/PersonalAssetLocationPinned'))

    def Unpin(self, locationID, *args):
        if self._SetLocationImportance(locationID, IMPORTANCE_NONE):
            ShowQuickMessage(GetByLabel('UI/Inventory/AssetsWindow/PersonalAssetLocationUnpinned'))

    def Hide(self, locationID, *args):
        if self._SetLocationImportance(locationID, IMPORTANCE_HIDDEN):
            ShowQuickMessage(GetByLabel('UI/Inventory/AssetsWindow/PersonalAssetLocationHidden'))

    def Unhide(self, locationID, *args):
        if self._SetLocationImportance(locationID, IMPORTANCE_NONE):
            ShowQuickMessage(GetByLabel('UI/Inventory/AssetsWindow/PersonalAssetLocationUnhidden'))

    def _SetLocationImportance(self, locationID, newImportanceValue):
        allImportanceSettings = settings.char.ui.Get('assets_window_importance', {})
        importanceSetting = allImportanceSettings.get(locationID, IMPORTANCE_NONE)
        if importanceSetting == newImportanceValue:
            return False
        if newImportanceValue == IMPORTANCE_NONE:
            allImportanceSettings.pop(locationID, None)
        else:
            allImportanceSettings[locationID] = newImportanceValue
        settings.char.ui.Set('assets_window_importance', allImportanceSettings)
        self.ReloadTabs()
        return True

    def GetStationSolarSystemIDAndTypeID(self, node):
        locationID = node.location.locationID
        solarSystemID = stationTypeID = None
        if idCheckers.IsStation(locationID):
            stationInfo = sm.GetService('ui').GetStationStaticInfo(locationID)
            stationTypeID = stationInfo.stationTypeID
            solarSystemID = stationInfo.solarSystemID
        else:
            stations = sm.GetService('invCache').GetInventory(const.containerGlobal).ListStations()
            for station in stations:
                if station.stationID == locationID:
                    stationTypeID = station.typeID
                    solarSystemID = station.solarSystemID
                    break

        return (solarSystemID, stationTypeID)

    def MoveItemsInStructureToAssetSafety(self, solarSystemID, structureID):
        sm.GetService('assetSafety').MoveItemsInStructureToAssetSafetyForCharacter(solarSystemID, structureID)

    def SetHint(self, hintstr = None):
        if self.scroll:
            self.scroll.ShowHint(hintstr)

    def OnGroupDeleted(self, ids):
        pass

    def OnGroupDragEnter(self, group, drag):
        pass

    def LoadInfoTooltip(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.cellSpacing = 1
        tooltipPanel.AddLabelLarge(text=GetByLabel('UI/Inventory/AssetsWindow/AdvancedSearch'), colSpan=2)
        tooltipPanel.AddLabelMedium(text='<b>%s' % GetByLabel('UI/Inventory/AssetsWindow/AdvancedSearchKeywords'))
        tooltipPanel.AddLabelMedium(wrapWidth=200, text='<b>%s' % GetByLabel('UI/Inventory/AssetsWindow/AdvancedSearchHints'), padLeft=20)
        for keywordOption in self.searchKeywords:
            tooltipPanel.AddLabelSmall(text='<b>%s:</b>' % keywordOption.keyword, opacity=0.85)
            tooltipPanel.AddLabelSmall(wrapWidth=200, text=keywordOption.optionDescription, padLeft=20, opacity=0.75)

        tooltipPanel.AddSpacer(width=0, height=10, colSpan=3)
        tooltipPanel.AddLabelMedium(text='<b>%s:' % GetByLabel('UI/Inventory/AssetsWindow/AdvancedSearchExamples'), colSpan=3)
        text = '%s:%s' % (GetByLabel('UI/Inventory/AssetSearch/KeywordType'), evetypes.GetName(1230)[:5])
        tooltipPanel.AddLabelSmall(text=text, opacity=0.75, colSpan=3, padLeft=10)
        text = '%s:%s %s:2 %s:9 %s:0.9' % (GetByLabel('UI/Inventory/AssetSearch/KeywordCategory'),
         evetypes.GetCategoryNameByCategory(const.categoryShip),
         GetByLabel('UI/Inventory/AssetSearch/KeywordTechLevel'),
         GetByLabel('UI/Inventory/AssetSearch/KeywordMetalevel'),
         GetByLabel('UI/Inventory/AssetSearch/KeywordMinSecurityLevel'))
        tooltipPanel.AddLabelSmall(text=text, opacity=0.75, colSpan=2, padLeft=10)

    def SearchTypeID(self, typeID):
        self.tabGroup.SelectByID('search')
        searchText = self.GetSearchTextForTypeID(typeID)
        if self.search_inited:
            self.searchEditBox.SetValue(searchText)
        self.searchText = searchText
        self.Search()

    def GetSearchTextForTypeID(self, typeID):
        return '%s:%s' % (GetByLabel('UI/Inventory/AssetSearch/KeywordTypeExact'), evetypes.GetName(typeID))

    def UnloadTabPanel(self, args, panel, tabgroup):
        self._kill_loading_thread_maybe()

    def _start_loading_thread(self, func, *args, **kwargs):
        self._kill_loading_thread_maybe()

        def loading_thread():
            try:
                func(*args, **kwargs)
            finally:
                self._loading_thread = None

        self._loading_thread = uthread2.start_tasklet(loading_thread)

    def _kill_loading_thread_maybe(self):
        if self._loading_thread is not None:
            self._loading_thread.kill()

    def ShowLoad(self, doBlock = True):
        pass

    def HideLoad(self):
        pass


class UpdateDelayHint(ContainerAutoSize):
    ICON_SIZE = 16
    _visible = True

    def __init__(self, **kwargs):
        super(UpdateDelayHint, self).__init__(**kwargs)
        self._layout()

    def _layout(self):
        Sprite(parent=self, align=uiconst.CENTER, width=self.ICON_SIZE, height=self.ICON_SIZE, texturePath=eveicon.clock, hint=localization.GetByLabel('UI/Inventory/AssetsWindow/CachedFor5Min'), color=TextColor.DISABLED)

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        required_budget = self.left + self.padLeft + self.ICON_SIZE + self.padRight
        if reverse_scale_dpi(budgetWidth) < required_budget:
            if self._visible:
                self._visible = False
                animations.FadeOut(self, duration=0.3)
        elif not self._visible:
            self._visible = True
            animations.FadeIn(self, duration=0.3)
        return super(UpdateDelayHint, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
