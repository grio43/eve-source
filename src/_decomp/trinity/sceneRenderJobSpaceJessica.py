#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinity\sceneRenderJobSpaceJessica.py
from . import _trinity as trinity
from . import _singletons
from .sceneRenderJobSpace import SceneRenderJobSpace
import evegraphics.settings as gfxsettings

def CreateJessicaSpaceRenderJob(name = None):
    newRJ = SceneRenderJobSpaceJessica()
    if name is not None:
        newRJ.ManualInit(name)
    else:
        newRJ.ManualInit()
    return newRJ


class SceneRenderJobSpaceJessica(SceneRenderJobSpace):

    def _ManualInit(self, name = 'SceneRenderJobSpace'):
        SceneRenderJobSpace._ManualInit(self, name)
        self.persistedPostProcess = {}
        self.settings = {'aaQuality': 3,
         'postProcessingQuality': 2,
         'shadowQuality': 2,
         'shadowMapSize': 2048,
         'reflections': gfxsettings.GFX_REFLECTION_QUALITY_ULTRA,
         'ao': gfxsettings.GFX_AO_QUALITY_HIGH,
         'volumetricQuality': gfxsettings.GFX_VOLUMETRIC_QUALITY_HIGH,
         'upscalingTechnique': trinity.UPSCALING_TECHNIQUE.NONE,
         'upscalingSetting': trinity.UPSCALING_SETTING.NATIVE,
         'frameGeneration': False}
        self.backBufferOverride = None
        self.depthBufferOverride = None

    def SetSettings(self, rjSettings):
        self.settings = rjSettings

    def GetSettings(self):
        return self.settings

    def _GetSettings(self):
        return self.settings

    def OverrideBuffers(self, backBuffer, depthBuffer):
        self.backBufferOverride = backBuffer
        self.depthBufferOverride = depthBuffer

    def _SetSettingsBasedOnPerformancePreferences(self):
        self.aaQuality = self.settings['aaQuality']
        self.shadowQuality = self.settings['shadowQuality']
        if self.shadowQuality == 0:
            self.cascadedShadowMap = None
            self.rtManager = None
            return
        if self.shadowQuality < 3:
            self.cascadedShadowMap = trinity.Tr2ShadowMap()
        elif self.shadowQuality == 3:
            self.rtManager = trinity.Tr2RaytracingManager()

    def _RefreshRenderTargets(self):
        SceneRenderJobSpace._RefreshRenderTargets(self)
        if self.depthBufferOverride:
            self.AddStep('SET_SWAPCHAIN_DEPTH', trinity.TriStepPushDepthStencil(self.depthBufferOverride))
            self.AddStep('RESET_SWAPCHAIN_DEPTH', trinity.TriStepPopDepthStencil())
        if self.backBufferOverride:
            self.AddStep('SET_SWAPCHAIN_RT', trinity.TriStepPushRenderTarget(self.backBufferOverride))
            self.AddStep('RESET_SWAPCHAIN_RT', trinity.TriStepPopRenderTarget())

    def GetDisplaySize(self):
        if self.backBufferOverride is None:
            return SceneRenderJobSpace.GetDisplaySize(self)
        return (self.backBufferOverride.width, self.backBufferOverride.height)

    def GetBackBufferRenderTarget(self):
        if self.backBufferOverride is not None:
            return self.backBufferOverride
        return SceneRenderJobSpace.GetBackBufferRenderTarget(self)
