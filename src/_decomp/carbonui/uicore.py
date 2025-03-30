#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\uicore.py
import weakref
import blue
import carbonui
from carbonui import uiconst
import carbonui.uianimations
import carbonui.uilib
import carbonui.util.effect
import localization
from carbonui.util.color import Color
from eveprefs import boot
import evespacemouse
import log
import trinity

class UIDeviceResource():

    def __init__(self):
        dev = trinity.device
        dev.RegisterResource(self)

    def OnInvalidate(self, level):
        pass

    def OnCreate(self, dev):
        if getattr(uicore, 'uilib', None) is None:
            return
        uicore.UpdateCursor(uicore.uilib.mouseOver, 1)


def _ExecuteSpaceMouseAction(action):
    cmd = uicore.cmd.GetCommandToExecute(action)
    if cmd:
        cmd()
        raise evespacemouse.StopPropagation()


class UICore():
    fontHandler = None
    audioHandler = None
    imeHandler = None
    commandHandler = None
    tooltipHandler = None
    dpiScaling = 1.0

    def __init__(self, appName = None):
        import __builtin__
        if 'uicore' in __builtin__.__dict__.keys():
            pass
        else:
            if appName is None:
                try:
                    appName = boot.appname
                except:
                    appName = 'CarbonUI'

            self.newRendererEnabled = False
            self._lastCursor = None
            self._cursorSprite = None
            self._hint = None
            self.isRunning = False
            self.desktop = None
            self.dragData = None
            self.uilib = None
            self.dragObject = None
            self.triappargs = {'title': appName,
             'left': 0,
             'top': 0,
             'colordepth': 0,
             'exclusiveInput': 0,
             'refreshrate': 0}
        self.textObjects = weakref.WeakSet()
        self.deviceResource = UIDeviceResource()

    def Startup(self, layerlist = None, clientStartup = True):
        if clientStartup:
            sm.GetService('settings').LoadSettings()
            deviceSvc = sm.StartServiceAndWaitForRunningState('device')
            deviceSvc.CreateDevice()
            self.device = deviceSvc
            evespacemouse.Enable()
            evespacemouse.StartListening(None, None, _ExecuteSpaceMouseAction, 1000)
        self.uilib = self.event = carbonui.uilib.Uilib()
        self.desktop = self.uilib.desktop
        if self.fontHandler is None:
            self.LoadBaseFontHandler()
        if self.audioHandler is None:
            self.LoadBaseAudioHandler()
        from carbonui.services.registry import RegistryHandler
        self.registry = RegistryHandler()
        if clientStartup:
            from carbonui.services.ime import construct_ime_handler
            self.imeHandler = construct_ime_handler()
        self.LoadLayers(layerlist)
        self.effect = carbonui.util.effect.UIEffects()
        self.animations = carbonui.uianimations.animations
        trinity.device.RegisterResource(self)
        from carbonui.window.settings import window_margin_mode
        window_margin_mode.initialize(get_resolution=lambda : (self.desktop.width, self.desktop.height), service_manager=sm)
        self.isRunning = True

    def LoadBaseFontHandler(self):
        from carbonui.services.font import FontHandler
        self.SetFontHandler(FontHandler())

    def SetFontHandler(self, fontHandler):
        self.fontHandler = fontHandler
        self.font = fontHandler

    def LoadBaseAudioHandler(self):
        from carbonui.handlers.audioHandler import AudioHandler
        self.audioHandler = AudioHandler()

    def SetAudioHandler(self, audioHandler):
        self.audioHandler = audioHandler

    def SetCommandHandler(self, commandHandler):
        self.commandHandler = commandHandler
        self.cmd = commandHandler

    def SetTooltipHandler(self, tooltipHandler):
        self.tooltipHandler = tooltipHandler

    def IsReady(self):
        return getattr(self, 'isRunning', False)

    def OnInvalidate(self, *args):
        self.layer.hint.Flush()
        self._hint = None

    def OnCreate(self, *args):
        self.layer.hint.Flush()
        self._hint = None

    def LoadLayers(self, layerlist):
        self.layer = carbonui.control.layer.LayerManager()
        self.layerData = {}
        self.layerList = layerlist
        layerlist = layerlist or self.GetDefaultLayers()
        for layerName, className, subLayers in layerlist:
            self.desktop.AddLayer(layerName, className, subLayers)

    def GetDefaultLayers(self):
        layers = [('l_hint', None, None),
         ('l_menu', None, None),
         ('l_modal', None, None),
         ('l_abovemain', None, None),
         ('l_main', None, None),
         ('l_videoOverlay', None, None),
         ('l_loading', None, None),
         ('l_dragging', None, None)]
        return layers

    def CheckCursor(self):
        self.UpdateCursor(uicore.uilib.mouseOver)

    def CheckHint(self):
        pass

    def UpdateHint(self, item, force = 0):
        pass

    def IsHintVisible(self):
        return self._hint and self._hint.display

    def HideHint(self):
        if self.IsHintVisible():
            self._hint.LoadHint('')

    def UpdateCursor(self, item, force = 0):
        if not item:
            cursor = uiconst.UICURSOR_DEFAULT
        else:
            cursor = self._GetCursorForItem(item)
        if force or self._lastCursor != cursor:
            self.uilib.SetCursor(cursor)
            self._lastCursor = cursor

    def _GetCursorForItem(self, item):
        specifiedCursor = self._GetSpecifiedCursorForItem(item)
        if specifiedCursor is not None:
            return specifiedCursor
        if item.HasEventHandler('OnChar'):
            return uiconst.UICURSOR_IBEAM
        hasGetMenu = item.HasEventHandler('GetMenu')
        clickFunc = item.HasEventHandler('OnClick')
        if clickFunc:
            if hasGetMenu:
                return uiconst.UICURSOR_POINTER_MENU
            else:
                return uiconst.UICURSOR_SELECT
        elif hasGetMenu:
            return uiconst.UICURSOR_HASMENU
        return uiconst.UICURSOR_DEFAULT

    def _GetSpecifiedCursorForItem(self, item):
        if hasattr(item, 'GetCursor'):
            specifiedCursor = item.GetCursor()
        else:
            specifiedCursor = getattr(item, 'cursor', None)
        return specifiedCursor

    def GetLayer(self, name):
        return self.layer.GetLayer(name)

    def Message(self, *args, **kw):
        print 'Unhandled carbonui.Message', args, kw

    def WaitForResourceLoad(self):
        fence = trinity.device.GetCurrentResourceLoadFence()
        timeWaited = 0
        while trinity.device.GetLastResourceLoadFenceReached() < fence:
            waitMs = 100
            blue.pyos.synchro.SleepWallclock(waitMs)
            timeWaited += waitMs
            if timeWaited % 5000 == 0:
                log.general.Log('WaitForResourceLoad has waited for %d seconds! (%d vs. %d)' % (timeWaited / 1000, trinity.device.GetLastResourceLoadFenceReached(), fence), log.LGERR)

    def ScaleDpi(self, value):
        return int(round(value * self.dpiScaling))

    def ScaleDpiF(self, value):
        return value * self.dpiScaling

    def ReverseScaleDpi(self, value):
        if self.dpiScaling != 1.0:
            try:
                return int(round(value / self.dpiScaling))
            except (ValueError, OverflowError):
                return 0

        else:
            try:
                return int(value)
            except ValueError:
                return 0

    def IsDragging(self):
        return not self.dragObject == None

    def DrawDebugLine(self, pos1, pos2, width = 2, color1 = None, color2 = None):
        color1 = color1 or Color.YELLOW
        color2 = color2 or Color.RED
        self.ConstructDebugLineset()
        self.debugLineSet.AddStraightLine(pos1, color1, pos2, color2, width)
        self.debugLineSet.SubmitChanges()

    def DrawDebugAxis(self, pos = None, lineWidth = 5, len = 1000.0):
        import geo2
        self.ConstructDebugLineset()
        if not pos:
            pos = (0, 0, 0)
        self.debugLineSet.AddStraightLine(pos, Color.YELLOW, geo2.Add(pos, (len, 0, 0)), Color.YELLOW, lineWidth)
        self.debugLineSet.AddStraightLine(pos, Color.RED, geo2.Add(pos, (0, len, 0)), Color.RED, lineWidth)
        self.debugLineSet.AddStraightLine(pos, Color.GREEN, geo2.Add(pos, (0, 0, len)), Color.GREEN, lineWidth)
        self.debugLineSet.SubmitChanges()

    def ClearDebugLines(self):
        self.debugLineSet.ClearLines()
        self.debugLineSet.SubmitChanges()

    def ConstructDebugLineset(self):
        if hasattr(self, 'debugLineSet'):
            scene = sm.GetService('sceneManager').GetActiveScene()
            if self.debugLineSet in scene.objects:
                return
        self.debugLineSet = trinity.EveCurveLineSet()
        self.debugLineSet.scaling = (1.0, 1.0, 1.0)
        tex2D1 = trinity.TriTextureParameter()
        tex2D1.name = 'TexMap'
        tex2D1.resourcePath = 'res:/texture/global/lineSolid.dds'
        self.debugLineSet.lineEffect.resources.append(tex2D1)
        tex2D2 = trinity.TriTextureParameter()
        tex2D2.name = 'OverlayTexMap'
        tex2D2.resourcePath = 'res:/UI/Texture/Planet/link.dds'
        self.debugLineSet.lineEffect.resources.append(tex2D2)
        scene = sm.GetService('sceneManager').GetActiveScene()
        scene.objects.append(self.debugLineSet)
        return self.debugLineSet


def GetWindowName(characterid = None):
    if characterid is not None:
        return localization.GetByLabel('UI/WindowNameWithCharacterName', player=characterid)
    return localization.GetByLabel('UI/WindowName')


uicore = UICore()
