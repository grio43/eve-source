#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\tabGroup.py
import logging
import weakref
import eveformat
import eveicon
import mathext
import telemetry
import uthread
from carbonui import fontconst, uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.control.tab import Tab
from carbonui.decorative.divider_line import DividerLine
from carbonui.decorative.selectionIndicatorLine import SelectionIndicatorLine
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from carbonui.util.dpi import reverse_scale_dpi, scale_dpi
from carbonui.util.various_unsorted import divide_evenly
from eve.client.script.ui import eveThemeColor
log = logging.getLogger(__name__)

class TabGroup(Container):
    __guid__ = 'uicontrols.TabGroup'
    default_name = 'tabgroup'
    default_align = uiconst.TOTOP
    default_height = 32
    default_state = uiconst.UI_PICKCHILDREN
    default_minTabsize = 20
    default_groupID = None
    default_callback = None
    default_padBottom = 8
    default_tabClass = Tab
    default_tabAlign = uiconst.TOLEFT
    default_autoSelect = True
    default_analyticID = None
    default_tabSpacing = 24
    default_minTabSpacing = 12
    default_fontsize = fontconst.EVE_MEDIUM_FONTSIZE
    default_labelPadding = 16
    default_leftMargin = 0
    default_rightMargin = 0
    default_tabReservedSpace = 0
    _line = None
    _main_cont = None
    _tab_sizes_dirty = False
    _trailing_buttons = None
    _updating_size = False
    _updating_tab_sizes = False
    _selected_tab = None
    _selection_indicator = None
    _selection_indicator_destination = (0, 0)

    def __init__(self, show_line = True, auto_size = False, show_selection_indicator = True, **kwargs):
        if 'showLine' in kwargs:
            show_line = kwargs['showLine']
        self._auto_size = auto_size
        self._show_line = show_line
        self._show_selection_indicator = show_selection_indicator
        super(TabGroup, self).__init__(**kwargs)

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self._inited = 0
        self.tabData = []
        self.tabsmenu = None
        self.sr.tabs = []
        self.mytabs = []
        self.totalTabWidth = 0
        self.linkedrows = []
        self.selectedTab = None
        self._tab_sizes_dirty = False
        self._tabs_by_label = weakref.WeakValueDictionary()
        self._autoSelectThread = None
        self.leftMargin = attributes.get('leftMargin', self.default_leftMargin)
        self.rightMargin = attributes.get('rightMargin', self.default_rightMargin)
        self.minTabsize = attributes.get('minTabsize', self.default_minTabsize)
        self.labelPadding = attributes.get('labelPadding', self.default_labelPadding)
        self.callback = attributes.get('callback', self.default_callback)
        self.tabReservedSpace = attributes.get('tabReservedSpace', self.default_tabReservedSpace)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        self.tabClass = attributes.get('tabClass', self.default_tabClass)
        self.groupID = attributes.get('groupID', self.default_groupID)
        self.autoselecttab = attributes.get('autoselecttab', self.default_autoSelect)
        self.silently = attributes.get('silently', False)
        self.settingsID = attributes.get('settingsID', self.groupID)
        self.tabAlign = attributes.get('tabAlign', self.default_tabAlign)
        self._analyticID = attributes.get('analyticID', self.default_analyticID)
        self._tab_spacing = attributes.get('tabSpacing', self.default_tabSpacing)
        self.minTabSpacing = attributes.get('minTabSpacing', self.default_minTabSpacing)
        self.UIIDPrefix = attributes.UIIDPrefix
        self.tabs = attributes.tabs
        self._layout()

    @property
    def show_line(self):
        return self._show_line

    @show_line.setter
    def show_line(self, value):
        if self._show_line != value:
            self._show_line = value
            self._update_line()

    def _layout(self):
        if self._show_selection_indicator:
            self._selection_indicator = SelectionIndicatorLine(parent=ContainerAutoSize(parent=self, align=uiconst.TOBOTTOM_NOPUSH), align=uiconst.TOPLEFT, height=1, width=0, selected=True)
        if self.tabAlign in uiconst.PROPORTIONALALIGNMENTS:
            align = uiconst.TOALL
        else:
            align = uiconst.TOLEFT
        self._main_cont = ContainerAutoSize(parent=self, align=align, alignMode=self.tabAlign)
        if self._show_line:
            self._construct_line()
        if self.tabAlign in uiconst.PROPORTIONALALIGNMENTS:
            self.tabsCont = Container(name='tabsCont', parent=self._main_cont)
        else:
            self.tabsCont = ContainerAutoSize(name='tabsCont', parent=self._main_cont, align=self.tabAlign, alignMode=self.tabAlign)
        self._trailing_buttons = TrailingContainer(parent=self._main_cont, align=uiconst.TOLEFT, alignMode=uiconst.TOLEFT, spacing_left=self.tabSpacing, callback=self._on_trailing_container_size_changed, only_use_callback_when_size_changes=True)
        if self.tabs:
            for each in self.tabs:
                if isinstance(each, dict):
                    self.AddTab(**each)
                else:
                    self.AddTab(*each)

            if self.autoselecttab:
                self.AutoSelect(self.silently)

    def _construct_line(self):
        self._line = DividerLine(parent=self._main_cont, align=uiconst.TOBOTTOM_NOPUSH, idx=0)

    def _update_line(self):
        if self._show_line:
            if self._line is None:
                self._construct_line()
            else:
                self._line.display = True
        elif self._line is not None:
            self._line.display = False

    @property
    def analyticID(self):
        return self._analyticID

    @analyticID.setter
    def analyticID(self, value):
        self._analyticID = value

    @property
    def tabSpacing(self):
        return self._tab_spacing

    @tabSpacing.setter
    def tabSpacing(self, value):
        if self._tab_spacing != value:
            self._tab_spacing = value
            self.UpdateSizes()

    tab_spacing = tabSpacing

    @telemetry.ZONE_METHOD
    def Startup(self, tabs, groupID = None, _notUsed_callback = None, _notUsed_isSub = 0, _notUsed_detachable = 0, autoselecttab = 1, UIIDPrefix = None, silently = False):
        self.settingsID = groupID
        self.autoselecttab = autoselecttab
        self.UIIDPrefix = UIIDPrefix
        self.silently = silently
        for each in tabs:
            if isinstance(each, dict):
                self.AddTab(**each)
            else:
                self.AddTab(*each)

        if self.autoselecttab:
            self.AutoSelect(self.silently)

    def AddTab(self, label, panel = None, code = None, tabID = None, panelParent = None, hint = '', tabClass = None, enabled = True, callback = None, uniqueName = None, **kwargs):
        if tabClass is None:
            tabClass = self.tabClass
        if not self._inited:
            self._inited = True
        label, name = self.GetNameLabel(label)
        uiID = self.GetUIID(name, tabID)
        tabData = self.GetTabData(tabID, code, hint, label, panel, panelParent, tabClass, uiID, callback)
        newtab = tabClass(parent=self.tabsCont, labelPadding=self.labelPadding, fontsize=self.fontsize, align=self.tabAlign, tabID=tabID, enabled=enabled, uniqueUiName=uniqueName, **kwargs)
        self.mytabs.append(newtab)
        newtab.Startup(self, tabData)
        self._tabs_by_label[tabData.label] = newtab
        self.sr.Set('%s_tab' % tabData.label, newtab)
        self.sr.tabs.append(newtab)
        self.tabData.append(tabData)
        self.height = max(self.height, int(self.GetMaxHeight() * 1.7))
        self.UpdateSizes()
        return newtab

    def AddButton(self, icon, func = None, hint = None, btnClass = ButtonIcon):
        return btnClass(parent=ContainerAutoSize(parent=self._trailing_buttons, align=uiconst.TOLEFT), align=uiconst.CENTER, width=24, height=24, texturePath=icon, iconSize=16, func=func, hint=hint)

    def Flush(self):
        self.ClearTabs()
        self._trailing_buttons.Flush()

    def ClearTabs(self):
        for child in self.tabsCont.children[:]:
            if isinstance(child, Tab):
                child.Close()

        self.sr.tabs = []
        self._tabs_by_label.clear()
        self.tabData = []
        self.mytabs = []
        self._KillAutoSelectThread()

    def GetNameLabel(self, label):
        if isinstance(label, tuple):
            name, label = label
        else:
            name = label
        return (label, name)

    def GetUIID(self, name, tabID = None):
        if isinstance(tabID, (basestring, int)):
            if self.UIIDPrefix is not None:
                return '%s%s' % (self.UIIDPrefix, tabID)
            else:
                return unicode(tabID)
        elif self.UIIDPrefix is not None:
            secondPart = name.replace(' ', '')
            secondPart = secondPart.capitalize()
            return '%s%s' % (self.UIIDPrefix, secondPart)
        return 'tab'

    def GetTabData(self, tabID, code, hint, label, panel, panelParent, tabClass, uiID, callback):
        tabData = Bunch()
        tabData.label = label
        tabData.code = code
        tabData.args = tabID
        tabData.panel = panel
        tabData.panelparent = panelParent
        tabData.hint = hint
        tabData.name = uiID
        tabData.tabClass = tabClass
        tabData.callback = callback
        return tabData

    def GetMaxHeight(self):
        maxHeight = 0
        for tab in self.mytabs:
            tabHeight = tab.GetHeight()
            maxHeight = max(tabHeight, maxHeight)

        return maxHeight

    def UpdateUIScaling(self, value, oldValue):
        super(TabGroup, self).UpdateUIScaling(value, oldValue)
        if not self.destroyed:
            self.UpdateSizes()

    @telemetry.ZONE_METHOD
    def Prepare_Tabsmenu_(self):
        if self.tabsmenu is None:
            self.tabsmenu = ContainerAutoSize(parent=self._trailing_buttons, align=uiconst.TOLEFT)
            TabOverflowMenuButton(parent=self.tabsmenu, align=uiconst.CENTER, tab_group=self)

    def _CloseTabsMenu(self):
        if self.tabsmenu is not None:
            self.tabsmenu.Close()
            self.tabsmenu = None

    def GetTabsMenu(self):
        return [ (eveformat.bold(each.label.text) if each.IsSelected() else each.label.text, self.SelectByIdx, (self.sr.tabs.index(each),)) for each in self.sr.tabs ]

    def _OnSizeChange_NoBlock(self, width, height):
        Container._OnSizeChange_NoBlock(self, width, height)

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        if self._auto_size:
            if self.align in uiconst.ALIGNMENTS_WITH_RELEVANT_WIDTH:
                budget_width = max(0, reverse_scale_dpi(budgetWidth) - self.padLeft - self.padRight)
            else:
                budget_width = None
            self._update_size(budget_width)
            result = super(TabGroup, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
            if self._show_selection_indicator:
                self._update_selection_indicator(animate=False)
            return result
        else:
            a, b, c, d, size_changed = super(TabGroup, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
            if size_changed or self._tab_sizes_dirty:
                self._update_tab_sizes()
            if self._childrenAlignmentDirty:
                super(TabGroup, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly=True)
                if self._show_selection_indicator:
                    self._update_selection_indicator(animate=False)
            return (a,
             b,
             c,
             d,
             size_changed)

    def _get_height(self):
        height = 32
        for tab in self.tabs:
            height = max(height, tab.GetHeight())

        return height

    def _on_trailing_container_size_changed(self):
        self._tab_sizes_dirty = True

    def _update_size(self, budget_width = None):
        if self.destroyed or self._updating_size:
            return
        self._updating_size = True
        try:
            if self.align in uiconst.ALIGNMENTS_WITH_RELEVANT_WIDTH:
                tabs = self.mytabs[:]
                for tab in tabs:
                    tab.UpdateTabSize()

                tab_count = len(tabs)
                gap_count = max(0, tab_count - 1)
                total_size = sum((max(self.minTabsize, tab.sr.width) for tab in tabs)) + gap_count * self.tabSpacing
                if self._trailing_buttons is not None and len(self._trailing_buttons.children) > 0:
                    if self._trailing_buttons._alignmentDirty or self._trailing_buttons._childrenAlignmentDirty or self._trailing_buttons._forceUpdateAlignment:
                        self._trailing_buttons.UpdateAlignment(budgetLeft=0, budgetTop=0, budgetWidth=scale_dpi(budget_width), budgetHeight=self._get_height(), updateChildrenOnly=False)
                    if tab_count > 0:
                        total_size += self.tabSpacing
                    total_size += self._trailing_buttons.width
                width_before = self.width
                if budget_width is not None and total_size > budget_width:
                    width = budget_width
                else:
                    width = total_size
                if self.align in uiconst.ALIGNMENTS_WITH_INCLUDED_HORIZONTAL_PADDING:
                    width += self.padLeft + self.padRight
                self.width = width
                if width_before != self.width:
                    self._tab_sizes_dirty = True
            else:
                self.width = 0
            if self._tab_sizes_dirty:
                self._update_tab_sizes()
        finally:
            self._updating_size = False

    @telemetry.ZONE_METHOD
    def UpdateSizes(self, absSize = None):
        self._tab_sizes_dirty = True
        self.FlagAlignmentDirty(hint='TabGroup.UpdateSizes')

    def _update_tab_sizes(self):
        if self.destroyed or not self.mytabs:
            return
        self._tab_sizes_dirty = True
        if self._updating_tab_sizes:
            return
        self._updating_tab_sizes = True
        try:
            self._tab_sizes_dirty = False
            if self._auto_size:
                tab_group_width = self.width
            else:
                tab_group_width, _ = self.GetCurrentAbsoluteSize()
            tabs = self.mytabs[:]
            if not self._auto_size:
                for tab in tabs:
                    tab.UpdateTabSize()

            tab_count = len(tabs)
            space_count = tab_count - 1
            available_width = tab_group_width
            if len(self._trailing_buttons.children) > 0:
                space_count += 1
                available_width -= self._trailing_buttons.width + self._trailing_buttons.padRight
            tabs_min_total_space = sum((min(self.minTabsize, tab.sr.width) for tab in tabs)) + space_count * self.minTabSpacing
            overflow_at_min = max(tabs_min_total_space - available_width, 0)
            if overflow_at_min > 0:
                selected_tab_index = self.GetSelectedIdx() or 0
                first_visible_index = 0
                last_visible_index = 0
                accumulated_width = 0
                if len(self._trailing_buttons.children) > 0:
                    accumulated_width += self.minTabSpacing
                out_of_space = False
                for i, tab in enumerate(tabs):
                    tab_space = self.minTabSpacing if i != 0 else 0
                    tab_size = min(self.minTabsize, tab.sr.width)
                    out_of_space = out_of_space or accumulated_width + tab_space + tab_size > available_width
                    if out_of_space and i > selected_tab_index:
                        tab.state = uiconst.UI_HIDDEN
                        continue
                    accumulated_width += tab_space + tab_size
                    last_visible_index = i

                for i, tab in enumerate(tabs):
                    if accumulated_width <= available_width or i == last_visible_index:
                        break
                    tab.state = uiconst.UI_HIDDEN
                    tab_space = self.minTabSpacing
                    tab_size = min(self.minTabsize, tab.sr.width)
                    accumulated_width -= tab_size + tab_space
                    first_visible_index = i + 1

                tabs = tabs[first_visible_index:last_visible_index + 1]
                tab_count = len(tabs)
                if tab_count != len(self.mytabs):
                    self.Prepare_Tabsmenu_()
            else:
                self._CloseTabsMenu()
            if len(self._trailing_buttons.children) > 0:
                space_count = tab_count
            else:
                space_count = tab_count - 1
            tabs_total_width = sum((tab.sr.width for tab in tabs))
            spacing_total_width = space_count * self.tabSpacing
            total_width = tabs_total_width + spacing_total_width
            overflow = max(total_width - available_width, 0)
            if overflow > 0:
                spacing_min_total = space_count * self.minTabSpacing
                compressed_spacing_total = max(spacing_total_width - overflow, spacing_min_total)
                overflow -= spacing_total_width - compressed_spacing_total
            else:
                compressed_spacing_total = spacing_total_width
            tab_sizes = [ TabSize(i, tab.sr.width) for i, tab in enumerate(tabs) ]
            if overflow > 0:
                tab_sizes = sorted(tab_sizes, reverse=True, key=lambda tab: (tab.size, -tab.index))
                remaining_overflow = overflow
                for i in range(tab_count):
                    if remaining_overflow == 0:
                        break
                    next_diff = max(tab_sizes[i].size - self.minTabsize, 0)
                    if i + 1 < tab_count:
                        next_diff = min(next_diff, tab_sizes[i].size - tab_sizes[i + 1].size)
                    compress_by = min(next_diff * (i + 1), remaining_overflow)
                    if compress_by == 0:
                        continue
                    for x, tab in enumerate(tab_sizes[:i + 1]):
                        tab.size -= divide_evenly(compress_by, i - x, i + 1)

                    remaining_overflow -= compress_by

            tab_sizes = [ tab.size for tab in sorted(tab_sizes, key=lambda tab: tab.index) ]
            prev_tab = None
            gap = self.tabSpacing
            for i, (tab, size) in enumerate(zip(tabs, tab_sizes)):
                if space_count > 0:
                    gap = divide_evenly(compressed_spacing_total, i, space_count)
                if i == 0:
                    tab.left = 0
                    tab.gap_left = gap
                else:
                    tab.left = gap
                    tab.gap_left = gap
                    prev_tab.gap_right = gap
                if not tab.enabled:
                    tab.Disable()
                else:
                    tab.Enable()
                tab.width = size
                prev_tab = tab

            if prev_tab is not None:
                prev_tab.gap_right = gap
            if space_count > 0:
                self._trailing_buttons.spacing_left = divide_evenly(compressed_spacing_total, space_count - 1, space_count)
            else:
                self._trailing_buttons.spacing_left = 0
        finally:
            self._updating_tab_sizes = False

    def _UpdateSizesOld(self, absSize = None):
        if self.destroyed or not self._inited or not (self.sr and self.mytabs) or not self.IsUnder(uicore.desktop):
            return
        if self._updating_tab_sizes:
            return
        self._updating_tab_sizes = True
        try:
            if absSize:
                mw, _ = absSize
            else:
                mw, _ = self.GetAbsoluteSize()
            for tab in self.mytabs:
                tab.UpdateTabSize()

            totalSpacingWidth = max(len(self.mytabs) - 1, 0) * self.tabSpacing
            totalTabWidth = sum([ each.sr.width for each in self.mytabs ])
            totalSpace = mw - self.leftMargin - self.rightMargin
            needToShrink = max(0, totalTabWidth + totalSpacingWidth - totalSpace)
            totalShrunk = 0
            allMin = True
            for each in self.mytabs:
                portionOfFull = each.sr.width / float(totalTabWidth)
                each.portionOfFull = portionOfFull
                each.width = mathext.clamp(value=each.sr.width, low=self.minTabsize, high=each.sr.width - int(needToShrink * portionOfFull))
                if each.width > self.minTabsize:
                    allMin = False
                totalShrunk += each.sr.width - each.width

            needMore = max(0, needToShrink - totalShrunk)
            while needMore and not allMin:
                _allMin = True
                for each in self.mytabs:
                    if each.width > self.minTabsize and needMore > 0:
                        each.width -= 1
                        needMore = max(0, needMore - 1)
                    if each.width > self.minTabsize:
                        _allMin = False

                allMin = _allMin

            allMin = True
            for each in self.mytabs:
                if each.width != self.minTabsize:
                    allMin = False

            if self.tabsmenu:
                self.tabsmenu.Close()
                self.tabsmenu = None
            active = self.GetSelectedTab()
            i = 0
            i2 = 0
            totalWidth = 0
            totalVisible = 0
            hidden = False
            countActive = None
            startHiddenIdx = None
            for each in self.mytabs:
                if allMin and (hidden or totalWidth + each.width > totalSpace):
                    if each == active:
                        countActive = i2
                    each.state = uiconst.UI_HIDDEN
                    if not hidden:
                        startHiddenIdx = i
                    hidden = True
                    i2 += 1
                else:
                    each.state = uiconst.UI_NORMAL
                    totalWidth += each.width
                    totalVisible += 1
                i += 1

            if allMin:
                if countActive is not None and startHiddenIdx is not None:
                    totalWidth = 0
                    totalVisible = 0
                    i = 0
                    for each in self.mytabs:
                        if i <= countActive:
                            each.state = uiconst.UI_HIDDEN
                        elif startHiddenIdx <= i <= startHiddenIdx + countActive:
                            if not each.enabled:
                                each.Disable()
                            else:
                                each.Enable()
                        if each.state == uiconst.UI_NORMAL:
                            totalWidth += each.width
                            totalVisible += 1
                        i += 1

            self.totalTabWidth = totalWidth
            totalVisibleWidth = self.leftMargin + self.tabReservedSpace
            visibleSpacingWidth = totalVisible * self.tabSpacing
            leftover = max(0, totalSpace - totalWidth - visibleSpacingWidth)
            for each in self.mytabs:
                if each.state == uiconst.UI_NORMAL:
                    each.width = mathext.clamp(value=each.sr.width, low=self.minTabsize, high=each.width + leftover / totalVisible)
                    totalVisibleWidth += each.width

            if hidden:
                self.Prepare_Tabsmenu_()
                self.tabsmenu.left = totalVisibleWidth
                self.tabsmenu.state = uiconst.UI_NORMAL
            for tabgroup in self.linkedrows:
                if tabgroup != self:
                    tabgroup.UpdateSizes()

        finally:
            self._updating_tab_sizes = False

    def GetTabs(self):
        if not self.destroyed:
            return self.sr.tabs

    def GetTotalWidth(self):
        tw = sum([ each.sr.width for each in self.mytabs ])
        return tw + self.leftMargin + self.rightMargin + self.tabReservedSpace

    def AddRow(self, tabgroup):
        for tab in tabgroup.sr.tabs:
            tab.tabgroup = self
            self.sr.tabs.append(tab)

        self.linkedrows.append(tabgroup)
        if self not in self.linkedrows:
            self.linkedrows.append(self)
        tabgroup.UpdateSizes()

    @telemetry.ZONE_METHOD
    def AutoSelect(self, silently = False, useCallback = True):
        if self.destroyed:
            return
        self._KillAutoSelectThread()
        idx = self._FindAutoSelectTabIDx()
        tab = self.sr.tabs[min(len(self.sr.tabs) - 1, idx)]
        self._autoSelectThread = uthread.new(tab.Select, silently=silently, useCallback=useCallback, saveSelectedName=False)
        self.selectedTab = tab

    def CancelAutoSelect(self):
        self._KillAutoSelectThread()

    def _KillAutoSelectThread(self):
        if hasattr(self, '_autoSelectThread') and self._autoSelectThread:
            self._autoSelectThread.kill()
            self._autoSelectThread = None

    def _FindAutoSelectTabIDx(self):
        if self.settingsID:
            panelName = settings.user.tabgroups.Get('%s_names' % self.settingsID, None)
            if panelName:
                tab = self.GetPanelByName(panelName)
                if tab and tab.enabled:
                    return self.sr.tabs.index(tab)
            else:
                storedIdx = settings.user.tabgroups.Get(self.settingsID, None)
                if storedIdx:
                    try:
                        tab = self.sr.tabs[storedIdx]
                        if tab and tab.enabled:
                            return storedIdx
                    except IndexError:
                        pass

        for i, tab in enumerate(self.sr.tabs):
            if tab.enabled:
                return i

    def SelectByIdx(self, idx, silent = 1):
        if len(self.sr.tabs) > idx:
            self.sr.tabs[idx].Select(silent)

    def SelectPrev(self):
        idx = self.GetSelectedIdx()
        if idx is None:
            return
        idx -= 1
        if idx < 0:
            idx = len(self.sr.tabs) - 1
        self.SelectByIdx(idx, silent=False)

    def SelectNext(self):
        idx = self.GetSelectedIdx()
        if idx is None:
            return
        idx += 1
        if idx > len(self.sr.tabs) - 1:
            idx = 0
        self.SelectByIdx(idx, silent=False)

    def GetSelectedIdx(self):
        for idx, tab in enumerate(self.sr.tabs):
            if tab.IsSelected():
                return idx

    def GetSelectedID(self):
        return self.GetSelectedArgs()

    def SelectByID(self, panelID, silent = False, useCallback = True):
        for tab in self.sr.tabs:
            if tab.sr.args == panelID:
                if not tab.IsSelected():
                    tab.Select(silently=silent, useCallback=useCallback)
            elif tab.IsSelected():
                tab.Deselect()

    def ShowPanel(self, panel, *args):
        for tab in self.sr.tabs:
            if tab.sr.panel == panel:
                tab.Select(1)

    def ShowPanelByID(self, panelID, silent = False, *args):
        for tab in self.sr.tabs:
            if tab.sr.args == panelID:
                tab.Select(silently=silent)

    def ShowPanelByName(self, panelname, blink = 1):
        if panelname:
            tab = self.GetPanelByName(panelname)
            if tab:
                tab.Select(1)
        else:
            log.warning("ShowPanelByName: Can't find panel with name %s", panelname)

    def GetPanelByName(self, panelname):
        return self.GetTabByLabel(panelname)

    def GetTabByLabel(self, label):
        tab = self._tabs_by_label.get(label, None)
        if tab is not None and not tab.destroyed:
            return tab

    def GetTabByID(self, panelID):
        for tab in self.sr.tabs:
            if tab.sr.args == panelID:
                return tab

    def BlinkPanelByName(self, panelname, blink = 1):
        if panelname:
            tab = self.GetPanelByName(panelname)
            if tab:
                tab.Blink(blink)
        else:
            log.warning("BlinkPanelByName: Can't find panel with name %s", panelname)

    def BlinkPanelByID(self, panelID):
        tab = self.GetTabByID(panelID)
        if tab:
            tab.Blink()

    def _OnClose(self, *args):
        self.callback = None
        self.linkedrows = []
        for each in self.sr.tabs:
            if each is not None and not each.destroyed:
                each.Close()

        self.sr.tabs = None
        self._tabs_by_label.clear()
        self.btns = []
        Container._OnClose(self, *args)

    def GetSelectedTab(self):
        if self.destroyed:
            return None
        for tab in self.sr.tabs:
            if tab.IsSelected():
                return tab

    def GetSelectedPanel(self):
        tab = self.GetSelectedTab()
        if tab is not None:
            return tab.sr.panel

    def ReloadVisible(self):
        tab = self.GetSelectedTab()
        if tab:
            tab.Select(1)

    def GetSelectedArgs(self):
        if not self.sr.tabs:
            return None
        for tab in self.sr.tabs:
            if tab.IsSelected():
                return tab.sr.args

    def OnGlobalFontSizeChanged(self):
        super(TabGroup, self).OnGlobalFontSizeChanged()
        self.UpdateSizes()

    def _get_selection_indicator_destination(self):
        tab = self.GetSelectedTab()
        if tab:
            left = reverse_scale_dpi(tab.displayX)
            width = reverse_scale_dpi(tab.displayWidth)
            return (left, width)
        else:
            return (0, 0)

    def _update_selection_indicator(self, initial_selection = False, animate = True):
        if self._show_selection_indicator and self._selection_indicator:
            left, width = self._get_selection_indicator_destination()
            if self._selection_indicator_destination != (left, width):
                self._selection_indicator_destination = (left, width)
                if animate and not initial_selection:
                    MIN_DURATION = 0.05
                    MAX_DURATION = 0.15
                    RANGE = 200
                    distance = abs(self._selection_indicator.left - left)
                    duration = MIN_DURATION + (MAX_DURATION - MIN_DURATION) * min(1.0, distance / RANGE)
                    animations.MorphScalar(self._selection_indicator, 'left', startVal=self._selection_indicator.left, endVal=left, duration=duration)
                    animations.MorphScalar(self._selection_indicator, 'width', startVal=self._selection_indicator.width, endVal=width, duration=duration)
                else:
                    animations.StopAnimation(self._selection_indicator, 'left')
                    animations.StopAnimation(self._selection_indicator, 'width')
                    self._selection_indicator.left = left
                    self._selection_indicator.width = width

    def _set_selected_tab(self, tab):
        previous_tab = self._selected_tab
        self._selected_tab = tab
        if self._show_selection_indicator:
            self._update_selection_indicator(initial_selection=previous_tab is None)


class TabOverflowMenuButton(ButtonIcon):
    expandOnLeft = True

    def __init__(self, tab_group, parent = None, align = uiconst.TOPLEFT):
        self._tab_group_ref = weakref.ref(tab_group)
        super(TabOverflowMenuButton, self).__init__(parent=parent, align=align, width=24, height=24, iconSize=16, texturePath=eveicon.expand_more)

    def _select_tab_by_index(self, index):
        tab_group = self._tab_group_ref()
        if tab_group is not None:
            tab_group.SelectByIdx(index)

    def GetMenu(self):
        tab_group = self._tab_group_ref()
        if tab_group is None:
            return []
        tabs = tab_group.GetTabs()
        if tabs is None:
            return []
        return MenuData([ MenuEntryData(text=eveformat.color(tab.label.text, eveThemeColor.THEME_FOCUS) if tab.IsSelected() else tab.label.text, func=lambda _index = index: self._select_tab_by_index(_index)) for index, tab in enumerate(tabs) ])


class TrailingContainer(ContainerAutoSize):

    def __init__(self, spacing_left = 0, spacing_right = 0, **kwargs):
        if any((x in kwargs for x in ('padding', 'padLeft', 'padRight'))):
            raise TypeError("Don't override this container's padding. Use spacing_left and spacing_right to adjust the container's padding.")
        self._spacing = (spacing_left, spacing_right)
        super(TrailingContainer, self).__init__(**kwargs)

    @property
    def spacing_left(self):
        return self._spacing[0]

    @spacing_left.setter
    def spacing_left(self, value):
        if self.spacing_left != value:
            self._spacing = (value, self.spacing_right)
            if len(self.children) > 0:
                self._apply_spacing()

    @property
    def spacing_right(self):
        return self._spacing[1]

    @spacing_right.setter
    def spacing_right(self, value):
        if self.spacing_right != value:
            self._spacing = (self.spacing_left, value)
            if len(self.children) > 0:
                self._apply_spacing()

    def _apply_spacing(self):
        self.padLeft, self.padRight = self._spacing

    def _remove_spacing(self):
        self.padLeft = 0
        self.padRight = 0

    def _InsertChildRO(self, idx, child):
        super(TrailingContainer, self)._InsertChildRO(idx, child)
        self._apply_spacing()

    def _AppendChildRO(self, child):
        super(TrailingContainer, self)._AppendChildRO(child)
        self._apply_spacing()

    def _RemoveChildRO(self, child):
        super(TrailingContainer, self)._RemoveChildRO(child)
        if len(self.children) == 0:
            self._remove_spacing()


class TabSize(object):

    def __init__(self, index, size):
        self.index = index
        self.size = size


def GetTabData(label, panel = None, code = None, tabID = None, panelParent = None, hint = '', tabClass = None, enabled = True, callback = None, uniqueName = None):
    return {'label': label,
     'panel': panel,
     'code': code,
     'tabID': tabID,
     'panelParent': panelParent,
     'hint': hint,
     'tabClass': tabClass,
     'enabled': enabled,
     'callback': callback,
     'uniqueName': uniqueName}
