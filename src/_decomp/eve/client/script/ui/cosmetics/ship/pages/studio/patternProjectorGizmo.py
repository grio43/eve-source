#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\patternProjectorGizmo.py
import math
import blue
import geo2
from cosmetics.client.ships.skins.live_data import current_skin_design_signals, current_skin_design
from cosmetics.common.ships.skins.static_data.pattern_attribute import PatternAttribute
from cosmetics.common.ships.skins.static_data.slot_name import SlotID, PATTERN_SLOT_IDS, PATTERN_SLOT_ID_BY_PATTERN_MATERIAL_ID, PATTERN_RELATED_SLOT_IDS
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.pages import current_page
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSettings, studioSignals, patternProjectionUtil

class PatternProjectorGizmo:

    def __init__(self):
        self.position = (0.0, 0.0, 0.0)
        self.rotation = (0.0, 0.0, 0.0, 1.0)
        self.scaling = (1.0, 1.0, 1.0)
        self.model = None
        self.origin_model = None
        self.lineBetweenRoot = None
        self.lineBetweenEffect = None
        self.scale = 1.0
        self._last_scale_value = 0.0

    def connect_signals(self):
        current_skin_design_signals.on_component_attribute_changed.connect(self.on_current_skin_design_component_attribute_changed)
        current_skin_design_signals.on_slot_selected.connect(self.on_slot_selected)
        current_skin_design_signals.on_slot_fitting_changed.connect(self.on_slot_fitting_changed)
        studioSignals.on_page_opened.connect(self.on_page_opened)

    def on_page_opened(self, page_id, page_args, last_page_id, animate = True):
        if page_id != SkinrPage.STUDIO_DESIGNER:
            self.disappear()

    def on_slot_fitting_changed(self, slot_id, component_instance):
        self.update_visibility()

    def on_slot_selected(self, slot_id):
        self.update_visibility()

    def update_visibility(self):
        slot_id = current_skin_design.get_selected_slot_id()
        if not slot_id or slot_id not in PATTERN_RELATED_SLOT_IDS:
            self.disappear()
        else:
            slot_id = PATTERN_SLOT_ID_BY_PATTERN_MATERIAL_ID.get(slot_id, slot_id)
            if current_skin_design.get().slot_layout.get_component(slot_id):
                self.update_placement(slot_id)
                self.appear()
            else:
                self.disappear()

    def load_and_place_in_scene(self, scene):
        self.model = blue.resMan.LoadObject('res:/dx9/scene/skinr/Gizmo/Skinr_Gizmo_Crosshair_01a.red')
        self.origin_model = blue.resMan.LoadObject('res:/dx9/scene/skinr/skinr_gizmo_pointer_01a.red')
        self.lineBetweenRoot = blue.resMan.LoadObject('res:/dx9/scene/skinr/Skinr_Gizmo_Offset_01a.red')
        self.connect_signals()
        if self.model is not None:
            scene.objects.append(self.model)
            self.model.StartControllers()
        if self.origin_model is not None:
            scene.objects.append(self.origin_model)
            self.origin_model.StartControllers()
        if self.lineBetweenRoot is not None:
            scene.objects.append(self.lineBetweenRoot)
            self.lineBetweenRoot.StartControllers()
            childContainer = self.lineBetweenRoot.effectChildren.FindByName('EveChildLineSet_Base')
            if childContainer is not None:
                subChildContainer = childContainer.objects.FindByName('scaler')
                if subChildContainer is not None:
                    lineSet = subChildContainer.objects.FindByName('EveChildLineSet_01')
                    if lineSet is not None and len(lineSet.lines) > 0:
                        self.lineBetweenEffect = lineSet.lines[0]
        self.disappear()

    def update_line_between(self, pos1 = (0.0, 0.0, 0.0), pos2 = (0.0, 0.0, 0.0)):
        if pos1 is not None and pos2 is not None:
            if self.lineBetweenEffect is not None:
                self.lineBetweenEffect.point1 = pos1
                self.lineBetweenEffect.point2 = pos2

    def update_placement(self, slot_id):
        c = current_skin_design.get().get_fitted_component_instance(slot_id)
        if not c:
            return
        scale = max(c.ellipsoid_radii)
        self.scale = scale / 1000.0
        self.model.scaling = (self.scale, self.scale, self.scale)
        self.origin_model.scaling = (self.scale, self.scale, self.scale)
        position, rotation, userTwist, totalOffsetNormalized = (c.position,
         c.rotation,
         c.roll,
         c.offset_u_ratio ** 2 + c.offset_v_ratio ** 2)
        totalAddedGizmoOffset = (-0.5 * scale, 0.0, 0.0)
        totalAddedGizmoOffset = geo2.QuaternionTransformVector(rotation, totalAddedGizmoOffset)
        projector_pos = patternProjectionUtil.get_projector_position(c.yaw, c.pitch, c.ellipsoid_center, c.ellipsoid_radii)
        projector_pos = geo2.Vec3Add(projector_pos, totalAddedGizmoOffset)
        position = geo2.Vec3Add(position, totalAddedGizmoOffset)
        self.origin_model.translation = projector_pos
        self.origin_model.rotation = rotation
        offset = (scale * 0.005, 0.0, 0.0)
        offset = geo2.QuaternionTransformVector(rotation, offset)
        twistQuaternion = geo2.QuaternionRotationSetYawPitchRoll(0.0, userTwist * math.pi, 0.0)
        self.model.translation = geo2.Vec3Add(position, offset)
        self.model.rotation = geo2.QuaternionMultiply(geo2.QuaternionInverse(twistQuaternion), rotation)
        self.model.SetControllerVariable('twistValue', float(userTwist))
        self.update_line_between(geo2.Vec3Add(projector_pos, offset), geo2.Vec3Add(position, offset))
        self.lineBetweenRoot.SetControllerVariable('offsetBrightness', totalOffsetNormalized)

    def on_current_skin_design_component_attribute_changed(self, slot_id, attribute_id, value):
        if slot_id in PATTERN_SLOT_IDS:
            self.play_attribute_change_animation(attribute_id, value)
            self.update_placement(slot_id)

    def play_attribute_change_animation(self, attribute_id, value):
        if attribute_id == PatternAttribute.YAW_RATIO:
            self.model.HandleControllerEvent('orbitHorizontal')
            self.origin_model.HandleControllerEvent('isMoving')
            self.lineBetweenRoot.HandleControllerEvent('isMoving')
        elif attribute_id == PatternAttribute.PITCH_RATIO:
            self.model.HandleControllerEvent('orbitVertical')
            self.origin_model.HandleControllerEvent('isMoving')
            self.lineBetweenRoot.HandleControllerEvent('isMoving')
        elif attribute_id == PatternAttribute.OFFSET_U_RATIO:
            self.model.HandleControllerEvent('offsetHorizontal')
            self.lineBetweenRoot.HandleControllerEvent('isMoving')
        elif attribute_id == PatternAttribute.OFFSET_V_RATIO:
            self.model.HandleControllerEvent('offsetVertical')
            self.lineBetweenRoot.HandleControllerEvent('isMoving')
        elif attribute_id == PatternAttribute.ROLL_RATIO:
            self.model.HandleControllerEvent('twisting')
        elif attribute_id == PatternAttribute.SCALE:
            if value[0] > self._last_scale_value:
                self.model.HandleControllerEvent('scaleUp')
            else:
                self.model.HandleControllerEvent('scaleDown')
            self._last_scale_value = value[0]

    def appear(self):
        if not self.model:
            return
        self.model.SetControllerVariable('crosshairVisible', 1.0)
        self.lineBetweenRoot.SetControllerVariable('offsetVisible', 1.0)
        self.origin_model.SetControllerVariable('pointerVisible', 1.0)

    def disappear(self):
        studioSettings.pattern_rotation_follow_camera_setting.disable()
        if not self.model:
            return
        self.model.SetControllerVariable('crosshairVisible', 0.0)
        self.lineBetweenRoot.SetControllerVariable('offsetVisible', 0.0)
        self.origin_model.SetControllerVariable('pointerVisible', 0.0)
