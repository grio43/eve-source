#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\uilib.py
import math
import weakref
import blue
import log
import telemetry
import carbonui.const as uiconst
import carbonui.control
import evegraphics.settings as gfxsettings
import trinity
import uthread
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.text.settings import font_shadow_enabled_setting
from carbonui.util.weakrefutil import CallableWeakRef
from eve.client.script.ui.services.uiColorSettings import show_window_bg_blur_setting
from eveexceptions import UserError
from logmodule import LogException
DBLCLICKDELAY = 250.0
CLICKCOUNTRESETTIME = 250
HOVERTIME = 250

class Uilib(object):
    __notifyevents__ = ['OnUIScalingChange',
     'OnSessionChanged',
     'OnGraphicSettingsChanged',
     'OnUIColorsChanged',
     'OnFontSizeChanged']
    UTHREADEDEVENTS = (uiconst.UI_CLICK,
     uiconst.UI_DBLCLICK,
     uiconst.UI_TRIPLECLICK,
     uiconst.UI_KEYUP,
     uiconst.UI_KEYDOWN,
     uiconst.UI_MOUSEMOVE)
    EVENTMAP = {uiconst.UI_MOUSEHOVER: 'OnMouseHover',
     uiconst.UI_MOUSEMOVE: 'OnMouseMove',
     uiconst.UI_MOUSEMOVEDRAG: 'OnMouseMoveDrag',
     uiconst.UI_MOUSEENTER: 'OnMouseEnter',
     uiconst.UI_MOUSEEXIT: 'OnMouseExit',
     uiconst.UI_MOUSEDOWN: 'OnMouseDown',
     uiconst.UI_MOUSEDOWNDRAG: 'OnMouseDownDrag',
     uiconst.UI_MOUSEUP: 'OnMouseUp',
     uiconst.UI_MOUSEWHEEL: 'OnMouseWheel',
     uiconst.UI_CLICK: 'OnClick',
     uiconst.UI_DBLCLICK: 'OnDblClick',
     uiconst.UI_TRIPLECLICK: 'OnTripleClick',
     uiconst.UI_KEYDOWN: 'OnKeyDown',
     uiconst.UI_KEYUP: 'OnKeyUp',
     uiconst.UI_CHAR: 'OnChar'}
    tooltipHandler = None
    auxiliaryTooltip = None
    auxiliaryTooltipPosition = None
    cursorPos = (-1, -1)

    def __init__(self, paparazziMode = False):
        if not paparazziMode:
            sm.RegisterNotify(self)
        if len(trinity.textureAtlasMan.atlases) == 0:
            trinity.textureAtlasMan.AddAtlas(trinity.PIXEL_FORMAT.B8G8R8A8_UNORM, 2048, 2048)
        self.textureAtlas = trinity.textureAtlasMan.atlases[0]
        self.textureAtlas.optimizeOnRemoval = False
        self.renderObjectToPyObjectDict = weakref.WeakValueDictionary()
        self.x = -1
        self.y = -1
        self.z = 0
        self.dx = 0
        self.dy = 0
        self.dz = 0
        self._mouseOver = None
        self._auxMouseOverRO = None
        self._capturingMouseItem = None
        self._clickItem = None
        self._mouseTargetObject = None
        self.exclusiveMouseFocusActive = False
        self.appfocusitem = None
        self.selectedCursorType = uiconst.UICURSOR_DEFAULT
        self.centerMouse = False
        self.ignoreDeadChar = None
        self._clickTime = None
        self._clickCount = 0
        self._clickTimer = None
        self._clickPosition = None
        self.rootObjects = []
        self.rootObjectsByName = {}
        self._triuiRegs = {}
        self._triuiRegsByMsgID = {}
        self._mouseButtonStates = {}
        self._mouseDownPosition = {}
        self._appfocusitem = None
        self._modkeysOff = tuple([ 0 for x in uiconst.MODKEYS ])
        self._expandMenu = None
        self._keyDownAcceleratorThread = None
        self.blurredBackBufferRenderJob = None
        self.blurredBackBufferAtlas = None
        self.desktopBlurredBg = None
        self._pickProjection = trinity.TriProjection()
        self._pickView = trinity.TriView()
        self._pickViewport = trinity.TriViewport()
        self.cursorCache = {}
        self.alignIslands = set()
        from carbonui.uicore import uicore
        uicore.uilib = self
        trinity.fontMan.loadFlag = 32
        if not paparazziMode:
            self._SetupRenderJob()
            glowEnabled = gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY) > gfxsettings.SHADER_MODEL_LOW
            self.desktop = self.CreateRootObject('Desktop', renderJob=self.desktopRenderJob, isFullscreen=True, glowEnabled=glowEnabled)
            uthread.new(self.EnableEventHandling)
            from eve.client.script.ui.tooltips.tooltipHandler import TooltipHandler
            self.tooltipHandler = TooltipHandler()
        trinity.device.RegisterResource(self)
        self._hoverThread = None
        self.eventHandlerResolver = None
        self.menuHandlerResolver = None
        show_window_bg_blur_setting.on_change.connect(self.OnWindowBlurSettingChanged)
        font_shadow_enabled_setting.on_change.connect(self._on_font_shadow_enabled_setting_changed)

    def __del__(self, *args):
        trinity.mainWindow.onMouseMove = None
        trinity.mainWindow.onMouseDown = None
        trinity.mainWindow.onMouseUp = None
        trinity.mainWindow.onMouseWheel = None
        trinity.mainWindow.onKeyDown = None
        trinity.mainWindow.onKeyUp = None
        trinity.mainWindow.onChar = None
        if self.renderJob:
            self.renderJob.UnscheduleRecurring()

    def EnableEventHandling(self):
        from carbonui.uicore import uicore
        while not uicore.IsReady():
            blue.synchro.SleepWallclock(1)

        trinity.mainWindow.onMouseMove = self._OnMouseMove
        trinity.mainWindow.onMouseDown = self._OnMouseDown
        trinity.mainWindow.onMouseUp = self._OnMouseUp
        trinity.mainWindow.onMouseWheel = self._OnMouseWheel
        trinity.mainWindow.onKeyDown = self._OnKeyDown
        trinity.mainWindow.onKeyUp = self._OnKeyUp
        trinity.mainWindow.onChar = self._OnChar
        trinity.mainWindow.onFocusChange = self._OnFocusChange
        trinity.mainWindow.onClose = self._OnClose
        log.LogInfo('Uilib event handling enabled')

    def OnInvalidate(self, *args):
        self.cursorCache = {}

    def OnCreate(self, *args):
        uthread.new(self.PrepareBlurredBackBuffer)

    def OnWindowBlurSettingChanged(self, *args):
        self.PrepareBlurredBackBuffer()

    def OnGraphicSettingsChanged(self, *args, **kwargs):
        if self.desktop:
            self.desktop.glowEnabled = gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY) > gfxsettings.SHADER_MODEL_LOW

    def OnUIColorsChanged(self):
        self.desktop.OnColorThemeChanged()

    def OnFontSizeChanged(self):
        self.desktop.OnGlobalFontSizeChanged()

    def _on_font_shadow_enabled_setting_changed(self, value):
        self.desktop.OnGlobalFontShadowChanged()

    def CreateTexture(self, width, height):
        tex = self.textureAtlas.CreateTexture(int(width), int(height))
        return tex

    def CreateRootObject(self, name, width = None, height = None, depthMin = None, depthMax = None, isFullscreen = False, renderTarget = None, renderJob = None, **kwargs):
        from carbonui.primitives.desktop import UIRoot
        desktop = UIRoot(pos=(0,
         0,
         width or trinity.mainWindow.width,
         height or trinity.mainWindow.height), name=name, depthMin=depthMin, depthMax=depthMax, isFullscreen=isFullscreen, renderTarget=renderTarget, renderJob=renderJob, **kwargs)
        self.AddRootObject(desktop)
        return desktop

    def GetRenderJob(self):
        return self.desktopRenderJob

    def GetVideoJob(self):
        return self.videoJob

    def OnUIScalingChange(self, *args):
        self.PrepareBlurredBackBuffer()

    def PrepareBlurredBackBuffer(self):
        if self.blurredBackBufferRenderJob:
            renderJob = self.blurredBackBufferRenderJob
            renderJob.enabled = True
            for step in renderJob.steps[:]:
                renderJob.steps.remove(step)

        else:
            renderJob = trinity.CreateRenderJob()
            renderJob.name = 'Blurred Back Buffer'
            renderJob.ScheduleRecurring(insertFront=True)
            self.blurredBackBufferRenderJob = renderJob
        gfxShaderSettingSupportsBlur = gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY) > gfxsettings.SHADER_MODEL_LOW
        if not (show_window_bg_blur_setting.is_enabled() and gfxShaderSettingSupportsBlur):
            if self.blurredBackBufferRenderJob:
                self.blurredBackBufferRenderJob.enabled = False
            return
        backbuffer = trinity.device.GetRenderContext().GetDefaultBackBuffer()
        self.spaceSceneBackBufferCopy = trinity.Tr2RenderTarget(trinity.mainWindow.width, trinity.mainWindow.height, 1, backbuffer.format)
        self.spaceSceneBackBufferDownSizedCopy = trinity.Tr2RenderTarget(trinity.mainWindow.width / 4, trinity.mainWindow.height / 4, 1, trinity.PIXEL_FORMAT.B8G8R8X8_UNORM)
        self.spaceSceneBackBufferDownSizedCopy.name = 'spaceSceneBackBufferDownSizedCopy'
        step = trinity.TriStepResolve(self.spaceSceneBackBufferCopy, backbuffer)
        step.name = 'Resolve back buffer'
        renderJob.steps.append(step)
        if self.desktopBlurredBg:
            self.RemoveRootObject(self.desktopBlurredBg)
            self.desktopBlurredBg.Close()
        self.desktopBlurredBg = self.CreateRootObject(name='desktopBlurred', renderTarget=self.spaceSceneBackBufferCopy, renderJob=renderJob, isFullscreen=True)
        self.desktopBlurredBg.renderObject.clearBackground = False
        renderJob.PushDepthStencil().pushCurrent = False
        renderJob.SetVariableStore('BlitCurrent', self.spaceSceneBackBufferCopy).name = 'Set BlitCurrent variable'
        value = (1.0 / trinity.mainWindow.width,
         1.0 / trinity.mainWindow.height,
         trinity.mainWindow.width,
         trinity.mainWindow.height)
        renderJob.SetVariableStore('g_texelSize', value).name = 'Set g_texelSize variable'
        renderJob.PushRenderTarget(self.spaceSceneBackBufferDownSizedCopy)
        renderJob.Clear((0, 0, 0, 0))
        effect = trinity.Tr2Effect()
        effect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/PostProcess/ColorDownFilter4.fx'
        renderJob.RenderEffect(effect)
        renderJob.PopRenderTarget()
        renderJob.PopDepthStencil()
        textureRes = trinity.TriTextureRes()
        textureRes.SetFromRenderTarget(self.spaceSceneBackBufferDownSizedCopy)
        atlasTexture = trinity.Tr2AtlasTexture()
        atlasTexture.textureRes = textureRes
        self.blurredBackBufferAtlas = atlasTexture
        sm.ScatterEvent('OnBlurredBufferCreated')

    def _SetupRenderJob(self):
        self.renderJob = trinity.CreateRenderJob()
        self.renderJob.name = 'UI'
        self.PrepareBlurredBackBuffer()
        self.sceneViewStep = self.renderJob.SetView()
        self.scaledViewportStep = self.renderJob.SetViewport()
        self.sceneProjectionStep = self.renderJob.SetProjection()
        videoJobStep = self.renderJob.RunJob()
        videoJobStep.name = 'Videos'
        self.videoJob = trinity.CreateRenderJob()
        self.videoJob.name = 'Update videos job'
        videoJobStep.job = self.videoJob
        self.bracketCurveSet = trinity.TriCurveSet()
        self.bracketCurveSet.Play()
        self.renderJob.Update(self.bracketCurveSet).name = 'Update brackets'
        self.renderJob.SetViewport()
        self.renderJob.PythonCB(self.Update).name = 'Update uilib'
        self.desktopRenderJob = trinity.CreateRenderJob()
        self.desktopRenderJob.name = 'Desktop'
        self.renderJob.steps.append(trinity.TriStepRunJob(self.desktopRenderJob))
        self.renderJob.ScheduleRecurring()
        is_perforce_client = not blue.pyos.packaged
        if is_perforce_client:
            trinity.SetFpsEnabled(settings.public.ui.Get('isFpsRenderJobEnabled', is_perforce_client))

    def OnSessionChanged(self, isRemote, sess, change):
        if 'userid' in change:
            has_required_role = session.role & ROLE_GML
            is_perforce_client = not blue.pyos.packaged
            if has_required_role and settings.public.ui.Get('isFpsRenderJobEnabled', is_perforce_client):
                trinity.SetFpsEnabled(True)
            else:
                trinity.SetFpsEnabled(False)

    def _GetMouseTravel(self):
        if self._mouseButtonStates.get(uiconst.MOUSELEFT, False):
            x, y, z = self._mouseDownPosition[uiconst.MOUSELEFT]
            return math.sqrt(abs((x - self.x) * (x - self.x) + (y - self.y) * (y - self.y)))
        return 0

    mouseTravel = property(_GetMouseTravel)

    def _GetRightBtn(self):
        return self._mouseButtonStates.get(uiconst.MOUSERIGHT, False)

    rightbtn = property(_GetRightBtn)

    def _GetLeftBtn(self):
        return self._mouseButtonStates.get(uiconst.MOUSELEFT, False)

    leftbtn = property(_GetLeftBtn)

    def _GetMiddleBtn(self):
        return self._mouseButtonStates.get(uiconst.MOUSEMIDDLE, False)

    midbtn = property(_GetMiddleBtn)

    def ReleaseObject(self, object):
        try:
            del self.renderObjectToPyObjectDict[object.renderObject]
        except KeyError:
            pass

    def GetMouseOver(self):
        if self._mouseOver:
            mouseOver = self._mouseOver()
            if mouseOver and not mouseOver.destroyed:
                return mouseOver
            self._mouseOver = None
        from carbonui.uicore import uicore
        return uicore.desktop

    mouseOver = property(GetMouseOver)

    def GetAuxMouseOver(self):
        if self._auxMouseOverRO:
            return self.GetPyObjectFromRenderObject(self._auxMouseOverRO())

    auxMouseOver = property(GetAuxMouseOver)

    def CheckAppFocus(self, hasFocus):
        from carbonui.uicore import uicore
        if getattr(uicore, 'registry', None) is None:
            return
        uicore.UpdateCursor(self.GetMouseOver(), 1)
        if hasFocus:
            modal = uicore.registry.GetModalWindow()
            if modal:
                uicore.registry.SetFocus(modal)
            else:
                f = uicore.registry.GetFocus()
                if (not f or f.destroyed) and self.appfocusitem and self.appfocusitem():
                    f = self.appfocusitem()
                if f is not None and not f.destroyed:
                    uicore.registry.SetFocus(f)
                self.appfocusitem = None
        else:
            focus = uicore.registry.GetFocus()
            if focus:
                self.appfocusitem = weakref.ref(focus)
                uicore.registry.SetFocus(None)
            mouseCaptureItem = self.GetMouseCapture()
            if mouseCaptureItem:
                self.ReleaseCapture()
                self.centerMouse = False
                self._mouseButtonStates = {}
                self._mouseDownPosition = {}
                self._TryExecuteHandler(uiconst.UI_MOUSEUP, mouseCaptureItem, (uiconst.MOUSELEFT,))
        return 1

    def CheckAccelerators(self, vkey, flag):
        modkeys = self.GetModifierKeyState(vkey)
        if self.CheckActiveWindowAccelerators(modkeys, vkey, flag):
            return True
        if self.CheckMappedAccelerators(modkeys, vkey, flag):
            return True
        if self.CheckDirectionalAccelerators(vkey):
            return True
        return False

    def CheckActiveWindowAccelerators(self, modkeys, vkey, flag):
        from carbonui.uicore import uicore
        wnd = uicore.registry.GetActive()
        if wnd and hasattr(wnd, 'OnShortcutKeyDown'):
            return wnd.OnShortcutKeyDown(modkeys, vkey, flag)
        return False

    def GetModifierKeyState(self, vkey = None):
        ret = []
        for key in uiconst.MODKEYS:
            ret.append(trinity.app.Key(key) and key != vkey)

        return tuple(ret)

    def CheckMappedAccelerators(self, modkeys, vkey, flag):
        from carbonui.uicore import uicore
        if not uicore.commandHandler:
            return False
        ctrl = self.Key(uiconst.VK_CONTROL)
        if not ctrl and (self._modkeysOff, vkey) in uicore.commandHandler.commandMap.accelerators:
            cmd = uicore.commandHandler.commandMap.accelerators[self._modkeysOff, vkey]
            if cmd.ignoreModifierKey:
                if not cmd.repeatable and flag & 1073741824:
                    return False
                sm.ScatterEvent('OnCommandExecuted', cmd.name)
                ret = uicore.cmd.ExecuteCommand(cmd)
                if ret:
                    return ret
        if (modkeys, vkey) in uicore.commandHandler.commandMap.accelerators:
            cmd = uicore.commandHandler.commandMap.accelerators[modkeys, vkey]
            if not cmd.repeatable and flag & 1073741824:
                return False
            sm.ScatterEvent('OnCommandExecuted', cmd.name)
            return uicore.cmd.ExecuteCommand(cmd)
        return False

    def CheckDirectionalAccelerators(self, vkey):
        from carbonui.uicore import uicore
        active = uicore.registry.GetActive()
        focus = uicore.registry.GetFocus()
        focusOrActive = focus or active
        if vkey == uiconst.VK_UP and hasattr(focusOrActive, 'OnUp'):
            uthread.pool('uisvc::CheckDirectionalAccelerators OnUp', focusOrActive.OnUp)
            return True
        if vkey == uiconst.VK_DOWN and hasattr(focusOrActive, 'OnDown'):
            uthread.pool('uisvc::CheckDirectionalAccelerators OnDown', focusOrActive.OnDown)
            return True
        if vkey == uiconst.VK_LEFT and hasattr(focusOrActive, 'OnLeft'):
            uthread.pool('uisvc::CheckDirectionalAccelerators OnLeft', focusOrActive.OnLeft)
            return True
        if vkey == uiconst.VK_RIGHT and hasattr(focusOrActive, 'OnRight'):
            uthread.pool('uisvc::CheckDirectionalAccelerators OnRight', focusOrActive.OnRight)
            return True
        if vkey == uiconst.VK_HOME and hasattr(focusOrActive, 'OnHome'):
            uthread.pool('uisvc::CheckDirectionalAccelerators OnHome', focusOrActive.OnHome)
            return True
        if vkey == uiconst.VK_END and hasattr(focusOrActive, 'OnEnd'):
            uthread.pool('uisvc::CheckDirectionalAccelerators OnEnd', focusOrActive.OnEnd)
            return True

    def RegisterForTriuiEvents(self, msgIDlst, function, *args, **kw):
        if type(msgIDlst) == int:
            msgIDlst = [msgIDlst]
        cookie = uthread.uniqueId() or uthread.uniqueId()
        self._triuiRegs[cookie] = msgIDlst
        ref = CallableWeakRef(function)
        for id_ in msgIDlst:
            self._triuiRegsByMsgID.setdefault(id_, {})[cookie] = (ref, args, kw)

        log.LogInfo('RegisterForTriuiEvents', cookie, msgIDlst, function, args, kw)
        return cookie

    def UnregisterForTriuiEvents(self, cookie):
        if cookie not in self._triuiRegs:
            return
        log.LogInfo('UnregisterForTriuiEvents', cookie)
        try:
            for msgID_ in self._triuiRegs[cookie]:
                del self._triuiRegsByMsgID[msgID_][cookie]

            del self._triuiRegs[cookie]
        except KeyError as what:
            log.LogError('UnregisterForTriuiEvents: Tried to kill unexisting registration?', cookie)
            log.LogException()

    @telemetry.ZONE_METHOD
    def RegisterObject(self, pyObject, renderObject):
        self.renderObjectToPyObjectDict[renderObject] = pyObject

    def GetPyObjectFromRenderObject(self, RO):
        pyObject = self.renderObjectToPyObjectDict.get(RO, None)
        if pyObject and not pyObject.destroyed:
            return pyObject

    def AddRootObject(self, obj):
        if self.rootObjectsByName.has_key(obj.name):
            raise AttributeError('Root object already exists with this name (%s)' % obj.name)
        self.rootObjectsByName[obj.name] = obj
        if obj not in self.rootObjects:
            self.rootObjects.append(obj)

    def UpdateRootObjectSizes(self):
        for obj in self.rootObjects:
            obj.UpdateSize()

    def RemoveRootObject(self, obj):
        if obj.name in self.rootObjectsByName:
            del self.rootObjectsByName[obj.name]
        if obj in self.rootObjects:
            self.rootObjects.remove(obj)

    def FindRootObject(self, name):
        return self.rootObjectsByName.get(name, None)

    def AddMouseTargetObject(self, mouseTargetObject):
        self._mouseTargetObject = mouseTargetObject

    def GetMouseTargetObject(self):
        if self._mouseTargetObject:
            if self._mouseTargetObject.GetOwner():
                return self._mouseTargetObject
            self._mouseTargetObject = None

    @telemetry.ZONE_METHOD
    def Update(self, *args):
        try:
            if getattr(self, 'updatingFromRoot', False):
                return
            vp = trinity.TriViewport()
            vp.width = trinity.device.width
            vp.height = trinity.device.height
            self.scaledViewportStep.viewport = vp
            self.cursorPos = trinity.mainWindow.GetCursorPos()
            self.UpdateMouseOver()
            if self.tooltipHandler:
                self.tooltipHandler.RefreshTooltip()
            for root in self.rootObjects:
                root.UpdateAlignmentAsRoot('uilib.Update')

            islands = self.alignIslands
            self.alignIslands = set()
            for island in islands:
                if not island.destroyed:
                    island.UpdateAlignmentAsRoot('uilib.Update Islands')

        except:
            LogException()
            raise

    def SetSceneCamera(self, camera):
        from eve.client.script.ui.camera.cameraBase import CameraBase
        if isinstance(camera, CameraBase):
            self.sceneViewStep.view = None
            self.sceneViewStep.camera = camera._camera
            self.sceneProjectionStep.projection = camera.projectionMatrix
        else:
            self.sceneViewStep.view = camera.viewMatrix
            self.sceneViewStep.camera = None
            self.sceneProjectionStep.projection = camera.projectionMatrix

    def SetSceneView(self, view, projection):
        self.sceneViewStep.camera = None
        self.sceneViewStep.view = view
        self.sceneProjectionStep.projection = projection

    @telemetry.ZONE_METHOD
    def UpdateMouseOver(self, *args):
        from carbonui.uicore import uicore
        pyObject = None
        auxRenderObject = None
        cursorX, cursorY = self.cursorPos
        if 0 <= cursorX <= trinity.mainWindow.width and 0 <= cursorY <= trinity.mainWindow.height:
            mouseTargetObject = self.GetMouseTargetObject()
            if mouseTargetObject and mouseTargetObject.IsMouseHeadingTowards():
                return
            triobj, pyObject = self.PickScreenPosition(int(uicore.ScaleDpi(self.x)), int(uicore.ScaleDpi(self.y)))
            if getattr(triobj, 'auxMouseover', None):
                auxRenderObject = triobj.auxMouseover
        newMouseOver = pyObject or uicore.desktop
        currentMouseOver = self.GetMouseOver()
        currentAuxiliaryTooltip = getattr(self, 'auxiliaryTooltip', None)
        if auxRenderObject:
            self._auxMouseOverRO = weakref.ref(auxRenderObject)
            pyAuxObject = self.GetPyObjectFromRenderObject(auxRenderObject)
            if pyAuxObject and hasattr(pyAuxObject, 'GetAuxiliaryTooltip'):
                self.auxiliaryTooltip = pyAuxObject.GetAuxiliaryTooltip()
                self.auxiliaryTooltipPosition = pyAuxObject.GetAuxiliaryTooltipPosition()
            else:
                self.auxiliaryTooltip = None
                self.auxiliaryTooltipPosition = None
        else:
            self.auxiliaryTooltip = None
            self.auxiliaryTooltipPosition = None
            self._auxMouseOverRO = None
        mouseCaptureItem = self.GetMouseCapture()
        if newMouseOver is not self.mouseOver:
            self._mouseOver = weakref.ref(newMouseOver)
        if currentMouseOver is not newMouseOver or currentAuxiliaryTooltip != self.auxiliaryTooltip:
            self.FlagTooltipsDirty()
        if not mouseCaptureItem and currentMouseOver is not newMouseOver:
            if self._hoverThread:
                self._hoverThread.kill()
            uicore.HideHint()
            from carbonui.primitives.dragdrop import DragDropObject
            if currentMouseOver:
                if uicore.IsDragging() and isinstance(currentMouseOver, DragDropObject) and uicore.dragObject is not currentMouseOver:
                    currentMouseOver.OnDragExit(uicore.dragObject, uicore.dragObject.dragData)
                    self.CheckCallbacks(newMouseOver, uiconst.UI_DRAGEXIT, (uicore.dragObject, uicore.dragObject.dragData))
                else:
                    self._Propagate(eventId=uiconst.UI_MOUSEEXIT, uiObject=currentMouseOver, stopper=newMouseOver)
            if newMouseOver:
                if uicore.IsDragging() and isinstance(newMouseOver, DragDropObject) and uicore.dragObject is not newMouseOver:
                    newMouseOver.OnDragEnter(uicore.dragObject, uicore.dragObject.dragData)
                    self.CheckCallbacks(newMouseOver, uiconst.UI_DRAGENTER, (uicore.dragObject, uicore.dragObject.dragData))
                else:
                    self._Propagate(eventId=uiconst.UI_MOUSEENTER, uiObject=newMouseOver, stopper=currentMouseOver)
                hoverHandlerArgs, hoverHandler = self.FindEventHandler(newMouseOver, self.EVENTMAP[uiconst.UI_MOUSEHOVER])
                if hoverHandler:
                    self._hoverThread = uthread.new(self._HoverThread)
            uicore.CheckCursor()

    def PickScreenPosition(self, x, y):
        triobj = None
        pyObject = None
        for root in self.rootObjects:
            if not root.pickState:
                continue
            RO = root.GetRenderObject()
            if not RO:
                continue
            camera = root.GetCamera()
            if root.renderTargetStep:
                pass
            elif camera:
                triobj = RO.PickObject(x, y, camera.projectionMatrix, camera.viewMatrix, trinity.device.viewport)
            elif hasattr(root, 'PickObject'):
                triobj = root.PickObject(x, y)
            else:
                triobj = RO.PickObject(x, y, self._pickProjection, self._pickView, self._pickViewport)
            if triobj:
                pyObject = self.GetPyObjectFromRenderObject(triobj)
                if pyObject:
                    overridePick = getattr(pyObject, 'OverridePick', None)
                    if overridePick:
                        overrideObject = overridePick(x, y)
                        if overrideObject:
                            pyObject = overrideObject
                from carbonui.control.layer import LayerCore
                if pyObject and not isinstance(pyObject, LayerCore):
                    break

        return (triobj, pyObject)

    def FlagTooltipsDirty(self, instant = False):
        if self.tooltipHandler:
            self.tooltipHandler.FlagTooltipsDirty(instant)

    UpdateTooltip = FlagTooltipsDirty

    def RefreshTooltipForOwner(self, owner):
        if self.tooltipHandler:
            self.tooltipHandler.RefreshTooltipForOwner(owner)

    def _OnMouseMove(self, left, top):
        from carbonui.uicore import uicore
        with uthread.BlockTrapSection():
            currentMouseOver = self.GetMouseOver()
            mouseX = uicore.ReverseScaleDpi(left)
            mouseY = uicore.ReverseScaleDpi(top)
            if self.desktop:
                self.desktop.glowHighlightCoords = (left, top)
            if self.x != mouseX or self.y != mouseY:
                self.dx = mouseX - self.x
                self.dy = mouseY - self.y
                self.x = mouseX
                self.y = mouseY
                self.z = 0
                if self.centerMouse:
                    self.SetCursorPos(uicore.desktop.width / 2, uicore.desktop.height / 2)
                mouseCaptureItem = self.GetMouseCapture()
                if mouseCaptureItem:
                    self._TryExecuteHandler(uiconst.UI_MOUSEMOVE, mouseCaptureItem)
                    self._TryExecuteHandler(uiconst.UI_MOUSEMOVEDRAG, mouseCaptureItem)
                elif currentMouseOver:
                    self._TryExecuteHandler(uiconst.UI_MOUSEMOVE, currentMouseOver)
                    self._TryExecuteHandler(uiconst.UI_MOUSEMOVEDRAG, currentMouseOver)

    def _OnMouseDown(self, button, left, top):
        with uthread.BlockTrapSection():
            if button == uiconst.MOUSELEFT:
                self._OnLeftMouseDown()
            elif button == uiconst.MOUSEMIDDLE:
                self._OnMiddleMouseDown()
            elif button == uiconst.MOUSERIGHT:
                self._OnRightMouseDown()
            elif button in (uiconst.MOUSEXBUTTON1, uiconst.MOUSEXBUTTON2):
                self._OnOtherMouseDown(button)

    def _OnLeftMouseDown(self):
        from carbonui.uicore import uicore
        button = uiconst.MOUSELEFT
        currentMouseOver = self.GetMouseOver()
        self._clickCount += 1
        self._clickTimer = AutoTimer(CLICKCOUNTRESETTIME, self.ResetClickCounter)
        self._expandMenu = button
        self._mouseButtonStates[button] = True
        self._mouseDownPosition[button] = (self.x, self.y, self.z)
        if self.exclusiveMouseFocusActive:
            self._TryExecuteHandler(uiconst.UI_MOUSEDOWN, self.GetMouseCapture(), (button,), param=(button,))
            self._TryExecuteHandler(uiconst.UI_MOUSEDOWNDRAG, self.GetMouseCapture(), (button,), param=(button,))
        else:
            self._TryExecuteHandler(uiconst.UI_MOUSEDOWN, currentMouseOver, (button,), param=(button,))
            self._TryExecuteHandler(uiconst.UI_MOUSEDOWNDRAG, currentMouseOver, (button,), param=(button,))
            self.SetCapture(currentMouseOver, retainFocus=self.exclusiveMouseFocusActive)
            if not currentMouseOver.IsUnder(uicore.layer.menu):
                from carbonui.control.contextMenu.menuUtil import CloseContextMenus
                CloseContextMenus()
                currentFocus = uicore.registry.GetFocus()
                if currentFocus != currentMouseOver:
                    uicore.registry.SetFocus(currentMouseOver)

    def _OnMiddleMouseDown(self):
        currentMouseOver = self.GetMouseOver()
        button = uiconst.MOUSEMIDDLE
        self._expandMenu = None
        self._mouseButtonStates[button] = True
        self._mouseDownPosition[button] = (self.x, self.y, self.z)
        self._TryExecuteHandler(uiconst.UI_MOUSEDOWN, currentMouseOver, (button,), param=(button,))
        uthread.new(self.CheckAccelerators, uiconst.VK_MBUTTON, 0)

    def _OnRightMouseDown(self):
        from carbonui.uicore import uicore
        currentMouseOver = self.GetMouseOver()
        button = uiconst.MOUSERIGHT
        self._expandMenu = button
        self._mouseButtonStates[button] = True
        self._mouseDownPosition[button] = (self.x, self.y, self.z)
        if self.exclusiveMouseFocusActive:
            self._TryExecuteHandler(uiconst.UI_MOUSEDOWN, self.GetMouseCapture(), (button,), param=(button,))
        else:
            self._TryExecuteHandler(uiconst.UI_MOUSEDOWN, currentMouseOver, (button,), param=(button,))
        if not currentMouseOver.IsUnder(uicore.layer.menu):
            from carbonui.control.contextMenu.menuUtil import CloseContextMenus
            CloseContextMenus()
            currentFocus = uicore.registry.GetFocus()
            if currentFocus is not currentMouseOver:
                uicore.registry.SetFocus(currentMouseOver)

    def _OnOtherMouseDown(self, button):
        currentMouseOver = self.GetMouseOver()
        self._mouseButtonStates[button] = True
        self._TryExecuteHandler(uiconst.UI_MOUSEDOWN, currentMouseOver, (button,), param=(button,))
        acc = uiconst.VK_XBUTTON1 if button == uiconst.MOUSEXBUTTON1 else uiconst.VK_XBUTTON2
        uthread.new(self.CheckAccelerators, acc, 0)

    def _OnMouseUp(self, button, left, top):
        with uthread.BlockTrapSection():
            if button == uiconst.MOUSELEFT:
                self._OnLeftMouseUp()
            elif button == uiconst.MOUSERIGHT:
                self._OnRightMouseUp()
            elif button in (uiconst.MOUSEMIDDLE, uiconst.MOUSEXBUTTON1, uiconst.MOUSEXBUTTON2):
                self._OnOtherMouseUp(button)

    def _OnLeftMouseUp(self):
        currentMouseOver = self.GetMouseOver()
        button = uiconst.MOUSELEFT
        self._mouseButtonStates[button] = False
        mouseCaptureItem = self.GetMouseCapture()
        if mouseCaptureItem:
            if not self.exclusiveMouseFocusActive:
                if getattr(mouseCaptureItem, 'expandOnLeft', 0) and not self.rightbtn and self._expandMenu == button and self.FindMenuHandler(mouseCaptureItem):
                    x, y, z = self._mouseDownPosition[button]
                    if abs(self.x - x) < 3 and abs(self.y - y) < 3:
                        self.FlagTooltipsDirty(True)
                        uthread.new(carbonui.control.contextMenu.contextMenu.ShowMenu, mouseCaptureItem, self.GetAuxMouseOver())
                self._expandMenu = False
            self._TryExecuteHandler(uiconst.UI_MOUSEUP, mouseCaptureItem, (button,), param=(button, 0))
            if not self.exclusiveMouseFocusActive:
                self.ReleaseCapture()
            if currentMouseOver is not mouseCaptureItem:
                self._Propagate(eventId=uiconst.UI_MOUSEEXIT, uiObject=mouseCaptureItem, stopper=currentMouseOver)
                self._Propagate(eventId=uiconst.UI_MOUSEENTER, uiObject=currentMouseOver, stopper=mouseCaptureItem)
            else:
                self._TryExecuteClickHandler(0, 0)

    def _OnRightMouseUp(self):
        currentMouseOver = self.GetMouseOver()
        button = uiconst.MOUSERIGHT
        self._mouseButtonStates[button] = False
        if self.exclusiveMouseFocusActive:
            self._TryExecuteHandler(uiconst.UI_MOUSEUP, self.GetMouseCapture(), (button,), param=(button, 0))
        else:
            if not self.leftbtn and self._expandMenu == button and (self.FindMenuHandler(currentMouseOver) or self._auxMouseOverRO is not None):
                x, y, z = self._mouseDownPosition[button]
                if abs(self.x - x) < 3 and abs(self.y - y) < 3:
                    self.FlagTooltipsDirty(True)
                    uthread.new(carbonui.control.contextMenu.contextMenu.ShowMenu, currentMouseOver, self.GetAuxMouseOver())
            self._expandMenu = None
            self._TryExecuteHandler(uiconst.UI_MOUSEUP, currentMouseOver, (button,), param=(button, 0))

    def _OnOtherMouseUp(self, button):
        self._mouseButtonStates[button] = False
        self._TryExecuteHandler(uiconst.UI_MOUSEUP, self.GetMouseOver(), (button,), param=(button, 0))

    def _OnMouseWheel(self, delta):
        from carbonui.uicore import uicore
        with uthread.BlockTrapSection():
            mouseZ = delta
            self.dz = mouseZ
            if self.mouseOver:
                mouseOver = self.mouseOver
                wasHandled = False
                while mouseOver.parent and mouseOver != uicore.uilib.desktop:
                    mwHandlerArgs, mwHandler = self.FindEventHandler(mouseOver, 'OnMouseWheel')
                    if mwHandler:
                        args = [mouseZ] + list(mwHandlerArgs[:])
                        wasHandled = mwHandler(*args)
                        if wasHandled != False:
                            break
                    mouseOver = mouseOver.parent

                handlerObject = mouseOver if wasHandled else None
                self.CheckCallbacks(handlerObject, uiconst.UI_MOUSEWHEEL, (mouseZ,))

    def _OnKeyDown(self, key, flags):
        from carbonui.uicore import uicore
        with uthread.BlockTrapSection():
            focus = uicore.registry.GetFocus()
            if focus:
                self._TryExecuteHandler(uiconst.UI_KEYDOWN, focus, (key, flags), param=(key, flags))
            else:
                self.CheckCallbacks(None, uiconst.UI_KEYDOWN, (key, flags))
            self._keyDownAcceleratorThread = uthread.new(self.CheckAccelerators, key, flags)

    def _OnKeyUp(self, key, flags):
        from carbonui.uicore import uicore
        with uthread.BlockTrapSection():
            focus = uicore.registry.GetFocus()
            if focus:
                self._TryExecuteHandler(uiconst.UI_KEYUP, focus, (key, flags), param=(key, flags))
            else:
                self.CheckCallbacks(None, uiconst.UI_KEYUP, (key, flags))
            if key == uiconst.VK_SNAPSHOT and uicore.commandHandler:
                uicore.commandHandler.PrintScreen()

    def _OnChar(self, key, flags, isDead):
        from carbonui.uicore import uicore
        with uthread.BlockTrapSection():
            if isDead:
                focus = uicore.registry.GetFocus()
                if focus and focus.HasEventHandler('OnChar') and focus.IsVisible():
                    self.StopKeyDownAcceleratorThread()
                else:
                    self.ignoreDeadChar = key
            else:
                char = key
                ignoreChar = False
                if char <= 32 or char == self.ignoreDeadChar:
                    ctrl = trinity.app.Key(uiconst.VK_CONTROL)
                    if char not in (uiconst.VK_RETURN, uiconst.VK_BACK, uiconst.VK_SPACE) or ctrl:
                        ignoreChar = True
                if not ignoreChar:
                    calledOn = self.ResolveOnChar(key, flags)
                    if calledOn:
                        self.StopKeyDownAcceleratorThread()
                self.ignoreDeadChar = None

    def _OnFocusChange(self, hasFocus):
        from carbonui.uicore import uicore
        with uthread.BlockTrapSection():
            self.CheckAppFocus(hasFocus=hasFocus)
            self.CheckCallbacks(obj=uicore.registry.GetFocus(), msgID=uiconst.UI_ACTIVE, param=(hasFocus,))
            sm.ScatterEvent('OnApplicationFocusChanged', hasFocus)

    def _OnClose(self):
        from carbonui.uicore import uicore
        with uthread.BlockTrapSection():
            if uicore.commandHandler:
                uthread.new(uicore.commandHandler.CmdQuitGame)
                return False
        return True

    def CheckCallbacks(self, obj, msgID, param):
        for cookie, (wr, args, kw) in self._triuiRegsByMsgID.get(msgID, {}).items():
            try:
                if not wr() or not wr()(*(args + (obj, msgID, param)), **kw):
                    self.UnregisterForTriuiEvents(cookie)
            except UserError as what:

                def f():
                    raise what

                uthread.new(f)
            except:
                log.LogError('OnAppEvent (cookie', cookie, '): Exception when trying to process callback!')
                log.LogException()

    def StopKeyDownAcceleratorThread(self):
        if self._keyDownAcceleratorThread:
            self._keyDownAcceleratorThread.kill()

    def ResetClickCounter(self, *args):
        self._clickTimer = None
        self._clickCount = 0

    def GetClickCounter(self):
        return (self._clickCount - 1) % 3 + 1

    def ResolveOnChar(self, char, flag):
        ignore = (uiconst.VK_RETURN, uiconst.VK_BACK)
        if char < 32 and char not in ignore:
            return False
        from carbonui.uicore import uicore
        focus = uicore.registry.GetFocus()
        if focus and focus.HasEventHandler('OnChar') and focus.IsVisible():
            _, handler = self.FindEventHandler(focus, 'OnChar')
            handled = handler(char, flag)
            if handled:
                return focus

    def _TryExecuteClickHandler(self, wParam, lParam):
        currentMouseOver = self.GetMouseOver()
        if self._clickCount > 1:
            clickObject = self.GetClickObject()
            if clickObject is None:
                self.ResetClickCounter()
                return
            x, y = self._clickPosition
            distanceOK = abs(self.x - x) < 5 and abs(self.y - y) < 5
            clickPosOK = clickObject is currentMouseOver and distanceOK
            dblHandlerArgs, dblHandler = self.FindEventHandler(clickObject, 'OnDblClick')
            tripHandlerArgs, tripleHandler = self.FindEventHandler(clickObject, 'OnTripleClick')
            if self._clickCount == 2 and dblHandler and clickPosOK:
                self._TryExecuteHandler(uiconst.UI_DBLCLICK, currentMouseOver)
            elif self._clickCount == 3 and tripleHandler and clickPosOK:
                self._TryExecuteHandler(uiconst.UI_TRIPLECLICK, currentMouseOver)
            else:
                self._clickCount = 1
        if self._clickCount <= 1:
            handlerArgs, handler = self.FindEventHandler(currentMouseOver, 'OnClick')
            if handler:
                self._TryExecuteHandler(uiconst.UI_CLICK, currentMouseOver)
                self.SetClickObject(currentMouseOver)
                self._clickPosition = (self.x, self.y)

    def _TryExecuteHandler(self, eventID, uiObject, eventArgs = None, param = None):
        itemCapturingMouse = self.GetMouseCapture()
        if itemCapturingMouse:
            uiObject = itemCapturingMouse
        handled = self._ExecuteHandlerRaw(eventID, uiObject, eventArgs)
        handlerObject = uiObject if handled else None
        self.CheckCallbacks(handlerObject, eventID, param)
        return handlerObject

    def _ExecuteHandlerRaw(self, eventID, uiObject, arguments = None):
        functionName = self.EVENTMAP.get(eventID, None)
        if functionName is None:
            raise NotImplementedError
        handlerArgs, handler = self.FindEventHandler(uiObject, functionName)
        if not handler:
            return False
        args = handlerArgs[:]
        if arguments:
            args += arguments
        if eventID in self.UTHREADEDEVENTS:
            uthread.new(handler, *args)
        else:
            try:
                handler(*args)
            except Exception:
                log.LogException()
                raise

        return True

    def SetWindowOrder(self, *args):
        return trinity.app.uilib.SetWindowOrder(*args)

    def FindEventHandler(self, uiObject, handlerName):
        if getattr(self, 'eventHandlerResolver', None):
            return self.eventHandlerResolver(uiObject, handlerName)
        else:
            return uiObject.FindEventHandler(handlerName)

    def GetEventHandlerResolver(self):
        return self.eventHandlerResolver

    def SetEventHandlerResolver(self, resolver):
        self.eventHandlerResolver = resolver

    def FindMenuHandler(self, uiObject):
        if getattr(self, 'menuHandlerResolver', None):
            return self.menuHandlerResolver(uiObject)
        else:
            return getattr(uiObject, 'GetMenu', None)

    def GetMenuHandlerResolver(self):
        return self.menuHandlerResolver

    def SetMenuHandlerResolver(self, resolver):
        self.menuHandlerResolver = resolver

    def GetMouseButtonState(self, buttonFlag):
        return self._mouseButtonStates.get(buttonFlag, False)

    def Key(self, vkey):
        return trinity.app.Key(vkey)

    def SetCursorProperties(self, cursor):
        trinity.mainWindow.mouseCursor = cursor

    def SetCursorPos(self, x, y):
        self.x = x
        self.y = y
        from carbonui.uicore import uicore
        return trinity.app.SetCursorPos(uicore.ScaleDpi(x), uicore.ScaleDpi(y))

    def SetCursor(self, cursorResPath):
        if self.exclusiveMouseFocusActive:
            return
        if not blue.paths.exists(cursorResPath):
            raise RuntimeError('Cursor not found: %s' % cursorResPath)
        cursor = self.cursorCache.get(cursorResPath, None)
        if cursor is None:
            cursor = self._ConstructCursor(cursorResPath)
        self.SetCursorProperties(cursor)

    def _ConstructCursor(self, cursorResPath):
        representations = []
        for each in uiconst.UICURSOR_REPRESENTATIONS.get(cursorResPath, ()):
            bmp = trinity.Tr2HostBitmap()
            bmp.CreateFromFile(each)
            representations.append(bmp)

        bmp = trinity.Tr2HostBitmap()
        bmp.CreateFromFile(cursorResPath)
        cursor = trinity.Tr2MouseCursor(bmp, 16, 15, representations)
        self.cursorCache[cursorResPath] = cursor
        return cursor

    def FindWindow(self, wndName, fromParent):
        return trinity.app.uilib.FindWindow(wndName, fromParent)

    def SetMouseCapture(self, item, retainFocus = False):
        self._capturingMouseItem = weakref.ref(item)
        self.exclusiveMouseFocusActive = retainFocus
        self.FlagTooltipsDirty()

    SetCapture = SetMouseCapture

    def GetMouseCapture(self):
        if self._capturingMouseItem:
            captureItem = self._capturingMouseItem()
            if captureItem and not captureItem.destroyed:
                return captureItem
            self._capturingMouseItem = None
            self.exclusiveMouseFocusActive = False

    GetCapture = GetMouseCapture
    capture = property(GetMouseCapture)

    def SetClickObject(self, item):
        self._clickItem = weakref.ref(item)

    def GetClickObject(self):
        if self._clickItem:
            clickObject = self._clickItem()
            if clickObject and not clickObject.destroyed:
                return clickObject

    def ReleaseCapture(self, itemReleasing = None):
        self._capturingMouseItem = None
        self.exclusiveMouseFocusActive = False
        self.FlagTooltipsDirty()
        from carbonui.uicore import uicore
        uicore.UpdateCursor(uicore.uilib.mouseOver)

    def ClipCursor(self, *rect):
        from carbonui.uicore import uicore
        self._cursorClip = rect
        l, t, r, b = rect
        trinity.app.ClipCursor(uicore.ScaleDpi(l), uicore.ScaleDpi(t), uicore.ScaleDpi(r), uicore.ScaleDpi(b))

    def UnclipCursor(self, *args):
        self._cursorClip = None
        trinity.app.UnclipCursor()

    def _HoverThread(self):
        while True:
            if trinity.app.IsHidden():
                return
            blue.synchro.SleepWallclock(HOVERTIME)
            self._TryExecuteHandler(uiconst.UI_MOUSEHOVER, self.mouseOver)

    def _Propagate(self, eventId, uiObject, arguments = None, globalArguments = None, stopper = None):
        firstHandler = None
        while uiObject:
            if uiObject in self.rootObjects:
                break
            if uiObject is stopper or stopper.IsUnder(uiObject):
                break
            handled = self._ExecuteHandlerRaw(eventId, uiObject, arguments)
            if handled and firstHandler is None:
                firstHandler = uiObject
            uiObject = uiObject.parent

        self.CheckCallbacks(firstHandler, eventId, globalArguments)
