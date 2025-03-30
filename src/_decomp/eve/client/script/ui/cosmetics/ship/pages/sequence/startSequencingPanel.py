#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\sequence\startSequencingPanel.py
import eveicon
import uthread2
from carbonui import Align, AxisAlignment, Density, PickState
from carbonui import ButtonVariant, ButtonStyle
from carbonui import TextBody, TextColor, TextHeader
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from characterskills.client import skill_signals
from cosmetics.client.shipSkinSequencingSvc import get_ship_skin_sequencing_svc
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.ships.qa.settings import is_sequencing_button_always_enabled
from cosmetics.client.ships.skins.errors import SEQUENCING_ERROR_TEXT_BY_CODE
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from cosmetics.common.cosmeticsConst import SEQUENCE_BINDER_TYPES
from cosmetics.common.ships.skins import sequencing_util
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from cosmetics.common.ships.skins.util import Currency
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.controls.costInfo import SequencingPanelCostInfo
from eve.client.script.ui.cosmetics.ship.controls.decoratedLine import DecoratedLine
from eve.client.script.ui.cosmetics.ship.controls.sequencingTime import SequencingTime
from eve.client.script.ui.cosmetics.ship.pages import current_page
from eve.client.script.ui.cosmetics.ship.pages.sequence import sequence_ui_signals
from eve.client.script.ui.cosmetics.ship.pages.sequence.sequenceBinderEntries import SequenceBinderCostEntry, UnlimitedComponentLicenseEntry, LimitedComponentLicenseEntry
from eve.client.script.ui.cosmetics.ship.pages.sequence.tooltipInfoIcons import NumRunsInfoIcon
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from skills.client.util import get_skill_service
from stackless_response_router.exceptions import TimeoutException

class StartSequencingPanel(Container):
    default_width = 350

    def __init__(self, **kw):
        super(StartSequencingPanel, self).__init__(**kw)
        self.unlimited_sequence_binder_entries = []
        self.limited_sequence_binder_entries = []
        self.sequencing_time = None
        self.cost_info = None
        self.num_skins_edit = None
        self.start_btn = None
        self.unlimited_use_entry_container = None
        self.limited_use_entry_container = None
        self._update_values_thread = None
        self._set_num_runs_thread = None
        self.construct_bottom_buttons()
        self.construct_cost_info_container()
        self.construct_sequencing_time_container()
        self.construct_content_containers()
        self.connnect_signals()

    def Close(self):
        try:
            self.kill_threads()
            self.disconnect_signals()
        finally:
            super(StartSequencingPanel, self).Close()

    def kill_threads(self):
        self.kill_update_values_thread()
        self.kill_set_num_runs_thread()

    def kill_update_values_thread(self):
        if self._update_values_thread:
            self._update_values_thread.kill()
            self._update_values_thread = None

    def kill_set_num_runs_thread(self):
        if self._set_num_runs_thread:
            self._set_num_runs_thread.kill()
            self._set_num_runs_thread = None

    def connnect_signals(self):
        skill_signals.on_skill_levels_trained.connect(self.on_skill_levels_trained)
        sequence_ui_signals.on_num_skins_changed.connect(self.on_num_skins_changed)
        sequence_ui_signals.on_sequence_binders_changed.connect(self.on_sequence_binders_changed)
        current_skin_design_signals.on_name_changed.connect(self.on_current_skin_design_name_changed)
        current_skin_design_signals.on_component_instance_license_to_use_changed.connect(self.on_component_instance_license_to_use_changed)
        ship_skin_signals.on_component_license_granted.connect(self.on_component_license_granted)
        ship_skin_signals.on_skin_sequencing_cache_invalidated.connect(self.on_skin_sequencing_cache_invalidated)
        is_sequencing_button_always_enabled.on_change.connect(self._on_mock_sequencing_button_changed)
        self.on_size_changed.connect(self.on_size_changed_signal)
        sm.RegisterForNotifyEvent(self, 'OnAurumChangeFromVgs')

    def disconnect_signals(self):
        skill_signals.on_skill_levels_trained.disconnect(self.on_skill_levels_trained)
        sequence_ui_signals.on_num_skins_changed.disconnect(self.on_num_skins_changed)
        sequence_ui_signals.on_sequence_binders_changed.disconnect(self.on_sequence_binders_changed)
        current_skin_design_signals.on_name_changed.disconnect(self.on_current_skin_design_name_changed)
        current_skin_design_signals.on_component_instance_license_to_use_changed.disconnect(self.on_component_instance_license_to_use_changed)
        ship_skin_signals.on_component_license_granted.disconnect(self.on_component_license_granted)
        ship_skin_signals.on_skin_sequencing_cache_invalidated.disconnect(self.on_skin_sequencing_cache_invalidated)
        is_sequencing_button_always_enabled.on_change.disconnect(self._on_mock_sequencing_button_changed)
        self.on_size_changed.disconnect(self.on_size_changed_signal)
        sm.UnregisterForNotifyEvent(self, 'OnAurumChangeFromVgs')

    def load_panel(self):
        current_skin_design.get().clean_up_skin()
        self.reconstruct_layout()
        self.update_values()
        self.anim_entry()

    def anim_entry(self):
        self.content.opacity = 0.0
        animations.MorphScalar(self, 'left', -200, 0, duration=0.6)
        animations.FadeTo(self.content, 0.0, 1.0, duration=0.3, timeOffset=0.6)

    def reconstruct_layout(self):
        self.content.Flush()
        self.construct_layout()
        self.on_size_changed_signal()

    def construct_content_containers(self):
        outer_container = Container(name='outer_container', parent=self, align=Align.TOALL, padding=(0, 8, 0, 16))
        self.scroll_divider_top = DecoratedLine(name='scroll_divider_top', parent=outer_container, align=Align.TOTOP, color=eveThemeColor.THEME_ALERT)
        self.scroll_container = ScrollContainer(name='scroll_container', parent=outer_container, align=Align.TOALL, padding=(0, 16, 0, 16))
        self.content = ContainerAutoSize(name='content', parent=self.scroll_container, align=Align.CENTER, width=self.default_width - 16)
        self.scroll_divider_bottom = DecoratedLine(name='scroll_divider_bottom', parent=outer_container, align=Align.TOBOTTOM, color=eveThemeColor.THEME_ALERT)

    def construct_layout(self):
        self.construct_num_runs_input()
        self.construct_sections_header()
        self.construct_unlimited_use_section()
        self.construct_limited_use_section()
        self.construct_sequencing_time()
        self.construct_cost_info()

    def construct_num_runs_input(self):
        num_skins_cont = ContainerAutoSize(name='num_skins_cont', parent=self.content, align=Align.TOTOP)
        label_cont = ContainerAutoSize(name='label_cont', parent=num_skins_cont, align=Align.CENTERTOP, height=20)
        TextBody(parent=ContainerAutoSize(parent=label_cont, align=Align.TOLEFT), text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SkinAmount'), align=Align.CENTERLEFT)
        NumRunsInfoIcon(parent=ContainerAutoSize(parent=label_cont, align=Align.TOLEFT, padLeft=4), align=Align.CENTERLEFT)
        self.num_skins_edit = SingleLineEditInteger(name='num_skins_edit', parent=num_skins_cont, align=Align.CENTERTOP, density=Density.EXPANDED, top=32, width=96, minValue=1, maxValue=sequencing_util.get_maximum_runs_per_job(get_skill_service().GetMyLevel), setvalue=get_ship_skin_sequencing_svc().get_num_runs(), OnChange=self.on_num_skins_edit)

    def construct_sections_header(self):
        sections_header_container = Container(name='sections_header_container', parent=self.content, align=Align.TOTOP, height=32, padTop=32)
        TextBody(parent=sections_header_container, align=Align.CENTERLEFT, color=TextColor.SECONDARY, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ConsumablesRequired'))

    def construct_unlimited_use_section(self):
        unlimited_use_section_container = ContainerAutoSize(name='unlimited_use_section_container', parent=self.content, align=Align.TOTOP, padTop=8)
        ComponentTypeHeader(name='unlimited_use_section_header', parent=unlimited_use_section_container, align=Align.TOTOP, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/UnlimitedDesignElement'), icon=eveicon.infinity)
        self.unlimited_use_entry_container = ContainerAutoSize(name='unlimited_use_entry_container', parent=unlimited_use_section_container, align=Align.TOTOP)
        self.refresh_unlimited_use_entries()

    def refresh_unlimited_use_entries(self):
        if not self.unlimited_use_entry_container:
            return
        self.unlimited_use_entry_container.Flush()
        self.unlimited_sequence_binder_entries = []
        for type_id in SEQUENCE_BINDER_TYPES:
            entry = SequenceBinderCostEntry(parent=self.unlimited_use_entry_container, align=Align.TOTOP, type_id=type_id, pickState=PickState.ON, padTop=8)
            self.unlimited_sequence_binder_entries.append(entry)
            fitted_components = current_skin_design.get().get_fitted_components()
            for component in fitted_components:
                if type_id != component.sequence_binder_type_id:
                    continue
                component_license = component.get_component_license()
                if component_license and component_license.license_type != ComponentLicenseType.UNLIMITED:
                    continue
                if not component_license:
                    available_licenses = component.get_component_data().component_item_data_by_type_id.values()
                    limited_licenses = [ l for l in available_licenses if l.license_type == ComponentLicenseType.LIMITED ]
                    if len(limited_licenses) > 0:
                        continue
                UnlimitedComponentLicenseEntry(parent=self.unlimited_use_entry_container, align=Align.TOTOP, type_id=type_id, component=component, padTop=8)

            if type_id != SEQUENCE_BINDER_TYPES[-1]:
                DecoratedLine(parent=self.unlimited_use_entry_container, padTop=16, align=Align.TOTOP)

    def construct_limited_use_section(self):
        self.limited_use_section_container = ContainerAutoSize(name='limited_use_section_container', parent=self.content, align=Align.TOTOP, padTop=32)
        ComponentTypeHeader(name='limited_use_section_header', parent=self.limited_use_section_container, align=Align.TOTOP, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/LimitedDesignElement'), icon=eveicon.limited)
        self.limited_use_entry_container = ContainerAutoSize(name='limited_use_entry_container', parent=self.limited_use_section_container, align=Align.TOTOP)
        self.refresh_limited_use_entries()

    def refresh_limited_use_entries(self):
        if not self.limited_use_entry_container:
            return
        self.limited_use_entry_container.Flush()
        self.limited_sequence_binder_entries = []
        fitted_components = current_skin_design.get().get_fitted_components()
        if len(fitted_components) > 0:
            self.limited_use_section_container.display = True
            for component in fitted_components:
                component_license = component.get_component_license()
                if component_license and component_license.license_type != ComponentLicenseType.LIMITED:
                    continue
                if not component_license:
                    available_licenses = component.get_component_data().component_item_data_by_type_id.values()
                    limited_licenses = [ l for l in available_licenses if l.license_type == ComponentLicenseType.LIMITED ]
                    if len(limited_licenses) == 0:
                        continue
                if any([ e.component.component_id == component.component_id for e in self.limited_sequence_binder_entries ]):
                    continue
                entry = LimitedComponentLicenseEntry(parent=self.limited_use_entry_container, align=Align.TOTOP, component=component, padTop=8)
                self.limited_sequence_binder_entries.append(entry)

        else:
            self.limited_use_section_container.display = False

    def get_components_by_sequence_binder_type(self, license_type):
        components_by_type = {}
        fitted_components = current_skin_design.get().get_fitted_components()
        for component in fitted_components:
            component_license = component.get_component_license()
            if component_license is None or component_license.license_type != license_type:
                continue
            type_id = component.get_component_data().sequence_binder_type_id
            components_by_type[type_id] = components_by_type.get(type_id, component)

        return components_by_type

    def construct_sequencing_time_container(self):
        self.sequencing_time_container = Container(name='sequencing_time_container', parent=self, align=Align.TOBOTTOM, height=32, padBottom=4)

    def construct_sequencing_time(self):
        self.sequencing_time_container.Flush()
        self.sequencing_time = SequencingTime(name='sequencing_time', parent=self.sequencing_time_container, align=Align.TOTOP, minWidth=self.start_btn.width - 32)

    def construct_cost_info_container(self):
        self.cost_info_container = ContainerAutoSize(name='cost_info_container', parent=self, align=Align.TOBOTTOM, padBottom=4)

    def construct_cost_info(self):
        self.cost_info_container.Flush()
        self.cost_info = SequencingPanelCostInfo(name='cost_info', parent=self.cost_info_container, align=Align.TOBOTTOM, currency=Currency.PLEX)

    def construct_bottom_buttons(self):
        button_group = ButtonGroup(parent=self, align=Align.TOBOTTOM, button_alignment=AxisAlignment.CENTER, button_size_mode=ButtonSizeMode.STRETCH, density=Density.EXPANDED)
        self.start_btn = StartSequencingBtn(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/CreateSKIN'), func=self.on_start_sequencing_btn, variant=ButtonVariant.PRIMARY)
        button_group.add_button(self.start_btn)

    @uthread2.debounce(0.2)
    def update_values(self):
        self.kill_update_values_thread()
        self._update_values_thread = uthread2.start_tasklet(self._update_values_async)

    def _update_values_async(self):
        if self.destroyed:
            return
        svc = get_ship_skin_sequencing_svc()
        if self.sequencing_time:
            self.sequencing_time.update()
        if self.cost_info:
            try:
                plex_cost, discount = svc.get_sequencing_plex_price(current_skin_design.get(), svc.get_num_runs())
            except (GenericException, TimeoutException):
                ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
                plex_cost = 0

            self.cost_info.set_cost(plex_cost, discount)
        if self.num_skins_edit:
            self.num_skins_edit.SetMaxValue(sequencing_util.get_maximum_runs_per_job(get_skill_service().GetMyLevel))
        self.refresh_unlimited_use_entries()
        self.refresh_limited_use_entries()
        if self.start_btn:
            self.start_btn.update()

    @uthread2.debounce(0.5)
    def on_num_skins_edit(self, *args):
        self.kill_set_num_runs_thread()
        self._set_num_runs_thread = uthread2.start_tasklet(get_ship_skin_sequencing_svc().set_num_runs, self.number_of_skins)

    def on_num_skins_changed(self, *args):
        self.update_values()

    def on_sequence_binders_changed(self, *args):
        self.update_values()

    def on_component_instance_license_to_use_changed(self, *args):
        self.update_values()

    def on_component_license_granted(self, *args):
        self.update_values()

    def on_skin_sequencing_cache_invalidated(self, *args):
        self.update_values()

    def on_current_skin_design_name_changed(self, *args):
        self.update_values()

    def on_skill_levels_trained(self, *args):
        self.update_values()

    def on_size_changed_signal(self, *args):
        if self.scroll_container:
            is_scrolling = self.scroll_container.IsVerticalScrollBarVisible()
            self.scroll_divider_top.display = is_scrolling
            self.scroll_divider_bottom.display = is_scrolling

    def OnAurumChangeFromVgs(self, *args):
        self.update_values()

    def on_start_sequencing_btn(self, *args):
        self.on_sequencing_attempt()
        try:
            error = get_ship_skin_sequencing_svc().sequence_design(current_skin_design.get())
            if not error:
                current_skin_design.create_blank_design()
                current_page.reset_history()
                current_page.set_page_id(SkinrPage.STUDIO)
            else:
                label = SEQUENCING_ERROR_TEXT_BY_CODE.get(error, None)
                if label:
                    ShowQuickMessage(GetByLabel(label))
        finally:
            self.on_after_sequencing_attempt()

    def on_sequencing_attempt(self):
        if self.start_btn:
            self.start_btn.busy = True
            self.start_btn.disabled = True
        if self.num_skins_edit:
            self.num_skins_edit.Disable()

    def on_after_sequencing_attempt(self):
        if self.start_btn:
            self.start_btn.disabled = False
            self.start_btn.busy = False
            self.start_btn.update()
        if self.num_skins_edit:
            self.num_skins_edit.Enable()

    def _on_mock_sequencing_button_changed(self, *args):
        self.on_after_sequencing_attempt()

    @property
    def number_of_skins(self):
        return self.num_skins_edit.GetValue()


class StartSequencingBtn(Button):
    __notifyevents__ = ['OnSubscriptionChanged']
    errors = None

    def __init__(self, **kwargs):
        super(StartSequencingBtn, self).__init__(**kwargs)
        sm.RegisterNotify(self)

    def update(self):
        if current_page.get_page_id() != SkinrPage.STUDIO_SEQUENCING:
            return
        if is_sequencing_button_always_enabled.is_enabled():
            self.errors = []
        else:
            self.errors = get_ship_skin_sequencing_svc().validate_design_for_sequencing(current_skin_design.get())
        if self.errors:
            self.style = ButtonStyle.DANGER
        else:
            self.style = ButtonStyle.NORMAL

    def OnSubscriptionChanged(self):
        self.update()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if not self.errors:
            return
        if self.busy:
            return
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 1
        tooltipPanel.AddMediumHeader(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/UnableToStartSequencingJob'), wrapWidth=300)
        for error in self.errors:
            label = SEQUENCING_ERROR_TEXT_BY_CODE.get(error, None)
            if label:
                tooltipPanel.AddLabelMedium(text=GetByLabel(label), wrapWidth=300, color=eveColor.DANGER_RED)

    def _CallFunction(self):
        if self.errors:
            return
        else:
            return super(StartSequencingBtn, self)._CallFunction()


class ComponentTypeHeader(Container):
    default_height = 29

    def __init__(self, text, icon, *args, **kwargs):
        super(ComponentTypeHeader, self).__init__(*args, **kwargs)
        self.text = text
        self.icon = icon
        self.construct_layout()

    def construct_layout(self):
        Fill(bgParent=self, color=eveColor.TUNGSTEN_GREY, opacity=0.1)
        TextHeader(parent=self, align=Align.CENTERLEFT, text=self.text, padLeft=8)
        icon_container = Container(parent=self, align=Align.TORIGHT, width=16, padRight=8)
        Sprite(parent=icon_container, align=Align.CENTER, texturePath=self.icon, pos=(0, 0, 16, 16))
