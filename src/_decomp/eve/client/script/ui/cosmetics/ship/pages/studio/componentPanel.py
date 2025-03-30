#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\componentPanel.py
import eveicon
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_QA
from carbonui import Align, TextColor, uiconst, TextBody
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.checkbox import Checkbox
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.tabGroup import TabGroup
from carbonui.primitives.container import Container
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uiconst import VK_DOWN, VK_UP, VK_LEFT, VK_RIGHT, VK_PRIOR, VK_NEXT
from carbonui.uicore import uicore
from collections import defaultdict
from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.ships.qa.settings import show_unpublished_components
from cosmetics.client.ships.skins.live_data import current_skin_design
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from cosmetics.common.ships.skins.static_data.component_finish import ComponentFinish
from cosmetics.common.ships.skins.static_data.slot import SlotsDataLoader
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.cosmetics.ship.const import COMPONENT_CATEGORY_NAMES, SkinrPage, SLOT_ICONS
from eve.client.script.ui.cosmetics.ship.pages import current_page
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
from eve.client.script.ui.cosmetics.ship.pages.studio.componentLicenseEntry import ComponentEntry
from eve.client.script.ui.cosmetics.ship.pages.studio.studioSettings import only_shown_owned_design_elements_setting
from localization import GetByLabel
from signals import Signal
FINISH_ALL = 0
LABEL_BY_COMPONENT_FINISH = {ComponentFinish.MATTE: 'UI/Personalization/ShipSkins/SKINR/FinishMatte',
 ComponentFinish.SATIN: 'UI/Personalization/ShipSkins/SKINR/FinishSatin',
 ComponentFinish.GLOSS: 'UI/Personalization/ShipSkins/SKINR/FinishGloss'}

class ComponentPanel(Container):
    default_state = uiconst.UI_DISABLED
    default_width = 360
    default_opacity = 0.0
    RADIUS_OFFSET = 50
    isTabStop = True

    def __init__(self, slot_data, *args, **kwargs):
        super(ComponentPanel, self).__init__(*args, **kwargs)
        self.slot_data = slot_data
        self.is_active = False
        self.on_close_btn = Signal('on_close_btn')
        self._reconstruct_thread = None
        self._selected_category = None
        self.construct_layout()
        self.connect_signals()

    def Close(self):
        try:
            self.kill_reconstruct_thread()
            self.disconnect_signals()
        finally:
            super(ComponentPanel, self).Close()

    def kill_reconstruct_thread(self):
        if self._reconstruct_thread is not None:
            self._reconstruct_thread.kill()
            self._reconstruct_thread = None

    def connect_signals(self):
        studioSignals.on_scene_zoom.connect(self.on_scene_zoom)
        ship_skin_signals.on_component_license_granted.connect(self._on_component_license_granted)
        ship_skin_signals.on_component_license_cache_invalidated.connect(self._on_component_license_cache_invalidated)
        ship_skin_signals.on_skin_sequencing_job_updated.connect(self.on_skin_sequencing_job_updated)
        only_shown_owned_design_elements_setting.on_change.connect(self.on_only_show_owned_design_elements_setting)
        show_unpublished_components.on_change.connect(self._on_qa_show_unpublished)

    def disconnect_signals(self):
        studioSignals.on_scene_zoom.disconnect(self.on_scene_zoom)
        ship_skin_signals.on_component_license_granted.disconnect(self._on_component_license_granted)
        ship_skin_signals.on_component_license_cache_invalidated.disconnect(self._on_component_license_cache_invalidated)
        ship_skin_signals.on_skin_sequencing_job_updated.disconnect(self.on_skin_sequencing_job_updated)
        only_shown_owned_design_elements_setting.on_change.disconnect(self.on_only_show_owned_design_elements_setting)
        show_unpublished_components.on_change.disconnect(self._on_qa_show_unpublished)

    def on_only_show_owned_design_elements_setting(self, *args):
        self.reconstruct_entries()

    def construct_layout(self):
        self.content = Container(name='content', parent=self, padding=16)
        self.construct_header()
        self.category_toggle_button_group = ToggleButtonGroup(name='category_toggle_button_group', parent=self.content, align=Align.TOTOP, padTop=4, callback=self.on_category_toggle_buttons)
        self.finish_tab_group = TabGroup(name='finish_tab_group', parent=self.content, callback=self.on_finish_tab_group, show_line=False, padTop=4, padBottom=-4)
        Checkbox(name='only_ownned_checkbox', parent=self.content, align=Align.TOTOP, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/OnlyShowOwned'), setting=only_shown_owned_design_elements_setting, padTop=16)
        self.button_group = ButtonGroup(parent=self.content, align=Align.TOBOTTOM, button_size_mode=ButtonSizeMode.STRETCH, padTop=4)
        Button(name='buy_more_btn', parent=self.button_group, label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/BuyMore'), func=self.on_buy_more_btn)
        self.scroll_container = ScrollContainer(name='scroll_container', parent=self.content, align=Align.TOALL, padTop=8)
        self.scroll_container.OnKeyDown = self.OnKeyDown
        self.flow_container = FlowContainer(name='flow_container', parent=self.scroll_container, align=Align.TOTOP, contentSpacing=(4, 4))

    def construct_header(self):
        header_cont = Container(name='header_cont', parent=self.content, align=Align.TOTOP, height=36)
        icon_cont = Container(name='icon_cont', parent=header_cont, align=Align.TOLEFT, width=36)
        Frame(bgParent=icon_cont, color=(1, 1, 1, 0.05))
        Sprite(parent=icon_cont, texturePath=SLOT_ICONS[self.slot_data.unique_id], pos=(0, 0, 32, 32), align=Align.CENTER, color=TextColor.HIGHLIGHT)
        text_cont = Container(parent=header_cont, bgColor=(1, 1, 1, 0.05), clipChildren=True, padLeft=4)
        TextBody(parent=text_cont, align=Align.VERTICALLY_CENTERED, text=self.slot_data.name, color=TextColor.HIGHLIGHT, autoFadeSides=10, padLeft=16, padRight=32)
        ButtonIcon(parent=header_cont, align=Align.CENTERRIGHT, texturePath=eveicon.close, func=self.on_close_btn)

    def on_finish_tab_group(self, *args):
        self.reconstruct_entries()

    def on_buy_more_btn(self, *args):
        current_page.set_page_id(page_id=SkinrPage.STORE_COMPONENTS, page_args=self.get_selected_category())

    def _on_qa_show_unpublished(self, *args):
        if session.role & ROLE_QA:
            self.reconstruct_entries()

    def get_selected_category(self):
        return self.category_toggle_button_group.GetSelected()

    def reconstruct_category_buttons(self):
        self.kill_reconstruct_thread()
        self._reconstruct_thread = uthread2.start_tasklet(self.reconstruct_category_buttons_async)

    def reconstruct_category_buttons_async(self):
        try:
            self.category_toggle_button_group.Flush()
            licenses_by_category = self.get_components_by_category()
            categories = licenses_by_category.keys()
            for category in categories:
                category_name = GetByLabel(COMPONENT_CATEGORY_NAMES.get(category))
                self.category_toggle_button_group.AddButton(label=category_name, btnID=category)

            self.category_toggle_button_group.display = len(categories) > 1
            category_id = self.get_selected_category_id(licenses_by_category)
            if category_id:
                self.category_toggle_button_group.SelectByID(category_id)
        finally:
            self._reconstruct_thread = None

    def get_components_by_category(self):
        slot_id = self.slot_data.unique_id
        components_by_category = defaultdict(list)
        components = SlotsDataLoader.get_allowed_component(slot_id).values()
        for component_data in components:
            category = component_data.category
            components_by_category[category].append(component_data)

        return components_by_category

    def check_tab_exists(self, finish):
        if finish == FINISH_ALL:
            finish_label = GetByLabel('UI/Common/All')
        else:
            finish_label = GetByLabel(LABEL_BY_COMPONENT_FINISH[finish])
        label, name = self.finish_tab_group.GetNameLabel(finish_label)
        uiID = self.finish_tab_group.GetUIID(name, finish)
        exist = list(filter(lambda x: x.parent == self.finish_tab_group.tabsCont and str(x.tabID) == str(uiID), self.finish_tab_group.mytabs))
        return len(exist) > 0

    def reconstruct_finish_tabs(self):
        selected_finish = self.finish_tab_group.GetSelectedID()
        self.finish_tab_group.Flush()
        components = self.get_components_to_show()
        finishes = {c.finish for c in components}
        if not self.check_tab_exists(FINISH_ALL):
            self.finish_tab_group.AddTab(label=GetByLabel('UI/Common/All'), tabID=FINISH_ALL)
        if len(finishes) > 1:
            self.finish_tab_group.display = True
            for finish in (ComponentFinish.MATTE, ComponentFinish.SATIN, ComponentFinish.GLOSS):
                if finish not in finishes:
                    continue
                if not self.check_tab_exists(finish):
                    self.finish_tab_group.AddTab(label=GetByLabel(LABEL_BY_COMPONENT_FINISH[finish]), tabID=finish)

        else:
            self.finish_tab_group.display = False
        if selected_finish is None:
            selected_finish = FINISH_ALL
        self.finish_tab_group.SelectByID(selected_finish, useCallback=False)

    def get_selected_category_id(self, licenses_by_category):
        if self._selected_category:
            return self._selected_category
        component_instance = current_skin_design.get().slot_layout.slots[self.slot_data.unique_id]
        if component_instance:
            return component_instance.category
        elif len(licenses_by_category.keys()) > 0:
            return licenses_by_category.keys()[0]
        else:
            return None

    def on_category_toggle_buttons(self, new_category, old_category):
        self._selected_category = new_category
        self.reconstruct_finish_tabs()
        self.reconstruct_entries()

    def reconstruct_entries(self):
        self.flow_container.Flush()
        components = self.get_components_to_show()
        fitted_component = current_skin_design.get().slot_layout.slots.get(self.slot_data.unique_id)
        fitted_component_id = fitted_component.component_id if fitted_component else None
        for component_data in components:
            owned_licenses_by_type = get_ship_skin_component_svc().get_owned_licenses_by_type(component_data.component_id)
            is_selected = component_data.component_id == fitted_component_id
            ComponentEntry(parent=self.flow_container, slot_id=self.slot_data.unique_id, component_data=component_data, is_selected=is_selected, limited_license=owned_licenses_by_type.get(ComponentLicenseType.LIMITED, None), unlimited_license=owned_licenses_by_type.get(ComponentLicenseType.UNLIMITED, None))

    def get_components_to_show(self):
        components = SlotsDataLoader.get_allowed_component(self.slot_data.unique_id).values()
        if only_shown_owned_design_elements_setting.is_enabled():
            owned_licenses = get_ship_skin_component_svc().get_all_owned_licenses()
            owned_ids = {l.component_id for l in owned_licenses}
            components = [ c for c in components if c.component_id in owned_ids ]
        show_unpublished = show_unpublished_components.is_enabled()
        if not session.role & ROLE_QA or not show_unpublished:
            components = [ c for c in components if c.published ]
        category_id = self.get_selected_category()
        if category_id:
            components = [ c for c in components if c.category == category_id ]
        selected_finish = self.finish_tab_group.GetSelectedID()
        if selected_finish:
            components = [ c for c in components if c.finish == selected_finish ]
        components = sorted(components, key=lambda component: component.color_shade_sort_index, reverse=False)
        return components

    def get_components_in_selected_category(self):
        components_by_category = self.get_components_by_category()
        components = components_by_category[self.get_selected_category()]
        return components

    def on_slot_selected(self, slot_id):
        if slot_id == self.slot_data.unique_id:
            self.reconstruct_tabs()
            self.appear()
            uicore.registry.SetFocus(self)
        else:
            self.disappear()

    def reconstruct_tabs(self):
        self.reconstruct_category_buttons()
        self.reconstruct_finish_tabs()

    def disappear(self):
        self.is_active = False
        self.state = uiconst.UI_DISABLED
        self.StopAnimations()
        self.opacity = 0.0

    def appear(self):
        if self.is_active:
            return
        self.is_active = True
        self.state = uiconst.UI_PICKCHILDREN
        animations.FadeTo(self, self.opacity, 1.0, duration=4 * uiconst.TIME_ENTRY)

    def on_scene_zoom(self, is_zoomed):
        if not self.is_active:
            return
        target_opacity = 0.0 if is_zoomed else 1.0
        time_offset = 0.0 if is_zoomed else 0.15
        animations.FadeTo(self, self.opacity, target_opacity, duration=0.15, timeOffset=time_offset)

    def OnKeyDown(self, key, *args):
        diff = None
        if key == VK_LEFT:
            diff = -1
        elif key == VK_RIGHT:
            diff = 1
        elif key == VK_UP:
            diff = -3
        elif key == VK_DOWN:
            diff = 3
        elif key == VK_PRIOR:
            self.scroll_container.ScrollByPage(up=True)
        elif key == VK_NEXT:
            self.scroll_container.ScrollByPage(up=False)
        if diff:
            self._select_new_component(diff)

    def _select_new_component(self, diff):
        selected = self.get_selected()
        components = self.flow_container.children
        if selected:
            idx = components.index(selected) + diff
        else:
            idx = 0
        if 0 <= idx < len(components):
            components[idx].toggle_selected()

    def get_selected(self):
        for component in self.flow_container.children:
            if component.is_selected:
                return component

    def select_component(self, component_instance):
        for component in self.flow_container.children:
            if component_instance is None:
                component.is_selected = False
            else:
                component.is_selected = component.component_data.component_id == component_instance.component_id

    def _on_component_license_granted(self, *args):
        self._on_licenses_updated()

    def _on_component_license_cache_invalidated(self, _licenses_flushed):
        self._on_licenses_updated()

    def on_skin_sequencing_job_updated(self, *args):
        self._on_licenses_updated()

    @uthread2.debounce(1.0)
    def _on_licenses_updated(self):
        self.reconstruct_tabs()
