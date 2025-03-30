#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\desktop.py
import blue
import geo2
import trinity
from carbonui import uiconst
from carbonui.control.layer import LayerCore
from carbonui.primitives.container import Container
from carbonui.uicore import uicore

class UIRoot(Container):
    __renderObject__ = trinity.Tr2Sprite2dScene
    default_name = 'root'
    default_clearBackground = False
    default_backgroundColor = (0, 0, 0, 1)
    default_isFullscreen = True
    default_align = uiconst.ABSOLUTE
    default_state = uiconst.UI_NORMAL
    default_dpiScaling = 1.0
    default_doesTakeFocus = True
    default_glowEnabled = False
    default_glowBrightness = 1.0
    default_glowDistortion = 0.0
    default_glowHighlightRadius = 200.0
    default_glowHighlightBrightness = 3.0
    _rotationX = 0.0
    _rotationY = 0.0
    _rotationZ = 0.0

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        renderTarget = attributes.renderTarget
        depthMax = attributes.depthMax
        depthMin = attributes.depthMin
        if depthMax or depthMin:
            self.depthMin = depthMin
            self.depthMax = depthMax
            myScene = self.GetRenderObject()
            myScene.is2dRender = False
            myScene.is2dPick = False
            self.InitCamera()
        else:
            self.depthMin = 0
            self.depthMax = 0
            self.camera = None
        self.isFullscreen = attributes.isFullscreen if attributes.isFullscreen is not None else self.default_isFullscreen
        self.clearBackground = attributes.clearBackground if attributes.clearBackground is not None else self.default_clearBackground
        self.backgroundColor = attributes.backgroundColor or self.default_backgroundColor
        self._dpiScaling = attributes.dpiScaling or self.default_dpiScaling
        self.doesTakeFocus = attributes.doesTakeFocus if attributes.doesTakeFocus is not None else self.default_doesTakeFocus
        self.sceneObject = None
        self.renderTargetStep = None
        self.generateMipsStep = None
        self.renderSteps = []
        self._glowRenderTarget = None
        self._blurRenderTarget0 = None
        self._blurRenderTarget1 = None
        self._glowProcessStep = None
        self._glowTransform = None
        self._glowTargetSteps = []
        self._glowEnabled = attributes.glowEnabled if attributes.glowEnabled is not None else self.default_glowEnabled
        self._glowBrightness = self.default_glowBrightness
        self._glowDistortion = self.default_glowDistortion
        self._glowHighlightRadius = self.default_glowHighlightRadius
        self._glowHighlightBrightness = self.default_glowHighlightBrightness
        self._glowHighlightCoords = (0, 0)
        self._renderJob = attributes.renderJob
        if self._renderJob:
            self.ConstructRenderSteps(depthMax, self._renderJob, renderTarget)

    def _GetRenderTarget(self):
        if self.renderTargetStep:
            return self.renderTargetStep.renderTarget

    def _RefreshGlowTargets(self, renderTarget):
        self._ConstructGlowTargets(renderTarget)
        if self._glowProcessStep:
            self._glowProcessStep.job = self._ConstructGlowRenderJob()
        for each in self._glowTargetSteps:
            each.renderTarget = self._glowRenderTarget

    def _ConstructGlowTargets(self, renderTarget):
        if not self._glowEnabled:
            self._glowRenderTarget = None
            self._blurRenderTarget0 = None
            self._blurRenderTarget1 = None
            return
        if renderTarget:
            width, height = renderTarget.width, renderTarget.height
            fmt = renderTarget.format
        else:
            width, height = trinity.device.width, trinity.device.height
            fmt = trinity.PIXEL_FORMAT.B8G8R8A8_UNORM
        self._glowRenderTarget = trinity.Tr2RenderTarget(width, height, 1, fmt)
        self._glowRenderTarget.name = 'UI Glow Target'
        self._blurRenderTarget0 = trinity.Tr2RenderTarget(width / 2, height / 2, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
        self._blurRenderTarget0.name = 'UI Glow Blur Target 0'
        self._blurRenderTarget1 = trinity.Tr2RenderTarget(width / 2, height / 2, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
        self._blurRenderTarget1.name = 'UI Glow Blur Target 1'

    def _ConstructGlowRenderJob(self):
        targets = [self._blurRenderTarget0, self._blurRenderTarget1]
        glowRJ = trinity.CreateRenderJob()
        glowRJ.name = 'Glow'
        glowRJ.PushRenderTarget().name = 'Save RT'
        glowRJ.SetStdRndStates(trinity.RM_FULLSCREEN)
        glowRJ.SetRenderTarget(targets[0])

        def param(name, value):
            if isinstance(value, float):
                p = trinity.Tr2FloatParameter()
            else:
                p = trinity.Tr2Vector2Parameter()
            p.name = name
            p.value = value
            return p

        glow = trinity.Tr2Effect()
        glow.StartUpdate()
        glow.effectFilePath = 'res:/graphics/effect/ui/glowtransform.fx'
        glow.resources.append(trinity.Tr2RuntimeTextureParameter('GlowMap', self._glowRenderTarget))
        glow.parameters.append(param('GlowSize', (self._glowRenderTarget.width, self._glowRenderTarget.height)))
        glow.parameters.append(param('DistortionStrength', self._glowDistortion))
        glow.parameters.append(param('Brightness', self._glowBrightness))
        glow.parameters.append(param('HighlightRadius', self._glowHighlightRadius))
        glow.parameters.append(param('HighlightBrightness', self._glowHighlightBrightness))
        glow.parameters.append(param('HighlightCoords', self._glowHighlightCoords))
        glow.EndUpdate()
        self._glowTransform = glow
        glowRJ.RenderEffect(glow).name = 'Transform Glow'
        glowRJ.SetRenderTarget(targets[1])
        blur = trinity.Tr2Effect()
        blur.StartUpdate()
        blur.effectFilePath = 'res:/graphics/effect/ui/glowblur.fx'
        blur.resources.append(trinity.Tr2RuntimeTextureParameter('InputMap', targets[0]))
        blur.constParameters.append(('InputMapSize', (targets[0].width,
          targets[0].height,
          0,
          0)))
        blur.EndUpdate()
        glowRJ.RenderEffect(blur).name = 'Blur Horiz'
        glowRJ.SetRenderTarget(targets[0])
        blur = trinity.Tr2Effect()
        blur.StartUpdate()
        blur.effectFilePath = 'res:/graphics/effect/ui/glowblur.fx'
        blur.resources.append(trinity.Tr2RuntimeTextureParameter('InputMap', targets[1]))
        blur.constParameters.append(('InputMapSize', (targets[1].width,
          targets[1].height,
          0,
          0)))
        blur.constParameters.append(('Direction', (0, 1, 0, 0)))
        blur.EndUpdate()
        glowRJ.RenderEffect(blur).name = 'Blur Vert'
        glowRJ.PopRenderTarget().name = 'Restore RT'
        composite = trinity.Tr2Effect()
        composite.StartUpdate()
        composite.effectFilePath = 'res:/graphics/effect/ui/glowcomposite.fx'
        composite.resources.append(trinity.Tr2RuntimeTextureParameter('GlowMap', targets[0]))
        composite.EndUpdate()
        glowRJ.RenderEffect(composite).name = 'Composite Glow'
        return glowRJ

    def ConstructRenderSteps(self, depthMax, renderJob, renderTarget):
        myScene = self.GetRenderObject()
        viewportStep = renderJob.SetViewport()
        viewportStep.name = 'Set fullscreen viewport'
        updateStep = renderJob.Update(myScene)
        updateStep.name = self.name + ' Update'
        renderSteps = [viewportStep, updateStep]
        self._ConstructGlowTargets(renderTarget)
        if depthMax:
            cameraUpdateStep = renderJob.PythonCB(self.camera)
            cameraUpdateStep.name = self.name + ' Camera Update'
            self.viewStep = renderJob.SetView(self.camera.viewMatrix)
            self.projStep = renderJob.SetProjection(self.camera.projectionMatrix)
            renderSteps.append(cameraUpdateStep)
            renderSteps.append(self.viewStep)
            renderSteps.append(self.projStep)
        if renderTarget:
            self.renderTargetStep = renderJob.PushRenderTarget(renderTarget)
            renderSteps.append(self.renderTargetStep)
            myScene.clearBackground = True
            myScene.backgroundColor = (0, 0, 0, 1)
        if self._glowRenderTarget:
            push = renderJob.PushRenderTarget(self._glowRenderTarget)
            renderSteps.append(push)
            self._glowTargetSteps.append(push)
            renderSteps.append(renderJob.Clear((0, 0, 0, 0)))
            renderSteps.append(renderJob.PopRenderTarget())
            push = renderJob.PushRenderTarget(self._glowRenderTarget, 1)
            renderSteps.append(push)
            self._glowTargetSteps.append(push)
        renderStep = renderJob.RenderScene(myScene)
        renderStep.name = self.name + ' Render'
        renderSteps.append(renderStep)
        if self._glowRenderTarget:
            renderSteps.append(renderJob.PopRenderTarget(1))
            glowRJ = self._ConstructGlowRenderJob()
            self._glowProcessStep = renderJob.RunJob(glowRJ)
            self._glowProcessStep.name = 'Process Glow'
            renderSteps.append(self._glowProcessStep)
        if renderTarget and type(renderTarget) is trinity.Tr2RenderTarget:
            renderSteps.append(renderJob.PopRenderTarget())
            self.generateMipsStep = renderJob.GenerateMipMaps(renderTarget)
            renderSteps.append(self.generateMipsStep)
        self.renderSteps = renderSteps

    def SetRenderTarget(self, renderTarget):
        if self.renderTargetStep is not None:
            self.renderTargetStep.renderTarget = renderTarget
        if self.generateMipsStep is not None:
            self.generateMipsStep.renderTarget = renderTarget
        self._RefreshGlowTargets(renderTarget)

    def InitCamera(self):
        pass

    def GetCamera(self):
        return self.camera

    def Create3DRenderTarget(self, destscene):
        sprite = blue.resMan.LoadObject('res:/uicore/uiInSpace.red')
        area = sprite.mesh.opaqueAreas[0]
        texture = area.effect.resources[0]
        destscene.objects.append(sprite)
        rj = trinity.CreateRenderJob()
        rj.Update(destscene)
        myScene = self.GetRenderObject()
        renderTarget = trinity.Tr2RenderTarget(self.width, self.height, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
        rj.PushRenderTarget(renderTarget)
        rj.RenderScene(myScene).name = 'Render 2D scene'
        rj.PopRenderTarget()
        rj.ScheduleRecurring(insertFront=True)
        texture.SetResource(trinity.TriTextureRes(renderTarget))
        myScene.is2dRender = True
        self.sceneObject = blue.BluePythonWeakRef(sprite)
        self.renderSteps[-1].enabled = False

    def GetInSceneObject(self):
        if self.sceneObject:
            return self.sceneObject.object

    def CheckMouseMove(self, *args):
        if uicore.uilib.leftbtn and uicore.uilib.Key(uiconst.VK_MENU):
            if uicore.uilib.rightbtn:
                self.camera.distance -= uicore.uilib.dy
            else:
                self.camera.AdjustYaw(-uicore.uilib.dx * 0.1)
                self.camera.AdjustPitch(-uicore.uilib.dy * 0.1)
        return 1

    def _CleanUpRenderJob(self):
        if self.renderSteps:
            renderJob = uicore.uilib.GetRenderJob()
            if renderJob:
                for each in self.renderSteps:
                    if each in renderJob.steps:
                        renderJob.steps.remove(each)

        self.renderSteps = None
        self.renderTargetStep = None
        self.generateMipsStep = None
        self._glowRenderTarget = None
        self._blurRenderTarget0 = None
        self._blurRenderTarget1 = None
        self._glowProcessStep = None
        self._glowTransform = None
        self._glowTargetSteps = []

    def _OnClose(self, *args, **kwds):
        self._CleanUpRenderJob()
        uicore.uilib.RemoveRootObject(self)
        Container._OnClose(self, *args, **kwds)

    def AddLayer(self, name, decoClass = None, subLayers = None, idx = -1, loadLayerClass = False):
        useClass = decoClass or LayerCore
        layer = useClass(parent=self, name=name, idx=idx, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        layer.decoClass = decoClass
        uicore.layerData[name] = (useClass, subLayers)
        if name.startswith('l_'):
            setattr(uicore.layer, name[2:].lower(), layer)
        else:
            setattr(uicore.layer, name.lower(), layer)
        if subLayers is not None:
            for _layerName, _decoClass, _subLayers in subLayers:
                layer.AddLayer(_layerName, _decoClass, _subLayers)

        return layer

    def UpdateSize(self):
        if self.isFullscreen and not self.renderTargetStep:
            preSize = (self.width, self.height)
            self.width = int(float(trinity.device.width) / self.dpiScaling)
            self.height = int(float(trinity.device.height) / self.dpiScaling)
            self.renderObject.isFullscreen = True
            if preSize != (self.width, self.height):
                self.FlagForceUpdateAlignment()
        self._RefreshGlowTargets(self._GetRenderTarget())
        if self.camera:
            self.camera.AdjustForDesktop()

    def GetAbsoluteSize(self):
        return (self.width, self.height)

    def GetAbsolutePosition(self):
        return (0, 0)

    @property
    def dpiScaling(self):
        return self._dpiScaling

    @dpiScaling.setter
    def dpiScaling(self, value):
        self._dpiScaling = value
        uicore.dpiScaling = value
        self.UpdateSize()
        for each in uicore.textObjects:
            each.OnCreate(trinity.device)

    @property
    def rotationY(self):
        return self._rotationY

    @rotationY.setter
    def rotationY(self, value):
        self._rotationY = value
        ro = self.renderObject
        if ro:
            ro.rotation = geo2.QuaternionRotationSetYawPitchRoll(self._rotationY, self._rotationX, self._rotationZ)

    @property
    def clearBackground(self):
        return self.renderObject.clearBackground

    @clearBackground.setter
    def clearBackground(self, value):
        self.renderObject.clearBackground = value

    @property
    def backgroundColor(self):
        return self.renderObject.backgroundColor

    @backgroundColor.setter
    def backgroundColor(self, value):
        self.renderObject.backgroundColor = value

    def UpdateUIScaling(self, value, oldValue):
        self.dpiScaling = value
        self.UpdateSize()
        super(UIRoot, self).UpdateUIScaling(value, oldValue)

    @property
    def glowEnabled(self):
        return self._glowEnabled

    @glowEnabled.setter
    def glowEnabled(self, value):
        if self._glowEnabled == value:
            return
        self._glowEnabled = value
        rt = self._GetRenderTarget()
        self._CleanUpRenderJob()
        self.ConstructRenderSteps(self.depthMax, self._renderJob, rt)

    @property
    def glowBrightness(self):
        return self._glowBrightness

    @glowBrightness.setter
    def glowBrightness(self, value):
        self._glowBrightness = value
        if self._glowTransform:
            self._glowTransform.parameters.FindByName('Brightness').value = value

    @property
    def glowDistortion(self):
        return self._glowDistortion

    @glowDistortion.setter
    def glowDistortion(self, value):
        self._glowDistortion = value
        if self._glowTransform:
            self._glowTransform.parameters.FindByName('DistortionStrength').value = value

    @property
    def glowHighlightRadius(self):
        return self._glowHighlightRadius

    @glowHighlightRadius.setter
    def glowHighlightRadius(self, value):
        self._glowHighlightRadius = value
        if self._glowTransform:
            self._glowTransform.parameters.FindByName('HighlightRadius').value = value

    @property
    def glowHighlightBrightness(self):
        return self._glowHighlightBrightness

    @glowHighlightBrightness.setter
    def glowHighlightBrightness(self, value):
        self._glowHighlightBrightness = value
        if self._glowTransform:
            self._glowTransform.parameters.FindByName('HighlightBrightness').value = value

    @property
    def glowHighlightCoords(self):
        return self._glowHighlightCoords

    @glowHighlightCoords.setter
    def glowHighlightCoords(self, value):
        self._glowHighlightCoords = value
        if self._glowTransform:
            self._glowTransform.parameters.FindByName('HighlightCoords').value = value
