#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinity\sceneRenderJobSpaceEmbedded.py
import logging
from . import _trinity as trinity
from .sceneRenderJobSpace import SceneRenderJobSpace
from .renderJob import CreateRenderJob
logger = logging.getLogger(__name__)

def CreateEmbeddedRenderJobSpace(name = None, usePostProcessing = True, additiveBlending = False):
    newRJ = SceneRenderJobSpaceEmbedded()
    if name is not None:
        newRJ.ManualInit(name)
    else:
        newRJ.ManualInit()
    newRJ.embeddedPostprocessing = usePostProcessing
    newRJ.additiveBlending = additiveBlending
    return newRJ


class SceneRenderJobSpaceEmbedded(SceneRenderJobSpace):
    renderStepOrder = ['PUSH_RENDER_TARGET', 'PUSH_DEPTH_STENCIL']
    renderStepOrder += SceneRenderJobSpace.renderStepOrder
    renderStepOrder += ['POP_RENDER_TARGET',
     'POP_DEPTH_STENCIL',
     'COPY_TO_BLIT_TEXTURE',
     'PUSH_POSTPROCESSING_RENDER_TARGET',
     'RJ_POSTPROCESSING_EMBEDDED',
     'POP_POSTPROCESSING_RENDER_TARGET',
     'PUSH_BLIT_DEPTH',
     'SET_BLIT_VIEWPORT',
     'SET_BLENDMODE',
     'FINAL_BLIT_EMBEDDED',
     'POP_BLIT_DEPTH']

    def _ManualInit(self, name):
        self.stencilBlitEffect = None
        self.stencilPath = ''
        self.SetupStencilBlitEffect()
        self.isOffscreen = False
        self.doFinalBlit = True
        self.offscreenRenderTarget = None
        self.finalTexture = None
        self.rtWidth = 0
        self.rtHeight = 0
        self.blitViewport = trinity.TriViewport()
        SceneRenderJobSpace._ManualInit(self, name)
        self.updateJob = None
        self.useImpostors = False
        self.useReflectionProbe = False
        self.embeddedPostprocessing = True
        self.additiveBlending = False
        self.useUpscaling = False

    def SetupStencilBlitEffect(self):
        self.stencilBlitEffect = trinity.Tr2Effect()
        self.stencilBlitEffect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/system/BlitStencil.fx'
        stencilMap = trinity.TriTextureParameter()
        stencilMap.name = 'StencilMap'
        stencilMap.resourcePath = self.stencilPath
        self.stencilBlitEffect.resources.append(stencilMap)
        self.blitMapParameter = trinity.TriTextureParameter()
        self.blitMapParameter.name = 'BlitSource'
        self.stencilBlitEffect.resources.append(self.blitMapParameter)

    def SetOffscreen(self, isOffscreen):
        self.isOffscreen = isOffscreen

    def SetStencil(self, path = None):
        self.stencilPath = path
        self.SetupStencilBlitEffect()
        self.EnableStep('CLEAR')
        self._CreateRenderTargets()
        self._RefreshRenderTargets()

    def _DoPrepareResources(self):
        self.prepared = True
        self.SetSettingsBasedOnPerformancePreferences()

    def ScheduleUpdateJob(self):
        if self.updateJob is None:
            self.updateJob = CreateRenderJob('embedded_Update')
            self.updateJob.scheduled = False
        super(SceneRenderJobSpaceEmbedded, self).ScheduleUpdateJob()

    def DoReleaseResources(self, level):
        self.finalTexture = None
        self.offscreenRenderTarget = None
        self.blitMapParameter.SetResource(None)
        SceneRenderJobSpace.DoReleaseResources(self, level)

    def DoPrepareResources(self):
        if not self.enabled:
            return
        self._DoPrepareResources()

    def PrepareUpscaling(self, displayWidth, displayHeight, backbufferFormat, depthStencilFormat):
        if self._UsePostProcessingEmbedded() and self.useUpscaling:
            super(SceneRenderJobSpaceEmbedded, self).PrepareUpscaling(displayWidth, displayHeight, backbufferFormat, depthStencilFormat, allowFramegen=False)
        else:
            self.AddStep('SET_UPSCALING_CONTEXT_ID', trinity.TriStepSetUpscalingContextID())
            self.DeleteUpscalingContext()

    def _GetSourceRTForPostProcessing(self):
        if self.hdrEnabled:
            return self.customBackBuffer
        return self.finalTexture

    def _CreateRenderTargets(self):
        if not self.prepared:
            return
        SceneRenderJobSpace._CreateRenderTargets(self)
        width, height = self.GetRenderSize()
        self.rtWidth = width
        self.rtHeight = height
        finalWidth, finalHeight = self.GetDisplaySize()
        if self.customBackBuffer is None:
            self.offscreenRenderTarget = trinity.Tr2RenderTarget(finalWidth, finalHeight, 1, self.bbFormat)
            self.finalTexture = self.offscreenRenderTarget
        else:
            self.finalTexture = trinity.Tr2RenderTarget(finalWidth, finalHeight, 1, self.customBackBuffer.format)
        self.finalTexture.name = 'finalTexture'

    def _UsePostProcessingEmbedded(self):
        return self.usePostProcessing and self.embeddedPostprocessing

    def _RefreshRenderTargets(self):
        if self._UsePostProcessingEmbedded() and self._GetSourceRTForPostProcessing() is None:
            return
        SceneRenderJobSpace._RefreshRenderTargets(self)
        self.RemoveStep('PUSH_RENDER_TARGET')
        self.RemoveStep('PUSH_DEPTH_STENCIL')
        self.RemoveStep('POP_RENDER_TARGET')
        self.RemoveStep('POP_DEPTH_STENCIL')
        self.RemoveStep('SET_BLIT_VIEWPORT')
        self.RemoveStep('COPY_TO_BLIT_TEXTURE')
        self.RemoveStep('FINAL_BLIT_EMBEDDED')
        self.RemoveStep('PUSH_BLIT_DEPTH')
        self.RemoveStep('POP_BLIT_DEPTH')
        self.RemoveStep('PUSH_POSTPROCESSING_RENDER_TARGET')
        self.RemoveStep('RJ_POSTPROCESSING_EMBEDDED')
        self.RemoveStep('POP_POSTPROCESSING_RENDER_TARGET')
        viewport = self.GetViewport()
        if viewport is not None:
            vpStep = self.GetStep('SET_VIEWPORT')
            if vpStep is not None:
                bracketViewportStep = trinity.TriStepSetViewport()
                fullViewport = trinity.TriViewport(0, 0, viewport.width, viewport.height)
                bracketViewportStep.viewport = fullViewport
                self.AddStep('SET_BRACKET_VIEWPORT', bracketViewportStep)
                renderWidth, renderHeight = self.GetRenderSize()
                upscaledViewport = trinity.TriViewport(0, 0, renderWidth, renderHeight)
                vpStep.viewport = upscaledViewport
        if self.offscreenRenderTarget:
            self.AddStep('PUSH_RENDER_TARGET', trinity.TriStepPushRenderTarget(self.offscreenRenderTarget))
            self.AddStep('POP_RENDER_TARGET', trinity.TriStepPopRenderTarget())
        self.AddStep('PUSH_BLIT_DEPTH', trinity.TriStepPushDepthStencil(None))
        self.RemoveStep('FINAL_BLIT')
        if self._UsePostProcessingEmbedded():
            self.AddStep('RJ_POSTPROCESSING_EMBEDDED', trinity.TriStepRenderPostProcess(self.GetScene(), self._GetSourceRTForPostProcessing(), self.customOpaqueBackBuffer))
            if self.finalTexture:
                self.AddStep('PUSH_POSTPROCESSING_RENDER_TARGET', trinity.TriStepPushRenderTarget(self.finalTexture))
                self.AddStep('POP_POSTPROCESSING_RENDER_TARGET', trinity.TriStepPopRenderTarget())
        elif self.customBackBuffer is not None and self.finalTexture is not None:
            step = trinity.TriStepResolve(self.finalTexture, self.customBackBuffer)
            step.name = 'Resolve: finalTexture <== customBackBuffer'
            self.AddStep('COPY_TO_BLIT_TEXTURE', step)
        if self.doFinalBlit:
            self.AddStep('SET_BLIT_VIEWPORT', trinity.TriStepSetViewport(viewport))
            if self.finalTexture:
                if self.additiveBlending:
                    step = trinity.TriStepSetStdRndStates()
                    step.renderingMode = trinity.RM_ALPHA_ADDITIVE
                    self.AddStep('SET_BLENDMODE', step)
                if self.stencilPath is None or self.stencilPath == '':
                    self.AddStep('FINAL_BLIT_EMBEDDED', trinity.TriStepRenderTexture(self.finalTexture))
                else:
                    self.blitMapParameter.SetResource(self.finalTexture)
                    self.AddStep('FINAL_BLIT_EMBEDDED', trinity.TriStepRenderEffect(self.stencilBlitEffect))
        self.AddStep('POP_BLIT_DEPTH', trinity.TriStepPopDepthStencil())

    def GetDisplaySize(self):
        vp = self.GetViewport()
        if vp is None:
            return (None, None)
        return (vp.width, vp.height)

    def DoFinalBlit(self, enabled):
        self.doFinalBlit = enabled

    def UpdateViewport(self, viewport):
        if viewport.width != self.rtWidth or viewport.height != self.rtHeight:
            self._CreateRenderTargets()
            self._RefreshRenderTargets()

    def ApplyBaseSettings(self):
        SceneRenderJobSpace.ApplyBaseSettings(self)
        self.gpuParticlesEnabled = False
