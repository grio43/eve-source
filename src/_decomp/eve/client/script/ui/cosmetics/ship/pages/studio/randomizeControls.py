#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\randomizeControls.py
import eveicon
import random
import uthread
import uthread2
from carbonui.control.contextMenu.contextMenuMixin import ContextMenuMixin
from carbonui.control.contextMenu.menuUtil import ClearMenuLayer
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.text.color import TextColor
from carbonui.text.styles import TextBody
from carbonui.uianimations import animations
from carbonui.uiconst import Align, PickState, TIME_ENTRY
from carbonui.uicore import uicore
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from cosmetics.common.ships.skins.static_data.slot import SlotsDataLoader
from cosmetics.common.ships.skins.static_data.slot_name import SlotID, PATTERN_SLOT_IDS, PATTERN_MATERIAL_SLOT_IDS, PATTERN_RELATED_SLOT_IDS
from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
from eve.client.script.ui import eveColor
from eve.client.script.ui.cosmetics.ship.const import CHILD_PAGES_BY_PARENT_PAGE, SkinrPage
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSettings, studioSignals
from eve.client.script.ui.cosmetics.ship.pages.studio.circularButtonIcon import CircularMenuButtonIcon
from eve.client.script.ui.cosmetics.ship.pages.studio.cosmeticSlot import CosmeticSlotButton
from eve.client.script.ui.cosmetics.ship.pages.studio.radiallyAlignedMixin import RadiallyAlignedMixin
from eve.client.script.ui.cosmetics.ship.pages.studio.studioUtil import RANDOMIZE_BUTTON_ANALYTIC_ID
from localization import GetByLabel
from signals import Signal
ICON_BY_SLOT_ID = {SlotID.PRIMARY_NANOCOATING: eveicon.primary_area,
 SlotID.SECONDARY_NANOCOATING: eveicon.secondary_area,
 SlotID.TERTIARY_NANOCOATING: eveicon.details,
 SlotID.TECH_AREA: eveicon.tech_area,
 SlotID.PATTERN: eveicon.patterns,
 SlotID.SECONDARY_PATTERN: eveicon.patterns,
 SlotID.PATTERN_MATERIAL: eveicon.kerr,
 SlotID.SECONDARY_PATTERN_MATERIAL: eveicon.kerr}
PRIMARY_PATTERN_TOGGLE_IDS = [SlotID.PATTERN, SlotID.PATTERN_MATERIAL]
SECONDARY_PATTERN_TOGGLE_IDS = [SlotID.SECONDARY_PATTERN, SlotID.SECONDARY_PATTERN_MATERIAL]
NON_PATTERN_TOGGLE_IDS = [SlotID.PRIMARY_NANOCOATING,
 SlotID.SECONDARY_NANOCOATING,
 SlotID.TERTIARY_NANOCOATING,
 SlotID.TECH_AREA]
PAIRED_PATTERN_SLOT_ID = {SlotID.PATTERN: SlotID.PATTERN_MATERIAL,
 SlotID.PATTERN_MATERIAL: SlotID.PATTERN,
 SlotID.SECONDARY_PATTERN: SlotID.SECONDARY_PATTERN_MATERIAL,
 SlotID.SECONDARY_PATTERN_MATERIAL: SlotID.SECONDARY_PATTERN}
TOGGLE_OFFSET = 40
on_filter_changed = Signal('on_filter_changed')

class RandomizeControls(Container, RadiallyAlignedMixin):
    default_align = Align.CENTER
    default_width = 128
    default_height = 128

    def __init__(self, *args, **kwargs):
        super(RandomizeControls, self).__init__(*args, **kwargs)
        self.on_randomize = Signal('on_randomize')
        self.construct_layout()
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(RandomizeControls, self).Close()

    def connect_signals(self):
        current_skin_design_signals.on_ship_type_id_changed.connect(self.on_ship_type_id_changed)
        current_skin_design_signals.on_slot_fitting_changed.connect(self.on_slot_fitting_changed)
        studioSignals.on_page_opened.connect(self.on_page_opened)

    def disconnect_signals(self):
        current_skin_design_signals.on_ship_type_id_changed.disconnect(self.on_ship_type_id_changed)
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.on_slot_fitting_changed)
        studioSignals.on_page_opened.disconnect(self.on_page_opened)

    def construct_layout(self):
        self.randomize_button = CosmeticSlotButton(name='randomize_button', parent=self, align=Align.CENTER, texture_path=eveicon.randomize, icon_size=16, hint=GetByLabel('UI/CharacterCreation/Randomize'), pos=(0, 0, 48, 48))
        self.randomize_button.analyticID = RANDOMIZE_BUTTON_ANALYTIC_ID
        self.randomize_button.on_click = self.on_randomize_button_click
        self.slot_filters = RandomizeSlotFilters(name='slot_filters', parent=self, align=Align.CENTER, slot_id=SlotID.PATTERN, left=48, top=24)

    @uthread2.debounce(0.15)
    def on_randomize_button_click(self, *args):
        slot_ids = self.slot_filters.selected_slot_ids
        uthread.parallel([ (self.apply_random_component, (slot_id,)) for slot_id in slot_ids ])
        current_skin_design.add_to_undo_history()

    def on_ship_type_id_changed(self, *args):
        self.slot_filters.rebuild()

    def on_slot_fitting_changed(self, slot_id, component_instance):
        if slot_id == SlotID.SECONDARY_PATTERN and component_instance is None:
            self.slot_filters.deselect_secondary_pattern()

    def on_page_opened(self, page_id, page_args, last_page_id, animate = True):
        if last_page_id not in CHILD_PAGES_BY_PARENT_PAGE[SkinrPage.STUDIO]:
            return
        if page_id not in CHILD_PAGES_BY_PARENT_PAGE[SkinrPage.STUDIO]:
            self.slot_filters.clear()

    def apply_random_component(self, slot_id):
        only_owned = studioSettings.only_shown_owned_design_elements_setting.is_enabled()
        component_data = get_ship_skin_component_svc().get_random_component_data(slot_id, only_owned=only_owned)
        component_intance = current_skin_design.get().fit_slot(slot_id, component_data.component_id)
        if slot_id in PATTERN_SLOT_IDS:
            self.randomize_pattern_attributes(component_intance)

    def randomize_pattern_attributes(self, component_instance):
        component_instance.scaling_ratio = 0.5 + 0.5 * random.random()
        component_instance.offset_v_ratio = -0.5 + random.random()
        component_instance.offset_u_ratio = -0.5 + random.random()
        component_instance.yaw = -1.0 + 2 * random.random()
        component_instance.pitch = 0.75 + 0.25 * random.random()
        component_instance.mirrored = random.choice([True, False])


class RandomizeSlotFilters(CircularMenuButtonIcon):
    default_pickState = PickState.ON
    default_texturePath = eveicon.ship_areas
    default_hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/RandomizeAreaApplication')

    def __init__(self, *args, **kwargs):
        super(RandomizeSlotFilters, self).__init__(*args, **kwargs)
        self.menu = None
        self._filters = {}
        self.clear()
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(RandomizeSlotFilters, self).Close()

    def connect_signals(self):
        on_filter_changed.connect(self.on_filter_changed)

    def disconnect_signals(self):
        on_filter_changed.disconnect(self.on_filter_changed)

    def on_filter_changed(self, slot_id, is_selected):
        self._filters[slot_id] = is_selected

    def clear(self):
        self._filters.clear()
        for slot_id in current_skin_design.get().slot_layout.slots.keys():
            self._filters[slot_id] = True

        self.clear_if_no_filters()

    def rebuild(self):
        existing_filters = self._filters.copy()
        self.clear()
        for slot_id in self._filters:
            if slot_id in existing_filters:
                self._filters[slot_id] = existing_filters[slot_id]

        self.clear_if_no_filters()

    def clear_if_no_filters(self):
        if len(self.selected_slot_ids) == 0:
            self.clear()

    def deselect_secondary_pattern(self):
        for slot_id in SECONDARY_PATTERN_TOGGLE_IDS:
            self._filters[slot_id] = False

        if len(self.selected_slot_ids) == 0:
            self.clear()

    def OnMouseUp(self, *args):
        if self.has_open_menu:
            return
        ClearMenuLayer()
        left, top, width, height = self.GetAbsolute()
        self.menu = SlotToggleMenu(parent=uicore.layer.menu, filters=self._filters, left=left + TOGGLE_OFFSET, top=top)

    def GetHint(self):
        if self.has_open_menu:
            return None
        return super(RandomizeSlotFilters, self).GetHint()

    @property
    def has_open_menu(self):
        return self.menu and not self.menu.destroyed

    @property
    def selected_slot_ids(self):
        return [ k for k, v in self._filters.items() if v ]


class SlotToggleMenu(Container, ContextMenuMixin):
    default_align = Align.ABSOLUTE
    default_width = 232
    default_height = 72

    def __init__(self, filters, *args, **kwargs):
        super(SlotToggleMenu, self).__init__(*args, **kwargs)
        self._toggles = {}
        self._pattern_links = {}
        self.construct_layout(filters)
        self.appear()

    def construct_layout(self, filters):
        for slot_id, is_selected in filters.items():
            toggle = SlotToggle(parent=self, slot_id=slot_id, is_selected=is_selected, texturePath=ICON_BY_SLOT_ID[slot_id])
            toggle.on_click.connect(self.on_toggle_click)
            self._toggles[slot_id] = toggle
            if slot_id in PATTERN_MATERIAL_SLOT_IDS:
                link = Fill(parent=self, align=Align.TOPLEFT, pos=(0, 0, 2, 8), color=eveColor.GUNMETAL_GREY, opacity=0.5)
                self._pattern_links[slot_id] = link

    def on_toggle_click(self, toggle):
        if toggle.is_selected and self.is_last_toggle_or_pair(toggle.slot_id):
            return
        if not toggle.is_selected and toggle.slot_id in SECONDARY_PATTERN_TOGGLE_IDS:
            if SlotID.PATTERN not in self.selected_slot_ids and not self.is_component_fitted(SlotID.PATTERN):
                return
        if toggle.is_selected and toggle.slot_id in PRIMARY_PATTERN_TOGGLE_IDS:
            if self.is_component_fitted(SlotID.PATTERN):
                pass
            else:
                if self.only_pattern_slot_ids_selected and not self.is_component_fitted(SlotID.SECONDARY_PATTERN):
                    return
                if not self.is_component_fitted(SlotID.SECONDARY_PATTERN):
                    self.deselect_secondary_pattern()
        toggle.toggle_value()
        on_filter_changed(toggle.slot_id, toggle.is_selected)
        if toggle.slot_id in PAIRED_PATTERN_SLOT_ID:
            self.set_paired_toggle(toggle.slot_id, toggle.is_selected)

    def is_last_toggle_or_pair(self, slot_id):
        selected_slot_ids = self.selected_slot_ids
        if len(selected_slot_ids) == 1 and slot_id in selected_slot_ids:
            return True
        if len(selected_slot_ids) == 2:
            if slot_id in PATTERN_RELATED_SLOT_IDS and slot_id in selected_slot_ids:
                return True
        return False

    def set_paired_toggle(self, slot_id, is_selected):
        paired_slot_id = PAIRED_PATTERN_SLOT_ID[slot_id]
        paired_toggle = self._toggles[paired_slot_id]
        paired_toggle.set_value(is_selected)
        on_filter_changed(paired_slot_id, is_selected)

    def deselect_secondary_pattern(self):
        for slot_id in SECONDARY_PATTERN_TOGGLE_IDS:
            toggle = self._toggles.get(slot_id, None)
            if not toggle:
                continue
            toggle.set_value(False)
            on_filter_changed(slot_id, False)

    def appear(self):
        left_index = 0
        for i, toggle in enumerate(self._toggles.values()):
            if toggle.slot_id in PATTERN_MATERIAL_SLOT_IDS:
                if left_index > 0:
                    left_index -= 1
                animations.MorphScalar(toggle, 'top', 0, TOGGLE_OFFSET, duration=TIME_ENTRY)
                link = self._pattern_links[toggle.slot_id]
                animations.MorphScalar(obj=link, attrName='top', startVal=TOGGLE_OFFSET * 0.5 - link.height * 0.5, endVal=TOGGLE_OFFSET - link.height, duration=TIME_ENTRY)
                animations.MorphScalar(obj=link, attrName='left', startVal=-TOGGLE_OFFSET * 0.5 - link.width * 0.5, endVal=left_index * TOGGLE_OFFSET + toggle.width * 0.5 - link.width * 0.5, duration=TIME_ENTRY)
            animations.MorphScalar(toggle, 'left', -TOGGLE_OFFSET, left_index * TOGGLE_OFFSET, duration=TIME_ENTRY)
            left_index += 1

    def is_component_fitted(self, slot_id):
        if current_skin_design.get().get_fitted_component_instance(slot_id):
            return True
        return False

    @property
    def selected_slot_ids(self):
        return [ k for k, v in self._toggles.items() if v.is_selected ]

    @property
    def only_pattern_slot_ids_selected(self):
        for slot_id in self.selected_slot_ids:
            if slot_id in NON_PATTERN_TOGGLE_IDS:
                return False

        return True


class SlotToggle(CircularMenuButtonIcon):
    default_colorSelected = TextColor.NORMAL

    def __init__(self, slot_id, is_selected, *args, **kwargs):
        super(SlotToggle, self).__init__(*args, **kwargs)
        self.slot_id = slot_id
        self.is_selected = is_selected
        self.on_click = Signal('on_click')
        self.construct_layout()
        self.update()

    def construct_layout(self):
        slot_data = SlotsDataLoader.get_slot_data(self.slot_id)
        self.text = TextBody(parent=self, text=slot_data.name, align=Align.CENTER, opacity=0.0)

    def update(self):
        if self.is_selected:
            self.SetSelected()
        else:
            self.SetDeselected()

    def toggle_value(self):
        self.is_selected = not self.is_selected
        self.update()

    def set_value(self, is_selected):
        self.is_selected = is_selected
        self.update()

    def OnClick(self, *args):
        self.on_click(self)

    def OnMouseEnter(self, *args):
        animations.FadeIn(self.text, endVal=TextColor.NORMAL[-1], duration=TIME_ENTRY)
        offset = TOGGLE_OFFSET * 0.5
        if self.slot_id in PATTERN_MATERIAL_SLOT_IDS:
            animations.MorphScalar(self.text, 'top', offset, offset + 8, duration=0.1)
        else:
            animations.MorphScalar(self.text, 'top', -offset, -offset - 8, duration=0.1)

    def OnMouseExit(self, *args):
        animations.FadeOut(self.text, duration=0.1)
        offset = TOGGLE_OFFSET * 0.5
        if self.slot_id in PATTERN_MATERIAL_SLOT_IDS:
            animations.MorphScalar(self.text, 'top', self.text.top, offset, duration=0.1)
        else:
            animations.MorphScalar(self.text, 'top', self.text.top, -offset, duration=0.1)
