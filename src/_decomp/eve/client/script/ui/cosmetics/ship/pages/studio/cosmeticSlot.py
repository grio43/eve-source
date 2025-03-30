#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\cosmeticSlot.py
import eveicon
import evetypes
import gametime
import math
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui import Align, uiconst, PickState, SpriteEffect
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.loggers.buttonLogger import log_button_clicked
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uiconst import OutputMode
from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
from cosmetics.client.shipSkinSequencingSvc import get_ship_skin_sequencing_svc
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.ships.skins.live_data import current_skin_design_signals, current_skin_design
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from cosmetics.common.ships.skins.static_data.slot_name import PATTERN_SLOT_IDS, PATTERN_SLOT_ID_BY_PATTERN_MATERIAL_ID
from eve.client.script.ui import eveThemeColor, eveColor
from eve.client.script.ui.cosmetics.ship import const as shipConst
from eve.client.script.ui.cosmetics.ship.pages.sequence import sequence_ui_signals
from eve.client.script.ui.cosmetics.ship.pages.studio.licenseSelector import LicenseSelector
from eve.client.script.ui.cosmetics.ship.pages.studio.radiallyAlignedMixin import RadiallyAlignedMixin
from eve.client.script.ui.cosmetics.ship.pages.studio.requiredComponentTooltipPanel import RequiredComponentTooltipPanel
from eveservices.menu import GetMenuService
from localization import GetByLabel
from signals import Signal
OPACITY_FRAME_IDLE = 0.1
OPACITY_FRAME_HOVER = 0.2
OPACITY_FRAME_SELECTED = 0.3

def get_frame_color(showing_warning):
    if showing_warning:
        return eveColor.DANGER_RED
    else:
        return eveThemeColor.THEME_FOCUSDARK


def get_side_frame_color(showing_warning):
    return eveThemeColor.THEME_FOCUSDARK


def get_anim_time_offset(duration):
    seconds = gametime.GetWallclockTimeNow() / float(gametime.SEC)
    return duration - seconds % duration


class CosmeticSlotButton(Container, RadiallyAlignedMixin):
    default_width = 64
    default_height = 64
    default_state = uiconst.UI_NORMAL
    default_align = Align.CENTER
    analyticID = None

    def __init__(self, texture_path = None, icon_size = 32, is_selectable = True, **kw):
        super(CosmeticSlotButton, self).__init__(**kw)
        self.is_selectable = is_selectable
        self.is_selected = False
        self.is_hovered = False
        self.showing_warning = False
        self.construct_icon(texture_path, icon_size)
        self.construct_hover_frame()
        self.construct_frame()
        self.on_click = Signal('on_click')
        self.on_mouse_enter = Signal('on_mouse_enter')
        self.on_mouse_exit = Signal('on_mouse_exit')
        self.on_selected = Signal('on_selected')
        self.on_deselected = Signal('on_deselected')

    def OnClick(self, *args):
        self.on_click()
        log_button_clicked(self)

    def OnMouseEnter(self, *args):
        self.is_hovered = True
        self.update_state()
        self.on_mouse_enter()

    def OnMouseExit(self, *args):
        self.is_hovered = False
        self.update_state()
        self.on_mouse_exit()

    def construct_icon(self, texture_path, icon_size):
        self.icon = Sprite(name='icon', parent=self, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath=texture_path, pos=(0,
         0,
         icon_size,
         icon_size))
        Sprite(bgParent=self, texturePath='res:/UI/Texture/circle_full.png', padding=8, color=eveThemeColor.THEME_FOCUSDARK, opacity=0.2)
        Sprite(bgParent=self, texturePath='res:/UI/Texture/circle_full.png', padding=8, color=eveColor.BLACK, opacity=0.4)

    def construct_hover_frame(self):
        self.hover_frame = Transform(parent=self, align=Align.TOALL, pickState=PickState.OFF, padding=4, opacity=0.0, scalingCenter=(0.5, 0.5))
        self.hover_frame_sprite = Sprite(name='hover_frame_sprite', bgParent=self.hover_frame, texturePath='res:/UI/Texture/Classes/Cosmetics/Ship/Pages/Studio/slot_hover_frame.png', outputMode=OutputMode.COLOR_AND_GLOW, glowBrightness=0.2, color=eveThemeColor.THEME_ACCENT)

    def construct_frame(self):
        self.frame = Transform(name='frame', parent=self, align=Align.TOALL, pickState=PickState.OFF, padding=-6, opacity=OPACITY_FRAME_IDLE, scalingCenter=(0.5, 0.5))
        self.frame_bg = Sprite(bgParent=self.frame, texturePath='res:/UI/Texture/Classes/Cosmetics/Ship/Pages/Studio/slot_frame.png', outputMode=OutputMode.COLOR_AND_GLOW, glowBrightness=0.2, color=get_frame_color(self.showing_warning))

    def set_selected(self):
        self.is_selected = True
        self.on_selected()

    def set_deselected(self):
        self.is_selected = False
        self.on_deselected()

    def update_state(self, animate = True):
        self._update_state_frame(animate)
        self._update_state_hover_frame(animate)

    def _update_state_hover_frame(self, animate):
        opacity = 1.0 if self.is_selected else 0.0
        if self.is_selected:
            scale = (1.0, 1.0)
        else:
            scale = (0.7, 0.7)
        if animate:
            animations.FadeTo(self.hover_frame, self.hover_frame.opacity, opacity, duration=2 * uiconst.TIME_ENTRY)
            animations.MorphVector2(self.hover_frame, 'scale', self.hover_frame.scale, scale, duration=2 * uiconst.TIME_ENTRY)
        else:
            self.hover_frame.opacity = opacity
            self.hover_frame.scale = scale

    def _update_state_frame(self, animate = True):
        if self.is_selected:
            opacity = OPACITY_FRAME_SELECTED
        elif self.is_hovered:
            opacity = OPACITY_FRAME_HOVER
        else:
            opacity = OPACITY_FRAME_IDLE
        rotation = 0.0 if self.is_hovered or self.is_selected else -math.pi / 2
        scale = (1.06, 1.06) if self.is_selected else (1.0, 1.0)
        self.frame_bg.rgb = get_frame_color(self.showing_warning)[:3]
        if animate:
            animations.FadeTo(self.frame, self.frame.opacity, opacity, duration=uiconst.TIME_ENTRY)
            animations.MorphScalar(self.frame, 'rotation', self.frame.rotation, rotation, duration=0.15)
            animations.MorphVector2(self.frame, 'scale', self.frame.scale, scale, duration=0.15)
        else:
            self.frame.opacity = opacity
            self.frame.rotation = rotation
            self.frame.scale = scale


class CosmeticSlot(Container, RadiallyAlignedMixin):
    default_width = 256
    default_height = 256
    default_align = Align.CENTER
    default_pickState = PickState.CHILDREN
    default_display = True
    _radial_offset = 20
    has_side_frame = True
    showing_warning = False

    def __init__(self, slot_data, component = None, selectable = True, license_selector_align = Align.CENTERBOTTOM, *args, **kwargs):
        super(CosmeticSlot, self).__init__(*args, **kwargs)
        self.slot_data = slot_data
        self.is_selectable = selectable
        self._selected_component = component
        self._license_selector_align = license_selector_align
        self.construct_layout()
        self.connect_signals()
        self.update_icon()
        self.update_warning()
        self._update_state(animate=False)

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(CosmeticSlot, self).Close()

    def connect_signals(self):
        current_skin_design_signals.on_slot_selected.connect(self.on_slot_selected)
        current_skin_design_signals.on_slot_fitting_changed.connect(self.on_slot_fitting_changed)
        sequence_ui_signals.on_num_skins_changed.connect(self.on_num_skins_changed)
        sequence_ui_signals.on_component_license_selection_changed.connect(self.on_component_license_selection_changed)
        ship_skin_signals.on_component_license_granted.connect(self.on_component_license_granted)
        ship_skin_signals.on_component_license_cache_invalidated.connect(self.on_component_license_cache_invalidated)

    def disconnect_signals(self):
        current_skin_design_signals.on_slot_selected.disconnect(self.on_slot_selected)
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.on_slot_fitting_changed)
        sequence_ui_signals.on_num_skins_changed.disconnect(self.on_num_skins_changed)
        sequence_ui_signals.on_component_license_selection_changed.disconnect(self.on_component_license_selection_changed)
        ship_skin_signals.on_component_license_granted.disconnect(self.on_component_license_granted)
        ship_skin_signals.on_component_license_cache_invalidated.disconnect(self.on_component_license_cache_invalidated)

    def on_num_skins_changed(self, num_skins):
        self._check_show_not_owned_warning()
        self.update_warning()

    def on_component_license_selection_changed(self):
        self._check_show_not_owned_warning()
        self.update_warning()

    def on_component_license_granted(self, *args):
        self._check_show_not_owned_warning()
        self.update_warning()

    def on_component_license_cache_invalidated(self, _licenses_flushed):
        self._check_show_not_owned_warning()
        self.update_warning()

    def construct_layout(self):
        self.construct_button()
        if self.has_side_frame:
            self.construct_side_frame()
        self.construct_license_selector()
        self.construct_pulse_highlight()

    def construct_button(self):
        self.button = CosmeticSlotButton(parent=self, align=Align.CENTER, is_selectable=self.is_selectable)
        if self.slot_data.unique_id in PATTERN_SLOT_IDS:
            mask_texture = 'res:/UI/Texture/circle_full.png'
        else:
            mask_texture = 'res:/UI/Texture/classes/Cosmetics/Ship/pages/studio/nanocoating_mask.png'
        self.button.icon.spriteEffect = SpriteEffect.MODULATE
        self.button.icon.SetSecondaryTexturePath(mask_texture)
        self.button.on_click.connect(self.OnSlotClick)
        self.button.on_mouse_enter.connect(self.OnSlotMouseEnter)
        self.button.on_mouse_exit.connect(self.OnSlotMouseExit)
        self.button.on_selected.connect(self.on_button_selected)
        self.button.on_deselected.connect(self.on_button_deselected)
        self.button.GetMenu = self.GetSlotMenu
        self.button.ConstructTooltipPanel = self.ConstructButtonTooltipPanel

    def ConstructButtonTooltipPanel(self, *args):
        return RequiredComponentTooltipPanel(component_instance=self.selected_component, title=self.slot_data.name, text=self.get_fitted_component_name(), show_warning=self.showing_warning)

    def get_fitted_component_name(self):
        if self.selected_component:
            return self.selected_component.get_component_data().name
        else:
            return GetByLabel('UI/OrbitalSkyhook/ConfigWnd/NothingSelected')

    def on_button_selected(self):
        self._update_state()

    def on_button_deselected(self):
        self._update_state()

    def construct_side_frame(self):
        self.side_frame = Container(name='side_frame', parent=self, align=Align.CENTER, pickState=PickState.OFF, pos=(-54, 0, 39, 36))
        Sprite(parent=self.side_frame, pos=(-2, 0, 24, 24), align=Align.CENTER, texturePath=shipConst.SLOT_ICONS[self.slot_data.unique_id])
        self.side_frame_bg = Sprite(bgParent=self.side_frame, texturePath='res:/UI/Texture/Classes/Cosmetics/Ship/Pages/Studio/slot_side_frame.png', color=get_side_frame_color(self.showing_warning), glowBrightness=0.2, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW)

    def construct_license_selector(self):
        if self._license_selector_align == Align.CENTERTOP:
            align = Align.CENTER
            left = 0
            top = -53
        elif self._license_selector_align == Align.CENTERBOTTOM:
            align = Align.CENTER
            left = 0
            top = 53
        elif self._license_selector_align == Align.CENTERLEFT:
            align = Align.CENTERRIGHT
            left = 174
            top = 0
        elif self._license_selector_align == Align.CENTERRIGHT:
            align = Align.CENTERLEFT
            left = 174
            top = 0
        self.license_selector_container = ContainerAutoSize(name='license_selector_container', parent=self, align=align, height=20, left=left, top=top, display=False)
        self.license_selector = LicenseSelector(name='license_selector', parent=self.license_selector_container, component_instance=self.selected_component)

    def construct_pulse_highlight(self):
        self.pulse_highlight = Transform(name='pulse_highlight', parent=self, align=Align.CENTER, pickState=PickState.OFF, scalingCenter=(0.5, 0.5), pos=(0, 0, 120, 120), display=False)
        self.pulse_highlight_bg = Sprite(bgParent=self.pulse_highlight, texturePath='res:/UI/Texture/Classes/Cosmetics/Ship/Pages/Studio/slot_pulse_highlight.png')

    def show_pulse_highlight(self):
        self.pulse_highlight.display = True
        scale_contracted = (0.85, 0.85)
        scale_expanded = (1.1, 1.1)
        duration = 5.0
        animation_curve = ((0.0, scale_contracted),
         (0.5 / duration, scale_contracted),
         (2.5 / duration, scale_expanded),
         (3.0 / duration, scale_expanded),
         (1.0, scale_contracted))
        animations.MorphVector2(obj=self.pulse_highlight, attrName='scale', duration=5.0, curveType=animation_curve, loops=uiconst.ANIM_REPEAT, timeOffset=get_anim_time_offset(5.0))

    def hide_pulse_highlight(self):
        animations.StopAllAnimations(self.pulse_highlight_bg)
        self.pulse_highlight.display = False

    def show_warning(self):
        self.showing_warning = True
        self.button.showing_warning = True
        self._update_state()

    def hide_warning(self):
        self.showing_warning = False
        self.button.showing_warning = False
        self._update_state()

    def update_warning(self):
        if not self.selected_component:
            return
        layout = current_skin_design.get().slot_layout
        number_of_runs = get_ship_skin_sequencing_svc().get_num_runs()
        num_required = number_of_runs * layout.get_amount_of_components_with_license_type(self.selected_component.component_id, ComponentLicenseType.LIMITED)
        license = self.selected_component.component_license_to_use or get_ship_skin_component_svc().get_default_license_to_use(self.selected_component.component_id, self.selected_component.get_component_data().category)
        if license is None:
            has_sufficient_licenses = True
        elif license.license_type == ComponentLicenseType.LIMITED:
            has_sufficient_licenses = license is None or not license.has_enough_remaining_uses(num_required)
        else:
            has_sufficient_licenses = False
        if has_sufficient_licenses:
            self.show_warning()
        else:
            self.hide_warning()

    def on_slot_selected(self, slot_id):
        if slot_id and slot_id == self.slot_data.unique_id:
            self.button.set_selected()
        else:
            self.button.set_deselected()

    def _update_state(self, animate = True):
        self.button.update_state(animate)
        if self.has_side_frame:
            self._update_state_side_frame(animate)
        self._update_state_license_selector()

    def _update_state_side_frame(self, animate):
        if not self.is_fitted:
            opacity = 0.0
        elif self.is_selected:
            opacity = OPACITY_FRAME_SELECTED
        elif self.button.is_hovered:
            opacity = OPACITY_FRAME_HOVER
        else:
            opacity = OPACITY_FRAME_IDLE
        self.side_frame_bg.rgb = get_side_frame_color(self.showing_warning)[:3]
        if animate:
            animations.FadeTo(self.side_frame_bg, self.side_frame_bg.opacity, opacity, duration=2 * uiconst.TIME_ENTRY)
        else:
            self.side_frame_bg.opacity = opacity
        opacity = 1.0 if opacity > 0 else 0.0
        if animate:
            animations.FadeTo(self.side_frame, self.side_frame.opacity, opacity, duration=2 * uiconst.TIME_ENTRY)
        else:
            self.side_frame.opacity = opacity

    def _update_state_license_selector(self):
        if self.license_selector:
            self.license_selector.component_instance = self.selected_component
            self.license_selector_container.display = self.selected_component is not None and self.is_selected

    @property
    def is_selected(self):
        return current_skin_design.get_selected_slot_id() == self.slot_data.unique_id

    def on_slot_fitting_changed(self, slot_id, component_instance):
        self._check_show_not_owned_warning()
        if slot_id != self.slot_data.unique_id:
            return
        self.selected_component = component_instance
        self.update_icon()
        self._update_state()

    def _check_show_not_owned_warning(self):
        if not self.selected_component:
            self.hide_warning()
            return
        license = self.selected_component.component_license_to_use or get_ship_skin_component_svc().get_default_license_to_use(self.selected_component.component_id, self.selected_component.get_component_data().category)
        if not license:
            self.show_warning()
            return
        if license.license_type == ComponentLicenseType.UNLIMITED:
            self.hide_warning()
            return
        layout = current_skin_design.get().slot_layout
        number_of_runs = get_ship_skin_sequencing_svc().get_num_runs()
        num_required = number_of_runs * layout.get_amount_of_components_with_license_type(self.selected_component.component_id, ComponentLicenseType.LIMITED)
        if license.has_enough_remaining_uses(num_required):
            self.hide_warning()
        else:
            self.show_warning()

    def update_icon(self):
        if self.selected_component:
            self.button.icon.texturePath = self.selected_component.get_component_data().icon_file_path
            self.button.icon.width = self.button.icon.height = 48
        else:
            self.button.icon.texturePath = shipConst.SLOT_ICONS[self.slot_data.unique_id]
            self.button.icon.width = self.button.icon.height = 32

    @property
    def is_fitted(self):
        return bool(self.selected_component)

    def OnSlotClick(self, *args):
        if not self.is_selectable:
            return
        PlaySound('nanocoating_button_push_primary_play')
        selected_slot = None if self.is_selected else self.slot_data
        current_skin_design.set_selected_slot_id(selected_slot.unique_id if selected_slot else None)

    def OnSlotMouseEnter(self, *args):
        if not self.is_selectable:
            return
        PlaySound('nanocoating_button_hover_play')
        self._update_state()

    def OnSlotMouseExit(self, *args):
        if not self.is_selectable:
            return
        self._update_state()

    @property
    def selected_component(self):
        return current_skin_design.get().get_fitted_component_instance(self.slot_data.unique_id)

    @selected_component.setter
    def selected_component(self, value):
        self._selected_component = value
        self._update_state()
        if value:
            animations.MorphScalar(self.button.hover_frame_sprite, 'glowBrightness', 2.0, 0.0, duration=1.2)

    def GetSlotMenu(self):
        if not self.selected_component:
            return
        component_data = self.selected_component.get_component_data()
        m = MenuData()
        for type_id in component_data.component_item_data_by_type_id.keys():
            m.AddEntry(evetypes.GetName(type_id), subMenuData=GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=type_id, includeMarketDetails=True))

        if self.is_fitted and self.slot_data.unique_id not in PATTERN_SLOT_ID_BY_PATTERN_MATERIAL_ID.keys():
            m.AddSeparator()
            m.AddEntry(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ResetSlot'), self.unfit_slot, texturePath=eveicon.close)
        if self.slot_data.unique_id in PATTERN_SLOT_IDS:
            component_instance = current_skin_design.get().get_fitted_component_instance(self.slot_data.unique_id)
            if component_instance:
                m.AddSeparator()
                m.AddEntry(GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ResetPatternProjection'), lambda c = component_instance: self.reset_pattern_rotation_scale_and_offset(c), texturePath=eveicon.refresh)
        if session.role & ROLE_GML:
            m.AddSeparator()
            component_id = self.selected_component.component_id if self.selected_component else None
            m.AddEntry('QA: slot_id: {}, component_id: {}'.format(self.slot_data.unique_id, component_id))
        return m

    def reset_pattern_rotation_scale_and_offset(self, component_instance):
        component_instance.reset_rotation_scale_and_offset()
        current_skin_design.add_to_undo_history()

    def unfit_slot(self, *args):
        current_skin_design.get().fit_slot(self.slot_data.unique_id, None)
        current_skin_design.add_to_undo_history()

    def show(self):
        self.state = uiconst.UI_PICKCHILDREN
        animations.FadeTo(self, self.opacity, 1.0, 0.2)

    def hide(self):
        self.state = uiconst.UI_DISABLED
        animations.FadeTo(self, self.opacity, 0.0, 0.25)


class PatternCosmeticSlot(CosmeticSlot):
    has_side_frame = False
