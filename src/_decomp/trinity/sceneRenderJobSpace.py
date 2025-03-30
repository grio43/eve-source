#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinity\sceneRenderJobSpace.py
import logging
import blue
import evegraphics.settings as gfxsettings
from . import _trinity as trinity
from . import _singletons
from .renderJob import CreateRenderJob
from .sceneRenderJobBase import SceneRenderJobBase
from .renderJobUtils import renderTargetManager as rtm
from . import evePostProcess
DEFAULT_POSTPROCESS_PATH = 'res:/dx9/default/postprocess.red'
DEFAULT_SSAO_PATH = 'res:/dx9/default/ssao.red'
logger = logging.getLogger(__name__)

def CreateSceneRenderJobSpace(name = None):
    newRJ = SceneRenderJobSpace()
    if name is not None:
        newRJ.ManualInit(name)
    else:
        newRJ.ManualInit()
    return newRJ


def _IsIntelGPU():
    vendorID = 0
    try:
        vendorID = _singletons.adapters.GetAdapterInfo(_singletons.device.adapter).vendorID
    except (AttributeError, trinity.ALError):
        pass

    return vendorID == 32902


def CanSupportSsao():
    return blue.sysinfo.os.platform != blue.OsPlatform.OSX or not _IsIntelGPU()


class SceneRenderJobSpace(SceneRenderJobBase):
    renderStepOrder = ['SET_SWAPCHAIN_RT',
     'SET_SWAPCHAIN_DEPTH',
     'SET_UPDATE_VIEW',
     'SET_UPDATE_PROJECTION',
     'SET_UPSCALING_CONTEXT_ID',
     'SET_CUSTOM_RT',
     'SET_DEPTH',
     'SET_VAR_DEPTH',
     'SET_VIEWPORT',
     'CAMERA_UPDATE',
     'SET_PROJECTION',
     'SET_VIEW',
     'UPDATE_PHYSICS',
     'UPDATE_SCENE',
     'SET_BRACKET_VIEWPORT',
     'UPDATE_BRACKETS',
     'CLEAR',
     'BEGIN_RENDER',
     'RENDER_REFLECTIONS',
     'RENDER_BACKGROUND',
     'DO_BACKGROUND_DISTORTIONS',
     'RENDER_DEPTH_PASS',
     'RENDER_MAIN_PASS',
     'DO_DISTORTIONS',
     'END_RENDERING',
     'SET_PERFRAME_DATA',
     'SET_FINAL_RT',
     'RJ_POSTPROCESSING',
     'FINAL_BLIT',
     'FPS_COUNTER',
     'SET_UI_PROJECTION',
     'SET_UI_VIEW',
     'RENDER_DEBUG',
     'UPDATE_TOOLS',
     'RENDER_PROXY',
     'RENDER_INFO',
     'RENDER_VISUAL',
     'RENDER_TOOLS',
     'RENDER_3D_UI',
     'RESTORE_DEPTH',
     'RESET_SWAPCHAIN_DEPTH',
     'RESET_SWAPCHAIN_RT',
     'PRESENT_SWAPCHAIN']
    visualizations = []

    def _ManualInit(self, name = 'SceneRenderJobSpace'):
        self.scene = None
        self.clientToolsScene = None
        self.camera = None
        self.customBackBuffer = None
        self.customOpaqueBackBuffer = None
        self.customDepthStencil = None
        self.normalTexture = None
        self.blitTexture = None
        self.distortionTexture = None
        self.velocityTexture = None
        self.accumulationBuffer = None
        self.cascadedShadowMap = None
        self.rtManager = None
        self.ui = None
        self.hdrEnabled = False
        self.usePostProcessing = False
        self.shadowQuality = 0
        self.aaQuality = 0
        self.distortionEffectsEnabled = False
        self.secondaryLighting = False
        self.postProcessingQuality = 0
        self.upscalingContextID = None
        self.bbFormat = _singletons.device.GetRenderContext().GetBackBufferFormat()
        self.prepared = False
        self._enablePostProcessing = True
        self.distortionJob = evePostProcess.EvePostProcessingJob()
        self.backgroundDistortionJob = evePostProcess.EvePostProcessingJob()
        self.overrideSettings = {}
        self.SetSettingsBasedOnPerformancePreferences()
        self.updateJob = CreateRenderJob(name + '_Update')
        self.updateJob.scheduled = False
        self.gpuParticlesEnabled = True
        self.useImpostors = True
        self.reflectionSetting = gfxsettings.GFX_REFLECTION_QUALITY_LOW
        self.aoSetting = gfxsettings.GFX_AO_QUALITY_HIGH
        self.volumetricQuality = gfxsettings.GFX_VOLUMETRIC_QUALITY_HIGH
        self.shaderModel = trinity.GetShaderModel()

    def Enable(self, schedule = True):
        SceneRenderJobBase.Enable(self, schedule)
        self.SetSettingsBasedOnPerformancePreferences()

    def SuspendRendering(self):
        SceneRenderJobBase.UnscheduleRecurring(self)
        self.scheduled = False
        self.EnableGpuEmission(False)
        self.EnableUnRenderedSceneUpdate(True)

    def Start(self):
        SceneRenderJobBase.Start(self)
        self.EnableGpuEmission(True)
        self.ScheduleUpdateJob()
        self.EnableUnRenderedSceneUpdate(False)

    def ScheduleUpdateJob(self):
        if self.updateJob is not None and not self.updateJob.scheduled:
            self.updateJob.ScheduleUpdate()
            self.updateJob.scheduled = True

    def EnableGpuEmission(self, enable):
        if not self.gpuParticlesEnabled:
            return
        scene = self.GetScene()
        if scene is None:
            return
        if scene.gpuParticleSystem is not None:
            scene.gpuParticleSystem.enableEmit = enable

    def Disable(self):
        SceneRenderJobBase.Disable(self)
        self.UnscheduleUpdateJob()

    def UnscheduleUpdateJob(self):
        if self.updateJob is not None and self.updateJob.scheduled:
            self.updateJob.UnscheduleUpdate()
            self.updateJob.scheduled = False

    def UnscheduleRecurring(self, scheduledRecurring = None):
        SceneRenderJobBase.UnscheduleRecurring(self, scheduledRecurring)
        self.UnscheduleUpdateJob()

    def SetClientToolsScene(self, scene):
        if scene is None:
            self.clientToolsScene = None
        else:
            self.clientToolsScene = blue.BluePythonWeakRef(scene)
        self.AddStep('UPDATE_TOOLS', trinity.TriStepUpdate(scene))
        self.AddStep('RENDER_TOOLS', trinity.TriStepRenderScene(scene))

    def GetClientToolsScene(self):
        if self.clientToolsScene is None:
            return
        else:
            return self.clientToolsScene.object

    def SetCameraView(self, view):
        super(SceneRenderJobSpace, self).SetCameraView(view)
        self._SetUpdateStep(trinity.TriStepSetView(view), 'SET_VIEW')
        self.AddStep('SET_UI_VIEW', trinity.TriStepSetView(view))

    def SetCameraProjection(self, proj):
        super(SceneRenderJobSpace, self).SetCameraProjection(proj)
        self._SetUpdateStep(trinity.TriStepSetProjection(proj), 'SET_PROJECTION')
        self.AddStep('SET_UI_PROJECTION', trinity.TriStepSetProjection(proj))

    def SetCameraCallback(self, cb):
        if self.updateJob is not None and self.updateJob.scheduled:
            self._SetUpdateStep(trinity.TriStepPythonCB(cb), 'CAMERA_UPDATE')
        else:
            self.AddStep('CAMERA_UPDATE', trinity.TriStepPythonCB(cb))

    def SetActiveCamera(self, camera = None, view = None, projection = None):
        if camera is None and view is None and projection is None:
            self.RemoveStep('SET_VIEW')
            self.RemoveStep('SET_PROJECTION')
            self.RemoveStep('SET_UPDATE_VIEW')
            self.RemoveStep('SET_UPDATE_PROJECTION')
            self.RemoveStep('SET_UI_VIEW')
            self.RemoveStep('SET_UI_PROJECTION')
            return
        if camera is not None:
            self.AddStep('SET_VIEW', trinity.TriStepSetView(None, camera))
            self.AddStep('SET_UPDATE_VIEW', trinity.TriStepSetView(None, camera))
            self.AddStep('SET_UI_VIEW', trinity.TriStepSetView(None, camera))
            self._SetUpdateStep(trinity.TriStepSetView(None, camera), 'SET_VIEW')
            self.AddStep('SET_PROJECTION', trinity.TriStepSetProjection(camera.projectionMatrix))
            self.AddStep('SET_UPDATE_PROJECTION', trinity.TriStepSetProjection(camera.projectionMatrix))
            self._SetUpdateStep(trinity.TriStepSetProjection(camera.projectionMatrix), 'SET_PROJECTION')
        if view is not None:
            self.AddStep('SET_VIEW', trinity.TriStepSetView(view))
            self.AddStep('SET_UI_VIEW', trinity.TriStepSetView(view))
            self.AddStep('SET_UPDATE_VIEW', trinity.TriStepSetView(view))
            self._SetUpdateStep(trinity.TriStepSetView(view), 'SET_VIEW')
        if projection is not None:
            self.AddStep('SET_PROJECTION', trinity.TriStepSetProjection(projection))
            self.AddStep('SET_UI_PROJECTION', trinity.TriStepSetProjection(projection))
            self.AddStep('SET_UPDATE_PROJECTION', trinity.TriStepSetProjection(projection))
            self._SetUpdateStep(trinity.TriStepSetProjection(projection), 'SET_PROJECTION')

    def SetActiveScene(self, scene, key = None):
        self.SetScene(scene)
        self.EnableUnRenderedSceneUpdate(not self.scheduled)

    def _SetDepthMap(self):
        if not self.enabled:
            return
        if self.GetScene() is None:
            return
        setattr(self.GetScene(), 'colorTexture', self.customBackBuffer)
        setattr(self.GetScene(), 'opaqueColorTexture', self.customOpaqueBackBuffer)
        setattr(self.GetScene(), 'depthTexture', self.customDepthStencil)

    def _SetNormalMap(self):
        if not self.enabled:
            return
        if self.GetScene() is None:
            return
        setattr(self.GetScene(), 'normalTexture', self.normalTexture)

    def _SetDistortionMap(self):
        if not self.enabled:
            return
        if self.GetScene() is None:
            return
        if hasattr(self.GetScene(), 'distortionTexture'):
            self.GetScene().distortionTexture = self.distortionTexture

    def ApplyShadowQuality(self):
        self._SetShadowSetting()

    def _SetShadowSetting(self):
        scene = self.GetScene()
        if scene is None:
            return
        if self.shadowQuality == 0:
            self.DisableShadows()
        elif self.shadowQuality < 3:
            if self.cascadedShadowMap is None:
                self.cascadedShadowMap = trinity.Tr2ShadowMap()
            scene.cascadedShadowMap = self.cascadedShadowMap
            self.DisableRaytracedShadows()
        elif self.shadowQuality == 3:
            if self.rtManager is None:
                self.rtManager = trinity.Tr2RaytracingManager()
            scene.raytracingManager = self.rtManager
            self.DisableCascadedShadows()
        scene.shadowQualitySetting = self.shadowQuality

    def _SetSecondaryLighting(self):
        scene = self.GetScene()
        if scene is None:
            return
        if self.secondaryLighting:
            if not scene.shLightingManager:
                scene.shLightingManager = trinity.Tr2ShLightingManager()
                scene.shLightingManager.primaryIntensity = gfxsettings.SECONDARY_LIGHTING_INTENSITY
                scene.shLightingManager.secondaryIntensity = gfxsettings.SECONDARY_LIGHTING_INTENSITY
        else:
            scene.shLightingManager = None

    def _RefreshPostProcessingJob(self, job, enabled):
        if enabled:
            job.Prepare(self._GetSourceRTForPostProcessing(), self.blitTexture, destination=None)
            job.CreateSteps()
        else:
            job.Release()

    def _GetSourceRTForPostProcessing(self):
        if self.customBackBuffer is not None:
            return self.customBackBuffer
        return self.GetBackBufferRenderTarget()

    def _CreateDepthPass(self):
        rj = trinity.TriRenderJob()
        rj.steps.append(trinity.TriStepPushViewport())
        rj.steps.append(trinity.TriStepPushDepthStencil(self.customDepthStencil))
        rj.steps.append(trinity.TriStepPopViewport())
        rj.steps.append(trinity.TriStepPushViewport())
        rj.steps.append(trinity.TriStepRenderPass(self.GetScene(), trinity.TRIPASS_DEPTH_PASS))
        rj.steps.append(trinity.TriStepPopDepthStencil())
        rj.steps.append(trinity.TriStepPopViewport())
        self.AddStep('RENDER_DEPTH_PASS', trinity.TriStepRunJob(rj))

    def _CreateUpdateStep(self, step, name, enabled = True):
        self.updateJob.steps.append(step)
        step.name = name
        step.enabled = enabled

    def _CreateUpdateSteps(self):
        self._CreateUpdateStep(trinity.TriStepPushViewport(), 'PUSH_VIEWPORT')
        self._CreateUpdateStep(trinity.TriStepSetViewport(), 'SET_VIEWPORT')
        self._CreateUpdateStep(trinity.TriStepPythonCB(), 'CAMERA_UPDATE')
        self._CreateUpdateStep(trinity.TriStepSetView(), 'SET_VIEW')
        self._CreateUpdateStep(trinity.TriStepSetProjection(), 'SET_PROJECTION')
        self._CreateUpdateStep(trinity.TriStepUpdate(self.GetScene()), 'UPDATE_SCENE', enabled=False)
        self._CreateUpdateStep(trinity.TriStepPopViewport(), 'POP_VIEWPORT')

    def SetBracketCurveSet(self, cs):
        self.SetStepAttr('UPDATE_BRACKETS', 'object', cs)

    def _SetUpdateStep(self, step, name):
        if self.updateJob is None:
            return
        step.name = name
        idx = None
        for i, each in enumerate(self.updateJob.steps):
            if each.name == name:
                idx = i
                break

        if idx is None:
            raise KeyError('Update step is not found')
        self.updateJob.steps[idx] = step

    def _SetScene(self, scene):
        if scene is not None:

            def load_default(path, default_type):
                if blue.paths.exists(path):
                    return trinity.Load(path)
                else:
                    logger.info('Missing file for project specific defaults: %s. Returning trinity defaults', path)
                    return default_type()

            if hasattr(scene, 'postprocess') and scene.postprocess is None:
                scene.postprocess = load_default(DEFAULT_POSTPROCESS_PATH, trinity.Tr2PostProcess2)
            if hasattr(scene, 'SSAO') and scene.SSAO is None:
                scene.SSAO = load_default(DEFAULT_SSAO_PATH, trinity.Tr2SSAO)
        self._CreateRenderTargets()
        self._RefreshRenderTargets()
        self.UpdateTAAEffect()
        self.ModifyPostProcessForPerformance()
        self.SetStepAttr('UPDATE_SCENE', 'object', scene)
        self.SetStepAttr('RENDER_MAIN_PASS', 'scene', scene)
        self.SetStepAttr('BEGIN_RENDER', 'scene', scene)
        self.SetStepAttr('END_RENDERING', 'scene', scene)
        self.SetStepAttr('SET_PERFRAME_DATA', 'scene', scene)
        self.SetStepAttr('RENDER_3D_UI', 'scene', scene)
        self.SetStepAttr('RENDER_BACKGROUND', 'scene', scene)
        self.SetStepAttr('RENDER_REFLECTIONS', 'scene', scene)
        self.SetStepAttr('DO_BACKGROUND_DISTORTIONS', 'predicate', scene)
        self.SetStepAttr('DO_DISTORTIONS', 'predicate', scene)
        self._CreateDepthPass()
        self.ApplyPerformancePreferencesToScene()

    def UpdateTAAEffect(self):
        scene = self.GetScene()
        if scene is not None and scene.postprocess is not None:
            if self.IsAAEnabled():
                scene.postprocess.taa = trinity.Tr2PPTaaEffect()
                scene.postprocess.taa.quality = self.aaQuality
            else:
                scene.postprocess.taa = None

    def _CreateBasicRenderSteps(self):
        if self.updateJob is not None:
            if len(self.updateJob.steps) == 0:
                self._CreateUpdateSteps()
        scene = self.GetScene()
        self.AddStep('UPDATE_SCENE', trinity.TriStepUpdate(scene))
        self.AddStep('UPDATE_BRACKETS', trinity.TriStepUpdate())
        self.AddStep('SET_VIEWPORT', trinity.TriStepSetViewport())
        self.AddStep('BEGIN_RENDER', trinity.TriStepRenderPass(scene, trinity.TRIPASS_BEGIN_RENDER))
        self.AddStep('END_RENDERING', trinity.TriStepRenderPass(scene, trinity.TRIPASS_END_RENDER))
        self.AddStep('RENDER_REFLECTIONS', trinity.TriStepRenderPass(scene, trinity.TRIPASS_REFLECTION_RENDER))
        self.AddStep('RENDER_MAIN_PASS', trinity.TriStepRenderPass(scene, trinity.TRIPASS_MAIN_RENDER))
        self.AddStep('SET_PERFRAME_DATA', trinity.TriStepRenderPass(scene, trinity.TRIPASS_SET_PERFRAME_DATA))
        self.AddStep('RENDER_3D_UI', trinity.TriStepRenderPass(scene, trinity.TRIPASS_RENDER_UI))
        self._CreateDepthPass()
        self.AddStep('RENDER_BACKGROUND', trinity.TriStepRenderPass(scene, trinity.TRIPASS_BACKGROUND_RENDER))
        self.AddStep('DO_BACKGROUND_DISTORTIONS', trinity.TriStepPredicated('hasBackgroundDistortionBatches', scene, trinity.TriStepRunJob(self.backgroundDistortionJob)))
        self.AddStep('CLEAR', trinity.TriStepClear((0.0, 0.0, 0.0, 0.0), 0.0))
        if self.clientToolsScene is not None:
            self.SetClientToolsScene(self.clientToolsScene.object)

    def DoReleaseResources(self, level):
        self.prepared = False
        self.hdrEnabled = False
        self.usePostProcessing = False
        self.shadowQuality = 0
        self.cascadedShadowMap = None
        self.customBackBuffer = None
        self.customOpaqueBackBuffer = None
        self.customDepthStencil = None
        self.blitTexture = None
        self.distortionTexture = None
        self.accumulationBuffer = None
        self.velocityTexture = None
        self.DeleteUpscalingContext()
        self.distortionJob.Release()
        self.backgroundDistortionJob.Release()
        self.distortionJob.SetPostProcessVariable('Distortion', 'TexDistortion', None)
        self.backgroundDistortionJob.SetPostProcessVariable('Distortion', 'TexDistortion', None)
        self._CreateRenderTargets()
        self._SetDistortionMap()
        self._RefreshRenderTargets()

    def _GetSettings(self):
        currentSettings = {}
        currentSettings['postProcessingQuality'] = self.overrideSettings.get(gfxsettings.GFX_POST_PROCESSING_QUALITY, gfxsettings.Get(gfxsettings.GFX_POST_PROCESSING_QUALITY))
        currentSettings['shadowQuality'] = gfxsettings.Get(gfxsettings.GFX_SHADOW_QUALITY)
        currentSettings['aaQuality'] = gfxsettings.Get(gfxsettings.GFX_ANTI_ALIASING)
        try:
            currentSettings['gpuParticles'] = gfxsettings.Get(gfxsettings.UI_GPU_PARTICLES_ENABLED)
        except gfxsettings.UninitializedSettingsGroupError:
            currentSettings['gpuParticles'] = gfxsettings.GetDefault(gfxsettings.UI_GPU_PARTICLES_ENABLED)

        currentSettings['shaderModel'] = gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY)
        if currentSettings['shaderModel'] == gfxsettings.SHADER_MODEL_LOW:
            currentSettings['ao'] = gfxsettings.GFX_AO_QUALITY_OFF
        else:
            currentSettings['ao'] = gfxsettings.Get(gfxsettings.GFX_AO_QUALITY)
        currentSettings['upscalingTechnique'] = gfxsettings.Get(gfxsettings.GFX_UPSCALING_TECHNIQUE)
        currentSettings['upscalingSetting'] = gfxsettings.Get(gfxsettings.GFX_UPSCALING_SETTING)
        currentSettings['frameGeneration'] = gfxsettings.Get(gfxsettings.GFX_FRAMEGENERATION_ENABLED)
        currentSettings['dofEnabled'] = gfxsettings.Get(gfxsettings.GFX_DOF_POSTPROCESS_ENABLED)
        currentSettings['volumetricQuality'] = gfxsettings.Get(gfxsettings.GFX_VOLUMETRIC_QUALITY)
        self._GetRefectionSettings(currentSettings)
        if blue.sysinfo.os.platform == blue.OsPlatform.OSX and blue.sysinfo.os.majorVersion == 10 and blue.sysinfo.os.minorVersion <= 14 and _IsIntelGPU():
            logger.warn('Disabling GPU particles because of issues with Intel GPUs on macOS 10.14')
            currentSettings['gpuParticles'] = False
        return currentSettings

    def _GetRefectionSettings(self, currentSettings):
        if currentSettings['shaderModel'] == gfxsettings.SHADER_MODEL_LOW:
            currentSettings['reflections'] = gfxsettings.GFX_REFLECTION_QUALITY_OFF
            gfxsettings.Set(gfxsettings.GFX_REFLECTION_QUALITY, currentSettings['reflections'], pending=False)
        else:
            currentSettings['reflections'] = gfxsettings.Get(gfxsettings.GFX_REFLECTION_QUALITY)
            if currentSettings['reflections'] == gfxsettings.GFX_REFLECTION_QUALITY_OFF:
                gfxsettings.SetDefault(gfxsettings.GFX_REFLECTION_QUALITY, pending=False)
                currentSettings['reflections'] = gfxsettings.Get(gfxsettings.GFX_REFLECTION_QUALITY)

    def ApplyBaseSettings(self):
        currentSettings = self._GetSettings()
        self.bbFormat = _singletons.device.GetRenderContext().GetBackBufferFormat()
        self.postProcessingQuality = currentSettings['postProcessingQuality']
        self.shadowQuality = currentSettings['shadowQuality']
        self.aaQuality = currentSettings['aaQuality']
        self.hdrEnabled = self.postProcessingQuality > 0 or _singletons.device.upscalingTechnique != trinity.UPSCALING_TECHNIQUE.NONE
        self.gpuParticlesEnabled = currentSettings.get('gpuParticles', True)
        isDepth = trinity.GetShaderModel().endswith('DEPTH')
        self.secondaryLighting = self.distortionEffectsEnabled = isDepth
        trinity.settings.SetValue('eveSpaceSceneDynamicLighting', trinity.GetShaderModel().endswith('DEPTH'))
        trinity.settings.SetValue('postprocessDofEnabled', currentSettings.get('dofEnabled', True))
        if 'bbFormat' in self.overrideSettings:
            self.bbFormat = self.overrideSettings['bbFormat']
        if 'aaQuality' in self.overrideSettings:
            self.aaQuality = self.overrideSettings['aaQuality']
        self.reflectionSetting = currentSettings['reflections']
        self.aoSetting = currentSettings['ao']
        self.volumetricQuality = currentSettings['volumetricQuality']

    def OverrideSettings(self, key, value):
        self.overrideSettings[key] = value

    def StopOverrideSettings(self, key):
        try:
            del self.overrideSettings[key]
        except KeyError:
            pass

    def _CreateRenderTargets(self):
        if not self.prepared:
            return
        displayWidth, displayHeight = self.GetDisplaySize()
        if _singletons.device.SupportsRenderTargetFormat(trinity.PIXEL_FORMAT.R11G11B10_FLOAT):
            customFormat = trinity.PIXEL_FORMAT.R11G11B10_FLOAT
        else:
            customFormat = trinity.PIXEL_FORMAT.R16G16B16A16_FLOAT
        dsFormatAL = trinity.DEPTH_STENCIL_FORMAT.D32F
        self.PrepareUpscaling(displayWidth, displayHeight, customFormat, dsFormatAL)
        width, height = self.GetRenderSize()
        self.customBackBuffer = rtm.GetRenderTargetAL(width, height, 1, customFormat)
        if self.customBackBuffer is not None:
            self.customBackBuffer.name = 'sceneRenderJobSpace.customBackBuffer'
        if self.usePostProcessing and (self.aaQuality >= gfxsettings.AA_QUALITY_TAA_MEDIUM or _singletons.device.upscalingTechnique != trinity.UPSCALING_TECHNIQUE.NONE):
            self.customOpaqueBackBuffer = rtm.GetRenderTargetAL(width, height, 1, customFormat, index=314)
            self.customOpaqueBackBuffer.name = 'sceneRenderJobSpace.customOpaqueBackBuffer'
        else:
            self.customOpaqueBackBuffer = None
        self.customDepthStencil = rtm.GetDepthStencilAL(width, height, dsFormatAL, 1)
        blitFormat = customFormat
        if self._TargetDiffers(self.blitTexture, 'trinity.Tr2RenderTarget', blitFormat, width, height):
            self.blitTexture = rtm.GetRenderTargetAL(width, height, 1, blitFormat, index=1)
            if self.blitTexture is not None:
                self.blitTexture.name = 'sceneRenderJobSpace.blitTexture'
        if self.aoSetting == gfxsettings.GFX_AO_QUALITY_OFF and self.shadowQuality < 3 or trinity.GetShaderModel() == 'SM_3_0_LO':
            needNormalMap = False
        else:
            needNormalMap = True
        if needNormalMap:
            if self._TargetDiffers(self.normalTexture, 'trinity.Tr2RenderTarget', trinity.PIXEL_FORMAT.R10G10B10A2_UNORM, width, height):
                self.normalTexture = rtm.GetRenderTargetAL(width, height, 1, trinity.PIXEL_FORMAT.R10G10B10A2_UNORM, 1)
                if self.normalTexture:
                    self.normalTexture.name = 'sceneRenderJobSpace.normalTexture'
        else:
            self.normalTexture = None
        self._SetNormalMap()
        if self.distortionEffectsEnabled:
            index = 2
            if self._TargetDiffers(self.distortionTexture, 'trinity.Tr2RenderTarget', trinity.PIXEL_FORMAT.B8G8R8A8_UNORM, width, height):
                self.distortionTexture = rtm.GetRenderTargetAL(width, height, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM, index)
                if self.distortionTexture:
                    self.distortionTexture.name = 'sceneRenderJobSpace.distortionTexture'
            self._SetDistortionMap()
        else:
            self.distortionTexture = None
            self._SetDistortionMap()

    def IsAAEnabled(self):
        return self.aaQuality is not gfxsettings.AA_QUALITY_DISABLED

    def _TargetDiffers(self, target, blueType, format, width = 0, height = 0):
        if target is None:
            return True
        if blueType != target.__bluetype__:
            return True
        if format != target.format:
            return True
        if width != 0 and target.width != width:
            return True
        if height != 0 and target.height != height:
            return True
        return False

    def EnableDistortionEffects(self, enable):
        self.distortionEffectsEnabled = enable

    def DoPrepareResources(self):
        if not self.enabled:
            return
        try:
            gfxsettings.Set(gfxsettings.GFX_UPSCALING_TECHNIQUE, _singletons.device.upscalingTechnique)
            gfxsettings.Set(gfxsettings.GFX_UPSCALING_SETTING, _singletons.device.upscalingSetting)
            gfxsettings.Set(gfxsettings.GFX_FRAMEGENERATION_ENABLED, _singletons.device.frameGeneration)
        except gfxsettings.UninitializedSettingsGroupError:
            pass

        self.prepared = True
        self.SetSettingsBasedOnPerformancePreferences()

    def _SetSettingsBasedOnPerformancePreferences(self):
        if self.cascadedShadowMap is None:
            self.cascadedShadowMap = trinity.Tr2ShadowMap()

    def EnablePostProcessing(self, enable):
        self._enablePostProcessing = enable
        self.SetSettingsBasedOnPerformancePreferences()

    def SetSettingsBasedOnPerformancePreferences(self):
        if not self.enabled:
            return
        self.ApplyBaseSettings()
        self._SetSettingsBasedOnPerformancePreferences()
        self.usePostProcessing = self.postProcessingQuality > 0 or _singletons.device.upscalingTechnique != _singletons._trinity.UPSCALING_TECHNIQUE.NONE
        if self.distortionEffectsEnabled:
            self.distortionJob.AddPostProcess('Distortion', 'res:/fisfx/postprocess/distortion.red')
            self.backgroundDistortionJob.AddPostProcess('Distortion', 'res:/fisfx/postprocess/distortion.red')
        self._CreateRenderTargets()
        self._RefreshRenderTargets()
        self.ModifyPostProcessForPerformance()
        self.ApplyPerformancePreferencesToScene()

    def ModifyPostProcessForPerformance(self):
        if not self.enabled:
            return
        step = self.GetStep('FINAL_BLIT')
        if step is None:
            return
        if self.scene and self.scene.object.visualizeMethod == 0:
            step.quality = self.postProcessingQuality
        else:
            step.quality = 0

    def ApplyPerformancePreferencesToScene(self):
        self._SetShadowSetting()
        self._SetDepthMap()
        self._SetNormalMap()
        self._SetDistortionMap()
        self._SetSecondaryLighting()
        trinity.settings.SetValue('eveSpaceSceneDynamicLighting', trinity.GetShaderModel().endswith('DEPTH'))
        scene = self.GetScene()
        if scene is None:
            return
        self.SetSSAOBasedOnSettings()
        self.ApplyVolumetricQuality()
        if self.useImpostors:
            scene.impostorManager = trinity.Tr2ImpostorManager()
        if self.gpuParticlesEnabled:
            if not scene.gpuParticleSystem:
                scene.gpuParticleSystem = blue.resMan.LoadObject('res:/fisfx/gpuparticles/system.red')
        else:
            scene.gpuParticleSystem = None
        self.SetReflectionBasedOnSettings()

    def SetReflectionBasedOnSettings(self):
        scene = self.GetScene()
        if self.reflectionSetting != gfxsettings.GFX_REFLECTION_QUALITY_OFF:
            scene.reflectionProbe = trinity.Tr2ReflectionProbe()
            if self.reflectionSetting == gfxsettings.GFX_REFLECTION_QUALITY_ULTRA:
                scene.reflectionProbe.renderFrequency = trinity.ReflectionProbeRenderFrequency.AllSidesPerFrame
            else:
                scene.reflectionProbe.renderFrequency = trinity.ReflectionProbeRenderFrequency.OneSidePerFrame
            self.EnableStep('RENDER_REFLECTIONS')
        else:
            scene.reflectionProbe = None
            self.DisableStep('RENDER_REFLECTIONS')
        trinity.settings.SetValue('eveReflectionSetting', self.reflectionSetting)
        if hasattr(scene, 'ReregisterEntities'):
            scene.ReregisterEntities()

    def SetSSAOBasedOnSettings(self):
        scene = self.GetScene()
        forceDisable = not CanSupportSsao()
        if forceDisable or self.aoSetting == gfxsettings.GFX_AO_QUALITY_OFF or trinity.GetShaderModel() == 'SM_3_0_LO':
            scene.SSAO.enabled = False
        else:
            scene.SSAO.enabled = True
            if self.aoSetting == gfxsettings.GFX_AO_QUALITY_LOW:
                scene.SSAO.quality = trinity.SSAOQuality.Lowest
                scene.SSAO.downsampled = True
            elif self.aoSetting == gfxsettings.GFX_AO_QUALITY_MEDIUM:
                scene.SSAO.quality = trinity.SSAOQuality.Medium
                scene.SSAO.downsampled = False
            else:
                scene.SSAO.quality = trinity.SSAOQuality.Highest
                scene.SSAO.downsampled = False

    def ApplyVolumetricQuality(self):
        scene = self.GetScene()
        if scene:
            scene.volumetricsRenderer.blur = True
            scene.volumetricsRenderer.quality = self.volumetricQuality
            if self.volumetricQuality == gfxsettings.GFX_VOLUMETRIC_QUALITY_ULTRA:
                trinity.GetTextureLodManager().useLowResVtaFiles = False
                scene.volumetricsRenderer.scaleFactor = 1.0
                scene.volumetricsRenderer.castShadows = True
                scene.volumetricsRenderer.receiveShadows = True
            elif self.volumetricQuality == gfxsettings.GFX_VOLUMETRIC_QUALITY_HIGH:
                trinity.GetTextureLodManager().useLowResVtaFiles = False
                scene.volumetricsRenderer.scaleFactor = 0.7
                scene.volumetricsRenderer.castShadows = True
                scene.volumetricsRenderer.receiveShadows = False
            elif self.volumetricQuality == gfxsettings.GFX_VOLUMETRIC_QUALITY_MEDIUM:
                trinity.GetTextureLodManager().useLowResVtaFiles = True
                scene.volumetricsRenderer.scaleFactor = 0.5
                scene.volumetricsRenderer.castShadows = False
                scene.volumetricsRenderer.receiveShadows = False
            else:
                trinity.GetTextureLodManager().useLowResVtaFiles = True
                scene.volumetricsRenderer.scaleFactor = 0.3
                scene.volumetricsRenderer.castShadows = False
                scene.volumetricsRenderer.receiveShadows = False

    def UpdateFinalBlitStep(self):
        oldStep = self.GetStep('FINAL_BLIT')
        if oldStep is not None and isinstance(oldStep, trinity.TriStepRenderPostProcess):
            newStep = trinity.TriStepRenderPostProcess(oldStep.scene, oldStep.renderTarget, self.customOpaqueBackBuffer)
            self.AddStep('FINAL_BLIT', newStep)

    def _RefreshRenderTargets(self):
        self.RemoveStep('SET_DEPTH')
        if self.GetSwapChain() is not None:
            self.AddStep('SET_SWAPCHAIN_RT', trinity.TriStepPushRenderTarget(self.GetSwapChain().backBuffer))
            self.AddStep('RESET_SWAPCHAIN_RT', trinity.TriStepPopRenderTarget())
            self.AddStep('SET_SWAPCHAIN_DEPTH', trinity.TriStepPushDepthStencil(self.GetSwapChain().depthStencilBuffer))
            self.AddStep('RESET_SWAPCHAIN_DEPTH', trinity.TriStepPopDepthStencil())
        else:
            self.RemoveStep('SET_SWAPCHAIN_RT')
            self.RemoveStep('RESET_SWAPCHAIN_RT')
            self.RemoveStep('SET_SWAPCHAIN_DEPTH')
            self.RemoveStep('RESET_SWAPCHAIN_DEPTH')
        if self.customBackBuffer is not None:
            self.AddStep('SET_CUSTOM_RT', trinity.TriStepPushRenderTarget(self.customBackBuffer))
            self.AddStep('SET_FINAL_RT', trinity.TriStepPopRenderTarget())
        else:
            self.RemoveStep('SET_CUSTOM_RT')
            self.RemoveStep('SET_FINAL_RT')
        self.UpdateTAAEffect()
        self.AddStep('FINAL_BLIT', trinity.TriStepRenderPostProcess(self.GetScene(), self._GetSourceRTForPostProcessing(), self.customOpaqueBackBuffer))
        self.AddStep('SET_DEPTH', trinity.TriStepPushDepthStencil(self.customDepthStencil))
        self.AddStep('RESTORE_DEPTH', trinity.TriStepPopDepthStencil())
        self._SetDepthMap()
        self._SetNormalMap()
        self.AddStep('SET_VAR_DEPTH', trinity.TriStepSetVariableStore('DepthMap', self.customDepthStencil))
        self._RefreshPostProcessingJob(self.distortionJob, self.distortionEffectsEnabled and self.prepared)
        self._RefreshPostProcessingJob(self.backgroundDistortionJob, self.distortionEffectsEnabled and self.prepared)
        if self.distortionTexture is not None:
            self.AddStep('DO_DISTORTIONS', trinity.TriStepPredicated('hasForegroundDistortionBatches', self.GetScene(), trinity.TriStepRunJob(self.distortionJob)))
            distortionTriTextureRes = trinity.TriTextureRes()
            distortionTriTextureRes.SetFromRenderTarget(self.distortionTexture)
            self.distortionJob.SetPostProcessVariable('Distortion', 'TexDistortion', distortionTriTextureRes)
            self.backgroundDistortionJob.SetPostProcessVariable('Distortion', 'TexDistortion', distortionTriTextureRes)
        else:
            self.RemoveStep('DO_DISTORTIONS')
        self._CreateDepthPass()

    def EnableSceneUpdate(self, isEnabled):
        if self.updateJob:
            if isEnabled:
                if len(self.updateJob.steps) == 0:
                    self._CreateUpdateSteps()
                else:
                    self._SetUpdateStep(trinity.TriStepUpdate(self.GetScene()), 'UPDATE_SCENE')
            elif len(self.updateJob.steps) > 0:
                del self.updateJob.steps[0]
        elif isEnabled:
            self.AddStep('UPDATE_SCENE', trinity.TriStepUpdate(self.GetScene()))
        else:
            self.RemoveStep('UPDATE_SCENE')

    def EnableUnRenderedSceneUpdate(self, isEnabled):
        if not self.updateJob:
            return
        if len(self.updateJob.steps) == 0:
            self._CreateUpdateSteps()
        updateStep = self.updateJob.steps.FindByName('UPDATE_SCENE')
        updateStep.object = self.GetScene()
        updateStep.enabled = isEnabled

    def DisableShadows(self):
        scene = self.GetScene()
        if scene is not None:
            scene.cascadedShadowMap = None
            self.cascadedShadowMap = None
            scene.raytracingManager = None
            self.rtManager = None

    def DisableRaytracedShadows(self):
        scene = self.GetScene()
        if scene is not None:
            scene.raytracingManager = None
            self.rtManager = None

    def DisableCascadedShadows(self):
        scene = self.GetScene()
        if scene is not None:
            scene.cascadedShadowMap = None
            self.cascadedShadowMap = None
