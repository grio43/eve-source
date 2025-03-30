#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\mapViewSceneContainer.py
import trinity
from eve.client.script.ui.control.scenecontainer import SceneContainer
import evegraphics.settings as gfxsettings

class MapViewSceneContainer(SceneContainer):

    def ApplyAttributes(self, attributes):
        self.cameraID = attributes.cameraID
        SceneContainer.ApplyAttributes(self, attributes)

    def PrepareCamera(self):
        self.camera = sm.GetService('sceneManager').GetOrCreateCamera(self.cameraID)
        self.camera.OnActivated()
        self.camera.SetViewport(self.viewport)
        self.projection = self.camera.projectionMatrix

    def Close(self, *args, **kwds):
        SceneContainer.Close(self, *args, **kwds)
        self.scene = None
        self.camera = None
        self.projection = None
        self.renderJob = None
        self.bracketCurveSet = None

    def DisplaySpaceScene(self, blendMode = None):
        from trinity.sceneRenderJobSpaceEmbedded import CreateEmbeddedRenderJobSpace
        self.renderJob = CreateEmbeddedRenderJobSpace(usePostProcessing=False, additiveBlending=True)
        if self.destroyed:
            return
        rj = self.renderJob
        rj.ScheduleUpdateJob()
        rj.CreateBasicRenderSteps()
        rj.OverrideSettings('aaQuality', gfxsettings.AA_QUALITY_DISABLED)
        self.CreateBracketCurveSet()
        rj.SetActiveCamera(None, self.camera.viewMatrix, self.camera.projectionMatrix)
        rj.SetScene(self.scene)
        rj.SetViewport(self.viewport)
        if self.destroyed:
            return
        rj.UpdateViewport(self.viewport)
        rj.SetCameraCallback(self.UpdateCamera)
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
        self.renderObject.renderJob = self.renderJob

    def UpdateCamera(self, *args):
        self.camera._Update()

    def SetClearColor(self, clearColor):
        step = self.renderObject.renderJob.GetStep('CLEAR')
        if step:
            step.color = clearColor

    def DisplayScene(self, addClearStep = False, addBitmapStep = False, addShadowStep = False, backgroundImage = None):
        pass

    def UpdateViewPort(self, *args):
        self.fieldOfView = self.camera.fov
        self.backClip = self.camera.farClip
        self.frontClip = self.camera.nearClip
        SceneContainer.UpdateViewPort(self, *args)

    def UpdateProjection(self):
        self.camera.UpdateProjection()
