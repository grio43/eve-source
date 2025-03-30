#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\uisvc.py
import math
import sys
import weakref
import blue
import log
import carbonui.const as uiconst
import uthread
from carbon.common.script.sys.service import Service
from carbon.common.script.util import mathUtil
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.common.script.sys.idCheckers import IsStation
UI_LAYER_NAMES = ('abovemain', 'bracket', 'charsel', 'intro', 'login', 'main', 'shipui', 'tactical', 'target', 'space_ui')

class UI(Service):
    __update_on_reload__ = 0
    __guid__ = 'svc.ui'
    __dependencies__ = ['settings']
    __notifyevents__ = []

    def Run(self, *etc):
        Service.Run(self, *etc)
        self.stationsdata = None
        self.blinksA = {}
        self.blinksRGB = {}
        self.blink_running = False
        self.knownNonStations = set()
        self.stationNames = {}
        self.hiddenLayers = weakref.WeakSet()
        self._hidden = False
        self._suppressed = False
        self._can_be_toggled = True
        self.cursorSurfaces = {}
        uicore.event.RegisterForTriuiEvents([uiconst.UI_KEYUP], self.CheckKeyUp)

    def Stop(self, memStream = None):
        self.LogInfo('Stopping UI Service')
        self.blink_running = False
        self.cursorSurfaces.clear()

    def StopBlink(self, sprite):
        if not getattr(self, 'blink_running', False):
            return
        if not hasattr(self, 'remPending'):
            self.remPending = []
        self.remPending.append(id(sprite))

    def BlinkSpriteA(self, sprite, a, time = 1000.0, maxCount = 10, passColor = 1, minA = 0.0, timeFunc = blue.os.GetWallclockTime):
        if not hasattr(self, 'blinksA'):
            self.blinksA = {}
        key = id(sprite)
        self.blinksA[key] = (sprite,
         a,
         minA,
         time,
         maxCount,
         passColor,
         timeFunc)
        if key in getattr(self, 'remPending', []):
            self.remPending.remove(key)
        if not getattr(self, 'blink_running', False):
            self.blink_running = True
            uthread.new(self._BlinkThread)

    def BlinkSpriteRGB(self, sprite, r, g, b, time = 1000.0, maxCount = 10, passColor = 1, timeFunc = blue.os.GetWallclockTime):
        if not hasattr(self, 'blinksRGB'):
            self.blinksRGB = {}
        key = id(sprite)
        self.blinksRGB[key] = (sprite,
         r,
         g,
         b,
         time,
         maxCount,
         passColor,
         timeFunc)
        if key in getattr(self, 'remPending', []):
            self.remPending.remove(key)
        if not getattr(self, 'blink_running', False):
            self.blink_running = True
            uthread.new(self._BlinkThread)

    def _BlinkThread(self):
        startTimes = {}
        countsA = {}
        countsRGB = {}
        if not hasattr(self, 'blinksA'):
            self.blinksA = {}
        if not hasattr(self, 'blinksRGB'):
            self.blinksRGB = {}
        try:
            while 1:
                if not self:
                    return
                diffTimes = {}
                rem = []
                for key, each in self.blinksA.iteritems():
                    sprite, a, minA, time, maxCount, passColor, timeFunc = each
                    if not sprite or sprite.destroyed:
                        rem.append(key)
                        continue
                    if passColor and getattr(sprite, 'tripass', None):
                        color = sprite.tripass.textureStage0.customColor
                    else:
                        color = sprite.color
                    if key in getattr(self, 'remPending', []):
                        rem.append(key)
                        color.a = minA or a
                        continue
                    now = timeFunc()
                    try:
                        diff = blue.os.TimeDiffInMs(now, startTimes[timeFunc])
                    except KeyError:
                        startTimes[timeFunc] = now
                        diff = 0

                    pos = diff % time
                    if pos < time / 2.0:
                        ndt = min(pos / (time / 2.0), 1.0)
                        color.a = mathUtil.Lerp(a, minA, ndt)
                    else:
                        ndt = min((pos - time / 2.0) / (time / 2.0), 1.0)
                        color.a = mathUtil.Lerp(minA, a, ndt)
                    if key not in countsA:
                        countsA[key] = timeFunc()
                    if maxCount and blue.os.TimeDiffInMs(countsA[key], timeFunc()) / time > maxCount:
                        rem.append(key)
                        color.a = minA or a
                        if key in countsA:
                            del countsA[key]

                for each in rem:
                    if each in self.blinksA:
                        del self.blinksA[each]

                rem = []
                for key, each in self.blinksRGB.iteritems():
                    sprite, r, g, b, time, maxCount, passColor, timeFunc = each
                    if not sprite or sprite.destroyed:
                        rem.append(key)
                        continue
                    if passColor and getattr(sprite, 'tripass', None):
                        color = sprite.tripass.textureStage0.customColor
                    else:
                        color = sprite.color
                    if key in getattr(self, 'remPending', []):
                        rem.append(key)
                        color.r = r
                        color.g = g
                        color.b = b
                        continue
                    now = timeFunc()
                    try:
                        diff = blue.os.TimeDiffInMs(now, startTimes[timeFunc])
                    except KeyError:
                        startTimes[timeFunc] = now
                        diff = 0

                    pos = diff % time
                    if pos < time / 2.0:
                        ndt = min(pos / (time / 2.0), 1.0)
                        color.r = mathUtil.Lerp(r, 0.0, ndt)
                        color.g = mathUtil.Lerp(g, 0.0, ndt)
                        color.b = mathUtil.Lerp(b, 0.0, ndt)
                    else:
                        ndt = min((pos - time / 2.0) / (time / 2.0), 1.0)
                        color.r = mathUtil.Lerp(0.0, r, ndt)
                        color.g = mathUtil.Lerp(0.0, g, ndt)
                        color.b = mathUtil.Lerp(0.0, b, ndt)
                    if key not in countsRGB:
                        countsRGB[key] = timeFunc()
                    if maxCount and blue.os.TimeDiffInMs(countsRGB[key], timeFunc()) / time > maxCount:
                        rem.append(key)
                        color.r = r
                        color.g = g
                        color.b = b
                        if key in countsRGB:
                            del countsRGB[key]

                for each in rem:
                    if each in self.blinksRGB:
                        del self.blinksRGB[each]

                self.remPending = []
                if not len(self.blinksA) and not len(self.blinksRGB) or not self.blink_running:
                    self.blinksA = {}
                    self.blinksRGB = {}
                    self.blink_running = False
                    break
                blue.pyos.synchro.Yield()

        except Exception:
            self.blink_running = False
            log.LogException()
            sys.exc_clear()

    def Rotate(self, uitransform, time = 1.0, fromRot = 360.0, toRot = 0.0, timeFunc = blue.os.GetWallclockTime):
        uthread.new(self._Rotate, uitransform, time, fromRot, toRot, timeFunc)

    def _Rotate(self, uitransform, time, fromRot, toRot, timeFunc):
        time *= 1000
        i = 0
        while not uitransform.destroyed:
            start, ndt = timeFunc(), 0.0
            while ndt != 1.0:
                ndt = max(ndt, min(blue.os.TimeDiffInMs(start, timeFunc()) / time, 1.0))
                deg = mathUtil.Lerp(fromRot, toRot, ndt)
                rad = math.radians(deg)
                uitransform.SetRotation(rad)
                blue.pyos.synchro.Yield()

    def Browse(self, msgkey, dict):
        if msgkey == 'BrowseHtml':
            blue.os.ShellExecute(dict['url'])
        elif msgkey == 'BrowseIGB':
            uicore.cmd.GetCommandAndExecute('OpenBrowser', **dict)

    def ForceCursorUpdate(self):
        if uicore.uilib:
            uicore.UpdateCursor(uicore.uilib.mouseOver, 1)

    def IsNotificationCenterAvailable(self):
        notificationUi = sm.GetServiceIfRunning('notificationUIService')
        return notificationUi and notificationUi.IsAvailable()

    def CheckKeyUp(self, wnd, msgID, vkey_flag):
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        alt = uicore.uilib.Key(uiconst.VK_MENU)
        vkey, flag = vkey_flag
        if hasattr(wnd, 'KeyUp') and not wnd.destroyed:
            if wnd.KeyUp(vkey, flag):
                return 1
        if vkey == uiconst.VK_CONTROL:
            return self.CheckCtrlUp(wnd, msgID, vkey)
        return 1

    def CheckCtrlUp(self, wnd, msgID, ckey):
        if eve.chooseWndMenu and not eve.chooseWndMenu.destroyed and eve.chooseWndMenu.state != uiconst.UI_HIDDEN:
            eve.chooseWndMenu.ChooseHilited()
        eve.chooseWndMenu = None
        return 1

    def GetStation(self, stationid):
        if self.stationsdata is None:
            data = sm.RemoteSvc('map').GetStationInfo()
            self.stationsdata = data.Index('stationID')
        return self.stationsdata.get(stationid, None)

    def GetStationStaticInfo(self, stationID):
        if stationID in cfg.oldStations:
            return cfg.oldStations.Get(stationID)
        try:
            if IsStation(stationID) and stationID not in self.knownNonStations:
                return cfg.stations.Get(stationID)
        except RuntimeError:
            self.knownNonStations.add(stationID)

    def GetStationName(self, stationID):
        try:
            return self.stationNames[stationID]
        except KeyError:
            stationName = cfg.evelocations.Get(stationID).locationName
            self.stationNames[stationID] = stationName
            return stationName

    def GetStationSolarSystem(self, stationID):
        stationInfo = self.GetStationStaticInfo(stationID)
        return stationInfo.solarSystemID

    def GetStationOwner(self, stationID):
        stationInfo = self.GetStationStaticInfo(stationID)
        return stationInfo.ownerID

    def IsUiVisible(self):
        return not self._hidden and not self._suppressed

    def IsUIHidden(self):
        return self._hidden

    def IsUISuppressed(self):
        return self._suppressed

    def GetHiddenLayers(self):
        return self.hiddenLayers

    def SetUiToggleState(self, can_be_toggled):
        self._can_be_toggled = can_be_toggled

    def HideUi(self, duration = None, except_layers = None):
        if self._hidden:
            return
        if except_layers is None:
            except_layers = []
        layers = filter(None, map(uicore.layer.Get, UI_LAYER_NAMES))
        for layer in layers:
            if layer in except_layers:
                continue
            if duration:
                animations.FadeOut(layer, duration=duration, callback=layer.Hide)
            else:
                layer.state = uiconst.UI_HIDDEN
            self.hiddenLayers.add(layer)

        self._hidden = True
        if not self._suppressed:
            sm.ScatterEvent('OnHideUI')

    def ShowUi(self, duration = None, except_layers = None):
        if self._suppressed:
            self.hiddenLayers.clear()
            self._hidden = False
            return
        if not self._hidden:
            return
        if except_layers is None:
            except_layers = []
        for layer in self.hiddenLayers:
            if layer in except_layers:
                continue
            layer.state = uiconst.UI_PICKCHILDREN
            if duration:
                animations.FadeIn(layer, duration=duration)
            else:
                layer.opacity = 1.0

        self.hiddenLayers.clear()
        self._hidden = False
        if not self._suppressed:
            sm.ScatterEvent('OnShowUI')

    def ToggleUiVisible(self):
        if not self._can_be_toggled:
            return
        if self._hidden:
            self.ShowUi()
        else:
            self.HideUi()

    def SuppressUI(self, duration = None):
        if self._suppressed:
            return
        layers = filter(None, map(uicore.layer.Get, UI_LAYER_NAMES))
        for layer in layers:
            if layer in self.hiddenLayers:
                continue
            if duration:
                animations.FadeOut(layer, duration=duration, callback=layer.Hide)
            else:
                layer.state = uiconst.UI_HIDDEN

        self._suppressed = True
        if not self._hidden:
            sm.ScatterEvent('OnHideUI')

    def UnsuppressUI(self, duration = None):
        if not self._suppressed:
            return
        layers = filter(None, map(uicore.layer.Get, UI_LAYER_NAMES))
        for layer in layers:
            if self.hiddenLayers and layer in self.hiddenLayers:
                continue
            layer.state = uiconst.UI_PICKCHILDREN
            if duration:
                animations.FadeIn(layer, duration=duration)
            else:
                layer.opacity = 1.0

        self._suppressed = False
        if not self._hidden:
            sm.ScatterEvent('OnShowUI')
