#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinity\sceneRenderJobBase.py
import blue
import decometaclass
from . import _singletons
from . import _trinity as trinity
from .renderJob import renderJobs

class SceneRenderJobBase(object):
    __cid__ = 'trinity.TriRenderJob'
    __metaclass__ = decometaclass.BlueWrappedMetaclass
    renderStepOrder = []
    visualizations = []

    def Start(self):
        if not hasattr(self, 'renderOrder'):
            self.renderOrder = 0
        if not self.scheduled:
            wantedIndex = 0
            for index, rj in enumerate(renderJobs.recurring):
                if hasattr(rj, 'renderOrder') and self.renderOrder <= rj.renderOrder:
                    wantedIndex += 1
                else:
                    break

            renderJobs.recurring.insert(wantedIndex, self)
            self.scheduled = True

    def Pause(self):
        if self.scheduled:
            self.UnscheduleRecurring()
            self.scheduled = False

    def UnscheduleRecurring(self, scheduledRecurring = None):
        if scheduledRecurring is None:
            scheduledRecurring = renderJobs.recurring
        if self in scheduledRecurring:
            scheduledRecurring.remove(self)

    def ScheduleOnce(self):
        if not self.enabled:
            self.enabled = True
            try:
                self.DoPrepareResources()
            except trinity.ALError:
                pass

        renderJobs.once.append(self)

    def WaitForFinish(self):
        while not (self.status == trinity.RJ_DONE or self.status == trinity.RJ_FAILED):
            blue.synchro.Yield()

    def Disable(self):
        self.enabled = False
        self.DoReleaseResources(1)
        if self.scheduled:
            renderJobs.recurring.remove(self)
            self.scheduled = False

    def Enable(self, schedule = True):
        self.enabled = True
        try:
            self.DoPrepareResources()
        except trinity.ALError:
            pass

        if schedule:
            self.Start()

    def AddStep(self, stepKey, step):
        renderStepOrder = self.renderStepOrder
        if renderStepOrder is None:
            return
        elif stepKey not in renderStepOrder:
            return
        else:
            if stepKey in self.stepsLookup:
                s = self.stepsLookup[stepKey]
                if s.object is None:
                    del self.stepsLookup[stepKey]
                else:
                    replaceIdx = self.steps.index(s.object)
                    if replaceIdx >= 0:
                        while True:
                            try:
                                self.steps.remove(s.object)
                            except:
                                break

                        self.steps.insert(replaceIdx, step)
                        step.name = stepKey
                        self.stepsLookup[stepKey] = blue.BluePythonWeakRef(step)
                        return step
            stepIdx = renderStepOrder.index(stepKey)
            nextExistingStepIdx = None
            nextExistingStep = None
            for i, oStep in enumerate(renderStepOrder[stepIdx + 1:]):
                if oStep in self.stepsLookup and self.stepsLookup[oStep].object is not None:
                    nextExistingStepIdx = i + stepIdx
                    nextExistingStep = self.stepsLookup[oStep].object
                    break

            if nextExistingStepIdx is not None:
                insertPosition = self.steps.index(nextExistingStep)
                self.steps.insert(insertPosition, step)
                step.name = stepKey
                self.stepsLookup[stepKey] = blue.BluePythonWeakRef(step)
                return step
            step.name = stepKey
            self.stepsLookup[stepKey] = blue.BluePythonWeakRef(step)
            self.steps.append(step)
            return step

    def HasStep(self, stepKey):
        if stepKey in self.stepsLookup:
            s = self.stepsLookup[stepKey].object
            if s is not None:
                return True
        return False

    def RemoveStep(self, stepKey):
        if stepKey in self.stepsLookup:
            s = self.stepsLookup[stepKey].object
            if s is not None:
                while True:
                    try:
                        self.steps.remove(s)
                    except:
                        break

            del self.stepsLookup[stepKey]

    def EnableStep(self, stepKey):
        self.SetStepAttr(stepKey, 'enabled', True)

    def DisableStep(self, stepKey):
        self.SetStepAttr(stepKey, 'enabled', False)

    def GetStep(self, stepKey):
        if stepKey in self.stepsLookup:
            return self.stepsLookup[stepKey].object

    def SetStepAttr(self, stepKey, attr, val):
        if stepKey in self.stepsLookup:
            s = self.stepsLookup[stepKey].object
            if s is not None:
                setattr(s, attr, val)

    def GetScene(self):
        if self.scene is None:
            return
        else:
            return self.scene.object

    def GetVisualizationsForRenderjob(self):
        return self.visualizations

    def AppendRenderStepToRenderStepOrder(self, renderStep):
        if renderStep not in self.renderStepOrder:
            self.renderStepOrder.append(renderStep)

    def ApplyVisualization(self, vis):
        if self.appliedVisualization is not None:
            self.appliedVisualization.RemoveVisualization(self)
            self.appliedVisualization = None
        if vis is not None:
            visInstance = vis()
            visInstance.ApplyVisualization(self)
            self.appliedVisualization = visInstance

    def ManualInit(self, name = 'BaseSceneRenderJob'):
        self.name = name
        self.scene = None
        self.stepsLookup = {}
        self.enabled = False
        self.scheduled = False
        self.appliedVisualization = None
        self.view = None
        self.projection = None
        self.viewport = None
        self.upscalingContextID = None
        self.swapChain = None
        self.renderOrder = 0
        self.renderSize = None
        self._ManualInit(name)

    def DoPrepareResources(self):
        raise NotImplementedError('You must provide an implementation of DoPrepareResources(self)')

    def DoReleaseResources(self, level):
        raise NotImplementedError('You must provide an implementation of DoReleaseResources(self, level)')

    def SetScene(self, scene):
        if scene is None:
            self.scene = None
        else:
            self.scene = blue.BluePythonWeakRef(scene)
        self._SetScene(scene)

    def CreateBasicRenderSteps(self):
        self.steps.removeAt(-1)
        self.stepsLookup = {}
        self._CreateBasicRenderSteps()

    def SetViewport(self, viewport = None):
        if viewport is None:
            self.RemoveStep('SET_VIEWPORT')
            self.viewport = None
        else:
            self.AddStep('SET_VIEWPORT', trinity.TriStepSetViewport(viewport))
            self.viewport = blue.BluePythonWeakRef(viewport)
        return self.viewport

    def GetViewport(self):
        if self.viewport is None:
            return
        elif hasattr(self.viewport, 'object'):
            return self.viewport.object
        else:
            return self.viewport

    def SetCameraView(self, view):
        if view is None:
            self.RemoveStep('SET_VIEW')
            self.view = None
        else:
            self.AddStep('SET_VIEW', trinity.TriStepSetView(view))
            self.view = blue.BluePythonWeakRef(view)

    def SetCameraProjection(self, proj):
        if proj is None:
            self.RemoveStep('SET_PROJECTION')
            self.projection = None
        else:
            self.AddStep('SET_PROJECTION', trinity.TriStepSetProjection(proj))
            self.projection = blue.BluePythonWeakRef(proj)

    def GetCameraProjection(self):
        if self.projection is None:
            return
        elif hasattr(self.projection, 'object'):
            return self.projection.object
        else:
            return self.projection

    def SetActiveCamera(self, camera):
        self.SetCameraView(camera.viewMatrix)
        self.SetCameraProjection(camera.projectionMatrix)

    def SetClearColor(self, color):
        step = self.GetStep('CLEAR')
        if step is not None:
            step.color = color

    def SetSwapChain(self, swapChain):
        self.DoReleaseResources(1)
        if swapChain is None:
            self.RemoveStep('PRESENT_SWAPCHAIN')
        else:
            self.AddStep('PRESENT_SWAPCHAIN', trinity.TriStepPresentSwapChain(swapChain))
        self.swapChain = blue.BluePythonWeakRef(swapChain)
        self.DoPrepareResources()

    def GetSwapChain(self):
        if self.swapChain is not None:
            return self.swapChain.object

    def PrepareUpscaling(self, displayWidth, displayHeight, backbufferFormat, depthStencilFormat, allowFramegen = True):
        if _singletons.device.upscalingTechnique != trinity.UPSCALING_TECHNIQUE.NONE:
            if self.upscalingContextID is not None:
                self.upscalingContextID = _singletons.device.CreateUpscalingContext(displayWidth, displayHeight, backbufferFormat, depthStencilFormat, allowFramegen, self.upscalingContextID)
            else:
                self.upscalingContextID = _singletons.device.CreateUpscalingContext(displayWidth, displayHeight, backbufferFormat, depthStencilFormat, allowFramegen)
            self.AddStep('SET_UPSCALING_CONTEXT_ID', trinity.TriStepSetUpscalingContextID(self.upscalingContextID))
        else:
            self.AddStep('SET_UPSCALING_CONTEXT_ID', trinity.TriStepSetUpscalingContextID())
            self.DeleteUpscalingContext()

    def DeleteUpscalingContext(self):
        if self.upscalingContextID is not None:
            _singletons.device.DeleteUpscalingContext(self.upscalingContextID)
            self.upscalingContextID = None

    def GetRenderSize(self):
        if self.upscalingContextID is None:
            return self.GetDisplaySize()
        size = _singletons.device.GetRenderResolution(self.upscalingContextID)
        if size[0] < 0 or size[1] < 0:
            return self.GetDisplaySize()
        return (int(size[0]), int(size[1]))

    def GetDisplaySize(self):
        if self.GetSwapChain() is not None:
            if self.GetSwapChain().backBuffer is not None:
                width = self.GetSwapChain().backBuffer.width
                height = self.GetSwapChain().backBuffer.height
            else:
                width = self.GetSwapChain().width
                height = self.GetSwapChain().height
        else:
            width = _singletons.device.width
            height = _singletons.device.height
        return (width, height)

    def GetBackBufferRenderTarget(self):
        if self.GetSwapChain() is not None:
            return self.GetSwapChain().backBuffer
        return _singletons.device.GetRenderContext().GetDefaultBackBuffer()
