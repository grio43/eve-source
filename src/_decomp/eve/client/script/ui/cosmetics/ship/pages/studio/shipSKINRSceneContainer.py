#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\shipSKINRSceneContainer.py
import logging
import blue
import geo2
import trinity
import uthread
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.uianimations import animations
from cosmetics.client.ships.skins.live_data import current_skin_design_signals, current_skin_design
from cosmetics.common.ships.skins.static_data.component_category import ComponentCategory
from cosmetics.common.ships.skins.static_data.pattern_attribute import PatternAttribute
from cosmetics.common.ships.skins.static_data.slot_name import SlotID, PATTERN_SLOT_IDS, PATTERN_SLOT_ID_BY_PATTERN_MATERIAL_ID
from eve.client.script.environment.sofService import GetSofService
from eve.client.script.environment.spaceObject.cosmeticsManager import CosmeticsManager
from eve.client.script.environment.spaceObject.spaceObject import modify_dna
from eve.client.script.ui.camera.skinrShipSceneContainerCamera import SkinrShipSceneContainerCamera
from eve.client.script.ui.control.scenecontainer import SceneContainer
from eve.client.script.ui.cosmetics.ship.const import ANIM_DURATION_LONG, ANIM_DURATION_EXTRA_LONG
from eve.client.script.ui.cosmetics.ship.pages.studio.patternProjectorGizmo import PatternProjectorGizmo
from eve.client.script.ui.cosmetics.ship.pages.studio.studioUtil import is_green_screen_enabled
from evegraphics import utils as gfxutils
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from cosmetics.client.ships.qa.settings import visualize_shape_ellipsoid
log = logging.getLogger(__name__)
TRANSITION_ZOOM_DEFAULT = 0.5
ZOOM_RANGE = [1.6, 3.6]
SCENE_GRAPHICID = 26811
SHIP_MATERIALIZATION_MULTIEFFECT_GRAPHICID = 27581
SKINR_ENVIRONMENT_VFX_GRAPHICID = 27580

class ShipSKINRSceneContainer(SceneContainer):
    _model_dna = None
    _type_id = None

    def __init__(self, **kwargs):
        log.info('SKIN PREVIEW - PaintPreviewSceneContainer: Start constructing')
        super(ShipSKINRSceneContainer, self).__init__(**kwargs)
        self.pattern_projector_gizmo = PatternProjectorGizmo()
        self.environment = None
        self.shipReplacementMultiEffect = None
        self._lastSwapTriggerTimeStamp = 0.0
        self.model = None
        self.oldModel = None
        self._current_skin_design = None
        self._load_ship_thread = None
        self.PrepareSpaceScene()
        if self.camera:
            self.camera.farClip = 1000000
            self.camera.nearClip = 10
        self.cosmetics_manager = CosmeticsManager()
        log.info('SKIN PREVIEW - PaintPreviewSceneContainer: Finish constructing')
        self.connect_signals()

    def Close(self):
        super(ShipSKINRSceneContainer, self).Close()
        self.disconnect_signals()

    def connect_signals(self):
        current_skin_design_signals.on_component_attribute_changed.connect(self.on_current_design_component_attribute_changed)
        current_skin_design_signals.on_pattern_blend_mode_changed.connect(self.on_pattern_blend_mode_changed)
        current_skin_design_signals.on_slot_fitting_changed.connect(self.on_slot_fitting_changed)
        visualize_shape_ellipsoid.on_change.connect(self.on_visualize_shape_ellipsoid)

    def disconnect_signals(self):
        current_skin_design_signals.on_component_attribute_changed.disconnect(self.on_current_design_component_attribute_changed)
        current_skin_design_signals.on_pattern_blend_mode_changed.disconnect(self.on_pattern_blend_mode_changed)
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.on_slot_fitting_changed)

    def on_visualize_shape_ellipsoid(self, value):
        if value is True:
            childEffect = trinity.Load('res:/fisfx/utils/ShieldEllipsoidTester.red')
            r = self.model.shapeEllipsoidRadius
            childEffect.scaling = (r[0] * 2.0, r[1] * 2.0, r[2] * 2.0)
            childEffect.translation = self.model.shapeEllipsoidCenter
            self.model.effectChildren.append(childEffect)
        elif len(self.model.effectChildren) > 0:
            self.model.effectChildren.pop()

    def on_slot_fitting_changed(self, slot_id, component_instance):
        if component_instance:
            data = component_instance.get_component_data()
            if data:
                self._play_apply_sound(data.category)
        self.cosmetics_manager.apply_component(slot_id, component_instance)

    def _play_apply_sound(self, category):
        if category == ComponentCategory.MATERIAL:
            PlaySound('nanocoating_button_select_color_play')
        elif category == ComponentCategory.METALLIC:
            PlaySound('nanocoating_button_push_detailing_play')
        elif category == ComponentCategory.PATTERN:
            PlaySound('nanocoating_button_select_pattern_play')

    def on_pattern_blend_mode_changed(self, value):
        self.cosmetics_manager.SetBlendMode(self.model, value)

    def on_current_design_component_attribute_changed(self, slot_id, attribute_id, value):
        if slot_id not in PATTERN_SLOT_IDS:
            return
        if attribute_id == PatternAttribute.MIRROR:
            self.cosmetics_manager.SetMirroredState(slot_id, value)
        elif attribute_id == PatternAttribute.PROJECT_TO_AREA_1:
            self.cosmetics_manager.SetTargetMaterialArea(slot_id, SlotID.PRIMARY_NANOCOATING, value)
        elif attribute_id == PatternAttribute.PROJECT_TO_AREA_2:
            self.cosmetics_manager.SetTargetMaterialArea(slot_id, SlotID.SECONDARY_NANOCOATING, value)
        elif attribute_id == PatternAttribute.PROJECT_TO_AREA_3:
            self.cosmetics_manager.SetTargetMaterialArea(slot_id, SlotID.TERTIARY_NANOCOATING, value)
        elif attribute_id == PatternAttribute.PROJECT_TO_AREA_4:
            self.cosmetics_manager.SetTargetMaterialArea(slot_id, SlotID.TECH_AREA, value)
        elif attribute_id == PatternAttribute.SCALE:
            self.cosmetics_manager.ApplyScaling(slot_id, value)
        elif attribute_id == PatternAttribute.ROTATION:
            self.cosmetics_manager.ApplyRotation(slot_id, value)
        elif attribute_id == PatternAttribute.POSITION:
            self.cosmetics_manager.ApplyTranslation(slot_id, value)

    def PrepareCamera(self):
        self.camera = SkinrShipSceneContainerCamera()
        self.camera.OnActivated()

    def turn_camera(self, yaw, pitch, duration):
        self.camera.StopUpdateThreads()
        self.camera.StopAnimations()
        animations.MorphScalar(self.camera, 'yaw', self.camera.yaw, yaw, duration=duration)
        animations.MorphScalar(self.camera, 'pitch', self.camera.pitch, pitch, duration=duration)

    def rotate_ship_in(self, duration):
        q1 = geo2.QuaternionRotationSetYawPitchRoll(-0.1, -0.05, 0.0)
        q2 = geo2.QuaternionRotationSetYawPitchRoll(0.0, 0.0, 0.0)
        animations.MorphQuaternion(self.model.rotationCurve, 'value', q1, q2, duration)

    def SetPattern(self, pattern_id):
        self.cosmetics_manager.SetProjectionTexture(pattern_id)

    def GetCurrentShip(self):
        return self.model

    def GetCurrentCamera(self):
        return self.camera

    def PrepareSpaceScene(self, scenePath = None):
        log.info('SKIN PREVIEW - PaintPreviewSceneContainer: PrepareSpaceScene started')
        if scenePath is None:
            scenePath = GetGraphicFile(SCENE_GRAPHICID)
        super(ShipSKINRSceneContainer, self).PrepareSpaceScene(scenePath=scenePath)
        log.info('SKIN PREVIEW - PaintPreviewSceneContainer: PrepareSpaceScene prepared base scene')
        if not self.scene:
            return
        if not self.scene.postprocess:
            self.scene.postprocess = trinity.Tr2PostProcess2()
        log.info('SKIN PREVIEW - PaintPreviewSceneContainer: PrepareSpaceScene added postprocess')
        if not is_green_screen_enabled():
            environmentResourcePath = GetGraphicFile(SKINR_ENVIRONMENT_VFX_GRAPHICID)
            self.environment = blue.resMan.LoadObject(environmentResourcePath)
            if self.environment is not None:
                self.AddToScene(self.environment, clear=0)
            self.environment.StartControllers()
        else:
            self.renderJob.GetStep('CLEAR').color = (0, 1, 0, 0)
        log.info('SKIN PREVIEW - PaintPreviewSceneContainer: PrepareSpaceScene added environment')
        multiEffectResourcePath = GetGraphicFile(SHIP_MATERIALIZATION_MULTIEFFECT_GRAPHICID)
        sme = blue.resMan.LoadObject(multiEffectResourcePath)
        self.shipReplacementMultiEffect = sme
        if self.shipReplacementMultiEffect is not None:
            self.AddToScene(self.shipReplacementMultiEffect, clear=0)
            if self.environment is not None:
                self.shipReplacementMultiEffect.SetParameter('skinrEnv', self.environment)
            self.shipReplacementMultiEffect.SetControllerVariable('object_materialize', 0.0)
            self.shipReplacementMultiEffect.StartControllers()
        log.info('SKIN PREVIEW - PaintPreviewSceneContainer: PrepareSpaceScene added ship replacement multieffect')
        if self.pattern_projector_gizmo is not None and self.scene:
            self.pattern_projector_gizmo.load_and_place_in_scene(self.scene)
        log.info('SKIN PREVIEW - PaintPreviewSceneContainer: PrepareSpaceScene finished')

    def preview_type(self, type_id, skinDesign = None, animate = True):
        log.info('SKIN PREVIEW - Preview: commanded preview for type: {type_id}'.format(type_id=type_id))
        model_dna = modify_dna(base_dna=gfxutils.BuildSOFDNAFromTypeID(type_id), patternMat1='green_lime_emissive', patternName='cosm_blank_projection')
        type_changed = type_id != self._type_id
        self._type_id = type_id
        self._model_dna = model_dna
        if skinDesign:
            self._current_skin_design = skinDesign
        if animate or type_changed:
            self._animate_model_swap()
        else:
            trinity.WaitForResourceLoads()
            self.cosmetics_manager.apply_design(self._current_skin_design)

    def _animate_model_swap(self):
        if self._load_ship_thread:
            self._lastSwapTriggerTimeStamp = blue.os.GetSimTime()
        else:
            PlaySound('nanocoating_ship_paint2_play')
            if self.shipReplacementMultiEffect is not None:
                self.shipReplacementMultiEffect.SetControllerVariable('object_materialize', 0.0)
            log.info('SKIN PREVIEW - Preview: queued delayed load')
            self._load_ship_thread = uthread.new(self._load_ship_async)

    def _load_ship_async(self):
        try:
            self._lastSwapTriggerTimeStamp = blue.os.GetSimTime()
            SECOND = 10000000.0
            timeUntilReveal = SECOND * ANIM_DURATION_LONG
            while self._lastSwapTriggerTimeStamp + timeUntilReveal > blue.os.GetSimTime():
                uthread2.Sleep(0.15)

        finally:
            if self.destroyed:
                return
            self._load_ship()
            trinity.WaitForResourceLoads()
            self._swap_out_old_ship()
            self._load_ship_thread = None
            log.info('SKIN PREVIEW - Preview: delayed load removed from queue')

    def _load_ship(self):
        log.info('SKIN PREVIEW - Preview: load started for type {type_id}'.format(type_id=self._type_id))
        if self.destroyed:
            return
        space_object_factory = GetSofService().spaceObjectFactory
        self.model = space_object_factory.BuildFromDNA(self._model_dna)
        self.model.rotationCurve = trinity.Tr2RotationAdapter()
        self.cosmetics_manager.SetTypeID(self._type_id)
        self.cosmetics_manager.SetModel(self.model)
        self.cosmetics_manager.apply_design(self._current_skin_design)
        self.model.SetControllerVariable('boosterOn', 1.0)
        log.info('SKIN PREVIEW - Preview: model set for type {type_id}'.format(type_id=self._type_id))
        while len(self.model.observers) > 0:
            self.model.observers.pop()

        self.model.FreezeHighDetailMesh()
        if hasattr(self.model, 'dirtLevel'):
            self.model.dirtLevel = -1.5
        log.info('SKIN PREVIEW - Preview: load finished for type {type_id}'.format(type_id=self._type_id))

    def _swap_out_old_ship(self):
        log.info('SKIN PREVIEW - SwapOutOldShip: started')
        if self.destroyed:
            return
        if self.oldModel is not None and self.oldModel in self.scene.objects:
            self.scene.objects.remove(self.oldModel)
        log.info('SKIN PREVIEW - SwapOutOldShip: Old Model removed')
        if self.scene and self.model is not None:
            self.scene.objects.append(self.model)
        log.info('SKIN PREVIEW - SwapOutOldShip: model added to scene')
        self._fit_model_in_view(self.model)
        log.info('SKIN PREVIEW - SwapOutOldShip: model fit in view')
        if self.shipReplacementMultiEffect is not None:
            self.shipReplacementMultiEffect.SetParameter('skinrAsset', self.model)
            self.shipReplacementMultiEffect.StartControllers()
            self.shipReplacementMultiEffect.SetControllerVariable('object_materialize', 1.0)
        log.info('SKIN PREVIEW - SwapOutOldShip: replacement multieffect applied')
        self.model.StartControllers()
        self.oldModel = self.model
        self.rotate_ship_in(ANIM_DURATION_EXTRA_LONG)
        log.info('SKIN PREVIEW - SwapOutOldShip: finished')

    def _fit_model_in_view(self, model):
        if model is None or not self.camera:
            return
        rad = model.GetBoundingSphereRadius()
        maxRenderDist = self.camera.farClip or 400000.0
        min_zoom = ZOOM_RANGE[0] * rad
        max_zoom = min(ZOOM_RANGE[1] * rad, maxRenderDist - 2 * rad)
        self.SetMinMaxZoom(min_zoom, max_zoom)
        self.SetZoom(TRANSITION_ZOOM_DEFAULT)
        self.camera.SetInnerBoundRadius(self.model.shapeEllipsoidRadius)
        self.camera.SetModelCenter(self.model.shapeEllipsoidCenter)
