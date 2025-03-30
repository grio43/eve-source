#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\scenecontainer.py
import logging
import blue
import geo2
import locks
import math
import trinity
from carbon.common.lib import bitmapjob
from carbonui import uiconst
from carbonui.control.window import Window
from carbonui.primitives.base import Base
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import GetWindowAbove
from eve.client.script.ui.camera.baseCamera import Camera
from eve.client.script.ui.camera.cameraUtil import GetCameraSensitivityMultiplier
from eve.client.script.ui.camera.sceneContainerCamera import SceneContainerCamera
from signals import Signal
STENCIL_MAP_DEFAULT = 'res:/UI/Texture/circleStencil.dds'
STENCIL_MAP_NONE = ''
log = logging.getLogger(__name__)

class SceneContainer(Base):
    __guid__ = 'form.SceneContainer'
    __renderObject__ = trinity.Tr2Sprite2dRenderJob
    __notifyevents__ = ['ProcessWindowUnstacked', 'ProcessWindowStacked']
    default_minZoom = 10.0
    default_maxZoom = 3000.0

    def ApplyAttributes(self, attributes):
        self.viewport = trinity.TriViewport()
        self.viewport.x = 0
        self.viewport.y = 0
        self.viewport.width = 1
        self.viewport.height = 1
        self.viewport.minZ = 0.0
        self.viewport.maxZ = 1.0
        self.projection = trinity.TriProjection()
        self.bracketCurveSet = trinity.TriCurveSet()
        self.renderJob = None
        self.frontClip = 1.0
        self.backClip = 350000.0
        self.fov = 1.0
        self.minPitch = None
        self.maxPitch = None
        self.scene = None
        self.offscreen = False
        self.PrepareCamera()
        self._reloadLock = locks.Lock()
        Base.ApplyAttributes(self, attributes)
        self.minZoom = attributes.Get('minZoom', self.default_minZoom)
        self.maxZoom = attributes.Get('maxZoom', self.default_maxZoom)
        sm.RegisterNotify(self)

    def ProcessWindowStacked(self, wnd, stack):
        if GetWindowAbove(self) == wnd:
            wnd.UnregisterSceneContainer(self)
            stack.RegisterSceneContainer(self)

    def ProcessWindowUnstacked(self, wnd, stack):
        if GetWindowAbove(self) == wnd:
            stack.UnregisterSceneContainer(self)
            wnd.RegisterSceneContainer(self)

    def SetParent(self, parent, idx = None):
        Base.SetParent(self, parent, idx)
        wnd = GetWindowAbove(self)
        if wnd:
            stack = wnd.GetStack()
            if stack:
                stack.RegisterSceneContainer(self)
            else:
                wnd.RegisterSceneContainer(self)

    def Startup(self, *args):
        self.DisplayScene()

    def PrepareSpaceScene(self, maxPitch = None, scenePath = None, offscreen = False, resetZoom = True):
        self.offscreen = offscreen
        if scenePath is None:
            self.scene = trinity.EveSpaceScene()
        else:
            self.scene = trinity.Load(scenePath)
        self.frontClip = 1.0
        self.backClip = 400000.0
        self.fov = 1.0
        self.minPitch = None
        self.maxPitch = maxPitch
        self.scene.DisableShadows()
        self.SetupCamera(resetZoom=resetZoom)
        self.DisplaySpaceScene()

    def CreateBracketCurveSet(self):
        self.bracketCurveSet.Play()
        self.renderJob.SetBracketCurveSet(self.bracketCurveSet)

    def PrepareInteriorScene(self, backgroundImage = None, useShadows = True, shadowResolution = 1024, startOpacity = 1.0, sceneFile = None):
        if not sceneFile:
            sceneFile = 'res:/Graphics/Interior/characterCreation/Preview.red'
        self.scene = trinity.Load(sceneFile)
        self.scene.renderShadows = useShadows
        self.scene.shadowSize = shadowResolution
        self.frontClip = 0.1
        self.backClip = 10.0
        self.fov = 0.3
        self.minPitch = -0.6 + math.pi / 2
        self.maxPitch = 0.6 + math.pi / 2
        self.SetupCamera()
        blue.resMan.Wait()
        self.DisplayInteriorScene(backgroundImage=backgroundImage, startOpacity=startOpacity)

    def PrepareCharacterCreationScene(self):
        self.scene = trinity.Load('res:/Graphics/Interior/characterCreation/Preview.red')
        self.scene.shadowSize = 512
        blue.resMan.Wait()

    def SetupCamera(self, resetZoom = True):
        if self.destroyed:
            return
        self.camera.nearClip = self.frontClip
        self.camera.farClip = self.backClip
        self.camera.fov = self.fov
        if resetZoom or not 0.0 <= self.camera.GetZoomLinear() <= 1.0:
            self.camera.SetZoomLinear(0.5)
        self.camera.kMinPitch = self.minPitch if self.minPitch is not None else Camera.kMinPitch
        self.camera.kMaxPitch = self.maxPitch if self.maxPitch is not None else Camera.kMaxPitch

    def PrepareCamera(self):
        self.camera = SceneContainerCamera()
        self.camera.OnActivated()

    def DisplaySpaceScene(self, blendMode = None):
        from trinity.sceneRenderJobSpaceEmbedded import CreateEmbeddedRenderJobSpace
        self.renderJob = CreateEmbeddedRenderJobSpace()
        if self.destroyed:
            return
        rj = self.renderJob
        rj.CreateBasicRenderSteps()
        self.CreateBracketCurveSet()
        rj.SetActiveCamera(view=self.camera.viewMatrix, projection=self.camera.projectionMatrix)
        rj.SetCameraProjection(self.camera.projectionMatrix)
        rj.SetCameraView(self.camera.viewMatrix)
        rj.SetScene(self.scene)
        rj.SetViewport(self.viewport)
        if not self.viewport:
            return
        if self.offscreen:
            rj.SetOffscreen(self.offscreen)
        rj.UpdateViewport(self.viewport)
        sm.GetService('sceneManager').RegisterJob(rj)
        try:
            rj.DoPrepareResources()
        except trinity.ALError:
            pass

        if blendMode:
            step = trinity.TriStepSetStdRndStates()
            step.renderingMode = blendMode
            rj.AddStep('SET_BLENDMODE', step)
        rj.Enable(False)
        rj.SetSettingsBasedOnPerformancePreferences()
        if self and not self.destroyed:
            self.renderObject.renderJob = self.renderJob

    def DisplayScene(self, addClearStep = False, addBitmapStep = False, backgroundImage = None):
        self.renderJob = trinity.CreateRenderJob('SceneInScene')
        self.renderJob.SetViewport(self.viewport)
        self.renderJob.SetProjection(self.camera.projectionMatrix)
        self.renderJob.SetView(self.camera.viewMatrix)
        self.renderJob.Update(self.scene)
        if addClearStep:
            self.renderJob.Clear(None, 1.0)
        if addBitmapStep:
            if backgroundImage is None:
                backgroundImage = 'res:/UI/Texture/preview/asset_preview_background.png'
            step = bitmapjob.makeBitmapStep(backgroundImage, scaleToFit=False, color=(1.0, 1.0, 1.0, 1.0))
            self.renderJob.steps.append(step)
        self.renderJob.RenderScene(self.scene)
        self.renderObject.renderJob = self.renderJob

    def DisplayInteriorScene(self, backgroundImage = None, startOpacity = 1.0):
        from trinity.sceneRenderJobCharacters import CreateSceneRenderJobCharacters
        self.renderJob = CreateSceneRenderJobCharacters('SceneInScene')
        self.renderJob.SetStartOpacity(startOpacity)
        self.renderJob.CreateBasicRenderSteps()
        self.renderJob.SetScene(self.scene)
        while self.viewport.width == 1 or self.viewport.height == 1:
            blue.synchro.Yield()

        if backgroundImage:
            step = bitmapjob.makeBitmapStep(backgroundImage, scaleToFit=False, color=(1.0, 1.0, 1.0, 1.0), targetSize=(self.viewport.width, self.viewport.height))
            self.renderJob.AddStep('RENDER_BACKDROP', step)
        self.renderJob.EnableScatter(False)
        self.renderJob.EnableSculpting(False)
        self.renderJob.SetViewport(self.viewport)
        self.renderJob.SetSettingsBasedOnPerformancePreferences()
        self.renderJob.Enable(False)
        self.renderJob.SetCameraProjection(self.camera.projectionMatrix)
        self.renderJob.SetCameraView(self.camera.viewMatrix)
        self.renderObject.renderJob = self.renderJob

    def SetStencilMap(self, path = STENCIL_MAP_DEFAULT):
        if hasattr(self.renderJob, 'SetStencil'):
            self.renderJob.SetStencil(path)

    def AddToScene(self, model, clear = 1):
        if model is None:
            log.warning('SceneContainer: Trying to load a None model to the scene')
            return
        if self.scene is None:
            log.warning('SceneContainer: Trying to load a model to a None scene')
            return
        if clear:
            del self.scene.objects[:]
        self.scene.objects.append(model)
        log.info('SceneContainer: Model added to scene')
        self.scene.UpdateScene(blue.os.GetSimTime())
        log.info('SceneContainer: Scene updated')

    def RemoveFromScene(self, model):
        self.scene.objects.remove(model)
        log.info('SceneContainer: Model added to scene')
        self.scene.UpdateScene(blue.os.GetSimTime())
        log.info('SceneContainer: Scene updated')

    def ClearScene(self):
        self.scene.UpdateScene(blue.os.GetSimTime())
        del self.scene.objects[:]

    def _OnResize(self):
        self.UpdateViewPort()

    def UpdateViewPort(self, *args):
        l, t, w, h = self.GetAbsoluteViewport()
        if not h:
            return
        if not self.offscreen:
            l = uicore.ScaleDpi(l)
            t = uicore.ScaleDpi(t)
            w = uicore.ScaleDpi(w)
            h = uicore.ScaleDpi(h)
        self.viewport.x = l
        self.viewport.y = t
        self.viewport.width = w
        self.viewport.height = h
        self.camera.UpdateViewportSize(w, h)
        if hasattr(self.renderJob, 'UpdateViewport'):
            self.renderJob.UpdateViewport(self.viewport)

    def OnResize_(self, k, v):
        self.UpdateViewPort()

    def UpdateAlignment(self, *args):
        ret = Base.UpdateAlignment(self, *args)
        self.UpdateViewPort()
        return ret

    def _OnClose(self, *args):
        with self._reloadLock:
            self.clearStep = None
            self.viewport = None
            self.projection = None
            if self.camera:
                self.camera.OnDeactivated()
                self.camera = None
            self.scene = None
            if hasattr(self.renderJob, 'Disable'):
                self.renderJob.Disable()
            self.renderJob = None

    def AnimEntry(self, yaw0 = 1.1 * math.pi, pitch0 = 0.0, yaw1 = 1.25 * math.pi, pitch1 = -0.5, duration = 2.0):
        if self.destroyed:
            return
        self.camera.StopUpdateThreads()
        pitch0 = self._ConvertPitch(pitch0)
        pitch1 = self._ConvertPitch(pitch1)
        uicore.animations.MorphScalar(self, 'zoom', 1.0, self.zoom, duration=duration)
        uicore.animations.MorphScalar(self.camera, 'yaw', yaw0, yaw1, duration=duration)
        uicore.animations.MorphScalar(self.camera, 'pitch', pitch0, pitch1, duration=duration)

    def _ConvertPitch(self, pitch):
        return math.pi / 2 - pitch

    def GetOrbit(self):
        return (0.0, 0.0)

    def SetOrbit(self, yaw, pitch):
        self.camera.SetYaw(yaw)
        self.camera.SetPitch(pitch)

    orbit = property(GetOrbit, SetOrbit)

    def OrbitParent(self, dx, dy):
        self.StopAnimations()
        fov = self.camera.fov
        cameraSpeed = 0.02
        self.camera.Orbit(dx * fov * cameraSpeed, dy * fov * cameraSpeed)

    def GetZoom(self):
        if self.camera:
            return self.camera.GetZoomLinear()
        else:
            return 0.0

    def SetZoom(self, value):
        if self.camera:
            self.camera.SetZoomLinear(value)

    zoom = property(GetZoom, SetZoom)

    def SetMinMaxZoom(self, minZoom, maxZoom):
        self.camera.minZoom = maxZoom
        self.camera.maxZoom = minZoom

    def Zoom(self, dz):
        self.StopAnimations()
        self.camera.Zoom(dz)


class SceneWindowTest(Window):
    __guid__ = 'form.SceneWindowTest'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        sc = SceneContainer(Frame(parent=self.sr.main, padding=(6, 6, 6, 6), color=(1.0, 1.0, 1.0, 0.5)))
        sc.Startup()
        nav = SceneContainerBaseNavigation(Container(parent=self.sr.main, left=6, top=6, width=6, height=6, idx=0, state=uiconst.UI_NORMAL))
        nav.Startup(sc)
        self.sr.navigation = nav
        self.sr.sceneContainer = sc

    def OnResizeUpdate(self, *args):
        self.sr.sceneContainer.UpdateViewPort()


class SceneContainerBaseNavigation(Container):
    __guid__ = 'form.SceneContainerBaseNavigation'
    isTabStop = 1
    on_zoom = Signal('on_zoom')
    on_drop_data = Signal('on_drop_data')
    on_mouse_down = Signal('on_mouse_down')
    on_mouse_up = Signal('on_mouse_down')
    on_dbl_click = Signal('on_dbl_click')

    def Startup(self, sceneContainer):
        self.sr.sceneContainer = sceneContainer
        self.sr.cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self._OnGlobalMouseUp)
        self.sr.cookie2 = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self._OnGlobalMouseDown)

    def _OnClose(self, *args):
        if self.sr.cookie:
            uicore.event.UnregisterForTriuiEvents(self.sr.cookie)
            self.sr.cookie = None
        if self.sr.cookie2:
            uicore.event.UnregisterForTriuiEvents(self.sr.cookie2)
            self.sr.cookie2 = None

    def SetMinMaxZoom(self, minZoom, maxZoom):
        self.sr.sceneContainer.SetMinMaxZoom(minZoom, maxZoom)

    def OnMouseWheel(self, *args):
        modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
        self.sr.sceneContainer.Zoom(modifier * uicore.uilib.dz * 0.001)

    def OnMouseMove(self, *args):
        if self.destroyed or uicore.IsDragging():
            return
        dx = GetMouseDX()
        dy = GetMouseDY()
        onlyLMB = uicore.uilib.leftbtn and not uicore.uilib.rightbtn
        onlyRMB = uicore.uilib.rightbtn and not uicore.uilib.leftbtn
        isRotate = onlyLMB or onlyRMB
        if isRotate:
            self.sr.sceneContainer.OrbitParent(dx, dy)
        if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
            advancedInspectionOn = False
            camera = self.sr.sceneContainer.camera
            if hasattr(self.sr.sceneContainer.camera, 'GetCurrentInspectionStatus'):
                advancedInspectionOn = advancedInspectionOn or camera.GetCurrentInspectionStatus()
            if not advancedInspectionOn:
                modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
                self.sr.sceneContainer.Zoom(modifier * -dy * 0.01)
                self.sr.sceneContainer.OrbitParent(dx, 0.0)
            else:
                kRotate = 0.005 * self.sr.sceneContainer.camera.fov
                camera.Rotate(kRotate * dx, kRotate * dy)

    def _OnGlobalMouseUp(self, wnd, msgID, btn, *args):
        camera = self.sr.sceneContainer.camera
        if btn and btn[0] == uiconst.MOUSERIGHT:
            if self.sr.sceneContainer and camera:
                if hasattr(camera, 'SetCurrentInspectionStatus'):
                    camera.SetCurrentInspectionStatus(False)
                    self.on_zoom(False)
                camera.rotationOfInterest = geo2.QuaternionIdentity()
        if btn and btn[0] == uiconst.MOUSELEFT and camera:
            camera.ResetRotate()
            if hasattr(camera, 'GetAdvancedInspectionModeStatus'):
                if camera.GetAdvancedInspectionModeStatus():
                    if camera.GetCurrentInspectionStatus():
                        self.sr.sceneContainer.camera.SetFovTarget(camera.fov * 2)
        return 1

    def _OnGlobalMouseDown(self, wnd, msgID, btn, *args):
        camera = self.sr.sceneContainer.camera
        if type(wnd) != type(self):
            return 1
        if btn and btn[0] == uiconst.MOUSERIGHT and camera and not uicore.uilib.leftbtn:
            if self.sr.sceneContainer:
                if hasattr(camera, 'GetAdvancedInspectionModeStatus'):
                    if camera.GetAdvancedInspectionModeStatus():
                        camera.SetCurrentInspectionStatus(True)
                        self.on_zoom(True)
        if btn and btn[0] == uiconst.MOUSELEFT and camera:
            if hasattr(camera, 'GetAdvancedInspectionModeStatus'):
                if camera.GetAdvancedInspectionModeStatus():
                    if camera.GetCurrentInspectionStatus():
                        self.sr.sceneContainer.camera.SetFovTarget(camera.fov / 2)
        return 1

    def OnDropData(self, dragSource, dragData):
        self.on_drop_data(dragSource, dragData)

    def OnMouseDown(self, button, *args):
        super(SceneContainerBaseNavigation, self).OnMouseDown(button, *args)
        self.on_mouse_down(button)

    def OnMouseUp(self, button, *args):
        super(SceneContainerBaseNavigation, self).OnMouseUp(button, *args)
        self.on_mouse_up(button)

    def OnDblClick(self, *args):
        self.on_dbl_click(*args)


class SceneContainerBrackets(Base):
    __guid__ = 'form.SceneContainerBrackets'
    __renderObject__ = trinity.Tr2Sprite2dRenderJob

    def ApplyAttributes(self, attributes):
        Base.ApplyAttributes(self, attributes)
        self.viewport = trinity.TriViewport()
        self.viewport.x = 0
        self.viewport.y = 0
        self.viewport.width = 1
        self.viewport.height = 1
        self.viewport.minZ = 0.0
        self.viewport.maxZ = 1.0
        self.projection = trinity.TriProjection()
        self.frontClip = 1.0
        self.backClip = 350000.0
        self.fov = 1.0
        self.minPitch = None
        self.maxPitch = None
        self.minZoom = 0.0
        self.maxZoom = 1.0
        self.scene = trinity.EveSpaceScene()
        self.transform = trinity.EveRootTransform()
        self.scene.objects.append(self.transform)
        self.PrepareCamera()
        self.DisplayScene()
        self.CreateBracketCurveSet()
        self.UpdateViewPort()

    def SetParent(self, parent, idx = None):
        Base.SetParent(self, parent, idx)
        wnd = GetWindowAbove(self)
        if wnd:
            wnd.RegisterSceneContainer(self)

    def PrepareCamera(self):
        self.camera = SceneContainerCamera()
        self.camera.OnActivated()
        self.camera.frontClip = self.frontClip
        self.camera.backClip = self.backClip
        self.camera.fov = self.fov
        self.camera.zoom = 0.7

    def GetTranslationsForSolarsystemIDs(self, solarSystemIDs):
        xAv = yAv = zAv = 0
        scale = 1e+16
        for solarsystemID in solarSystemIDs:
            systemCenter = cfg.mapSystemCache[solarsystemID].center
            xAv += systemCenter.x
            yAv += systemCenter.y
            zAv += systemCenter.z

        numSystems = len(solarSystemIDs)
        xAv /= numSystems
        yAv /= numSystems
        zAv /= numSystems
        translations = []
        for solarsystemID in solarSystemIDs:
            systemCenter = cfg.mapSystemCache[solarsystemID].center
            translations.append(((systemCenter.x - xAv) / scale, (systemCenter.y - yAv) / scale, (systemCenter.z - zAv) / scale))

        return translations

    def CreateBracketTransform(self, translation):
        tr = trinity.EveTransform()
        tr.translation = translation
        self.transform.children.append(tr)
        return tr

    def AnimRotateFrom(self, yaw, pitch, zoom, duration):
        curve = trinity.Tr2CurveEulerRotation()
        curve.yaw.AddKey(0.0, math.radians(yaw))
        curve.yaw.AddKey(duration, 0.0)
        curve.pitch.AddKey(0.0, math.radians(pitch))
        curve.pitch.AddKey(duration, 0.0)
        self.transform.rotationCurve = trinity.Tr2RotationAdapter()
        self.transform.rotationCurve.curve = curve

    def DisplayScene(self):
        self.renderJob = trinity.CreateRenderJob()
        self.renderJob.SetViewport(self.viewport)
        self.renderJob.SetView(self.camera.viewMatrix)
        self.renderJob.SetProjection(self.camera.projectionMatrix)
        self.renderJob.Update(self.scene)
        self.renderJob.RenderScene(self.scene)
        self.renderObject.renderJob = self.renderJob

    def CreateBracketCurveSet(self):
        self.bracketCurveSet = trinity.TriCurveSet()
        self.bracketCurveSet.Play()
        step = trinity.TriStepUpdate()
        step.object = self.bracketCurveSet
        step.name = 'Update brackets'
        self.renderJob.steps.append(step)

    def _OnResize(self):
        self.UpdateViewPort()

    def UpdateViewPort(self, *args):
        l, t, w, h = self.GetAbsoluteViewport()
        log.info('SceneContainerBrackets::UpdateViewPort', l, t, w, h)
        if not w and not h:
            return
        self.viewport.width = uicore.ScaleDpi(w)
        self.viewport.height = uicore.ScaleDpi(h)
        log.info('new viewport dimensions', self.viewport.x, self.viewport.y, self.viewport.width, self.viewport.height)
        log.info('projection', self.fov, self.viewport.GetAspectRatio(), self.frontClip, self.backClip)
        self.camera.UpdateViewportSize(uicore.ScaleDpi(w), uicore.ScaleDpi(h))

    def _OnClose(self, *args):
        self.clearStep = None
        self.viewport = None
        self.projection = None
        if self.camera:
            self.camera.OnDeactivated()
            self.camera = None
        self.scene = None
        if hasattr(self.renderJob, 'Disable'):
            self.renderJob.Disable()
        self.renderJob = None

    def GetOrbit(self):
        return (0.0, 0.0)

    def SetOrbit(self, yaw, pitch):
        self.camera.SetYaw(yaw)
        self.camera.SetPitch(pitch)

    orbit = property(GetOrbit, SetOrbit)

    def OrbitParent(self, dx, dy):
        self.StopAnimations()
        fov = self.camera.fov
        cameraSpeed = 0.01
        self.camera.Orbit(dx * fov * cameraSpeed, dy * fov * cameraSpeed)

    def GetZoom(self):
        return self.camera.GetZoomLinear()

    def SetZoom(self, value):
        self.camera.SetZoomLinear(value)

    zoom = property(GetZoom, SetZoom)

    def SetMinMaxZoom(self, minZoom, maxZoom):
        self.camera.minZoom = maxZoom
        self.camera.maxZoom = minZoom

    def Zoom(self, dz):
        self.camera.Zoom(dz)


def GetMouseDY():
    return uicore.uilib.dy * GetCameraSensitivityMultiplier()


def GetMouseDX():
    return uicore.uilib.dx * GetCameraSensitivityMultiplier()
