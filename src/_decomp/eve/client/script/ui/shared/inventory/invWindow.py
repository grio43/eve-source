#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\inventory\invWindow.py
import logging
import weakref
from math import pi
import blue
import eveformat
import eveicon
import threadutils
import functools
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_WORLDMOD
from carbonui import AxisAlignment, Density, TextColor, uiconst
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.services.setting import UserSettingBool
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import IsUnder
from carbonui.window.settings import GetRegisteredState
from eve.client.script.environment.invControllers import AssetSafetyDeliveries as AssetSafetyDeliveriesController, AssetSafetyContainer as AssetSafetyContainerController, GetInvCtrlFromInvID, ItemWreck, ItemFloatingCargo, LOOT_GROUPS, LOOT_GROUPS_NOCLOSE, ShipCargo as ShipCargoController, StationCorpDeliveries as StationCorpDeliveriesController, StationItems as StationItemsController, StationShips as StationShipsController, StructureItemHangar as StructureItemsController, StructureShipHangar as StructureShipsController
from eve.client.script.parklife.states import flagWreckEmpty, mouseOver, selected
from eve.client.script.ui import eveColor
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from carbonui.control.window import Window
from eve.client.script.ui.control.historyBuffer import HistoryBuffer
from carbonui.button.menu import MenuButtonIcon
from eve.client.script.ui.inflight.bracketsAndTargets.bracketVarious import GetIconColor
from eve.client.script.ui.plex.textures import PLEX_WINDOW_ICON
from eve.client.script.ui.shared.container import InvContCapacityGauge, InvContQuickFilter
from eve.client.script.ui.shared.inventory.invCommon import CONTAINERGROUPS
from eve.client.script.ui.shared.inventory.invFilters import InvFilters
from eve.client.script.ui.shared.inventory.invSettings import always_open_secondary_inventory_setting, keep_inv_quick_filter_setting, always_show_full_tree_setting
from eve.client.script.ui.shared.inventory.treeData import TreeDataInv, TreeDataInvFolder, GetTreeDataClassByInvName
from eve.client.script.ui.shared.inventory.treeViewEntries import GetTreeViewEntryClassByDataType
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from eve.common.lib import appConst
from eve.common.lib import appConst as const
from eve.common.script.sys.eveCfg import GetActiveShip, InShipInSpace, InStructure
from eve.common.script.sys.idCheckers import IsStarbase
from eve.common.script.util.eveFormat import FmtISKAndRound, GetAveragePrice
import inventorycommon.const as invConst
from eveexceptions import UserError
from localization import GetByLabel
from signals import Signal
import telemetry
from uthread2 import StartTasklet
logger = logging.getLogger(__name__)
HISTORY_LENGTH = 50
TREE_DEFAULT_WIDTH = 160
SORT_OPTIONS = [('UI/Common/Name', 'UI/Inventory/NameReversed', 'name'),
 ('UI/Inventory/ItemQuantity', 'UI/Inventory/QuantityReversed', 'qty'),
 ('UI/Common/Type', 'UI/Inventory/TypeReversed', 'type'),
 ('UI/Inventory/EstPrice', 'UI/Inventory/EstPriceReversed', 'estPrice')]

class Inventory(Window):
    __guid__ = 'form.Inventory'
    __notifyevents__ = ['OnSessionChanged',
     'OnPrimaryViewChanged',
     'OnItemNameChange',
     'OnMultipleItemChange',
     'ProcessActiveShipChanged',
     'OnBeforeActiveShipChanged',
     'OnOfficeRentalChanged',
     'OnStateChange',
     'OnInvContDragEnter',
     'OnInvContDragExit',
     'DoBallsAdded',
     'DoBallRemove',
     'ProcessTempInvLocationAdded',
     'ProcessTempInvLocationRemoved',
     'OnSlimItemChange',
     'OnInvFiltersChanged',
     'OnInvContRefreshed',
     'OnCapacityChange',
     'OnWreckLootAll',
     'OnShowFullInvTreeChanged',
     'DoBallsRemove',
     'OnInvTreeUpdatingChanged']
    default_windowID = 'Inventory'
    default_width = 600
    default_height = 450
    default_minSize = (100, 140)
    default_iconNum = 'res:/UI/Texture/WindowIcons/items.png'
    default_isCompactable = True
    default_caption = None
    default_left = 80
    _filter_bottom_button = None
    _search_field = None
    _search_field_header_parent = None
    _search_field_top_parent = None
    _sort_by_button = None
    _top_action_container = None
    _view_mode_button = None

    def __init__(self, **kwargs):
        self.invController = None
        super(Inventory, self).__init__(**kwargs)

    @classmethod
    def Open(cls, invID = None, *args, **kwds):
        if invID:
            invController = GetInvCtrlFromInvID(invID)
            if invController and not invController.IsPrimed():
                if not invController.IsInRange():
                    raise UserError('FakeItemNotFound')
                try:
                    invController.GetItems()
                except RuntimeError:
                    raise UserError('FakeItemNotFound')

        return super(Inventory, cls).Open(invID=invID, *args, **kwds)

    def ApplyAttributes(self, attributes):
        self.currInvID = attributes.Get('invID', None)
        self.rootInvID = attributes.Get('rootInvID', self.currInvID)
        self.invController = GetInvCtrlFromInvID(self.currInvID)
        super(Inventory, self).ApplyAttributes(attributes)
        sm.GetService('inv').Register(self)
        self.treeEntryByID = {}
        self.tempTreeEntryByID = {}
        self.dragHoverThread = None
        self.refreshTreeThread = None
        self.updateSelectedItemsThread = None
        self.updateSelectedItemsPending = None
        self.invCont = None
        self.loadingTreeView = False
        self.loadingInvCont = False
        self.dragOpenNewWindowCookie = None
        self.treeData = None
        self.treeDataTemp = None
        self.containersInRangeUpdater = None
        self.history = HistoryBuffer(HISTORY_LENGTH)
        self.breadcrumbInvIDs = []
        self.needsUpdate = True
        self._is_tree_expanded = True
        self._is_tree_expanded_setting = TreeExpandedSetting(self)
        self.onDividerMoved = Signal(signalName='onDividerMoved')
        if session.stationid:
            StationItemsController().GetItems()
        self.dividerCont = DragResizeCont(name='dividerCont', settingsID='invTreeViewWidth_%s' % self.GetWindowSettingsID(), parent=self.sr.main, align=uiconst.TOLEFT, minSize=45, maxSize=None, defaultSize=TREE_DEFAULT_WIDTH, onResizeCallback=self.OnDividerContResize, onDragCallback=self.OnDividerContDragged, handle_cross_axis_alignment=AxisAlignment.START)
        StartTasklet(self.OnDividerContResize)
        self._search_field_header_parent = ContainerAutoSize(parent=self.header.extra_content, align=uiconst.TORIGHT)
        treeCont = None
        treeCont = Container(parent=self.dividerCont.mainCont, align=uiconst.TOALL)
        self._tree_underlay = PanelUnderlay(parent=self.dividerCont.mainCont, align=uiconst.TOALL, padding=self._get_tree_underlay_padding())
        self.on_content_padding_changed.connect(self._update_tree_padding)
        self.treeBottomCont = InvFilters(parent=treeCont, settingsID='invFiltersHeight_%s' % self.GetWindowSettingsID(), minSize=100, maxSize=0.5, defaultSize=150, windowID=self.GetWindowSettingsID(), show_filter_toggle_button=False)
        self.treeBottomCont.on_filters_updated.connect(self.UpdateFilters)
        self.treeBottomCont.on_expand_collapse_animation.connect(self.ChangeTreeWhenAnimating)
        self.tree = ScrollContainer(name='tree', parent=treeCont, innerPadding=self._get_tree_inner_padding(), padLeft=-8)
        self.tree.GetMenu = self.GetMenu
        self.tree.Paste = self.Paste
        self.rightCont = Container(name='rightCont', parent=self.sr.main, padding=(-8, 0, 0, 0))
        self.noInventoryLabel = eveLabel.EveCaptionMedium(name='noInventoryLabel', parent=self.rightCont, state=uiconst.UI_HIDDEN, text=GetByLabel('UI/Inventory/NoInventoryLocationSelected'), pos=(17, 78, 0, 0), opacity=0.5)
        self.topRightCont2 = Container(name='topRightCont2', parent=self.rightCont, align=uiconst.TOTOP, height=24, padBottom=16, clipChildren=True)
        self.bottomRightCont = Container(name='bottomRightcont', parent=self.rightCont, align=uiconst.TOBOTTOM, height=24, padding=self._get_bottom_right_cont_padding(), clipChildren=True)
        self.specialActionsCont = ContainerAutoSize(name='specialActionsCont', parent=self.bottomRightCont, align=uiconst.TORIGHT, padding=(16, 0, 0, 0))
        self._top_action_container = ContainerAutoSize(parent=self.topRightCont2, align=uiconst.TOLEFT, padding=self._get_top_action_container_padding())
        ButtonIcon(parent=ContainerAutoSize(parent=self._top_action_container, align=uiconst.TOLEFT), align=uiconst.CENTER, width=24, height=24, iconSize=16, texturePath=eveicon.stack, hint=GetByLabel('UI/Inventory/StackAll'), func=self._stack_all, name=pConst.UNIQUE_NAME_INVENTORY_STACK_ALL, uniqueUiName=pConst.UNIQUE_NAME_INVENTORY_STACK_ALL)
        self._view_mode_button = MenuButtonIcon(parent=ContainerAutoSize(parent=self._top_action_container, align=uiconst.TOLEFT), align=uiconst.CENTER, width=24, height=24, iconSize=16, texturePath=eveicon.grid_view, get_menu_func=self._get_view_mode_menu, hint=self._get_view_mode_button_hint(), uniqueUiName=pConst.UNIQUE_NAME_INVENTORY_VIEW)
        self._sort_by_button = MenuButtonIcon(parent=ContainerAutoSize(parent=self._top_action_container, align=uiconst.TOLEFT), align=uiconst.CENTER, width=24, height=24, iconSize=16, texturePath=eveicon.bars_sort_ascending, get_menu_func=self._get_sort_menu, hint=GetByLabel('UI/Common/SortBy'))
        self._update_sort_by_button_display()
        self._search_field_top_parent = ContainerAutoSize(parent=self.topRightCont2, align=uiconst.TORIGHT)
        self.quickFilter = self._search_field = InvContQuickFilter(parent=self._get_search_field_parent(), align=self._get_search_field_align(), width=120)
        self.capacityGauge = InvContCapacityGauge(parent=self.topRightCont2, align=uiconst.TOALL, padding=(0, 0, 8, 0))
        self.bottomRightLabelCont = Container(name='bottomRightLabelCont', parent=self.bottomRightCont, align=uiconst.TOALL, clipChildren=True)
        self.numItemsLabel = eveLabel.EveLabelMediumBold(name='numItemsLabel', parent=ContainerAutoSize(parent=self.bottomRightLabelCont, align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, color=TextColor.SECONDARY)
        self.totalPriceLabel = eveLabel.EveLabelMedium(name='totalPriceLabel', parent=ContainerAutoSize(parent=self.bottomRightLabelCont, align=uiconst.TOLEFT, left=8), align=uiconst.CENTERLEFT, color=TextColor.SECONDARY)
        expanded = False
        if self._is_tree_expanded_setting.is_default_determined:
            expanded = self._is_tree_expanded_setting.get()
        if expanded:
            self._ExpandTree(animate=False)
        else:
            self._CollapseTree(animate=False)
        self._is_tree_expanded_setting.on_change.connect(self._on_tree_expanded_setting_changed)
        self.treeBottomCont.ExpandOrCollapeFilters()
        if not self.currInvID:
            self.currInvID = settings.user.ui.Get('invLastOpenContainerData_%s' % self.GetWindowSettingsID(), None)
        self.ShowInvContLoadingWheel()
        StartTasklet(self.ConstructFilters)
        shouldUpdateCorpHangarNodes = self._IsCorpHangarNode(self.currInvID)
        if self._IsCurrentInventoryValid():
            if shouldUpdateCorpHangarNodes:
                self.currInvID = None
        else:
            self.currInvID = None
        StartTasklet(self.RefreshTree, corpHangarsChanged=shouldUpdateCorpHangarNodes)
        if self.compact:
            self.OnCompactModeEnabled()
        self.on_content_padding_changed.connect(self._on_content_padding_changed)
        self.on_compact_mode_changed.connect(self._on_compact_mode_changed)

    def _get_top_action_container_padding(self):
        if self.compact:
            return (0, 0, 0, 0)
        elif self._is_tree_expanded_setting.get():
            return (12, 0, 8, 0)
        else:
            return (-4, 0, 8, 0)

    def _update_top_action_container_padding(self, animate = True):
        if animate:
            for attr, value in zip(['padLeft',
             'padTop',
             'padRight',
             'padBottom'], self._get_top_action_container_padding()):
                animations.MorphScalar(self._top_action_container, attr, endVal=value, duration=0.3)

        else:
            self._top_action_container.padding = self._get_top_action_container_padding()

    def _get_top_action_container_display(self):
        return not self.compact and self.invCont and self.invCont.IsViewModesEnabled()

    def _update_top_action_container_display(self):
        self._top_action_container.display = self._get_top_action_container_display()

    def _get_view_mode_menu(self):
        menu = MenuData()
        for viewMode in self.invCont.availableViewModes:
            menu.AddEntry(text=self.invCont.GetViewModeName(viewMode), texturePath=self.invCont.GetViewModeIcon(viewMode), func=functools.partial(self.SetInvContViewMode, viewMode))

        return menu

    def _get_sort_menu(self):
        active_criteria, active_direction = self._get_container_sort_by()
        menu = MenuData()
        for i, (label_ascending, label_descending, criteria) in enumerate(SORT_OPTIONS):
            if i > 0:
                menu.AddSeparator()
            for direction, label in ((0, label_ascending), (1, label_descending)):

                def select_sort_order(_criteria = criteria, _direction = direction):
                    self._sort_container_by(_criteria, _direction)

                icon = eveicon.checkmark if active_criteria == criteria and active_direction == direction else None
                menu.AddEntry(text=GetByLabel(label), texturePath=icon, func=select_sort_order)

        return menu

    def _get_container_sort_by(self):
        if self._has_sort_by():
            return (self.invCont.sortIconsBy, self.invCont.sortIconsDir)
        else:
            return (None, None)

    def _sort_container_by(self, criteria, direction):
        if self._has_sort_by():
            self.invCont.SortIconsBy(criteria, direction)

    def _update_sort_by_button_display(self):
        self._sort_by_button.display = self._has_sort_by()

    def _has_sort_by(self):
        return bool(self.invCont and self.invCont.ShouldShowSortBy())

    def _get_view_mode_icon(self):
        if self.invCont:
            return self.invCont.GetActiveViewModeIcon() or eveicon.eye
        return eveicon.eye

    def _get_view_mode_button_hint(self):
        if self.invCont:
            view_mode_name = self.invCont.GetActiveViewModeName()
            return GetByLabel('UI/Inventory/ViewModeWithCurrent', current_view_mode=view_mode_name)

    def _update_view_mode_button(self):
        icon = self._get_view_mode_icon()
        self._view_mode_button.SetTexturePath(icon)
        self._view_mode_button.hint = self._get_view_mode_button_hint()

    def _stack_all(self):
        if self.invCont:
            self.invCont.StackAll()

    def _get_search_field_parent(self):
        if self.compact:
            return self._search_field_header_parent
        else:
            return self._search_field_top_parent

    def _get_search_field_align(self):
        return uiconst.CENTER

    def _update_search_field(self):
        parent = self._get_search_field_parent()
        align = self._get_search_field_align()
        if parent != self._search_field.parent:
            self._search_field.SetParent(None)
            self._search_field.align = align
            self._search_field.SetParent(parent)
        elif align != self._search_field.align:
            self._search_field.align = align

    def _create_filter_bottom_button(self):
        if self._filter_bottom_button is None:
            self._filter_bottom_button = ButtonIcon(parent=Container(parent=self.bottomRightCont, align=uiconst.TOLEFT, idx=0), align=uiconst.TOPLEFT, width=24, height=24, iconSize=16, texturePath=eveicon.filter, hint=GetByLabel('UI/Inventory/FilterChipClear'), func=self._clear_all_filters)

    def _update_filter_bottom_button(self):
        if self.destroyed:
            return
        if self._is_filtered():
            if self._filter_bottom_button is None:
                self._create_filter_bottom_button()
            animations.FadeIn(self._filter_bottom_button, duration=0.2)
            parent = self._filter_bottom_button.parent
            animations.MorphScalar(parent, 'width', startVal=parent.width, endVal=24, duration=0.2)
            animations.MorphScalar(parent, 'padRight', startVal=parent.padRight, endVal=4, duration=0.2)
        elif self._filter_bottom_button:
            animations.FadeOut(self._filter_bottom_button, duration=0.2)
            parent = self._filter_bottom_button.parent
            animations.MorphScalar(parent, 'width', startVal=parent.width, endVal=0, duration=0.2)
            animations.MorphScalar(parent, 'padRight', startVal=parent.padRight, endVal=0, duration=0.2)

    def _is_filtered(self):
        return self.invCont and (len(self.GetActiveFilters()) > 0 or self.quickFilter.GetQuickFilterInput())

    @threadutils.threaded
    def _on_tree_expanded_setting_changed(self, expanded):
        if expanded:
            self._ExpandTree()
        else:
            self._CollapseTree()

    def _get_tree_underlay_padding(self):
        pad_left, pad_top, _, pad_bottom = self.content_padding
        return (-pad_left,
         -pad_top,
         0,
         -pad_bottom)

    def _get_tree_inner_padding(self):
        _, content_pad_top, _, _ = self.content_padding
        pad_top = 0 if content_pad_top > 0 else 16
        return (0,
         pad_top,
         0,
         0)

    def _get_bottom_right_cont_padding(self):
        pad_top = self.content_padding[3]
        if self._is_tree_expanded:
            if self.compact:
                pad_left = 8
            else:
                pad_left = 16
        else:
            pad_left = 0
        return (pad_left,
         pad_top,
         0,
         0)

    def _on_content_padding_changed(self, window):
        self._update_bottom_right_cont_padding(animate=False)

    def _on_compact_mode_changed(self, window):
        self._update_bottom_right_cont_padding(animate=False)

    def _update_bottom_right_cont_padding(self, animate = True):
        if animate:
            for attr, value in zip(['padLeft',
             'padTop',
             'padRight',
             'padBottom'], self._get_bottom_right_cont_padding()):
                animations.MorphScalar(obj=self.bottomRightCont, attrName=attr, startVal=getattr(self.bottomRightCont, attr), endVal=value, duration=0.2)

        else:
            self.bottomRightCont.padding = self._get_bottom_right_cont_padding()

    def _update_tree_padding(self, window):
        if self._tree_underlay is not None and not self._tree_underlay.destroyed:
            self._tree_underlay.padding = self._get_tree_underlay_padding()
        if self.tree is not None and not self.tree.destroyed:
            self.tree.innerPadding = self._get_tree_inner_padding()

    def _IsCurrentInventoryValid(self):
        if not session.structureid and not session.stationid:
            return True
        if self.currInvID:
            currInvCtrl = GetInvCtrlFromInvID(self.currInvID)
            if currInvCtrl:
                try:
                    invItem = currInvCtrl.GetInventoryItem()
                    if invItem:
                        return sm.GetService('invCache').ValidateItemCanBeOpened(invItem)
                except (KeyError, RuntimeError, UserError):
                    return False

        return True

    def GetMenuMoreOptions(self):
        menuData = super(Inventory, self).GetMenuMoreOptions()
        menuData.AddCheckbox(text=GetByLabel('UI/Inventory/ShowSidebar'), setting=self._is_tree_expanded_setting)
        menuData.AddCheckbox(text=GetByLabel('UI/Inventory/AlwaysOpenSeparate'), setting=always_open_secondary_inventory_setting)
        menuData.AddCheckbox(text=GetByLabel('UI/Inventory/KeepQuickFilterValue'), setting=keep_inv_quick_filter_setting)
        menuData.AddCheckbox(text=GetByLabel('UI/Inventory/AlwaysShowFullTree'), setting=always_show_full_tree_setting)
        if self.compact and self.invCont and self.invCont.IsViewModesEnabled():
            menuData.AddSeparator()
            menuData.AddCaption(text=GetByLabel('UI/Inventory/ViewMode'))
            for viewMode in self.invCont.availableViewModes:
                menuData.AddRadioButton(text=self.invCont.GetViewModeName(viewMode), value=viewMode, setting=self.invCont.view_mode_setting)

        return menuData

    def OnSettingChangedSecondaryWnd(self, openSecondary, *args):
        settings.user.ui.Set('openSecondaryInv', openSecondary)

    def OnSettingChangedKeepQuickFilter(self, keepQuickFilterInput, *args):
        settings.user.ui.Set('keepInvQuickFilterInput', keepQuickFilterInput)

    def OnSettingChangedAlwaysShowFullTree(self, alwaysShowFullTree, *args):
        settings.user.ui.Set('alwaysShowFullInvTree', alwaysShowFullTree)
        sm.ScatterEvent('OnShowFullInvTreeChanged')

    def OnShowFullInvTreeChanged(self):
        self.RefreshTree()

    def GetRegisteredPositionAndSize(self):
        return self.GetRegisteredPositionAndSizeByClass(self.windowID)

    def RegisterPositionAndSize(self, key = None, windowID = None):
        windowID = self.windowID
        Window.RegisterPositionAndSize(self, key, windowID)

    def ShowTreeLoadingWheel(self):
        if self.loadingTreeView:
            return
        self.loadingTreeView = True
        StartTasklet(self._ShowTreeLoadingWheel)

    def _ShowTreeLoadingWheel(self):
        blue.synchro.SleepWallclock(500)
        wheelCont = Container(parent=self.dividerCont.mainCont)
        LoadingWheel(parent=wheelCont, align=uiconst.CENTER)
        while self.loadingTreeView:
            blue.synchro.Yield()

        wheelCont.Close()

    def HideTreeLoadingWheel(self):
        self.loadingTreeView = False

    def ShowInvContLoadingWheel(self):
        if self.loadingInvCont:
            return
        self.loadingInvCont = True
        StartTasklet(self._ShowInvContLoadingWheel)

    def _ShowInvContLoadingWheel(self):
        blue.synchro.SleepWallclock(500)
        wheel = LoadingWheel(parent=self.rightCont, align=uiconst.CENTER)
        while self.loadingInvCont:
            blue.synchro.Yield()

        wheel.Close()

    def HideInvContLoadingWheel(self):
        self.loadingInvCont = False

    def OnInvFiltersChanged(self):
        self.ConstructFilters()
        self.UpdateFilters()

    @telemetry.ZONE_METHOD
    def ConstructFilters(self):
        self.treeBottomCont.ConstructFilters()

    def RemoveTreeEntry(self, entry, byUser = False, checkRemoveParent = False):
        parent = entry.data.GetParent()
        if entry.childCont:
            for childEntry in entry.childCont.children[:]:
                self.RemoveTreeEntry(childEntry)

        invID = entry.data.GetID()
        sm.GetService('inv').RemoveTemporaryInvLocation(invID, byUser)
        if invID == self.rootInvID:
            self.Close()
            return
        if invID in self.treeEntryByID:
            self.treeEntryByID.pop(invID)
        if invID in self.tempTreeEntryByID:
            self.tempTreeEntryByID.pop(invID)
        if entry.data in self.treeData.GetChildren():
            self.treeData.RemoveChild(entry.data)
        if invID == self.currInvID:
            if not self.IsInvTreeExpanded():
                self.Close()
                return
            self.ShowInvContainer(self.GetDefaultInvID())
        entry.Close()
        if checkRemoveParent and isinstance(parent, TreeDataInvFolder) and not parent.GetChildren():
            parEntry = self.treeEntryByID.get(parent.GetID(), None)
            if parEntry:
                self.RemoveTreeEntry(parEntry, checkRemoveParent=True)

    def OnInvContScrollSelectionChanged(self, nodes):
        items = []
        for node in nodes:
            items.append(node.rec)

        self.UpdateSelectedItems(items)

    @telemetry.ZONE_METHOD
    def UpdateSelectedItems(self, items = None):
        if not session.IsItSafe():
            return
        if not self.invCont:
            return
        self.updateSelectedItemsPending = items or []
        if self.updateSelectedItemsThread:
            return
        self.updateSelectedItemsThread = StartTasklet(self._UpdateSelectedItems)

    @telemetry.ZONE_METHOD
    def _UpdateSelectedItems(self):
        try:
            while self.updateSelectedItemsPending is not None and not self.destroyed:
                if session.mutating:
                    break
                items = self.updateSelectedItemsPending
                if not items and self.invCont:
                    iskItems = self.invCont.items
                    self.UpdateIskPriceLabel(iskItems)
                else:
                    self.UpdateIskPriceLabel(items)
                self.capacityGauge.SetSecondaryVolume(items)
                self.capacityGauge.SetAdditionalVolume()
                self.UpdateNumberOfItems(items)
                self._update_filter_bottom_button()
                self.updateSelectedItemsPending = None
                blue.synchro.SleepWallclock(500)

        finally:
            self.updateSelectedItemsThread = None

    def SetInvContViewMode(self, value):
        if self.invCont:
            self.invCont.SetInvContViewMode(value)
        self.UpdateSelectedItems()

    @telemetry.ZONE_METHOD
    def UpdateNumberOfItems(self, items = None):
        items = items or []
        item_count_selected = len(items)
        item_count_filtered = self.invCont.numFilteredItems
        item_count_total = len(self.invCont.invController.GetItems())
        item_count_remaining = item_count_total - item_count_filtered
        if item_count_filtered > 0:
            filtered_text = GetByLabel('UI/Inventory/NumFiltered', numFiltered=item_count_filtered)
        else:
            filtered_text = ''
        if item_count_selected > 0:
            text = GetByLabel('UI/Inventory/NumItemsAndSelected2', numItems=item_count_remaining, numSelected=item_count_selected, numFilteredTxt=filtered_text)
        else:
            text = GetByLabel('UI/Inventory/NumItems2', numItems=item_count_remaining, numFilteredTxt=filtered_text)
        if item_count_filtered > 0:
            text = eveformat.color(text, eveColor.SUCCESS_GREEN)
        self.numItemsLabel.text = text

    def OnInvContDragEnter(self, invID, nodes):
        if not session.IsItSafe():
            return
        if invID != self.currInvID or self.invCont is None:
            return
        items = []
        for node in nodes:
            if getattr(node, 'item', None):
                if self.invController.IsItemHereVolume(node.item):
                    return
                items.append(node.item)

        self.capacityGauge.SetAdditionalVolume(items)

    def OnInvContDragExit(self, invID, nodes):
        if not session.IsItSafe():
            return
        self.capacityGauge.SetAdditionalVolume()

    @telemetry.ZONE_METHOD
    def UpdateIskPriceLabel(self, items):
        total = 0
        for item in items:
            if item is None:
                continue
            price = GetAveragePrice(item)
            if price:
                total += price * item.stacksize

        self.totalPriceLabel.text = GetByLabel('UI/Inventory/EstIskPrice2', iskString=FmtISKAndRound(total, False))

    def UpdateSpecialActionButtons(self):
        self.specialActionsCont.Flush()
        actions = self.invCont.invController.GetSpecialActions()
        for label, func, name, isDefaultBtn in actions:
            button = Button(parent=self.specialActionsCont, label=label, func=func, align=uiconst.CENTERLEFT, name=name, btn_default=isDefaultBtn, density=Density.COMPACT)
            self.invCont.RegisterSpecialActionButton(button)

        self.specialActionsCont.display = len(self.specialActionsCont.children) > 0

    def RegisterID(self, entry, invID):
        if id in self.treeEntryByID:
            raise ValueError('Duplicate inventory location ids: %s' % repr(invID))
        self.treeEntryByID[invID] = entry

    def UnregisterID(self, invID):
        if id in self.treeEntryByID:
            self.treeEntryByID.pop(invID)

    def OnTreeViewClick(self, entry, *args):
        if session.solarsystemid and hasattr(entry.data, 'GetItemID'):
            itemID = entry.data.GetItemID()
            isCurrStation = itemID in (session.stationid, session.structureid)
            bp = sm.GetService('michelle').GetBallpark()
            if bp and itemID in bp.slimItems and not isCurrStation:
                sm.GetService('stateSvc').SetState(itemID, selected, 1)
        if hasattr(entry.data, 'OpenNewWindow') and uicore.uilib.Key(uiconst.VK_SHIFT) and entry.canAccess:
            entry.data.OpenNewWindow()
        elif isinstance(entry.data, TreeDataInv) and entry.data.HasInvCont():
            self.ShowInvContainer(entry.data.GetID())
        elif entry.data.HasChildren():
            entry.ToggleChildren()

    def OnTreeViewDblClick(self, entry, *args):
        if isinstance(entry.data, TreeDataInv) and entry.data.HasInvCont():
            if always_open_secondary_inventory_setting.is_enabled() and entry.canAccess:
                entry.data.OpenNewWindow()
            else:
                entry.ToggleChildren()

    def OnTreeViewMouseEnter(self, entry, *args):
        if not session.solarsystemid:
            return
        if hasattr(entry.data, 'GetItemID'):
            sm.GetService('stateSvc').SetState(entry.data.GetItemID(), mouseOver, 1)

    def OnTreeViewMouseExit(self, entry, *args):
        if not session.solarsystemid:
            return
        if hasattr(entry.data, 'GetItemID'):
            sm.GetService('stateSvc').SetState(entry.data.GetItemID(), mouseOver, 0)

    def OnTreeViewDragEnter(self, entry, dragObj, nodes):
        self.dragHoverThread = StartTasklet(self._OnTreeViewDragEnter, entry, dragObj, nodes)

    def OnTreeViewDragExit(self, entry, dragObj, nodes):
        sm.ScatterEvent('OnInvContDragExit', dragObj, nodes)
        if self.dragHoverThread:
            self.dragHoverThread.kill()
            self.dragHoverThread = None

    def _OnTreeViewDragEnter(self, entry, dragObj, nodes):
        blue.synchro.SleepWallclock(1000)
        if uicore.uilib.mouseOver == entry and uicore.uilib.leftbtn:
            entry.ShowChildren()

    def OnTreeViewGetDragData(self, entry):
        self.dragOpenNewWindowCookie = uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVEDRAG, self.OnGlobalDragExit, entry)

    def OnGlobalDragExit(self, entry, *args):
        if not uicore.IsDragging():
            return False
        else:
            mo = uicore.uilib.mouseOver
            if IsUnder(mo, self) or mo == self:
                return True
            if entry.canAccess and hasattr(entry.data, 'OpenNewWindow'):
                entry.CancelDrag()
                invID = entry.data.GetID()
                windowID = '%s_%s' % (invID[0], entry.settingsID)
                windowInstanceID = '%s_%s' % (invID[1], entry.settingsID)
                wnd = uicore.registry.GetWindow(windowID, windowInstanceID)
                if wnd and wnd.InStack():
                    wnd.GetStack().RemoveWnd(wnd, (0, 5), dragging=True)
                elif wnd:
                    StartTasklet(wnd._OpenDraggingThread)
                else:
                    StartTasklet(entry.data.OpenNewWindow, True)
            return False

    @telemetry.ZONE_METHOD
    def ShowInvContainer(self, invID, branchHistory = True):
        if invID and not self.IsInvIDLegit(invID):
            invID = self.GetDefaultInvID(startFromInvID=invID)
            if invID not in self.treeEntryByID:
                invID = None
        if invID is None:
            if self.invCont:
                self.invCont.Close()
                self.invCont = None
            self.noInventoryLabel.Show()
            self.HideInvContLoadingWheel()
            self._ExpandTree(animate=False)
            return
        self.noInventoryLabel.Hide()
        if self.invCont is not None and invID == self.invCont.invController.GetInvID():
            return
        entry = self.treeEntryByID.get(invID, None)
        if entry is None:
            return
        try:
            entry.data.invController.GetItems()
        except UserError:
            self.HideInvContLoadingWheel()
            if not self.invCont:
                defaultInvID = self.GetDefaultInvID()
                if defaultInvID != invID:
                    self.ShowInvContainer(defaultInvID)
            raise

        if self.invCont:
            self.invCont.Close()
        self.ShowInvContLoadingWheel()
        if keep_inv_quick_filter_setting.is_enabled():
            quickFilterInput = self.quickFilter.GetQuickFilterInput()
        else:
            quickFilterInput = None
        self.invCont = entry.data.GetInvCont(parent=self.rightCont, activeFilters=self.GetActiveFilters(), name=self.GetWindowSettingsID(), quickFilterInput=quickFilterInput, padding=(0 if not self._is_tree_expanded else (8 if self.compact else 16),
         0,
         0,
         0))
        self.invController = self.invCont.invController
        self.HideInvContLoadingWheel()
        self.invCont.view_mode_setting.on_change.connect(self._on_inv_cont_view_mode_changed)
        self.rightCont.state = uiconst.UI_NORMAL
        if hasattr(self.invCont, 'scroll') and self.invCont.scroll:
            self.rightCont.OnMouseDown = self.invCont.scroll.OnMouseDown
            self.rightCont.OnMouseUp = self.invCont.scroll.OnMouseUp
            self.invCont.GetRubberbandParentContainer = lambda : self.rightCont
            self.invCont.scroll.OnSelectionChange = self.OnInvContScrollSelectionChanged
        self.UpdateIskPriceLabel(self.invCont.invController.GetItems())
        self.UpdateSpecialActionButtons()
        self._update_view_mode_button()
        self._update_sort_by_button_display()
        self._update_filter_bottom_button()
        self.UpdateQuickFilter()
        self.UpdateCapacityGauge()
        self.UpdateTopRightCont()
        self.UpdateBottomRightCont()
        if branchHistory:
            self.history.Append(invID)
        previousInvID = self.currInvID
        self.currInvID = invID
        self.RegisterLastOpenInvID(invID)
        self.UpdateSelectedState()
        self.UpdateNumberOfItems()
        self.UpdateUIForCompactMode()
        sm.ScatterEvent('OnInventoryContainerShown', invID, previousInvID)

    def _on_inv_cont_view_mode_changed(self, view_mode):
        self._update_view_mode_button()
        self._update_sort_by_button_display()

    def UpdateQuickFilter(self):
        if self.invCont.IsQuickFilterEnabled():
            self.quickFilter.SetInvCont(self.invCont)
        if self.invCont.IsQuickFilterEnabled():
            self.quickFilter.Show()
        else:
            self.quickFilter.Hide()

    def UpdateCapacityGauge(self):
        if self.invCont.IsCapacityEnabled():
            self.capacityGauge.SetInvCont(self.invCont)
            self.capacityGauge.Show()
        else:
            self.capacityGauge.Hide()

    def UpdateTopRightCont(self):
        if self.invCont.IsCapacityEnabled() or self.invCont.IsQuickFilterEnabled() or self.invCont.IsViewModesEnabled():
            self.topRightCont2.Show()
        else:
            self.topRightCont2.Hide()

    def UpdateBottomRightCont(self):
        self.bottomRightCont.display = self.invCont is not None and self.invCont.IsEstimatedValueEnabled()

    def GetMenu(self):
        m = []
        if session.role & (ROLE_GML | ROLE_WORLDMOD):
            m.append(('GM / WM Extras', ('isDynamic', self.GetGMMenu, ())))
        m.extend(Window.GetMenu(self))
        return m

    def GetGMMenu(self):
        return [('Clear client inventory cache', sm.GetService('invCache').InvalidateCache, ()), ('Toggle inventory priming debug mode (Red means primed)', self.ToggleInventoryPrimingDebug, ())]

    def ToggleInventoryPrimingDebug(self):
        isOn = settings.user.ui.Get('invPrimingDebugMode', False)
        settings.user.ui.Set('invPrimingDebugMode', not isOn)

    def OnBack(self):
        invID = self.history.GoBack()
        if invID:
            if invID in self.treeEntryByID:
                self.ShowInvContainer(invID, branchHistory=False)
            else:
                self.history.GoForward()

    def OnForward(self):
        invID = self.history.GoForward()
        if invID:
            if invID in self.treeEntryByID:
                self.ShowInvContainer(invID, branchHistory=False)
            else:
                self.history.GoBack()

    def Close(self, setClosed = False, *args, **kwds):
        super(Inventory, self).Close(setClosed, *args, **kwds)
        sm.ScatterEvent('OnInventoryClosed', self.currInvID)

    def OnResize_(self, *args):
        if self.InStack():
            width = self.GetStack().width
        else:
            width = self.width
        self.dividerCont.SetMaxSize(width - 10)
        self.treeBottomCont.UpdateSize()

    def OnDividerContResize(self):
        minWidth, minHeight = self.default_minSize
        minWidth = max(self.dividerCont.width + 10, minWidth)
        minSize = (minWidth, minHeight)
        self.SetMinSize(minSize)

    def OnDividerContDragged(self):
        self.onDividerMoved()

    def RegisterLastOpenInvID(self, invID):
        settings.user.ui.Set('invLastOpenContainerData_%s' % self.GetWindowSettingsID(), invID)

    def DeselectAllFilters(self):
        self.treeBottomCont.DeselectAllFilters()

    def UpdateFilters(self):
        if self.invCont:
            self.SetActiveFilters(self.GetActiveFilters())

    def SetActiveFilters(self, filters):
        self.invCont.SetFilters(filters)
        self.treeBottomCont.SetActiveFilters(filters)
        self._update_filter_bottom_button()

    def OnInvContRefreshed(self, invCont):
        if self.invCont == invCont:
            self.UpdateSelectedItems()

    def GetActiveFilters(self):
        return self.treeBottomCont.GetActiveFilters()

    def ChangeTreeWhenAnimating(self, animationStart):
        if animationStart:
            self.tree.DisableScrollbars()
        else:
            self.tree.EnableScrollbars()

    def OnBreadcrumbLinkClicked(self, linkNum):
        invID = self.breadcrumbInvIDs[linkNum]
        if self.IsInvIDLegit(invID):
            self.ShowInvContainer(invID)

    def GetNeocomGroupIcon(self):
        return 'res:/UI/Texture/WindowIcons/folder_cargo.png'

    def GetNeocomGroupLabel(self):
        return GetByLabel('UI/Neocom/InventoryBtn')

    def GetDefaultWndIcon(self):
        if self.invController:
            return self.invController.GetIconName()
        return self.default_iconNum

    def GetWindowSettingsID(self):
        return self.windowID

    @staticmethod
    def GetWindowIDFromInvID(invID = None):
        invCtrlName = invID[0]
        if invID == (invConst.INVENTORY_ID_SHIP_CARGO, GetActiveShip()):
            return 'ActiveShipCargo'
        return invCtrlName

    @staticmethod
    def GetWindowIDPrimary():
        if session.stationid:
            return invConst.INVENTORY_ID_STATION
        elif session.structureid:
            return invConst.INVENTORY_ID_STRUCTURE
        else:
            return invConst.INVENTORY_ID_SPACE

    @staticmethod
    def OpenOrShow(invID = None, usePrimary = True, toggle = False, openFromWnd = None, windowID = None, windowInstanceID = None, **kw):
        if uicore.uilib.Key(uiconst.VK_SHIFT) or always_open_secondary_inventory_setting.is_enabled():
            usePrimary = False
            openFromWnd = None
        if not Inventory.IsPrimaryInvTreeExpanded():
            usePrimary = False
        if openFromWnd:
            if not isinstance(openFromWnd, Inventory):
                openFromWnd = None
            else:
                usePrimary = False
        if usePrimary or not invID:
            cls = InventoryPrimary
            if not windowID:
                windowID = Inventory.GetWindowIDPrimary()
            rootInvID = None
        else:
            if invID == (invConst.INVENTORY_ID_SHIP_CARGO, GetActiveShip()):
                cls = ActiveShipCargo
            else:
                import form
                cls = getattr(form, invID[0], Inventory)
            if not windowID:
                windowID = Inventory.GetWindowIDFromInvID(invID)
            if not windowInstanceID:
                windowInstanceID = invID[1]
            rootInvID = invID
        if toggle:
            wnd = cls.ToggleOpenClose(windowID=windowID, windowInstanceID=windowInstanceID, invID=invID, rootInvID=rootInvID, **kw)
        else:
            if openFromWnd:
                wnd = openFromWnd
            else:
                wnd = cls.GetIfOpen(windowID=windowID, windowInstanceID=windowInstanceID)
            if wnd:
                wnd.Maximize()
                if wnd.currInvID != invID:
                    if invID not in wnd.treeEntryByID:
                        wnd.RefreshTree(invID)
                    else:
                        wnd.ShowInvContainer(invID)
            else:
                wnd = cls.Open(windowID=windowID, windowInstanceID=windowInstanceID, invID=invID, rootInvID=rootInvID, **kw)
        if wnd:
            wnd.ScrollToActiveEntry()
        return wnd

    def ScrollToActiveEntry(self):
        StartTasklet(self._ScrollToActiveEntry)

    def _ScrollToActiveEntry(self):
        blue.synchro.Yield()
        _, h = self.tree.GetAbsoluteSize()
        if h <= 0:
            return
        entry = self.treeEntryByID.get(self.currInvID, None)
        if not entry:
            return
        _, topEntry = entry.GetAbsolutePosition()
        _, topScroll, _, height = self.tree.mainCont.GetAbsolute()
        denum = height - entry.topRightCont.height
        if denum:
            fraction = float(topEntry - topScroll) / denum
            self.tree.ScrollToVertical(fraction)

    def OnDropData(self, dragObj, nodes):
        if self.invCont:
            return self.invCont.OnDropData(dragObj, nodes)

    def OnTreeViewDropData(self, entry, obj, nodes):
        if self.dragHoverThread:
            self.dragHoverThread.kill()
            self.dragHoverThread = None
        if self.dragOpenNewWindowCookie:
            uicore.uilib.UnregisterForTriuiEvents(self.dragOpenNewWindowCookie)
            self.dragOpenNewWindowCookie = None
        if isinstance(entry.data, TreeDataInv):
            sm.ScatterEvent('OnInvContDragExit', obj, nodes)
            StartTasklet(self._MoveItems, entry, nodes)

    def _MoveItems(self, entry, nodes):
        if not nodes:
            return
        if isinstance(nodes[0], TreeDataInv):
            item = nodes[0].invController.GetInventoryItem()
        else:
            item = getattr(nodes[0], 'item', None)
        if item and entry.data.invController.IsItemHere(item):
            return
        if isinstance(nodes[0], TreeDataInv) and not nodes[0].invController.IsMovable():
            return
        if entry.data.invController.OnDropData(nodes):
            entry.Blink()

    def GetTreeEntryByItemID(self, itemID):
        ret = []
        for _, entry in self.treeEntryByID.iteritems():
            if hasattr(entry.data, 'GetItemID') and entry.data.GetItemID() == itemID:
                ret.append(entry)

        return ret

    def GetTreeEntryByID(self, dataID):
        ret = []
        for _, entry in self.treeEntryByID.iteritems():
            if hasattr(entry.data, 'GetID') and entry.data.GetID() == dataID:
                ret.append(entry)

        return ret

    def ProcessTempInvLocationAdded(self, invID):
        if invID in self.treeEntryByID:
            return
        if self.rootInvID in sm.GetService('inv').GetTemporaryInvLocations():
            return
        invName, itemID = invID
        cls = GetTreeDataClassByInvName(invName)
        data = cls(invName, parent=self.treeDataTemp, itemID=itemID, isRemovable=True)
        entry = self.CreateTreeViewEntry(data)
        self.UpdateCelestialEntryStatus(entry)

    def ProcessTempInvLocationRemoved(self, invID, byUser):
        if invID == self.currInvID and not byUser:
            self.Close()
        else:
            entry = self.treeEntryByID.get(invID, None)
            if entry:
                if self.treeDataTemp:
                    self.treeDataTemp.RemoveChild(entry.data)
                if entry.data.IsRemovable():
                    self.RemoveTreeEntry(entry)

    def OnSessionChanged(self, isRemote, sess, change):
        if change.keys() == ['shipid']:
            return
        shouldUpdateCorpHangarNodes = False
        if not self._IsCurrentInventoryValid():
            shouldUpdateCorpHangarNodes = self._IsCorpHangarNode(self.currInvID)
            self.currInvID = None
        elif 'corprole' in change or 'corpid' in change:
            shouldUpdateCorpHangarNodes = self._IsCorpHangarNode(self.currInvID)
            if shouldUpdateCorpHangarNodes:
                self.currInvID = None
        self.RefreshTree(corpHangarsChanged=shouldUpdateCorpHangarNodes)

    def _IsCorpHangarNode(self, invID):
        if not invID or not (session.stationid or session.structureid):
            return False
        if not self.treeData:
            return False
        invData = self.treeData.GetChildByID(invID)
        if not invData:
            return False
        office = sm.GetService('officeManager').GetCorpOfficeAtLocation()
        if not office:
            return False
        invAncestorsData = invData.GetAncestors()
        invAncestorsData.append(invData)
        invAncestorsIDs = [ invData.GetID() for invData in invAncestorsData ]
        invClass = 'StationCorpHangars' if session.stationid else 'StructureCorpHangar'
        corpHangarItemID = office.officeID
        corpHangarInvID = (invClass, corpHangarItemID)
        return corpHangarInvID in invAncestorsIDs

    def OnPrimaryViewChanged(self, *args):
        self.RefreshTree()

    def _IsInventoryItem(self, item):
        if item.groupID in CONTAINERGROUPS:
            return True
        if item.categoryID == const.categoryShip:
            return True
        if item.typeID == const.typeAssetSafetyWrap:
            return True
        return False

    @telemetry.ZONE_METHOD
    def OnMultipleItemChange(self, items, change):
        self.UpdateSelectedItems()

    @telemetry.ZONE_METHOD
    def OnInvChangeAny(self, item = None, change = None):
        if not self._IsInventoryItem(item):
            return
        if item.itemID == GetActiveShip():
            return
        if item.categoryID == const.categoryShip and not session.stationid and not session.structureid:
            return
        if const.ixSingleton in change:
            self.RefreshTree()
            return
        if not item.singleton:
            return
        if const.ixLocationID in change or const.ixFlag in change:
            if session.stationid and item.categoryID == const.categoryShip:
                if session.charid in (item.ownerID, change.get(const.ixOwnerID, None)):
                    self.RefreshTree()
            elif session.solarsystemid and item.groupID in CONTAINERGROUPS and not InStructure():
                ownerIDs = (item.ownerID, change.get(const.ixOwnerID, None))
                if ownerIDs[0] == ownerIDs[1] == session.corpid:
                    return
                if session.corpid in ownerIDs and session.charid not in ownerIDs:
                    return
                self.RefreshTree()
            else:
                shouldUpdateCorpHangarNodes = False
                if not self._IsCurrentInventoryValid():
                    shouldUpdateCorpHangarNodes = self._IsCorpHangarNode(self.currInvID)
                    self.currInvID = None
                self.RefreshTree(corpHangarsChanged=shouldUpdateCorpHangarNodes)
        if const.ixOwnerID in change and item.typeID == const.typePlasticWrap:
            self.RefreshTree()

    def GetSlimItem(self):
        itemID = self.invController.itemID
        bp = sm.GetService('michelle').GetBallpark()
        if bp:
            return bp.slimItems.get(itemID, None)

    @telemetry.ZONE_METHOD
    def RemoveItem(self, item):
        if session.solarsystemid and not self.invController.GetItems():
            slimItem = self.GetSlimItem()
            if slimItem is not None and slimItem.groupID in LOOT_GROUPS:
                self.RemoveWreckEntryOrClose()

    def OnWreckLootAll(self, invID, items):
        if invID == self.currInvID:
            self.RemoveWreckEntryOrClose()
        treeEntry = self.treeEntryByID.get((invConst.INVENTORY_ID_SHIP_CARGO, GetActiveShip()))
        if treeEntry and items:
            treeEntry.Blink()

    def RemoveWreckEntryOrClose(self):
        if self.IsInvTreeExpanded():
            entry = self.treeEntryByID.get(self.currInvID, None)
            if entry:
                self.SwitchToOtherLootable(entry)
                if entry.data.IsRemovable():
                    self.RemoveTreeEntry(entry, byUser=True)
        else:
            slimItem = self.GetSlimItem()
            if slimItem is not None and slimItem.groupID not in LOOT_GROUPS_NOCLOSE:
                self.CloseByUser()

    def SwitchToOtherLootable(self, oldEntry):
        lootableData = [ data for data in self.treeDataTemp.GetChildren() if data.GetID()[0] in ('ItemWreck', 'ItemFloatingCargo') ]
        if oldEntry.data not in lootableData:
            return
        idx = lootableData.index(oldEntry.data)
        lootableData.remove(oldEntry.data)
        if lootableData:
            newIdx = min(len(lootableData) - 1, idx)
            invID = lootableData[newIdx].GetID()
            self.ShowInvContainer(invID)

    def OnStateChange(self, itemID, flag, isSet, *args):
        if flag == flagWreckEmpty:
            entries = self.GetTreeEntryByItemID(itemID)
            for entry in entries:
                self.RemoveTreeEntry(entry)

    def OnSlimItemChange(self, oldSlim, newSlim):
        if IsStarbase(newSlim.categoryID):
            if oldSlim.posState != newSlim.posState:
                self.RefreshTree()

    def OnCapacityChange(self, itemID):
        if self.invController and itemID == self.invController.itemID:
            self.UpdateSelectedItems()
            self.capacityGauge.RefreshCapacity()

    def DoBallsAdded(self, data):
        for _, slimItem in data:
            if slimItem.categoryID == const.categoryStarbase:
                self.RefreshTree()
                return

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        StartTasklet(self._DoBallRemove, ball, slimItem, terminal)

    def _DoBallRemove(self, ball, slimItem, terminal):
        if self and self.destroyed:
            return
        invID = (invConst.INVENTORY_ID_SHIP_CARGO, GetActiveShip())
        if slimItem.itemID in (session.structureid, session.stationid):
            return
        for entry in self.GetTreeEntryByItemID(slimItem.itemID):
            if entry.data.GetID() == invID:
                continue
            if entry.data.IsDescendantOf(invID):
                continue
            self.RemoveTreeEntry(entry, checkRemoveParent=True)

    def OnItemNameChange(self, *args):
        self.RefreshTree()

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        self.RefreshTree()

    def OnCompactModeEnabled(self):
        super(Inventory, self).OnCompactModeEnabled()
        self.UpdateUIForCompactMode()
        self.UpdateBottomRightCont()

    def OnCompactModeDisabled(self):
        super(Inventory, self).OnCompactModeDisabled()
        self.UpdateUIForCompactMode()
        self.UpdateBottomRightCont()

    def UpdateUIForCompactMode(self):
        if self.invController is None:
            return
        self.invController.SetCompactMode(self.IsCompact())
        self._update_search_field()
        self._update_top_action_container_padding(animate=False)
        self._update_top_action_container_display()
        if self.IsCompact():
            show_capacity = self.invCont and self.invCont.IsCapacityEnabled()
            if show_capacity:
                self.topRightCont2.Show()
                self.capacityGauge.padding = 0
                self.capacityGauge.HideLabel()
                self.topRightCont2.height = 5
            else:
                self.topRightCont2.Hide()
            self.capacityGauge.state = uiconst.UI_NORMAL
            self.rightCont.padLeft = -8 if self._is_tree_expanded else 0
            if self.invCont:
                self.invCont.padLeft = 8 if self._is_tree_expanded else 0
            self.topRightCont2.padLeft = 8 if self._is_tree_expanded else 0
            self.topRightCont2.padBottom = 8
        else:
            if self.invCont and self.invCont.IsCapacityEnabled():
                self.topRightCont2.Show()
                self.capacityGauge.padding = (0, 0, 8, 0)
                self.capacityGauge.ShowLabel()
                self.topRightCont2.height = 24
            if self.invCont:
                self.invCont.padLeft = 16 if self._is_tree_expanded else 0
            self.capacityGauge.state = uiconst.UI_PICKCHILDREN
            self.rightCont.padLeft = -8 if self._is_tree_expanded else 0
            self.topRightCont2.padLeft = 0
            self.topRightCont2.padBottom = 16

    def CollapseFilters(self, animate = True):
        self.filterCont.Disable()
        self.expandFiltersBtn.Disable()
        self.expandFiltersBtn.SetRotation(pi)
        self.treeBottomCont.DisableDragResize()
        height = self.filterHeaderCont.height + 6
        self.treeBottomCont.minSize = self.treeBottomCont.maxSize = height
        self.filterCont.DisableScrollbars()
        if animate:
            self.tree.DisableScrollbars()
            animations.MorphScalar(self.treeBottomCont, 'height', self.treeBottomCont.height, height, duration=0.3)
            animations.FadeOut(self.filterCont, duration=0.3, sleep=True)
            self.tree.EnableScrollbars()
        self.treeBottomCont.height = height
        self.filterCont.opacity = 0.0
        self.expandFiltersBtn.Enable()
        settings.user.ui.Set('invFiltersExpanded_%s' % self.GetWindowSettingsID(), False)

    def CollapseFilters(self, animate = True):
        self.filterCont.Disable()
        self.expandFiltersBtn.Disable()
        self.expandFiltersBtn.SetRotation(pi)
        self.treeBottomCont.DisableDragResize()
        height = self.filterHeaderCont.height + 16
        self.treeBottomCont.minSize = self.treeBottomCont.maxSize = height
        self.filterCont.DisableScrollbars()
        if animate:
            self.tree.DisableScrollbars()
            animations.MorphScalar(self.treeBottomCont, 'height', self.treeBottomCont.height, height, duration=0.3)
            animations.FadeOut(self.filterCont, duration=0.3, sleep=True)
            self.tree.EnableScrollbars()
        self.treeBottomCont.height = height
        self.filterCont.opacity = 0.0
        self.expandFiltersBtn.Enable()
        settings.user.ui.Set('invFiltersExpanded_%s' % self.GetWindowSettingsID(), False)

    def Paste(self, value):
        if self.invCont:
            self.invCont.Paste(value)

    def OnOfficeRentalChanged(self, corporationID, officeID):
        if corporationID == session.corpid:
            self.RefreshTree()

    @telemetry.ZONE_METHOD
    def RefreshTree(self, invID = None, corpHangarsChanged = False):
        if invID:
            self.currInvID = invID
        while not session.IsItSafe():
            blue.pyos.synchro.SleepSim(250)

        if not sm.GetService('inv').IsTreeUpdatingEnabled() or self.refreshTreeThread and self.refreshTreeThread.tasklet.alive:
            self.needsUpdate = True
            return
        if self.refreshTreeThread:
            self.refreshTreeThread.kill()
        self.refreshTreeThread = StartTasklet(self._RefreshTree, corpHangarsChanged)

    @telemetry.ZONE_METHOD
    def _RefreshTree(self, corpHangarsChanged = False):
        needsUpdate = True
        while needsUpdate:
            if self.destroyed:
                return
            self.needsUpdate = False
            if self.invCont:
                self.invCont.Disable()
            self.tree.Disable()
            try:
                self.ConstructTree(corpHangarsChanged)
            finally:
                self.tree.Enable()
                if self.invCont:
                    self.invCont.Enable()

            self.UpdateRangeUpdater()
            needsUpdate = self.needsUpdate

    def IsInvIDLegit(self, invID):
        data = self.treeData.GetDescendants().get(invID, None)
        if data is None:
            data = self.treeDataTemp.GetDescendants().get(invID, None)
        if invID == self.treeData.GetID():
            data = self.treeData
        return data is not None and isinstance(data, TreeDataInv) and data.HasInvCont()

    def GetDefaultInvID(self, startFromInvID = None):
        treeData = None
        if startFromInvID:
            treeData = self.treeData.GetChildByID(startFromInvID) or self.treeData
        else:
            treeData = self.treeData
        invID = self._GetDefaultInvID([treeData])
        if startFromInvID and invID is None:
            return self.GetDefaultInvID()
        else:
            return invID

    def _IsValidDefaultInvID(self, data):
        if isinstance(data, TreeDataInv) and data.HasInvCont():
            if not data.IsValidDefaultSelection():
                return False
            invController = GetInvCtrlFromInvID(data.GetID())
            if invController.IsInRange():
                return True
        return False

    def _GetDefaultInvID(self, dataNodes):
        settingsInvID = settings.user.ui.Get('invLastOpenContainerData_%s' % self.GetWindowSettingsID(), None)
        if settingsInvID:
            for data in dataNodes:
                if data.GetID() == settingsInvID and self._IsValidDefaultInvID(data):
                    return data.GetID()

        for data in dataNodes:
            if self._IsValidDefaultInvID(data):
                return data.GetID()
            if data.HasChildren():
                ret = self._GetDefaultInvID(data.GetChildren())
                if ret:
                    return ret

    def ConstructTree(self, corpHangarsChanged = False):
        self.treeEntryByID = {}
        self.tree.Flush()
        self.ShowTreeLoadingWheel()
        try:
            self.treeData = sm.GetService('inv').GetInvLocationTreeData(self.rootInvID)
        except RuntimeError as e:
            if e.args[0] == 'CharacterNotAtStation':
                return
            raise

        self.treeDataTemp = sm.GetService('inv').GetInvLocationTreeDataTemp(self.rootInvID)
        if not self.caption and self.rootInvID:
            data = self.GetTreeDataByInvID(self.rootInvID)
            if data:
                self.SetCaption(data.GetLabel())
        if self.currInvID is None or not self.IsInvIDLegit(self.currInvID):
            self.currInvID = self.GetDefaultInvID(self.currInvID)
            if self.currInvID:
                GetInvCtrlFromInvID(self.currInvID).GetItems()
                self.treeData = sm.GetService('inv').GetInvLocationTreeData(self.rootInvID)
        if self.rootInvID and not always_show_full_tree_setting.is_enabled():
            tempData = self.treeDataTemp.GetChildByID(self.rootInvID)
            rootNodes = []
            if tempData:
                self.treeData = tempData
                rootNodes.append(self.treeData)
            else:
                childData = self.treeData.GetChildByID(self.rootInvID)
                if childData:
                    self.treeData = childData
                rootNodes.append(self.treeData)
                rootNodes.extend(self.treeDataTemp.GetChildren())
        else:
            rootNodes = self.treeData.GetChildren()
            rootNodes.extend(self.treeDataTemp.GetChildren())
        expanded = self._is_tree_expanded_setting.get()
        if expanded:
            self._ExpandTree(animate=False)
        self.tree.opacity = 0.0
        for data in rootNodes:
            self.CreateTreeViewEntry(data)

        self.HideTreeLoadingWheel()
        animations.FadeIn(self.tree, duration=0.2)
        if self.currInvID:
            self.UpdateSelectedState()
            self.ScrollToActiveEntry()
        if self.rootInvID is not None and self.rootInvID not in self.treeEntryByID:
            self.Close()
        else:
            self.ShowInvContainer(self.currInvID)
            if corpHangarsChanged:
                if self.rootInvID:
                    self._CloseCorpHangars()
                else:
                    self._CollapseCorpHangars()

    def CreateTreeViewEntry(self, data):
        treeEntryClass = GetTreeViewEntryClassByDataType(data)
        treeEntry = treeEntryClass(name=getattr(data, 'clsName', ''), parent=self.tree, level=0, eventListener=self, data=data, settingsID=self.GetWindowSettingsID(), onDividerMoved=self.onDividerMoved)
        return treeEntry

    def _CloseCorpHangars(self):
        if self._IsCorpHangarNode(self.rootInvID):
            self.Close()

    def _CollapseCorpHangars(self):
        corpHangarsNodeID = None
        if session.structureid or session.stationid:
            office = sm.GetService('officeManager').GetCorpOfficeAtLocation()
            if office:
                corpHangarsNodeID = ('StationCorpHangars', office.officeID)
        if not corpHangarsNodeID:
            return
        entries = self.GetTreeEntryByID(corpHangarsNodeID)
        for entry in entries:
            entry.HideChildren()

    def UpdateSelectedState(self):
        selectedIDs = self.treeData.GetPathToDescendant(self.currInvID) or self.treeDataTemp.GetPathToDescendant(self.currInvID) or []
        selectedIDs = [ node.GetID() for node in selectedIDs ]
        if selectedIDs:
            for entry in self.treeEntryByID.values():
                entry.UpdateSelectedState(selectedIDs=selectedIDs)

    def UpdateRangeUpdater(self):
        if InShipInSpace() and not self.containersInRangeUpdater:
            self.containersInRangeUpdater = StartTasklet(self.UpdateTreeViewEntriesInRange)
        elif (session.structureid or session.stationid) and self.containersInRangeUpdater:
            self.containersInRangeUpdater.kill()
            self.containersInRangeUpdater = None

    def UpdateTreeViewEntriesInRange(self):
        while not self.destroyed:
            if session.solarsystemid is None:
                self.containersInRangeUpdater = None
                return
            self._UpdateTreeViewEntriesInRange()

    def _UpdateTreeViewEntriesInRange(self):
        for entry in self.treeEntryByID.values():
            if not entry.display or entry.IsCompletelyClipped(self.tree):
                continue
            self.UpdateCelestialEntryStatus(entry)
            blue.pyos.BeNice()

        blue.synchro.Sleep(500)

    def UpdateCelestialEntryStatus(self, entry):
        if hasattr(entry.data, 'GetLabelWithDistance'):
            entry.label.text = entry.data.GetLabelWithDistance()
        invController = getattr(entry.data, 'invController', None)
        if invController is None:
            canAccess = True
        else:
            canAccess = invController.IsInRange()
            if isinstance(entry.data.invController, (ItemWreck, ItemFloatingCargo)):
                data = entry.data
                entry.icon.LoadIcon(data.GetIcon(), ignoreSize=True)
                slimItem = sm.GetService('michelle').GetBallpark().slimItems[data.invController.itemID]
                entry.iconColor = GetIconColor(slimItem)
        entry.SetAccessability(canAccess)

    def OnExpandTreeBtn(self, *args):
        if self.dividerCont.pickState:
            self.CollapseTree()
        else:
            self.ExpandTree()
        self.OnDividerContResize()

    def GetTreeDataByInvID(self, invID):
        for root in (self.treeData, self.treeDataTemp):
            data = root.GetChildByID(invID)
            if data:
                return data

    def SetInvTreeExpandedSetting(self, isExpanded):
        self._is_tree_expanded_setting.set(isExpanded)

    def IsInvTreeExpanded(self, getDefault = True):
        return self._is_tree_expanded_setting.get()

    @staticmethod
    def IsPrimaryInvTreeExpanded():
        windowID = Inventory.GetWindowIDPrimary()
        return bool(settings.user.ui.Get('invTreeExpanded_%s' % windowID, True))

    @staticmethod
    def IsPrimaryInvCompacted():
        windowID = Inventory.GetWindowIDPrimary()
        return GetRegisteredState(windowID, 'compact')

    def GetDefaultInvTreeExpanded(self):
        if not self.rootInvID:
            return True
        if not self.treeData:
            return None
        data = self.treeData.GetChildByID(self.rootInvID)
        if data:
            return data.HasChildren()

    def ExpandTree(self, animate = True):
        self._ExpandTree(animate)
        self.SetInvTreeExpandedSetting(True)

    def _ExpandTree(self, animate = True):
        if self._is_tree_expanded:
            return
        self._is_tree_expanded = True
        width = settings.user.ui.Get('invTreeViewWidth_%s' % self.GetWindowSettingsID(), TREE_DEFAULT_WIDTH)
        self._update_top_action_container_padding(animate)
        self._update_bottom_right_cont_padding(animate)
        if animate:
            DURATION = 0.3
            animations.MorphScalar(self.dividerCont, 'width', self.dividerCont.width, width, duration=DURATION)
            animations.MorphScalar(self.rightCont, 'padLeft', endVal=-8, duration=DURATION)
            if self.invCont:
                animations.MorphScalar(self.invCont, 'padLeft', endVal=8 if self.compact else 16, duration=DURATION)
            if self.compact:
                animations.MorphScalar(self.topRightCont2, 'padLeft', endVal=8, duration=DURATION)
            animations.FadeIn(self.dividerCont, duration=0.3, sleep=True)
        else:
            self.dividerCont.width = width
            self.rightCont.padLeft = -8
            if self.invCont:
                self.invCont.padLeft = 8 if self.compact else 16
            if self.compact:
                self.topRightCont2.padLeft = 8
        self.dividerCont.state = uiconst.UI_PICKCHILDREN
        self.OnDividerContResize()

    def CollapseTree(self, animate = True):
        self._CollapseTree(animate)
        self.SetInvTreeExpandedSetting(False)

    def _CollapseTree(self, animate = True):
        if not self._is_tree_expanded:
            return
        self._is_tree_expanded = False
        self.dividerCont.state = uiconst.UI_DISABLED
        self._update_top_action_container_padding(animate)
        self._update_bottom_right_cont_padding(animate)
        if animate:
            DURATION = 0.3
            animations.MorphScalar(self.dividerCont, 'width', self.dividerCont.width, 0.0, duration=DURATION)
            animations.MorphScalar(self.rightCont, 'padLeft', endVal=0, duration=DURATION)
            if self.invCont:
                animations.MorphScalar(self.invCont, 'padLeft', endVal=0, duration=DURATION)
            if self.compact:
                animations.MorphScalar(self.topRightCont2, 'padLeft', endVal=0, duration=DURATION)
            animations.FadeOut(self.dividerCont, duration=DURATION, sleep=True)
        else:
            self.dividerCont.width = 0
            self.rightCont.padLeft = 0
            if self.invCont:
                self.invCont.padLeft = 0
            if self.compact:
                self.topRightCont2.padLeft = 0
        self.OnDividerContResize()

    def OnInvTreeUpdatingChanged(self, newState):
        if newState and self.needsUpdate:
            self.RefreshTree()

    def _clear_all_filters(self):
        self.DeselectAllFilters()
        if self.invCont:
            self.quickFilter.ClearFilter()
        self._update_filter_bottom_button()


class InventoryPrimary(Inventory):
    __guid__ = 'form.InventoryPrimary'
    default_windowID = 'InventoryPrimary'
    default_caption = 'UI/Neocom/InventoryBtn'

    def GetDefaultWndIcon(self):
        return self.default_iconNum

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        if self.currInvID == (invConst.INVENTORY_ID_SHIP_CARGO, oldShipID):
            invID = (invConst.INVENTORY_ID_SHIP_CARGO, shipID)
        else:
            invID = None
        self.RefreshTree(invID)

    def ApplyAttributes(self, attributes):
        super(InventoryPrimary, self).ApplyAttributes(attributes)
        if session.stationid:
            self.SetScope(uiconst.SCOPE_STATION)
        elif session.structureid:
            self.SetScope(uiconst.SCOPE_STRUCTURE)
        else:
            self.SetScope(uiconst.SCOPE_INFLIGHT)

    @classmethod
    def Open(cls, windowID = None, *args, **kwds):
        if not windowID:
            windowID = Inventory.GetWindowIDPrimary()
        return super(InventoryPrimary, cls).Open(windowID=windowID, *args, **kwds)

    @classmethod
    def GetIfOpen(cls, windowID = None, windowInstanceID = None):
        if not windowID:
            windowID = Inventory.GetWindowIDPrimary()
        return super(InventoryPrimary, cls).GetIfOpen(windowID, windowInstanceID)


class InventorySecondary(Inventory):

    @classmethod
    def Open(cls, invID = None, *args, **kwds):
        if not invID:
            invID = (kwds.get('windowID', cls.default_windowID), kwds.get('windowInstanceID', None))
        return super(InventorySecondary, cls).Open(invID=invID, *args, **kwds)


class StationItems(InventorySecondary):
    __guid__ = 'form.' + invConst.INVENTORY_ID_STATION_ITEMS
    default_windowID = invConst.INVENTORY_ID_STATION_ITEMS
    default_scope = uiconst.SCOPE_DOCKED
    default_iconNum = StationItemsController.iconName

    @classmethod
    def OnDropDataCls(cls, dragObj, nodes):
        return StationItemsController().OnDropData(nodes)


class StructureItems(InventorySecondary):
    __guid__ = 'form.' + invConst.INVENTORY_ID_STRUCTURE_ITEMS
    default_windowID = invConst.INVENTORY_ID_STRUCTURE_ITEMS
    default_scope = uiconst.SCOPE_DOCKED
    default_iconNum = StructureItemsController.iconName

    @classmethod
    def OnDropDataCls(cls, dragObj, nodes):
        return StructureItemsController().OnDropData(nodes)


class PlexVaultWindow(InventorySecondary):
    __guid__ = 'form.PlexVault'
    default_windowID = invConst.INVENTORY_ID_PLEX_VAULT
    default_iconNum = PLEX_WINDOW_ICON


class StationShips(InventorySecondary):
    __guid__ = 'form.' + invConst.INVENTORY_ID_STATION_SHIPS
    default_windowID = invConst.INVENTORY_ID_STATION_SHIPS
    default_scope = uiconst.SCOPE_DOCKED
    default_iconNum = StationShipsController.iconName

    @classmethod
    def OnDropDataCls(cls, dragObj, nodes):
        return StationShipsController().OnDropData(nodes)

    def ShowInvContainer(self, invID, *args, **kw):
        if invID[1] == GetActiveShip():
            InventorySecondary.OpenOrShow(invID, usePrimary=False)
        else:
            InventorySecondary.ShowInvContainer(self, invID, *args, **kw)


class StructureShips(StationShips):
    __guid__ = 'form.' + invConst.INVENTORY_ID_STRUCTURE_SHIPS
    default_windowID = invConst.INVENTORY_ID_STRUCTURE_SHIPS
    default_scope = uiconst.SCOPE_DOCKED
    default_iconNum = StructureShipsController.iconName

    @classmethod
    def OnDropDataCls(cls, dragObj, nodes):
        return StructureShipsController().OnDropData(nodes)


class StationCorpHangars(InventorySecondary):
    __guid__ = 'form.StationCorpHangars'
    default_windowID = invConst.INVENTORY_ID_STATION_CORP_HANGARS
    default_scope = uiconst.SCOPE_DOCKED
    default_iconNum = 'res:/ui/Texture/WindowIcons/corpHangar.png'

    def GetDefaultWndIcon(self):
        return self.default_iconNum


class StationCorpDeliveries(InventorySecondary):
    __guid__ = 'form.StationCorpDeliveries'
    default_windowID = invConst.INVENTORY_ID_STATION_CORP_DELIVERIES
    default_scope = uiconst.SCOPE_DOCKED
    default_iconNum = StationCorpDeliveriesController.iconName

    @classmethod
    def OnDropDataCls(cls, dragObj, nodes):
        return StationCorpDeliveriesController().OnDropData(nodes)

    @classmethod
    def Open(cls, invID = None, *args, **kwds):
        deliveryRoles = appConst.corpRoleAccountant | appConst.corpRoleJuniorAccountant | appConst.corpRoleTrader
        if session.corprole & deliveryRoles == 0:
            uicore.Message('CrpAccessDenied', {'reason': GetByLabel('UI/Commands/CorpRoleMissing')})
            allOpen = settings.char.windows.Get('openWindows', {})
            allOpen.pop('CorpMarketHangar', None)
            settings.char.windows.Set('openWindows', allOpen)
            return
        return super(StationCorpDeliveries, cls).Open(invID, *args, **kwds)


class AssetSafetyDeliveries(InventorySecondary):
    __guid__ = 'form.AssetSafetyDeliveries'
    default_windowID = 'AssetSafetyDeliveries'
    default_scope = uiconst.SCOPE_DOCKED
    default_iconNum = AssetSafetyDeliveriesController.iconName

    @classmethod
    def OnDropDataCls(cls, dragObj, nodes):
        return None


class AssetSafetyContainer(InventorySecondary):
    __guid__ = 'form.AssetSafetyContainer'
    default_windowID = 'AssetSafetyContainer'
    default_scope = uiconst.SCOPE_DOCKED
    default_iconNum = AssetSafetyContainerController.iconName

    @classmethod
    def OnDropDataCls(cls, dragObj, nodes):
        return None


class ActiveShipCargo(InventorySecondary):
    __guid__ = 'form.ActiveShipCargo'
    default_windowID = 'ActiveShipCargo'
    default_iconNum = 'res:/UI/Texture/WindowIcons/cargo.png'
    default_caption = 'UI/Neocom/ActiveShipCargoBtn'

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        self.rootInvID = (invConst.INVENTORY_ID_SHIP_CARGO, shipID)
        self.RefreshTree()

    def GetDefaultWndIcon(self):
        return self.default_iconNum

    @classmethod
    def OnDropDataCls(cls, dragObj, nodes):
        return ShipCargoController(GetActiveShip()).OnDropData(nodes)


class TreeExpandedSetting(UserSettingBool):

    def __init__(self, window):
        self._window_ref = weakref.ref(window)
        super(TreeExpandedSetting, self).__init__(settings_key='invTreeExpanded_{}'.format(window.windowID), default_value=self._get_default_value)

    @property
    def is_default_determined(self):
        window = self._window_ref()
        if window is None:
            return False
        if not window.rootInvID:
            return True
        return bool(window.treeData)

    def set(self, value):
        if self.is_default_determined:
            super(TreeExpandedSetting, self).set(value)

    def _get_default_value(self):
        window = self._window_ref()
        if window is None:
            return False
        if not window.rootInvID:
            return True
        if not window.treeData:
            return False
        data = window.treeData.GetChildByID(window.rootInvID)
        if data:
            return data.HasChildren()
        return False
