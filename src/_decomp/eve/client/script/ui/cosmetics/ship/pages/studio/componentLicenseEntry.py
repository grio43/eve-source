#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\componentLicenseEntry.py
import blue
import gametime
from carbonui.uiconst import OutputMode
import carbonui
import evetypes
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui import Align, uiconst, PickState, SpriteEffect
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from cosmetics.client.ships.skins.static_data import rarity_icon
from cosmetics.common.ships.skins.static_data.component import projection_type_to_fsd
from cosmetics.common.ships.skins.static_data.component_category import ComponentCategory
from cosmetics.common.ships.skins.static_data.slot_name import SlotID, PATTERN_MATERIAL_SLOT_ID_BY_PATTERN_ID, PATTERN_SLOT_IDS
from eve.client.script.ui import eveThemeColor, eveColor
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.cosmetics.ship.controls.rarityIndicator import RarityIndicator
from eveservices.menu import GetMenuService
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException
ICON_SIZE = 48
TOOLTIP_ICON_SIZE = 128
PADDING = 14

def get_anim_time_offset(duration):
    seconds = gametime.GetWallclockTimeNow() / float(gametime.SEC)
    return duration - seconds % duration


brightness_blink_curve = ((0.0, 0.0),
 (2 / 7.0, 1.5),
 (4 / 7.0, 1.5),
 (6 / 7.0, 0.0),
 (1.0, 0.0))

class ComponentEntry(Container):
    default_width = ICON_SIZE + PADDING
    default_height = ICON_SIZE + PADDING
    default_state = uiconst.UI_NORMAL

    def __init__(self, component_data, slot_id, is_selected, limited_license = None, unlimited_license = None, *args, **kwargs):
        super(ComponentEntry, self).__init__(*args, **kwargs)
        self.limited_license = limited_license
        self.unlimited_license = unlimited_license
        self.slot_id = slot_id
        self._is_selected = is_selected
        self.component_data = component_data
        self.is_new = False
        self.is_animating = False
        self.construct_layout()
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(ComponentEntry, self).Close()

    def connect_signals(self):
        current_skin_design_signals.on_slot_fitting_changed.connect(self.on_slot_fitting_changed)
        current_skin_design_signals.on_pattern_blend_mode_changed.connect(self.on_blend_mode_changed)

    def disconnect_signals(self):
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.on_slot_fitting_changed)
        current_skin_design_signals.on_pattern_blend_mode_changed.disconnect(self.on_blend_mode_changed)

    def on_blend_mode_changed(self, *args):
        self._check_fit_default_pattern_material()

    def construct_layout(self):
        self.construct_icon()
        self.construct_selection_frame()
        self.check_construct_not_owned_frame()
        self.update()

    def check_construct_not_owned_frame(self):
        if not self.limited_license and not self.unlimited_license:
            self.not_owned_frame = Sprite(name='not_owned_frame', parent=self, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/circle_frame_bg.png', color=eveColor.WHITE, opacity=0.2, align=Align.TOALL, pickState=PickState.OFF)

    def construct_icon(self):
        if self.is_pattern():
            size = ICON_SIZE - 2
        else:
            size = ICON_SIZE
        self.icon = Sprite(name='icon', parent=self, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath=self.component_data.icon_file_path, textureSecondaryPath=self.icon_mask_texture, spriteEffect=SpriteEffect.MASK, pos=(0,
         0,
         size,
         size))

    def construct_selection_frame(self):
        self.selection_frame = Sprite(name='selection_frame', parent=self, texturePath='res:/UI/Texture/Classes/Cosmetics/Ship/circle_frame.png', align=Align.TOALL, pickState=PickState.OFF, glowBrightness=0.0)

    def update(self):
        self.is_new = get_ship_skin_component_svc().is_component_new(self.component_data.component_id)
        if self.is_selected and self.is_new:
            get_ship_skin_component_svc().set_component_is_new_flag(self.component_data.component_id, False)
            self.is_new = False
        self.selection_frame.display = self.is_selected or self.is_new
        if self.is_new:
            self.selection_frame.color = eveColor.DUSKY_ORANGE
            self.selection_frame.outputMode = uiconst.OUTPUT_COLOR_AND_GLOW
        else:
            self.selection_frame.color = eveThemeColor.THEME_ACCENT
            self.selection_frame.outputMode = self.selection_frame.default_outputMode
        if self.is_new:
            if not self.is_animating:
                self.start_new_highlight_animation()
        else:
            self.stop_new_highlight_animation()

    def start_new_highlight_animation(self):
        self.is_animating = True
        animations.MorphScalar(obj=self.selection_frame, attrName='glowBrightness', duration=2.5, loops=uiconst.ANIM_REPEAT, curveType=brightness_blink_curve, timeOffset=get_anim_time_offset(2.5))

    def on_new_highlight_animation_out_complete(self, *args):
        if self.is_new:
            self.start_new_highlight_animation()

    def stop_new_highlight_animation(self):
        animations.StopAnimation(self.selection_frame, 'glowBrightness')
        self.selection_frame.glowBrightness = 0.0
        self.is_animating = False

    def on_slot_fitting_changed(self, slot_id, component_instance):
        if slot_id != self.slot_id:
            return
        self.is_selected = component_instance and component_instance.component_id == self.component_data.component_id

    def OnClick(self, *args):
        get_ship_skin_component_svc().set_component_is_new_flag(self.component_data.component_id, False)
        if self.slot_id in (SlotID.PATTERN_MATERIAL, SlotID.SECONDARY_PATTERN_MATERIAL):
            if not self.is_selected:
                self.set_selected()
                current_skin_design.add_to_undo_history()
        else:
            self.toggle_selected()
            current_skin_design.add_to_undo_history()

    def is_pattern(self):
        return self.slot_id in PATTERN_SLOT_IDS

    def toggle_selected(self):
        if self.is_selected:
            self.set_deselected()
        else:
            self.set_selected()

    def set_selected(self):
        current_skin_design.get().fit_slot(self.slot_id, self.component_data.component_id, None)
        if self.is_pattern():
            self._check_fit_default_pattern_material()

    def set_deselected(self):
        current_skin_design.get().fit_slot(self.slot_id, None)

    def _check_fit_default_pattern_material(self):
        material_slot_id = PATTERN_MATERIAL_SLOT_ID_BY_PATTERN_ID.get(self.slot_id, None)
        if not material_slot_id or current_skin_design.get().get_fitted_component_instance(material_slot_id):
            return
        if not current_skin_design.get().get_fitted_component_instance(self.slot_id):
            return
        try:
            component_license = get_ship_skin_component_svc().get_random_component_license(material_slot_id)
            if component_license:
                current_skin_design.get().fit_slot(material_slot_id, component_license.component_id, component_license)
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))

    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value):
        self._is_selected = value
        self.update()

    def ConstructTooltipPanel(self):
        return ComponentEntryTooltipPanel(self.component_data, self.icon_mask_texture)

    @property
    def icon_mask_texture(self):
        if self.is_pattern():
            return 'res:/UI/Texture/circle_full.png'
        else:
            return 'res:/UI/Texture/classes/Cosmetics/Ship/pages/studio/nanocoating_mask.png'

    def GetMenu(self):
        m = MenuData()
        for type_id in self.component_data.component_item_data_by_type_id.keys():
            m.AddEntry(evetypes.GetName(type_id), subMenuData=GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=type_id, includeMarketDetails=True))

        if session.role & ROLE_GML:
            m.AddEntry('QA:', subMenuData=self.get_qa_menu())
        return m

    def get_qa_menu(self):
        m = MenuData()
        m.AddEntry(text='component_id: {}'.format(self.component_data.component_id), func=lambda *x: blue.pyos.SetClipboardData(str(self.component_data.component_id)))
        m.AddEntry(text='icon_path: {}'.format(self.component_data.icon_file_path), func=lambda *x: blue.pyos.SetClipboardData(str(self.component_data.icon_file_path)))
        import webbrowser
        m.AddEntry(text='Show in FSD editor', func=lambda : webbrowser.open_new('http://localhost:8000/cfsd/projects/cosmetic/ship_skin_design_components/ship_skin_design_components/{}/edit/'.format(self.component_data.component_id)))
        for license in (self.limited_license, self.unlimited_license):
            if not license:
                continue
            m.AddEntry(text='license_type: {}'.format(license.license_type), func=lambda *x: blue.pyos.SetClipboardData(str(license.license_type)))
            component_type_id = None
            for type_id, data in self.component_data.component_item_data_by_type_id.items():
                if data.license_type == license.license_type:
                    component_type_id = type_id
                    break

            m.AddEntry(text='type_id: {}'.format(component_type_id), func=lambda *x: blue.pyos.SetClipboardData(str(component_type_id)))

        m.AddEntry(text='Points Value: %s' % self.component_data.points_value)
        if self.component_data.projection_type_uv:
            u_fmt = projection_type_to_fsd(self.component_data.projection_type_uv[0])
            v_fmt = projection_type_to_fsd(self.component_data.projection_type_uv[1])
            m.AddEntry('Projection Type U: %s' % u_fmt)
            m.AddEntry('Projection Type V: %s' % v_fmt)
        return m


class TooltipCard(Container):
    default_width = 130
    default_height = 135

    def __init__(self, component_data, **kw):
        super(TooltipCard, self).__init__(**kw)
        self.construct_icon(component_data)
        self.construct_background()

    def construct_icon(self, component_data):
        icon_cont = Container(parent=self, align=Align.CENTERTOP, pos=(0, 12, 94, 94))
        if component_data.category == ComponentCategory.PATTERN:
            Sprite(parent=icon_cont, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath=component_data.icon_file_path, pos=(0, 0, 80, 80))
            Fill(parent=icon_cont, align=Align.CENTER, state=uiconst.UI_DISABLED, color=eveThemeColor.THEME_TINT, opacity=0.5, pos=(0, 0, 92, 92))
        else:
            Sprite(parent=icon_cont, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath=component_data.icon_file_path, textureSecondaryPath='res:/UI/Texture/classes/Cosmetics/Ship/pages/studio/nanocoating_mask.png', spriteEffect=SpriteEffect.MASK, pos=(0, 0, 80, 80))
            Sprite(parent=icon_cont, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/circle_full.png', color=eveThemeColor.THEME_TINT, opacity=0.5, pos=(0, 0, 92, 92))

    def construct_background(self):
        Sprite(parent=self, align=Align.HORIZONTALLY_CENTERED, width=120, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/Cards/Tooltip/outline.png', color=eveColor.WHITE, opacity=0.2)
        Sprite(parent=self, align=Align.HORIZONTALLY_CENTERED, width=130, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/Cards/Tooltip/bg_overlay.png', color=eveThemeColor.THEME_FOCUSDARK, opacity=0.3)
        Sprite(parent=self, align=Align.HORIZONTALLY_CENTERED, width=120, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/Cards/Tooltip/bg_fill.png', color=eveColor.BLACK, opacity=0.9)


class ComponentEntryTooltipPanel(TooltipPanel):
    default_margin = 0
    default_cellPadding = 0
    default_cellSpacing = (0, 4)

    def __init__(self, component_data, icon_mask_texture, **kw):
        super(ComponentEntryTooltipPanel, self).__init__(**kw)
        self.columns = 1
        self.construct_header(component_data)
        TooltipCard(parent=self, component_data=component_data, align=Align.CENTER, pickState=PickState.OFF)
        self.SetBackgroundAlpha(0.0)

    def construct_header(self, component_data):
        layout_grid = LayoutGrid(parent=self, columns=1, align=Align.CENTERTOP, cellSpacing=(8, 8), margin=(16, 16, 16, 8))
        license = get_ship_skin_component_svc().get_default_license_to_use(component_data.component_id, component_data.category)
        is_new = get_ship_skin_component_svc().is_component_new(component_data.component_id)
        if not license:
            carbonui.TextBody(parent=layout_grid, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/NotInYourCollection'), color=eveColor.HOT_RED)
        elif is_new:
            carbonui.TextBody(parent=layout_grid, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/NewInYourCollection'), color=eveColor.DUSKY_ORANGE)
        carbonui.TextHeader(parent=layout_grid, text=component_data.name, maxWidth=160)
        rarity_cont = ContainerAutoSize(parent=layout_grid)
        RarityIndicator(parent=rarity_cont, rarity=component_data.rarity, align=Align.CENTERLEFT)
        carbonui.TextBody(parent=rarity_cont, align=Align.CENTERLEFT, left=40, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/RarityName', rarity=GetByLabel(rarity_icon.get_name(component_data.rarity))), wrapWidth=300)
        if is_new:
            frame = Frame(bgParent=layout_grid, align=Align.HORIZONTALLY_CENTERED, width=120, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/Cards/Tooltip/frame_textbox.png', color=eveColor.DUSKY_ORANGE, opacity=1.0, outputMode=OutputMode.COLOR_AND_GLOW, glowBrightness=0.0, cornerSize=16)
            animations.MorphScalar(obj=frame, attrName='glowBrightness', duration=2.5, curveType=brightness_blink_curve, loops=uiconst.ANIM_REPEAT, timeOffset=get_anim_time_offset(2.5))
        else:
            Frame(bgParent=layout_grid, align=Align.HORIZONTALLY_CENTERED, width=120, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/Cards/Tooltip/frame_textbox.png', color=eveColor.WHITE, opacity=0.2, cornerSize=16)
        Frame(bgParent=layout_grid, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/Cards/Tooltip/bg_textbox.png', color=eveThemeColor.THEME_FOCUSDARK, opacity=0.2, cornerSize=16)
        Frame(bgParent=layout_grid, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/Cards/Tooltip/bg_textbox.png', color=eveColor.BLACK, opacity=0.9, cornerSize=16)
