#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\iconGenerator.py
import trinity
import blue
import os
import telemetry
from iconrendering2.renderers.utils_scene import GetViewAndProjectionUsingBoundingSphere, GetViewAndProjectionUsingMeshGeometry
from pytelemetry.zoning import TelemetryContext
from trinity.sceneRenderJobSpaceJessica import CreateJessicaSpaceRenderJob
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from eve.client.script.environment.spaceObject.cosmeticsManager import CosmeticsManager
from liveIconCacheUtils import get_unique_filename
_LIGHT_RIG_GRAPHIC_ID = 27583

class IconGenerator(object):
    __guid__ = 'form.IconGenerator'
    __renderObject__ = trinity.Tr2Sprite2d

    def __init__(self, width = 256, height = 256, skin_design = None, bg_texture_path = None):
        self._scenePath = 'res:/dx9/scene/iconbackground/generic.red'
        self._scene = None
        self.object = None
        self.renderJob = None
        self.depth_stencil = None
        self.outline_resolve_step = None
        self.outline_effect_step = None
        self.width = width
        self.height = height
        self._bg_texture_path = bg_texture_path
        self.skin_design = skin_design
        self.cachedTexturePath = None
        self.light_rig = trinity.EveEffectRoot2()

    def __del__(self):
        self.renderJob = None
        self._scene = None
        self.depth_stencil = None
        self.object = None
        self.light_rig = None
        self.outline_resolve_step = None
        self.outline_effect_step = None

    def save_texture_to_disk(self, skin_design, bg_texture_path):
        fileName = get_unique_filename(skin_design, bg_texture_path)
        p = fileName.encode('ascii', 'ignore')
        hostBitmap = trinity.Tr2HostBitmap(self.renderJob.renderTarget)
        trinity.WaitForResourceLoads()
        hostBitmap.Save(p)
        blue.pyos.BeNice()
        return p

    def create_bg_sprite(self):
        sprite = trinity.Tr2Sprite2d()
        sprite.texturePrimary = trinity.Tr2Sprite2dTexture()
        sprite.displayHeight = 1
        sprite.displayWidth = 1
        sprite.displayX = 0
        sprite.displayY = 0
        return sprite

    def AddLightRig(self):
        ligth_rig_resource_path = GetGraphicFile(_LIGHT_RIG_GRAPHIC_ID)
        light_rig = trinity.Load(ligth_rig_resource_path)
        if light_rig:
            self.light_rig.effectChildren.append(light_rig)

    def AdjustLightRig(self, boundingSphereRadius, boundingSphereCenter):
        lightRigContainer = self.light_rig.effectChildren.FindByName('ShipLights_Scaler')
        if not lightRigContainer:
            return
        lightRigContainer.scaling = (boundingSphereRadius, boundingSphereRadius, boundingSphereRadius)
        lightRigContainer.translation = (lightRigContainer.translation[0], boundingSphereCenter[1], lightRigContainer.translation[2])

    def _GetRenderStepPosition(rj, name):
        for i, each in enumerate(rj.steps):
            if each.name == name:
                return i

        return -1

    def create_outline_step(self):
        current_blit = trinity.Tr2RenderTarget(self.width, self.height, 1, trinity.PIXEL_FORMAT.B8G8R8X8_UNORM)
        self.outline_resolve_step = trinity.TriStepResolve()
        self.outline_resolve_step.name = 'Copy RT'
        self.outline_resolve_step.destination = current_blit
        effect = trinity.Tr2Effect()
        effect.effectFilePath = 'res:/graphics/effect/managed/space/system/outline.fx'
        effect.resources.append(trinity.Tr2RuntimeTextureParameter('BlitSource', current_blit))
        self.outline_effect_step = trinity.TriStepRenderEffect()
        self.outline_effect_step.effect = effect
        self.outline_effect_step.name = 'Outline'
        pos = IconGenerator._GetRenderStepPosition(self.renderJob, 'FINAL_BLIT')
        self.renderJob.steps.insert(pos + 1, self.outline_effect_step)
        pos = IconGenerator._GetRenderStepPosition(self.renderJob, 'FINAL_BLIT')
        self.renderJob.steps.insert(pos + 1, self.outline_resolve_step)

    @telemetry.ZONE_METHOD
    def construct_render_job(self):
        try:
            self._shaderModel = trinity.GetShaderModel()
            self._scene = blue.resMan.LoadObject(self._scenePath)
            if self._scene is None:
                return
            blue.pyos.BeNice()
            self._scene.backgroundRenderingEnabled = False
            self._scene.sunDiffuseColorWithDynamicLights = (0.2, 0.2, 0.2, 0.2)
            self._scene.sunDiffuseColor = (0.7, 0.7, 0.7, 0.7)
            self.AddLightRig()
            self.depth_stencil = trinity.Tr2DepthStencil(self.width, self.height, trinity.DEPTH_STENCIL_FORMAT.D24S8)
            vp = trinity.TriViewport()
            vp.width = self.width
            vp.height = self.height
            self.renderJob = CreateJessicaSpaceRenderJob()
            self.renderJob.updateJob = None
            self.renderJob.CreateBasicRenderSteps()
            settings = self.renderJob.GetSettings()
            settings['aaQuality'] = 0
            self.renderJob.SetSettings(settings)
            self.renderJob.SetViewport(vp)
            bgStep = trinity.TriStepRenderScene()
            bgStep.name = 'BACKGROUND_SPRITE'
            bg_sprite = self.create_bg_sprite()
            bgSpriteScene = trinity.Tr2Sprite2dScene()
            bgSpriteScene.children.append(bg_sprite)
            bgStep.scene = bgSpriteScene
            pos = IconGenerator._GetRenderStepPosition(self.renderJob, 'CLEAR')
            self.renderJob.steps.insert(pos + 1, bgStep)
            setattr(self.renderJob, 'backgroundTexture', bg_sprite.texturePrimary)
            self._scene.reflectionProbe = None
            self._scene.postprocess = None
            self._scene.useSunDiffuseColorWithDynamicLights = True
            self.renderJob.SetScene(self._scene)
            self.renderJob.SetSettingsBasedOnPerformancePreferences()
            self.create_outline_step()
            for step_name in ['RENDER_REFLECTIONS',
             'DO_BACKGROUND_DISTORTIONS',
             'SET_UI_PROJECTION',
             'SET_UI_VIEW',
             'RENDER_3D_UI']:
                self.renderJob.RemoveStep(step_name)

            blue.resMan.Wait()
            self.renderJob.RemoveStep('FPS_COUNTER')
        finally:
            trinity.renderJobs.UnscheduleByName('FPS')

    def set_skin_design(self, skin_design):
        self.skin_design = skin_design
        self.construct_space_object(skin_design)

    def construct_space_object(self, skin_design):
        dna_string = CosmeticsManager.CreateSOFDNAfromSkinState(skin_design, skin_design.ship_type_id)
        space_object = sm.GetService('sofService').spaceObjectFactory.BuildFromDNA(dna_string)
        trinity.WaitForResourceLoads()
        CosmeticsManager.UpdatePatternProjectionParametersFromSkinState(skin_design, space_object, typeID=skin_design.ship_type_id)
        blend_mode = skin_design.slot_layout.pattern_blend_mode
        if blend_mode is not None:
            CosmeticsManager.SetBlendMode(space_object, blendMode=blend_mode)
        self.space_object = space_object
        self.set_object(self.space_object)

    def attach_render_target(self, render_target):
        self.renderJob.OverrideBuffers(render_target, self.depth_stencil)
        self.renderJob.renderTarget = render_target
        self.renderJob.Enable(False)
        self.outline_resolve_step.source = render_target

    @telemetry.ZONE_METHOD
    def set_object(self, object):
        if self.object:
            self._scene.objects.fremove(self.object)
        self.object = object
        if not object:
            return
        with TelemetryContext('initializing'):
            self._initialize_object()
        with TelemetryContext('view projection'):
            aspectRatio = float(self.width) / float(self.height)
            center = self.object.boundingSphereCenter
            radius = self.object.boundingSphereRadius
            translation = trinity.Tr2CurveConstant()
            translation.value = (0,
             -0.1 * radius,
             0,
             0)
            self.object.modelTranslationCurve = translation
            view, projection = GetViewAndProjectionUsingMeshGeometry(self.object.mesh.geometry, scene=self._scene, boundingSphereRadius=radius, boundingSphereCenter=center, aspectRatio=aspectRatio)
        with TelemetryContext('set camera'):
            if self.renderJob is not None:
                self.renderJob.SetActiveCamera(view=view, projection=projection)
        with TelemetryContext('obj things'):
            if self._scene is not None:
                self._scene.objects.removeAt(-1)
                self._scene.objects.append(self.light_rig)
                self._scene.objects.append(self.object)
        self.AdjustLightRig(object.boundingSphereRadius, object.boundingSphereCenter)
        trinity.WaitForResourceLoads()
        if self._scene is not None:
            self._scene.UpdateScene(blue.os.GetTime())

    def _construct_render_target(self, width, height):
        self.render_target = trinity.Tr2RenderTarget(width, height, 1, trinity.PIXEL_FORMAT.B8G8R8X8_UNORM)

    @telemetry.ZONE_METHOD
    def render_icon(self, skin_design, bg_texture_path, render_glow = True):
        self.bg_texture_path = bg_texture_path
        self._construct_render_target(self.width, self.height)
        if self.renderJob is None:
            return
        self.attach_render_target(self.render_target)
        self.outline_resolve_step.enabled = self.outline_effect_step.enabled = render_glow
        self.renderJob.ScheduleOnce()
        self.renderJob.ScheduleOnce()
        self.renderJob.WaitForFinish()
        blue.synchro.Yield()
        p = self.save_texture_to_disk(skin_design, bg_texture_path)
        return p

    @telemetry.ZONE_METHOD
    def _initialize_object(self):
        perlinCurves = self.object.Find('trinity.TriPerlinCurve')
        for curve in perlinCurves:
            curve.scale = 0.0

        if hasattr(self.object, 'modelRotationCurve'):
            self.object.modelRotationCurve = None
        if hasattr(self.object, 'modelTranslationCurve'):
            self.object.modelTranslationCurve = None
        if hasattr(self.object, 'rotationCurve'):
            self.object.rotationCurve = None
        if hasattr(self.object, 'translationCurve'):
            self.object.translationCurve = None
        if hasattr(self.object, 'boosters'):
            self.object.boosters = None
        if self._scene is not None:
            self._scene.gpuParticleSystem = trinity.Tr2GpuParticleSystem()

    @property
    def bg_texture_path(self):
        return self._bg_texture_path

    @bg_texture_path.setter
    def bg_texture_path(self, value):
        self._bg_texture_path = value
        if self.renderJob:
            self.renderJob.backgroundTexture.resPath = value
