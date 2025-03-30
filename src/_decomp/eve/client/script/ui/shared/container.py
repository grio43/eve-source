#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\container.py
from math import pi, fabs
import eveicon
import evetypes
import eveui
import gametime
import mathext
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_PROGRAMMER, ROLE_WORLDMOD
from carbon.common.script.util import timerstuff
from carbon.common.script.util.commonutils import StripTags
from carbonui import Density
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.services.setting import UserSettingEnum
from carbonui.util.various_unsorted import NiceFilter
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.themeColored import FillThemeColored, FrameThemeColored
from eve.client.script.ui.shared.inventory import invSettings
from eve.client.script.ui.shared.item import InvItem
from eve.common.script.sys import eveCfg
from eve.common.script.util.eveFormat import GetAveragePrice
from eveexceptions import UserError
from inventorycommon.const import VIEW_MODES, SCROLL_VIEW_MODES, VIEWMODE_DETAILS, VIEWMODE_ICONS, VIEWMODE_LIST, VIEWMODE_CARDS, flagFrigateEscapeBay, flagStructureDeed
from inventorycommon.util import GetItemVolume
from eve.client.script.ui.util import uix
import blue
import carbon.client.script.util.lg as lg
import uthread
import carbonui.const as uiconst
import log
import trinity
import eve.client.script.environment.invControllers as invCtrl
import localization
import telemetry
import functools
from carbonui.uicore import uicore
from menu import MenuLabel
from bannedwords.client import bannedwords
from eve.common.lib import appConst as const
VIEW_MODE_ROW_PADDING = {VIEWMODE_LIST: 0,
 VIEWMODE_DETAILS: 0,
 VIEWMODE_ICONS: 12,
 VIEWMODE_CARDS: 6}

class InvContViewBtns(ContainerAutoSize):
    default_name = 'InvContViewBtns'
    default_align = uiconst.TOPLEFT
    default_height = 24

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.viewModeButtons = {}
        for viewMode in self.controller.availableViewModes:
            self.viewModeButtons[viewMode] = ButtonIcon(texturePath=self.controller.GetViewModeIcon(viewMode), parent=self, width=self.height, align=uiconst.TOLEFT, func=functools.partial(self._SetViewMode, viewMode), hint=self.controller.GetViewModeName(viewMode))

    def _SetViewMode(self, viewMode):
        self.UpdateButtons(viewMode)
        self.controller.SetInvContViewMode(viewMode)

    def UpdateButtons(self, activeViewMode):
        for viewMode, button in self.viewModeButtons.iteritems():
            if viewMode == activeViewMode:
                button.SetSelected()
            else:
                button.SetDeselected()


class InvContQuickFilter(Container):
    default_align = uiconst.TOPLEFT
    default_height = 24
    default_width = 100

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.invCont = attributes.invCont
        self.inputThread = None
        self.quickFilterInputBox = SingleLineEditText(name='quickFilterInputBox', parent=self, align=uiconst.CENTER, width=self.width, height=24, top=0, density=Density.COMPACT, OnChange=self.SetQuickFilterInput, isTypeField=True, hintText=localization.GetByLabel('UI/Common/Search'))
        self.quickFilterInputBox.ShowClearButton(hint=localization.GetByLabel('UI/Inventory/Clear'))
        self.quickFilterInputBox.SetHistoryVisibility(0)
        if self.invCont:
            self.SetInvCont(self.invCont)

    def SetInvCont(self, invCont):
        self.invCont = invCont
        if not invSettings.keep_inv_quick_filter_setting.is_enabled():
            self.quickFilterInputBox.SetText(u'')
            self.quickFilterInputBox.ClearSelection()

    def GetQuickFilterInput(self):
        return self.quickFilterInputBox.GetText()

    def SetQuickFilterInput(self, txt):
        if self.inputThread:
            return
        self.inputThread = uthread.new(self._SetQuickFilterInput, txt)

    def ClearFilter(self):
        self.quickFilterInputBox.SetValue('')

    def _SetQuickFilterInput(self, txt):
        if txt:
            blue.synchro.SleepWallclock(300)
        if self.invCont:
            self.invCont.SetQuickFilterInput(self.quickFilterInputBox.GetValue())
        self.inputThread = None


class InvContCapacityGauge(Container):
    __notifyevents__ = ['OnItemChange', 'OnSessionChanged', 'OnSessionMutated']
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        invCont = attributes.invCont
        self.secondaryVolume = 0.0
        self.additionalVolume = 0.0
        self.refreshGaugesThread = None
        self.resetPending = False
        self.refreshCapacityPending = False
        self.queuedItemChanges = []
        self.capacityText = eveLabel.EveLabelSmall(name='capacityText', parent=self, align=uiconst.CENTERLEFT, top=1, left=8)
        self.bg = Fill(bgParent=self, color=(0.0, 0.0, 0.0), opacity=0.4)
        self.capacityGaugeParentSec = Container(name='capacityGaugeParent', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.capacityGaugeSec = Fill(parent=self.capacityGaugeParentSec, align=uiconst.TOLEFT_PROP, color=self._get_gauge_highlight_color())
        self.capacityGaugeParent = Container(name='capacityGaugeParent', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.capacityGauge = Fill(parent=self.capacityGaugeParent, align=uiconst.TOLEFT_PROP, color=self._get_gauge_color())
        self.capacityGaugeAdd = Fill(parent=self.capacityGaugeParent, align=uiconst.TOLEFT_PROP, color=self._get_gauge_highlight_color())
        if invCont:
            self.SetInvCont(invCont)
        else:
            self.invCont = None

    @staticmethod
    def _get_gauge_color():
        return tuple(eveThemeColor.THEME_FOCUSDARK[:3]) + (0.6,)

    @staticmethod
    def _get_gauge_highlight_color():
        return tuple(eveThemeColor.THEME_FOCUS[:3]) + (0.6,)

    def SetInvCont(self, invCont):
        self.invCont = invCont
        self.SetSecondaryVolume()
        self.SetAdditionalVolume()
        self.RefreshCapacity()

    @telemetry.ZONE_METHOD
    def RefreshCapacity(self):
        if not session.IsItSafe():
            self.refreshCapacityPending = True
            return
        self.refreshCapacityPending = False
        if not self.invCont:
            return
        self.UpdateLabel()
        proportion = 0.0
        if self.invCont.invController.hasCapacity:
            cap = self.invCont.invController.GetCapacity()
            if cap.capacity:
                proportion = min(1.0, max(0.0, cap.used / float(cap.capacity)))
        currWidth = self.capacityGauge.width
        duration = 0.5 * fabs(currWidth - proportion) ** 0.3
        uicore.animations.MorphScalar(self.capacityGauge, 'width', currWidth, proportion, duration=duration)

    def UpdateLabel(self):
        currentInvCont = self.invCont
        if currentInvCont is None or currentInvCont.destroyed:
            return
        if currentInvCont.invController.hasCapacity:
            cap = currentInvCont.invController.GetCapacity()
            volume = cap.used + self.additionalVolume
            text = localization.GetByLabel('UI/Inventory/ContainerQuantityAndCapacity', quantity=volume, capacity=cap.capacity)
        else:
            volume = 0.0
            for item in currentInvCont.invController.GetItems():
                volume += GetItemVolume(item)

            text = localization.GetByLabel('UI/Inventory/ContainerCapacity', capacity=volume)
        if currentInvCont is None or currentInvCont.destroyed:
            return
        if self.secondaryVolume:
            if text:
                text = '(%s) ' % localization.formatters.FormatNumeric(self.secondaryVolume, useGrouping=True, decimalPlaces=1) + text
        if currentInvCont.invController.locationFlag == flagFrigateEscapeBay:
            text = localization.GetByLabel('UI/Inventory/FrigateEscapeBayQuantityAndCapacity', quantity=volume, capacity=cap.capacity)
        elif currentInvCont.invController.locationFlag == flagStructureDeed:
            text = localization.GetByLabel('UI/Inventory/DeedBayQuantityAndCapacity', quantity=1 if volume else 0, capacity=1)
        self.capacityText.text = text

    def HideLabel(self):
        self.capacityText.Hide()

    def ShowLabel(self):
        self.capacityText.Show()

    def GetHint(self):
        return self.capacityText.text

    @telemetry.ZONE_METHOD
    def SetAdditionalVolume(self, items = []):
        if not self.invCont:
            return
        volume = 0
        for item in items:
            volume += GetItemVolume(item)

        self.additionalVolume = volume
        value = self.GetVolumeProportion(volume)
        animValue = min(value, 1.0 - self.capacityGauge.width)
        currWidth = self.capacityGaugeAdd.width
        duration = 0.5 * fabs(currWidth - animValue) ** 0.3
        uicore.animations.MorphScalar(self.capacityGaugeAdd, 'width', currWidth, animValue, duration=duration)
        color = self._get_gauge_highlight_color()
        if self.invCont.invController.hasCapacity:
            cap = self.invCont.invController.GetCapacity()
            if cap.capacity and volume + cap.used > cap.capacity:
                color = eveColor.WARNING_ORANGE[:3]
        self.capacityGaugeAdd.SetRGBA(*color)
        self.UpdateLabel()

    @telemetry.ZONE_METHOD
    def SetSecondaryVolume(self, items = []):
        self.secondaryVolume = volume = sum([ GetItemVolume(i) for i in items ])
        value = self.GetVolumeProportion(volume)
        currWidth = self.capacityGaugeSec.width
        duration = 0.5 * fabs(currWidth - value) ** 0.3
        uicore.animations.MorphScalar(self.capacityGaugeSec, 'width', currWidth, value, duration=duration)
        self.UpdateLabel()

    def GetVolumeProportion(self, volume):
        if self.invCont and self.invCont.invController.hasCapacity:
            cap = self.invCont.invController.GetCapacity()
            if cap.capacity:
                return min(1.0, volume / cap.capacity)
        return 0

    def OnItemChange(self, item, change, location):
        itemID = item.itemID
        sourceLocationID = item.locationID
        destinationLocationID = change[const.ixLocationID] if const.ixLocationID in change else item.locationID
        if not session.IsItSafe():
            self.queuedItemChanges.append((itemID, sourceLocationID, destinationLocationID))
            return
        if self._ShouldResetGauges(itemID, sourceLocationID, destinationLocationID):
            self.ResetGauges()

    def _ShouldResetGauges(self, itemID, sourceLocationID, destinationLocationID):
        if not self.invCont or itemID == eveCfg.GetActiveShip():
            return False
        return self.invCont.invController.itemID in (sourceLocationID, destinationLocationID)

    def _ApplyItemChangesReceivedDuringSessionChange(self):
        if not session.IsItSafe():
            return
        try:
            for itemID, sourceLocationID, destinationLocationID in self.queuedItemChanges:
                if self._ShouldResetGauges(itemID, sourceLocationID, destinationLocationID):
                    self.ResetGauges()
                    break

            if self.refreshCapacityPending:
                self.RefreshCapacity()
        finally:
            self.queuedItemChanges = []

    def OnSessionChanged(self, *args, **kwargs):
        self._ApplyItemChangesReceivedDuringSessionChange()

    def OnSessionMutated(self, *args, **kwargs):
        self._ApplyItemChangesReceivedDuringSessionChange()

    def ResetGauges(self):
        self.resetPending = True
        if self.refreshGaugesThread:
            return
        self.refreshGaugesThread = uthread.new(self._ResetGauges)

    def _ResetGauges(self):
        try:
            while self.resetPending:
                self.RefreshCapacity()
                nodes = self.invCont.scroll.GetSelected()
                self.SetSecondaryVolume([ node.item for node in nodes ])
                self.SetAdditionalVolume()
                self.resetPending = False
                blue.synchro.Sleep(500)

        finally:
            self.refreshGaugesThread = None

    def OnColorThemeChanged(self):
        if self.capacityGauge:
            self.capacityGauge.color = self._get_gauge_color()
        if self.capacityGaugeSec:
            self.capacityGaugeSec.color = self._get_gauge_highlight_color()
        if self.capacityGaugeAdd:
            self.capacityGaugeAdd.color = self._get_gauge_highlight_color()


class ItemSortData(object):

    def __init__(self, rec):
        self.rec = rec
        self.name = StripTags(uix.GetItemName(rec).lower())
        self.typeName = StripTags(uix.GetCategoryGroupTypeStringForItem(rec).lower())
        self.itemID = rec.itemID
        self.quantity = 0
        if not (rec.singleton or rec.typeID in (const.typeBookmark,)):
            self.quantity = rec.stacksize

    def GetSortKey(self, sortby, direction):
        if sortby == 'name':
            return (self.name,
             self.typeName,
             self.quantity,
             self.itemID,
             self.rec)
        if sortby == 'qty':
            return (self.quantity,
             self.typeName,
             self.name,
             self.itemID,
             self.rec)
        if sortby == 'type':
            return (self.typeName,
             self.name,
             self.quantity,
             self.itemID,
             self.rec)
        if sortby == 'estPrice':
            estimatedPrice = self.GetEstimatedPrice()
            return (estimatedPrice,
             self.name,
             self.typeName,
             self.quantity,
             self.itemID,
             self.rec)

    def GetEstimatedPrice(self):
        if evetypes.GetCategoryID(self.rec.typeID) == const.categoryBlueprint:
            return None
        averagePrice = GetAveragePrice(self.rec)
        if not averagePrice:
            return None
        return self.rec.stacksize * averagePrice


class _InvContBase(Container):
    __guid__ = 'invCont._InvContBase'
    default_name = 'InventoryContainer'
    default_showControls = False
    default_containerViewMode = VIEWMODE_ICONS
    default_availableViewModes = (VIEWMODE_ICONS, VIEWMODE_DETAILS, VIEWMODE_LIST)
    default_hasScrollBackground = False
    default_shouldAddFinalRowPadding = True
    default_scrollClass = eveScroll.Scroll
    default_selectAllOnFirstLoad = False
    __notifyevents__ = ['OnPostCfgDataChanged', 'OnInvTempFilterChanged']
    __invControllerClass__ = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.itemID = attributes.itemID
        self.displayName = attributes.displayName
        self.activeFilters = attributes.get('activeFilters', [])
        showControls = attributes.get('showControls', self.default_showControls)
        self.quickFilterInput = attributes.Get('quickFilterInput', None)
        self.hasScrollBackground = attributes.get('hasScrollBackground', self.default_hasScrollBackground)
        self.shouldAddFinalRowPadding = attributes.get('shouldAddFinalRowPadding', self.default_shouldAddFinalRowPadding)
        self.scrollClass = attributes.get('scrollClass', self.default_scrollClass)
        self.selectAllOnFirstLoad = attributes.get('selectAllOnFirstLoad', self.default_selectAllOnFirstLoad)
        self.availableViewModes = attributes.get('availableViewModes', self.default_availableViewModes)
        self.getItemClass = attributes.get('getItemClass', self.GetItemClass)
        self.invController = self._GetInvController(attributes)
        self.scroll = None
        self.items = []
        self.cols = None
        self.droppedIconData = (None, None)
        self.iconWidth = 64
        self.sr.resizeTimer = None
        self.tmpDropIdx = {}
        self.refreshingView = False
        self.reRefreshView = False
        self.changeViewModeThread = None
        self.hintText = None
        self.dragStart = None
        self.previouslyHighlighted = None
        self.dragContainer = None
        self.itemChangeThread = None
        self.initialized = False
        self.numFilteredItems = 0
        self.hasLoaded = False
        self.view_mode_setting = UserSettingEnum(settings_key=self.GetViewModeSettingKey(), options=VIEW_MODES, default_value=self.default_containerViewMode)
        self.rowPadding = 0
        self.colMargin = 16
        self._SetViewModeValue(self.view_mode_setting.get())
        if showControls:
            self.topCont = Container(parent=self, align=uiconst.TOTOP, height=24, padBottom=8)
            InvContViewBtns(parent=self.topCont, align=uiconst.CENTERLEFT, controller=self)
            if self.IsQuickFilterEnabled():
                InvContQuickFilter(parent=self.topCont, align=uiconst.CENTERRIGHT, invCont=self)
        self.ConstructUI()

    def ConstructUI(self):
        self.scroll = self.scrollClass(parent=self, state=uiconst.UI_PICKCHILDREN, hasUnderlay=self.hasScrollBackground, rowPadding=self.rowPadding, shouldAddFinalRowPadding=self.shouldAddFinalRowPadding)
        self.scroll.sr.id = self._GetIDForScroll()
        self.scroll.OnNewHeaders = self.OnNewHeadersSet
        self.scroll.allowFilterColumns = 1
        self.scroll.SetColumnsHiddenByDefault(uix.GetInvItemDefaultHiddenHeaders())
        self.scroll.dad = self
        self.scroll.Copy = self.Copy
        self.scroll.Cut = self.Cut
        self.scroll.Paste = self.Paste
        content = self.content = self.scroll.GetContentContainer()
        content.OnDragEnter = self.OnDragEnter
        content.OnDragExit = self.OnDragExit
        content.OnDropData = self.OnScrollContentDropData
        content.GetMenu = lambda : self.GetContainerMenu()
        content.OnMouseUp = self.scroll.OnMouseUp = self.OnScrollMouseUp
        content.OnMouseDown = self.scroll.OnMouseDown = self.OnScrollMouseDown
        self.invSvcCookie = sm.GetService('inv').Register(self)
        self.InitializeSortBy()
        uthread.new(self._ChangeViewMode)
        self.view_mode_setting.on_change.connect(self._on_view_mode_setting_changed)

    def _GetIDForScroll(self):
        return 'containerWnd__%s' % self.invController.GetName()

    def _on_view_mode_setting_changed(self, view_mode):
        if self.viewMode != view_mode:
            self._SetViewModeValue(view_mode)
            self._ChangeViewMode()

    def InitializeSortBy(self):
        self.sortIconsBy, self.sortIconsDir = settings.user.ui.Get('containerSortIconsBy_%s' % self.name, ('type', 0))

    def _GetInvController(self, attributes):
        return self.__invControllerClass__(itemID=attributes.itemID)

    def GetItemClass(self):
        return InvItem

    def GetViewModeSettingKey(self):
        return u'containerViewMode_{}'.format(self.name)

    def SetInvContViewMode(self, value):
        self._SetViewModeValue(value)
        self.view_mode_setting.set(self.viewMode)
        self._ChangeViewMode()

    def _SetViewModeValue(self, value):
        if value in self.availableViewModes:
            self.viewMode = value
        else:
            self.viewMode = self.availableViewModes[0] if self.availableViewModes else None
        self.itemClass = self.getItemClass()
        self.itemHeight = self.itemClass.GetEntryHeight()
        self.itemWidth = self.itemClass.GetEntryWidth()
        self.colMargin = self.itemClass.GetEntryColMargin()
        self.rowPadding = VIEW_MODE_ROW_PADDING.get(self.viewMode, 6)
        if self.scroll:
            self.scroll.rowPadding = self.rowPadding
        self.cols = None

    def IsViewModesEnabled(self):
        return bool(self.availableViewModes)

    def IsQuickFilterEnabled(self):
        return True

    def IsCapacityEnabled(self):
        return True

    def IsEstimatedValueEnabled(self):
        return True

    def SetQuickFilterInput(self, filterTxt = ''):
        if len(filterTxt) > 0:
            self.quickFilterInput = filterTxt.lower()
            self.Refresh()
        else:
            prefilter = self.quickFilterInput
            self.quickFilterInput = None
            if prefilter != None:
                self.Refresh()
            self.hintText = None

    def QuickFilter(self, item):
        name = uix.GetItemName(item).lower()
        typename = evetypes.GetName(item.typeID).lower()
        input = self.quickFilterInput.lower()
        return name.find(input) + 1 or typename.find(input) + 1

    def OnInvTempFilterChanged(self):
        self.Refresh()

    def SetFilters(self, filters):
        self.activeFilters = filters
        self.Refresh()

    def FilterOptionsChange(self, combo, label, value, *args):
        if combo and combo.name == 'filterCateg':
            if value is None:
                ops = [(localization.GetByLabel('UI/Inventory/Filters/All'), None)]
            else:
                ops = sm.GetService('marketutils').GetFilterops(value)
            self.sr.filterGroup.LoadOptions(ops)
            settings.user.ui.Set('containerCategoryFilter%s' % self.name.title(), value)
        elif combo and combo.name == 'filterGroup':
            settings.user.ui.Set('containerGroupFilter%s' % self.name.title(), value)
        self.Refresh()

    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            itemID = data[0]
            for each in self.scroll.GetNodes():
                if each and getattr(each, 'item', None) and each.item.itemID == itemID:
                    each.name = None
                    uix.GetItemLabel(each.item, each, 1)
                    if each.panel:
                        each.panel.UpdateLabel()
                    return

    def _OnClose(self, *args):
        if self.itemChangeThread:
            self.itemChangeThread.kill()

    def _ChangeViewMode(self):
        if self.changeViewModeThread:
            self.changeViewModeThread.kill()
        self.changeViewModeThread = uthread.new(self.__ChangeViewMode)

    def __ChangeViewMode(self):
        if self.destroyed:
            return
        self.items = self.invController.GetItems()
        self.invController.OnItemsViewed()
        self.PrimeItems([ item for item in self.items if item is not None ])
        if self.items:
            self.items = self.FilterItems(self.items)
        self.UpdateHint()
        try:
            if self.ShouldShowSortBy():
                self.RefreshSort(self.sortIconsBy, self.sortIconsDir)
            else:
                self.RefreshView()
        except UserError:
            self.Close()
            if self.sr.Get('cookie', None):
                sm.GetService('inv').Unregister(self.invSvcCookie)
            raise

        if self.selectAllOnFirstLoad and not self.hasLoaded:
            self.SelectAll()
        self.hasLoaded = True

    def IsInItems(self, itemID):
        for rec in self.items:
            if rec and rec.itemID == itemID:
                return True

        return False

    def FilterItems(self, items):
        oldNum = len(items)
        if self.quickFilterInput:
            bannedwords.check_search_words_allowed(self.quickFilterInput)
            items = NiceFilter(self.QuickFilter, items)
        for filter in self.activeFilters:
            items = sm.GetService('itemFilter').FilterItems(items, filter)

        if self.invController.filtersEnabled:
            items = sm.GetService('itemFilter').ApplyTempFilter(items)
        self.numFilteredItems = oldNum - len(items)
        return items

    def UpdateHint(self):
        if len(self.items) == 0:
            if self.numFilteredItems:
                self.hintText = localization.GetByLabel('UI/Inventory/NothingFoundFiltered', numFilters=self.numFilteredItems)
            elif not self.invController.CheckCanQuery():
                self.hintText = localization.GetByLabel('UI/Inventory/NoAccessHint')
            elif self.invController.isCompact and self.invController.GetName():
                self.hintText = localization.GetByLabel('UI/Common/NothingFoundInContainer', invContainerName=self.invController.GetName())
            else:
                self.hintText = localization.GetByLabel('UI/Common/NothingFound')
        else:
            self.hintText = ''
        self.scroll.ShowHint(self.hintText)

    def Refresh(self):
        self._ChangeViewMode()

    def GetSortData(self, sortby, direction):
        sortData = []
        for rec in self.items:
            if rec is None:
                continue
            sortKey = ItemSortData(rec).GetSortKey(sortby, direction)
            if not sortKey:
                log.LogError('Unknown sortkey used in container sorting', sortby, direction)
                continue
            sortData.append((sortKey, rec))

        return sortData

    def RefreshSort(self, sortby, direction):
        self.sortIconsBy = sortby
        self.sortIconsDir = direction
        settings.user.ui.Set('containerSortIconsBy_%s' % self.name, (sortby, direction))
        sortData = self.GetSortData(sortby, direction)
        locCmpFunc = localization.util.GetSortFunc(localization.util.GetLanguageID())

        def _sort(left, right):
            if len(left) == 0:
                return 0
            if isinstance(left[0], basestring):
                res = locCmpFunc(left[0], right[0])
            else:
                res = cmp(left[0], right[0])
            if res == 0:
                return _sort(left[1:], right[1:])
            return res

        sortedList = sorted(sortData, cmp=_sort, key=lambda x: x[0])
        sortedList = [ x[1] for x in sortedList ]
        if direction:
            sortedList.reverse()
        self.SetSortedItems(sortedList)

    def SetSortedItems(self, sortedList):
        self.items = sortedList
        self.RefreshView()

    def SortIconsBy(self, sortby, direction):
        self.RefreshSort(sortby, direction)

    def _OnSizeChange_NoBlock(self, *args):
        self.sr.resizeTimer = timerstuff.AutoTimer(250, self.OnEndScale_)

    def OnEndScale_(self, *etc):
        if self.destroyed:
            self.sr.resizeTimer = None
            return
        if not self.initialized:
            return
        self.sr.resizeTimer = None
        oldcols = self.cols
        self.RefreshCols()
        if self.viewMode not in SCROLL_VIEW_MODES:
            if self.refreshingView:
                self.reRefreshView = True
                return
            if oldcols != self.cols or not self.itemClass.IsFixedWidth():
                uthread.new(self.RefreshView)

    @telemetry.ZONE_METHOD
    def AddItem(self, rec, index = None, fromWhere = None):
        if self.quickFilterInput:
            if not self.QuickFilter(rec):
                return
        if not self.FilterItems([rec]):
            return
        lg.Info('vcont', 'AddItem', fromWhere, rec.stacksize, evetypes.GetName(rec.typeID))
        for node in self.scroll.sr.nodes:
            if self.viewMode in SCROLL_VIEW_MODES:
                if node is not None and node.Get('item', None) and node.item.itemID == rec.itemID:
                    lg.Warn('vcont', 'Tried to add an item that is already there??')
                    self.UpdateItem(node.item)
                    return
            else:
                for internalNode in node.internalNodes:
                    if internalNode is not None and internalNode.item.itemID == rec.itemID:
                        lg.Warn('vcont', 'Tried to add an item that is already there??')
                        self.UpdateItem(internalNode.item)
                        return

        if self.viewMode in SCROLL_VIEW_MODES:
            from eve.client.script.ui.shared.item import Item
            self.items.append(rec)
            data = self.GetItemData(rec, self.scroll.sr.id)
            self.scroll.AddEntries(-1, [GetFromClass(Item, data)])
            self.UpdateHint()
        else:
            if index is not None:
                while index < len(self.items):
                    if self.items[index] is None:
                        return self.SetItem(index, rec)
                    index += 1

                while index >= len(self.scroll.sr.nodes) * self.cols:
                    self.AddRow()

                return self.SetItem(index, rec)
            if len(self.items) and None in self.items:
                idx = self.tmpDropIdx.get(rec.itemID, None)
                if idx is None:
                    idx = self.items.index(None)
                return self.SetItem(idx, rec)
            if not self.cols:
                self.RefreshCols()
            if index >= len(self.scroll.sr.nodes) * self.cols:
                self.AddRow()
            return self.SetItem(0, rec)

    @telemetry.ZONE_METHOD
    def UpdateItem(self, rec, *etc):
        lg.Info('vcont', 'UpdateItem', rec and '[%s %s]' % (rec.stacksize, evetypes.GetName(rec.typeID)))
        if self.viewMode in SCROLL_VIEW_MODES:
            idx = 0
            for each in self.items:
                if each.itemID == rec.itemID:
                    self.items[idx] = rec
                    break
                idx += 1

            for entry in self.scroll.sr.nodes:
                if entry.item.itemID == rec.itemID:
                    newentry = self.GetItemData(rec, self.scroll.sr.id)
                    for key, value in newentry.iteritems():
                        entry[key] = value

                    if entry.panel:
                        entry.panel.Load(entry)
                    self.UpdateHint()
                    return

        else:
            i = 0
            for rowNode in self.scroll.sr.nodes:
                for entry in rowNode.internalNodes:
                    if entry is not None and entry.item and entry.item.itemID == rec.itemID:
                        self.SetItem(i, rec)
                        return
                    i += 1

    def GetItemData(self, rec, scrollID = None):
        return uix.GetItemData(rec, self.viewMode, self.invController.viewOnly, container=self, scrollID=scrollID)

    @telemetry.ZONE_METHOD
    def RemoveItem(self, rec):
        lg.Info('vcont', 'RemoveItem', rec and '[%s %s]' % (rec.stacksize, evetypes.GetName(rec.typeID)))
        if self.viewMode in SCROLL_VIEW_MODES:
            for entry in self.scroll.sr.nodes:
                if entry.item.itemID == rec.itemID:
                    self.scroll.RemoveEntries([entry])
                    break

            for item in self.items:
                if item.itemID == rec.itemID:
                    self.items.remove(item)

        else:
            i = 0
            for rowNode in self.scroll.sr.nodes:
                si = 0
                for entry in rowNode.internalNodes:
                    if entry and entry.item and entry.item.itemID == rec.itemID:
                        self.SetItem(i, None)
                        rowNode.internalNodes[si] = None
                        break
                    si += 1
                    i += 1

            i = 0
            for item in self.items:
                if item and item.itemID == rec.itemID:
                    self.items[i] = None
                i += 1

            self.CleanupRows()

    @telemetry.ZONE_METHOD
    def CleanupRows(self):
        rm = []
        for rowNode in self.scroll.sr.nodes:
            internalNodes = rowNode.Get('internalNodes', [])
            if internalNodes == [None] * len(internalNodes):
                rm.append(rowNode)
            else:
                rm = []

        if rm:
            self.scroll.RemoveEntries(rm)

    @telemetry.ZONE_METHOD
    def AddRow(self):
        self.items += [None] * self.cols
        self.scroll.AddEntries(fromIdx=-1, nodesData=[GetFromClass(Row, {'lenitems': len(self.scroll.sr.nodes) * self.cols,
          'rec': [None] * self.cols,
          'internalNodes': [None] * self.cols,
          'parentWindow': self,
          'hilightable': False,
          'container': self,
          'itemClass': self.itemClass,
          'itemWidth': self.itemWidth,
          'itemHeight': self.itemHeight})])
        self.scroll.UpdatePosition()

    @telemetry.ZONE_METHOD
    def StackAll(self):
        self.invController.StackAll()
        uthread.new(self.Refresh)

    def OnScrollContentDropData(self, dragObj, nodes):
        idx = None
        if self.viewMode not in SCROLL_VIEW_MODES and self.cols:
            l, t = self.scroll.GetAbsolutePosition()
            idx = self.cols * len(self.scroll.sr.nodes) + (uicore.uilib.x - l) // (64 + self.colMargin)
        sm.ScatterEvent('OnInvContDragExit', self.invController.GetInvID(), [])
        self.OnDropDataWithIdx(nodes, idx)

    def OnDragEnter(self, dragObj, nodes):
        sm.ScatterEvent('OnInvContDragEnter', self.invController.GetInvID(), nodes)

    def OnDragExit(self, dragObj, nodes):
        sm.ScatterEvent('OnInvContDragExit', self.invController.GetInvID(), nodes)

    def OnDropData(self, dragObj, nodes):
        return self.OnDropDataWithIdx(nodes)

    def Cut(self):
        items = self.scroll.GetSelected()
        sm.GetService('inv').SetItemClipboard(items)

    def Copy(self):
        if bool(session.role & ROLE_PROGRAMMER):
            items = self.scroll.GetSelected()
            sm.GetService('inv').SetItemClipboard(items, copy=True)
        return eveScroll.Scroll.Copy(self.scroll)

    def Paste(self, value):
        items, copy = sm.GetService('inv').PopItemClipboard()
        if copy and bool(session.role & ROLE_PROGRAMMER):
            from eve.devtools.script import param
            for item in items:
                itemID = sm.GetService('slash').cmd_createitem(param.ParamObject('%s %s' % (item.rec.typeID, item.rec.stacksize)))
                if itemID:
                    invController = invCtrl.StationItems() if session.stationid else invCtrl.ShipCargo()
                    blue.synchro.SleepWallclock(100)
                    newItem = invController.GetItem(itemID)
                    if newItem:
                        self.invController.AddItems([newItem])

        else:
            self.invController.OnDropData(items)

    @telemetry.ZONE_METHOD
    def OnDropDataWithIdx(self, nodes, idx = None):
        self.scroll.ClearSelection()
        if len(nodes) and getattr(nodes[0], 'scroll', None) and not nodes[0].scroll.destroyed:
            nodes[0].scroll.ClearSelection()
        if nodes and getattr(nodes[0], 'item', None) in self.invController.GetItems() and not uicore.uilib.Key(uiconst.VK_SHIFT):
            if getattr(nodes[0], 'scroll', None) != self.scroll:
                return
            if idx is not None:
                for i, node in enumerate(nodes):
                    self.tmpDropIdx[node.itemID] = idx + i

            for node in nodes:
                idx = self.tmpDropIdx.get(node.itemID, None)
                if idx is None:
                    if None in self.items:
                        idx = self.items.index(None)
                    else:
                        idx = len(self.items)
                self.OnItemDrop(idx, node)

            return
        return self.invController.OnDropData(nodes)

    @telemetry.ZONE_METHOD
    def OnItemDrop(self, index, node):
        if self.viewMode == VIEWMODE_ICONS:
            self.RemoveItem(node.item)
            self.AddItem(node.item, index)

    @telemetry.ZONE_METHOD
    def SetItem(self, index, rec):
        lg.Info('vcont', 'SetItem', index, rec and '[%s %s]' % (rec.stacksize, evetypes.GetName(rec.typeID)))
        if not self or self.destroyed:
            return
        if index < len(self.items) and rec and self.items[index] is not None and self.items[index].itemID != rec.itemID:
            while index < len(self.items) and self.items[index] is not None:
                index += 1

        if self.cols:
            rowIndex = index // self.cols
        else:
            rowIndex = 0
        while rowIndex >= len(self.scroll.sr.nodes):
            self.AddRow()

        while index >= len(self.items):
            self.items += [None]

        self.items[index] = rec
        try:
            self.scroll.sr.nodes[rowIndex].rec[index % self.cols] = rec
            self.UpdateHint()
            node = None
            if rec:
                node = self.GetItemData(rec, self.scroll.sr.id)
                if not self or self.destroyed:
                    return
                node.scroll = self.scroll
                node.panel = None
                node.idx = index
                node.__guid__ = self.itemClass.__guid__
                node.decoClass = self.itemClass
                node.width = self.itemWidth
                node.height = self.itemHeight
            self.scroll.sr.nodes[index // self.cols].internalNodes[index % self.cols] = node
        except IndexError:
            return

        icon = self.GetIcon(index)
        if icon:
            if rec is None:
                icon.display = False
                icon.sr.node = None
            else:
                icon.display = True
                node.panel = icon
                node.viewOnly = self.invController.viewOnly
                icon.Load(node)

    @telemetry.ZONE_METHOD
    def RefreshCols(self):
        w = self.scroll.GetContentWidth()
        columns = w // (self.itemWidth + self.colMargin)
        if w % (self.itemWidth + self.colMargin) >= self.itemWidth:
            columns += 1
        self.cols = max(1, columns)

    def PrimeItems(self, itemlist):
        locations = []
        for rec in itemlist:
            if rec.categoryID == const.categoryStation and rec.groupID == const.groupStation:
                locations.append(rec.itemID)
                locations.append(rec.locationID)
            if rec.singleton and (rec.categoryID == const.categoryShip or rec.groupID in (const.groupWreck,
             const.groupCargoContainer,
             const.groupSecureCargoContainer,
             const.groupAuditLogSecureContainer,
             const.groupFreightContainer,
             const.groupBiomass)):
                locations.append(rec.itemID)

        if locations:
            cfg.evelocations.Prime(locations)

    def OnNewHeadersSet(self, *args):
        self.RefreshView()

    @telemetry.ZONE_METHOD
    def RefreshView(self, *args):
        from eve.client.script.ui.shared.item import Item
        if self.refreshingView:
            return
        self.refreshingView = 1
        try:
            if self.viewMode in SCROLL_VIEW_MODES:
                self.scroll.sr.id = self._GetIDForScroll()
                self.scroll.hiliteSorted = 1
                scrolllist = []
                for rec in self.items:
                    if rec:
                        theData = self.GetItemData(rec, self.scroll.sr.id)
                        list = GetFromClass(Item, theData)
                        scrolllist.append(list)

                hdr = uix.GetInvItemDefaultHeaders()
                scrll = self.scroll.GetScrollProportion()
                self.scroll.LoadContent(contentList=scrolllist, headers=hdr, scrollTo=scrll)
            else:
                if not self.cols:
                    self.RefreshCols()
                while self.items and self.items[-1] is None:
                    self.items = self.items[:-1]

                content = []
                selectedItems = [ node.item for node in self.scroll.GetSelected() ]
                for i in xrange(len(self.items)):
                    blue.pyos.BeNice()
                    row_index = i % self.cols
                    if row_index == 0:
                        entry = [None] * self.cols
                        nodes = [None] * self.cols
                        content.append(GetFromClass(Row, {'lenitems': i,
                         'rec': entry,
                         'internalNodes': nodes,
                         'parentWindow': self,
                         'hilightable': False,
                         'container': self,
                         'itemClass': self.itemClass,
                         'itemWidth': self.itemWidth,
                         'itemHeight': self.itemHeight}))
                    if self.items[i]:
                        node = self.GetItemData(self.items[i])
                        node.scroll = self.scroll
                        node.panel = None
                        node.__guid__ = self.itemClass.__guid__
                        node.decoClass = self.itemClass
                        node.idx = i
                        node.selected = node.item in selectedItems
                        nodes[row_index] = node
                        entry[row_index] = self.items[i]

                self.scroll.sr.sortBy = None
                self.scroll.sr.id = None
                self.scroll.LoadContent(fixedEntryHeight=self.itemHeight, contentList=content, scrollTo=self.scroll.GetScrollProportion())
                self.CleanupRows()
            self.UpdateHint()
            self.initialized = True
            sm.ScatterEvent('OnInvContRefreshed', self)
        finally:
            if not self.destroyed:
                if self.viewMode == VIEWMODE_DETAILS:
                    self.scroll.sr.minColumnWidth = {localization.GetByLabel('UI/Common/Name'): 44}
                    self.scroll.UpdateTabStops()
                else:
                    self.scroll.sr.minColumnWidth = {}
                self.refreshingView = 0
                if self.reRefreshView:
                    self.reRefreshView = False
                    self.RefreshCols()
                    uthread.new(self.RefreshView)
                self._UpdateScrollPadding()

    def _UpdateScrollPadding(self):
        if self.viewMode not in SCROLL_VIEW_MODES:
            self.scroll.innerPadding = (8, 4, 0, 0)
            self.scroll.padding = (-8, 0, 0, 0)
            self.scroll.sr.maincontainer.padTop = -4
            self.scroll.sr.clipper.clipChildren = False
        else:
            self.scroll.innerPadding = 0
            self.scroll.padding = 0
            self.scroll.sr.maincontainer.padTop = 0
            self.scroll.sr.clipper.clipChildren = True

    def SelectAll(self):
        if not self.destroyed:
            self.scroll.SelectAll()

    def InvertSelection(self):
        if not self.destroyed:
            self.scroll.ToggleSelected()

    def GetIcons(self):
        return [ icon for row in self.scroll.GetContentContainer().children for icon in row.sr.icons if icon.display ]

    def OnScrollMouseDown(self, *args):
        if args[0] == uiconst.MOUSELEFT:
            self.dragStart = self.GetDragPosition()
            if uicore.uilib.Key(uiconst.VK_CONTROL) or uicore.uilib.Key(uiconst.VK_SHIFT):
                self.previouslyHighlighted = [ x.panel for x in self.scroll.GetSelected() ]
            else:
                self.previouslyHighlighted = []
            dragContainer = getattr(self, 'dragContainer', None)
            if dragContainer is None or dragContainer.destroyed:
                self.dragContainer = Container(name='dragContainer', parent=self.GetRubberbandParentContainer(), align=uiconst.TOPLEFT, idx=0)
                FrameThemeColored(parent=self.dragContainer, frameConst=uiconst.FRAME_BORDER1_CORNER3, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.5)
                FillThemeColored(parent=self.dragContainer, frameConst=uiconst.FRAME_FILLED_CORNER3, opacity=0.3)
            self.dragContainer.Hide()
            uthread.new(self.RubberbandSelection_thread)

    def IsRowInDragArea(self, row_top, row_height, startY, currentY):
        isYBeforeRow = lambda y: y < row_top
        isYAfterRow = lambda y: row_top + row_height < y
        isSelectionBeforeRow = lambda startY, currentY: isYBeforeRow(startY) and isYBeforeRow(currentY)
        isSelectionAfterRow = lambda startY, currentY: isYAfterRow(startY) and isYAfterRow(currentY)
        return not (isSelectionBeforeRow(startY, currentY) or isSelectionAfterRow(startY, currentY))

    def IsIconInDragArea(self, icon, startX, currentX):
        iconX = self._CorrectXInScroll(icon.absoluteLeft)
        isXBeforeIcon = lambda x: x < iconX
        isXAfterIcon = lambda x: iconX + icon.width < x
        isSelectionBeforeIcon = lambda startX, currentX: isXBeforeIcon(startX) and isXBeforeIcon(currentX)
        isSelectionAfterIcon = lambda startX, currentX: isXAfterIcon(startX) and isXAfterIcon(currentX)
        return not (isSelectionBeforeIcon(startX, currentX) or isSelectionAfterIcon(startX, currentX))

    def _CorrectXInScroll(self, x):
        return x - self.scroll.GetContentContainer().absoluteLeft

    def _CorrectYInScroll(self, y):
        return y - self.scroll.GetContentContainer().absoluteTop

    def GetDragPosition(self):
        x = self._CorrectXInScroll(uicore.uilib.x)
        y = self._CorrectYInScroll(uicore.uilib.y)
        return (x, y)

    def GetRubberbandParentContainer(self):
        return self.scroll.GetContentContainer()

    def UpdateDragContainerPosition(self, startX, startY, currentX, currentY):
        xCorrection = 0
        yCorrection = 0
        scrollContent = self.scroll.GetContentContainer()
        dragArea = self.GetRubberbandParentContainer()
        if scrollContent != dragArea:
            xCorrection = scrollContent.absoluteLeft - dragArea.absoluteLeft
            yCorrection = scrollContent.absoluteTop - dragArea.absoluteTop
        left = max(startX + xCorrection, 0)
        width = min(currentX + xCorrection, self.GetRubberbandParentContainer().displayWidth) - left
        top = max(startY + yCorrection, 0)
        height = min(currentY + yCorrection, self.GetRubberbandParentContainer().displayHeight) - top
        self.dragContainer.left = left
        self.dragContainer.top = top
        self.dragContainer.width = width
        self.dragContainer.height = height

    def RubberbandSelection_thread(self, *args):
        from eve.client.script.ui.shared.item import Item
        timer = IntervalTimer()
        scroll_remainder = 0.0
        block_scrolling = not is_mouse_inside_vertically(self.scroll)
        while self.dragStart and uicore.uilib.leftbtn and trinity.app.IsActive():
            startX, startY = self.dragStart
            currentX, currentY = self.GetDragPosition()
            if startX > currentX:
                temp = currentX
                currentX = startX
                startX = temp
            if startY > currentY:
                temp = currentY
                currentY = startY
                startY = temp
            self.UpdateDragContainerPosition(startX, startY, currentX, currentY)
            self.dragContainer.Show()
            for each in self.scroll.GetContentContainer().children:
                if isinstance(each, Row):
                    row_top = each.top
                    row_height = self.itemClass.GetEntryHeight()
                    if self.IsRowInDragArea(row_top, row_height, startY, currentY):
                        for icon in each.sr.icons:
                            if self.IsIconInDragArea(icon, startX, currentX):
                                if icon in self.previouslyHighlighted:
                                    if uicore.uilib.Key(uiconst.VK_SHIFT):
                                        icon.Select()
                                    elif uicore.uilib.Key(uiconst.VK_CONTROL):
                                        icon.Deselect()
                                else:
                                    icon.Select()
                            elif icon not in self.previouslyHighlighted:
                                icon.Deselect()
                            else:
                                icon.Select()

                    else:
                        for icon in each.sr.icons:
                            if icon not in self.previouslyHighlighted:
                                icon.Deselect()
                            else:
                                icon.Select()

                elif isinstance(each, Item):
                    if each.top >= startY and each.top + each.height <= currentY or each.top + each.height >= startY and each.top <= currentY:
                        each.Select()
                        if each in self.previouslyHighlighted:
                            if uicore.uilib.Key(uiconst.VK_SHIFT):
                                each.Select()
                            elif uicore.uilib.Key(uiconst.VK_CONTROL):
                                each.Deselect()
                        else:
                            each.Select()
                    elif each not in self.previouslyHighlighted:
                        each.Deselect()
                    else:
                        each.Select()

            dt = timer.tick().total_seconds()
            if block_scrolling:
                block_scrolling = not is_mouse_inside_vertically(self.scroll)
            if not block_scrolling:
                scroll_speed = calculate_drag_scroll_speed_vertical(self.scroll)
                if not mathext.is_almost_zero(scroll_speed):
                    scroll_delta = scroll_speed * dt
                    scroll_remainder += scroll_delta % 1.0
                    while scroll_remainder >= 1.0:
                        scroll_delta += 1.0
                        scroll_remainder -= 1.0

                    self.scroll.ScrollPixels(mathext.floor(scroll_delta))
            eveui.wait_for_next_frame()

        self.dragStart = None
        self.previouslyHighlighted = None
        self.dragContainer.Hide()

    def OnScrollMouseUp(self, *args):
        from eve.client.script.ui.shared.item import Item
        if self.dragStart and args[0] == uiconst.MOUSELEFT:
            startX, startY = self.dragStart
            endX, endY = self.GetDragPosition()
            if startX > endX:
                temp = endX
                endX = startX
                startX = temp
            if startY > endY:
                temp = endY
                endY = startY
                startY = temp
            preSelectedNodes = self.scroll.GetSelected() if uicore.uilib.Key(uiconst.VK_CONTROL) or uicore.uilib.Key(uiconst.VK_SHIFT) else []
            selectedNodes = []
            for each in self.scroll.GetContentContainer().children:
                if isinstance(each, Row):
                    row_top = each.top
                    row_height = self.itemClass.GetEntryHeight()
                    if self.IsRowInDragArea(row_top, row_height, startY, endY):
                        for icon in each.sr.icons:
                            if self.IsIconInDragArea(icon, startX, endX) and icon.sr.node:
                                selectedNodes.append(icon.sr.node)

                elif isinstance(each, Item):
                    if each.top >= startY and each.top + each.height <= endY or each.top + each.height >= startY and each.top <= endY:
                        selectedNodes.append(each.sr.node)

            if uicore.uilib.Key(uiconst.VK_SHIFT):
                selectedNodes.extend(preSelectedNodes)
            elif uicore.uilib.Key(uiconst.VK_CONTROL):
                newSelectedNodes = [ item for item in selectedNodes if item not in preSelectedNodes ]
                newSelectedNodes.extend([ item for item in preSelectedNodes if item not in selectedNodes ])
                selectedNodes = newSelectedNodes
            uthread.new(self.scroll.SelectNodes, selectedNodes)
            self.dragStart = None
            self.previouslyHighlighted = None
            self.dragContainer.Hide()

    def GetIcon(self, index):
        for each in self.scroll.GetContentContainer().children:
            if getattr(each, 'index', -1) == index // self.cols * self.cols:
                lg.Info('vcont', 'GetIcon(', index, ') returns', each.sr.icons[index % self.cols].name)
                return each.sr.icons[index % self.cols]

        lg.Info('vcont', 'GetIcon(', index, ') found nothing')

    def RegisterSpecialActionButton(self, button):
        pass

    def GetContainerMenu(self):
        return GetContainerMenu(self)

    def IsItemPresent(self, itemID):
        return itemID in [ item.itemID for item in self.items if item is not None ]

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

    def GetActiveViewModeName(self):
        return self.GetViewModeName(self.viewMode)

    def GetViewModeIcon(self, viewMode):
        if viewMode == VIEWMODE_ICONS:
            return eveicon.grid_view
        if viewMode == VIEWMODE_DETAILS:
            return eveicon.details_view
        if viewMode == VIEWMODE_LIST:
            return eveicon.list_view
        if viewMode == VIEWMODE_CARDS:
            return eveicon.card_view

    def GetActiveViewModeIcon(self):
        return self.GetViewModeIcon(self.viewMode)

    def ShouldShowSortBy(self):
        return self.viewMode not in SCROLL_VIEW_MODES


def is_mouse_inside_vertically(element):
    _, element_top, _, element_height = element.GetAbsolute()
    return element_top <= uicore.uilib.y <= element_top + element_height


class IntervalTimer(object):

    def __init__(self, now_func = None):
        if now_func is None:
            now_func = gametime.now
        self._now_func = now_func
        self._last_update = None

    def start(self):
        self._last_update = self._now_func()

    def tick(self):
        if self._last_update is None:
            self.start()
        now = self._now_func()
        dt = now - self._last_update
        self._last_update = now
        return dt


def calculate_drag_scroll_speed_vertical(scroll):
    MIN_SCROLL_SPEED = 100
    MAX_SCROLL_SPEED = 4000
    SCROLL_SPEED_DISTANCE_FACTOR = 1.6
    _, scroll_top, _, scroll_height = scroll.GetAbsolute()
    distance_from_top = scroll_top - uicore.uilib.y
    distance_from_bottom = uicore.uilib.y - (scroll_top + scroll_height)
    if distance_from_top > 0:
        return mathext.clamp(distance_from_top ** SCROLL_SPEED_DISTANCE_FACTOR, MIN_SCROLL_SPEED, MAX_SCROLL_SPEED)
    elif distance_from_bottom > 0:
        return -mathext.clamp(distance_from_bottom ** SCROLL_SPEED_DISTANCE_FACTOR, MIN_SCROLL_SPEED, MAX_SCROLL_SPEED)
    else:
        return 0


class Row(SE_BaseClassCore):
    __guid__ = 'listentry.VirtualContainerRow'
    default_showHilite = False

    def Startup(self, dad):
        self.dad = dad.dad
        self.initialized = False
        self.sr.icons = []

    @telemetry.ZONE_METHOD
    def Load(self, node):
        if self.initialized:
            return
        self.initialized = True
        self.sr.node = node
        self.index = node.lenitems
        for i in range(len(self.sr.icons), len(node.internalNodes)):
            icon = node.itemClass(parent=self, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT)
            icon.width = self.GetItemWidth(node)
            icon.height = node.itemHeight
            icon.top = 0
            icon.left = (icon.width + self.dad.colMargin) * i
            self.sr.icons.append(icon)

        for icon in self.sr.icons[self.dad.cols:]:
            icon.sr.node = None
            icon.subnodeIdx = None

        i = 0
        for subnode in node.internalNodes:
            icon = self.sr.icons[i]
            if not node.itemClass.IsFixedWidth():
                icon.width = self.GetItemWidth(node)
                icon.left = (icon.width + self.dad.colMargin) * i
            if subnode is None:
                icon.display = False
                icon.sr.node = None
                icon.subnodeIdx = None
            else:
                subnode.panel = icon
                icon.Load(subnode)
                icon.display = True
                icon.subnodeIdx = subnode.idx = self.index + i
            i += 1

    def GetItemWidth(self, node):
        if node.itemClass.IsFixedWidth():
            return node.itemWidth
        return max(node.itemWidth, (self.width + self.dad.colMargin) / len(self.sr.node.internalNodes) - self.dad.colMargin)

    def GetMenu(self):
        return self.dad.GetContainerMenu()

    def OnDropData(self, dragObj, nodes):
        l, t, w, h = self.GetAbsolute()
        index = self.index + (uicore.uilib.x - l) // (64 + self.dad.colMargin)
        self.dad.OnDropDataWithIdx(nodes, index)

    def OnDragEnter(self, dragObj, nodes):
        self.sr.node.container.OnDragEnter(dragObj, nodes)

    def OnDragExit(self, dragObj, nodes):
        self.sr.node.container.OnDragExit(dragObj, nodes)

    def OnMouseDown(self, *etc):
        if self.dad.scroll:
            self.dad.scroll.OnMouseDown(*etc)

    def OnMouseUp(self, *etc):
        if self.dad.scroll:
            self.dad.scroll.OnMouseUp(*etc)

    def OnMouseMove(self, *etc):
        if self.dad.scroll:
            self.dad.scroll.OnMouseMove(*etc)

    def ShowSelected(self, *args):
        pass


def GetContainerMenu(containerWindow):
    menu = MenuData()
    if eve.session.role & (ROLE_GML | ROLE_WORLDMOD):
        menu.AddEntry(text=MenuLabel('UI/Commands/Refresh'), func=containerWindow.Refresh)
        menu.AddSeparator()
    menu.AddEntry(text=MenuLabel('UI/Common/SelectAll'), func=containerWindow.SelectAll)
    menu.AddEntry(text=MenuLabel('UI/Inventory/InvertSelection'), func=containerWindow.InvertSelection)
    if containerWindow.ShouldShowSortBy():
        menu.AddSeparator()
        sort_options = GetBasicSortOptions()
        sort_options += [None, ('UI/Inventory/EstPrice', ('estPrice', 0)), ('UI/Inventory/EstPriceReversed', ('estPrice', 1))]
        menu.AddEntry(text=MenuLabel('UI/Common/SortBy'), texturePath=eveicon.bars_sort_ascending, subMenuData=GetSortMenuForOptionsOptions(containerWindow, sort_options))
    if not containerWindow.invController.viewOnly:
        container_item = containerWindow.invController.GetInventoryItem()
        container_slim = sm.GetService('michelle').GetItem(container_item.itemID)
        offer_stack_all = should_offer_stack_all(session, container_group_id=container_item.groupID, container_category_id=container_item.categoryID, container_owner_id=container_item.ownerID, container_corporation_id=getattr(container_slim, 'corpID', None), container_alliance_id=getattr(container_slim, 'allianceID', None))
        if offer_stack_all:
            menu.AddSeparator()
            menu.AddEntry(text=MenuLabel('UI/Inventory/StackAll'), texturePath=eveicon.stack, func=containerWindow.StackAll)
    return menu


def should_offer_stack_all(session, container_group_id, container_category_id, container_owner_id, container_corporation_id, container_alliance_id):
    return container_group_id in (const.groupStation, const.groupPlanetaryCustomsOffices) or container_category_id == const.categoryStructure or container_owner_id in (session.charid, session.corpid, session.allianceid) or session.corpid == container_corporation_id or session.allianceid and session.allianceid == container_alliance_id


def GetSortMenuForOptionsOptions(containerWindow, options):
    m = []
    for eachOption in options:
        if eachOption is None:
            m.append(None)
        else:
            labelPath, args = eachOption
            m.append((MenuLabel(labelPath), containerWindow.SortIconsBy, args))

    return m


def GetBasicSortOptions():
    return [('UI/Common/Name', ('name', 0)),
     ('UI/Inventory/NameReversed', ('name', 1)),
     None,
     ('UI/Inventory/ItemQuantity', ('qty', 0)),
     ('UI/Inventory/QuantityReversed', ('qty', 1)),
     None,
     ('UI/Common/Type', ('type', 0)),
     ('UI/Inventory/TypeReversed', ('type', 1))]
