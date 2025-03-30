#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\marketbase.py
import sys
from collections import defaultdict
import eveicon
import blue
import telemetry
import carbonui.const as uiconst
import dogma.data
import utillib
from carbon.common.script.sys.serviceConst import ROLEMASK_ELEVATEDPLAYER
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import FmtAmt
from carbonui import AxisAlignment, ButtonVariant, Density, fontconst, TextColor
from carbonui.control.dragdrop.dragdata import TypeDragData
from carbonui.control.scroll_const import SortDirection
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.decorative.divider_line import DividerLine
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.sprite import Sprite
from carbonui.util.bunch import Bunch
from carbonui.util.various_unsorted import ConvertDecimal, GetClipboardData
from dogma.const import attributeDataTypeTypeMirror
from carbonui.button.group import ButtonGroup
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.divider import Divider
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveTabgroupUtil import FixedTabName
from carbonui.control.window import Window
from eve.client.script.ui.control.listgroup import ListGroup
from carbonui.control.tabGroup import TabGroup, GetTabData
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.cloneGrade import ORIGIN_MARKET
from eve.client.script.ui.shared.cloneGrade.omegaCloneOverlayIcon import OmegaCloneOverlayIcon
import evetypes
import inventorycommon.typeHelpers
import localization
import log
import threadutils
from eve.client.script.ui.shared.market.entries import GenericMarketItem, MarketMetaGroupEntry, MarketOrder, QuickbarGroup, QuickbarItem, MarketListGroup
from eve.client.script.ui.shared.market.wallet_balance import get_wallet_balance_options_menu, WalletBalance
from eve.client.script.ui.util import uix, utilWindows
import uthread
import uthread2
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control import eveLabel, eveScroll
from eve.client.script.ui.control.eveImage import Image
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.listwindow import ListWindow
from carbonui.control.button import Button
from eve.client.script.ui.shared.fitting.fittingUtil import FITKEYS
from eve.client.script.ui.shared.market import GetTypeIDFromDragItem
from eve.client.script.ui.shared.market.requirements import RequirementsContainer
from eve.client.script.ui.shared.market.ticker import MarketTicker, ticker_enabled_setting
from eve.client.script.ui.shared.traits import TraitsContainer, HasTraits
from eve.common.lib import appConst as const
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.util import industryCommon
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions import ExceptionEater, UserError
import expertSystems.client
from fastcheckout.client.purchasepanels.purchaseButton import PurchaseButton
from fsdBuiltData.common.iconIDs import GetIconFile
from inventoryrestrictions import can_view_market_details
from localization import GetByLabel
from marketgroups.data import MarketGroupObject
from marketutil import ConvertTuplesToBestByOrders
from marketutil.const import MAX_ORDER_PRICE
from marketutil.quickbarUtil import TICKER_SETTING_NAME
import metaGroups
from shipfitting.multiBuyUtil import BuyMultipleTypesWithQty
from fastcheckout.const import FROM_MARKET_WINDOW, FROM_PLEX_MARKET_GROUP
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
from menu import MenuLabel
from eveprefs import boot
from textImporting import IsUsingDefaultLanguage
from textImporting.exportQuickbar import QuickbarExporter
from textImporting.importQuickbar import QuickbarImporter
from textImporting.textToTypeIDFinder import SEARCH_LOCALIZED, SEARCH_BOTH
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
ACTION_ICON = 'res:/UI/Texture/classes/UtilMenu/BulletIcon.png'
INFINITY = 999999999999999999L
MARKET_NES_BUTTON_ANALYTIC_ID = 'MarketNESButton'
CATEGORIES_WITH_FACTION_AND_STORYLINE_SUBFOLDERS = (const.categoryModule,
 const.categoryStructureModule,
 const.categoryDrone,
 const.categoryStarbase,
 const.categoryFighter)

def GetNumericValueFromSetting(configName, defaultValue = 0):
    value = settings.user.ui.Get(configName, defaultValue)
    if value == '-':
        return defaultValue
    return value


class RegionalMarket(Window):
    __guid__ = 'form.RegionalMarket'
    __notifyevents__ = ['OnSessionChanged']
    default_width = 900
    default_height = 768
    default_windowID = 'market'
    default_captionLabelPath = 'Tooltips/StationServices/Market'
    default_descriptionLabelPath = 'Tooltips/StationServices/Market_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/market.png'
    default_minSize = (650, 435)
    default_apply_content_padding = False

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        typeID = attributes.typeID
        marketGroupID = attributes.marketGroupID
        WalletBalance(parent=self.header.extra_content, align=uiconst.TORIGHT)
        self.sr.market = MarketBase(name='marketbase', parent=self.sr.main, state=uiconst.UI_PICKCHILDREN, content_padding=self.content_padding)
        self.sr.market.Startup(marketGroupID=marketGroupID)
        self.on_content_padding_changed.connect(self._on_content_padding_changed)
        if typeID:
            self.LoadTypeID_Ext(typeID)
        sm.RegisterNotify(self)

    def InitializeCaption(self, attributes):
        self.caption = self._get_caption()

    @staticmethod
    def _get_caption():
        return GetByLabel('UI/Market/MarketQuote/RegionalMarket', regionName=cfg.evelocations.Get(session.regionid).name)

    def OnSessionChanged(self, isRemove, session, change):
        if self.destroyed:
            return
        if 'solarsystemid2' in change:
            self.caption = self._get_caption()

    def LoadTypeID_Ext(self, typeID):
        self.sr.market.LoadTypeID_Ext(typeID)
        self.sr.market.OpenOnTypeID(typeID)
        self.SetOrder(0)

    def LoadMarketGroup(self, marketGroupID):
        self.sr.market.LoadMarketGroup(marketGroupID)

    def OnBack(self, *args):
        self.sr.market.GoBack()

    def OnForward(self, *args):
        self.sr.market.GoForward()

    @classmethod
    def OpenAndSearch(cls, searchString):
        window = cls.Open()
        market = window.sr.market
        market.sr.searchInput.SetValue(searchString)
        market.sr.sbTabs.SelectByIdx(0)
        market.ReloadMarketListTab()

    def GetMenuMoreOptions(self):
        menu = super(RegionalMarket, self).GetMenuMoreOptions()
        wallet_balance_menu = get_wallet_balance_options_menu()
        if wallet_balance_menu:
            menu += wallet_balance_menu
        menu.AddCheckbox(text=localization.GetByLabel('UI/Market/ShowMarketTicker'), setting=ticker_enabled_setting, hint=localization.GetByLabel('UI/Market/TickerHint'))
        return menu

    def _on_content_padding_changed(self, window):
        self.sr.market.content_padding = self.content_padding


class MarketBase(Container):
    __guid__ = 'form.Market'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnMarketQuickbarChange', 'OnOwnOrdersChanged', 'OnSessionChanged']
    __update_on_reload__ = 1

    def __init__(self, content_padding = (0,
 0,
 0,
 0), **kwargs):
        self._content_padding = content_padding
        self._details_panel = None
        self._group_panel = None
        self._left_side = None
        self._left_side_divider = None
        self._left_side_fill = None
        self._main_tab_container = None
        self._ticker = None
        super(MarketBase, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        super(MarketBase, self).ApplyAttributes(attributes)
        self.inited = 0
        self.searchAsksForMyRange = None
        self.pendingType = None
        self.loadingType = 0
        self.loadingMarketData = None
        self.lastdetailTab = localization.GetByLabel('UI/Market/MarketData')
        self.lastOnOrderChangeTime = None
        self.refreshOrdersTimer = None
        self.groupListData = None
        self.sr.lastSearchResult = []
        self.sr.lastBrowseResult = []
        self.sr.marketgroups = None
        self.sr.quickType = None
        self.sr.pricehistory = None
        self.sr.grouplist = None
        self.sr.marketdata = None
        self.detailsInited = 0
        self.updatingGroups = 0
        self.settingsInited = 0
        self.OnChangeFuncs = {}
        self.SetChangeFuncs()
        self.lastid = 0
        self.marketItemList = []
        self.name = 'MarketBase'
        self.sr.detailTypeID = None
        self.parentDictionary = {}
        self.historyData = []
        self.historyIdx = None

    @property
    def content_padding(self):
        return self._content_padding

    @content_padding.setter
    def content_padding(self, value):
        if value != self._content_padding:
            self._content_padding = value
            self._update_content_padding()

    def _update_content_padding(self):
        self._left_side.padding = self._get_left_side_padding()
        self._left_side_divider.padding = self._get_left_side_divider_padding()
        self._main_tab_container.padding = self._get_main_tab_container_padding()
        self._group_panel.padding = self._get_group_panel_padding()
        self._details_panel.padding = self._get_details_panel_padding()
        self._left_side_fill.padding = self._get_left_side_fill_padding()

    def _get_left_side_padding(self):
        pad_left, pad_top, _, _ = self.content_padding
        return (pad_left,
         pad_top,
         0,
         0)

    def _get_left_side_divider_padding(self):
        _, pad_top, _, _ = self.content_padding
        return (0,
         pad_top,
         8,
         0)

    def _get_main_tab_container_padding(self):
        _, pad_top, pad_right, _ = self.content_padding
        return (0,
         pad_top,
         pad_right,
         8)

    def _get_group_panel_padding(self):
        _, _, pad_right, pad_bottom = self.content_padding
        if ticker_enabled_setting.is_enabled():
            pad_bottom = 0
        return (0,
         0,
         pad_right,
         pad_bottom)

    def _get_details_panel_padding(self):
        _, _, pad_right, pad_bottom = self.content_padding
        if ticker_enabled_setting.is_enabled():
            pad_bottom = 0
        return (0,
         0,
         pad_right,
         pad_bottom)

    def _get_left_side_fill_padding(self):
        pad_left, pad_top, _, _ = self.content_padding
        return (-pad_left,
         -pad_top,
         0,
         0)

    def _OnClose(self, *args):
        if self.groupListData is not None:
            settings.char.ui.Set('marketGroupID_groupList', self.groupListData.marketGroupID)
        if self._left_side is not None:
            settings.user.ui.Set('marketselectorwidth_%s' % self.idName, self._left_side.width)
        settings.user.ui.Set('quickbar_lastid', self.lastid)
        settings.user.ui.Set('quickbar', self.folders)
        sm.UnregisterNotify(self)

    def Startup(self, isStationMarket = 0, marketGroupID = None):
        self.idName = 'region'
        if marketGroupID:
            self.groupListData = sm.GetService('marketutils').GetMarketGroupByID(marketGroupID)
        else:
            marketGroupID = settings.char.ui.Get('marketGroupID_groupList', None)
            if marketGroupID:
                try:
                    self.groupListData = MarketGroupObject(marketGroupID)
                except StandardError:
                    self.groupListData = None

            else:
                self.groupListData = None
        with ExceptionEater('AddMarketTicker'):
            self.AddMarketTicker()
        self._left_side = Container(name='leftSide', parent=self, align=uiconst.TOLEFT, width=settings.user.ui.Get('marketselectorwidth_%s' % self.idName, 180), padding=self._get_left_side_padding())
        self._left_side_divider = Divider(name='divider', parent=self, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, width=8, padding=self._get_left_side_divider_padding(), cross_axis_alignment=AxisAlignment.START)
        self._left_side_divider.Startup(self._left_side, 'width', 'x', 180, 450)
        tabs = TabGroup(name='tabparent', parent=self._left_side, padding=0)
        self.sr.sbTabs = tabs
        self._main_tab_container = Container(parent=self, align=uiconst.TOTOP, height=32, padding=self._get_main_tab_container_padding())
        self.sr.tabs = TabGroup(name='tabparent', parent=self._main_tab_container, align=uiconst.TOLEFT, padBottom=0, auto_size=True)
        button_group = ButtonGroup(parent=self._main_tab_container, align=uiconst.TOBOTTOM, padLeft=24, density=Density.COMPACT, button_alignment=AxisAlignment.END)
        self.marketNESButton = Button(parent=button_group, label=GetByLabel('UI/VirtualGoodsStore/VgsName'), hint=GetByLabel('Tooltips/Neocom/Vgs_description'), func=uicore.cmd.ToggleAurumStore, variant=ButtonVariant.GHOST)
        self.marketNESButton.analyticID = MARKET_NES_BUTTON_ANALYTIC_ID
        Button(parent=button_group, label=GetByLabel('Tooltips/StationServices/MarketOrders'), hint=GetByLabel('Tooltips/StationServices/MarketOrders_description'), func=uicore.cmd.OpenMarketOrders, variant=ButtonVariant.GHOST)
        multiBuyBtn = Button(parent=button_group, label=GetByLabel('UI/Market/Multibuy'), hint=GetByLabel('UI/Market/Multibuy_description'), func=self.OnOpenMultiBuyBtn, variant=ButtonVariant.GHOST)
        multiBuyBtn.OnDropData = self.OnDropOnMultibuyBtn
        self._group_panel = ScrollContainer(name='groupScroll', parent=self, align=uiconst.TOALL, padding=self._get_group_panel_padding())
        searchAndSettingParent = Container(name='searchAndSettingParent', parent=self._left_side, align=uiconst.TOTOP, height=24, padding=(0, 8, 8, 8))
        collapseParent = ContainerAutoSize(parent=searchAndSettingParent, align=uiconst.TORIGHT)
        ButtonIcon(name='collapse', parent=collapseParent, align=uiconst.CENTER, pos=(0, 0, 24, 24), iconSize=12, texturePath='res:/UI/Texture/classes/Scroll/Collapse.png', func=self.CollapseAll, hint=localization.GetByLabel('UI/Common/Buttons/CollapseAll'))
        searchparent = Container(name='searchparent', parent=searchAndSettingParent, align=uiconst.TOALL)
        filterParent = ContainerAutoSize(parent=searchAndSettingParent, align=uiconst.TORIGHT, idx=0)
        self.sr.filtericon = UtilMenu(parent=filterParent, align=uiconst.CENTER, GetUtilMenu=self.SettingMenu, texturePath=eveicon.tune, width=24, height=24, iconSize=16, uniqueUiName=pConst.UNIQUE_NAME_MARKET_BROWSE_SETTINGS)
        padRight = self.sr.filtericon.width + 4
        searchText = settings.char.ui.Get('market_searchText', '')
        inpt = QuickFilterEdit(name='searchField', parent=searchparent, setvalue=searchText, hintText=localization.GetByLabel('UI/Common/Search'), pos=(0, 0, 0, 18), padRight=4, maxLength=64, align=uiconst.TOALL, OnClearFilter=self.LoadMarketListOrSearch, isTypeField=True, triggerFilterOnCreation=False)
        inpt.ReloadFunction = self.OnSearchFieldChanged
        inpt.OnReturn = self.LoadMarketListOrSearch
        self.sr.searchInput = inpt
        self.sr.searchparent = searchparent
        self.sr.quickbarBtnsParent = Container(name='quickbarBtnsParent', parent=searchAndSettingParent, align=uiconst.TOALL)
        self.sr.quickbarBtnsParent.display = False
        ButtonIcon(parent=ContainerAutoSize(parent=self.sr.quickbarBtnsParent, align=uiconst.TOLEFT), align=uiconst.CENTER, width=24, height=24, texturePath=eveicon.add_folder, iconSize=16, hint=localization.GetByLabel('Tooltips/Market/MarketQuickbarNewFolder'), func=self.NewFolder, args=())
        importMenuParent = ContainerAutoSize(parent=self.sr.quickbarBtnsParent, align=uiconst.TOLEFT)
        UtilMenu(name='importMenu', menuAlign=uiconst.TOPLEFT, parent=importMenuParent, align=uiconst.CENTER, pos=(0, 0, 24, 24), GetUtilMenu=self.GetImportMenu, texturePath=eveicon.load, iconSize=16, hint=GetByLabel('UI/Market/Marketbase/ImportQuickbar'))
        exportMenuParent = ContainerAutoSize(parent=self.sr.quickbarBtnsParent, align=uiconst.TOLEFT)
        UtilMenu(name='exportMenu', menuAlign=uiconst.TOPLEFT, parent=exportMenuParent, align=uiconst.CENTER, pos=(0, 0, 24, 24), GetUtilMenu=self.GetExportMenu, texturePath=eveicon.export, iconSize=16, hint=GetByLabel('UI/Market/Marketbase/ExportQuickbar'))
        ButtonIcon(parent=ContainerAutoSize(parent=self.sr.quickbarBtnsParent, align=uiconst.TOLEFT), align=uiconst.CENTER, width=24, height=24, texturePath=eveicon.trashcan, iconSize=16, hint=localization.GetByLabel('Tooltips/Market/MarketQuickbarReset'), func=self.ResetQuickbar, args=())
        self._details_panel = Container(name='details', parent=self, padding=self._get_details_panel_padding(), clipChildren=True)
        maintabs = [GetTabData(label=localization.GetByLabel('UI/Market/Browse'), code=self, tabID='browse', hint=localization.GetByLabel('Tooltips/Market/MarketBrowseTab')), GetTabData(label=localization.GetByLabel('UI/Market/QuickBar'), code=self, tabID='quickbar', hint=localization.GetByLabel('Tooltips/Market/MarketQuickbarTab'))]
        subtabs = [GetTabData(label=FixedTabName('UI/Common/Details'), panel=self._details_panel, code=self, tabID='details', hint=localization.GetByLabel('Tooltips/Market/MarketDetailsTab'), uniqueName=pConst.UNIQUE_NAME_MARKET_DETAILS), GetTabData(label=FixedTabName('UI/Common/Groups'), panel=self._group_panel, code=self, tabID='groups', hint=localization.GetByLabel('Tooltips/Market/MarketGroupsTab'))]
        if self.destroyed:
            return
        scrollParent = Container(parent=self._left_side, align=uiconst.TOALL)
        self._left_side_fill = PanelUnderlay(bgParent=self._left_side, padding=self._get_left_side_fill_padding())
        self.sr.typescroll = eveScroll.Scroll(name='typescroll', parent=scrollParent, multiSelect=False, innerPadding=(0, 0, 0, 16))
        self.sr.typescroll.OnSelectionChange = self.CheckTypeScrollSelection
        self.sr.typescroll.GetContentContainer().OnDropData = self.OnScrollDrop
        self.sr.sbTabs.Startup(maintabs, 'tbselectortabs_%s' % self.idName, autoselecttab=1, UIIDPrefix='marketTab')
        quickbarTab = self.sr.sbTabs.GetTabs()[1]
        quickbarTab.OnTabDropData = self.OnQuickbarScrollDrop
        autoSelect = marketGroupID is None
        self.sr.tabs.Startup(subtabs, 'marketsubtabs_%s' % self.idName, autoselecttab=autoSelect, UIIDPrefix='marketTab')
        sm.RegisterNotify(self)
        self.inited = 1
        self.folders = settings.user.ui.Get('quickbar', {})
        self.lastid = settings.user.ui.Get('quickbar_lastid', 0)
        self.SetupFilters()
        self.SetFilterHint()
        self.maxdepth = 99
        if marketGroupID:
            uthread.new(self.sr.tabs.ShowPanelByName, localization.GetByLabel('UI/Common/Groups'))

    def ConstructTopContainer(self):
        pass

    def AddMarketTicker(self):
        self._ticker = MarketTicker(parent=self, align=uiconst.TOBOTTOM, height=28 * fontconst.fontSizeFactor)
        ticker_enabled_setting.on_change.connect(self._on_ticker_toggled)

    def _on_ticker_toggled(self, enabled):
        self._update_content_padding()

    def OnDropOnMultibuyBtn(self, dragObj, nodes):
        buyDict = {}
        for node in nodes:
            typeID = GetTypeIDFromDragItem(node)
            if not typeID:
                continue
            try:
                qty = int(node.extraText)
            except:
                qty = 1

            buyDict[typeID] = qty

        if buyDict:
            self.OpenMultiBuy(buyDict)

    def OnOpenMultiBuyBtn(self, *args):
        self.OpenMultiBuy({})

    def OpenMultiBuy(self, buyDict = None):
        if buyDict is None:
            buyDict = {}
        wnd = BuyMultipleTypesWithQty(buyDict)
        if wnd:
            wnd.Maximize()

    def CollapseAll(self, *args):
        self.sr.typescroll.CollapseAll()

    def SettingMenu(self, menuParent):
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/Market/ShowOnlyAvailable'), checked=bool(settings.user.ui.Get('showonlyavailable', 1)), callback=(self.OnCheckboxChange, 'showonlyavailable'))
        menuParent.AddSpace()
        menuParent.AddText(text=localization.GetByLabel('UI/Market/RangeFilter'))
        if session.stationid or session.structureid:
            menuParent.AddRadioButton(text=localization.GetByLabel('UI/Common/LocationTypes/Station'), checked=self.GetRange() == const.rangeStation, callback=(self.OnComboChange, const.rangeStation))
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'), checked=self.GetRange() == const.rangeSolarSystem, callback=(self.OnComboChange, const.rangeSolarSystem))
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/Common/LocationTypes/Region'), checked=self.GetRange() == const.rangeRegion, callback=(self.OnComboChange, const.rangeRegion))
        menuParent.AddSpace()
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/Market/Marketbase/FilterBySkills'), checked=bool(settings.user.ui.Get('showonlyskillsfor', 0)), callback=(self.OnCheckboxChange, 'showonlyskillsfor'))
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/Market/Marketbase/FilterByCPUAndPowergrid'), checked=bool(settings.user.ui.Get('showhavecpuandpower', 0)), callback=(self.OnCheckboxChange, 'showhavecpuandpower'))
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/Market/Marketbase/FilterByUntrainedSkills'), checked=bool(settings.user.ui.Get('shownewskills', 0)), callback=(self.OnCheckboxChange, 'shownewskills'))
        menuParent.AddSpace()
        menuParent.AddButton(text=GetByLabel('UI/Browser/BrowserSettings/ResetCacheLocation'), callback=self.ResetFilterSettings)

    def CheckTypeScrollSelection(self, sel):
        if len(sel) == 1:
            entry = sel[0]
            if entry.__guid__ == 'listentry.GenericMarketItem' or entry.__guid__ == 'listentry.QuickbarItem':
                self.OnTypeClick(entry.typeID)

    def GetOptions(self):
        if eve.session.stationid:
            options = [(localization.GetByLabel('UI/Common/LocationTypes/Station'), const.rangeStation), (localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'), const.rangeSolarSystem), (localization.GetByLabel('UI/Common/LocationTypes/Region'), const.rangeRegion)]
        else:
            options = [(localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'), const.rangeSolarSystem), (localization.GetByLabel('UI/Common/LocationTypes/Region'), const.rangeRegion)]
        return options

    def GetRange(self):
        return sm.StartService('marketutils').GetMarketRange()

    def OnComboChange(self, value, *args):
        if self.inited:
            sm.GetService('marketutils').SetMarketRange(value)
            self.sr.lastSearchResult = []
            uthread.new(self.ReloadMarketListTab)

    def ReloadMarketListTab(self, *args):
        if self.sr.sbTabs.GetSelectedArgs() == 'browse':
            self.LoadMarketListOrSearch()
        self.sr.tabs.ReloadVisible()

    def SetFilterHint(self, *args):
        filtersInUse, filterUsed = self.FiltersInUse1()
        self.sr.filtericon.hint = filtersInUse

    def OnCheckboxChange(self, sender, *args):
        c = settings.user.ui.Get(sender, 0)
        settings.user.ui.Set(sender, not c)
        self.SetFilterHint()
        if self.sr.sbTabs.GetSelectedArgs() == 'browse':
            self.LoadMarketListOrSearch()
        if self.sr.tabs.GetSelectedArgs() == 'browse':
            self.LoadMarketListOrSearch()

    def OnCheckboxChangeSett(self, sender, *args):
        settings.user.ui.Set(sender.name, bool(sender.checked))
        self.LoadMarketData()
        self.ShowFiltersInUse()

    def OnMarketQuickbarChange(self, fromMarket = 0, *args):
        if self and not self.destroyed:
            if not fromMarket:
                self.lastid = settings.user.ui.Get('quickbar_lastid', 0)
                self.folders = settings.user.ui.Get('quickbar', {})
            if self.sr.sbTabs.GetSelectedArgs() == 'quickbar':
                self.LoadQuickBar()

    def OnOwnOrdersChanged(self, orders, reason, isCorp):
        if self and not self.destroyed:
            showAutoRefresh = False
            for order in orders:
                if not settings.user.ui.Get('autorefresh', True) and self.sr.detailTypeID:
                    if order.typeID == self.sr.detailTypeID:
                        showAutoRefresh = True
                if reason != 'Expiry':
                    self._OnOwnOrderChanged()

            if showAutoRefresh:
                self.sr.reloadBtn.display = True

    @threadutils.throttled(5)
    def _OnOwnOrderChanged(self):
        if self and not self.destroyed:
            try:
                if settings.user.ui.Get('autorefresh', True):
                    if self.sr.sbTabs.GetSelectedArgs() == 'browse':
                        self.LoadMarketListOrSearch()
                    self.sr.tabs.ReloadVisible()
            except AttributeError:
                if not self or self.destoyed:
                    return
                raise

    def OnSessionChanged(self, isremote, session, change):
        if 'solarsystemid' in change and self and not self.destroyed:
            combo = self.FindChild('marketComboRangeFilter')
            if combo:
                oldValue = combo.GetValue()
                newValue = self.GetRange()
                combo.LoadOptions(self.GetOptions(), newValue)
                if oldValue != newValue:
                    self.ReloadMarketListTab()

    def GetQuickItemMenu(self, btn, *args):
        if btn.sr.node.extraText:
            menuText = 'UI/Market/Marketbase/EditAdditionalText'
        else:
            menuText = 'UI/Market/Marketbase/AddAdditionalText'
        m = [(MenuLabel(menuText), self.EditExtraText, (btn.sr.node.id, btn.sr.node.extraText, btn.sr.node.label))]
        m += [None]
        m += [(MenuLabel('UI/Market/Remove'), self.RemoveFromQuickBar, (btn.sr.node,))]
        if eve.session.role & ROLEMASK_ELEVATEDPLAYER:
            m.append(None)
            m += sm.GetService('menu').GetGMTypeMenu(btn.sr.node.typeID)
        return m

    def RemoveFromQuickBar(self, node):
        nodes = node.scroll.GetSelectedNodes(node)
        for each in nodes:
            GetMenuService().RemoveFromQuickBar(each)

    def EditExtraText(self, groupID, extraText, label, *args):
        typeNewTextLabel = localization.GetByLabel('UI/Market/Marketbase/TypeInAdditionalText')
        extraText = utilWindows.NamePopup(label, typeNewTextLabel, setvalue=unicode(extraText), maxLength=25, validator=self.ValidateExtraText)
        if extraText is None:
            return
        self.folders[groupID[1]].extraText = extraText
        sm.ScatterEvent('OnMarketQuickbarChange')

    def ValidateExtraText(self, *args):
        pass

    def OnSearchFieldChanged(self, *args):
        inputValue = self.sr.searchInput.GetValue().strip()
        if inputValue == '':
            return self.LoadMarketListOrSearch()
        if len(inputValue) > 1:
            self.DoSearch()

    def DoSearch(self):
        if self.destroyed:
            return
        self.PopulateSeachAsksForMyRange()
        settings.char.ui.Set('market_searchText', self.sr.searchInput.GetValue())
        self.Search()

    def LoadMarketListOrSearch(self):
        if self.destroyed:
            return
        settings.char.ui.Set('market_searchText', self.sr.searchInput.GetValue())
        self.SetFilterHint()
        self.mine = self.GetMySkills()
        self.PopulateAsksForMyRange()
        if self.sr.searchInput.GetValue().strip():
            self.Search()
        else:
            if not self.sr.filtericon.enabled:
                self.sr.filtericon.Enable()
                self.SetFilterHint()
            self.LoadMarketList()

    def LoadMarketList(self):
        scrolllist = self.GetGroupListForBrowse()
        if self.destroyed:
            return
        self.sr.typescroll.Load(contentList=scrolllist, scrollTo=self.sr.typescroll.GetScrollProportion())

    @telemetry.ZONE_METHOD
    def PopulateAsksForMyRange(self):
        asksForMyRange = self._GetAsksForRange()
        self.searchAsksForMyRange = asksForMyRange
        marketRange = self.GetRange()
        if marketRange in (const.rangeStation, const.rangeSolarSystem) or idCheckers.IsWormholeRegion(session.regionid):
            asksForMyRange = ConvertTuplesToBestByOrders(asksForMyRange)
        self.asksForMyRange = asksForMyRange

    def _GetAsksForRange(self):
        quote = sm.StartService('marketQuote')
        marketRange = self.GetRange()
        if marketRange == const.rangeStation:
            asksForMyRange = quote.GetStationAsks()
        elif marketRange == const.rangeSolarSystem or idCheckers.IsWormholeRegion(session.regionid):
            asksForMyRange = quote.GetSystemAsks()
        else:
            asksForMyRange = quote.GetRegionBest()
        return asksForMyRange

    def PopulateSeachAsksForMyRange(self):
        self.searchAsksForMyRange = self._GetAsksForRange()

    def GetScrollListFromTypeList(self, nodedata, *args):
        typeIDs = nodedata.invTypes
        sublevel = nodedata.sublevel
        return self._GetScrollListFromTypeList(typeIDs, sublevel)

    def _GetScrollListFromTypeList(self, typeIDs, sublevel):
        subList = []
        for typeID in typeIDs:
            typeName = evetypes.GetName(typeID)
            subList.append((typeName, GetFromClass(GenericMarketItem, {'label': typeName,
              'invtype': typeID,
              'sublevel': sublevel + 1,
              'GetMenu': self.OnTypeMenu,
              'ignoreRightClick': 1,
              'showinfo': 1,
              'typeID': typeID})))

        subList = [ item[1] for item in localization.util.Sort(subList, key=lambda x: x[0]) ]
        return subList

    def GetTypesByMetaGroups(self, typeIDs):
        typesByMetaGroupID = defaultdict(list)
        for typeID in typeIDs:
            if evetypes.GetVariationParentTypeIDOrNone(typeID) is None:
                metaGroupID = None
            else:
                metaGroupID = evetypes.GetMetaGroupID(typeID)
                if metaGroupID == const.metaGroupStoryline:
                    metaGroupID = const.metaGroupFaction
            typesByMetaGroupID[metaGroupID].append(typeID)

        return typesByMetaGroupID

    def OnMetaGroupClicked(self, *args):
        self.sr.tabs.ShowPanelByName(localization.GetByLabel('UI/Common/Groups'))

    def GetGroupListForBrowse(self, nodedata = None, newitems = 0):
        scrolllist = []
        if nodedata and nodedata.marketGroupInfo.hasTypes:
            typesByMetaGroupID = self.GetTypesByMetaGroups(nodedata.typeIDs)
            for metaGroupID, types in sorted(typesByMetaGroupID.items()):
                subList = []
                if len(types) == 0:
                    continue
                categoryID = evetypes.GetCategoryID(types[0])
                if metaGroupID in (const.metaGroupStoryline,
                 const.metaGroupFaction,
                 const.metaGroupOfficer,
                 const.metaGroupDeadspace) and categoryID in CATEGORIES_WITH_FACTION_AND_STORYLINE_SUBFOLDERS:
                    if metaGroupID in (const.metaGroupStoryline, const.metaGroupFaction):
                        label = localization.GetByLabel('UI/Market/FactionAndStoryline')
                    else:
                        label = metaGroups.get_name(metaGroupID)
                    marketGroupID = nodedata.marketGroupInfo.marketGroupID if nodedata is not None else None
                    subList.append((label, GetFromClass(MarketMetaGroupEntry, {'GetSubContent': self.GetScrollListFromTypeList,
                      'label': label,
                      'id': (marketGroupID, metaGroupID),
                      'showlen': 0,
                      'metaGroupID': metaGroupID,
                      'invTypes': types,
                      'sublevel': nodedata.sublevel + 1,
                      'showicon': GetIconFile(metaGroups.get_icon_id(metaGroupID)),
                      'state': 'locked',
                      'BlockOpenWindow': True,
                      'OnToggle': self.OnMetaGroupClicked,
                      'typeIDs': types})))
                    subList = [ item[1] for item in localization.util.Sort(subList, key=lambda x: x[0]) ]
                else:
                    subList = self._GetScrollListFromTypeList(types, nodedata.sublevel)
                scrolllist += subList

        else:
            marketGroupID = None
            level = 0
            if nodedata:
                marketGroupID = nodedata.marketGroupInfo.marketGroupID
                level = nodedata.sublevel + 1
            grouplist = sm.GetService('marketutils').GetMarketGroups()[marketGroupID]
            for marketGroupInfo in grouplist:
                if not len(marketGroupInfo.types):
                    continue
                if self.destroyed:
                    return
                typeIDs = self.FilterItemsForBrowse(marketGroupInfo)
                if len(typeIDs) == 0:
                    continue
                if level in (0, 1):
                    groupHint = marketGroupInfo.description
                else:
                    groupHint = ''
                groupID = (marketGroupInfo.marketGroupName, marketGroupInfo.marketGroupID)
                data = {'GetSubContent': self.GetGroupListForBrowse,
                 'label': marketGroupInfo.marketGroupName,
                 'id': groupID,
                 'typeIDs': typeIDs,
                 'iconMargin': 18,
                 'showlen': 0,
                 'marketGroupInfo': marketGroupInfo,
                 'sublevel': level,
                 'state': 'locked',
                 'OnClick': self.OnMarketGroupClicked,
                 'showicon': None if not marketGroupInfo.hasTypes else 'hide',
                 'iconID': marketGroupInfo.iconID,
                 'selected': False,
                 'BlockOpenWindow': 1,
                 'MenuFunction': self.SelectFolderMenu,
                 'hint': groupHint}
                if not level and marketGroupInfo.description:
                    data['hint'] = marketGroupInfo.description
                if marketGroupInfo.hasTypes and getattr(self, 'groupListData', None) and self.groupListData.marketGroupID != marketGroupInfo.marketGroupID:
                    uicore.registry.SetListGroupOpenState(groupID, 0)
                scrolllist.append((marketGroupInfo.marketGroupName, GetFromClass(MarketListGroup, data)))

            scrolllist = [ item[1] for item in localization.util.Sort(scrolllist, key=lambda x: x[0]) ]
        return scrolllist

    def OnMarketGroupClicked(self, entry, openGroup = True):
        if not openGroup:
            return
        marketGroup = entry.sr.node.marketGroupInfo
        self._LoadMarketGroup(marketGroup)

    def LoadMarketGroup(self, marketGroupID):
        self.groupListData = sm.GetService('marketutils').GetMarketGroupByID(marketGroupID)
        self.sr.tabs.ShowPanelByName(localization.GetByLabel('UI/Common/Groups'))

    def _LoadMarketGroup(self, marketGroup):
        self.state = uiconst.UI_DISABLED
        try:
            if marketGroup.hasTypes:
                groupID = marketGroup.marketGroupID
                for entry in self.sr.typescroll.GetNodes():
                    if not (entry.marketGroupInfo and entry.marketGroupInfo.hasTypes):
                        continue
                    if entry.marketGroupInfo.marketGroupID == groupID:
                        if not entry.panel:
                            entry.open = 1
                            self.sr.typescroll.PrepareSubContent(entry)
                        self.sr.typescroll.SelectNode(entry)
                        self.sr.typescroll.ShowNodeIdx(entry.idx)
                        if entry.open or self.groupListData is None or self.groupListData.marketGroupID != groupID:
                            self.groupListData = entry.marketGroupInfo
                            self.sr.tabs.ShowPanelByName(localization.GetByLabel('UI/Common/Groups'))
                    else:
                        if not entry.open:
                            continue
                        if entry.panel:
                            entry.panel.Toggle()
                        else:
                            entry.open = 0
                            if entry.subNodes:
                                rm = entry.subNodes
                                entry.subNodes = []
                                entry.open = 0
                                self.sr.typescroll.RemoveEntries(rm)

        finally:
            self.state = uiconst.UI_PICKCHILDREN

    def GetAttrDict(self, typeID):
        ret = {}
        for each in dogma.data.get_type_attributes(typeID):
            attribute = dogma.data.get_attribute(each.attributeID)
            if attribute.dataType == attributeDataTypeTypeMirror:
                ret[each.attributeID] = evetypes.GetAttributeForType(typeID, attribute.name)
            else:
                ret[each.attributeID] = each.value

        if not ret.has_key(const.attributeCapacity) and evetypes.GetCapacity(typeID):
            ret[const.attributeCapacity] = evetypes.GetCapacity(typeID)
        attrInfo = sm.GetService('godma').GetType(typeID)
        for each in attrInfo.displayAttributes:
            ret[each.attributeID] = each.value

        return ret

    def GetActiveShipSlots(self):
        ship = sm.GetService('godma').GetItem(eve.session.shipid)
        if ship is None:
            return 0
        hiSlots = getattr(ship, 'hiSlots', 0)
        medSlots = getattr(ship, 'medSlots', 0)
        lowSlots = getattr(ship, 'lowSlots', 0)
        rigSlots = getattr(ship, 'rigSlots', 0)
        flags = []
        for gidx in xrange(3):
            for sidx in xrange(8):
                flags.append(getattr(const, 'flag%sSlot%s' % (FITKEYS[gidx], sidx)))

        for module in ship.modules:
            if module.flagID not in flags:
                continue
            for effect in module.effects.itervalues():
                if effect.effectID == const.effectHiPower:
                    hiSlots -= 1
                elif effect.effectID == const.effectMedPower:
                    medSlots -= 1
                elif effect.effectID == const.effectLoPower:
                    lowSlots -= 1
                elif effect.effectID == const.effectRigSlot:
                    rigSlots -= 1

        return (hiSlots,
         medSlots,
         lowSlots,
         rigSlots)

    def GetMySkills(self):
        return sm.GetService('skills').MyEffectiveSkillLevelsByID()

    @telemetry.ZONE_METHOD
    def ShowGroupPage(self, *args):
        if self.updatingGroups:
            return
        self.updatingGroups = 0
        self.PopulateAsksForMyRange()
        try:
            self._group_panel.Flush()
            group = self.groupListData
            if group:
                self._group_panel.ShowNoContentHint(localization.GetByLabel('UI/Market/Marketbase/Loading'))
                freeslots = self.GetActiveShipSlots()
                self.mine = mySkills = self.GetMySkills()
                dataByTypeID = {data.typeID:data for data in self.FilterItemsForGroupPage(group)}
                typesByMetaGroupID = self.GetTypesByMetaGroups(dataByTypeID.keys())
                scrolllist = []
                for _, typeIDs in sorted(typesByMetaGroupID.iteritems()):
                    subList = []
                    if len(typeIDs) == 0:
                        continue
                    for typeID in typeIDs:
                        subList.append((evetypes.GetName(typeID), dataByTypeID[typeID]))

                    subList = [ item[1] for item in localization.util.Sort(subList, key=lambda x: x[0]) ]
                    scrolllist += subList

                if not scrolllist:
                    noItemsText = localization.GetByLabel('UI/Market/Marketbase/NoItemsAvailable')
                    if settings.user.ui.Get('showonlyavailable', 1):
                        noItemsText += '<br><br>' + localization.GetByLabel('UI/Market/Marketbase/DisableShowOnlyAvailable')
                    self._group_panel.ShowNoContentHint(noItemsText)
                marketRange = self.GetRange()
                if marketRange == const.rangeStation:
                    bestPriceLocation = localization.GetByLabel('UI/Common/LocationTypes/Station')
                elif marketRange == const.rangeSolarSystem:
                    bestPriceLocation = localization.GetByLabel('UI/Common/LocationTypes/System')
                else:
                    bestPriceLocation = localization.GetByLabel('UI/Common/LocationTypes/Region')
                for data in scrolllist:
                    entryData = Bunch()
                    entryData.marketData = data
                    entryData.invType = data.typeID
                    entryData.typeImageAttributes = Bunch(width=64, height=64, src='typeicon:%s' % data.typeID, bumped=True, showfitting=True, showtechlevel=True)
                    entryData.freeslots = freeslots
                    entryData.mySkills = mySkills
                    desc = evetypes.GetDescription(data.typeID).replace('\r\n', '<br>').strip()
                    if desc.endswith('<br>'):
                        desc = desc[:len(desc) - 4]
                    entryData.description = desc
                    jump = ''
                    if data.qty:
                        jumps = int(data.jumps)
                        if jumps == 0:
                            jump = localization.GetByLabel('UI/Market/Marketbase/InThisSystem')
                        elif jumps == -1:
                            jump = localization.GetByLabel('UI/Market/Marketbase/InThisStation')
                        else:
                            jump = localization.GetByLabel('UI/Market/Marketbase/JumpsAway', jumps=data.jumps)
                    if data.qty > 0:
                        entryData.unitsAvailable = localization.GetByLabel('UI/Market/Marketbase/UnitsAvailable', quantity=int(data.qty), numberOfJumps=jump)
                    entryData.bestPrice = localization.GetByLabel('UI/Market/Marketbase/BestPriceIn', place=bestPriceLocation)
                    MarketGroupEntry(parent=self._group_panel, data=entryData)

                self._group_panel.HideNoContentHint()
            else:
                self._group_panel.ShowNoContentHint(localization.GetByLabel('UI/Market/Marketbase/SelectGroupToBrowse'))
        finally:
            if self.destroyed:
                return
            self.updatingGroups = 0

    def Load(self, key):
        if key == 'marketdata':
            self.lastdetailTab = localization.GetByLabel('UI/Market/MarketData')
            self.LoadMarketData()
        elif key == 'quickbar':
            self.sr.searchparent.display = False
            self.sr.quickbarBtnsParent.display = True
            self.sr.typescroll.multiSelect = 1
            self.LoadQuickBar()
        elif key == 'details':
            self.LoadDetails()
        elif key == 'pricehistory':
            self.lastdetailTab = localization.GetByLabel('UI/Market/Marketbase/PriceHistory')
            self.LoadPriceHistory()
        elif key == 'browse':
            self.sr.searchparent.display = True
            self.sr.quickbarBtnsParent.display = False
            self.sr.typescroll.multiSelect = 0
            self.LoadMarketListOrSearch()
        elif key == 'groups':
            self.ShowGroupPage()

    def Search(self, *args):
        self.sr.searchInput.RegisterHistory()
        self.sr.filtericon.Disable()
        self.sr.filtericon.hint = localization.GetByLabel('UI/Market/FiltersDontApply')
        search = self.sr.searchInput.GetValue().lower()
        if not search or search == ' ':
            self.LoadMarketListOrSearch()
            return
        self.sr.typescroll.Load(contentList=[])
        self.sr.typescroll.ShowHint(localization.GetByLabel('UI/Common/Searching'))
        t = uix.TakeTime('Market::GetSearchResult', self.GetSearchResult)
        if not t:
            t = [GetFromClass(Generic, {'label': localization.GetByLabel('UI/Market/NothingFoundWithSearch', search=search)})]
        self.sr.typescroll.ShowHint()
        self.sr.typescroll.Load(contentList=t)

    def SetChangeFuncs(self):
        self.OnChangeFuncs['market_filter_price_min'] = self.OnChange_minEdit_market_filter_price
        self.OnChangeFuncs['market_filter_price_max'] = self.OnChange_maxEdit_market_filter_price
        self.OnChangeFuncs['market_filter_jumps_min'] = self.OnChange_minEdit_market_filter_jump
        self.OnChangeFuncs['market_filter_jumps_max'] = self.OnChange_maxEdit_market_filter_jumps
        self.OnChangeFuncs['market_filter_quantity_min'] = self.OnChange_minEdit_market_filter_quantity
        self.OnChangeFuncs['market_filter_quantity_max'] = self.OnChange_maxEdit_market_filter_quantity
        self.OnChangeFuncs['market_filters_sellorderdev_min'] = self.OnChange_minEdit_market_filters_sellorderdev
        self.OnChangeFuncs['market_filters_sellorderdev_max'] = self.OnChange_maxEdit_market_filters_sellorderdev
        self.OnChangeFuncs['market_filters_buyorderdev_min'] = self.OnChange_minEdit_market_filters_buyorderdev
        self.OnChangeFuncs['market_filters_buyorderdev_max'] = self.OnChange_maxEdit_market_filters_buyorderdev

    def LoadDetails(self):
        if not self.detailsInited:
            topPar = ContainerAutoSize(name='topCont', parent=self._details_panel, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
            buttons = ContainerAutoSize(parent=topPar, align=uiconst.TORIGHT, padLeft=4)
            self.goBackBtn = ButtonIcon(parent=ContainerAutoSize(parent=buttons, align=uiconst.TOLEFT), align=uiconst.TOPLEFT, width=24, height=24, iconSize=16, texturePath=eveicon.navigate_back, func=self.GoBack, hint=localization.GetByLabel('UI/Control/EveWindow/Previous'))
            self.DisableArrow(self.goBackBtn)
            self.goForwardBtn = ButtonIcon(parent=ContainerAutoSize(parent=buttons, align=uiconst.TOLEFT), align=uiconst.TOPLEFT, width=24, height=24, iconSize=16, texturePath=eveicon.navigate_forward, func=self.GoForward, hint=localization.GetByLabel('UI/Control/EveWindow/Next'))
            self.DisableArrow(self.goForwardBtn)
            self.sr.reloadBtn = ButtonIcon(parent=ContainerAutoSize(parent=buttons, align=uiconst.TOLEFT), align=uiconst.TOPLEFT, width=24, height=24, iconSize=16, texturePath=eveicon.arrow_rotate_right, func=self.OnReload, hint=localization.GetByLabel('UI/Market/Marketbase/Reload'))
            self.sr.reloadBtn.display = False
            self.settingsIcon = UtilMenu(parent=ContainerAutoSize(parent=buttons, align=uiconst.TOLEFT), align=uiconst.TOPLEFT, GetUtilMenu=self.DetailsSettingsMenu, texturePath=eveicon.tune, width=24, height=24, iconSize=16)
            top = ContainerAutoSize(name='typeNameCont', align=uiconst.TOTOP, parent=topPar)
            topDetailsCont = ContainerAutoSize(parent=top, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=64)
            self.mainIconContainer = Container(name='mainIconContainer', parent=Container(parent=topDetailsCont, align=uiconst.TOLEFT, width=64, padRight=8), align=uiconst.TOTOP, height=64)
            self.sr.detailIcon = MarketGroupItemImage(parent=self.mainIconContainer, align=uiconst.TOALL, name='detailIcon', height=64, width=64)
            self.sr.detailIcon.Hide()
            self.sr.detailGroupTrace = eveLabel.EveLabelMedium(parent=topDetailsCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text='', color=TextColor.SECONDARY)
            self.sr.detailGroupTrace.OnClick = (self.ClickGroupTrace, self.sr.detailGroupTrace)
            captionGrid = LayoutGrid(parent=ContainerAutoSize(parent=topDetailsCont, align=uiconst.TOTOP), align=uiconst.TOPLEFT, columns=3, cellSpacing=(8, 0))
            self.sr.detailTop = eveLabel.EveCaptionMedium(parent=captionGrid, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/Market/Marketbase/NoTypeSelected'), state=uiconst.UI_NORMAL)
            self.sr.detailInfoicon = InfoIcon(parent=captionGrid, align=uiconst.CENTER, state=uiconst.UI_HIDDEN)
            self.sr.detailInfoicon.OnClick = self.ShowInfoFromDetails
            self.sr.detailTypeID = None
            self.browseBtn = ButtonIcon(name='browseBtn', parent=captionGrid, align=uiconst.CENTER, width=16, height=16, iconSize=16, texturePath='res:/UI/Texture/classes/MapView/focusIcon.png', hint=localization.GetByLabel('UI/Market/Marketbase/FindInBrowseTab'), func=self.OpenOnType, args=self.sr.detailGroupTrace, uniqueUiName=pConst.UNIQUE_NAME_MARKET_FIND_IN_BROWSER)
            self.browseBtn.display = False
            self.sr.requirements = RequirementsContainer(parent=ContainerAutoSize(parent=topDetailsCont, align=uiconst.TOTOP), align=uiconst.TOPLEFT, top=4, width=200)
            self.buyPlexButton = PurchaseButton(name='buyPlexButton', parent=ContainerAutoSize(parent=topDetailsCont, align=uiconst.TOTOP), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, top=4, width=70, height=20, fontsize=12, func=lambda *args: uicore.cmd.CmdBuyPlex(logContext=FROM_MARKET_WINDOW), text=localization.GetByLabel('UI/VirtualGoodsStore/Buttons/BuyPlex'))
            self.sr.filtersText = eveLabel.EveLabelMedium(parent=top, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padding=(0, 8, 0, 0))
            self.ShowFiltersInUse()
            self.sr.detailtabs = TabGroup(name='tabparent', parent=self._details_panel)
            self.sr.marketdata = Container(name='marketinfo', parent=self._details_panel, pos=(0, 0, 0, 0))
            from eve.client.script.ui.shared.market.pricehistorychart import PriceHistoryParent
            self.sr.pricehistory = PriceHistoryParent(name='pricehistory', parent=self._details_panel, pos=(0, 0, 0, 0))
            detailtabs = [GetTabData(label=localization.GetByLabel('UI/Market/MarketData'), panel=self.sr.marketdata, code=self, tabID='marketdata', hint=localization.GetByLabel('Tooltips/Market/MarketDetailsData'), uniqueName=pConst.UNIQUE_NAME_MARKET_DATA), GetTabData(label=FixedTabName('UI/Market/Marketbase/PriceHistory'), panel=self.sr.pricehistory, code=self, tabID='pricehistory', hint=localization.GetByLabel('Tooltips/Market/MarketDetailsHistory'), uniqueName=pConst.UNIQUE_NAME_MARKET_PRICE_HISTORY)]
            self.sr.detailtabs.Startup(detailtabs, 'marketdetailtabs', autoselecttab=1, UIIDPrefix='marketDetailsTab')
            self.detailsInited = 1
            return
        if self.lastdetailTab:
            self.sr.detailtabs.ShowPanelByName(self.lastdetailTab)
        self.ShowFiltersInUse()

    def ShowFiltersInUse(self):
        filtersInUse = self.FiltersInUse2()
        if filtersInUse:
            self.sr.filtersText.display = True
            self.sr.filtersText.text = localization.GetByLabel('UI/Market/Marketbase/MarketFilters')
            self.sr.filtersText.hint = filtersInUse
        else:
            self.sr.filtersText.display = False
            self.sr.filtersText.text = ''
            self.sr.filtersText.hint = None

    def DetailsSettingsMenu(self, menuParent):
        grid = menuParent.AddLayoutGrid(columns=4, cellPadding=4)
        priceConfig = settings.user.ui.Get('market_filter_price', 0)
        Checkbox(text=GetByLabel('UI/Market/Marketbase/Price'), settingsKey='market_filter_price', checked=priceConfig, parent=grid, align=uiconst.TOPLEFT, callback=self.OnCheckboxChangeSett, wrapLabel=False)
        self.MakeFloatEdit('market_filter_price', isMin=True, parent=grid)
        eveLabel.EveLabelSmall(text='-', parent=grid, align=uiconst.CENTER)
        self.MakeFloatEdit('market_filter_price', isMin=False, parent=grid)
        jumpsConfig = settings.user.ui.Get('market_filter_jumps', 0)
        Checkbox(text=GetByLabel('UI/Market/Marketbase/Jumps'), settingsKey='market_filter_jumps', checked=jumpsConfig, parent=grid, align=uiconst.TOPLEFT, callback=self.OnCheckboxChangeSett, wrapLabel=False)
        self.MakeIntEdit('market_filter_jumps', isMin=True, parent=grid, ints=[0, None])
        eveLabel.EveLabelSmall(text='-', parent=grid, align=uiconst.CENTER)
        self.MakeIntEdit('market_filter_jumps', isMin=False, parent=grid, ints=[0, None])
        qtyConfig = settings.user.ui.Get('market_filter_quantity', 0)
        Checkbox(text=GetByLabel('UI/Common/Quantity'), settingsKey='market_filter_quantity', checked=qtyConfig, parent=grid, align=uiconst.TOPLEFT, callback=self.OnCheckboxChangeSett, wrapLabel=False)
        self.MakeIntEdit('market_filter_quantity', isMin=True, parent=grid, ints=[0, None])
        eveLabel.EveLabelSmall(text='-', parent=grid, align=uiconst.CENTER)
        self.MakeIntEdit('market_filter_quantity', isMin=False, parent=grid, ints=[0, None])
        subGrid = LayoutGrid(columns=3, cellPadding=(0, 0, 20, 0))
        showOrdersLabel = EveLabelSmall(text=GetByLabel('UI/Market/Marketbase/ShowOrdersIn'), left=2)
        subGrid.AddCell(cellObject=showOrdersLabel, colSpan=3)
        boxes = self.GetSecStatusBoxes()
        for label, configname, retval, checked, hint in boxes:
            cb = Checkbox(text='%s' % label, parent=subGrid, settingsKey=configname, checked=checked, callback=self.OnCheckboxChangeSett, align=uiconst.TOPLEFT, wrapLabel=False)

        subGrid.RefreshGridLayout()
        grid.AddCell(cellObject=subGrid, colSpan=4)
        sellConfig = settings.user.ui.Get('market_filters_sellorderdev', 0)
        Checkbox(text=GetByLabel('UI/Market/Marketbase/SellOrdersDeviation'), settingsKey='market_filters_sellorderdev', checked=sellConfig, parent=grid, align=uiconst.TOPLEFT, hint=GetByLabel('UI/Market/Marketbase/SellOrdersDeviationToolTip'), callback=self.OnCheckboxChangeSett, wrapLabel=False)
        self.MakeIntEdit('market_filters_sellorderdev', isMin=True, parent=grid, ints=[-100, None])
        eveLabel.EveLabelSmall(text='-', parent=grid, align=uiconst.CENTER)
        self.MakeIntEdit('market_filters_sellorderdev', isMin=False, parent=grid, ints=[-100, None])
        buyConfig = settings.user.ui.Get('market_filters_buyorderdev', 0)
        Checkbox(text=GetByLabel('UI/Market/Marketbase/BuyOrdersDeviation'), settingsKey='market_filters_buyorderdev', checked=buyConfig, parent=grid, align=uiconst.TOPLEFT, hint=GetByLabel('UI/Market/Marketbase/BuyOrdersDeviationToolTip'), callback=self.OnCheckboxChangeSett, wrapLabel=False)
        self.MakeIntEdit('market_filters_buyorderdev', isMin=True, parent=grid, ints=[-100, None])
        eveLabel.EveLabelSmall(text='-', parent=grid, align=uiconst.CENTER)
        self.MakeIntEdit('market_filters_buyorderdev', isMin=False, parent=grid, ints=[-100, None])
        currentMyOrdersValue = settings.user.ui.Get('hilitemyorders', True)
        mmo = Checkbox(text=GetByLabel('UI/Market/Marketbase/MarkMyOrders'), settingsKey='hilitemyorders', checked=currentMyOrdersValue, hint=GetByLabel('UI/Market/Marketbase/MarkMyOrdersHint'), callback=self.OnCheckboxChangeSett)
        grid.AddCell(cellObject=mmo, colSpan=4)
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/Market/Marketbase/AutoRefresh'), checked=bool(settings.user.ui.Get('autorefresh', 0)), callback=(self.OnCheckboxChange, 'autorefresh'))
        menuParent.AddButton(text=GetByLabel('UI/Browser/BrowserSettings/ResetCacheLocation'), callback=self.ResetDetailsSettings)

    def MakeIntEdit(self, configName, isMin, parent, ints):
        if isMin:
            funcKey = '%s_min' % configName
            editName = 'minEdit_%s' % configName
        else:
            funcKey = '%s_max' % configName
            editName = 'maxEdit_%s' % configName
        edit = SingleLineEditInteger(name=editName, setvalue=GetNumericValueFromSetting(editName), parent=parent, minValue=ints[0], maxValue=ints[1], OnChange=self.OnChangeFuncs[funcKey])
        edit.AutoFitToText(FmtAmt(sys.maxint))
        return edit

    def MakeFloatEdit(self, configName, isMin, parent):
        if isMin:
            funcKey = '%s_min' % configName
            editName = 'minEdit_%s' % configName
        else:
            funcKey = '%s_max' % configName
            editName = 'maxEdit_%s' % configName
        edit = SingleLineEditFloat(name=editName, setvalue=GetNumericValueFromSetting(editName), parent=parent, maxValue=MAX_ORDER_PRICE, decimalPlaces=2, OnChange=self.OnChangeFuncs[funcKey])
        edit.AutoFitToText(FmtAmt(sys.maxint))
        return edit

    def GetSecStatusBoxes(self):
        highSecurityLabel = GetByLabel('UI/Common/HighSec')
        highSecurityToolTipLabel = GetByLabel('UI/Market/Marketbase/FilterHighSecurityToolTip')
        lowSecurityLabel = GetByLabel('UI/Common/LowSec')
        lowSecurityToolTipLabel = GetByLabel('UI/Market/Marketbase/FilterLowSecurityToolTip')
        zeroSecurityLabel = GetByLabel('UI/Common/NullSec')
        zeroSecurityToolTipLabel = GetByLabel('UI/Market/Marketbase/FilterZeroSecurityToolTip')
        boxes = [(highSecurityLabel,
          'market_filter_highsec',
          settings.user.ui.Get('market_filter_highsec', 0) == 1,
          settings.user.ui.Get('market_filter_highsec', 0),
          highSecurityToolTipLabel), (lowSecurityLabel,
          'market_filter_lowsec',
          settings.user.ui.Get('market_filter_lowsec', 0) == 1,
          settings.user.ui.Get('market_filter_lowsec', 0),
          lowSecurityToolTipLabel), (zeroSecurityLabel,
          'market_filter_zerosec',
          settings.user.ui.Get('market_filter_zerosec', 0) == 1,
          settings.user.ui.Get('market_filter_zerosec', 0),
          zeroSecurityToolTipLabel)]
        return boxes

    def OnReload(self, *args):
        self.sr.reloadBtn.display = False
        self.sr.marketdata.children[0].OnReload()
        if self.sr.sbTabs.GetSelectedArgs() == 'browse':
            self.LoadMarketListOrSearch()
        self.OnOrderChangeTimer = None
        self.lastOnOrderChangeTime = blue.os.GetWallclockTime()

    def ShowInfoFromDetails(self, *args):
        typeID = self.GetTypeIDFromDetails()
        if typeID is not None:
            sm.GetService('info').ShowInfo(typeID)

    def PreviewFromDetails(self, *args):
        typeID = self.GetTypeIDFromDetails()
        if typeID is not None:
            sm.GetService('preview').PreviewType(typeID)

    def GetTypeIDFromDetails(self):
        typeID = None
        invtype = self.GetSelection()
        if invtype:
            typeID = invtype
        if typeID is None:
            if self.sr.Get('detailTypeID'):
                typeID = self.sr.detailTypeID
        return typeID

    def ClickGroupTrace(self, trace, *args):
        if trace.sr.marketGroupInfo:
            self.groupListData = trace.sr.marketGroupInfo
            self.sr.tabs.ShowPanelByName(localization.GetByLabel('UI/Common/Groups'))

    def OpenOnType(self, trace, *args):
        typeID = trace.typeID
        if trace.sr.marketGroupInfo:
            self.groupListData = trace.sr.marketGroupInfo
        searchValueBefore = self.sr.searchInput.GetValue().strip()
        if searchValueBefore:
            self.sr.searchInput.SetText('')
            self.sr.searchInput.caretIndex = (0, 0)
            self.sr.searchInput.CheckHintText()
            self.sr.searchInput.RefreshCaretPosition()
        reloadingDone = False
        if not self.sr.sbTabs.GetSelectedArgs() == 'browse':
            self.sr.sbTabs.ShowPanelByName(localization.GetByLabel('UI/Market/Browse'))
            reloadingDone = True
        if settings.user.ui.Get('showonlyavailable', True):
            settings.user.ui.Set('showonlyavailable', False)
            self.LoadMarketListOrSearch()
            reloadingDone = True
        if searchValueBefore and not reloadingDone:
            self.LoadMarketListOrSearch()
        if self.sr.typescroll:
            self.OpenOnTypeID(typeID)

    def OpenOnTypeID(self, typeID, groupsToSkip = [], *args):
        for node in self.sr.typescroll.GetNodes():
            if typeID in node.get('typeIDs', []) and node.id not in groupsToSkip:
                if self.sr.typescroll.scrollingRange:
                    position = node.scroll_positionFromTop / float(self.sr.typescroll.scrollingRange)
                    self.sr.typescroll.ScrollToProportion(position, threaded=False)
                groupsToSkipCopy = groupsToSkip[:] + [node.id]
                if not node.open:
                    if node.panel is not None:
                        node.panel.OnClick(openGroup=False)
                    else:
                        uicore.registry.SetListGroupOpenState(node.id, True)
                    blue.synchro.Yield()
                    return self.OpenOnTypeID(typeID, groupsToSkipCopy)
            elif node.get('typeID', None) == typeID:
                self.sr.typescroll.SelectNode(node)
                break

    def LoadQuickBar(self, selectFolder = 0, *args):
        self.selectFolder = selectFolder
        self.folders = settings.user.ui.Get('quickbar', {})
        if not self.folders:
            if settings.user.ui.Get('marketquickbar', 0):
                self.LoadOldQuickBar()
        scrolllist = self.LoadQuickBarItems(selectFolder)
        if self.selectFolder:
            selectAFolderLabel = localization.GetByLabel('UI/Market/Marketbase/SelectAFolder')
            result = self.ListWnd([], 'item', selectAFolderLabel, None, 1, contentList=scrolllist)
            if not result:
                return False
            id, parentDepth = result
            if self.depth + 1 + parentDepth + 1 > 7:
                msg = localization.GetByLabel('UI/Market/Marketbase/DeepQuickbarFolder', folderDepth=self.depth + 1 + parentDepth + 1)
                yesNo = eve.Message('AskAreYouSure', {'cons': msg}, uiconst.YESNO)
                return [False, id][yesNo == uiconst.ID_YES]
            return id
        self.sr.typescroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/Common/NothingFound'))

    def LoadOldQuickBar(self):
        items = settings.user.ui.Get('marketquickbar', [])
        for each in items:
            n = utillib.KeyVal()
            n.parent = 0
            n.id = self.lastid
            n.label = each
            self.folders[n.id] = n
            self.lastid += 1

        settings.user.ui.Delete('marketquickbar')

    def LoadMarketData(self, *args):
        invtype = self.GetSelection()
        if self.sr.marketdata:
            if not len(self.sr.marketdata.children):
                MarketData(name='marketdata', parent=self.sr.marketdata, pos=(0, 0, 0, 0))
            marketDataChild = self.sr.marketdata.children[0]
            self.loadingMarketData = marketDataChild.GetInvTypeID()
            if invtype:
                marketDataChild.LoadType(invtype)
                self.StoreTypeInHistory(invtype)
            else:
                marketDataChild.ReloadType()
            self.sr.reloadBtn.display = False
        self.loadingMarketData = None

    def LoadPriceHistory(self, invtype = None, *args):
        invtype = invtype or self.GetSelection()
        if not invtype:
            return
        if self.sr.pricehistory:
            self.sr.reloadBtn.display = False
            if not self.sr.pricehistory.inited:
                self.sr.pricehistory.Startup()
            self.sr.pricehistory.LoadType(invtype)
            self.StoreTypeInHistory(invtype)

    @telemetry.ZONE_METHOD
    def GetSearchResult(self):
        search = self.sr.searchInput.GetValue().lower()
        showOnlyAvailable = settings.user.ui.Get('showonlyavailable', 1)
        if self.sr.lastSearchResult and self.sr.lastSearchResult[0] == search and self.sr.lastSearchResult[2] == showOnlyAvailable:
            scrollList = self.sr.lastSearchResult[1][:]
        else:
            scrollList = []
            byCategories = {}
            if search:
                searchWhat = SEARCH_LOCALIZED
                if not IsUsingDefaultLanguage(session):
                    bilingualSettings = localization.settings.bilingualSettings
                    importantNameSetting = bilingualSettings.GetValue('localizationImportantNames')
                    if importantNameSetting == bilingualSettings.IMPORTANT_NAME_ENGLISH:
                        searchWhat = SEARCH_BOTH
                    elif bilingualSettings.GetValue('languageTooltip'):
                        searchWhat = SEARCH_BOTH
                typeIDFinder = sm.GetService('marketutils').GetMarketTypeIDFinder()
                res = typeIDFinder.FindTypeIDsWithPartialMatch(search, searchWhat)
                allMarketGroups = sm.GetService('marketutils').GetMarketGroups()[None]
                myCategories = {}
                for typeID in res:
                    for mg in allMarketGroups:
                        if typeID in mg.types:
                            topMarketCategory = mg
                            break
                    else:
                        topMarketCategory = None

                    if topMarketCategory is None:
                        continue
                    if topMarketCategory.marketGroupID in byCategories:
                        byCategories[topMarketCategory.marketGroupID].append(typeID)
                    else:
                        byCategories[topMarketCategory.marketGroupID] = [typeID]
                        myCategories[topMarketCategory.marketGroupID] = topMarketCategory

                if len(byCategories) > 1:
                    for categoryID, categoryTypeIDs in byCategories.iteritems():
                        category = myCategories[categoryID]
                        group = GetFromClass(ListGroup, {'GetSubContent': self.GetSeachCategory,
                         'label': category.marketGroupName,
                         'id': ('searchGroups', categoryID),
                         'showlen': 0,
                         'sublevel': 0,
                         'state': 'locked',
                         'BlockOpenWindow': True,
                         'categoryID': category.marketGroupID,
                         'typeIDs': categoryTypeIDs,
                         'iconID': category.iconID,
                         'hint': category.description})
                        scrollList.append(group)

                else:
                    for categoryID, categoryTypeIDs in byCategories.iteritems():
                        fakeNodeData = utillib.KeyVal(typeIDs=categoryTypeIDs, sublevel=-1, categoryID=categoryID)
                        results = self.GetSeachCategory(fakeNodeData)
                        scrollList.extend(results)

        self.sr.lastSearchResult = (search, scrollList[:], showOnlyAvailable)
        return scrollList

    def GetSeachCategory(self, nodedata, *args):
        types = nodedata.typeIDs
        typesByMetaGroupID = self.GetTypesByMetaGroups(types)
        sublevel = nodedata.sublevel
        categoryID = nodedata.categoryID
        scrollList = []
        for metaGroupID, types in sorted(typesByMetaGroupID.items()):
            specialItemGroups = (const.metaGroupStoryline,
             const.metaGroupFaction,
             const.metaGroupOfficer,
             const.metaGroupDeadspace)
            if metaGroupID in specialItemGroups:
                searchGroup = self.GetSearchSubGroup(metaGroupID, types, sublevel=sublevel + 1, categoryID=categoryID)
                scrollList.append((searchGroup.label, searchGroup))
            else:
                for typeID in types:
                    searchEntry = self.GetSearchEntry(typeID, sublevel=sublevel + 1)
                    scrollList.append((' ' + evetypes.GetName(typeID), searchEntry))
                    blue.pyos.BeNice()

        scrollList = [ item[1] for item in localization.util.Sort(scrollList, key=lambda x: x[0]) ]
        return scrollList

    def GetSearchSubGroup(self, metaGroupID, types, sublevel = 0, categoryID = -1, *args):
        if metaGroupID in (const.metaGroupStoryline, const.metaGroupFaction):
            label = localization.GetByLabel('UI/Market/FactionAndStoryline')
        else:
            label = metaGroups.get_name(metaGroupID)
        groupEntry = GetFromClass(MarketMetaGroupEntry, {'GetSubContent': self.GetSearchScrollListFromTypeList,
         'label': label,
         'id': ('searchGroups', (metaGroupID, categoryID)),
         'showlen': 0,
         'metaGroupID': metaGroupID,
         'invTypes': types,
         'sublevel': sublevel,
         'showicon': GetIconFile(metaGroups.get_icon_id(metaGroupID)),
         'state': 'locked',
         'BlockOpenWindow': True,
         'OnToggle': self.OnMetaGroupClicked,
         'typeIDs': types})
        return groupEntry

    def GetSearchScrollListFromTypeList(self, nodedata):
        subList = []
        invTypes = nodedata.invTypes
        sublevel = nodedata.sublevel
        for typeID in invTypes:
            searchEntry = self.GetSearchEntry(typeID, sublevel=sublevel + 1)
            subList.append((evetypes.GetName(typeID), searchEntry))

        subList = [ item[1] for item in localization.util.Sort(subList, key=lambda x: x[0]) ]
        return subList

    def GetSearchEntry(self, typeID, sublevel = 0, *args):
        data = utillib.KeyVal()
        data.label = evetypes.GetName(typeID)
        data.GetMenu = self.OnTypeMenu
        data.invtype = typeID
        data.showinfo = 1
        data.sublevel = sublevel
        data.typeID = typeID
        data.ignoreRightClick = 1
        onlyShowAvailable = settings.user.ui.Get('showonlyavailable', 0)
        if onlyShowAvailable and not self.IsTypeIdInCurrentRange(typeID):
            data.inRange = False
        else:
            data.inRange = True
        entry = GetFromClass(GenericMarketItem, data)
        return entry

    def IsTypeIdInCurrentRange(self, typeID):
        if self.searchAsksForMyRange:
            return typeID in self.searchAsksForMyRange
        return False

    def OnTypeClick(self, typeID, *args):
        if not self.sr.typescroll.GetSelected():
            return
        if self.loadingType:
            self.pendingType = 1
            return
        self.sr.quickType = typeID
        self.ReloadType()

    def OnTypeMenu(self, entry):
        typeID = entry.sr.node.invtype
        categoryID = evetypes.GetCategoryID(typeID)
        menu = [(MenuLabel('UI/Inventory/ItemActions/AddTypeToMarketQuickbar'), self.AddTypeToQuickBar, (entry.sr.node.typeID,)), (MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (typeID,))]
        if categoryID in const.previewCategories and inventorycommon.typeHelpers.GetIcon(typeID) and inventorycommon.typeHelpers.GetIcon(typeID).iconFile != '':
            previewLabel = MenuLabel('UI/Market/Marketbase/Preview')
            menu.append((previewLabel, sm.GetService('preview').PreviewType, (typeID,)))
        if industryCommon.IsBlueprintCategory(categoryID):
            from eve.client.script.ui.shared.industry.industryWnd import Industry
            menu.append((localization.GetByLabel('UI/Industry/ViewInIndustry'), Industry.OpenOrShowBlueprint, (None, typeID)))
        if eve.session.role & ROLEMASK_ELEVATEDPLAYER:
            menu.append(None)
            menu += sm.GetService('menu').GetGMTypeMenu(typeID)
        return menu

    def ShowInfo(self, typeID):
        sm.GetService('info').ShowInfo(typeID)

    def AddTypeToQuickBar(self, typeID, parent = 0, extraText = ''):
        settings.user.ui.Set('quickbar', self.folders)
        settings.user.ui.Set('quickbar_lastid', self.lastid)
        sm.GetService('marketutils').AddTypeToQuickBar(typeID, parent, fromMarket=True, extraText=extraText)
        self.lastid = settings.user.ui.Get('quickbar_lastid', 0)
        self.folders = settings.user.ui.Get('quickbar', {})

    def LoadQuickType(self, quick = None, *args):
        if quick:
            self.sr.quickType = quick.invType
            self.ReloadType()

    def LoadTypeID_Ext(self, typeID):
        self.sr.quickType = typeID
        self.ReloadType()

    def ReloadType(self):
        typeID = self.GetSelection()
        sm.ScatterEvent('OnMarketTypeSelectionChanged', typeID)
        if not typeID:
            self.loadingType = 0
            return
        marketTypes = sm.GetService('marketutils').GetMarketTypes()
        if typeID not in marketTypes:
            self.loadingType = 0
            return
        if self.loadingMarketData and self.loadingMarketData != typeID:
            uthread2.call_after_wallclocktime_delay(self.ReloadType, 0.1)
            return
        self.pendingType = 0
        self.loadingType = 1
        blue.pyos.synchro.Yield()
        try:
            self.sr.tabs.ShowPanelByName(localization.GetByLabel('UI/Common/Details'))
        except StandardError as e:
            self.loadingType = 0
            raise e

        blue.pyos.synchro.Yield()
        typeName = evetypes.GetName(typeID)
        self.sr.detailTop.text = typeName
        self.sr.detailIcon.attrs = Bunch(width=64, height=64, src='typeicon:%s' % typeID, bumped=True, showfitting=True, showtechlevel=True)
        self.sr.detailIcon.typeName = typeName
        self.sr.detailIcon.LoadTypeIcon(typeID)
        self.sr.detailIcon.SetOmegaIconState(typeID)
        self.sr.detailIcon.SetState(uiconst.UI_NORMAL)
        self.sr.detailIcon.Show()
        self.sr.detailInfoicon.state = uiconst.UI_NORMAL
        self.browseBtn.display = True
        self.sr.detailTypeID = typeID
        self.sr.requirements.LoadTypeRequirements(self.sr.detailTypeID)
        if typeID == const.typePlex:
            self.buyPlexButton.Show()
        else:
            self.buyPlexButton.Hide()
        marketGroup, trace = sm.GetService('marketutils').FindMarketGroup(typeID)
        if marketGroup:
            self.sr.detailGroupTrace.sr.marketGroupInfo = marketGroup
            self.sr.detailGroupTrace.text = trace
            self.sr.detailGroupTrace.typeID = typeID
            self.sr.detailGroupTrace.display = True
        else:
            self.sr.detailGroupTrace.display = False
            self.sr.detailGroupTrace.sr.marketGroupInfo = None
            self.sr.detailGroupTrace.typeID = None
        self.loadingType = 0
        if self.pendingType:
            self.ReloadType()

    def GetSelection(self):
        if self.sr.quickType:
            return self.sr.quickType
        selection = self.sr.typescroll.GetSelected()
        if not selection:
            return None
        if hasattr(selection[0], 'invtype'):
            return selection[0].invtype

    def ResetQuickbar(self):
        if eve.Message('ResetQuickbar', buttons=uiconst.YESNO) != uiconst.ID_YES:
            return
        self.folders = {}
        settings.user.ui.Set('quickbar', self.folders)
        self.lastid = 0
        settings.user.ui.Set('quickbar_lastid', self.lastid)
        sm.ScatterEvent('OnMarketQuickbarChange')

    def ResetFilterSettings(self):
        settings.user.ui.Set('showonlyskillsfor', False)
        settings.user.ui.Set('showhavecpuandpower', False)
        settings.user.ui.Set('shownewskills', False)
        settings.user.ui.Set('showonlyavailable', True)
        settings.user.ui.Set('autorefresh', True)
        if self.sr.sbTabs.GetSelectedArgs() == 'browse':
            self.LoadMarketListOrSearch()

    def ResetDetailsSettings(self):
        settings.user.ui.Set('market_filter_price', False)
        settings.user.ui.Set('minEdit_market_filter_price', 0)
        settings.user.ui.Set('maxEdit_market_filter_price', 100000)
        settings.user.ui.Set('market_filter_jumps', False)
        settings.user.ui.Set('minEdit_market_filter_jumps', 0)
        settings.user.ui.Set('maxEdit_market_filter_jumps', 20)
        settings.user.ui.Set('market_filter_quantity', False)
        settings.user.ui.Set('minEdit_market_filter_quantity', 0)
        settings.user.ui.Set('maxEdit_market_filter_quantity', 1000)
        settings.user.ui.Set('market_filter_zerosec', True)
        settings.user.ui.Set('market_filter_lowsec', True)
        settings.user.ui.Set('market_filter_highsec', True)
        settings.user.ui.Set('market_filters_sellorderdev', False)
        settings.user.ui.Set('minEdit_market_filters_sellorderdev', 0)
        settings.user.ui.Set('maxEdit_market_filters_sellorderdev', 0)
        settings.user.ui.Set('market_filters_buyorderdev', False)
        settings.user.ui.Set('minEdit_market_filters_buyorderdev', 0)
        settings.user.ui.Set('maxEdit_market_filters_buyorderdev', 0)
        self.LoadMarketData()
        self.ShowFiltersInUse()

    def LoadQuickBarItems(self, selectFolder = 0, *args):
        import types
        scrolllist = []
        notes = self.GetItems(parent=0)
        tickerFolderID = settings.char.ui.Get(TICKER_SETTING_NAME, 0)
        for id, n in notes.items():
            try:
                if type(n.label) == types.UnicodeType:
                    groupID = ('quickbar', id)
                    data = {'GetSubContent': self.GetGroupSubContent,
                     'label': n.label,
                     'id': groupID,
                     'groupItems': self.GroupGetContentIDList(groupID),
                     'iconMargin': 18,
                     'showlen': 0,
                     'state': 0,
                     'sublevel': 0,
                     'MenuFunction': [self.GroupMenu, self.SelectFolderMenu][self.selectFolder],
                     'BlockOpenWindow': 1,
                     'DropData': self.GroupDropNode,
                     'ChangeLabel': self.GroupChangeLabel,
                     'DeleteFolder': self.GroupDeleteFolder,
                     'selected': 1,
                     'hideNoItem': self.selectFolder,
                     'allowGuids': ['listentry.QuickbarGroup', 'listentry.QuickbarItem'],
                     'selectGroup': selectFolder,
                     'isTickerFolder': tickerFolderID == id}
                    if self.selectFolder:
                        data['OnDblClick'] = self.OnDblClick
                        if data.get('sublevel', 0) + self.depth >= self.maxdepth:
                            return []
                    scrolllist.append((n.label, GetFromClass(QuickbarGroup, data)))
            except Exception as e:
                log.LogWarn('Failed to load quickbar folder, reason: ', e)
                continue

        if scrolllist:
            scrolllist = [ item[1] for item in localization.util.Sort(scrolllist, key=lambda x: x[0]) ]
        tempScrolllist = []
        if not self.selectFolder:
            for id, n in notes.items():
                try:
                    if type(n.label) == types.IntType:
                        groupID = ('quickbar', id)
                        tempScrolllist.append((evetypes.GetName(n.label), GetFromClass(QuickbarItem, {'label': evetypes.GetName(n.label),
                          'typeID': n.label,
                          'id': groupID,
                          'itemID': None,
                          'getIcon': 0,
                          'sublevel': 0,
                          'showinfo': 1,
                          'GetMenu': self.GetQuickItemMenu,
                          'DropData': self.GroupDropNode,
                          'parent': n.parent,
                          'selected': 1,
                          'invtype': n.label,
                          'extraText': n.get('extraText', '')})))
                except Exception as e:
                    log.LogWarn('Failed to load_ quickbar type, reason: ', e)
                    continue

        if tempScrolllist:
            tempScrolllist = [ item[1] for item in localization.util.Sort(tempScrolllist, key=lambda x: x[0]) ]
            scrolllist.extend(tempScrolllist)
        return scrolllist

    def GroupMenu(self, node):
        m = []
        if node.sublevel < self.maxdepth:
            m.append((MenuLabel('UI/Market/NewFolder'), self.NewFolder, (node.id[1], node)))
        return m

    def QuickbarHasFolder(self):
        import types
        if settings.user.ui.Get('quickbar', {}):
            for id, node in settings.user.ui.Get('quickbar', {}).items():
                if type(node.label) == types.UnicodeType:
                    return True

        return False

    def SelectFolderMenu(self, node):
        m = []
        if node.sublevel < self.maxdepth:
            if self.QuickbarHasFolder():
                m.append((MenuLabel('UI/Market/Marketbase/AddGroupToQuickbarFolder'), self.FolderPopUp, (node,)))
            m.append((MenuLabel('UI/Market/Marketbase/AddGroupToQuickbarRoot'), self.FolderPopUp, (node, True)))
        return m

    def FolderPopUp(self, node, root = False):
        self.tempLastid = self.lastid
        self.tempFolders = {}
        self.depth, firstID = self.AddGroupParent(nodedata=node)
        if root:
            id = 0
        else:
            id = self.LoadQuickBar(selectFolder=1)
        if id is not None and id is not False:
            self.tempFolders[firstID].parent = id
            for each in range(firstID, self.tempLastid + 1):
                self.folders[each] = self.tempFolders[each]

            self.lastid = self.tempLastid
            settings.user.ui.Set('quickbar_lastid', self.lastid)

    def GetGroupSubContent(self, nodedata, newitems = 0):
        scrolllist = []
        notelist = self.GetItems(nodedata.id[1])
        if len(notelist):
            qi = 1
            NoteListLength = len(notelist)
            import types
            for id, note in notelist.items():
                if type(note.label) == types.UnicodeType:
                    entry = self.GroupCreateEntry((note.label, id), nodedata.sublevel + 1, selectGroup=self.selectFolder)
                    if entry:
                        scrolllist.append((note.label, entry))

            if scrolllist:
                scrolllist = [ item[1] for item in localization.util.Sort(scrolllist, key=lambda x: x[0]) ]
            tempScrolllist = []
            if not self.selectFolder:
                for id, note in notelist.items():
                    if type(note.label) == types.IntType:
                        entry = self.GroupCreateEntry((note.label, id), nodedata.sublevel + 1)
                        if entry:
                            tempScrolllist.append((evetypes.GetName(note.label), entry))

            if tempScrolllist:
                tempScrolllist = [ item[1] for item in localization.util.Sort(tempScrolllist, key=lambda x: x[0]) ]
                scrolllist.extend(tempScrolllist)
            if len(nodedata.groupItems) != len(scrolllist):
                nodedata.groupItems = self.GroupGetContentIDList(nodedata.id)
        return scrolllist

    def GroupCreateEntry(self, id, sublevel, selectGroup = 0):
        note, id = self.folders[id[1]], id[1]
        import types
        tickerFolderID = settings.char.ui.Get(TICKER_SETTING_NAME, 0)
        if type(note.label) == types.UnicodeType:
            groupID = ('quickbar', id)
            data = {'GetSubContent': self.GetGroupSubContent,
             'label': note.label,
             'id': groupID,
             'groupItems': self.GroupGetContentIDList(groupID),
             'iconMargin': 18,
             'showlen': 0,
             'state': 0,
             'sublevel': sublevel,
             'BlockOpenWindow': 1,
             'parent': note.parent,
             'MenuFunction': self.GroupMenu,
             'ChangeLabel': self.GroupChangeLabel,
             'DeleteFolder': self.GroupDeleteFolder,
             'selected': 1,
             'DropData': self.GroupDropNode,
             'hideNoItem': self.selectFolder,
             'allowGuids': ['listentry.QuickbarGroup', 'listentry.QuickbarItem'],
             'selectGroup': selectGroup,
             'isTickerFolder': tickerFolderID == id}
            if self.selectFolder:
                data['OnDblClick'] = self.OnDblClick
                if data.get('sublevel', 0) + self.depth >= self.maxdepth:
                    return []
            return GetFromClass(QuickbarGroup, data)
        if type(note.label) == types.IntType:
            groupID = ('quickbar', id)
            return GetFromClass(QuickbarItem, {'label': evetypes.GetName(note.label),
             'typeID': note.label,
             'id': groupID,
             'itemID': None,
             'getIcon': 0,
             'sublevel': sublevel,
             'showinfo': 1,
             'GetMenu': self.GetQuickItemMenu,
             'DropData': self.GroupDropNode,
             'parent': note.parent,
             'selected': 1,
             'invtype': note.label,
             'extraText': note.get('extraText', '')})
        del self.folders[id]

    def OnDblClick(self, *args):
        pass

    def GroupGetContentIDList(self, id):
        ids = self.GetItems(id[1])
        test = [ (self.folders[id].label, id) for id in ids ]
        return test

    def GetItems(self, parent):
        dict = {}
        for id in self.folders:
            if self.folders[id].parent == parent:
                dict[id] = self.folders[id]

        return dict

    def NewFolderClick(self, *args):
        self.NewFolder(0)

    def GroupChangeLabel(self, id, newname):
        self.RenameFolder(id[1], name=newname)

    def RenameFolder(self, folderID = 0, entry = None, name = None, *args):
        if name is None:
            folderNameLabel = localization.GetByLabel('UI/Market/Marketbase/FolderName')
            typeNewFolderNameLabel = localization.GetByLabel('UI/Market/Marketbase/TypeNewFolderName')
            ret = utilWindows.NamePopup(folderNameLabel, typeNewFolderNameLabel, maxLength=20)
            if ret is None:
                return self.folders[folderID].label
            name = ret
        self.folders[folderID].label = name
        sm.ScatterEvent('OnMarketQuickbarChange')
        return name

    def NewFolder(self, folderID = 0, node = None, *args):
        folderNameLabel = localization.GetByLabel('UI/Market/Marketbase/FolderName')
        typeFolderNameLabel = localization.GetByLabel('UI/Market/Marketbase/TypeFolderName')
        ret = utilWindows.NamePopup(folderNameLabel, typeFolderNameLabel, maxLength=20)
        if ret is not None:
            self.lastid += 1
            n = utillib.KeyVal()
            n.parent = folderID
            n.id = self.lastid
            n.label = ret
            self.folders[n.id] = n
            settings.user.ui.Set('quickbar', self.folders)
            settings.user.ui.Set('quickbar_lastid', self.lastid)
            sm.ScatterEvent('OnMarketQuickbarChange')
            return n

    def GroupDeleteFolder(self, id):
        import types
        noteID = id[1]
        notes = self.GetItems(noteID)
        for id, note in notes.items():
            if type(note.label) == types.UnicodeType:
                self.GroupDeleteFolder((0, id))
                continue
            self.DeleteFolderNote(id)

        self.DeleteFolderNote(noteID)
        sm.ScatterEvent('OnMarketQuickbarChange')

    def DeleteFolderNote(self, noteID):
        del self.folders[noteID]

    def GroupDropNode(self, id, nodes):
        for node in nodes:
            if getattr(node, 'id', None) and id[1] in self.folders:
                parent = self.folders[id[1]].parent
                shouldContinue = False
                while parent:
                    if node.id[1] == parent or node.id[1] == id[1]:
                        shouldContinue = True
                        break
                    parent = self.folders[parent].parent

                if shouldContinue:
                    continue
            guid = getattr(node, '__guid__', None)
            if guid in ('listentry.FittingEntry',):
                self.AddFittingFolder(node, id[1])
                continue
            shouldContinue = False
            for folderID, data in self.folders.items():
                if data.label == node.typeID and data.parent == id[1]:
                    shouldContinue = True
                    break

            if shouldContinue:
                continue
            if guid in ('listentry.QuickbarItem', 'listentry.QuickbarGroup'):
                noteID = node.id[1]
                if uicore.uilib.Key(uiconst.VK_CONTROL):
                    self.AddTypeToQuickBar(node.typeID, parent=id[1])
                elif noteID in self.folders and noteID != id[1]:
                    self.folders[noteID].parent = id[1]
            elif guid == 'listentry.GenericMarketItem':
                self.AddTypeToQuickBar(node.typeID, parent=id[1])
            elif guid in ('xtriui.ShipUIModule', 'xtriui.InvItem', 'listentry.InvItem', 'listentry.InvAssetItem'):
                self.AddTypeToQuickBar(node.rec.typeID, parent=id[1])
            elif isinstance(node, TypeDragData):
                typeID = node.typeID
                if can_view_market_details(typeID):
                    self.AddTypeToQuickBar(typeID, parent=id[1])

        sm.ScatterEvent('OnMarketQuickbarChange')

    def OnScrollDrop(self, dropObj, nodes):
        if self.sr.sbTabs.GetSelectedArgs() != 'quickbar':
            return
        self.OnQuickbarScrollDrop(dropObj, nodes)

    def OnQuickbarScrollDrop(self, dropObj, nodes):
        for node in nodes:
            guid = getattr(node, '__guid__', None)
            if isinstance(node, TypeDragData):
                typeID = node.typeID
                if can_view_market_details(typeID):
                    self.AddTypeToQuickBar(typeID)
            elif guid == 'listentry.GenericMarketItem':
                self.AddTypeToQuickBar(node.typeID)
            elif guid in ('xtriui.ShipUIModule', 'xtriui.InvItem', 'listentry.InvItem', 'listentry.InvAssetItem'):
                self.AddTypeToQuickBar(node.rec.typeID)
            elif guid in ('listentry.QuickbarItem', 'listentry.QuickbarGroup'):
                self.folders[node.id[1]].parent = 0
                sm.ScatterEvent('OnMarketQuickbarChange')
            elif guid == 'listentry.FittingEntry':
                self.AddFittingFolder(node)

    def AddFittingFolder(self, node, parent = 0):
        self.lastid += 1
        fittingGroup = utillib.KeyVal()
        fittingGroup.parent = parent
        fittingGroup.id = self.lastid
        fittingGroup.label = node.label
        self.folders[fittingGroup.id] = fittingGroup
        settings.user.ui.Set('quickbar', self.folders)
        settings.user.ui.Set('quickbar_lastid', self.lastid)
        rackTypes = sm.GetService('fittingSvc').GetTypesByRack(node.fitting)
        rackNames = {'hiSlots': const.effectHiPower,
         'medSlots': const.effectMedPower,
         'lowSlots': const.effectLoPower,
         'rigSlots': const.effectRigSlot,
         'subSystems': const.effectSubSystem,
         'serviceSlots': const.effectServiceSlot}
        for rack, contents in rackTypes.iteritems():
            if len(contents):
                name = None
                if rack == 'drones':
                    name = localization.GetByLabel('UI/Drones/Drones')
                elif rack == 'charges':
                    name = localization.GetByLabel('UI/Generic/Charges')
                elif rack == 'ice':
                    name = localization.GetByLabel('UI/Market/Marketbase/IceProducts')
                elif rack in rackNames:
                    name = dogma.data.get_effect_display_name(rackNames[rack])
                self.lastid += 1
                n = utillib.KeyVal()
                n.parent = fittingGroup.id
                n.id = self.lastid
                n.label = name
                self.folders[n.id] = n
                cannotAddToQuickbar = []
                for typeID, count in contents.iteritems():
                    if count > 1:
                        extraText = count
                    else:
                        extraText = ''
                    try:
                        self.AddTypeToQuickBar(typeID, parent=n.id, extraText=extraText)
                    except UserError as e:
                        if e.msg == 'cannotTradeOnMarket':
                            cannotAddToQuickbar.append(typeID)
                        else:
                            raise

                settings.user.ui.Set('quickbar', self.folders)
                settings.user.ui.Set('quickbar_lastid', self.lastid)

        self.AddTypeToQuickBar(node.fitting.shipTypeID, parent=fittingGroup.id)
        sm.ScatterEvent('OnMarketQuickbarChange')

    def ShouldShowType(self, typeID):
        filterSkills = settings.user.ui.Get('showonlyskillsfor', 0)
        filterCpuPower = settings.user.ui.Get('showhavecpuandpower', 0)
        filterKnownSkills = settings.user.ui.Get('shownewskills', 0)
        doesMeetReq = True
        if filterSkills or filterCpuPower or filterKnownSkills:
            currShip = sm.StartService('godma').GetItem(eve.session.shipid)
            doesMeetReq, hasSkills, hasPower, hasCpu, hasSkill = self.MeetsRequirements(typeID, ship=currShip, reqTypeSkills=filterSkills, reqTypeCpuPower=filterCpuPower, hasSkill=filterKnownSkills)
        return doesMeetReq

    def FilterItemsForBrowse(self, marketGroupInfo):
        filterNone = settings.user.ui.Get('showonlyavailable', 0)
        ret = []
        for typeID in marketGroupInfo.types:
            ask = self.asksForMyRange.get(typeID, None)
            if (not filterNone or ask) and self.ShouldShowType(typeID):
                ret.append(typeID)

        return ret

    def FilterItemsForGroupPage(self, marketGroupInfo):
        filterNone = settings.user.ui.Get('showonlyavailable', 0)
        marketSvc = sm.StartService('marketQuote')
        ret = []
        marketGroupID = marketGroupInfo.marketGroupID
        for typeID in evetypes.GetTypeIDsByMarketGroup(marketGroupID):
            if not evetypes.IsPublished(typeID):
                continue
            data = None
            ask = self.asksForMyRange.get(typeID, None)
            if ask is None and filterNone:
                continue
            shouldShow = self.ShouldShowType(typeID)
            if not shouldShow:
                continue
            data = utillib.KeyVal()
            data.typeID = typeID
            data.price = getattr(ask, 'price', 0)
            data.qty = getattr(ask, 'volRemaining', 0)
            data.fmt_price = FmtISK(data.price) if data.price else localization.GetByLabel('UI/Market/Marketbase/NoneAvailable')
            data.fmt_qty = FmtAmt(data.qty) if data.qty else '0'
            data.jumps = marketSvc.GetStationDistance(ask.stationID, False) if ask else None
            ret.append(data)

        return ret

    def MeetsRequirements(self, typeID, ship = None, reqTypeSkills = 0, reqTypeCpuPower = 0, hasSkill = 0):
        haveReqSkill = True
        haveReqPower = True
        haveReqCpu = True
        haveSkillAlready = True
        categoryID = evetypes.GetCategoryID(typeID)
        if hasSkill:
            isSkill = categoryID == const.categorySkill
            if isSkill:
                if self.mine.get(typeID, None) is not None:
                    haveSkillAlready = False
        if reqTypeSkills:
            requiredSkills = sm.GetService('clientDogmaStaticSvc').GetRequiredSkills(typeID)
            if requiredSkills:
                for skillID, level in requiredSkills.iteritems():
                    if skillID not in self.mine or self.mine[skillID] < level:
                        haveReqSkill = False
                        break

            else:
                haveReqSkill = True
        if reqTypeCpuPower:
            havePower = 0
            haveCpu = 0
            isHardware = evetypes.IsCategoryHardwareByCategory(categoryID)
            if isHardware:
                powerEffect = None
                powerIdx = None
                powerEffects = [const.effectHiPower, const.effectMedPower, const.effectLoPower]
                for effect in dogma.data.get_type_effects(typeID):
                    if effect.effectID in powerEffects:
                        powerEffect = dogma.data.get_effect(effect.effectID)
                        powerIdx = powerEffects.index(effect.effectID)
                        break

                powerLoad = 0
                cpuLoad = 0
                shipID = eveCfg.GetActiveShip()
                if shipID is not None and powerIdx is not None:
                    dgmAttr = sm.GetService('godma').GetType(typeID)
                    for attribute in dgmAttr.displayAttributes:
                        if attribute.attributeID in (const.attributeCpuLoad, const.attributeCpu):
                            cpuLoad += attribute.value
                        elif attribute.attributeID in (const.attributePowerLoad, const.attributePower):
                            powerLoad += attribute.value

                    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
                    havePower = dogmaLocation.GetAttributeValue(shipID, const.attributePowerOutput) > powerLoad
                    haveCpu = dogmaLocation.GetAttributeValue(shipID, const.attributeCpuOutput) > cpuLoad
                if powerEffect:
                    haveReqPower = havePower
                    haveReqCpu = haveCpu
        meetsReq = haveReqSkill and haveReqPower and haveReqCpu and haveSkillAlready
        return (meetsReq,
         haveReqSkill,
         haveReqPower,
         haveReqCpu,
         haveSkillAlready)

    def OnChange_minEdit_market_filter_price(self, value, *args):
        newValue = self.ConvertInput(value, 2)
        settings.user.ui.Set('minEdit_market_filter_price', newValue)

    def OnChange_maxEdit_market_filter_price(self, value, *args):
        newValue = self.ConvertInput(value, 2)
        settings.user.ui.Set('maxEdit_market_filter_price', newValue)

    def OnChange_minEdit_market_filter_jump(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('minEdit_market_filter_jumps', newValue)

    def OnChange_maxEdit_market_filter_jumps(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('maxEdit_market_filter_jumps', newValue)

    def OnChange_minEdit_market_filter_quantity(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('minEdit_market_filter_quantity', newValue)

    def OnChange_maxEdit_market_filter_quantity(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('maxEdit_market_filter_quantity', newValue)

    def OnChange_minEdit_market_filters_sellorderdev(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('minEdit_market_filters_sellorderdev', newValue)

    def OnChange_maxEdit_market_filters_sellorderdev(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('maxEdit_market_filters_sellorderdev', newValue)

    def OnChange_minEdit_market_filters_buyorderdev(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('minEdit_market_filters_buyorderdev', newValue)

    def OnChange_maxEdit_market_filters_buyorderdev(self, value, *args):
        newValue = self.ConvertInput(value)
        settings.user.ui.Set('maxEdit_market_filters_buyorderdev', newValue)

    def ConvertInput(self, value, numDecimals = None):
        if not value or value == '-':
            value = 0
        value = self.ConvertToPoint(value, numDecimals)
        return value

    def FiltersInUse1(self):
        filterUsed = False
        browseFilters = [(localization.GetByLabel('UI/Market/ShowOnlyAvailable'), 'showonlyavailable'),
         (localization.GetByLabel('UI/Market/Marketbase/FilterBySkills'), 'showonlyskillsfor'),
         (localization.GetByLabel('UI/Market/Marketbase/FilterByCPUAndPowergrid'), 'showhavecpuandpower'),
         (localization.GetByLabel('UI/Market/Marketbase/FilterByUntrainedSkills'), 'shownewskills')]
        retBrowse = ''
        for label, filter in browseFilters:
            if settings.user.ui.Get('%s' % filter, 0):
                filterUsed = True
                temp = '%s<br>' % label
                retBrowse += temp

        if retBrowse == '' and not settings.user.ui.Get('showonlyavailable', 0):
            temp = '%s<br>' % localization.GetByLabel('UI/Common/Show all')
            retBrowse += temp
        if retBrowse:
            retBrowse = '%s<br>%s' % (localization.GetByLabel('UI/Market/Marketbase/BrowseFilters'), retBrowse)
            retBrowse = retBrowse[:-1]
        return (retBrowse, filterUsed)

    def FiltersInUse2(self, *args):
        ret = ''
        jumpFilter = [(localization.GetByLabel('UI/Market/Marketbase/Jumps'), 'market_filter_jumps')]
        detailFilters = [(localization.GetByLabel('UI/Common/Quantity'), 'market_filter_quantity'),
         (localization.GetByLabel('UI/Market/Marketbase/Price'), 'market_filter_price'),
         (localization.GetByLabel('UI/Market/Marketbase/SellOrdersDeviation'), 'market_filters_sellorderdev'),
         (localization.GetByLabel('UI/Market/Marketbase/BuyOrdersDeviation'), 'market_filters_buyorderdev')]
        secFilters = [(localization.GetByLabel('UI/Market/Marketbase/NoHighSecurity'), 'market_filter_highsec'), (localization.GetByLabel('UI/Market/Marketbase/NoLowSecurity'), 'market_filter_lowsec'), (localization.GetByLabel('UI/Market/Marketbase/NoZeroSecurity'), 'market_filter_zerosec')]
        retJump = ''
        for label, filter in jumpFilter:
            if settings.user.ui.Get('%s' % filter, 0):
                min = float(GetNumericValueFromSetting('minEdit_%s' % filter))
                max = float(GetNumericValueFromSetting('maxEdit_%s' % filter))
                andUp = False
                if min > max:
                    andUp = True
                    temp = '%s<br>' % localization.GetByLabel('UI/Market/Marketbase/FilterRangeAndUp', filterType=label, minValue=min)
                else:
                    temp = '%s<br>' % localization.GetByLabel('UI/Market/Marketbase/FilterRangeTo', filterType=label, minValue=min, maxValue=max)
                retJump += temp

        retDetail = retJump
        for label, filter in detailFilters:
            if settings.user.ui.Get('%s' % filter, 0):
                min = float(GetNumericValueFromSetting('minEdit_%s' % filter))
                max = float(GetNumericValueFromSetting('maxEdit_%s' % filter))
                andUp = False
                if min >= max:
                    andUp = filter not in ('market_filters_sellorderdev', 'market_filters_buyorderdev')
                    if andUp:
                        temp = '%s<br>' % localization.GetByLabel('UI/Market/Marketbase/FilterRangeAndUp', filterType=label, minValue=min)
                if not andUp:
                    temp = '%s<br>' % localization.GetByLabel('UI/Market/Marketbase/FilterRangeTo', filterType=label, minValue=min, maxValue=max)
                retDetail += temp

        if retDetail:
            retDetail = '%s<br>%s' % (localization.GetByLabel('UI/Market/Marketbase/DetailFilters'), retDetail)
        retSecurity = ''
        for label, filter in secFilters:
            if not settings.user.ui.Get('%s' % filter, 0):
                temp = '%s<br>' % label
                retSecurity += temp

        if retSecurity:
            retSecurity = '%s<br>%s' % (localization.GetByLabel('UI/Market/Marketbase/SecurityFilters'), retSecurity)
        for each in [retDetail, retSecurity]:
            if each:
                ret += '%s<br>' % each

        if ret:
            ret = ret[:-1]
        return ret

    def CheckboxRange(self, boxes, container):
        for height, label, configname, retval, checked, groupname, numRange, hint, isFloat in boxes:
            box = Container(name='checkbox_%s' % configname, parent=container, align=uiconst.TOTOP, padBottom=const.defaultPadding)
            rbox = Container(name='checkbox_%s' % configname, parent=box, align=uiconst.TORIGHT, width=180)
            cb = RadioButton(text='%s' % label, parent=box, settingsKey=configname, retval=retval, checked=checked, groupname=groupname, callback=self.OnCheckboxChangeSett, align=uiconst.TOPLEFT, height=height, width=150)
            if numRange:
                funcKey = '%s_min' % configname
                fromLabel = localization.GetByLabel('UI/Common/FromNumber')
                minText = eveLabel.EveLabelMedium(text=fromLabel, parent=rbox, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
                minSetValue = GetNumericValueFromSetting('minEdit_%s' % configname)
                if not isFloat:
                    minEdit = SingleLineEditInteger(name='minEdit_%s' % configname, setvalue=minSetValue, parent=rbox, left=minText.left + minText.textwidth + const.defaultPadding, top=0, align=uiconst.CENTERLEFT, minValue=numRange[0], maxValue=numRange[1], OnChange=self.OnChangeFuncs[funcKey])
                    minEdit.AutoFitToText(FmtAmt(sys.maxint))
                else:
                    minEdit = SingleLineEditFloat(name='minEdit_%s' % configname, setvalue=minSetValue, parent=rbox, left=minText.left + minText.textwidth + const.defaultPadding, top=0, align=uiconst.CENTERLEFT, minValue=numRange[0], maxValue=numRange[1], decimalPlaces=2, OnChange=self.OnChangeFuncs[funcKey])
                    minEdit.AutoFitToText(FmtAmt(float(MAX_ORDER_PRICE), showFraction=2))
                funcKey = '%s_max' % configname
                maxText = eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Common/ToNumber'), parent=rbox, left=minEdit.left + minEdit.width + const.defaultPadding, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
                maxSetValue = GetNumericValueFromSetting('maxEdit_%s' % configname)
                if not isFloat:
                    maxEdit = SingleLineEditInteger(name='maxEdit_%s' % configname, setvalue=maxSetValue, parent=rbox, left=maxText.left + maxText.textwidth + const.defaultPadding, top=0, align=uiconst.CENTERLEFT, minValue=numRange[0], maxValue=numRange[1], OnChange=self.OnChangeFuncs[funcKey])
                    maxEdit.AutoFitToText(FmtAmt(sys.maxint))
                else:
                    maxEdit = SingleLineEditFloat(name='maxEdit_%s' % configname, setvalue=maxSetValue, parent=rbox, left=maxText.left + maxText.textwidth + const.defaultPadding, top=0, align=uiconst.CENTERLEFT, minValue=numRange[0], maxValue=numRange[1], decimalPlaces=2, OnChange=self.OnChangeFuncs[funcKey])
                    maxEdit.AutoFitToText(FmtAmt(float(MAX_ORDER_PRICE), showFraction=2))
                rbox.width = maxEdit.left + maxEdit.width + const.defaultPadding
                box.height = rbox.height = max(cb.height, minEdit.height, minText.height, maxEdit.height, maxText.height)
            if hint:
                cb.hint = hint

    def SetupFilters(self):
        settings.user.ui.Set('showonlyavailable', settings.user.ui.Get('showonlyavailable', True))
        settings.user.ui.Set('showonlyskillsfor', settings.user.ui.Get('showonlyskillsfor', False))
        settings.user.ui.Set('showhavecpuandpower', settings.user.ui.Get('showhavecpuandpower', False))
        settings.user.ui.Set('shownewskills', settings.user.ui.Get('shownewskills', False))
        settings.user.ui.Set('market_filter_price', settings.user.ui.Get('market_filter_price', False))
        settings.user.ui.Set('minEdit_market_filter_price', GetNumericValueFromSetting('minEdit_market_filter_price'))
        settings.user.ui.Set('maxEdit_market_filter_price', GetNumericValueFromSetting('maxEdit_market_filter_price', 100000))
        settings.user.ui.Set('market_filter_jumps', settings.user.ui.Get('market_filter_jumps', False))
        settings.user.ui.Set('minEdit_market_filter_jumps', GetNumericValueFromSetting('minEdit_market_filter_jumps'))
        settings.user.ui.Set('maxEdit_market_filter_jumps', GetNumericValueFromSetting('maxEdit_market_filter_jumps', 20))
        settings.user.ui.Set('market_filter_quantity', settings.user.ui.Get('market_filter_quantity', False))
        settings.user.ui.Set('minEdit_market_filter_quantity', GetNumericValueFromSetting('minEdit_market_filter_quantity'))
        settings.user.ui.Set('maxEdit_market_filter_quantity', GetNumericValueFromSetting('maxEdit_market_filter_quantity', 1000))
        settings.user.ui.Set('market_filter_zerosec', settings.user.ui.Get('market_filter_zerosec', True))
        settings.user.ui.Set('market_filter_lowsec', settings.user.ui.Get('market_filter_lowsec', True))
        settings.user.ui.Set('market_filter_highsec', settings.user.ui.Get('market_filter_highsec', True))
        settings.user.ui.Set('market_filters_sellorderdev', settings.user.ui.Get('market_filters_sellorderdev', False))
        settings.user.ui.Set('minEdit_market_filters_sellorderdev', GetNumericValueFromSetting('minEdit_market_filters_sellorderdev'))
        settings.user.ui.Set('maxEdit_market_filters_sellorderdev', GetNumericValueFromSetting('maxEdit_market_filters_sellorderdev'))
        settings.user.ui.Set('market_filters_buyorderdev', settings.user.ui.Get('market_filters_buyorderdev', False))
        settings.user.ui.Set('minEdit_market_filters_buyorderdev', GetNumericValueFromSetting('minEdit_market_filters_buyorderdev'))
        settings.user.ui.Set('maxEdit_market_filters_buyorderdev', GetNumericValueFromSetting('maxEdit_market_filters_buyorderdev'))
        settings.user.ui.Set('quickbar', settings.user.ui.Get('quickbar', {}))
        settings.user.ui.Set('autorefresh', settings.user.ui.Get('autorefresh', True))

    def AddGroupParent(self, nodedata = None, newitems = 0):
        marketGroupID = None
        self.parentDictionary = {}
        if nodedata:
            marketGroupID = nodedata.marketGroupInfo.marketGroupID
        firstID = self.InsertQuickbarGroupItem(nodedata.marketGroupInfo.marketGroupName, 0)
        self.parentDictionary[marketGroupID] = self.tempLastid
        scrolllist = self.AddGroupChildren(nodedata=nodedata)
        self.test = QuickbarEntries()
        depth = self.test.Load(contentList=scrolllist, maxDepth=5, parentDepth=nodedata.sublevel)
        self.test.Close()
        return (depth, firstID)

    def AddGroupChildren(self, nodedata = None):
        scrolllist = []
        if nodedata and nodedata.marketGroupInfo.hasTypes:
            parent = self.parentDictionary.get(nodedata.marketGroupInfo.marketGroupID, 0)
            for typeID in nodedata.typeIDs:
                self.InsertQuickbarGroupItem(typeID, parent)

        else:
            marketGroupID = None
            level = 0
            if nodedata:
                marketGroupID = nodedata.marketGroupInfo.marketGroupID
                level = nodedata.sublevel + 1
            grouplist = sm.GetService('marketutils').GetMarketGroups()[marketGroupID]
            for marketGroupInfo in grouplist:
                if not len(marketGroupInfo.types):
                    continue
                if self.destroyed:
                    return
                items = [ typeID for typeID in marketGroupInfo.types ]
                groupID = (marketGroupInfo.marketGroupName, marketGroupInfo.marketGroupID)
                data = {'GetSubContent': self.AddGroupChildren,
                 'id': groupID,
                 'typeIDs': items,
                 'marketGroupInfo': marketGroupInfo,
                 'sublevel': level}
                parent = self.parentDictionary.get(marketGroupInfo.parentGroupID, 0)
                self.InsertQuickbarGroupItem(marketGroupInfo.marketGroupName, parent)
                self.parentDictionary[marketGroupInfo.marketGroupID] = self.tempLastid
                scrolllist.append(((marketGroupInfo.hasTypes, marketGroupInfo.marketGroupName.lower()), GetFromClass(QuickbarGroup, data)))

        return scrolllist

    def InsertQuickbarGroupItem(self, label, parent, extraText = ''):
        self.tempLastid += 1
        n = utillib.KeyVal()
        n.parent = parent
        n.id = self.tempLastid
        n.label = label
        n.extraText = extraText
        self.tempFolders[n.id] = n
        return n.id

    def ListWnd(self, lst, listtype = None, caption = None, hint = None, ordered = 0, minw = 200, minh = 256, minChoices = 1, maxChoices = 1, initChoices = [], validator = None, isModal = 1, scrollHeaders = [], iconMargin = 0, contentList = None):
        if caption is None:
            caption = localization.GetByLabel('UI/Market/Marketbase/SelectAFolder')
        if not isModal:
            SelectFolderWindow.CloseIfOpen()
        wnd = SelectFolderWindow.Open(lst=[], listtype=listtype, ordered=ordered, minw=minw, minh=minh, caption=caption, minChoices=minChoices, maxChoices=maxChoices, initChoices=initChoices, validator=validator, scrollHeaders=scrollHeaders, iconMargin=iconMargin)
        wnd.scroll.Load(contentList=contentList)
        wnd.Error(wnd.GetError(checkNumber=0))
        if hint:
            wnd.SetHint('<center>' + hint)
        if isModal:
            wnd.DefineButtons(uiconst.OKCANCEL)
            if wnd.ShowModal() == uiconst.ID_OK:
                return wnd.result
            else:
                return
        else:
            wnd.DefineButtons(uiconst.CLOSE)
            wnd.Maximize()

    def ConvertToPoint(self, value, numDigits = 0):
        ret = ConvertDecimal(value, ',', '.', numDigits)
        if numDigits is not None:
            ret = '%.*f' % (numDigits, float(ret))
        return ret

    def StoreTypeInHistory(self, typeID):
        if len(self.historyData) > 0:
            newHistory = self.historyData[:self.historyIdx + 1]
            lastTypeID = newHistory[min(self.historyIdx, len(self.historyData) - 1)]
            if lastTypeID != typeID:
                newHistory.append(typeID)
                self.historyIdx += 1
                self.historyData = newHistory
        else:
            self.historyData.append(typeID)
            self.historyIdx = 0
        self.ChangeBackAndForwardButtons()

    def GoBack(self, *args):
        if len(self.historyData) > 1 and self.historyIdx > 0:
            self.historyIdx = max(0, self.historyIdx - 1)
            typeID = self.historyData[min(self.historyIdx, len(self.historyData) - 1)]
            marketWnd = RegionalMarket.GetIfOpen()
            if marketWnd:
                marketWnd.LoadTypeID_Ext(typeID)

    def GoForward(self, *args):
        if self.historyIdx is None:
            return
        if len(self.historyData) > self.historyIdx + 1:
            self.historyIdx = max(0, self.historyIdx + 1)
            typeID = self.historyData[min(self.historyIdx, len(self.historyData) - 1)]
            marketWnd = RegionalMarket.GetIfOpen()
            if marketWnd:
                marketWnd.LoadTypeID_Ext(typeID)

    def ChangeBackAndForwardButtons(self):
        if self.historyIdx == 0:
            self.DisableArrow(self.goBackBtn)
        else:
            self.EnableArrow(self.goBackBtn)
        if self.historyIdx >= len(self.historyData) - 1:
            self.DisableArrow(self.goForwardBtn)
        else:
            self.EnableArrow(self.goForwardBtn)

    def DisableArrow(self, btn):
        btn.Disable()

    def EnableArrow(self, btn):
        btn.Enable()

    def GetImportMenu(self, menuParent):
        hint = GetByLabel('UI/Market/Marketbase/ImportQuickbarFormatHint', typeID=const.typeSpaceshipCommand)
        menuParent.AddIconEntry(icon=ACTION_ICON, text=GetByLabel('UI/Market/Marketbase/ImportNewQuickbar'), callback=self.ImportQuickbar, hint=hint)
        menuParent.AddIconEntry(icon=ACTION_ICON, text=GetByLabel('UI/Market/Marketbase/ImportQuickbarReplace'), callback=self.ImportQuickbarReplace, hint=hint)

    def ImportQuickbarReplace(self):
        self.ImportQuickbar(replace=True)

    def ImportQuickbar(self, replace = False):
        typeIDFinder = sm.GetService('marketutils').GetMarketTypeIDFinder()
        quickbarImporter = QuickbarImporter(typeIDFinder)
        text = GetClipboardData()
        if replace:
            lastID = 0
        else:
            lastID = self.lastid
        bundleDict = quickbarImporter.ImportText(text, lastID + 1)
        if bundleDict:
            quickbar = {} if replace else settings.user.ui.Get('quickbar', {})
            newQuickbarItems = {k:utillib.KeyVal(v) for k, v in bundleDict.iteritems()}
            quickbar.update(newQuickbarItems)
            settings.user.ui.Set('quickbar', quickbar)
            settings.user.ui.Set('quickbar_lastid', max(bundleDict))
            sm.ScatterEvent('OnMarketQuickbarChange')

    def GetExportMenu(self, menuParent):
        menuParent.AddIconEntry(icon=ACTION_ICON, text=GetByLabel('UI/Market/Marketbase/CopyQuickbarToClipboard'), callback=self.GetExportedQuickbarLocalized)
        if self.AreExtraExportOptionsAvailable():
            menuParent.AddIconEntry(icon=ACTION_ICON, text=GetByLabel('UI/Market/Marketbase/CopyQuickbarToClipboardInEnglish'), callback=self.GetExportedQuickbar)

    def GetExportedQuickbarLocalized(self):
        return self._GetExportedQuickbar(True)

    def GetExportedQuickbar(self, *args):
        return self._GetExportedQuickbar(False)

    def _GetExportedQuickbar(self, isLocalized = True):
        quickbar = settings.user.ui.Get('quickbar', {})
        exporter = QuickbarExporter()
        exportText = exporter.ExportQuickbarToClipboard(quickbar, isLocalized)
        blue.pyos.SetClipboardData(exportText)

    def AreExtraExportOptionsAvailable(self):
        extraOptions = boot.region != 'optic' and session.languageID != 'EN'
        return extraOptions


class MarketGroupEntry(ContainerAutoSize):
    default_name = 'MarketGroupEntry'
    default_align = uiconst.TOTOP
    PADDING_GENERIC = const.defaultPadding * 2

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        data = attributes.data
        typeID = data.invType
        self.topCont = ContainerAutoSize(name='topCont', parent=self, align=uiconst.TOTOP)
        typeImage = MarketGroupItemImage(parent=self.topCont, align=uiconst.TOPLEFT, width=64, height=64, state=uiconst.UI_NORMAL)
        typeImage.attrs = data.typeImageAttributes
        typeImage.typeName = evetypes.GetName(typeID)
        typeImage.LoadTypeIcon(typeID)
        typeImage.SetOmegaIconState(typeID)
        typeNameLabel = eveLabel.EveCaptionMedium(parent=self.topCont, align=uiconst.TOPLEFT, left=typeImage.left + typeImage.width + self.PADDING_GENERIC, text=typeImage.typeName, name='typeNameLabel')
        InfoIcon(parent=self.topCont, align=uiconst.TOPLEFT, typeID=typeID, left=typeNameLabel.left + typeNameLabel.width + const.defaultPadding, top=typeNameLabel.top + (typeNameLabel.height - 16) / 2)
        RequirementsContainer(parent=self.topCont, align=uiconst.TOPLEFT, top=typeNameLabel.top + typeNameLabel.height + const.defaultPadding, left=typeNameLabel.left, width=200, typeID=typeID)
        if typeID == const.typePlex:
            PurchaseButton(name='buyPlexButton', parent=self.topCont, align=uiconst.TOPLEFT, top=typeNameLabel.top + typeNameLabel.height + 8, left=typeNameLabel.left, width=70, height=20, fontsize=12, func=lambda *args: uicore.cmd.CmdBuyPlex(logContext=FROM_PLEX_MARKET_GROUP), text=localization.GetByLabel('UI/VirtualGoodsStore/Buttons/BuyPlex'))
        combinedDescription = data.bestPrice + '<br><fontsize=16><b>' + data.marketData.fmt_price + '</b></fontsize>'
        if data.unitsAvailable:
            combinedDescription += '<br>' + data.unitsAvailable
        if HasTraits(data.invType):
            TraitsContainer(parent=self, typeID=data.invType, align=uiconst.TOTOP, padding=(self.PADDING_GENERIC,
             4,
             self.PADDING_GENERIC,
             self.PADDING_GENERIC))
        elif data.description:
            combinedDescription = data.description + '<br><br>' + combinedDescription
        eveLabel.Label(parent=self, align=uiconst.TOTOP, padding=(0,
         4,
         self.PADDING_GENERIC,
         0), state=uiconst.UI_NORMAL, name='descriptionLabel', text=combinedDescription)
        button_group = ButtonGroup(name='buttonCont', parent=self, align=uiconst.TOTOP, top=16, button_alignment=AxisAlignment.START, density=Density.COMPACT)
        Button(parent=button_group, label=localization.GetByLabel('UI/Market/Marketbase/CommandViewDetails'), func=sm.GetService('marketutils').ShowMarketDetails, args=(typeID, None), hint=localization.GetByLabel('Tooltips/Market/MarketGroupsViewDetails'), variant=ButtonVariant.GHOST)
        if data.marketData.qty:
            buyLabel = localization.GetByLabel('UI/Market/MarketQuote/CommandBuy')
            buttonName = 'Buy_Btn'
        else:
            buyLabel = localization.GetByLabel('UI/Market/Marketbase/CommandPlaceBuyOrder')
            buttonName = 'Place Buy Order_Btn'
        if data.marketData.qty:
            buyHint = localization.GetByLabel('Tooltips/Market/MarketGroupsBuyButton')
        else:
            buyHint = localization.GetByLabel('Tooltips/Market/MarketGroupsPlaceBuy')
        Button(parent=button_group, name=buttonName, label=buyLabel, func=sm.GetService('marketutils').Buy, args=(typeID, None), hint=buyHint, variant=ButtonVariant.GHOST)
        if industryCommon.IsBlueprintCategory(evetypes.GetCategoryID(typeID)):
            from eve.client.script.ui.shared.industry.industryWnd import Industry
            Button(parent=button_group, label=localization.GetByLabel('UI/Industry/ViewInIndustry'), func=Industry.OpenOrShowBlueprint, args=(None, typeID), variant=ButtonVariant.GHOST)
        DividerLine(parent=self, align=uiconst.TOTOP, top=16, padBottom=16)


class MarketData(Container):
    __guid__ = 'form.MarketData'
    __notifyevents__ = ['OnPathfinderSettingsChange', 'OnSessionChanged']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.name = 'marketQuote'
        self.caption = 'Market Data'
        self.prefs = 'marketquote'
        self.invType = None
        self.loading = None
        self.scrollHeight = 0
        self.allMyOrderIDs = set()
        self.buyheadersPointers = {localization.GetByLabel('UI/Market/Marketbase/Jumps'): pConst.UNIQUE_NAME_MARKET_SELLERS_JUMP_COL,
         localization.GetByLabel('UI/Common/Quantity'): pConst.UNIQUE_NAME_MARKET_SELLERS_QTY_COL,
         localization.GetByLabel('UI/Market/Marketbase/Price'): pConst.UNIQUE_NAME_MARKET_SELLERS_PRICE_COL}
        self.sellheadersPointers = {localization.GetByLabel('UI/Market/Marketbase/Jumps'): pConst.UNIQUE_NAME_MARKET_BUYERS_JUMP_COL,
         localization.GetByLabel('UI/Common/Quantity'): pConst.UNIQUE_NAME_MARKET_BUYERS_QTY_COL,
         localization.GetByLabel('UI/Market/Marketbase/Price'): pConst.UNIQUE_NAME_MARKET_BUYERS_PRICE_COL}
        self.buyheaders = [localization.GetByLabel('UI/Market/Marketbase/Jumps'),
         localization.GetByLabel('UI/Common/Quantity'),
         localization.GetByLabel('UI/Market/Marketbase/Price'),
         localization.GetByLabel('UI/Common/Location'),
         localization.GetByLabel('UI/Market/Marketbase/ExpiresIn')]
        self.sellheaders = [localization.GetByLabel('UI/Market/Marketbase/Jumps'),
         localization.GetByLabel('UI/Common/Quantity'),
         localization.GetByLabel('UI/Market/Marketbase/Price'),
         localization.GetByLabel('UI/Common/Location'),
         localization.GetByLabel('UI/Common/Range'),
         localization.GetByLabel('UI/Market/MarketQuote/HeaderMinVolumn'),
         localization.GetByLabel('UI/Market/Marketbase/ExpiresIn')]
        self.avgSellPrice = None
        self.avgBuyPrice = None
        self.sr.buyParent = Container(name='buyParent', parent=self, align=uiconst.TOTOP, height=64, uniqueUiName=pConst.UNIQUE_NAME_MARKET_SELLER_LIST)
        buyLeft = Container(name='buyLeft', parent=self.sr.buyParent, align=uiconst.TOTOP, height=20)
        sellersLabel = localization.GetByLabel('UI/Market/Marketbase/Sellers')
        cap = eveLabel.EveCaptionMedium(text=sellersLabel, parent=buyLeft, align=uiconst.TOPLEFT)
        buyLeft.height = max(buyLeft.height, cap.textheight)
        a = eveLabel.EveLabelSmall(text='', parent=buyLeft, left=24, top=0, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        a.OnClick = self.BuyClick
        a.GetMenu = None
        self.buyFiltersActive1 = a
        a = eveLabel.EveLabelSmall(text='', parent=buyLeft, left=24, top=14, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        a.OnClick = self.BuyClick
        a.GetMenu = None
        self.buyFiltersActive2 = a
        self.sr.buyIcon = Sprite(name='buyIcon', parent=buyLeft, width=16, height=16, left=6, top=0, align=uiconst.TOPRIGHT)
        self.sr.buyIcon.OnClick = self.BuyClick
        self.sr.buyIcon.state = uiconst.UI_HIDDEN
        button_group = ButtonGroup(parent=self, align=uiconst.TOBOTTOM, padTop=16, button_alignment=AxisAlignment.END)
        Button(parent=button_group, name='Place Buy Order_Btn', label=localization.GetByLabel('UI/Market/Marketbase/CommandPlaceBuyOrder'), func=self.PlaceOrder, args=('buy',), variant=ButtonVariant.PRIMARY, texturePath=eveicon.isk)
        Button(parent=button_group, label=localization.GetByLabel('UI/Inventory/ItemActions/FindInContracts'), func=self.FindInContracts, args=())
        Button(parent=button_group, label=localization.GetByLabel('UI/Market/Marketbase/ExportToFile'), func=self.ExportToFile, hint=localization.GetByLabel('Tooltips/Market/MarketDetailsExportFile'), variant=ButtonVariant.GHOST)
        divider = Divider(name='divider', parent=self, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=16, show_line=True)
        divider.Startup(self.sr.buyParent, 'height', 'y', 64, self.scrollHeight)
        divider.OnSizeChanged = self.OnDetailScrollSizeChanged
        self.sr.divider = divider
        self.sr.buyscroll = eveScroll.Scroll(name='buyscroll', parent=self.sr.buyParent, rowPadding=1)
        self.sr.buyscroll.multiSelect = 0
        self.sr.buyscroll.smartSort = 1
        self.sr.buyscroll.ignoreHeaderWidths = 1
        self.sr.buyscroll.sr.id = '%sBuyScroll' % self.prefs
        self.sr.buyscroll.OnColumnChanged = self.OnBuyColumnChanged
        self.sr.buyscroll.SetDefaultSmartSorting(GetByLabel('UI/Market/MarketQuote/headerPrice'), SortDirection.ASCENDING, self.buyheaders)
        Container(name='divider', align=uiconst.TOTOP, height=const.defaultPadding, parent=self)
        self.sr.sellParent = Container(name='sellParent', parent=self, align=uiconst.TOALL, uniqueUiName=pConst.UNIQUE_NAME_MARKET_BUYER_LIST)
        sellLeft = Container(name='sellLeft', parent=self.sr.sellParent, align=uiconst.TOTOP, height=20)
        buyersLabel = localization.GetByLabel('UI/Market/Marketbase/Buyers')
        cap = eveLabel.EveCaptionMedium(text=buyersLabel, parent=sellLeft, align=uiconst.TOPLEFT)
        sellLeft.height = max(sellLeft.height, cap.textheight)
        a = eveLabel.EveLabelSmall(text='', parent=sellLeft, left=24, top=0, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL)
        a.OnClick = self.SellClick
        a.GetMenu = None
        self.sellFiltersActive1 = a
        a = eveLabel.EveLabelSmall(text='', parent=sellLeft, left=24, top=14, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        a.OnClick = self.SellClick
        a.GetMenu = None
        self.sellFiltersActive2 = a
        self.sr.sellIcon = Sprite(name='sellIcon', parent=sellLeft, width=16, height=16, left=6, top=0, align=uiconst.TOPRIGHT)
        self.sr.sellIcon.OnClick = self.SellClick
        self.sr.sellIcon.state = uiconst.UI_HIDDEN
        self.sr.sellscroll = eveScroll.Scroll(name='sellscroll', parent=self.sr.sellParent, rowPadding=1)
        self.sr.sellscroll.multiSelect = 0
        self.sr.sellscroll.smartSort = 1
        self.sr.sellscroll.ignoreHeaderWidths = 1
        self.sr.sellscroll.sr.id = '%sSellScroll' % self.prefs
        self.sr.sellscroll.OnColumnChanged = self.OnSellColumnChanged
        self.sr.sellscroll.SetDefaultSmartSorting(GetByLabel('UI/Market/MarketQuote/headerPrice'), SortDirection.DESCENDING, self.sellheaders)
        self._OnResize()
        sm.RegisterNotify(self)
        self.inited = 1
        self.sr.buy_ActiveFilters = 1
        self.sr.sell_ActiveFilters = 1

    def _GetButtonDataForExportToFile(self):
        return (localization.GetByLabel('UI/Market/Marketbase/ExportToFile'),
         self.ExportToFile,
         (),
         84,
         False,
         False,
         False,
         localization.GetByLabel('Tooltips/Market/MarketDetailsExportFile'),
         None,
         Button,
         'ExportToFileButton')

    def _GetButtonDataForPlaceOrder(self):
        return (localization.GetByLabel('UI/Market/Marketbase/CommandPlaceBuyOrder'),
         self.PlaceOrder,
         ('buy',),
         84,
         False,
         False,
         False,
         localization.GetByLabel('Tooltips/Market/MarketDetailsPlaceBuyOrder'),
         None,
         Button,
         'Place Buy Order_Btn')

    def OnDetailScrollSizeChanged(self):
        h = self.sr.buyParent.height
        absHeight = self.absoluteBottom - self.absoluteTop
        if h > absHeight - self.height - 64:
            h = absHeight - self.height - 64
            ratio = float(h) / absHeight
            settings.user.ui.Set('detailScrollHeight', ratio)
            self._OnResize()
            return
        ratio = float(h) / absHeight
        settings.user.ui.Set('detailScrollHeight', ratio)

    def SellClick(self, *args):
        self.sr.sell_ActiveFilters = not self.sr.sell_ActiveFilters
        self.Reload('sell')

    def BuyClick(self, *args):
        self.sr.buy_ActiveFilters = not self.sr.buy_ActiveFilters
        self.Reload('buy')

    def ExportToFile(self, *args):
        if not self.invType:
            return
        sm.GetService('marketQuote').DumpOrdersForType(self.invType)

    def OnPathfinderSettingsChange(self, *args):
        self.ReloadType()

    def OnSessionChanged(self, isremote, session, change):
        if 'solarsystemid' in change:
            self.ReloadType()

    def _OnResize(self, *args):
        if self and not self.destroyed and self.sr.buyParent:
            self.scrollHeight = self.absoluteBottom - self.absoluteTop - 34 - 64
            height = (self.absoluteBottom - self.absoluteTop - 46) / 2
            absHeight = self.absoluteBottom - self.absoluteTop
            ratio = settings.user.ui.Get('detailScrollHeight', 0.5)
            h = int(ratio * absHeight)
            if h > self.scrollHeight:
                h = self.scrollHeight
            self.sr.buyParent.height = max(64, h)
            self.sr.divider.max = self.scrollHeight

    def OnBuyColumnChanged(self, tabstops):
        if self.loading != 'buy':
            self.Reload('buy')

    def OnSellColumnChanged(self, tabstops):
        if self.loading != 'sell':
            self.Reload('sell')

    def PlaceOrder(self, what, *args):
        if not self.invType:
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Market/Marketbase/NoTypeToBuy')})
            return
        if what == 'buy':
            sm.GetService('marketutils').Buy(self.invType, placeOrder=True)
        elif what == 'sell':
            uicore.cmd.OpenAssets()

    def FindInContracts(self):
        sm.GetService('contracts').FindRelated(self.invType, None, None, None, None, None)

    def Reload(self, what):
        records = self.sr.Get('%sItems' % what, None)
        scrollList = []
        scroll = self.sr.Get('%sscroll' % what, None)
        self.loading = what
        if what == 'sell':
            headers = self.sellheaders
            columnNameAndPointersDict = self.sellheadersPointers
        else:
            headers = self.buyheaders
            columnNameAndPointersDict = self.buyheadersPointers
        marketUtil = sm.GetService('marketutils')
        marketQuoteSvc = sm.GetService('marketQuote')
        funcs = marketUtil.GetFuncMaps()

        def IsOrderASellWithinReach(order):
            if what != 'sell':
                return False
            dockedLocationID = session.stationid or session.structureid
            if marketQuoteSvc.SkipBidDueToStructureRestrictions(order, dockedLocationID):
                return False
            if order.jumps <= order.range:
                return True
            if session.stationid and order.range == -1 and order.stationID == session.stationid:
                return True
            if session.solarsystemid and order.jumps == 0:
                return True
            return False

        usingFilters = self.GetFilters2()[0]
        foundCounter = 0
        destPathList = sm.GetService('starmap').GetDestinationPath()
        if self.invType and records:
            dataList = []
            scroll.sr.headers = headers
            visibleHeaders = scroll.GetColumns()
            accumPrice = 0
            count = 0
            hasMarker = False
            for order in records[0]:
                data = utillib.KeyVal()
                data.label = ''
                data.typeID = order.typeID
                data.order = order
                data.mode = what
                data.inMyPath = self._IsInMyPath(destPathList, order.solarSystemID, order.stationID)
                accumPrice += order.price * order.volRemaining
                count += order.volRemaining
                data.flag = IsOrderASellWithinReach(order)
                data.markAsMine = order.orderID in self.allMyOrderIDs
                if data.flag or data.markAsMine or data.inMyPath:
                    hasMarker = True
                expires = order.issueDate + order.duration * const.DAY - blue.os.GetWallclockTime()
                if expires < 0:
                    continue
                for header in visibleHeaders:
                    header = StripTags(header, stripOnly=['localized'])
                    funcName = funcs.get(header, None)
                    if funcName and hasattr(marketUtil, funcName):
                        apply(getattr(marketUtil, funcName, None), (order, data))
                    else:
                        log.LogWarn('Unsupported header in record', header, order)
                        data.label += '###<t>'

                self.SetDataValues(order, data)
                data.label = data.label[:-3]
                dataList.append(data)

            avg = None
            if count > 0:
                avg = round(float(accumPrice / count), 2)
            if what == 'sell':
                self.avgSellPrice = avg
            else:
                self.avgBuyPrice = avg
            for data in dataList:
                if self.ApplyDetailFilters(data, self.sr.Get('%s_ActiveFilters' % what, None)):
                    data.isLabelOffset = hasMarker
                    scrollList.append(GetFromClass(MarketOrder, data))
                else:
                    foundCounter += 1

        hintText = ''
        if not scrollList:
            if self.invType:
                if (usingFilters or settings.user.ui.Get('market_filters_%sorderdev' % ['buy', 'sell'][what == 'buy'], 0)) and self.sr.Get('%s_ActiveFilters' % what, None):
                    hintText = localization.GetByLabel('UI/Market/Marketbase/NoOrdersMatched')
                else:
                    hintText = localization.GetByLabel('UI/Market/Orders/NoOrdersFound')
            else:
                hintText = localization.GetByLabel('UI/Market/Marketbase/NoTypeToBuy')
                self.sr.filtersText.text = ''
                self.sr.filtersText.hint = ''
        scroll.Load(contentList=scrollList, headers=headers, noContentHint=hintText)
        pConst.SetUniqueNamesForColumns(scroll, columnNameAndPointersDict)
        if what == 'buy':
            if usingFilters or settings.user.ui.Get('market_filters_sellorderdev', 0):
                if self.sr.buy_ActiveFilters:
                    text1 = localization.GetByLabel('UI/Market/Marketbase/AdditionalEntriesFound', foundCounter=foundCounter)
                    text2 = localization.GetByLabel('UI/Market/Marketbase/TurnFiltersOff')
                else:
                    text1 = localization.GetByLabel('UI/Market/Marketbase/TurnFiltersOn')
                    text2 = ''
                self.buyFiltersActive1.text = text1
                self.buyFiltersActive2.text = text2
                self.sr.buyIcon.state = uiconst.UI_NORMAL
                self.SetFilterIcon2(self.sr.buyIcon, on=bool(self.sr.buy_ActiveFilters))
            else:
                self.buyFiltersActive1.text = ''
                self.buyFiltersActive2.text = ''
                self.sr.buyIcon.state = uiconst.UI_HIDDEN
        if what == 'sell':
            if usingFilters or settings.user.ui.Get('market_filters_buyorderdev', 0):
                if self.sr.sell_ActiveFilters:
                    text1 = localization.GetByLabel('UI/Market/Marketbase/AdditionalEntriesFound', foundCounter=foundCounter)
                    text2 = localization.GetByLabel('UI/Market/Marketbase/TurnFiltersOff')
                else:
                    text1 = localization.GetByLabel('UI/Market/Marketbase/TurnFiltersOn')
                    text2 = ''
                self.sellFiltersActive1.text = text1
                self.sellFiltersActive2.text = text2
                self.sr.sellIcon.state = uiconst.UI_NORMAL
                self.SetFilterIcon2(self.sr.sellIcon, on=bool(self.sr.sell_ActiveFilters))
            else:
                self.sellFiltersActive1.text = ''
                self.sellFiltersActive2.text = ''
                self.sr.sellIcon.state = uiconst.UI_HIDDEN
        self.loading = None

    def _IsInMyPath(self, path, solarsystemID, locationID):
        if solarsystemID in path:
            return True
        if locationID in path:
            return True
        if not eveCfg.IsDocked() and solarsystemID == session.solarsystemid2:
            return True
        return False

    def SetFilterIcon2(self, icon, on, *args):
        if on:
            iconNo = 'ui_38_16_205'
        else:
            iconNo = 'ui_38_16_204'
        icon.LoadIcon(iconNo)

    def SetDataValues(self, record, data):
        data.Set('filter_Price', record.price)
        filterJumps = record.jumps
        if record.jumps == 0:
            filterJumps = -1
        data.Set('filter_Jumps', filterJumps)
        data.Set('filter_Quantity', int(record.volRemaining))

    def GetFilters2(self):
        self.filter_jumps_min = int(GetNumericValueFromSetting('minEdit_market_filter_jumps'))
        self.filter_jumps_max = int(GetNumericValueFromSetting('maxEdit_market_filter_jumps'))
        if self.filter_jumps_min == None or self.filter_jumps_min == '':
            self.filter_jumps_min = 0
        if self.filter_jumps_max == None or self.filter_jumps_max == '':
            self.filter_jumps_max = INFINITY
        if self.filter_jumps_min > self.filter_jumps_max:
            self.filter_jumps_max = INFINITY
        self.filter_quantity_min = int(GetNumericValueFromSetting('minEdit_market_filter_quantity'))
        self.filter_quantity_max = int(GetNumericValueFromSetting('maxEdit_market_filter_quantity'))
        if self.filter_quantity_min == None or self.filter_quantity_min == '':
            self.filter_quantity_min = 0
        if self.filter_quantity_max == None or self.filter_quantity_max == '':
            self.filter_quantity_max = INFINITY
        if self.filter_quantity_min >= self.filter_quantity_max:
            self.filter_quantity_max = INFINITY
        self.filter_price_min = float(GetNumericValueFromSetting('minEdit_market_filter_price'))
        self.filter_price_max = float(GetNumericValueFromSetting('maxEdit_market_filter_price'))
        if self.filter_price_min == None or self.filter_price_min == '':
            self.filter_price_min = 0
        if self.filter_price_max == None or self.filter_price_max == '':
            self.filter_price_max = INFINITY
        if self.filter_price_min >= self.filter_price_max:
            self.filter_price_max = INFINITY
        self.ignore_sellorder_min = GetNumericValueFromSetting('minEdit_market_filters_sellorderdev')
        if self.ignore_sellorder_min == None or self.ignore_sellorder_min == '':
            self.ignore_sellorder_min = 0
        self.ignore_sellorder_max = GetNumericValueFromSetting('maxEdit_market_filters_sellorderdev')
        if self.ignore_sellorder_max == None or self.ignore_sellorder_max == '':
            self.ignore_sellorder_max = 0
        self.ignore_buyorder_min = GetNumericValueFromSetting('minEdit_market_filters_buyorderdev')
        if self.ignore_buyorder_min == None or self.ignore_buyorder_min == '':
            self.ignore_buyorder_min = 0
        self.ignore_buyorder_max = GetNumericValueFromSetting('maxEdit_market_filters_buyorderdev')
        if self.ignore_buyorder_max == None or self.ignore_buyorder_max == '':
            self.ignore_buyorder_max = 0
        filters = [settings.user.ui.Get('market_filter_jumps', 0),
         settings.user.ui.Get('market_filter_quantity', 0),
         settings.user.ui.Get('market_filter_price', 0),
         not settings.user.ui.Get('market_filter_zerosec', 0),
         not settings.user.ui.Get('market_filter_highsec', 0),
         not settings.user.ui.Get('market_filter_lowsec', 0)]
        usingFilters = False
        for each in filters:
            if each:
                usingFilters = True
                break

        return [usingFilters,
         self.filter_jumps_min,
         self.filter_jumps_max,
         self.filter_quantity_min,
         self.filter_quantity_max,
         self.filter_price_min,
         self.filter_price_max,
         self.ignore_sellorder_min,
         self.ignore_sellorder_max,
         self.ignore_buyorder_min,
         self.ignore_buyorder_max]

    def ApplyDetailFilters(self, data, activeFilters = 1):
        if not activeFilters:
            return True
        if settings.user.ui.Get('market_filter_jumps', 0):
            if data.filter_Jumps:
                if self.filter_jumps_min > data.filter_Jumps or self.filter_jumps_max < data.filter_Jumps:
                    if not (self.filter_jumps_min == 0 and data.filter_Jumps == -1):
                        return False
        if settings.user.ui.Get('market_filter_quantity', 0):
            if data.filter_Quantity:
                if self.filter_quantity_min > data.filter_Quantity or self.filter_quantity_max < data.filter_Quantity:
                    return False
        if settings.user.ui.Get('market_filter_price', 0):
            if data.filter_Price:
                if self.filter_price_min > data.filter_Price or self.filter_price_max < data.filter_Price:
                    return False
        secClass = sm.GetService('securitySvc').get_modified_security_class(data.order.solarSystemID)
        if secClass == const.securityClassZeroSec:
            if not settings.user.ui.Get('market_filter_zerosec', 0):
                return False
        elif secClass == const.securityClassHighSec:
            if not settings.user.ui.Get('market_filter_highsec', 0):
                return False
        elif not settings.user.ui.Get('market_filter_lowsec', 0):
            return False
        if data.filter_Price:
            if settings.user.ui.Get('market_filters_sellorderdev', 0) and data.mode == 'buy':
                if self.avgBuyPrice:
                    percentage = (data.filter_Price - self.avgBuyPrice) / self.avgBuyPrice
                    if float(self.ignore_sellorder_max) < percentage * 100 or float(self.ignore_sellorder_min) > percentage * 100:
                        return False
            if settings.user.ui.Get('market_filters_buyorderdev', 0) and data.mode == 'sell':
                if self.avgSellPrice:
                    percentage = (data.filter_Price - self.avgSellPrice) / self.avgSellPrice
                    if float(self.ignore_buyorder_max) < percentage * 100 or float(self.ignore_buyorder_min) > percentage * 100:
                        return False
        return True

    def LoadType(self, invType):
        self.invType = invType
        self.ReloadType()

    def OnReload(self):
        self.ReloadType()

    def GetInvTypeID(self):
        return self.invType

    def ReloadType(self, *args):
        if self.invType:
            self.sr.sellscroll.Load(contentList=[], fixedEntryHeight=18, headers=self.sellheaders)
            self.sr.buyscroll.Load(contentList=[], fixedEntryHeight=18, headers=self.buyheaders)
            self.sr.sellscroll.ShowHint(localization.GetByLabel('UI/Market/Marketbase/FetchingOrders'))
            self.sr.buyscroll.ShowHint(localization.GetByLabel('UI/Market/Marketbase/FetchingOrders'))
            self.sr.buyItems, self.sr.sellItems = sm.GetService('marketQuote').GetOrders(self.invType)
            if settings.user.ui.Get('hilitemyorders', True):
                self.allMyOrderIDs = {order.orderID for order in sm.GetService('marketQuote').GetMyOrders()}
            else:
                self.allMyOrderIDs = set()
            self.Reload('buy')
            self.Reload('sell')
        else:
            self.sr.sellscroll.Load(contentList=[], fixedEntryHeight=18)
            self.sr.buyscroll.Load(contentList=[], fixedEntryHeight=18)


class QuickbarEntries(Container):
    __guid__ = 'xtriui.QuickbarEntries'
    __nonpersistvars__ = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sr.nodes = []
        self.tooDeep = False

    def __Load(self, contentList = [], maxDepth = 99, parentDepth = 0):
        if self.destroyed:
            return
        self.sr.nodes = []
        self.maxDepth = maxDepth
        self.parentDepth = parentDepth
        self.depth = 0
        self.AddEntries(0, contentList)
        if self.destroyed:
            return
        return [0, self.depth - parentDepth][bool(self.depth)]

    Load = LoadContent = __Load

    def AddEntry(self, idx, entry, update = 0, isSub = 0, fromW = None):
        _idx = idx
        if idx == -1:
            idx = len(self.GetNodes())
        entry.idx = idx
        if not self or not getattr(self, 'sr', None):
            return
        self.ReloadEntry(entry)
        return entry

    def ReloadEntry(self, entry):
        if entry.id and entry.GetSubContent:
            self.depth = max(self.depth, entry.sublevel)
            subcontent = entry.GetSubContent(entry)
            if self.destroyed:
                return
            self.AddEntries(entry.idx + 1, subcontent, entry)

    def AddEntries(self, fromIdx, entriesData, parentEntry = None):
        if self.parentDepth > self.maxDepth:
            self.tooDeep = True
            return
        if fromIdx == -1:
            fromIdx = len(self.GetNodes())
        isSub = 0
        if parentEntry:
            isSub = getattr(parentEntry, 'sublevel', 0) + 1
        entries = []
        idx = fromIdx
        for crap, data in entriesData:
            newentry = self.AddEntry(idx, data, isSub=isSub)
            if newentry is None:
                continue
            idx = newentry.idx + 1
            entries.append(newentry)

        if self.destroyed:
            return

    def _OnClose(self):
        for each in self.GetNodes():
            each.scroll = None
            each.data = None

        self.sr.nodes = []

    def GetNodes(self):
        return self.sr.nodes


class SelectFolderWindow(ListWindow):
    default_windowID = 'SelectFolderWindow'

    def GetError(self, checkNumber = 1):
        result = None
        if self.scroll.GetSelected():
            result = [self.scroll.GetSelected()[0].id[1], self.scroll.GetSelected()[0].sublevel]
        if hasattr(self, 'customValidator'):
            ret = self.customValidator and self.customValidator(result) or ''
            if ret:
                return ret
        try:
            if checkNumber:
                if result == None:
                    if self.minChoices == self.maxChoices:
                        label = localization.GetByLabel('UI/Control/ListWindow/MustSelectError', num=self.minChoices)
                    else:
                        label = localization.GetByLabel('UI/Control/ListWindow/SelectTooFewError', num=self.minChoices)
                    return label
        except ValueError as e:
            log.LogException()
            sys.exc_clear()
            return

        return ''

    def Confirm(self, *etc):
        if not self.isModal:
            return
        self.Error(self.GetError(checkNumber=0))
        if not self.GetError():
            if self.scroll.GetSelected():
                if hasattr(self.scroll.GetSelected()[0], 'id'):
                    self.result = [self.scroll.GetSelected()[0].id[1], self.scroll.GetSelected()[0].sublevel]
            self.SetModalResult(uiconst.ID_OK)

    def Error(self, error):
        ep = self.GetChild('errorParent')
        ep.Flush()
        if error:
            t = eveLabel.EveLabelMedium(text='<center>' + error, top=-3, parent=ep, width=self.minsize[0] - 32, state=uiconst.UI_DISABLED, color=(1.0, 0.0, 0.0, 1.0), align=uiconst.CENTER)
            ep.state = uiconst.UI_DISABLED
            ep.height = t.height + 8
        else:
            ep.state = uiconst.UI_HIDDEN


class MarketGroupItemImage(Image):
    isDragObject = True

    def ApplyAttributes(self, attributes):
        super(MarketGroupItemImage, self).ApplyAttributes(attributes)
        self.omegaService = sm.GetService('cloneGradeSvc')
        self.omegaIcon = OmegaCloneOverlayIcon(name='OmegaIcon', parent=self, state=uiconst.UI_DISABLED, align=uiconst.TOALL, opacity=0, origin=ORIGIN_MARKET)

    def LoadTypeIcon(self, typeID):
        Image.LoadTypeIcon(self)
        self.SetOmegaIconState(typeID)
        self.typeID = typeID
        self.omegaIcon.reason = typeID
        self.isUnlockedWithExpertSystem = sm.GetService('skills').IsUnlockedWithExpertSystem(self.typeID)

    def GetDragData(self, *args):
        return [Bunch(typeID=self.typeID, __guid__='listentry.GenericMarketItem', label=self.typeName, invtype=self.typeID)]

    def OnMouseMove(self, *args):
        if self.IsBeingDragged():
            self.cursor = self.default_cursor
        Container.OnMouseMove(self)

    def OnMouseEnter(self, *args):
        self.omegaIcon.OnMouseEnter()
        if eveCfg.IsPreviewable(self.typeID):
            self.cursor = uiconst.UICURSOR_MAGNIFIER
        else:
            self.cursor = self.default_cursor
        if evetypes.GetGroupID(self.typeID) == const.groupSkillInjectors:
            sm.ScatterEvent('OnSkillInjectorMouseEnter', self.typeID)

    def OnMouseExit(self, *args):
        self.omegaIcon.OnMouseExit()
        self.cursor = self.default_cursor
        if evetypes.GetGroupID(self.typeID) == const.groupSkillInjectors:
            sm.ScatterEvent('OnSkillInjectorMouseExit')

    def OnClick(self, *args):
        if eveCfg.IsPreviewable(self.typeID):
            sm.GetService('preview').PreviewType(self.typeID)

    def SetOmegaIconState(self, typeID):
        if self.omegaService.IsRestrictedForAlpha(typeID):
            self.omegaIcon.SetOpacity(1)
        else:
            self.omegaIcon.SetOpacity(0)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.omegaService.IsRestricted(self.typeID):
            self.omegaIcon.LoadTooltipPanel(tooltipPanel, args)
        else:
            tooltipPanel.LoadGeneric1ColumnTemplate()
        expertSystems.add_type_unlocked_by_expert_systems(tooltipPanel, self.typeID)
