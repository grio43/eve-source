#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\patternSlots.py
import eveicon
from carbonui import Align, PickState
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.primitives.container import Container
from carbonui.services.setting import SessionSettingEnum
from carbonui.uianimations import animations
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from cosmetics.common.ships.skins.static_data.pattern_attribute import PatternAttribute
from cosmetics.common.ships.skins.static_data.pattern_blend_mode import PatternBlendMode, NO_SECONDARY_COLOR_BLEND_MODES
from cosmetics.common.ships.skins.static_data.slot import SlotsDataLoader
from cosmetics.common.ships.skins.static_data.slot_name import SlotID, PATTERN_RELATED_SLOT_IDS
from eve.client.script.ui.cosmetics.ship.pages.studio import studioUtil
from eve.client.script.ui.cosmetics.ship.pages.studio.areaToggleButtonMenuIcon import AreaToggleButtonMenuIcon
from eve.client.script.ui.cosmetics.ship.pages.studio.circularButtonIcon import CircularButtonIcon, CircularMenuButtonIcon
from eve.client.script.ui.cosmetics.ship.pages.studio.cosmeticSlot import PatternCosmeticSlot
from localization import GetByLabel
SLOT_LEFT = 100
SLOT_TOP = 66
MATERIAL_OFFSET = 64
SLOT_LEFT_TOP_BY_ID = {SlotID.SECONDARY_PATTERN: (-SLOT_LEFT, -SLOT_TOP),
 SlotID.SECONDARY_PATTERN_MATERIAL: (-SLOT_LEFT + MATERIAL_OFFSET, -SLOT_TOP - MATERIAL_OFFSET),
 SlotID.PATTERN: (-SLOT_LEFT, SLOT_TOP),
 SlotID.PATTERN_MATERIAL: (-SLOT_LEFT + MATERIAL_OFFSET, SLOT_TOP + MATERIAL_OFFSET)}

class PatternSlots(Container):
    default_width = 360
    default_height = 400

    def __init__(self, *args, **kwargs):
        super(PatternSlots, self).__init__(*args, **kwargs)
        self.slots_by_id = {}
        self.construct_layout()
        self.update()
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(PatternSlots, self).Close()

    def connect_signals(self):
        current_skin_design_signals.on_slot_fitting_changed.connect(self.on_slot_fitting_changed)
        current_skin_design_signals.on_slot_selected.connect(self.on_slot_selected)
        current_skin_design_signals.on_pattern_blend_mode_changed.connect(self.on_pattern_blend_mode_changed)
        current_skin_design_signals.on_component_attribute_changed.connect(self.on_component_attribute_changed)

    def disconnect_signals(self):
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.on_slot_fitting_changed)
        current_skin_design_signals.on_slot_selected.disconnect(self.on_slot_selected)
        current_skin_design_signals.on_pattern_blend_mode_changed.disconnect(self.on_pattern_blend_mode_changed)
        current_skin_design_signals.on_component_attribute_changed.disconnect(self.on_component_attribute_changed)

    def on_component_attribute_changed(self, slot_id, attribute_id, value):
        if attribute_id == PatternAttribute.MIRROR:
            self.update_mirror_toggle_buttons()

    def on_pattern_blend_mode_changed(self, blend_mode):
        self.update_slots()

    def construct_layout(self):
        self.construct_mirror_toggle_buttons()
        self.construct_area_toggle_buttons()
        self.reconstruct_slots()
        self.construct_switch_pattern_button()
        self.construct_blendmode_button()

    def construct_mirror_toggle_buttons(self):
        self.primary_mirror_toggle_button = MirrorToggleButtonIcon(parent=self, align=Align.CENTER, left=-161, top=88, display=False, pickState=PickState.ON)
        self.secondary_mirror_toggle_button = MirrorSecondaryToggleButtonIcon(parent=self, align=Align.CENTER, left=-161, top=-88, display=False, pickState=PickState.ON)

    def construct_area_toggle_buttons(self):
        self.primary_area_toggle_button = AreaToggleButtonMenuIcon(parent=self, align=Align.CENTER, left=-161, top=46, slot_id=SlotID.PATTERN, display=False, pickState=PickState.ON)
        self.secondary_area_toggle_button = AreaToggleButtonMenuIcon(parent=self, align=Align.CENTER, left=-161, top=-46, slot_id=SlotID.SECONDARY_PATTERN, display=False, pickState=PickState.ON)

    def reconstruct_slots(self):
        for slot in self.slots_by_id.values():
            slot.Close()

        self.slots_by_id.clear()
        for slot_id in current_skin_design.get().slot_layout.slots:
            if slot_id not in PATTERN_RELATED_SLOT_IDS:
                continue
            slot_data = SlotsDataLoader.get_slot_data(slot_id)
            is_pattern = slot_data.unique_id in (SlotID.PATTERN, SlotID.SECONDARY_PATTERN)
            self.slots_by_id[slot_data.unique_id] = PatternCosmeticSlot(name='slot_{name}'.format(name=slot_data.internal_name), parent=self, slot_data=slot_data, opacity=0.0, license_selector_align=Align.CENTERRIGHT if is_pattern else Align.CENTERLEFT)

    def construct_switch_pattern_button(self):
        self.switch_pattern_button = SwitchPatternButtonIcon(name='switch_pattern_button', parent=self, pickState=PickState.OFF, align=Align.CENTER, opacity=0.0, func=self.on_switch_pattern_button, left=-100)

    def construct_blendmode_button(self):
        self.blendmode_button = BlendModeButton(name='blendmode_button', parent=self, pickState=PickState.OFF, align=Align.CENTER, opacity=0.0, left=-50)

    def update(self):
        self.update_slots()
        self.update_blend_and_switch_buttons()
        self.update_primary_buttons()
        self.update_secondary_buttons()

    def update_primary_buttons(self):
        show_primary_buttons = self.has_primary_pattern and current_skin_design.get_selected_slot_id() in (SlotID.PATTERN, SlotID.PATTERN_MATERIAL)
        self.primary_mirror_toggle_button.display = show_primary_buttons
        self.primary_area_toggle_button.display = show_primary_buttons
        self.primary_area_toggle_button.update_selected()

    def update_secondary_buttons(self):
        show_secondary_buttons = self.has_secondary_pattern and current_skin_design.get_selected_slot_id() in (SlotID.SECONDARY_PATTERN, SlotID.SECONDARY_PATTERN_MATERIAL)
        self.secondary_mirror_toggle_button.display = show_secondary_buttons
        self.secondary_area_toggle_button.display = show_secondary_buttons
        self.secondary_area_toggle_button.update_selected()

    def update_slots(self):
        for slot_id, slot in self.slots_by_id.items():
            if self.should_display_slot(slot_id):
                slot.show()
                animations.MoveTo(obj=slot, startPos=(slot.left, slot.top), endPos=self.get_slot_left_top(slot_id), duration=0.25)
            else:
                slot.hide()

        self.update_mirror_toggle_buttons()

    def update_mirror_toggle_buttons(self):
        component_instance = current_skin_design.get().get_fitted_component_instance(SlotID.PATTERN)
        if component_instance:
            if component_instance.mirrored:
                self.primary_mirror_toggle_button.SetSelected()
            else:
                self.primary_mirror_toggle_button.SetDeselected()
        component_instance = current_skin_design.get().get_fitted_component_instance(SlotID.SECONDARY_PATTERN)
        if component_instance:
            if component_instance.mirrored:
                self.secondary_mirror_toggle_button.SetSelected()
            else:
                self.secondary_mirror_toggle_button.SetDeselected()

    def update_blend_and_switch_buttons(self):
        for button in (self.blendmode_button, self.switch_pattern_button):
            if self.has_two_patterns:
                button.pickState = PickState.ON
                button.Enable()
            else:
                button.pickState = PickState.OFF
                button.Disable()
            target_opacity = 1.0 if self.has_primary_pattern else 0.0
            animations.FadeTo(button, button.opacity, target_opacity, duration=0.25)

    def populate_from_design(self):
        for slot_id in self.slots_by_id.keys():
            component_instance = current_skin_design.get().slot_layout.fitted_slots.get(slot_id, None)
            self.slots_by_id[slot_id].on_slot_fitting_changed(slot_id, component_instance)

        self.update()

    def update_radial_position(self, radius):
        self.left, self.top = studioUtil.get_radial_position(radius, 0)

    def on_switch_pattern_button(self, *args):
        pass

    def on_slot_fitting_changed(self, slot_id, component_instance):
        self.update()
        self.blendmode_button.update_selected()

    def on_slot_selected(self, slot_id):
        self.update_primary_buttons()
        self.update_secondary_buttons()

    def get_slot_left_top(self, slot_id):
        if not self.has_primary_pattern:
            return (-50, 0)
        else:
            return SLOT_LEFT_TOP_BY_ID[slot_id]

    def should_display_slot(self, slot_id):
        if slot_id == SlotID.PATTERN:
            return True
        if slot_id == SlotID.SECONDARY_PATTERN_MATERIAL:
            if current_skin_design.get().slot_layout.pattern_blend_mode in NO_SECONDARY_COLOR_BLEND_MODES:
                return False
            else:
                return self.has_secondary_pattern
        else:
            return self.has_primary_pattern

    def is_slot_fitted(self, slot_id):
        return current_skin_design.get().get_fitted_component_instance(slot_id) is not None

    @property
    def has_primary_pattern(self):
        return self.is_slot_fitted(SlotID.PATTERN)

    @property
    def has_secondary_pattern(self):
        return self.is_slot_fitted(SlotID.SECONDARY_PATTERN)

    @property
    def has_two_patterns(self):
        return self.has_primary_pattern and self.has_secondary_pattern


class BlendModeButton(CircularMenuButtonIcon):
    default_texturePath = eveicon.blend_modes
    default_hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/BlendModes')

    def __init__(self, **kwargs):
        super(BlendModeButton, self).__init__(**kwargs)
        self.update_selected()

    def on_blend_mode_setting_changed(self, value):
        current_skin_design.get().slot_layout.pattern_blend_mode = value
        self.update_selected()
        current_skin_design.add_to_undo_history()

    def update_selected(self):
        if not self.enabled or current_skin_design.get().slot_layout.pattern_blend_mode == PatternBlendMode.OVERLAY:
            self.SetDeselected()
        else:
            self.SetSelected()

    def Enable(self):
        super(BlendModeButton, self).Enable()
        self.update_selected()

    def Disable(self):
        super(BlendModeButton, self).Disable()
        self.update_selected()

    def GetMenu(self):
        pattern_blend_mode_setting = SessionSettingEnum(current_skin_design.get().slot_layout.pattern_blend_mode)
        pattern_blend_mode_setting.on_change.connect(self.on_blend_mode_setting_changed)
        m = MenuData()
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/BlendMode/Normal'), PatternBlendMode.OVERLAY, pattern_blend_mode_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/BlendMode/Subtractive'), PatternBlendMode.SUBTRACT, pattern_blend_mode_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/BlendMode/Exclusion'), PatternBlendMode.EXCLUSION, pattern_blend_mode_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/BlendMode/Nested'), PatternBlendMode.NESTED, pattern_blend_mode_setting)
        m.AddRadioButton(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/BlendMode/NestedInverted'), PatternBlendMode.NESTED_INVERTED, pattern_blend_mode_setting)
        return m


class MirrorToggleButtonIcon(CircularButtonIcon):
    default_texturePath = eveicon.mirror
    default_hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/MirrorToggle')

    def _ExecuteFunction(self, *args):
        self.ToggleSelected()
        component_instance = current_skin_design.get().get_fitted_component_instance(SlotID.PATTERN)
        if component_instance:
            component_instance.mirrored = self.isSelected
            current_skin_design.add_to_undo_history()


class MirrorSecondaryToggleButtonIcon(CircularButtonIcon):
    default_texturePath = eveicon.mirror
    default_hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Gizmo/MirrorToggle')

    def _ExecuteFunction(self, *args):
        self.ToggleSelected()
        component_instance = current_skin_design.get().get_fitted_component_instance(SlotID.SECONDARY_PATTERN)
        if component_instance:
            component_instance.mirrored = self.isSelected
            current_skin_design.add_to_undo_history()


class SwitchPatternButtonIcon(CircularButtonIcon):
    default_texturePath = eveicon.switch
    default_hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Switch')

    def _ExecuteFunction(self, *args):
        current_skin_design.get().swap_slots(SlotID.PATTERN, SlotID.SECONDARY_PATTERN)
        current_skin_design.add_to_undo_history()
