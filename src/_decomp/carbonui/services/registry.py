#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\services\registry.py
import weakref
import uthread
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import SortListOfTuples, GetDesktopObject
import log
import blue
import localization
from carbonui.uicore import uicore
from carbonui.window.settings import GetRegisteredState

class RegistryHandler(object):
    _focus = None
    toggleState = None

    def __init__(self, *args, **kwds):
        self.PrimeHandler()

    def PrimeHandler(self):
        self.modals = []
        self.windows = []
        self.stacks = []
        self.control_blockers = set()
        self._blockConfirm = 0
        self.windowsActiveTimes = {}
        self._activeWindow = None

    def RequestControl(self, requester):
        self.control_blockers.add(requester)

    def ReleaseControl(self, requester):
        if requester in self.control_blockers:
            self.control_blockers.remove(requester)

    def HasControl(self):
        return not self.control_blockers

    def RegisterWindow(self, wnd):
        if wnd not in self.windows:
            self.windows.append(wnd)

    def UnregisterWindow(self, wnd):
        if wnd in self.windows:
            self.windows.remove(wnd)
            self.windowsActiveTimes.pop(wnd.windowID, None)

    def GetWindows(self):
        return self.windows

    def GetWindow(self, windowID, windowInstanceID = None):
        if not windowID or isinstance(windowID, tuple):
            return
        for wnd in self.GetWindows():
            windowIDMatches = str(getattr(wnd, 'windowID', wnd.name)).lower() == windowID.lower()
            if not windowInstanceID and windowIDMatches:
                return wnd
            if windowInstanceID:
                windowInstanceIDMatches = wnd.windowInstanceID == windowInstanceID
                if windowIDMatches and windowInstanceIDMatches:
                    return wnd
                continue

    def GetWindowByClass(self, windowClass):
        for window in self.GetWindows():
            if isinstance(window, windowClass) and not window.destroyed:
                return window

    def GetWindowsByClass(self, windowClass):
        return [ wnd for wnd in self.GetWindows() if isinstance(wnd, windowClass) and not wnd.destroyed ]

    def GetWindowByClassAndName(self, windowClass, windowName):
        for window in self.GetWindows():
            if isinstance(window, windowClass) and not window.destroyed and window.name == windowName:
                return window

    def GetStack(self, stackID, stackClass = None, useDefaultPos = False):
        if stackID.startswith('windowStack_'):
            stackName = stackID
        else:
            stackName = 'windowStack_%s' % stackID
        stack = self.GetWindow(stackName)
        if stack is not None and not stack.closing:
            return stack
        return stackClass.Open(windowID=stackID, parent=uicore.layer.main, useDefaultPos=useDefaultPos)

    def GetTopLevelWindowAboveItem(self, item):
        checkPar = item.parent
        while checkPar:
            if self.IsTopLevelWindow(checkPar):
                return checkPar
            if checkPar.parent:
                checkPar = checkPar.parent
            else:
                break

        return uicore.desktop

    def IsTopLevelWindow(self, item):
        return getattr(item, 'isTopLevelWindow', False)

    def IsWindow(self, item):
        from carbonui.control.window import Window
        return isinstance(item, Window)

    def IsWindowStack(self, item):
        from carbonui.window.stack import WindowStack
        return isinstance(item, WindowStack)

    def GetValidWindows(self, getModals = 0, floatingOnly = False, getHidden = 0):
        validWnds = []
        for wnd in self.GetWindows():
            if not self.IsWindow(wnd) or wnd.stacked or getattr(wnd, '_changing', 0):
                continue
            if not getHidden and not wnd.IsVisible():
                continue
            if not getModals and (getattr(wnd, 'isModal', 0) or getattr(wnd, 'isDialog', 0)):
                continue
            if floatingOnly and wnd.GetAlign() != uiconst.RELATIVE:
                continue
            if getattr(wnd, 'parent', None) is None:
                log.LogError("Window without parent!; that shouldn't be possible. Window: %s" % repr(wnd))
                print "Window without parent!; that shouldn't be possible. Window: %s" % repr(wnd), wnd.name
                continue
            validWnds.append(wnd)

        return validWnds

    def GetModalWindow(self, exclude = None):
        if self.modals:
            mdl = self.modals[-1]
            if mdl is None or mdl.destroyed or exclude and mdl == exclude:
                self.modals.remove(mdl)
                return self.GetModalWindow()
            return mdl
        else:
            return

    def IsModalWindowOpen(self):
        return bool(self.GetModalWindow())

    def AddModalWindow(self, wnd, fillOpacity = uiconst.DEFAULT_MODAL_OPACITY, sceneSaturation = uiconst.DEFAULT_MODAL_SCENE_SATURATION):
        sceneMan = sm.GetService('sceneManager')
        sceneMan.Saturate(duration=0.3, saturateLevel=sceneSaturation)
        sm.GetService('loading').FadeIn(time=300.0, color=(0,
         0,
         0,
         fillOpacity), sleep=False, owner=wnd)
        if wnd in self.modals:
            self.RemoveModalWindow(wnd)
        self.modals.append(wnd)

    def RemoveModalWindow(self, wnd):
        if wnd in self.modals:
            self.modals.remove(wnd)
        sceneMan = sm.GetService('sceneManager')
        sm.GetService('loading').FadeOut(time=300.0, sleep=False, owner=wnd)
        if not self.modals:
            sceneMan.Saturate(0.3, 1.0)

    def GetActiveStackOrWindow(self, *args):
        all = self.GetValidWindows()
        active = self.GetActive()
        if active:
            for each in all:
                if each is active:
                    return each
                if active.IsUnder(each):
                    return each

    def _GetDerivedFocusItem(self, item):
        while item and not getattr(item, 'isTabStop', False):
            if self.IsTopLevelWindow(item):
                stackWnd = None
                current, tabstops = None, []
                if self.IsWindowStack(item):
                    stackWnd = item.GetActiveWindow()
                current, tabstops = self.CrawlForTabstops(stackWnd or item)
                if current:
                    item = current
                    break
                elif tabstops:
                    item = tabstops[0]
                    break
            if self.IsTopLevelWindow(item):
                break
            if not hasattr(item, 'parent') or item == uicore.desktop:
                break
            item = item.parent

        return item

    def SetFocus(self, item):
        if item:
            desktop = GetDesktopObject(item)
            if desktop and not getattr(desktop, 'doesTakeFocus', True):
                return
        focus = self._GetDerivedFocusItem(item)
        oldFocus = self.GetFocus()
        if focus:
            if self.IsTopLevelWindow(focus):
                wndAbove = focus
            else:
                wndAbove = self.GetTopLevelWindowAboveItem(focus)
            focus.SetFocus()
            self._SetActiveWindow(wndAbove)
            self._focus = focus
            self.RegisterFocusItem(focus)
        else:
            self._focus = None
            self._SetActiveWindow(uicore.desktop)
        if oldFocus != focus and hasattr(oldFocus, 'OnKillFocus'):
            oldFocus.OnKillFocus()
        if hasattr(focus, 'OnSetFocus') and not focus.destroyed:
            focus.OnSetFocus()

    def _SetActiveWindow(self, wnd = None):
        while not self.IsTopLevelWindow(wnd):
            if wnd == uicore.desktop:
                break
            wnd = wnd.parent

        if wnd == self.GetActive():
            return
        self._TriggerInactiveEvents()
        wnd = self._GetDerivedWindowToActivate(wnd)
        self._activeWindow = weakref.ref(wnd)
        if self.IsWindow(wnd):
            self.windowsActiveTimes[wnd.windowID] = blue.os.GetWallclockTime()
            if wnd.stacked:
                wnd.stack.SetOrder(0)
            elif wnd.parent and wnd.align == uiconst.TOPLEFT:
                wnd.SetOrder(0)
        if hasattr(wnd, 'SetActive'):
            wnd.SetActive()
            sm.ScatterEvent('OnWindowSetActive', wnd)

    def _GetDerivedWindowToActivate(self, wnd):
        if self.IsWindowStack(wnd):
            wnd = wnd.GetActiveWindow()
        if not wnd or wnd.destroyed:
            return uicore.desktop
        else:
            return wnd

    def _TriggerInactiveEvents(self):
        activeWnd = self.GetActive()
        if not activeWnd:
            return
        if hasattr(activeWnd, 'OnSetInactive'):
            activeWnd.OnSetInactive()
        sm.ScatterEvent('OnWindowSetInactive', activeWnd)

    def RegisterFocusItem(self, item):
        if item and not item.destroyed and item != uicore.desktop:
            wndAbove = self.GetTopLevelWindowAboveItem(item)
            if wndAbove and wndAbove is not uicore.desktop:
                tabstopGroupsFromTop, tabstopsFromTop = FindTabStopGroupsAndTabstops(wndAbove)
                for tabstop in tabstopsFromTop:
                    setattr(tabstop, 'hasFocus', 0)

                setattr(item, 'hasFocus', 1)

    def GetFocus(self, active = None):
        focus = self._focus
        if focus and not focus.destroyed:
            return focus

    def GetActive(self):
        activeWnd = self._activeWindow() if self._activeWindow else None
        if activeWnd and not activeWnd.destroyed:
            return activeWnd

    def FindFocus(self, browse = 0):
        modal = self.GetModalWindow()
        if modal:
            active = modal
        else:
            active = self.GetActive()
        focus = self.GetFocus()
        if active is None:
            active = uicore.desktop
        if focus and hasattr(focus, 'CheckFocusChange'):
            usedFocusChange = focus.CheckFocusChange(browse)
            if usedFocusChange:
                return
        if focus and focus.IsUnder(active) and focus.IsVisible() and not browse:
            uthread.new(self.SetFocus, focus)
            return
        tabstops = []
        if active:
            current, tabstops = self.CrawlForTabstops(active)
        if browse and len(tabstops) > 1:
            current = current or focus
            idx = 0
            if current in tabstops:
                idx = browse + tabstops.index(current)
            if idx < 0:
                idx = len(tabstops) - 1
            elif idx >= len(tabstops):
                idx = 0
            self.SetFocus(tabstops[idx])
            return
        if len(tabstops) and focus != tabstops[0]:
            self.SetFocus(tabstops[0])
            return

    def CrawlForTabstops(self, fromwhere):
        sorted = []
        current = []
        done = []
        tabstopGroupsFromTop, tabstopsFromTop = FindTabStopGroupsAndTabstops(fromwhere)
        for tabstopgroup in tabstopGroupsFromTop:
            tabstops = [ wnd for wnd in tabstopgroup.FindByInstance(Container) if getattr(wnd, 'isTabStop', False) ]
            gAbs = tabstopgroup.GetAbsolute()
            for tabstop in tabstops:
                if tabstop.IsClickable():
                    if getattr(tabstop, 'hasFocus', None):
                        current.append(tabstop)
                    tAbs = tabstop.GetAbsolute()
                    sorted.append(([gAbs[1],
                      gAbs[0],
                      tAbs[1],
                      tAbs[0]], tabstop))
                    done.append(tabstop)

        for tabstop in tabstopsFromTop:
            if tabstop not in done and tabstop.IsClickable():
                if getattr(tabstop, 'hasFocus', None) == 1:
                    current.append(tabstop)
                tAbs = tabstop.GetAbsolute()
                sorted.append(([tAbs[1],
                  tAbs[0],
                  tAbs[1],
                  tAbs[0]], tabstop))
                done.append(tabstop)

        if current:
            current = current[0]
        return (current, SortListOfTuples(sorted))

    def GetModalResult(self, default, funcname = 'btn_default'):
        result = None
        modal = self.GetModalWindow()
        if modal:
            result = default
            for wndType in ('trinity.Tr2Sprite2dContainer', 'trinity.Tr2Sprite2d'):
                for c in modal.Find(wndType):
                    if getattr(c, funcname, 0):
                        result = c.btn_modalresult
                        break

        return result

    def BlockConfirm(self):
        self._blockConfirm = 1

    def Confirm(self, starter = None):
        if self._blockConfirm:
            self._blockConfirm = 0
            return False
        if uicore.imeHandler and uicore.imeHandler.IsVisible():
            return
        focus = self.GetFocus()
        active = self.GetActive()
        modal = self.GetModalWindow()
        if modal:
            if focus and focus.IsUnder(modal):
                if hasattr(focus, 'Confirm') and focus != starter:
                    return uthread.new(focus.Confirm)
            if hasattr(modal, 'Confirm') and modal != starter:
                if not getattr(modal, 'blockconfirmonreturn', 0) or uicore.uilib.Key(uiconst.VK_CONTROL):
                    modal.Confirm()
                    return True
            else:
                result = self.GetModalResult(uiconst.ID_OK)
                modal.SetModalResult(result)
                return True
            return False
        if getattr(focus, 'Confirm', None) and focus != starter:
            uthread.new(focus.Confirm)
            return True
        if hasattr(active, 'IsCurrentDialog') and active.IsCurrentDialog():
            active.SetModalResult(uiconst.ID_OK)
            return True
        if getattr(active, 'Confirm', None) and active != starter:
            uthread.new(active.Confirm)
            return True
        if focus and focus.HasEventHandler('OnClick'):
            uthread.new(focus.OnClick, focus)
            return True
        if focus:
            searchFrom = self.GetTopLevelWindowAboveItem(focus)
        else:
            searchFrom = uicore.desktop
        if searchFrom:
            wnds = [ w for w in searchFrom.Find('trinity.Tr2Sprite2dContainer') + searchFrom.Find('trinity.Tr2Sprite2d') if getattr(w, 'btn_default', 0) == 1 ]
            if len(wnds):
                for wnd in wnds:
                    if starter and starter == wnd:
                        continue
                    if wnd.IsVisible():
                        if wnd.HasEventHandler('OnClick'):
                            uthread.new(wnd.OnClick, wnd)
                        return True

        return False

    def AddToListGroup(self, listID_groupID, add):
        listID = unicode(listID_groupID[0])
        groupID = unicode(listID_groupID[1])
        groups = self.GetAllGroups()
        if listID in groups and groupID in groups[listID] and 'groupItems' in groups[listID][groupID] and add not in groups[listID][groupID]['groupItems']:
            groups[listID][groupID]['groupItems'].append(add)
        try:
            if hasattr(settings, 'char'):
                settings.char.WriteToDisk()
        except:
            print 'Failed to write settings.char to disk'

    def RemoveFromListGroup(self, listID_groupID, rem):
        listID = unicode(listID_groupID[0])
        groupID = unicode(listID_groupID[1])
        groups = self.GetAllGroups()
        if listID in groups and groupID in groups[listID] and 'groupItems' in groups[listID][groupID] and rem in groups[listID][groupID]['groupItems']:
            groups[listID][groupID]['groupItems'].remove(rem)
        self.ReloadGroupWindow(listID_groupID)
        try:
            if hasattr(settings, 'char'):
                settings.char.WriteToDisk()
        except:
            print 'Failed to write settings.char to disk'

    def ReloadGroupWindow(self, listID_groupID):
        wnd = self.GetWindow(unicode(listID_groupID))
        if wnd:
            wnd.LoadContent()

    def AddListGroup(self, listID, listgroupName = None):
        from eve.client.script.ui.util.utilWindows import NamePopup
        groupname = NamePopup(localization.GetByLabel('/Carbon/UI/Common/TypeName'), localization.GetByLabel('/Carbon/UI/Common/TypeNameForFolder'))
        if not groupname:
            return
        if isinstance(groupname, dict):
            groupname = groupname['name']
        id = (listID, listgroupName or str(blue.os.GetWallclockTime()))
        group = self.GetListGroup(id)
        group['label'] = groupname
        group['id'] = id
        group['groupItems'] = []
        group['open'] = 0
        return group

    def GetLockedGroup(self, listID, listgroupName, label, openState = 0):
        id = (listID, listgroupName)
        group = self.GetListGroup(id)
        group['label'] = label
        group['id'] = id
        group['groupItems'] = []
        group['open'] = openState
        group['state'] = 'locked'
        return group

    def GetListGroup(self, listID_groupID):
        listID = unicode(listID_groupID[0])
        groupID = unicode(listID_groupID[1])
        if groupID in self.GetListGroups(listID):
            return self.GetListGroups(listID)[groupID]
        self.GetListGroups(listID)[groupID] = {}
        return self.GetListGroup(listID_groupID)

    def GetListGroups(self, listID):
        listID = unicode(listID)
        groups = self.GetAllGroups()
        if listID in groups:
            return groups[listID]
        groups[listID] = {}
        return self.GetListGroups(listID)

    def ChangeListGroupLabel(self, listID_groupID, newlabel):
        group = self.GetListGroup(listID_groupID)
        group['label'] = newlabel
        try:
            if hasattr(settings, 'char'):
                settings.char.WriteToDisk()
        except:
            print 'Failed to write settings.char to disk'

    def GetAllGroups(self):
        try:
            if hasattr(settings, 'char'):
                if settings.char.ui.Get('listgroups', None) is None:
                    settings.char.ui.Set('listgroups', {})
                return settings.char.ui.Get('listgroups', {})
        except:
            print 'Failed to fetch group settings'

        return {}

    def DeleteListGroup(self, listID_groupID):
        listID = unicode(listID_groupID[0])
        groupID = unicode(listID_groupID[1])
        groups = self.GetAllGroups()
        if listID in groups and groupID in groups[listID]:
            del groups[listID][groupID]
        try:
            if hasattr(settings, 'char'):
                settings.char.WriteToDisk()
        except:
            print 'Failed to write settings.char to disk'

    def GetGroupIDFromItemID(self, listID, itemID):
        groups = self.GetAllGroups()
        if listID in groups:
            for groupID in groups[listID].iterkeys():
                if itemID in groups[listID][groupID]['groupItems']:
                    return (listID, groupID)

    def GetListGroupOpenState(self, listID_groupID, default = False):
        listID = unicode(listID_groupID[0])
        groupID = unicode(listID_groupID[1])
        groups = self.GetAllGroups()
        return groups.get(listID, {}).get(groupID, {}).get('open', default)

    def SetListGroupOpenState(self, listID_groupID, state):
        listID = unicode(listID_groupID[0])
        groupID = unicode(listID_groupID[1])
        groups = self.GetAllGroups()
        if listID not in groups:
            groups[listID] = {}
        if groupID not in groups[listID]:
            groups[listID][groupID] = {}
        if listID in groups and groupID in groups[listID]:
            groups[listID][groupID]['open'] = state
        try:
            if hasattr(settings, 'char'):
                settings.char.WriteToDisk()
        except:
            print 'Failed to write settings.char to disk'

    def ToggleCollapseAllWindows(self):
        if self.toggleState is None:
            self.toggleState = settings.char.windows.Get('windowToggleState', [])
        if self.toggleState:

            def RegisterAsNotCollapsed(myWndID):
                allWnds = settings.char.windows.Get('collapsedWindows', {})
                allWnds[myWndID] = False
                settings.char.windows.Set('collapsedWindows', allWnds)

            for windowID in self.toggleState:
                wnd = self.GetWindow(windowID)
                if wnd and wnd.IsCollapsed():
                    wnd.Expand()
                else:
                    wID = windowID
                    if GetRegisteredState(wID, 'collapsed'):
                        RegisterAsNotCollapsed(wID)

            self.toggleState = []
            settings.char.windows.Set('windowToggleState', self.toggleState)
            return
        state = []
        wnds = self.GetValidWindows(floatingOnly=True)
        for wnd in wnds:
            if not getattr(wnd, 'windowID', None):
                continue
            windowID = wnd.windowID
            if not wnd.IsCollapsed():
                wnd.Collapse()
                state.append(windowID)

        if not state:
            for wnd in wnds:
                if wnd.IsCollapsed():
                    wnd.Expand()

        self.toggleState = state
        settings.char.windows.Set('windowToggleState', self.toggleState)

    def ResetToggleStateForWnd(self, windowID):
        if self.toggleState and windowID in self.toggleState:
            self.toggleState.remove(windowID)
            settings.char.windows.Set('windowToggleState', self.toggleState)


def FindTabStopGroupsAndTabstops(fromwhere):
    tabstopgroups = set()
    tabstops = set()
    for wnd in fromwhere.FindByInstance(Container):
        if getattr(wnd, 'isTabOrderGroup', None) and wnd.IsVisible():
            tabstopgroups.add(wnd)
        if getattr(wnd, 'isTabStop', False):
            tabstops.add(wnd)

    return (tabstopgroups, tabstops)
