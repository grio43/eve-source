#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\scroll.py
import contextlib
import logging
import sys
import weakref
import blue
import localization
import mathext
import telemetry
import uthread
import uthread2
from carbon.common.script.util.commonutils import StripTags
from carbonui import Axis, fontconst, uiconst
from carbonui.control.contextMenu.menuUtil import GetContextMenuOwner, HasContextMenu
from carbonui.control.label import LabelCore
from carbonui.control.scrollbar import Scrollbar
from carbonui.control.scrollColumnHeader import ColumnHeader
from carbonui.control.scroll_const import SortDirection, GetHiddenColumnsKey
from carbonui.control.scrollentries import SE_ListGroupCore
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.fontconst import DEFAULT_FONTSIZE, DEFAULT_LETTERSPACE, DEFAULT_UPPERCASE
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.text.color import TextColor
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.stringManip import GetAsUnicode
from carbonui.util.various_unsorted import GetAttrs, GetWindowAbove, SortListOfTuples
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.themeColored import LineThemeColored
from eve.common.lib import appConst as const
from eveexceptions import ExceptionEater
from menu import MenuLabel
from signals import Signal
log = logging.getLogger(__name__)
MINCOLUMNWIDTH = 24
VERSION = uiconst.SCROLLVERSION
TABMARGIN = uiconst.LABELTABMARGIN
MAIN_CONTAINER_PADDING = 0
PRIMARY_COLUMN = 'primaryColumn_%s'
SMART_SORT_DIRECTION = 'smartSortDirection_%s'

def SmartCompare(x, y, sortOrder):
    for column, direction in sortOrder:
        if direction == SortDirection.ASCENDING:
            if x[0][column] > y[0][column]:
                return 1
            if x[0][column] < y[0][column]:
                return -1
        elif direction == SortDirection.DESCENDING:
            if x[0][column] < y[0][column]:
                return 1
            if x[0][column] > y[0][column]:
                return -1
        else:
            raise ValueError('Unknown sort direction')

    return 0


class Scroll(Container):
    default_name = 'scroll'
    default_multiSelect = 1
    default_stickToBottom = 0
    default_smartSort = 0
    default_id = None
    default_state = uiconst.UI_NORMAL
    default_discardNonVisibleNodes = False
    default_columnWidth = {}
    default_hasUnderlay = False
    default_rowPadding = 0
    default_shouldAddFinalRowPadding = True
    default_innerPadding = (0, 0, 0, 0)
    default_pushContent = True
    default_cursor = uiconst.UICURSOR_DEFAULT
    default_headerFontSize = fontconst.EVE_SMALL_FONTSIZE
    scrollEnabled = True
    sortGroups = False
    reverseGroupSortEnabled = False
    entriesTotalHeight = 0
    dragHoverScrollSpeed = 1.0
    dragHoverScrollAreaSize = 30
    isLinelessScroll = True
    tabMargin = TABMARGIN
    _scrollbar_vertical = None
    _suppress_scroll_vertical_update = False

    def ApplyAttributes(self, attributes):
        self._innerPadding = self._sanitize_inner_padding_value(attributes.get('innerPadding', self.default_innerPadding))
        self._pushContent = attributes.get('pushContent', self.default_pushContent)
        self.headerFontSize = attributes.get('headerFontSize', self.default_headerFontSize)
        Container.ApplyAttributes(self, attributes)
        self.sr.maincontainer = Container(parent=self, name='maincontainer', padding=MAIN_CONTAINER_PADDING, clipChildren=True)
        self.sr.scrollHeaders = Container(name='scrollHeaders', parent=self.sr.maincontainer, height=18, state=uiconst.UI_HIDDEN, align=uiconst.TOTOP)
        self.sr.clipper = Container(name='__clipper', align=uiconst.TOALL, parent=self.sr.maincontainer, padding=self._get_clipper_padding(), clipChildren=True)
        self.sr.clipper._OnSizeChange_NoBlock = self.OnClipperResize
        self.sr.content = Container(name='__content', align=uiconst.RELATIVE, parent=self.sr.clipper, state=uiconst.UI_NORMAL)
        self.Release()
        self.multiSelect = attributes.get('multiSelect', self.default_multiSelect)
        self.stickToBottom = attributes.get('stickToBottom', self.default_stickToBottom)
        self.discardNonVisibleNodes = attributes.get('discardNonVisibleNodes', self.default_discardNonVisibleNodes)
        self.smartSort = attributes.get('smartSort', self.default_smartSort)
        self.sr.id = attributes.get('id', self.default_id)
        self.loadingWheel = None
        self.hasUnderlay = attributes.get('hasUnderlay', self.default_hasUnderlay)
        self.rowPadding = attributes.get('rowPadding', self.default_rowPadding)
        self.shouldAddFinalRowPadding = attributes.get('shouldAddFinalRowPadding', self.default_shouldAddFinalRowPadding)
        self.on_content_resize = Signal('on_content_resize')
        self.sr.selfProxy = weakref.proxy(self)
        self.Prepare_()
        self._mouseHoverCookie = uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEHOVER, self.OnGlobalMouseHover)

    @property
    def innerPadding(self):
        return self._innerPadding

    @innerPadding.setter
    def innerPadding(self, value):
        value = self._sanitize_inner_padding_value(value)
        if self._innerPadding != value:
            self._innerPadding = value
            self._update_clipper_padding()

    def _sanitize_inner_padding_value(self, value):
        if value is None:
            value = self.default_innerPadding
        if isinstance(value, int):
            value = (value,
             value,
             value,
             value)
        return value

    def _get_clipper_padding(self):
        inner_pad_left, _, inner_pad_right, _ = self._innerPadding
        return (inner_pad_left,
         0,
         inner_pad_right,
         0)

    def _update_clipper_padding(self):
        self.sr.clipper.padding = self._get_clipper_padding()

    def Close(self, *args):
        with ExceptionEater('Closing a Scroll'):
            uicore.uilib.UnregisterForTriuiEvents(self._mouseHoverCookie)
        super(Scroll, self).Close()

    def OnGlobalMouseHover(self, obj, *args):
        if uicore.IsDragging() and (obj == self or obj.IsUnder(self.sr.content)):
            l, t, w, h = self.GetAbsolute()
            if self.IsScrollbarVisible():
                y = uicore.uilib.y - t
                if y <= self.dragHoverScrollAreaSize:
                    self.Scroll(self.dragHoverScrollSpeed)
                elif y > h - self.dragHoverScrollAreaSize:
                    self.Scroll(-self.dragHoverScrollSpeed)
        return True

    def IsScrollbarVisible(self):
        return self._scrollbar_vertical and self._scrollbar_vertical.display

    def Prepare_(self):
        self.Prepare_Underlay_()
        self.Prepare_ScrollControls_()

    def Prepare_Underlay_(self):
        if getattr(self, 'hasUnderlay', self.default_hasUnderlay):
            self.sr.underlay = PanelUnderlay(parent=self, name='background')

    def Prepare_ScrollControls_(self):
        self.noResultsContainer = None
        self.noResultsLabel = None
        self._scrollbar_vertical = Scrollbar(parent=self.sr.maincontainer, align=uiconst.TORIGHT, axis=Axis.VERTICAL, padLeft=8 if self._pushContent else 0, on_scroll_fraction_changed=self._on_scroll_fraction_vertical_changed, idx=0)
        self._scrollbar_vertical.display = False

    def _on_scroll_fraction_vertical_changed(self, scrollbar):
        with self.suppress_scroll_vertical_update():
            self.ScrollToProportion(proportion=scrollbar.scroll_fraction, threaded=False)

    @contextlib.contextmanager
    def suppress_scroll_vertical_update(self):
        self._suppress_scroll_vertical_update = True
        try:
            yield
        finally:
            self._suppress_scroll_vertical_update = False

    def RemoveActiveFrame(self, *args):
        pass

    def HideBackground(self, alwaysHidden = 0):
        if getattr(self, 'hasUnderlay', self.default_hasUnderlay):
            self.sr.underlay.state = uiconst.UI_HIDDEN
        if alwaysHidden:
            self.SetNoBackgroundFlag(alwaysHidden)

    HideUnderLay = HideBackground

    def SetNoBackgroundFlag(self, hide = 0):
        self.hideBackground = hide

    def Release(self):
        self.isTabStop = 1
        self._loading = 0
        self._position = 0
        self._totalHeight = 0
        self._fixedEntryHeight = None
        self._customColumnWidths = None
        self.sr.scaleLine = None
        self.sr.headers = []
        self.sr.widthToHeaders = {}
        self.sr.tabs = []
        self.sr.nodes = []
        self.visibleNodes = []
        self.sr.overlays = []
        self.sr.underlays = []
        self.sr.fixedColumns = {}
        self.stretchLastHeader = False
        self.sr.maxDefaultColumns = {}
        self.sr.minColumnWidth = {}
        self.sr.defaultColumnWidth = self.default_columnWidth
        self.sr.ignoreTabTrimming = 0
        self.showColumnLines = True
        self.sr.id = None
        self.sortBy = None
        self.sr.iconMargin = 0
        self.sr.hint = None
        self.scrollingRange = 0
        self.hiliteSorted = 1
        self.reversedSort = 0
        self.debug = 0
        self.scrolling = 0
        self.scalingcol = 0
        self.refreshingColumns = 0
        self.lastDrawnColumns = None
        self.allowFilterColumns = 0
        self.lastSelected = None
        self.lastHeaders = None
        self.bumpHeaders = 1
        self.slimHeaders = 0
        self.newColumns = 0
        self.trimFast = 0
        self.refs = []
        self.lastCharReceivedAt = 0
        self.currChars = ''
        self.hideBackground = False
        self._ignoreSort = 0
        self._showCollapseIcon = False
        self._columnOffset = 0
        self._pendingPositionUpdate = None
        self.loopThread = None

    def GetVisibleNodes(self):
        if self.visibleNodes:
            return self.visibleNodes
        return self.sr.nodes

    def HasUnderlay(self):
        return hasattr(self.sr, 'underlay') and self.sr.underlay is not None

    def OnSetFocus(self, *args):
        if self and not self.destroyed and self.parent and self.parent.name == 'inlines':
            if self.parent.parent and self.parent.parent.sr.node:
                self.parent.parent.sr.node.scroll.ShowNodeIdx(self.parent.parent.sr.node.idx)
        if self.HasUnderlay() and hasattr(self.sr.underlay, 'AnimEntry'):
            self.sr.underlay.AnimEntry()

    def OnKillFocus(self, *args):
        if self.HasUnderlay() and hasattr(self.sr.underlay, 'AnimExit'):
            self.sr.underlay.AnimExit()

    def _show_header_resizer_hints(self):
        header_class = self.GetScrollHeaderClass()
        for child in self.sr.innerScrollHeaders.children:
            if isinstance(child, header_class):
                child.show_resizer_hint()

    def _hide_header_resizer_hints(self):
        header_class = self.GetScrollHeaderClass()
        for child in self.sr.innerScrollHeaders.children:
            if isinstance(child, header_class):
                child.hide_resizer_hint()

    def DrawHeaders(self, headers, tabs = []):
        self.sr.scrollHeaders.state = uiconst.UI_HIDDEN
        self.sr.scrollHeaders.Flush()
        self.sr.innerScrollHeaders = Container(name='innerScrollHeaders', parent=self.sr.scrollHeaders, clipChildren=True)
        self.sr.innerScrollHeaders.OnMouseEnter = lambda *args: self._show_header_resizer_hints()
        self.sr.innerScrollHeaders.OnMouseExit = lambda *args: self._hide_header_resizer_hints()
        for each in self.sr.clipper.children[:]:
            if each.name == '__columnLine':
                each.Close()
            if each.name == '__columnFill':
                each.Close()

        self.lastDrawnColumns = None
        self.sr.widthToHeaders = {}
        if not (headers and tabs and len(headers) == len(tabs)):
            self.sr.headers = []
            self.sr.tabs = []
            return
        if not self.sr.nodes:
            return
        self.sr.scrollHeaders.state = uiconst.UI_NORMAL
        self.sr.scrollHeaders.SetOrder(0)
        if not self.isLinelessScroll:
            LineThemeColored(parent=self.sr.scrollHeaders, align=uiconst.TOBOTTOM, opacity=uiconst.OPACITY_FRAME, idx=0)
        columnOffsetToUse = self.GetEffectiveColumnOffset()
        if self._showCollapseIcon:
            self.AddCollapseBtn()
        elif columnOffsetToUse:
            self.sr.innerScrollHeaders.padLeft = columnOffsetToUse
        i = 0
        totalWidth = 0
        maxTextHeight = 0
        headerClass = self.GetScrollHeaderClass()
        half_scale_handle_width = int(round(headerClass.SCALE_HANDLE_SIZE / 2.0))
        for header in headers:
            width = self.sr.fixedColumns.get(header, None)
            if width is None:
                if len(headers) == 1:
                    width = 128
                else:
                    width = tabs[i]
                    if i > 0:
                        width = width - tabs[i - 1]
            if self.smartSort:
                selected = self.GetPrimaryColumn() == header
                sortdir = self.GetSmartSortDirection(header)
            else:
                selected = self.sortBy == header
                sortdir = SortDirection.from_legacy_reversed_sort(self.GetSortDirection()) if selected else SortDirection.ASCENDING
            scalable = self.sr.id and header not in self.sr.fixedColumns and (not self.stretchLastHeader or header != headers[-1])
            self.sr.widthToHeaders[header] = totalWidth
            headerparent = headerClass(column_id=header, name=header, parent=self.sr.innerScrollHeaders, align=uiconst.TOLEFT, left=-half_scale_handle_width if i > 0 else 0, width=width + half_scale_handle_width, tab_margin=self.tabMargin, state=uiconst.UI_NORMAL, text=header, direction=sortdir, selected=selected, on_click=lambda _header = header: self.ChangeSortBy(_header), on_double_click=lambda _header = header: self.ResetColumnWidth(_header), get_menu=lambda _header = header: self.GetHeaderMenu(_header), scalable=scalable, on_scale_start=self._on_column_scale_start)
            headerparent.on_scale_move = lambda column = header, element = headerparent: self._on_column_scale_move(column, element)
            headerparent.on_scale_end = lambda column = header, element = headerparent: self._on_column_scale_end(column, element)
            if self.stretchLastHeader and header == headers[-1]:
                headerparent.align = uiconst.TOALL
                headerparent.width = 0
            totalWidth += width
            if not (self.smartSort or self.allowFilterColumns):
                headerparent.GetMenu = None
            maxTextHeight = max(maxTextHeight, headerparent.GetHeaderHeight())
            if not self.isLinelessScroll and headerparent.align != uiconst.TOALL and not self.sr.ignoreTabTrimming and self.sr.nodes and self.showColumnLines:
                self.BuildColumnLine(columnOffsetToUse, totalWidth, width, headerparent)
            i += 1

        self.sr.scrollHeaders.height = maxTextHeight
        self.lastDrawnColumns = headers

    def BuildColumnLine(self, columnOffsetToUse, totalWidth, headerWidth, headerparent):
        line = LineThemeColored(parent=self.sr.clipper, align=uiconst.RELATIVE, name='__columnLine', opacity=uiconst.OPACITY_FRAME)
        line.width = 1
        line.height = uicore.desktop.height
        line.top = 1
        lineLeft = totalWidth - 1
        line.originalLeft = lineLeft
        line.left = lineLeft + columnOffsetToUse

    def BuildColumnFill(self, columnOffsetToUse, totalWidth, headerWidth, headerparent):
        lineLeft = totalWidth - headerWidth + columnOffsetToUse
        columnFill = Frame(parent=self.sr.clipper, align=uiconst.RELATIVE, name='__columnFill', opacity=0.1, frameConst=uiconst.FRAME_FILLED_CORNER0, color=(0.94, 0.94, 0.94, 1.0), pos=(lineLeft,
         0,
         headerWidth,
         uicore.desktop.height))
        columnFill.originalLeft = lineLeft
        headerFrame = Frame(parent=headerparent, align=uiconst.TOALL, name='__columnFill', opacity=0.1, frameConst=uiconst.FRAME_FILLED_CORNER5, idx=0, color=(0.94, 0.94, 0.94, 1.0), padBottom=-10)
        headerparent.sr.headerFrame = headerFrame

    def GetScrollHeaderClass(self):
        return ColumnHeader

    def UpdateColumnLines(self):
        columnOffsetToUse = self.GetEffectiveColumnOffset()
        for each in self.sr.clipper.children:
            if each.name == '__columnLine':
                left = getattr(each, 'originalLeft', each.left)
                each.left = left + columnOffsetToUse
            elif each.name == '__columnFill':
                left = getattr(each, 'originalLeft', each.left)
                each.left = left + columnOffsetToUse

    def ShowHint(self, hint = None, labelClass = EveCaptionLarge):
        if not hint:
            if self.noResultsContainer:
                self.noResultsContainer.Hide()
            return
        center_hint = '<center>%s</center>' % hint
        isNew = self.noResultsLabel is None or self.noResultsLabel.GetText() != center_hint
        if self.noResultsContainer is None:
            self.ConstructNoResultsContainer(center_hint, labelClass)
        self.noResultsLabel.SetText(center_hint)
        self.noResultsContainer.SetState(uiconst.UI_DISABLED)
        if isNew:
            animations.FadeTo(self.noResultsContainer, 0.0, 1.0, duration=0.3)

    def ConstructNoResultsContainer(self, center_hint, labelClass):
        self.noResultsContainer = Container(name='noResultsContainer', parent=self.sr.clipper, align=uiconst.TOALL)
        cont = ContainerAutoSize(name='cont', parent=self.noResultsContainer, align=uiconst.TOTOP)
        self.noResultsLabel = labelClass(name='noResultsLabel', parent=cont, align=uiconst.TOTOP, text=center_hint, autoFitToText=True, padding=16, color=TextColor.SECONDARY)

    def _on_column_scale_start(self):
        self.scalingcol = uicore.uilib.x
        if self.sr.scaleLine is not None:
            self.sr.scaleLine.Close()
        self.ContructScaleLine()

    def ContructScaleLine(self):
        l, t, w, h = self.GetAbsolute()
        self.sr.scaleLine = LineThemeColored(parent=self, align=uiconst.TOPLEFT, pos=(uicore.uilib.x - l - 1,
         1,
         2,
         h), idx=0, opacity=uiconst.OPACITY_FRAME)

    def _on_column_scale_move(self, column, element):
        l, t, w, h = self.GetAbsolute()
        element_left, _ = element.GetCurrentAbsolutePosition()
        minColumnWidth = self.sr.minColumnWidth.get(column, MINCOLUMNWIDTH)
        if self.scalingcol and self.sr.scaleLine:
            self.sr.scaleLine.left = mathext.clamp(value=uicore.uilib.x - l - 2, low=element_left - l + minColumnWidth, high=w - minColumnWidth)

    def _on_column_scale_end(self, column, element):
        if self.sr.scaleLine is not None:
            if self.sr.id and self.scalingcol != uicore.uilib.x:
                currentSettings = settings.user.ui.Get('columnWidths_%s' % VERSION, {})
                currentSettings.setdefault(self.sr.id, {})
                currentWidth = element.width
                minColumnWidth = self.sr.minColumnWidth.get(column, MINCOLUMNWIDTH)
                if self.sr.scaleLine:
                    l, t, w, h = self.GetAbsolute()
                    newLeft = self.sr.scaleLine.left + l
                else:
                    newLeft = uicore.uilib.x
                diff = newLeft - self.scalingcol
                newWidth = currentWidth + diff
                currentSettings[self.sr.id][column] = max(minColumnWidth, newWidth)
                settings.user.ui.Set('columnWidths_%s' % VERSION, currentSettings)
                uthread.pool('VirtualScroll::EndScaleCol-->UpdateTabStops', self.UpdateTabStops, 'EndScaleCol')
            scaleLine = self.sr.scaleLine
            self.sr.scaleLine = None
            scaleLine.Close()
        self.scalingcol = 0

    def OnColumnChanged(self, *args):
        pass

    def OnNewHeaders(self, *args):
        pass

    def ShowNodeIdx(self, idx, threadedScrolling = True):
        if self.scrollingRange:
            node = self.GetNode(idx)
            fromTop = node.scroll_positionFromTop
            if fromTop is None:
                return
            if self._position > fromTop:
                portion = fromTop / float(self.scrollingRange)
                self.ScrollToProportion(portion, threaded=threadedScrolling)
            clipperWidth, clipperHeight = self.GetContentParentSize()
            nodeHeight = self.GetNodeHeight(node, clipperWidth)
            if self._position + clipperHeight < fromTop + nodeHeight:
                portion = (fromTop - clipperHeight + nodeHeight) / float(self.scrollingRange)
                self.ScrollToProportion(portion, threaded=threadedScrolling)

    def GetNodes(self, allowNone = False):
        ret = []
        for each in self.sr.nodes:
            if each.internalNodes:
                if allowNone:
                    ret += each.internalNodes
                else:
                    for internal in each.internalNodes:
                        if internal:
                            ret.append(internal)

            else:
                ret.append(each)

        return ret

    def SetSelected(self, idx):
        node = self.GetNode(idx)
        if node:
            self.SelectNode(node)
        self.ReportSelectionChange()

    def ActivateIdx(self, idx):
        node = self.GetNode(min(idx, len(self.GetNodes()) - 1))
        if node:
            self.SelectNode(node)
            self.ShowNodeIdx(node.idx)
        else:
            self.ReportSelectionChange()

    def _SelectNode(self, node):
        if getattr(node, 'selectable', 1) == 0:
            return
        node.selected = 1
        self.UpdateSelection(node)

    def _DeselectNode(self, node):
        node.selected = 0
        self.UpdateSelection(node)

    def SelectNodes(self, nodeList):
        self.DeselectAll()
        for node in nodeList:
            self._SelectNode(node)

        self.ReportSelectionChange()

    def SelectNode(self, node, multi = 0, subnode = None, checktoggle = 1):
        control = uicore.uilib.Key(uiconst.VK_CONTROL)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        selected = node.get('selected', 0)
        if not self.multiSelect:
            self.DeselectAll(0)
            if control:
                if not selected:
                    self._SelectNode(node)
            else:
                self._SelectNode(node)
        elif not control and not shift:
            self.DeselectAll(0)
            self._SelectNode(node)
        elif control and not shift:
            if not selected:
                self._SelectNode(node)
            else:
                self._DeselectNode(node)
        elif not control and shift:
            if self.lastSelected is not None and self.lastSelected != node.idx:
                self.DeselectAll(0)
                r = [self.lastSelected, node.idx]
                r.sort()
                for i in xrange(r[0], r[1] + 1):
                    _node = self.GetNode(i, checkInternalNodes=True)
                    if _node:
                        self._SelectNode(_node)

                self.ReportSelectionChange()
                return
            self.DeselectAll(0)
            self._SelectNode(node)
        elif control and shift:
            if self.lastSelected is not None and self.lastSelected != node.idx:
                r = [self.lastSelected, node.idx]
                r.sort()
                for i in xrange(r[0], r[1] + 1):
                    _node = self.GetNode(i, checkInternalNodes=True)
                    if _node:
                        self._SelectNode(_node)

        else:
            self.DeselectAll(0)
            self._SelectNode(node)
        self.lastSelected = node.idx
        self.ReportSelectionChange()

    def ReportSelectionChange(self):
        self.OnSelectionChange(self.GetSelected())

    def OnSelectionChange(self, *args):
        pass

    def DeselectAll(self, report = 1, *args):
        for node in self.GetNodes():
            node.selected = 0
            self.UpdateSelection(node)

        if report:
            self.ReportSelectionChange()

    def SelectAll(self, *args):
        if not self.multiSelect:
            return
        for node in self.GetNodes():
            if getattr(node, 'selectable', 1) == 0:
                continue
            node.selected = 1
            self.UpdateSelection(node)

        self.ReportSelectionChange()

    def ToggleSelected(self, *args):
        for node in self.GetNodes():
            node.selected = not node.get('selected', 0)
            self.UpdateSelection(node)

        self.ReportSelectionChange()

    def UpdateSelection(self, node):
        if node.panel:
            if node.panel.sr.selection:
                node.panel.sr.selection.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][node.selected]
            elif node.selected and hasattr(node.panel, 'Select'):
                node.panel.Select()
            elif not node.selected and hasattr(node.panel, 'Deselect'):
                node.panel.Deselect()

    def ClearSelection(self, *args):
        for node in self.GetNodes():
            node.selected = 0
            self.UpdateSelection(node)

        self.lastSelected = None
        self.ReportSelectionChange()

    def GetSelectedNodes(self, node, toggle = 0):
        if not node.get('selected', 0) or toggle:
            self.SelectNode(node)
        sel = []
        for each in self.GetNodes():
            if each.get('selected', 0):
                sel.append(each)

        return sel

    def GetSelected(self):
        sel = []
        for each in self.GetNodes():
            if each.get('selected', 0):
                sel.append(each)

        return sel

    def GetSortBy(self):
        if self.smartSort:
            return None
        if self.sr.id:
            pr = settings.user.ui.Get('scrollsortby_%s' % VERSION, {})
            if self.sr.id in pr:
                return pr[self.sr.id][0]
        return self.sortBy

    def GetSortDirection(self):
        if self.sr.id:
            pr = settings.user.ui.Get('scrollsortby_%s' % VERSION, {})
            if self.sr.id in pr:
                return pr[self.sr.id][1]
        return self.reversedSort

    def GetSmartSortDirection(self, column, default = SortDirection.ASCENDING):
        if self.sr.id and self.smartSort:
            pr = settings.user.ui.Get(SMART_SORT_DIRECTION % VERSION, {})
            if self.sr.id in pr:
                return pr[self.sr.id].get(column, default)
        return default

    def ToggleSmartSortDirection(self, column):
        if self.sr.id and self.smartSort:
            direction_current = self.GetSmartSortDirection(column)
            direction_new = SortDirection.flip(direction_current)
            pr = settings.user.ui.Get(SMART_SORT_DIRECTION % VERSION, {})
            if self.sr.id not in pr:
                pr[self.sr.id] = {}
            pr[self.sr.id][column] = direction_new
            settings.user.ui.Set(SMART_SORT_DIRECTION % VERSION, pr)

    def GetSortValue(self, by, node, idx = None):
        if getattr(node, 'sortValues', None):
            return node.sortValues[idx]
        if getattr(node, 'GetSortValue', None):
            return node.GetSortValue(node, by, self.GetSortDirection(), idx=idx)
        ret = self._GetSortValue(by, node, idx)
        return StripTags(ret, stripOnly=['localized'])

    def _GetSortValue(self, by, node, idx):
        val = node.Get('sort_' + by, None)
        if val is None:
            val = node.Get('sort_' + by.replace('<br>', ' '), None)
        if val is not None:
            try:
                val = val.lower()
            except:
                sys.exc_clear()

            return val
        if idx is not None:
            strings = self.GetStringFromNode(node).split('<t>')
            if len(strings) > idx:
                value = strings[idx].lower()
                try:
                    value = uicore.font.DeTag(value)
                    isAU = value.find('au') != -1
                    isKM = value.find('km') != -1
                    value = float(value.replace('m\xef\xbf\xbd', '').replace('isk', '').replace('km', '').replace('au', '').replace(',', '').replace(' ', '').replace('m3', ''))
                    if isAU:
                        value *= const.AU
                    elif isKM:
                        value *= 1000
                    return value
                except Exception:
                    sys.exc_clear()
                    rest = ''.join(strings[idx + 1:])
                    return value + rest

            return 'aaa'
        val = node.Get(by, '-')
        try:
            val = val.lower()
        except:
            sys.exc_clear()

        return val

    def GetContentContainer(self):
        return self.sr.content

    def GetColumns(self):
        if self.sr.id and (self.smartSort or self.allowFilterColumns):
            if not self.sr.headers:
                return []
            orderedColumns = settings.user.ui.Get('columnOrder_%s' % VERSION, {}).get(self.sr.id, self.sr.headers)
            notInOrdered = [ header for header in self.sr.headers if header not in orderedColumns ]
            headers = [ header for header in orderedColumns + notInOrdered if header in self.sr.headers ]
            hiddenColumnsKey = GetHiddenColumnsKey(self.sr.id)
            hiddenColumns = settings.user.ui.Get('filteredColumns_%s' % VERSION, {}).get(hiddenColumnsKey, [])
            allHiddenColumns = hiddenColumns + settings.user.ui.Get('filteredColumnsByDefault_%s' % VERSION, {}).get((hiddenColumnsKey, session.languageID), [])
            filterColumns = filter(lambda x: x not in allHiddenColumns, headers)
            return filterColumns
        else:
            return self.sr.headers

    def GetHeaderMenu(self, label):
        m = []
        if self.smartSort:
            m += [(MenuLabel('/Carbon/UI/Commands/CmdMakePrimary'), self.MakePrimary, (label,))]
        if self.smartSort or self.allowFilterColumns:
            if len(self.GetColumns()) > 1:
                m += [(MenuLabel('/Carbon/UI/Common/Hide', {'label': label}), self.HideColumn, (label,))]
            m += self.GetShowColumnMenu()
        return m

    def GetShowColumnMenu(self):
        m = []
        for label in self.sr.headers:
            if label not in self.GetColumns():
                m.append((MenuLabel('/Carbon/UI/Common/Show', {'label': label}), self.ShowColumn, (label,)))

        if m:
            m.insert(0, None)
        return m

    def MakePrimary(self, label, update = 1):
        all = settings.user.ui.Get(PRIMARY_COLUMN % VERSION, {})
        all[self.sr.id] = label
        settings.user.ui.Set(PRIMARY_COLUMN % VERSION, all)
        if update:
            self.ChangeColumnOrder(label, 0)

    def GetPrimaryColumn(self):
        return settings.user.ui.Get(PRIMARY_COLUMN % VERSION, {}).get(self.sr.id, None)

    def SetColumnsHiddenByDefault(self, columns, *args):
        if self.sr.id:
            filteredByDefault = settings.user.ui.Get('filteredColumnsByDefault_%s' % VERSION, {})
            key = GetHiddenColumnsKey(self.sr.id)
            idWithLanguage = (key, session.languageID)
            if idWithLanguage not in filteredByDefault:
                filteredByDefault[idWithLanguage] = columns
                settings.user.ui.Set('filteredColumnsByDefault_%s' % VERSION, filteredByDefault)

    def HideColumn(self, label):
        if self.sr.id:
            filtered = settings.user.ui.Get('filteredColumns_%s' % VERSION, {})
            key = GetHiddenColumnsKey(self.sr.id)
            if key not in filtered:
                filtered[key] = []
            if label not in filtered[key]:
                filtered[key].append(label)
            settings.user.ui.Set('filteredColumns_%s' % VERSION, filtered)
            self.OnColumnChanged(None)
            self.OnNewHeaders()

    def ShowColumn(self, label):
        if self.sr.id:
            key = GetHiddenColumnsKey(self.sr.id)
            filtered = settings.user.ui.Get('filteredColumns_%s' % VERSION, {})
            if key in filtered and label in filtered[key]:
                filtered[key].remove(label)
            filteredByDefault = settings.user.ui.Get('filteredColumnsByDefault_%s' % VERSION, {})
            idWithLanguage = (key, session.languageID)
            if idWithLanguage in filteredByDefault and label in filteredByDefault[idWithLanguage]:
                filteredByDefault[idWithLanguage].remove(label)
                settings.user.ui.Set('filteredColumnsByDefault_%s' % VERSION, filteredByDefault)
            settings.user.ui.Set('filteredColumns_%s' % VERSION, filtered)
            self.OnColumnChanged(None)
            self.OnNewHeaders()

    @telemetry.ZONE_METHOD
    def Sort(self, by = None, reversesort = 0, forceHilite = 0):
        if self.smartSort:
            self._SmartSort()
        else:
            self._Sort(by, reversesort)
            if self.sortBy != by or forceHilite:
                self.HiliteSorted(by, reversesort)
                self.sortBy = by

    def _Sort(self, by = None, reversesort = 0):
        idx = None
        headers = self.GetColumns()
        if by in headers:
            idx = headers.index(by)
        endOrder = []
        self.SortAsRoot(self.sr.nodes, endOrder, by, idx, reversesort)
        self.SetNodes(endOrder)
        self.UpdatePosition(fromWhere='Sort')

    def _SmartSort(self):
        columns = self.GetColumns()
        primary = self.GetPrimaryColumn()
        sortcolumns = columns[:]
        if primary in columns:
            idx = columns.index(primary)
            sortcolumns = columns[idx:]
        if columns:
            sortData = []
            rm = []
            for node in self.sr.nodes:
                nodeData = []
                idx = 0
                for header in columns:
                    if header not in sortcolumns:
                        continue
                    if idx in rm:
                        value = 0
                    else:
                        value = node.Get('sort_%s' % header, None)
                        if value is None:
                            log.warning('Cannot find sortvalue for column %s in scroll %s', header, self.sr.id)
                            rm.append(idx)
                            value = 0
                        else:
                            try:
                                value = value.lower()
                            except:
                                sys.exc_clear()

                    idx += 1
                    nodeData.append(value)

                sortData.append([nodeData, node])

            sortOrder = [ (idx, self.GetSmartSortDirection(header)) for idx, header in enumerate(sortcolumns) if idx not in rm ]
            sortData.sort(lambda x, y, sortOrder = sortOrder: SmartCompare(x, y, sortOrder))
            self.SetNodes([ each[1] for each in sortData ])
            self.UpdatePositionThreaded(fromWhere='Sort(Smart)')

    @telemetry.ZONE_METHOD
    def SortAsRoot(self, nodes, endOrder, columnName, columnIndex, reversedSorting = 0, groupIndex = None):
        groups = []
        rootSortList_Groups = []
        rootSortList_NotGroups = []
        for node in nodes:
            if groupIndex is None and node.isSub:
                continue
            val = self.GetSortValue(columnName, node, columnIndex)
            val = (val, self.GetStringFromNode(node).lower())
            if issubclass(node.decoClass, SE_ListGroupCore) or getattr(node, 'isListEntry', False):
                rootSortList_Groups.append((val, node))
            else:
                rootSortList_NotGroups.append((val, node))

        if self.sortGroups:
            rootSortList_Groups = SortListOfTuples(rootSortList_Groups)
        else:
            rootSortList_Groups = [ node for val, node in rootSortList_Groups ]
        rootSortList_NotGroups = SortListOfTuples(rootSortList_NotGroups)
        if reversedSorting:
            rootSortList_NotGroups.reverse()
            if self.reverseGroupSortEnabled:
                rootSortList_Groups.reverse()
        combinedGroupsAndOthers = rootSortList_Groups + rootSortList_NotGroups
        if groupIndex is not None:
            for subIndex, subNode in enumerate(combinedGroupsAndOthers):
                endOrder.insert(groupIndex + subIndex + 1, subNode)

        else:
            endOrder.extend(combinedGroupsAndOthers)
        if rootSortList_Groups:
            for groupNode in rootSortList_Groups:
                groupIdx = endOrder.index(groupNode)
                subNodes = groupNode.get('subNodes', [])
                self.SortAsRoot(subNodes, endOrder, columnName, columnIndex, reversedSorting, groupIndex=groupIdx)

        return nodes

    def GetStringFromNode(self, node):
        label_or_text = node.get('label', '') or node.get('text', '')
        return GetAsUnicode(label_or_text)

    def RefreshSort(self, forceHilite = 0):
        if self.smartSort:
            self.Sort()
        else:
            sortby = self.GetSortBy()
            if sortby is not None:
                self.Sort(sortby, self.GetSortDirection(), forceHilite=forceHilite)

    def ChangeSortBy(self, by, *args):
        if self.smartSort:
            old_primary = self.GetPrimaryColumn()
            if old_primary == by:
                self.ToggleSmartSortDirection(by)
            self.MakePrimary(by, 0)
            for header in self.GetHeadersChildren():
                if not self.IsExepectedColumnHeader(header):
                    continue
                if header.id == by:
                    header.select(direction=self.GetSmartSortDirection(header.id))
                else:
                    header.deselect()

            self.Sort()
        else:
            if self.sortBy == by:
                self.reversedSort = not self.reversedSort
            else:
                self.reversedSort = False
            self.sortBy = by
            if self.sr.id:
                pr = settings.user.ui.Get('scrollsortby_%s' % VERSION, {})
                pr[self.sr.id] = (self.sortBy, self.reversedSort)
                settings.user.ui.Set('scrollsortby_%s' % VERSION, pr)
            self.RefreshSort(1)

    def ChangeColumnOrder(self, column, toIdx):
        if self.sr.id and self.smartSort:
            all = settings.user.ui.Get('columnOrder_%s' % VERSION, {})
            currentOrder = all.get(self.sr.id, self.sr.headers)[:]
            if column in currentOrder:
                currentOrder.remove(column)
            currentOrder.insert(toIdx, column)
            all[self.sr.id] = currentOrder
            settings.user.ui.Set('columnOrder_%s' % VERSION, all)
            self.OnColumnChanged(None)
            self.OnNewHeaders()

    def HiliteSorted(self, by, rev, *args):
        selectedHeaderIdx = None
        totalWidth = 0
        for i, header in enumerate(self.GetHeadersChildren()):
            if not self.IsExepectedColumnHeader(header):
                continue
            header.deselect()
            header.direction = SortDirection.ASCENDING
            if self.hiliteSorted and header.id == by:
                header.select(direction=SortDirection.from_legacy_reversed_sort(rev))
                selectedHeaderIdx = i
            totalWidth += header.width

    def IsExepectedColumnHeader(self, header):
        return isinstance(header, ColumnHeader)

    def GetHeadersChildren(self):
        if self.sr.innerScrollHeaders and not self.sr.innerScrollHeaders.destroyed:
            return self.sr.innerScrollHeaders.children
        return []

    def Clear(self):
        self.visibleNodes = []
        self.LoadContent()

    def ReloadNodes(self, *args, **kwargs):
        for node in self.GetNodes():
            self.PrepareSubContent(node, threadedUpdate=False)
            if node.panel:
                node.panel.Load(node)

    @telemetry.ZONE_METHOD
    def LoadContent(self, fixedEntryHeight = None, contentList = [], sortby = None, reversesort = None, headers = [], scrollTo = None, customColumnWidths = False, showScrollTop = False, noContentHint = '', ignoreSort = False, scrolltotop = False, keepPosition = False, showCollapseIcon = False):
        if self.destroyed:
            return
        if scrolltotop:
            scrollTo = 0.0
        elif scrollTo is None or keepPosition:
            scrollTo = self.GetScrollProportion()
        self._loading = 1
        self._fixedEntryHeight = fixedEntryHeight
        self._customColumnWidths = customColumnWidths
        self._ignoreSort = ignoreSort
        self._showCollapseIcon = showCollapseIcon
        self._columnOffset = 0
        wnd = GetWindowAbove(self)
        if wnd and not wnd.destroyed and hasattr(wnd, 'ShowLoad'):
            wnd.ShowLoad()
        self.sr.nodes = self.sr.entries = []
        self.sr.content.Flush()
        self._position = self.sr.content.top = 0
        if showScrollTop:
            self._scrollbar_vertical.display = True
        if reversesort is None:
            reversesort = self.GetSortDirection()
        self.sortBy = sortby
        self.reversedSort = reversesort
        self.AddNodes(0, contentList, initing=True)
        if sortby and not ignoreSort:
            self.Sort(sortby, reversesort)
        if self.destroyed:
            return
        if noContentHint and not contentList:
            self.ShowHint(noContentHint)
            self.__LoadHeaders([])
        else:
            self.ShowHint()
            self.__LoadHeaders(headers)
        if self.destroyed:
            return
        self.RefreshNodes(fromWhere='LoadContent')
        self.ScrollToProportion(scrollTo, threaded=False)
        self.UpdateTabStops('LoadContent')
        self.UpdateColumnLines()
        if wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
            wnd.HideLoad()
        self._loading = 0

    Load = LoadContent

    def LoadHeaders(self, headers):
        wnd = GetWindowAbove(self)
        try:
            if self.__LoadHeaders(headers):
                self.OnColumnChanged(self.sr.tabs)
        finally:
            if wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
                wnd.HideLoad()

    @telemetry.ZONE_METHOD
    def __LoadHeaders(self, headers):
        self.sr.headers = headers
        self.UpdateTabStops('__LoadHeaders')
        if self.destroyed:
            return
        if headers:
            if not self.smartSort:
                sortby = self.GetSortBy()
                reversesort = self.GetSortDirection()
                if not sortby or sortby not in headers:
                    sortby = headers[0]
                if not self._ignoreSort:
                    self.Sort(sortby, reversesort)
                else:
                    self.UpdatePositionThreaded(fromWhere='__LoadHeaders')
            else:
                self.Sort()
        if len(self.sr.nodes) or not headers:
            self.lastHeaders = headers
        return 1

    def ResetColumnWidths(self):
        for header in self.GetColumns():
            self.ResetColumnWidth(header)

    def ResetColumnWidth(self, header, onlyReset = 0):
        if self.sr.id is None or self.refreshingColumns:
            return
        if not onlyReset:
            wnd = GetWindowAbove(self)
            if wnd and not wnd.destroyed and hasattr(wnd, 'ShowLoad'):
                wnd.ShowLoad()
        self.refreshingColumns = 1
        if header not in self.sr.fixedColumns and self.sr.id:
            headertab = [(header,
              self.headerFontSize,
              0,
              self.tabMargin,
              False)]
        else:
            headertab = [(header,
              self.headerFontSize,
              0,
              self.tabMargin,
              False)]
        if header in self.GetColumns():
            idx = self.GetColumns().index(header)
            width = None
            if self._customColumnWidths:
                headerWidth = uicore.font.GetTextWidth(header, fontsize=self.headerFontSize, letterspace=0, uppercase=False)
                headerWidth += self.tabMargin * 2
                normHeader = header.replace('<br>', ' ')
                width = max([headerWidth] + [ node.GetColumnWidthFunction(None, node, normHeader) for node in self.sr.nodes if node.get('GetColumnWidthFunction', None) is not None ])
            else:
                tabstops = self.GetTabStops(headertab, idx)
                if len(tabstops):
                    width = max(MINCOLUMNWIDTH, tabstops[0])
            if width is not None:
                current = settings.user.ui.Get('columnWidths_%s' % VERSION, {})
                current.setdefault(self.sr.id, {})[header] = width
                settings.user.ui.Set('columnWidths_%s' % VERSION, current)
                self.UpdateTabStops('ResetColumnWidth')
        if not onlyReset and wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
            wnd.HideLoad()
        self.refreshingColumns = 0

    @telemetry.ZONE_METHOD
    def ApplyTabstopsToNode(self, node, fromWhere = ''):
        if self.sr.ignoreTabTrimming or not self.GetColumns():
            return
        tabStops = self.sr.tabs
        node.tabs = tabStops
        if tabStops and GetAttrs(node, 'panel', 'OnColumnResize'):
            cols = []
            last = 0
            for tab in tabStops:
                cols.append(tab - last)
                last = tab

            cols[0] -= self.sr.maincontainer.left
            node.panel.OnColumnResize(cols)
        elif tabStops and node.panel and node.panel.sr.label:
            label = node.panel.sr.label
            columnOffsetToUse = self.GetEffectiveColumnOffset()
            subTract = label.left - columnOffsetToUse
            if isinstance(label, LabelCore):
                newtext = self.GetStringFromNode(node)
                if newtext and (getattr(label, 'tabs', None) != tabStops or getattr(label, 'xShift', 0) != -subTract) and newtext.find('<t>') != -1:
                    label.xShift = -subTract
                    label.tabs = tabStops
                    label.text = newtext
                    label.Update()

    def GetTabStops(self, headertabs, idx = None):
        strengir = []
        fontsize = fontconst.DEFAULT_FONTSIZE
        letterspace = 0
        shift = 0
        self._columnOffset = 0
        for node in self.sr.nodes:
            if node.Get('GetSubContent', None):
                self._columnOffset = 16
            s = self.GetStrengir(node, fontsize, letterspace, shift, idx)
            if s is None:
                continue
            strengir.append(s)

        return uicore.font.MeasureTabstops(strengir + headertabs, self.tabMargin)

    def GetStrengir(self, node, fontsize, letterspace, shift, idx = None):
        t = self.GetStringFromNode(node)
        if not t or t.find('<t>') == -1:
            return
        if idx is not None:
            t = t.split('<t>')
            if len(t) <= idx:
                return
            t = t[idx]
        if node.panel and node.panel.sr.label:
            label = node.panel.sr.label
            fontsize = label.fontsize
            letterspace = label.letterspace
            shift = label.left
        return (t,
         fontsize,
         letterspace,
         shift,
         0)

    @telemetry.ZONE_METHOD
    def UpdateTabStops(self, fromWhere = None, updatePosition = True):
        headers = self.GetColumns()
        headertabs = []
        if headers is not None and len(headers):
            headertabs = [('<t>'.join(headers),
              self.headerFontSize,
              0,
              self.tabMargin,
              False)]
        tabstops = self.GetTabStops(headertabs)
        if self.sr.id and headers:
            userDefined = settings.user.ui.Get('columnWidths_%s' % VERSION, {}).get(self.sr.id, {})
            i = 0
            columnOffsetToUse = self.GetEffectiveColumnOffset()
            total = columnOffsetToUse
            former = total
            for header in headers:
                if header in self.sr.fixedColumns:
                    stopSize = self.sr.fixedColumns[header]
                else:
                    userSetWidth = userDefined.get(header, None) or self.sr.defaultColumnWidth.get(header, None)
                    minColumnWidth = self.sr.minColumnWidth.get(header, MINCOLUMNWIDTH)
                    if userSetWidth is not None:
                        stopSize = max(userSetWidth, minColumnWidth)
                    else:
                        stopSize = max(tabstops[i] - former, minColumnWidth)
                        if header in self.sr.maxDefaultColumns:
                            stopSize = min(self.sr.maxDefaultColumns.get(header, minColumnWidth), stopSize)
                total += stopSize
                former = tabstops[i]
                tabstops[i] = total
                i += 1

        didChange = tabstops != self.sr.tabs
        self.sr.tabs = tabstops
        if self.sr.collapseCont and not self.sr.collapseCont.destroyed:
            collapseIconNeedsRefresh = False
            columnOffsetToUse = self.GetEffectiveColumnOffset()
            self.sr.collapseCont.display = bool(columnOffsetToUse)
        else:
            collapseIconNeedsRefresh = self._showCollapseIcon
        if headers != self.lastDrawnColumns or didChange or collapseIconNeedsRefresh:
            self.DrawHeaders(headers, tabstops)
            if didChange:
                if not self.smartSort:
                    self.HiliteSorted(self.GetSortBy(), self.GetSortDirection(), 'UpdateTabStops')
                if not self._loading:
                    self.OnColumnChanged(tabstops)
        if updatePosition:
            self.UpdatePositionThreaded('UpdateTabStops')
        return tabstops

    @telemetry.ZONE_METHOD
    def AddNode(self, idx, node, isSub = 0, initing = False):
        if idx == -1:
            idx = len(self.sr.nodes)
        node.panel = None
        node.open = 0
        node.idx = idx
        node.isSub = isSub
        node.scroll = self.sr.selfProxy
        node.selected = node.get('isSelected', 0)
        if node.get('PreLoadFunction', None):
            node.PreLoadFunction(node)
            if self.destroyed:
                return
        self.sr.nodes.insert(idx, node)
        self.PrepareSubContent(node, initing=initing)
        return node

    @telemetry.ZONE_METHOD
    def PrepareSubContent(self, node, initing = False, threadedUpdate = True):
        if node.id:
            if node.get('subNodes', []):
                rm = node.subNodes
                node.subNodes = []
                node.open = 0
                self.RemoveNodes(rm)
            if node.Get('GetSubContent', None) is not None:
                forceOpen = node.get('forceOpen', False) and initing
                if forceOpen or uicore.registry.GetListGroupOpenState(node.id, default=node.get('openByDefault', False)):
                    subcontent = node.GetSubContent(node)
                    if self.destroyed or node not in self.GetNodes():
                        return
                    if not node.Get('hideNoItem', False) and not len(subcontent):
                        noItemText = node.get('noItemText', localization.GetByLabel('/Carbon/UI/Controls/Common/NoItem'))
                        subcontent.append(self.GetNoItemNode(text=noItemText, sublevel=node.get('sublevel', 0) + 1))
                    if not self.destroyed:
                        self.AddNodes(node.idx + 1, subcontent, node, initing=initing, threadedUpdate=threadedUpdate)
                        if node not in self.GetNodes():
                            self.RemoveNodes(subcontent)
                        else:
                            node.subNodes = subcontent
                            node.open = 1
                            return subcontent

    def SetNodes(self, nodes):
        self.sr.nodes = nodes
        self.RefreshNodes()

    def _GetNodePanelName(self, node):
        if getattr(node, 'panelName', None):
            return node.panelName
        return node.name or 'entry_%s' % node.idx

    @telemetry.ZONE_METHOD
    def RefreshNodes(self, fromWhere = None):
        if self.destroyed:
            return
        clipperWidth, clipperHeight = self.sr.clipper.GetCurrentAbsoluteSize()
        if not clipperWidth or not clipperHeight:
            clipperWidth, clipperHeight = self.sr.clipper.GetAbsoluteSize()
        _, inner_pad_top, _, inner_pad_bottom = self._innerPadding
        fromTop = inner_pad_top
        for nodeidx, node in enumerate(self.sr.nodes):
            node.idx = nodeidx
            nodeheight = self.GetNodeHeight(node, clipperWidth)
            node.scroll_positionFromTop = fromTop
            if node.panel:
                node.panel.align = uiconst.TOPLEFT
                node.panel.left = 0
                node.panel.top = fromTop
                node.panel.width = clipperWidth
                node.panel.height = nodeheight
                node.panel.name = self._GetNodePanelName(node)
            fromTop += nodeheight
            if self.shouldAddFinalRowPadding or nodeidx + 1 < len(self.sr.nodes):
                fromTop += self.rowPadding

        for overlay, attrs, x, y in self.sr.overlays + self.sr.underlays:
            fromTop = max(fromTop, attrs.top + attrs.height)

        atBottom = self._position and self._position == self.scrollingRange
        self._totalHeight = fromTop + inner_pad_bottom
        self.scrollingRange = max(0, self._totalHeight - clipperHeight)
        if self.scrollingRange and self.scrollEnabled:
            self._scrollbar_vertical.display = True
        else:
            self._scrollbar_vertical.display = False
        if self.scrollEnabled:
            if not self.scrollingRange or atBottom or self.stickToBottom:
                self._position = self.scrollingRange
            self._position = min(self._position, self.scrollingRange)
        else:
            self._position = 0
        self.UpdateContentSize(clipperWidth, clipperHeight, self._totalHeight)
        if self.sr.overlays_content:
            self.sr.overlays_content.height = self.sr.content.height
            self.sr.overlays_content.width = clipperWidth
        if self.sr.underlays_content:
            self.sr.underlays_content.height = self.sr.content.height
            self.sr.underlays_content.width = clipperWidth

    @telemetry.ZONE_METHOD
    def UpdateContentSize(self, clipperWidth, clipperHeight, contentHeight):
        self.entriesTotalHeight = contentHeight
        self.on_content_resize(contentHeight)
        self.sr.content.height = max(clipperHeight, contentHeight)
        self.sr.content.width = clipperWidth

    def GetEntriesTotalHeight(self):
        return self.entriesTotalHeight

    @telemetry.ZONE_METHOD
    def AddNodes(self, fromIdx, nodesData, parentNode = None, ignoreSort = 0, initing = False, threadedUpdate = True):
        wnd = GetWindowAbove(self)
        if wnd and not wnd.destroyed and hasattr(wnd, 'ShowLoad'):
            wnd.ShowLoad()
        if fromIdx == -1:
            fromIdx = len(self.sr.nodes)
        isSub = 0
        if parentNode:
            isSub = parentNode.get('sublevel', 0) + 1
        nodes = []
        idx = fromIdx
        for data in nodesData:
            newnode = self.AddNode(idx, data, isSub=isSub, initing=initing)
            if newnode is None:
                continue
            subs = self.CollectSubNodes(newnode, clear=0)
            idx = newnode.idx + 1 + len(subs)
            nodes.append(newnode)

        if parentNode:
            parentNode.subNodes = nodes
        if not initing:
            if self.GetSortBy() and not (self._ignoreSort or ignoreSort):
                self.RefreshSort()
            elif threadedUpdate:
                self.RefreshNodes()
                self.UpdatePositionThreaded(fromWhere='AddNodes')
            else:
                self.RefreshNodes()
                self.UpdatePosition(fromWhere='AddNodes')
            if nodes:
                self.UpdateTabStops('AddNodes', updatePosition=True)
        if wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
            wnd.HideLoad()
        return nodes

    AddEntries = AddNodes

    @telemetry.ZONE_METHOD
    def RemoveNodes(self, nodes):
        wnd = GetWindowAbove(self)
        if wnd and not wnd.destroyed and hasattr(wnd, 'ShowLoad'):
            wnd.ShowLoad()
        subs = []
        for node in nodes:
            subs.extend(self.CollectSubNodes(node))

        for nodeList in (nodes, subs):
            for node in nodeList:
                if node.panel:
                    node.panel.Close()
                if node in self.sr.nodes:
                    self.sr.nodes.remove(node)

        self.RefreshNodes()
        self.UpdatePosition()
        if wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
            wnd.HideLoad()

    RemoveEntries = RemoveNodes

    @telemetry.ZONE_METHOD
    def CollectSubNodes(self, node, nodes = None, clear = 1):
        if nodes is None:
            nodes = []
        inNodes = [ id(each) for each in nodes ]
        for subnode in node.get('subNodes', []):
            if subnode is None:
                continue
            self.CollectSubNodes(subnode, nodes, clear)
            if id(subnode) not in inNodes:
                nodes.append(subnode)

        if clear:
            node.subNodes = []
        return nodes

    @telemetry.ZONE_METHOD
    def GetNodeHeight(self, node, clipperWidth):
        func = node.GetHeightFunction
        newStyle = getattr(node.decoClass, 'GetDynamicHeight', None)
        if func:
            allowDynamicResize = node.get('allowDynamicResize', True)
            if not node.height or allowDynamicResize and node._lastClipperWidth != clipperWidth:
                node.height = apply(func, (None, node, clipperWidth))
                node._lastClipperWidth = clipperWidth
        elif newStyle:
            if not node.height or node._lastClipperWidth != clipperWidth:
                node.height = newStyle(node, clipperWidth)
                node._lastClipperWidth = clipperWidth
        elif self._fixedEntryHeight:
            node.height = self._fixedEntryHeight
        else:
            node.height = getattr(node.decoClass, 'ENTRYHEIGHT', 18)
        if not node.height:
            if func:
                apply(func, (None, node, clipperWidth))
            else:
                node.height = getattr(node.decoClass, 'ENTRYHEIGHT', 18)
        return node.height

    @telemetry.ZONE_METHOD
    def GetContentWidth(self):
        w, h = self.GetContentParentSize()
        return w

    @telemetry.ZONE_METHOD
    def GetContentHeight(self):
        return self._totalHeight

    GetTotalHeight = GetContentHeight

    def GetContentParentSize(self):
        w, h = self.sr.clipper.GetAbsoluteSize()
        return (w, h)

    def UpdatePositionThreaded(self, fromWhere = None):
        if self.loopThread is None:
            self.loopThread = uthread.new(self.UpdatePositionLoop)
            self._pendingPositionUpdate = None
        else:
            self._pendingPositionUpdate = self._position

    @telemetry.ZONE_METHOD
    def UpdatePositionLoop(self, fromWhere = None):
        if self.destroyed:
            return
        while True:
            nodeCreatedOrRefreshed, updatedPos = self.UpdatePosition(fromWhere='UpdatePositionLoop', doYield=True)
            if self._pendingPositionUpdate == updatedPos:
                self._pendingPositionUpdate = None
            if self.discardNonVisibleNodes:
                with ExceptionEater('Discarding non-visible nodes'):
                    self.DiscardNonVisibleNodes()
            blue.pyos.BeNice()
            if self.destroyed:
                return
            if not nodeCreatedOrRefreshed:
                break

        self.loopThread = None
        if self._pendingPositionUpdate is not None:
            uthread2.call_after_wallclocktime_delay(self._DelayedPositionCorrection, 0.5, self._pendingPositionUpdate)

    def _DelayedPositionCorrection(self, pendingValue):
        if pendingValue == self._pendingPositionUpdate:
            self.UpdatePositionThreaded()

    def DiscardNonVisibleNodes(self):
        for eachNode in self.GetNodes():
            if eachNode.panel and not eachNode.panel.destroyed:
                if eachNode not in self.visibleNodes:
                    eachNode.panel.Close()
                    eachNode.panel = None

    @telemetry.ZONE_METHOD
    def UpdatePosition(self, fromWhere = None, doYield = False):
        if self.destroyed:
            return (None, None)
        clipperWidth, clipperHeight = self.sr.clipper.GetAbsoluteSize()
        self.sr.content.top = int(-self._position)
        if self.sr.overlays_content:
            self.sr.overlays_content.top = self.sr.content.top
        if self.sr.underlays_content:
            self.sr.underlays_content.top = self.sr.content.top
        self.UpdateScrollHandle(clipperHeight, fromWhere='UpdatePosition')
        tabStops = self.sr.tabs
        scrollPosition = self._position
        ignoreTabstops = self.sr.ignoreTabTrimming or not self.GetColumns()
        nodeLoaded = False
        self.visibleNodes = []
        for nodeCount, node in enumerate(self.sr.nodes):
            if nodeCount != node.idx or node.scroll_positionFromTop is None or node.height is None:
                self.RefreshNodes(fromWhere='UpdatePosition')
            nodeheight = node.height
            posFromTop = node.scroll_positionFromTop
            displayScrollEntry = node.panel
            if scrollPosition > posFromTop + nodeheight or scrollPosition + clipperHeight < posFromTop:
                if displayScrollEntry:
                    displayScrollEntry.state = uiconst.UI_HIDDEN
                if doYield:
                    blue.pyos.BeNice()
                continue
            forceTabstops = False
            if not displayScrollEntry or displayScrollEntry.destroyed:
                decoClass = node.decoClass
                displayScrollEntry = decoClass(parent=self.sr.content, align=uiconst.TOPLEFT, pos=(0,
                 posFromTop,
                 clipperWidth,
                 nodeheight), state=uiconst.UI_NORMAL, name=node.name or 'entry_%s' % node.idx, node=node)
                displayScrollEntry.sr.node = node
                node.panel = displayScrollEntry
                node.scroll = self.sr.selfProxy
                if hasattr(displayScrollEntry, 'Startup'):
                    displayScrollEntry.Startup(self.sr.selfProxy)
                displayScrollEntry.Load(node)
                forceTabstops = True
                nodeLoaded = True
            elif not displayScrollEntry.display:
                displayScrollEntry.state = uiconst.UI_NORMAL
                if not node.isStatic:
                    displayScrollEntry.Load(node)
                forceTabstops = True
                nodeLoaded = True
            elif getattr(displayScrollEntry, 'currentBandingValue', None) is not None:
                if node.idx % getattr(displayScrollEntry, 'MOD_DIV', 2) != displayScrollEntry.currentBandingValue and getattr(displayScrollEntry, 'UpdateBandingColor', None):
                    displayScrollEntry.UpdateBandingColor()
                    displayScrollEntry.UpdateBandingFillVisibility()
            self.visibleNodes.append(node)
            if not ignoreTabstops:
                updateTabs = node.tabs != tabStops
                if forceTabstops or updateTabs:
                    self.ApplyTabstopsToNode(node, 'UpdatePosition')

        self.OnUpdatePosition(self)
        return (nodeLoaded, scrollPosition)

    def UpdateScrollHandle(self, clipperHeight, fromWhere = ''):
        if self.destroyed or not self._scrollbar_vertical:
            return
        if not self._totalHeight:
            handle_size_fraction = 0.0
        else:
            handle_size_fraction = clipperHeight / float(self._totalHeight)
        self._scrollbar_vertical.handle_size_fraction = mathext.clamp(handle_size_fraction, 0.0, 1.0)
        if not self._suppress_scroll_vertical_update:
            scroll_fraction = 0.0
            if self._position and self.scrollingRange:
                scroll_fraction = self._position / float(self.scrollingRange)
            self._scrollbar_vertical.scroll_to_fraction(scroll_fraction)

    def OnChar(self, enteredChar, *args):
        if enteredChar < 32:
            return False
        if not self.sr.nodes:
            return False
        haveCharIndex = False
        for node in self.sr.nodes:
            if node.charIndex is not None:
                haveCharIndex = True
                break

        if not haveCharIndex:
            return False
        if blue.os.TimeAsDouble(blue.os.GetWallclockTime()) - self.lastCharReceivedAt < 1.0 and self.currChars is not None:
            self.currChars += unichr(enteredChar).lower()
        else:
            self.currChars = unichr(enteredChar).lower()
        if enteredChar == uiconst.VK_SPACE:
            selected = self.GetSelected()
            if len(selected) == 1 and self.currChars == ' ' and GetAttrs(selected[0], 'panel', 'OnCharSpace') is not None:
                selected[0].panel.OnCharSpace(enteredChar)
                return True
        uthread.new(self._OnCharThread, enteredChar)
        self.lastCharReceivedAt = blue.os.TimeAsDouble(blue.os.GetWallclockTime())
        return True

    def ScrollToSelectedNode(self):
        selected = self.GetSelected()
        if selected:
            self.ScrollToNode(selected[0])

    def ScrollToNode(self, node):
        numEntries = len(self.sr.nodes)
        if numEntries <= 1:
            return
        entryPos = self.sr.nodes.index(node)
        self.ScrollToProportion(float(entryPos) / (numEntries - 1))

    def _OnCharThread(self, enteredChar):
        if self.destroyed:
            return
        charsBefore = self.currChars
        blue.pyos.synchro.SleepWallclock(100)
        if self.destroyed:
            return
        if self.currChars != charsBefore:
            return
        selected = self.GetSelected()
        if not selected:
            selected = self.sr.nodes
        selected = selected[0]
        numEntries = len(self.sr.nodes)
        if selected not in self.sr.nodes:
            return
        startIndex = self.sr.nodes.index(selected)
        if len(self.currChars) == 1:
            startIndex += 1
        entryRange = range(numEntries)[startIndex:] + range(numEntries)[:startIndex]
        for i in entryRange:
            entry = self.sr.nodes[i]
            if entry.charIndex and entry.charIndex.lower().startswith(self.currChars):
                self.SelectNode(entry)
                self.ScrollToNode(entry)
                break

    def OnDelete(self):
        pass

    def OnUpdatePosition(self, *args):
        pass

    def ShowLoading(self):
        if not self.loadingWheel:
            self.loadingWheel = LoadingWheel(name='myLoadingWheel', parent=self, align=uiconst.CENTER, width=32, height=32)
        self.ShowHint(None)

    def HideLoading(self):
        if self.loadingWheel:
            self.loadingWheel.Close()
            self.loadingWheel = None

    def CheckOverlaysAndUnderlays(self):
        for overlay, attrs, x, y in self.sr.overlays + self.sr.underlays:
            if overlay is None or overlay.destroyed:
                continue
            if attrs.Get('align', None) == 'right':
                overlay.left = self.GetContentWidth() - overlay.width - attrs.left
            if not overlay.loaded:
                overlay.top = attrs.top
                overlay.SetAlign(uiconst.RELATIVE)
                overlay.state = uiconst.UI_NORMAL
                overlay.Load()

    def GetNode(self, idx, checkInternalNodes = False):
        if checkInternalNodes:
            allNodes = self.GetNodes(allowNone=True)
        else:
            allNodes = self.sr.nodes
        if idx == -1:
            if allNodes:
                return allNodes[-1]
            else:
                return None
        if len(allNodes) > idx:
            return allNodes[idx]

    def OnKeyDown(self, key, flag):
        if uiconst.VK_DELETE == key:
            self.OnDelete()
        elif key == uiconst.VK_PRIOR:
            self.ScrollByPage(up=True)
        elif key == uiconst.VK_NEXT:
            self.ScrollByPage(up=False)

    def ScrollByPage(self, up = True):
        visibleNodes = self.visibleNodes
        numVisibleNodes = len(visibleNodes)
        allNodesNum = len(self.sr.nodes)
        if numVisibleNodes < 1:
            return
        if up:
            lastVisibleNode = visibleNodes[0]
            step = -1
        else:
            lastVisibleNode = visibleNodes[-1]
            step = 1
        newNodesHeight = lastVisibleNode.height
        currentNodeIdx = lastVisibleNode.idx
        clipperWidth, clipperHeight = self.GetContentParentSize()
        while 1:
            nextNodeIdx = currentNodeIdx + step
            if not 0 < nextNodeIdx < allNodesNum - 1:
                break
            nextNode = self.GetNode(idx=nextNodeIdx, checkInternalNodes=False)
            newNodesHeight += nextNode.height
            if newNodesHeight > clipperHeight:
                break
            currentNodeIdx = nextNodeIdx

        self.ShowNodeIdx(currentNodeIdx, threadedScrolling=False)

    def Resizing(self):
        pass

    def OnClipperResize(self, clipperWidth, clipperHeight, *args, **kw):
        self.OnContentResize(clipperWidth, clipperHeight, *args, **kw)

    def OnContentResize(self, clipperWidth, clipperHeight, *args, **kw):
        if self.sr.hint:
            w, h = clipperWidth, clipperHeight
            newWidth = w - self.sr.hint.left * 2
            if abs(newWidth - self.sr.hint.width) > 12:
                self.sr.hint.width = newWidth
        if self.sr.content:
            self.RefreshNodes(fromWhere='OnContentResize')
            self.UpdatePositionThreaded(fromWhere='OnContentResize')
        if not self.destroyed:
            self.Resizing()

    def BrowseNodes(self, up):
        sel = self.GetSelected()
        control = uicore.uilib.Key(uiconst.VK_CONTROL)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if sel:
            shiftIdx = None
            if not control and shift:
                r = [ node.idx for node in sel ]
                if up:
                    if r[0] < self.lastSelected:
                        shiftIdx = r[0] - 1
                    else:
                        shiftIdx = r[-1] - 1
                elif r[0] < self.lastSelected:
                    shiftIdx = r[0] + 1
                else:
                    shiftIdx = r[-1] + 1
            if shiftIdx is None:
                if len(sel) > 1:
                    idx = sel[[-1, 0][up]].idx
                else:
                    idx = sel[-1].idx
                idx += [1, -1][up]
            else:
                idx = shiftIdx
            total = len(self.GetNodes())
            if 0 <= idx < total:
                self.ActivateIdx(idx)
                return 1
        return 0

    BrowseEntries = BrowseNodes

    def OnUp(self):
        if not self.GetSelected():
            self.ActivateIdx(len(self.sr.nodes) - 1)
            return
        if not self.BrowseNodes(1):
            self.Scroll(1 + 10 * uicore.uilib.Key(uiconst.VK_SHIFT))

    def OnDown(self):
        if not self.GetSelected():
            self.ActivateIdx(0)
            return
        if not self.BrowseNodes(0):
            self.Scroll(-1 - 10 * uicore.uilib.Key(uiconst.VK_SHIFT))

    def OnHome(self):
        self.ScrollToProportion(0.0)

    def OnEnd(self):
        self.ScrollToProportion(1.0)

    def OnMouseWheel(self, *etc):
        if getattr(self, 'wheeling', 0):
            return
        if HasContextMenu():
            menuOwner = GetContextMenuOwner()
            if menuOwner and menuOwner.IsUnder(self):
                return
        self.wheeling = 1
        self.Scroll(uicore.uilib.dz / 240.0)
        self.wheeling = 0

    def Scroll(self, dz):
        if not self.scrollEnabled:
            return
        step = 100
        pos = max(0, min(self.scrollingRange, self._position - step * dz))
        if pos != self._position:
            self._position = int(pos)
            self.stickToBottom = False
            self.UpdatePositionThreaded(fromWhere='Scroll')

    def ScrollPixels(self, delta):
        if not self.scrollEnabled:
            return
        pos = mathext.clamp(self._position - delta, 0, self.scrollingRange)
        if pos != self._position:
            self._position = int(pos)
            self.stickToBottom = False
            self.UpdatePositionThreaded(fromWhere='ScrollPixels')

    def GetScrollProportion(self):
        if self.scrollingRange:
            return self._position / float(self.scrollingRange)
        return 0.0

    @telemetry.ZONE_METHOD
    def ScrollToProportion(self, proportion, threaded = True):
        if not self.scrollEnabled:
            return
        proportion = min(1.0, max(0.0, proportion))
        pos = int(max(0, self.scrollingRange * proportion))
        self._position = int(pos)
        if threaded:
            self.UpdatePositionThreaded(fromWhere='ScrollToPorportion')
        else:
            self.UpdatePosition(fromWhere='ScrollToPorportion')

    def GetMinSize(self):
        return (64, 64)

    def GetMaxTextWidth(self, defaultTextWidth = 0):
        nodes = self.GetNodes()
        if not nodes:
            return defaultTextWidth
        textWidths = []
        for node in nodes:
            fontsize = node.Get('fontsize', DEFAULT_FONTSIZE)
            hspace = node.Get('letterspace', DEFAULT_LETTERSPACE)
            uppercase = node.Get('uppercase', DEFAULT_UPPERCASE)
            textWidth = uicore.font.GetTextWidth(node.label, fontsize, hspace, uppercase)
            padLeft = node.Get('padLeft', self.tabMargin)
            padRight = node.Get('padRight', self.tabMargin)
            padIndentation = uiconst.ENTRY_DEFAULT_ICONSIZE * (1 + node.get('sublevel', 0))
            textWidth += padIndentation + padLeft + padRight
            textWidths.append(textWidth)

        return max(textWidths)

    def GetNoItemNode(self, text, sublevel = 0, *args):
        return GetFromClass(Generic, {'label': text,
         'sublevel': sublevel})

    def Copy(self, *args):
        myNodes = self.GetSelected() or self.GetNodes()
        allLabelsList = []
        for node in myNodes:
            decoClass = node.decoClass
            if decoClass is None:
                report_node_missing_deco_class(node)
                continue
            GetCopyData = getattr(decoClass, 'GetCopyData', None)
            if GetCopyData is None:
                continue
            label = GetCopyData(node)
            if label:
                allLabelsList.append(label)

        allLabels = '\n'.join(allLabelsList)
        allLabels = allLabels.replace('<t>', '\t')
        strippedText = StripTags(allLabels)
        if strippedText:
            blue.pyos.SetClipboardData(strippedText)

    def AddCollapseBtn(self):
        self.sr.collapseCont = Container(parent=self.sr.scrollHeaders, name='collapseCont', pos=(4, 0, 12, 0), align=uiconst.TOLEFT, idx=0 if self.isLinelessScroll else 1)
        ButtonIcon(name='collapse', parent=self.sr.collapseCont, align=uiconst.CENTERLEFT, pos=(0, 0, 12, 12), iconSize=12, texturePath='res:/UI/Texture/classes/Scroll/Collapse.png', func=self.CollapseAll, hint=localization.GetByLabel('UI/Common/Buttons/CollapseAll'))

    def CollapseAll(self, *args):
        for eachNode in self.GetNodes():
            if eachNode.Get('GetSubContent', None):
                uicore.registry.SetListGroupOpenState(eachNode.id, 0)

        self.ReloadNodes()

    def GetEffectiveColumnOffset(self):
        if not self._showCollapseIcon:
            return 0
        return self._columnOffset

    def Startup(self, minZ = None):
        pass

    def SetDefaultSmartSorting(self, column, sortOrder, availableColumns = None):
        if not self.sr.id:
            return
        try:
            self._SetDefaultSmartSortingPrimary(column, availableColumns)
            self._SetDefaultSmartSortingDirection(column, sortOrder)
        except StandardError as e:
            log.exception('Failed to set deault smart sorting')

    def _SetDefaultSmartSortingPrimary(self, column, availableColumns):
        primaryColumns = settings.user.ui.Get(PRIMARY_COLUMN % VERSION, {})
        currentPrimaryForScroll = primaryColumns.get(self.sr.id, None)
        if currentPrimaryForScroll:
            if availableColumns and currentPrimaryForScroll not in availableColumns:
                primaryColumns[self.sr.id] = column
        else:
            primaryColumns[self.sr.id] = column
        settings.user.ui.Set(PRIMARY_COLUMN % VERSION, primaryColumns)

    def _SetDefaultSmartSortingDirection(self, column, sortOrder):
        sortDirections = settings.user.ui.Get(SMART_SORT_DIRECTION % VERSION, {})
        directionsForScroll = sortDirections.get(self.sr.id, None)
        if directionsForScroll is None:
            directionsForScroll = sortDirections[self.sr.id] = {}
        if column not in directionsForScroll:
            directionsForScroll[column] = sortOrder
        settings.user.ui.Set(SMART_SORT_DIRECTION % VERSION, sortDirections)


def report_node_missing_deco_class(node):
    scroll_path = ''
    scroll = getattr(node, 'scroll', None)
    if scroll is not None:
        scroll_path = gather_element_path(scroll)
        scroll_path = ' at {}'.format(scroll_path)
    log.error('Found a %s node without a decoClass property%s', getattr(node, '__guid__', None), scroll_path)


def gather_element_path(element):
    path = None
    while element:
        name = getattr(element, 'name', None)
        if name is None:
            element_type = getattr(element, '__class__', None)
            if element_type is not None:
                name = '[class:{}]'.format(element_type.__name__)
            else:
                name = '[unknown]'
        path = '{}.{}'.format(name, path) if path is not None else name
        element = getattr(element, 'parent', None)

    return path
