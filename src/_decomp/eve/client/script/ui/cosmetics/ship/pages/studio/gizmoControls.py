#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\gizmoControls.py
import carbonui
import eveicon
import geo2
import math
import uthread2
from carbonui import Align
from carbonui.button.menu import MenuButtonIcon
from carbonui.control.checkbox import Checkbox
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import GetWindowAbove
from cosmetics.client.ships.qa.settings import scene_debug_mode_setting
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from cosmetics.common.ships.skins.static_data.pattern_attribute import PatternAttribute
from cosmetics.common.ships.skins.static_data.slot_name import PATTERN_SLOT_IDS, PATTERN_SLOT_ID_BY_PATTERN_MATERIAL_ID
from eve.client.script.ui import eveColor
from eve.client.script.ui.camera.skinrShipSceneContainerCamera import ROLL_SNAP_STEP
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.control.toggleButtonGroupButton import ToggleButtonGroupButton
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSettings
from eve.client.script.ui.cosmetics.ship.pages.studio.studioSettings import pattern_rotation_follow_camera_setting
from localization import GetByLabel
DEFAULT_TOP_DOWN_VIEW = (0.999, 0.999)
DEFAULT_FRONTAL_VIEW = (1.0, 0.0)
DEFAULT_SIDE_RIGHT_VIEW = (0.5, 0.0)

class GizmoControls(ContainerAutoSize):
    default_width = 522
    default_alignMode = Align.TOTOP
    BUTTON_ID_OFFSET = 1
    BUTTON_ID_ORBITAL = 2
    BUTTON_ID_ROTATE_SCALE = 3

    def __init__(self, *args, **kwargs):
        super(GizmoControls, self).__init__(*args, **kwargs)
        self._radius = 0.0
        self.construct_layout()
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(GizmoControls, self).Close()

    def connect_signals(self):
        current_skin_design_signals.on_component_attribute_changed.connect(self.on_component_attribute_changed)
        current_skin_design_signals.on_slot_fitting_changed.connect(self.on_slot_fitting_changed)
        current_skin_design_signals.on_slot_selected.connect(self.on_slot_selected)
        current_skin_design_signals.on_existing_design_loaded.connect(self.on_existing_design_loaded)

    def disconnect_signals(self):
        current_skin_design_signals.on_component_attribute_changed.disconnect(self.on_component_attribute_changed)
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.on_slot_fitting_changed)
        current_skin_design_signals.on_slot_selected.disconnect(self.on_slot_selected)
        current_skin_design_signals.on_existing_design_loaded.disconnect(self.on_existing_design_loaded)

    def on_existing_design_loaded(self, *args):
        self.update_values()

    def on_slot_selected(self, slot_id):
        self.update_visibility()

    def on_slot_fitting_changed(self, slot_id, component_instance):
        self.update_visibility()

    def update_visibility(self):
        if current_skin_design.get_selected_pattern_component_instance():
            self.display = True
            self.update_values()
        else:
            self.display = False

    def update_values(self):
        self.offset_u_slider_cont.update_value()
        self.offset_v_slider_cont.update_value()
        self.yaw_slider_cont.update_value()
        self.pitch_slider_cont.update_value()
        self.scale_slider_cont.update_value()
        self.roll_slider_cont.update_value()

    def construct_layout(self):
        self.construct_top_container()
        self.construct_planar_controls()
        self.construct_camera()
        self.construct_buttons_and_panels()
        self._debug_label = carbonui.TextHeadline(parent=self, align=Align.TOTOP, display=scene_debug_mode_setting.is_enabled())
        self._debug_label_thread = None
        self._update_scene_debug_thread()
        scene_debug_mode_setting.on_change.connect(self.on_scene_debug_mode_setting)

    def _update_scene_debug_thread(self):
        if scene_debug_mode_setting.is_enabled():
            self._debug_label.display = True
            self._debug_label_thread = uthread2.start_tasklet(self._update_debug_label_thread)
        else:
            self._debug_label.display = False
            if self._debug_label_thread:
                self._debug_label_thread.kill()
            self._debug_label_thread = None

    def on_scene_debug_mode_setting(self, value):
        self._update_scene_debug_thread()

    def _update_debug_label_thread(self):
        while not self.destroyed:
            uthread2.Sleep(0.1)
            slot_id = current_skin_design.get_selected_slot_id()
            if slot_id not in PATTERN_SLOT_IDS:
                continue
            component_instance = current_skin_design.get().get_fitted_component_instance(slot_id)
            if component_instance:
                yaw, pitch, roll = geo2.QuaternionRotationGetYawPitchRoll(component_instance.rotation)
                text = 'Yaw={:.2f}, Pitch={:.2f} Roll={:.2f}\nPosition={:.2f}, {:.2f}, {:.2f}'.format(math.degrees(yaw), math.degrees(pitch), math.degrees(roll), *component_instance.position)
            else:
                text = ''
            self._debug_label.text = text

    def construct_top_container(self):
        self.top_container = Container(name='top_container', parent=self, align=Align.TOTOP, height=32)

    def construct_planar_controls(self):
        planar_container = Container(name='planar_container', parent=self.top_container, align=Align.TORIGHT, width=24, padLeft=8)
        MenuButtonIcon(name='planar_menu', parent=planar_container, align=Align.CENTER, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/Pages/Studio/gizmo/pattern_projection.png', iconSize=24, hint=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/ProjectionPresets'), get_menu_func=self.get_planar_menu, pos=(0, 0, 24, 24))

    def get_planar_menu(self):
        menu = MenuData()
        menu.AddEntry(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/PatternProjectionTop'), texturePath='res:/UI/Texture/classes/Cosmetics/Ship/Pages/Studio/gizmo/pattern_projection_top_down.png', func=self.on_planar_mode_top_button)
        menu.AddEntry(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/PatternProjectionFront'), texturePath='res:/UI/Texture/classes/Cosmetics/Ship/Pages/Studio/gizmo/pattern_projection_front_side.png', func=self.on_planar_mode_front_button)
        menu.AddEntry(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/PatternProjectionRight'), texturePath='res:/UI/Texture/classes/Cosmetics/Ship/Pages/Studio/gizmo/pattern_projection_right_side.png', func=self.on_planar_mode_right_button)
        return menu

    def on_planar_mode_top_button(self, *args):
        self._reset_pattern_yaw_pitch(*DEFAULT_TOP_DOWN_VIEW)

    def on_planar_mode_front_button(self, *args):
        self._reset_pattern_yaw_pitch(*DEFAULT_FRONTAL_VIEW)

    def on_planar_mode_right_button(self, *args):
        self._reset_pattern_yaw_pitch(*DEFAULT_SIDE_RIGHT_VIEW)

    def _reset_pattern_yaw_pitch(self, yaw, pitch):
        selected_slot_id = current_skin_design.get_selected_slot_id()
        pattern_slot_id = PATTERN_SLOT_ID_BY_PATTERN_MATERIAL_ID.get(selected_slot_id, selected_slot_id)
        component_instance = current_skin_design.get().get_fitted_component_instance(pattern_slot_id)
        if component_instance:
            component_instance.yaw = yaw
            component_instance.pitch = pitch
        if studioSettings.pattern_rotation_follow_camera_setting.is_enabled():
            studioSettings.pattern_rotation_follow_camera_setting.disable()
        else:
            current_skin_design.add_to_undo_history()

    def construct_camera(self):
        self.camera_container = ContainerAutoSize(name='camera_container', parent=self.top_container, align=Align.TORIGHT, height=32, padLeft=8)
        self.camera_checkbox = Checkbox(name='camera_checkbox', parent=self.camera_container, align=Align.TORIGHT, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/CameraToggle'), hint=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/CameraToggleHint'), setting=pattern_rotation_follow_camera_setting, padTop=4)

    def construct_buttons_and_panels(self):
        self.button_container = Container(name='button_container', parent=self.top_container, align=Align.TOTOP, height=32)
        self.button_group = ToggleButtonGroup(name='button_group', parent=self.button_container, align=Align.TOTOP)
        self.panel_container = ContainerAutoSize(name='panel_container', parent=self, padTop=4, align=Align.TOTOP)
        self.construct_orbit_panel()
        self.construct_offset_panel()
        self.construct_rotate_scale_panel()
        self.button_group.AddButton(btnID=self.BUTTON_ID_ORBITAL, label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/OrbitalPanelButton'), panel=self.orbital_panel, btnClass=OrbitButton)
        self.button_group.AddButton(btnID=self.BUTTON_ID_OFFSET, label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/OffsetPanelButton'), panel=self.offset_panel, btnClass=OffsetButton)
        self.button_group.AddButton(btnID=self.BUTTON_ID_ROTATE_SCALE, label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/RotateScalePanelButton'), panel=self.rotate_scale_panel, btnClass=RotateAndScaleButton)
        self.button_group.SetSelected(self.BUTTON_ID_ORBITAL)

    def construct_offset_panel(self):
        self.offset_panel = ContainerAutoSize(name='offset_panel', parent=self.panel_container, display=False, align=Align.TOTOP)
        self.offset_u_slider_cont = PatternAttributeSliderContainerOffsetU(parent=self.offset_panel, pattern_attribute_id=PatternAttribute.OFFSET_U_RATIO, icon_texture=eveicon.caret_left_right)
        self.offset_v_slider_cont = PatternAttributeSliderContainerOffsetV(parent=self.offset_panel, pattern_attribute_id=PatternAttribute.OFFSET_V_RATIO, icon_texture=eveicon.caret_up_down)

    def construct_orbit_panel(self):
        self.orbital_panel = ContainerAutoSize(name='orbital_panel', parent=self.panel_container, display=False, align=Align.TOTOP)
        self.yaw_slider_cont = PatternAttributeSliderContainerYaw(parent=self.orbital_panel, pattern_attribute_id=PatternAttribute.YAW_RATIO, icon_texture=eveicon.arrow_rotate_left)
        self.pitch_slider_cont = PatternAttributeSliderContainerPitch(parent=self.orbital_panel, pattern_attribute_id=PatternAttribute.PITCH_RATIO, icon_texture=eveicon.arrow_rotate_right)

    def construct_rotate_scale_panel(self):
        self.rotate_scale_panel = ContainerAutoSize(name='rotate_scale_panel', parent=self.panel_container, display=False, align=Align.TOTOP)
        self.roll_slider_cont = PatternAttributeSliderContainerRoll(name='roll_slider', parent=self.rotate_scale_panel, pattern_attribute_id=PatternAttribute.ROTATION, icon_texture=eveicon.orbit)
        self.scale_slider_cont = PatternAttributeSliderContainerScaling(name='scale_slider', parent=self.rotate_scale_panel, pattern_attribute_id=PatternAttribute.SCALE, icon_texture=eveicon.expand)

    def on_component_attribute_changed(self, slot_id, attribute_id, value):
        current_pattern_slot = PATTERN_SLOT_ID_BY_PATTERN_MATERIAL_ID.get(current_skin_design.get_selected_slot_id(), slot_id)
        if slot_id not in PATTERN_SLOT_IDS or slot_id != current_pattern_slot:
            return
        if attribute_id in (PatternAttribute.YAW_RATIO, PatternAttribute.PITCH_RATIO):
            if self.button_group.GetValue() is not self.BUTTON_ID_ORBITAL:
                self.button_group.SetSelected(self.BUTTON_ID_ORBITAL, animate=False)
        elif attribute_id in (PatternAttribute.OFFSET_U_RATIO, PatternAttribute.OFFSET_V_RATIO):
            if self.button_group.GetValue() is not self.BUTTON_ID_OFFSET:
                self.button_group.SetSelected(self.BUTTON_ID_OFFSET, animate=False)
        elif attribute_id in (PatternAttribute.ROLL_RATIO, PatternAttribute.SCALE):
            if self.button_group.GetValue() is not self.BUTTON_ID_ROTATE_SCALE:
                self.button_group.SetSelected(self.BUTTON_ID_ROTATE_SCALE, animate=False)

    def update_radial_position(self):
        wnd = GetWindowAbove(self)
        if not wnd:
            return
        width, _ = wnd.GetAbsoluteSize()
        offset = 48 if width < 1400 else 0
        self.top = 64 + offset

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
        self.update_radial_position()


class BasePatternAttributeSliderContainer(Container):
    default_height = 32
    default_align = Align.TOTOP
    min_value = -1.0
    max_value = 1.0
    decimal_places = 2

    def __init__(self, pattern_attribute_id, icon_texture, *args, **kwargs):
        super(BasePatternAttributeSliderContainer, self).__init__(*args, **kwargs)
        self.pattern_attribute_id = pattern_attribute_id
        self.icon_texture = icon_texture
        self.construct_layout()
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(BasePatternAttributeSliderContainer, self).Close()

    def construct_layout(self):
        self.icon_container = Container(name='icon_container', parent=self, align=Align.TOLEFT, width=16, padRight=8)
        self.icon = Sprite(name='icon', parent=self.icon_container, align=Align.CENTER, texturePath=self.icon_texture, width=16, height=16, color=eveColor.SILVER_GREY)
        self.value_edit = SingleLineEditFloat(name='value_edit', parent=self, align=Align.TORIGHT, width=80, padding=(4, 2, 0, 2), minValue=self.value_to_readable_value(self.min_value), maxValue=self.value_to_readable_value(self.max_value), OnChange=self.on_value_edit_changed, OnFocusLost=self.on_value_edit_focus_lost, OnReturn=self.on_value_edit_return, decimalPlaces=self.decimal_places)
        self.slider = Slider(name='slider', parent=self, getHintFunc=self.get_slider_hint, on_dragging=self.on_slider_value_changed, callback=self.on_slider_callback, barHeight=6, handleSize=28, align=Align.VERTICALLY_CENTERED, minValue=self.min_value, maxValue=self.max_value)

    def on_slider_callback(self, *args):
        self._apply_value_to_component_instance(self.slider.value)
        current_skin_design.add_to_undo_history()

    def on_value_edit_focus_lost(self, *args):
        self._update_slider_and_edit_value()
        current_skin_design.add_to_undo_history()

    def on_value_edit_return(self, *args):
        component_instance = current_skin_design.get_selected_pattern_component_instance()
        if component_instance:
            value = self.get_component_instance_value(component_instance)
            readable_value = self.value_to_readable_value(value)
            self.value_edit.SetValue(readable_value, docallback=False)
            current_skin_design.add_to_undo_history()

    def connect_signals(self):
        current_skin_design_signals.on_component_attribute_changed.connect(self.on_component_attribute_changed)

    def disconnect_signals(self):
        current_skin_design_signals.on_component_attribute_changed.disconnect(self.on_component_attribute_changed)

    def on_component_attribute_changed(self, slot_id, attribute_id, value):
        if self.pattern_attribute_id == attribute_id:
            self._update_slider_and_edit_value()

    def update_value(self):
        self._update_slider_and_edit_value()

    def on_slider_value_changed(self, slider):
        self._apply_value_to_component_instance(self.slider.value)

    def on_value_edit_changed(self, *args):
        self._apply_value_to_component_instance(self.readable_value_to_value(self.value_edit.GetValue()))

    def _apply_value_to_component_instance(self, value):
        component_instance = current_skin_design.get_selected_pattern_component_instance()
        if component_instance:
            self.set_component_instance_value(component_instance, value)

    def _update_slider_and_edit_value(self):
        component_instance = current_skin_design.get_selected_pattern_component_instance()
        if component_instance:
            value = self.get_component_instance_value(component_instance)
            self.slider.SetValue(value)
            readable_value = self.value_to_readable_value(value)
            if uicore.registry.GetFocus() != self.value_edit:
                self.value_edit.SetValue(readable_value, docallback=False)

    def set_component_instance_value(self, component_instance, value):
        raise NotImplementedError

    def get_component_instance_value(self, component_instance):
        raise NotImplementedError

    def get_readable_value(self):
        component_instance = self.get_component_instance()
        if not component_instance:
            return 0.0
        return self.value_to_readable_value(self.get_component_instance_value(component_instance))

    def get_component_instance(self):
        return current_skin_design.get_selected_pattern_component_instance()

    def readable_value_to_value(self, readable_value):
        return readable_value

    def value_to_readable_value(self, value):
        return value

    def get_slider_hint(self):
        return str(self.get_readable_value())


class PatternAttributeSliderContainerScaling(BasePatternAttributeSliderContainer):
    min_value = 0.0

    def set_component_instance_value(self, component_instance, value):
        component_instance.scaling_ratio = value

    def get_component_instance_value(self, component_instance):
        return component_instance.scaling_ratio

    def get_slider_hint(self, *args):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/ScaleAmountHint', amount=self.get_readable_value())

    def value_to_readable_value(self, value):
        return 2.0 * value

    def readable_value_to_value(self, readable_value):
        return readable_value / 2.0


class PatternAttributeSliderContainerYaw(BasePatternAttributeSliderContainer):
    min_value = -0.999
    max_value = 0.999
    decimal_places = 1

    def set_component_instance_value(self, component_instance, value):
        component_instance.yaw = value

    def get_component_instance_value(self, component_instance):
        return component_instance.yaw

    def get_slider_hint(self, *args):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/HorizontalOrbitHint', amount=self.get_readable_value())

    def value_to_readable_value(self, value):
        value = value / (self.max_value - self.min_value) + 0.5
        return value * 360.0

    def readable_value_to_value(self, readable_value):
        value = readable_value / 360.0 - 0.5
        return value * (self.max_value - self.min_value)


class PatternAttributeSliderContainerPitch(BasePatternAttributeSliderContainer):
    min_value = -0.999
    max_value = 0.999
    decimal_places = 1

    def set_component_instance_value(self, component_instance, value):
        component_instance.pitch = value

    def get_component_instance_value(self, component_instance):
        return component_instance.pitch

    def value_to_readable_value(self, value):
        value /= self.max_value - self.min_value
        return value * 180.0

    def readable_value_to_value(self, readable_value):
        value = readable_value / 180.0
        return value * (self.max_value - self.min_value)

    def get_slider_hint(self, *args):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/VerticalOrbitHint', amount=self.get_readable_value())


class PatternAttributeSliderContainerRoll(BasePatternAttributeSliderContainer):
    decimal_places = 1

    def set_component_instance_value(self, component_instance, value):
        component_instance.roll = value

    def get_component_instance_value(self, component_instance):
        return component_instance.roll

    def get_slider_hint(self, *args):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/RotateAmountHint', amount=self.get_readable_value())

    def value_to_readable_value(self, value):
        return value * 180.0

    def readable_value_to_value(self, readable_value):
        return readable_value / 180.0


class PatternAttributeSliderContainerOffsetU(BasePatternAttributeSliderContainer):
    decimal_places = 1

    def set_component_instance_value(self, component_instance, value):
        component_instance.offset_u_ratio = value

    def get_component_instance_value(self, component_instance):
        return component_instance._offset_u_ratio

    def get_slider_hint(self, *args):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/HorizontalOffsetHint', amount=self.get_readable_value())

    def value_to_readable_value(self, value):
        return value * 100.0

    def readable_value_to_value(self, readable_value):
        return readable_value / 100.0


class PatternAttributeSliderContainerOffsetV(BasePatternAttributeSliderContainer):
    decimal_places = 1

    def set_component_instance_value(self, component_instance, value):
        component_instance.offset_v_ratio = value

    def get_component_instance_value(self, component_instance):
        return component_instance._offset_v_ratio

    def get_slider_hint(self, *args):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/VerticalOffsetHint', amount=self.get_readable_value())

    def value_to_readable_value(self, value):
        return value * 100.0

    def readable_value_to_value(self, readable_value):
        return readable_value / 100.0


class OrbitButton(ToggleButtonGroupButton):

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.columns = 2
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.AddLabelLarge(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/OrbitalPanelButton'))
        tooltipPanel.AddDivider()
        tooltipPanel.AddLabelShortcut(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/OrbitPatternProjector'), 'CTRL + Left Mouse')
        tooltipPanel.AddLabelShortcut(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/PrecisionMode'), '+ SHIFT')


class OffsetButton(ToggleButtonGroupButton):

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.columns = 2
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.AddLabelLarge(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/OffsetPanelButton'))
        tooltipPanel.AddDivider()
        tooltipPanel.AddLabelShortcut(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/OffsetPatternProjector'), 'CTRL + Right Mouse')
        tooltipPanel.AddLabelShortcut(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/PrecisionMode'), '+ SHIFT')


class RotateAndScaleButton(ToggleButtonGroupButton):

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.columns = 2
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.AddLabelLarge(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/RotateScalePanelButton'))
        tooltipPanel.AddDivider()
        tooltipPanel.AddLabelShortcut(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/RotatePatternProjector'), 'CTRL + Mouse Wheel')
        tooltipPanel.AddLabelShortcut(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/ScalePattern'), 'CTRL + Left Mouse + Right Mouse')
        tooltipPanel.AddLabelShortcut(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/RotatePatternSnap', angle=ROLL_SNAP_STEP), '+ ALT')
        tooltipPanel.AddLabelShortcut(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/PrecisionMode'), '+ SHIFT')
