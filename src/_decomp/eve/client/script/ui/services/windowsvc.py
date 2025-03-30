#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\windowsvc.py
import weakref
from carbonui.primitives.fill import Fill
from carbonui.window.layout import apply_desktop_window_layout, capture_desktop_window_layout
from eve.client.script.ui import eveColor
from carbon.common.script.sys.service import Service
from carbonui.control.window import Window
from carbonui.window.settings import ResetAllWindowSettings
from carbonui.window.stack import WindowStack
from carbonui.primitives.base import ScaleDpi
from carbonui.util.various_unsorted import Transplant
import carbonui.const as uiconst
import evegraphics.settings as gfxsettings
from carbonui.uicore import uicore
from eve.client.script.ui.inflight.drones.dronesWindow import DronesWindow
from eve.client.script.ui.inflight.overview.overviewWindow import OverviewWindow
from eve.client.script.ui.inflight.selectedItemWnd import SelectedItemWnd
from eve.client.script.ui.services import sessionChangeWindowOpener
from eve.client.script.ui.shared.fleet.fleet import WatchListPanel
from chat.client.window import ChatWindow
from xmppchatclient.xmppchatwindow import XmppChatWindow

class WindowMgr(Service):
    __guid__ = 'svc.window'
    __servicename__ = 'window'
    __displayname__ = 'Window Service'
    __dependencies__ = ['form']
    __notifyevents__ = ['DoSessionChanging',
     'OnSessionChanged',
     'OnEndChangeDevice',
     'ProcessDeviceChange',
     'OnBlurredBufferCreated',
     'OnHideUI',
     'OnShowUI',
     'OnBeforeViewStateChanged',
     'OnViewStateChanged',
     'OnWindowMaximized']
    __startupdependencies__ = ['settings']

    def Run(self, memStream = None):
        self.LogInfo('Starting Window Service')
        self.wndIntersectionsByRects = {}
        self.windowsMinimizedByFullscreenView = weakref.WeakSet()

    def Stop(self, memStream = None):
        self.LogInfo('Stopping Window Service')
        Service.Stop(self)

    def ProcessDeviceChange(self, *args):
        self.PreDeviceChange_DesktopLayout = capture_desktop_window_layout()

    def OnEndChangeDevice(self, *args):
        self.RealignWindows()
        sm.GetService('device').SetupUIScaling()

    def OnBeforeViewStateChanged(self, oldViewName, newViewName):
        if not oldViewName:
            return
        viewStateSvc = sm.GetService('viewState')
        newViewInfo = viewStateSvc.GetViewInfo(newViewName)
        if newViewInfo.IsSecondary():
            self._OnEnteringSecondaryView()

    def OnViewStateChanged(self, oldViewName, newViewName):
        if not oldViewName:
            return
        viewStateSvc = sm.GetService('viewState')
        oldViewInfo = viewStateSvc.GetViewInfo(oldViewName)
        newViewInfo = viewStateSvc.GetViewInfo(newViewName)
        if newViewInfo.IsPrimary() and oldViewInfo.IsSecondary():
            self._OnExitingSecondaryView()

    def _OnEnteringSecondaryView(self):
        for wnd in uicore.registry.GetValidWindows(floatingOnly=True, getHidden=True):
            if not wnd.IsOverlayed() and not wnd.minimized:
                wnd.Minimize(animate=False)
                self.RegisterAsMinimizedByFullscreenView(wnd)

    def RegisterAsMinimizedByFullscreenView(self, wnd):
        self.windowsMinimizedByFullscreenView.add(wnd)

    def _OnExitingSecondaryView(self):
        shouldMaximze = []
        for wnd in self.windowsMinimizedByFullscreenView:
            if not wnd.destroyed:
                shouldMaximze.append(wnd)

        for wnd in shouldMaximze:
            wnd.Maximize(retainOrder=True)

    def OnWindowMaximized(self, wnd, wasMinimized):
        if wnd in self.windowsMinimizedByFullscreenView:
            self.windowsMinimizedByFullscreenView.remove(wnd)

    def ValidateWindows(self):
        d = uicore.desktop
        all = uicore.registry.GetValidWindows(1, floatingOnly=True)
        for wnd in all:
            if wnd.align != uiconst.RELATIVE:
                continue
            wnd.left = max(-wnd.width + 64, min(d.width - 64, wnd.left))
            wnd.top = max(0, min(d.height - wnd.GetCollapsedHeight(), wnd.top))

    def DoSessionChanging(self, isRemote, session, change):
        if not session.charid:
            for layer in (uicore.layer.starmap,):
                for each in layer.children:
                    each.Close()

    def OnSessionChanged(self, isRemote, session, change):
        if sm.GetService('connection').IsConnected() and self.IsLocationChange(change):
            sessionChangeWindowOpener.OnSessionChanged()

    def IsLocationChange(self, change):
        if 'locationid' in change:
            return True
        if 'structureid' in change:
            return True
        if 'shipid' in change and session.structureid in change['shipid']:
            return True
        return False

    def OnHideUI(self, *args):
        self.UpdateIntersectionBackground()

    def OnShowUI(self, *args):
        self.UpdateIntersectionBackground()

    def ResetWindowSettings(self):
        openWindowStacks = []
        openWindows = []
        for wnd in uicore.registry.GetWindows():
            if not isinstance(wnd, Window):
                continue
            if wnd.isDialog:
                continue
            if wnd.parent != uicore.layer.main:
                Transplant(wnd, uicore.layer.main)
            if isinstance(wnd, WindowStack):
                openWindowStacks.append(wnd)
            else:
                openWindows.append(wnd)

        for wnd in openWindowStacks:
            wnd.Close()

        sm.GetService('device').SetupUIScaling()
        ResetAllWindowSettings()
        favorClasses = [XmppChatWindow,
         ChatWindow,
         SelectedItemWnd,
         OverviewWindow,
         DronesWindow,
         WatchListPanel]
        openWindows = sorted(openWindows, key=lambda wnd: wnd.__class__ in favorClasses, reverse=True)
        for wnd in openWindows:
            wnd.OnResetWindowSettings()

        settings.user.ui.Delete('targetOrigin')
        sm.GetService('target').ArrangeTargets()

    def RealignWindows(self):
        desktopLayout = getattr(self, 'PreDeviceChange_DesktopLayout', None)
        if desktopLayout:
            apply_desktop_window_layout(desktopLayout)
        self.PreDeviceChange_DesktopLayout = None
        if session.charid:
            sm.GetService('target').ArrangeTargets()

    def OnBlurredBufferCreated(self):
        self.UpdateIntersectionBackground()

    def GetWindowIntersectionRects(self):
        ret = set()
        wndRects = self.GetWindowRects()
        numWnds = len(wndRects)
        for i in xrange(numWnds):
            for j in xrange(i + 1, numWnds):
                wnd1 = wndRects[i]
                wnd2 = wndRects[j]
                if self.IsIntersecting(wnd1, wnd2):
                    ret.add(self.GetIntersection(wnd1, wnd2))

        return ret

    def UpdateIntersectionBackground(self):
        desktop = uicore.uilib.desktopBlurredBg
        if not desktop:
            return
        currRects = self.GetWindowIntersectionRects()
        toRemove = [ rect for rect in self.wndIntersectionsByRects.keys() if rect not in currRects ]
        for rect in toRemove:
            intersection = self.wndIntersectionsByRects.pop(rect)
            intersection.Close()

        toCreate = [ rect for rect in currRects if rect not in self.wndIntersectionsByRects ]
        for x1, y1, x2, y2 in toCreate:
            intersection = Fill(parent=desktop, pos=(x1,
             y1,
             x2 - x1,
             y2 - y1), align=uiconst.TOPLEFT, padding=1, color=eveColor.BLACK, opacity=0.5)
            self.wndIntersectionsByRects[x1, y1, x2, y2] = intersection

        desktop.UpdateAlignmentAsRoot()

    def IsIntersecting(self, wnd1, wnd2):
        l1, t1, r1, b1 = wnd1
        l2, t2, r2, b2 = wnd2
        hoverlaps = True
        voverlaps = True
        if l1 >= r2 or r1 <= l2:
            hoverlaps = False
        if t1 >= b2 or b1 <= t2:
            voverlaps = False
        return hoverlaps and voverlaps

    def GetIntersection(self, wnd1, wnd2):
        l1, t1, r1, b1 = wnd1
        l2, t2, r2, b2 = wnd2
        left = max(l1, l2)
        top = max(t1, t2)
        right = min(r1, r2)
        bottom = min(b1, b2)
        return (left,
         top,
         right,
         bottom)

    def GetWindowRects(self):
        windows = uicore.registry.GetValidWindows()
        ret = [ (wnd.displayX,
         wnd.displayY,
         wnd.displayX + wnd.displayWidth,
         wnd.displayY + wnd.displayHeight) for wnd in windows ]
        neocom = sm.GetService('neocom').GetNeocomContainer()
        if neocom:
            l, t, w, h = neocom.GetAbsolute()
            ret.append((ScaleDpi(l),
             ScaleDpi(t),
             ScaleDpi(l + w),
             ScaleDpi(t + h)))
        return ret

    def GetCameraLeftOffset(self, width, align = None, left = 0, *args):
        offset = self.GetCameraOffsetSettingValue()
        if not offset:
            return 0
        if align in [uiconst.CENTER, uiconst.CENTERTOP, uiconst.CENTERBOTTOM]:
            camerapush = int(offset / 100.0 * uicore.desktop.width / 3.0)
            allowedOffset = int((uicore.desktop.width - width) / 2) - 10
            if camerapush < 0:
                return max(camerapush, -allowedOffset - left)
            if camerapush > 0:
                return min(camerapush, allowedOffset + left)
        return 0

    def GetCameraOffsetSettingValue(self):
        try:
            offsetUI = gfxsettings.Get(gfxsettings.UI_OFFSET_UI_WITH_CAMERA)
        except gfxsettings.UninitializedSettingsGroupError:
            offsetUI = False

        if not offsetUI:
            return 0
        else:
            return int(gfxsettings.Get(gfxsettings.UI_CAMERA_OFFSET))
