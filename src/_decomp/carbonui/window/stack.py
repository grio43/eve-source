#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\stack.py
import logging
import uthread
import uthread2
from carbonui import uiconst
from carbonui.primitives.base import ReverseScaleDpi
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.decorative.divider_line import DividerLine
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import Transplant
from carbonui.control.window import Window
from carbonui.window.header.base import WindowHeaderBase
from carbonui.control.tab import Tab
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.shared import closeWindowStackPrompt
from menu import MenuLabel
log = logging.getLogger(__name__)
PREFERRED_IDX_IN_STACK_CONFIG = 'preferredIdxInStack3'

class WindowStack(Window):

    def ApplyAttributes(self, attributes):
        self._initializingStack = True
        self.contentCont = None
        self.tabsCont = None
        self._tabGroup = None
        self._detaching = 0
        self._inserting = 0
        super(WindowStack, self).ApplyAttributes(attributes)
        self.ConstructContentParent()
        self._initializingStack = False

    @property
    def compact(self):
        wnd = self.GetActiveWindow()
        return wnd and wnd.compact

    @compact.setter
    def compact(self, value):
        wnd = self.GetActiveWindow()
        if wnd and wnd.compact != value:
            wnd.compact = value
            self._emit_on_compact_mode_changed()

    @property
    def compactable(self):
        wnd = self.GetActiveWindow()
        return wnd and wnd.compactable

    @property
    def killable(self):
        return all((window.killable for window in self.GetWindows()))

    @property
    def is_stack(self):
        return True

    def _on_header_tab_selected(self, tab_id, old_tab_id):
        old_window = old_tab_id
        new_window = tab_id
        if old_window is None or new_window is not None and new_window.compact != old_window.compact:
            self._emit_on_compact_mode_changed()
        self._update_window_controls()
        self._update_window_caption()

    def ConstructContentParent(self):
        self.contentCont = Container(name='__content', parent=self.sr.maincontainer, align=uiconst.TOALL, idx=self.sr.headerParent.GetOrder() + 1)

    def Prepare_LoadingIndicator_(self):
        self.sr.loadingIndicator = None

    def Prepare_ScaleAreas_(self):
        super(WindowStack, self).Prepare_ScaleAreas_()
        for wnd in self.GetWindows():
            wnd.Prepare_ScaleAreas_()

    def Prepare_Header_(self):
        self.header = WindowStackHeader(callback=self._on_header_tab_selected)

    def CheckStackWith(self, dropWnd):
        if self.closing:
            return
        if not self.IsStackable():
            return
        if self.sr.modalParent is not None or dropWnd.sr.modalParent is not None or dropWnd == self:
            return
        if not isinstance(dropWnd, WindowStack):
            self.InsertWnd(dropWnd, 0, 1, is_dropping=True)
        else:
            for wnd in dropWnd.GetWindows()[:]:
                self.InsertWnd(wnd, 0, 1, is_dropping=True)

            dropWnd.Close()
        uicore.registry.SetFocus(self)

    def Check(self, updatewnd = 0, autoselecttab = 1, checknone = 0):
        if self.closing:
            return
        myWindows = self.GetWindows()
        if checknone and len(myWindows) == 0:
            self.Close()
            return
        self.SetMinWH()
        tabs = []
        for wnd in myWindows:
            if wnd is None or wnd.destroyed:
                continue
            tabs.append([wnd.caption or '',
             wnd,
             self,
             wnd])
            wnd.HideBackground()
            wnd.state = uiconst.UI_PICKCHILDREN

        self._UpdateWindowStates(myWindows)
        if len(tabs):
            self.header.update_tabs(tabs, auto_select=bool(autoselecttab))
            all_tabs = self.header.tab_group.GetTabs()
            if all_tabs:
                for i in xrange(len(all_tabs)):
                    tab = all_tabs[i]
                    wnd = myWindows[i]
                    if wnd.isBlinking:
                        tab.Blink()

        if not self.active and any((window.active for window in myWindows)):
            self.SetActive()

    def _update_window_caption(self):
        active_window = self.GetActiveWindow()
        if active_window:
            self.caption = active_window.caption
        else:
            self.caption = ''

    def _UpdateWindowStates(self, myWindows):
        if any((wnd.IsOverlayed() for wnd in myWindows)):
            self.SetOverlayed()
        else:
            self.SetNotOverlayed()
        if any((wnd.IsLightBackgroundEnabled() for wnd in myWindows)):
            self.EnableLightBackground()
        else:
            self.DisableLightBackground()

    def IsLightBackgroundConfigurable(self):
        return all((wnd.IsLightBackgroundConfigurable() for wnd in self.GetWindows()))

    def EnableLightBackground(self):
        super(WindowStack, self).EnableLightBackground()
        for wnd in self.GetWindows():
            wnd.EnableLightBackground()

    def DisableLightBackground(self):
        super(WindowStack, self).DisableLightBackground()
        for wnd in self.GetWindows():
            wnd.DisableLightBackground()

    def SetOverlayed(self):
        super(WindowStack, self).SetOverlayed()
        for wnd in self.GetWindows():
            wnd.SetOverlayed()

    def SetNotOverlayed(self):
        super(WindowStack, self).SetNotOverlayed()
        for wnd in self.GetWindows():
            wnd.SetNotOverlayed()

    def GetMenu(self, *args):
        menu = []
        if self.IsKillable():
            menu.append((MenuLabel('/Carbon/UI/Controls/Window/CloseWindowStack'), self.CloseByUser))
        if not self.stacked and self.IsMinimizable():
            if self.state == uiconst.UI_NORMAL:
                menu.append((MenuLabel('/Carbon/UI/Controls/Window/MinimizeWindowStack'), self.ToggleMinimize))
            else:
                menu.append((MenuLabel('/Carbon/UI/Controls/Window/MaximizeWindowStack'), self.ToggleMinimize))
        return menu

    def GetMenuMoreOptions(self):
        wnd = self.GetActiveWindow()
        if wnd:
            return wnd.GetMenuMoreOptions()
        else:
            return MenuData()

    def get_wnd_menu_unique_name(self):
        wnd = self.GetActiveWindow()
        if wnd:
            return wnd.get_wnd_menu_unique_name()
        else:
            return None

    def GetCustomHeaderButtons(self):
        wnd = self.GetActiveWindow()
        if wnd:
            return wnd.GetCustomHeaderButtons()
        else:
            return []

    def GetWindowLinkData(self):
        wnd = self.GetActiveWindow()
        if wnd:
            return wnd.GetWindowLinkData()
        else:
            return None

    def RemoveWnd(self, wnd, grab, correctpos = 1, idx = 0, dragging = 0, check = 1):
        if wnd.parent != self.contentCont:
            return
        if hasattr(wnd, 'OnTabSelect'):
            uthread.worker('WindowStack::RemoveWnd', wnd.OnTabSelect)
        wnd._detaching = True
        Transplant(wnd, self.parent, idx)
        if hasattr(wnd, '_stack_cacheContents'):
            wnd.cacheContents = wnd._stack_cacheContents
        self.RemovePreferredIdx(self.windowID, wnd.windowID)
        self._SetRemovedWindowSize(wnd)
        wnd.RegisterStackID(None)
        wnd.OnStackRemove(correctpos, dragging, grab)
        if check:
            self.Check()
        wnd._detaching = False
        wnd._dragging = dragging
        myWindows = self.GetWindows()
        if len(myWindows) == 1 and not self.IsCollapsed():
            w = myWindows[0]
            aL, aT, aW, aH = self.GetAbsolute()
            x, y = aL, aT
            self.RemoveWnd(w, (0, 0), 1, 1, check=0)
            self.RemovePreferredIdx(self.windowID, w)
            w.left, w.top = x, y
            sm.ChainEvent('ProcessWindowUnstacked', wnd, self)
            return
        if len(self.GetWindows()) == 0:
            self.Close()
        sm.ChainEvent('ProcessWindowUnstacked', wnd, self)

    def CloseByUser(self, *args):
        if len(self.GetWindows()) > 1:
            response = closeWindowStackPrompt.ask()
            if response == closeWindowStackPrompt.Response.close_all:
                for window in self.GetWindows():
                    window.CloseByUser(*args)

            elif response == closeWindowStackPrompt.Response.close_current:
                self.GetActiveWindow().CloseByUser(*args)
        else:
            canCloseStack = True
            for wnd in self.GetWindows()[:]:
                canClose = wnd.CloseByUser()
                if canClose is False:
                    canCloseStack = False

            if canCloseStack:
                super(WindowStack, self).CloseByUser(*args)

    def _SetRemovedWindowSize(self, wnd):
        wnd.width = wnd._fixedWidth or self.width
        wnd.height = wnd._fixedHeight or self.height
        wnd.CheckMaxSize()

    def RegisterPositionAndSize(self, key = None, windowID = None):
        super(WindowStack, self).RegisterPositionAndSize(key, windowID)
        for each in self.GetWindows():
            each.RegisterPositionAndSize()

    def GetCollapsedHeight(self):
        _, margin_top, _, margin_bottom = self.GetWindowBorderPadding()
        _, border_top, _, border_bottom = self.GetWindowBorderSize()
        return margin_top + border_top + self.header_height + border_bottom + margin_bottom

    @classmethod
    def Reload(cls, instance):
        pass

    def GetCaption(self, update = 1):
        caption = ''
        for wnd in self.GetWindows():
            if wnd is not None and not wnd.destroyed:
                caption = '%s%s-' % (caption, wnd.GetCaption(update))

        if caption != '':
            return caption[:-1]
        return caption

    def OnCollapsed(self, *args):
        self.contentCont.display = False
        for wnd in self.GetWindows():
            wnd.OnCollapsed(*args)

    def OnExpanded(self, *args):
        self.contentCont.display = True
        for wnd in self.GetWindows():
            wnd.OnExpanded(*args)

    def OnEndScale_(self, *args):
        for wnd in self.GetWindows():
            if wnd.state == uiconst.UI_PICKCHILDREN:
                wnd._emit_on_end_scale()
                wnd.OnEndScale_(wnd)

    def OnStartScale_(self, wnd, *args):
        for wnd in self.GetWindows():
            if wnd.state == uiconst.UI_PICKCHILDREN:
                wnd._emit_on_start_scale()

    def InsertWnd(self, wnd, adjustlocation = 1, show = 0, hilite = 0, is_dropping = False):
        while self._initializingStack:
            uthread2.Yield()

        previous_window = self.GetActiveWindow()
        windowID = getattr(wnd, 'windowID', None)
        preferredIdx = self.GetAndRegisterPreferredIdxInStack(self.windowID, windowID, is_dropping)
        self._inserting = True
        l, t, mywidth, myheight = self.GetAbsolute()
        if not len(self.GetWindows()) and adjustlocation:
            log.info('WindowStack initing, taking size from %s %s %s %s %s %s' % (wnd.windowID,
             wnd.left,
             'l,t,w,h',
             wnd.top,
             wnd.width,
             wnd.height))
            self.width = wnd.width
            if not self.IsCollapsed():
                self.height = wnd.height
            self.left = wnd.left
            self.top = wnd.top
        if wnd.IsCollapsed():
            wnd.Expand()
        wnd.SetParent(self.contentCont, idx=preferredIdx)
        wnd.OnStackInsert(self)
        self.Check(0, show != 1)
        if show:
            self.ShowWnd(wnd, hilite, previous_window=previous_window)
        wnd.RegisterStackID(self)
        self.CleanupParent('snapIndicator')
        self._inserting = False
        if self.IsMinimized():
            self.Maximize()
        wnd.Prepare_ScaleAreas_()
        sm.ChainEvent('ProcessWindowStacked', wnd, self)
        self.UpdateIntersectionBackground()

    def SetMinWH(self):
        allMinW = 0
        allMinH = 0
        for each in self.GetWindows():
            allMinW = max(allMinW, each.minsize[0])
            allMinH = max(allMinH, each.minsize[1])

        if self.IsCollapsed():
            self.minsize = [allMinW, allMinH]
        else:
            self.SetMinSize([allMinW, allMinH])

    def ShowWnd(self, wnd, hilite = 0, previous_window = None):
        if wnd not in self.GetWindows() or wnd is None or wnd.destroyed:
            return
        tab_group = self.GetTabGroup()
        if tab_group is not None:
            tab_group.ShowPanel(wnd, hilite)
            self._on_header_tab_selected(tab_id=wnd, old_tab_id=previous_window)

    def GetActiveWindow(self):
        if self.closing:
            return
        tab_group = self.GetTabGroup()
        if tab_group is not None:
            return tab_group.GetSelectedPanel()

    def IsResizeable(self):
        if self.IsLocked():
            return False
        for wnd in self.GetWindows():
            if not wnd.IsResizeable():
                return False

        return True

    def IsMinimizable(self):
        for wnd in self.GetWindows():
            if not wnd.IsMinimizable():
                return False

        return True

    def Compact(self):
        wnd = self.GetActiveWindow()
        if wnd:
            wnd.compact = True

    def UnCompact(self):
        wnd = self.GetActiveWindow()
        if wnd:
            wnd.compact = False

    def Detach(self, wnd, grab):
        if self.IsLocked():
            return False
        if wnd is not None and not wnd.destroyed and not getattr(wnd, '_detaching', 0):
            uicore.registry.SetFocus(uicore.desktop)
            self._detaching = True
            self.RemoveWnd(wnd, grab, 1, 0, 1)
            if not self.destroyed:
                self._detaching = False
            uicore.registry.SetFocus(wnd)
            return 1

    def Load(self, wnd):
        if self.destroyed:
            return
        if self.IsCollapsed() and not self._detaching and not self._inserting:
            self.Expand()
        for _wnd in self.GetWindows():
            if _wnd is not wnd:
                _wnd.state = uiconst.UI_HIDDEN

        wnd.state = uiconst.UI_PICKCHILDREN

    def GetMinWidth(self, checkgroup = 1):
        trueMinWidth = self.minsize[0]
        for wnd in self.GetWindows():
            trueMinWidth = max(wnd.GetMinWidth(), trueMinWidth)

        return trueMinWidth

    def GetMinHeight(self):
        trueMinHeight = self.minsize[1]
        for wnd in self.GetWindows():
            trueMinHeight = max(wnd.GetMinHeight(), trueMinHeight)

        return trueMinHeight

    def OnStartMaximize_(self, *args):
        for wnd in self.GetWindows():
            wnd.OnStartMaximize_(wnd)

    def OnEndMaximize_(self, *args):
        for wnd in self.GetWindows():
            wnd.OnEndMaximize_(wnd)

    def OnStartMinimize_(self, *args):
        for wnd in self.GetWindows():
            wnd.OnStartMinimize_(wnd)

    def OnEndMinimize_(self, *args):
        for wnd in self.GetWindows():
            wnd.OnEndMinimize_(wnd)

    def OnResize_(self, *args):
        for wnd in self.GetWindows():
            wnd._OnResize()

    def GetWindows(self):
        if self.contentCont is None:
            return []
        else:
            return [ each for each in self.contentCont.children if isinstance(each, Window) ]

    def RegisterPreferredIdxInStack(self, stackID, windowID, idx = -1):
        allPreferred = settings.char.windows.Get(PREFERRED_IDX_IN_STACK_CONFIG, {})
        stackInfo = allPreferred.get(stackID, {})
        stackInfo[windowID] = idx
        allPreferred[stackID] = stackInfo
        settings.char.windows.Set(PREFERRED_IDX_IN_STACK_CONFIG, allPreferred)

    def GetAndRegisterPreferredIdxInStack(self, stackID, windowID, is_dropping = False):
        allPreferred = settings.char.windows.Get(PREFERRED_IDX_IN_STACK_CONFIG, {})
        stackInfo = allPreferred.get(stackID, {})
        preferredIdx = stackInfo.get(windowID, -1)
        if is_dropping:
            tab_index = 0
            tabs = self.header.tab_group.GetTabs()
            cursorX, cursorY = uicore.uilib.cursorPos
            cursorX = ReverseScaleDpi(cursorX)
            cursorY = ReverseScaleDpi(cursorY)
            for tab in tabs:
                if cursorX <= tab.absoluteRight and cursorY >= self.header.absoluteTop and cursorY <= self.header.absoluteBottom:
                    preferredIdx = tab_index
                    break
                tab_index += 1

        if preferredIdx < 0:
            if len(self.contentCont.children) < 1:
                preferredIdx = 0
            else:
                preferredIdx = len(self.contentCont.children)
            self.RegisterPreferredIdxInStack(stackID, windowID, preferredIdx)
        return preferredIdx

    def RemovePreferredIdx(self, stackID, windowID):
        allPreferred = settings.char.windows.Get(PREFERRED_IDX_IN_STACK_CONFIG, {})
        stackInfo = allPreferred.pop(stackID, None)
        if stackInfo:
            oldPreferredIdx = stackInfo.pop(windowID, None)
            openWndIDs = {x.windowID for x in uicore.registry.GetWindows()}
            stackInfoAsList = stackInfo.items()
            stackInfoAsList.sort(key=lambda x: x[1])
            newStackInfo = {}
            for eachWndID, eachIdx in stackInfoAsList:
                if eachWndID in openWndIDs and eachIdx > oldPreferredIdx:
                    eachIdx -= max(0, 1)
                newStackInfo[eachWndID] = eachIdx

            allPreferred[stackID] = newStackInfo
        settings.char.windows.Set(PREFERRED_IDX_IN_STACK_CONFIG, allPreferred)

    def GetTabGroup(self):
        if self.header is not None and self.header.tab_group is not None and not self.header.tab_group.destroyed:
            return self.header.tab_group

    def ForceUpdateSelectedTabSetting(self):
        tabGroup = self.GetTabGroup()
        if not tabGroup:
            return
        tab = tabGroup.GetSelectedTab()
        if not tab:
            return
        tab.UpdateSelectedSettings(True)


class WindowStackTab(Tab):

    def GetMenu(self):
        wnd = self.GetPanel()
        return wnd.GetMenu()


class WindowStackHeader(WindowHeaderBase, ContainerAutoSize):

    def __init__(self, callback = None):
        self._callback = callback
        self._tab_group = None
        self._line = None
        super(WindowStackHeader, self).__init__(alignMode=uiconst.TOTOP, clipChildren=True)

    @property
    def tab_group(self):
        return self._tab_group

    def mount(self, window):
        super(WindowStackHeader, self).mount(window)
        self._update_padding(window)
        self._layout(window)
        window.on_header_inset_changed.connect(self._on_header_inset_changed)
        window.on_collapsed_changed.connect(self._on_window_collapsed_changed)

    def unmount(self, window):
        super(WindowStackHeader, self).unmount(window)
        window.on_header_inset_changed.disconnect(self._on_header_inset_changed)
        window.on_collapsed_changed.disconnect(self._on_window_collapsed_changed)
        self._clear()

    def update_tabs(self, tabs, auto_select = True):
        if self._tab_group is None:
            raise RuntimeError("Attempting to update header when it's not mounted")
        self._tab_group.ClearTabs()
        for tab_data in tabs:
            self._tab_group.AddTab(*tab_data)

        if auto_select:
            self._tab_group.AutoSelect()

    def _layout(self, window):
        pad_left, pad_right = window.header_inset
        self._tab_group = TabGroup(name='tabparent', parent=self, padding=(pad_left,
         0,
         pad_right,
         0), groupID=window.name, tabClass=WindowStackTab, callback=self._callback, show_line=False)
        self._line = DividerLine(parent=self, align=uiconst.TOBOTTOM_NOPUSH)

    def _clear(self):
        self.Flush()
        self._tab_group = None
        self._line = None

    def _on_header_inset_changed(self, window):
        self._update_padding(window)

    def _on_window_collapsed_changed(self, window):
        self._line.display = False if window.collapsed else True

    def _update_padding(self, window):
        if self._tab_group is not None:
            self._tab_group.padLeft, self._tab_group.padRight = window.header_inset
