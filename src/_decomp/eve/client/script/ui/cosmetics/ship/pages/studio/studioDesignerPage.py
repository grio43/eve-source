#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\studioDesignerPage.py
import eveicon
from carbonui import Align, uiconst, AxisAlignment, Density, ButtonVariant, PickState
from carbonui.button.const import HEIGHT_EXPANDED
from carbonui.button.group import ButtonGroup, ButtonSizeMode, OverflowAlign
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from cosmetics.client.shipSkinDesignSvc import get_ship_skin_design_svc
from cosmetics.client.shipSkinSequencingSvc import get_ship_skin_sequencing_svc
from cosmetics.client.ships.qa.settings import should_show_popup_if_skin_name_missing
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from cosmetics.common.ships.skins.static_data.slot import SlotsDataLoader
from cosmetics.common.ships.skins.static_data.slot_configuration import SlotConfigurationsDataLoader, is_skinnable_ship
from cosmetics.common.ships.skins.static_data.slot_name import SlotID, PATTERN_RELATED_SLOT_IDS
from eve.client.script.ui.cosmetics.ship.const import ANIM_DURATION_LONG
from eve.client.script.ui.cosmetics.ship.controls.characterInfo import DesignOwnerCharacterInfo
from eve.client.script.ui.cosmetics.ship.controls.costInfo import StudioCostInfo
from eve.client.script.ui.cosmetics.ship.controls.sequencingTime import SequencingTime
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
from eve.client.script.ui.cosmetics.ship.pages.studio.componentPanel import ComponentPanel
from eve.client.script.ui.cosmetics.ship.pages.studio.cosmeticSlot import CosmeticSlot
from eve.client.script.ui.cosmetics.ship.pages.studio.gizmoControls import GizmoControls
from eve.client.script.ui.cosmetics.ship.pages.studio.hullSelectionPanel import HullSelectionPanel
from eve.client.script.ui.cosmetics.ship.pages.studio.patternSlots import PatternSlots
from eve.client.script.ui.cosmetics.ship.pages.studio.radiallyAlignedMixin import RadiallyAlignedMixin
from eve.client.script.ui.cosmetics.ship.pages.studio.randomizeControls import RandomizeControls
from eve.client.script.ui.cosmetics.ship.pages.studio.saveSkinButton import SaveSkinButton, SaveAsSkinButton
from eve.client.script.ui.cosmetics.ship.pages.studio.skinDesignDragData import SkinDesignDragData
from eve.client.script.ui.cosmetics.ship.pages.studio.skinNameDialogue import SkinNameDialogue
from eve.client.script.ui.cosmetics.ship.pages.studio.studioUtil import get_circular_layout_radius
from eve.client.script.ui.shared.cloneGrade import ORIGIN_SHIP_SKINR
from eve.client.script.ui.shared.cloneGrade.omegaTooltipPanelCell import OmegaTooltipPanelCell
from characterskills.client import skill_signals
from itertoolsext.Enum import Enum
from localization import GetByLabel
from signals import Signal
PANEL_PAD_TOP = 160
PANEL_PAD_BOTTOM = 160

class StudioDesignerPage(Container):
    SLOT_ANGLE_GAP = 14
    SLOT_WINDOW_GAP = 40
    SLOT_ANGLES = {SlotID.PRIMARY_NANOCOATING: 180 + SLOT_ANGLE_GAP * 1.5,
     SlotID.SECONDARY_NANOCOATING: 180 + SLOT_ANGLE_GAP * 0.5,
     SlotID.TERTIARY_NANOCOATING: 180 - SLOT_ANGLE_GAP * 0.5,
     SlotID.TECH_AREA: 180 - SLOT_ANGLE_GAP * 1.5}

    def __init__(self, *args, **kwargs):
        super(StudioDesignerPage, self).__init__(*args, **kwargs)
        self.slots_by_id = {}
        self.panels_by_id = {}
        self.hull_selection_panel = None
        self.is_loaded = False
        self.on_create_btn = Signal('on_create_btn')

    def LoadPanel(self, animate = True):
        if not self.is_loaded:
            self.is_loaded = True
            self.construct_layout()
            self.connect_signals()
        self.populate_from_design()
        self.create_button.update()
        self.state = uiconst.UI_PICKCHILDREN
        animations.FadeTo(self, 0.0, 1.0, duration=0.6, timeOffset=ANIM_DURATION_LONG)
        self.deselect_all_cosmetic_slots()
        self.check_show_hull_selection_panel()
        self.update_circular_layout(*self.GetAbsoluteSize())

    def check_show_hull_selection_panel(self):
        active_ship_type_id = current_skin_design.get_active_ship_type_id()
        if not is_skinnable_ship(active_ship_type_id):
            self.show_hull_selection_panel()
        else:
            self.close_hull_selection_panel()

    def UnloadPanel(self, animate = True):
        self.Disable()
        animations.FadeTo(self, self.opacity, 0.0, duration=0.2, callback=self.Hide)

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(StudioDesignerPage, self).Close()

    def connect_signals(self):
        self.on_size_changed.connect(self.on_size_changed_signal)
        studioSignals.on_scene_zoom.connect(self.on_scene_zoom)
        current_skin_design_signals.on_slot_selected.connect(self.on_slot_selected)
        current_skin_design_signals.on_slot_fitting_changed.connect(self.on_slot_fitting_changed)
        current_skin_design_signals.on_design_reset.connect(self.on_design_reset)
        current_skin_design_signals.on_existing_design_loaded.connect(self.on_existing_design_loaded)
        current_skin_design_signals.on_ship_type_id_changed.connect(self.on_ship_type_id_changed)
        skill_signals.on_skill_levels_trained.connect(self.on_skill_levels_trained)

    def disconnect_signals(self):
        self.on_size_changed.disconnect(self.on_size_changed_signal)
        studioSignals.on_scene_zoom.disconnect(self.on_scene_zoom)
        current_skin_design_signals.on_slot_selected.disconnect(self.on_slot_selected)
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.on_slot_fitting_changed)
        current_skin_design_signals.on_design_reset.disconnect(self.on_design_reset)
        current_skin_design_signals.on_existing_design_loaded.disconnect(self.on_existing_design_loaded)
        current_skin_design_signals.on_ship_type_id_changed.disconnect(self.on_ship_type_id_changed)
        skill_signals.on_skill_levels_trained.disconnect(self.on_skill_levels_trained)

    def on_ship_type_id_changed(self, type_id):
        self.create_button.update()
        self.update_slots()

    def on_slot_fitting_changed(self, slot_id, component_instance):
        self.create_button.update()
        self.hide_all_slot_pulse_highlights()
        if slot_id == SlotID.PATTERN and component_instance is None:
            if current_skin_design.get_selected_slot_id() in (SlotID.PATTERN_MATERIAL, SlotID.SECONDARY_PATTERN, SlotID.SECONDARY_PATTERN_MATERIAL):
                current_skin_design.set_selected_slot_id(None)

    def hide_all_slot_pulse_highlights(self):
        for slot_id in self.slots_by_id.keys():
            slot = self.slots_by_id[slot_id]
            slot.hide_pulse_highlight()

    def on_skill_levels_trained(self, levels_trained):
        self.sequencing_time.update()

    def construct_layout(self):
        self.construct_base_containers()
        self.construct_gizmo_controls()
        self.construct_bottom_left_buttons()
        self.construct_bottom_right_buttons()
        self.reconstruct_slots_and_panels()
        self.construct_randomize_controls()
        self.construct_undo_buttons()
        self.construct_pattern_slots()
        self.construct_creator_character_info()

    def construct_undo_buttons(self):
        self.undo_btns = UndoButtons(parent=self.center_right_cont)

    def construct_randomize_controls(self):
        self.randomize_controls = RandomizeControls(name='randomize_controls', parent=self.center_left_cont)
        self.randomize_controls.angle_deg = 220

    def construct_bottom_left_buttons(self):
        button_group = ButtonGroup(parent=self.button_overlay_cont, align=Align.TOLEFT, button_alignment=AxisAlignment.START, density=Density.EXPANDED, button_size_mode=ButtonSizeMode.DYNAMIC, ignore_overflow=True)
        self.hull_selection_button = Button(parent=self, align=Align.CENTER, label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/HullSelection'), func=self.on_hull_selection_button, texturePath=eveicon.spaceship_command)
        button_group.add_button(self.hull_selection_button)
        self.save_skin_button = SaveSkinButton(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/Save'))
        button_group.add_button(self.save_skin_button)
        self.save_as_skin_button = SaveAsSkinButton(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SaveAs'))
        button_group.add_button(self.save_as_skin_button)

    def construct_creator_character_info(self):
        self.made_by_character_info = DesignOwnerCharacterInfo(name='made_by_character_info', parent=self, align=Align.BOTTOMLEFT, left=32, top=116)
        self._update_creator_character_info()

    def _update_creator_character_info(self):
        creator_char_id = current_skin_design.get().creator_character_id
        self.made_by_character_info.character_id = creator_char_id
        self.made_by_character_info.display = creator_char_id != session.charid

    def get_share_button_drag_data(self, *args):
        saved_design_id = current_skin_design.get().saved_skin_design_id
        if saved_design_id:
            saved_design_data = get_ship_skin_design_svc().get_saved_design(saved_design_id)
            if saved_design_data:
                return SkinDesignDragData(design_data=saved_design_data, saved_design_id=saved_design_id)

    def construct_bottom_right_buttons(self):
        self.bottom_right_container = Container(name='bottom_right_container', parent=self.button_overlay_cont, align=Align.TORIGHT_PROP, width=0.3)
        button_group = ButtonGroup(parent=self.bottom_right_container, align=Align.BOTTOMRIGHT, button_alignment=AxisAlignment.END, button_size_mode=ButtonSizeMode.STRETCH, overflow_align=OverflowAlign.LEFT, density=Density.EXPANDED, width=220)
        self.create_button = CreateSKINButton(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/FinalizeDesign'), func=self._on_create_btn, variant=ButtonVariant.PRIMARY)
        info_container = ContainerAutoSize(name='info_container', parent=self, align=Align.BOTTOMRIGHT, width=button_group.width, left=64, top=108)
        StudioCostInfo(name='cost_info', parent=info_container, align=Align.TOBOTTOM)
        self.sequencing_time = SequencingTime(name='sequencing_time', parent=info_container, align=Align.TOBOTTOM, minWidth=button_group.width - 32, padBottom=4)
        button_group.add_button(self.create_button)

    def _on_create_btn(self, *args):
        if should_show_popup_if_skin_name_missing.is_enabled() and not current_skin_design.get().name:
            dialogue = SkinNameDialogue(window_name=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SKINName'))
            form_value = dialogue.ShowModal()
            if form_value == uiconst.ID_CLOSE or not form_value[SkinNameDialogue.COMPONENT_NAME]:
                return
        self.on_create_btn()

    def on_hull_selection_button(self, *args):
        if self.hull_selection_panel:
            self.close_hull_selection_panel()
        else:
            self.show_hull_selection_panel()

    def show_hull_selection_panel(self):
        self.deselect_all_cosmetic_slots()
        self.hull_selection_panel = HullSelectionPanel(parent=self.overlay_cont, align=uiconst.TOLEFT, width=360, padding=(0,
         PANEL_PAD_TOP,
         0,
         PANEL_PAD_BOTTOM))
        self.hull_selection_panel.on_close_btn.connect(self.on_hull_selection_close_btn)
        animations.FadeTo(self.hull_selection_panel, 0.0, 1.0, duration=0.2)

    def on_hull_selection_close_btn(self, *args):
        self.close_hull_selection_panel()

    def close_hull_selection_panel(self):
        if self.hull_selection_panel:
            self.hull_selection_panel.Close()
            self.hull_selection_panel = None

    def deselect_all_cosmetic_slots(self):
        current_skin_design.set_selected_slot_id(None)

    def close_all_overlay_panels(self):
        self.close_hull_selection_panel()
        self.deselect_all_cosmetic_slots()

    def construct_base_containers(self):
        self.button_overlay_cont = Container(name='button_overlay_cont', parent=self, padding=(32, 0, 64, 64), align=Align.TOBOTTOM_NOPUSH, height=HEIGHT_EXPANDED)
        self.center_top_cont = Container(name='center_top_cont', parent=self)
        self.center_left_cont = Container(name='center_left_cont', parent=self)
        self.center_right_cont = Container(name='center_right_cont', parent=self)
        self.slots_left_cont = Container(name='slots_left_cont', parent=self.center_left_cont)
        self.slots_right_cont = Container(name='slots_right_cont', parent=self.center_right_cont)
        self.overlay_cont = Container(name='overlay_cont', parent=self, padding=32)

    def construct_gizmo_controls(self):
        self.gizmo_controls = GizmoControls(name='gizmo_controls', parent=self.center_top_cont, align=Align.CENTERTOP)

    def reconstruct_slots_and_panels(self):
        self.reconstruct_slots()
        self.reconstruct_panels()

    def reconstruct_slots(self):
        self.construct_non_pattern_slots()

    def construct_non_pattern_slots(self):
        for slot in self.slots_by_id.values():
            slot.Close()

        self.slots_by_id.clear()
        slot_config = self.get_current_skin_slot_config()
        for slot_id in slot_config.slots:
            if slot_id in PATTERN_RELATED_SLOT_IDS:
                continue
            slot_data = SlotsDataLoader.get_slot_data(slot_id)
            slot = CosmeticSlot(name='slot_{name}'.format(name=slot_data.internal_name), parent=self.slots_left_cont, slot_data=slot_data)
            slot.angle_deg = self.SLOT_ANGLES.get(slot_data.unique_id)
            self.slots_by_id[slot_data.unique_id] = slot
            if slot_id == SlotID.PRIMARY_NANOCOATING and not current_skin_design.get().has_fitted_components():
                slot.show_pulse_highlight()

    def construct_pattern_slots(self):
        self.pattern_slots = PatternSlots(name='pattern_slots', parent=self.slots_right_cont, align=Align.CENTER)

    def reconstruct_panels(self):
        for panel in self.panels_by_id.values():
            panel.on_close_btn.disconnect(self.on_panel_close_btn)
            panel.Close()

        self.panels_by_id.clear()
        slot_config = self.get_current_skin_slot_config()
        for slot_id in slot_config.slots:
            slot_data = SlotsDataLoader.get_slot_data(slot_id)
            self._construct_panel(slot_data)

    def _construct_panel(self, slot_data):
        align = Align.TORIGHT_NOPUSH if slot_data.unique_id in PATTERN_RELATED_SLOT_IDS else Align.TOLEFT_NOPUSH
        panel = ComponentPanel(name='panel_{slot_name}'.format(slot_name=slot_data.internal_name), parent=self.overlay_cont, slot_data=slot_data, align=align, padding=(0,
         PANEL_PAD_TOP,
         0,
         PANEL_PAD_BOTTOM))
        panel.on_close_btn.connect(self.on_panel_close_btn)
        self.panels_by_id[slot_data.unique_id] = panel

    def on_panel_close_btn(self, *args):
        self.close_all_overlay_panels()

    def on_design_reset(self, *args):
        self.populate_from_design()
        self.update_slots()

    def on_existing_design_loaded(self, *args):
        self.populate_from_design()
        self.update_slots()
        self._update_creator_character_info()

    def populate_from_design(self):
        self.populate_non_pattern_slots_from_design()
        self.populate_pattern_slots_from_design()
        self.save_skin_button.update_button_state()
        self.save_as_skin_button.update_button_state()

    def populate_non_pattern_slots_from_design(self):
        for slot_id in self.slots_by_id.keys():
            component_instance = current_skin_design.get().slot_layout.fitted_slots.get(slot_id, None)
            self.slots_by_id[slot_id].on_slot_fitting_changed(slot_id, component_instance)
            self.panels_by_id[slot_id].select_component(component_instance)

    def populate_pattern_slots_from_design(self):
        self.pattern_slots.populate_from_design()
        for slot_id in self.pattern_slots.slots_by_id.keys():
            component_instance = current_skin_design.get().slot_layout.fitted_slots.get(slot_id, None)
            self.panels_by_id[slot_id].select_component(component_instance)

    def on_slot_selected(self, slot_id):
        self.close_hull_selection_panel()
        for panel in self.panels_by_id.values():
            panel.on_slot_selected(slot_id)

    def on_scene_zoom(self, is_zoomed):
        if is_zoomed:
            self.center_top_cont.state = uiconst.UI_DISABLED
            self.center_left_cont.state = uiconst.UI_DISABLED
            self.center_right_cont.state = uiconst.UI_DISABLED
        else:
            self.center_top_cont.state = uiconst.UI_PICKCHILDREN
            self.center_left_cont.state = uiconst.UI_PICKCHILDREN
            self.center_right_cont.state = uiconst.UI_PICKCHILDREN
        if is_zoomed:
            width_distance, height_distance = self.get_zoomed_width_height()
            left_target = -width_distance
            right_target = width_distance
            top_target = -(min(width_distance, height_distance) + self.SLOT_WINDOW_GAP)
        else:
            left_target = 0.0
            right_target = 0.0
            top_target = 0.0
        animations.MorphScalar(self.center_left_cont, 'left', self.center_left_cont.left, left_target, duration=0.3)
        animations.MorphScalar(self.center_right_cont, 'left', self.center_right_cont.left, right_target, duration=0.3)
        animations.MorphScalar(self.center_top_cont, 'top', self.center_top_cont.top, top_target, duration=0.3)

    def get_zoomed_width_height(self):
        diameter = self.get_circular_layout_radius() * 2.0
        page_width, page_height = self.GetAbsoluteSize()
        width_distance = page_width - diameter - self.SLOT_WINDOW_GAP * 2.0
        height_distance = page_height - diameter - self.SLOT_WINDOW_GAP * 2.0
        return (width_distance, height_distance)

    def on_size_changed_signal(self, width, height):
        self.update_circular_layout(width, height)
        if width < 1100:
            self.gizmo_controls.width = self.gizmo_controls.default_width + width - 1100
        else:
            self.gizmo_controls.width = self.gizmo_controls.default_width

    def update_circular_layout(self, width, height):
        radius = self.get_circular_layout_radius()
        width_available = min(380, width / 2 - radius - 72)
        compact_mode = width_available < 246
        for slot in self.slots_by_id.values():
            slot.radius = radius

        self.pattern_slots.update_radial_position(radius + 40)
        for panel in self.panels_by_id.values():
            if compact_mode:
                offset = 128 if panel.align == Align.TOLEFT else 164
                panel.left = width_available + offset
                panel.width = 246
                panel.padTop = PANEL_PAD_TOP + 16
                panel.padBottom = PANEL_PAD_BOTTOM + 8
            else:
                panel.left = 0
                panel.width = width_available
                panel.padTop = PANEL_PAD_TOP
                panel.padBottom = PANEL_PAD_BOTTOM

        self.gizmo_controls.radius = radius
        self.randomize_controls.radius = radius - 20
        self.randomize_controls.angle_deg = 212 if compact_mode else 220
        if compact_mode:
            self.undo_btns.align = Align.BOTTOMRIGHT
            self.undo_btns.left = 64
            self.undo_btns.top = 210
        else:
            self.undo_btns.align = Align.CENTER
            self.undo_btns.radius = radius
            self.undo_btns.angle_deg = 45

    def update_slots(self):
        self.reconstruct_slots_and_panels()
        self.populate_from_design()
        self.update_circular_layout(*self.GetAbsoluteSize())

    def get_circular_layout_radius(self):
        return get_circular_layout_radius(*self.GetAbsoluteSize())

    def get_current_skin_slot_config(self):
        return SlotConfigurationsDataLoader.get_for_ship(current_skin_design.get().ship_type_id)


@Enum

class CreateButtonErrorState(object):
    OMEGA_BLOCKED = 1
    NO_COMPONENT_SELECTED = 2
    SEQUENCING_FEATURE_DISABLED = 3


class CreateSKINButton(Button):
    __notifyevents__ = ['OnSubscriptionChanged']
    error_state = None

    def __init__(self, get_menu_entry_data_func = None, **kwargs):
        super(CreateSKINButton, self).__init__(get_menu_entry_data_func, **kwargs)
        sm.RegisterNotify(self)

    def OnSubscriptionChanged(self):
        self.update()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.error_state == CreateButtonErrorState.OMEGA_BLOCKED:
            tooltipPanel.LoadStandardSpacing()
            tooltipPanel.columns = 2
            tooltipPanel.AddRow(rowClass=OmegaTooltipPanelCell, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/CannotSequenceForHullOmega'), origin=ORIGIN_SHIP_SKINR)
            tooltipPanel.pickState = PickState.ON
        elif self.error_state == CreateButtonErrorState.NO_COMPONENT_SELECTED:
            tooltipPanel.LoadStandardSpacing()
            tooltipPanel.columns = 1
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/NoComponentsSelected'), wrapWidth=300)
        elif self.error_state == CreateButtonErrorState.SEQUENCING_FEATURE_DISABLED:
            tooltipPanel.LoadStandardSpacing()
            tooltipPanel.columns = 1
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SequencingFeatureDisabled'), wrapWidth=300)

    def update(self):
        if not get_ship_skin_sequencing_svc().can_sequence_for_hull(current_skin_design.get().ship_type_id):
            self.enabled = False
            self.error_state = CreateButtonErrorState.OMEGA_BLOCKED
        elif not current_skin_design.get().slot_layout.fitted_slots:
            self.enabled = False
            self.error_state = CreateButtonErrorState.NO_COMPONENT_SELECTED
        else:
            self.enabled = True
            self.error_state = None


class UndoButtons(ButtonGroup, RadiallyAlignedMixin):
    default_align = Align.CENTER

    def __init__(self, **kw):
        super(UndoButtons, self).__init__(**kw)
        self.undo_btn = Button(parent=self, func=self.on_undo_btn, texturePath=eveicon.arrow_rotate_left, hint=GetByLabel('UI/Common/Undo'), variant=ButtonVariant.GHOST)
        self.redo_btn = Button(parent=self, func=self.on_redo_btn, texturePath=eveicon.arrow_rotate_right, hint=GetByLabel('UI/Common/Redo'), variant=ButtonVariant.GHOST)
        self.connnect_signals()
        self.update()

    def connnect_signals(self):
        current_skin_design_signals.on_undo_history_change.connect(self.on_undo_history_change)

    def on_undo_history_change(self):
        self.update()

    def update(self):
        self.undo_btn.enabled = current_skin_design.is_undo_enabled()
        self.redo_btn.enabled = current_skin_design.is_redo_enabled()

    def on_undo_btn(self, *args):
        current_skin_design.undo()

    def on_redo_btn(self, *args):
        current_skin_design.redo()
