#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\areaToggleButtonMenuIcon.py
from carbonui.control.contextMenu.menuUtil import ClearMenuLayer
from carbonui.text.color import TextColor
from carbonui import uiconst
from carbonui.uianimations import animations
from carbonui.text.styles import TextBody
from carbonui.uiconst import Align
import eveicon
from carbonui.control.contextMenu.contextMenuMixin import ContextMenuMixin
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from eve.client.script.ui import eveColor
from eve.client.script.ui.cosmetics.ship.pages.studio.circularButtonIcon import CircularMenuButtonIcon
from localization import GetByLabel

class AreaToggleButtonMenuIcon(CircularMenuButtonIcon):
    default_texturePath = eveicon.ship_areas
    default_hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/PatternAreaApplication')

    def __init__(self, slot_id, *args, **kwargs):
        super(AreaToggleButtonMenuIcon, self).__init__(*args, **kwargs)
        self.slot_id = slot_id
        self.menu = None
        self.update_selected()
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(AreaToggleButtonMenuIcon, self).Close()

    def disconnect_signals(self):
        current_skin_design_signals.on_component_attribute_changed.disconnect(self.on_current_design_component_attribute_changed)

    def connect_signals(self):
        current_skin_design_signals.on_component_attribute_changed.connect(self.on_current_design_component_attribute_changed)

    def on_current_design_component_attribute_changed(self, *args):
        self.update_selected()

    def OnMouseUp(self, *args):
        if self.has_open_menu():
            return
        ClearMenuLayer()
        left, top, width, height = self.GetAbsolute()
        self.menu = AreaToggleButtonMenu(parent=uicore.layer.menu, left=left - AreaToggleButtonMenu.default_width - 16, top=top - (AreaToggleButtonMenu.default_height - height) / 2.0, slot_id=self.slot_id)

    def GetHint(self):
        if self.has_open_menu():
            return None
        return super(AreaToggleButtonMenuIcon, self).GetHint()

    def has_open_menu(self):
        return self.menu and not self.menu.destroyed

    def get_component_instance(self):
        component_instance = current_skin_design.get().get_fitted_component_instance(self.slot_id)
        return component_instance

    def is_all_areas_enabled(self):
        component_instance = self.get_component_instance()
        if not component_instance:
            return True
        return component_instance.projection_area1 and component_instance.projection_area2 and component_instance.projection_area3 and component_instance.projection_area4

    def update_selected(self):
        if self.enabled and not self.is_all_areas_enabled():
            self.SetSelected()
        else:
            self.SetDeselected()

    def Enable(self):
        super(AreaToggleButtonMenuIcon, self).Enable()
        self.update_selected()

    def Disable(self):
        super(AreaToggleButtonMenuIcon, self).Disable()
        self.update_selected()


class BaseAreaToggleButtonIcon(CircularMenuButtonIcon):
    area_name = None

    def __init__(self, slot_id, *args, **kwargs):
        super(BaseAreaToggleButtonIcon, self).__init__(*args, **kwargs)
        self.slot_id = slot_id
        self.update_selected()
        self.text = TextBody(parent=self, text=self.area_name, align=Align.CENTERRIGHT, opacity=0.0)

    def update_selected(self):
        if self.get_value():
            self.SetSelected()
        else:
            self.SetDeselected()

    def get_component_instance(self):
        component_instance = current_skin_design.get().get_fitted_component_instance(self.slot_id)
        return component_instance

    def get_value(self):
        raise NotImplemented

    def set_value(self, value):
        raise NotImplemented

    def toggle_value(self):
        self.set_value(not self.get_value())

    def OnClick(self, *args):
        self.toggle_value()
        self.update_selected()
        current_skin_design.add_to_undo_history()

    def OnMouseEnter(self, *args):
        animations.FadeIn(self.text, endVal=TextColor.NORMAL[-1], duration=uiconst.TIME_ENTRY)
        self.text.left = self.default_width + 8
        animations.MorphScalar(self.text, 'top', -8, 0, duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        animations.FadeOut(self.text, duration=0.1)
        animations.MorphScalar(self.text, 'left', self.text.left, self.default_width, duration=0.1)


class PrimaryAreaToggleButtonIcon(BaseAreaToggleButtonIcon):
    default_texturePath = eveicon.primary_area
    area_name = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/PrimaryArea')

    def get_value(self):
        return self.get_component_instance().projection_area1

    def set_value(self, value):
        self.get_component_instance().projection_area1 = value


class SecondaryAreaToggleButtonIcon(BaseAreaToggleButtonIcon):
    default_texturePath = eveicon.secondary_area
    area_name = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/SecondaryArea')

    def get_value(self):
        return self.get_component_instance().projection_area2

    def set_value(self, value):
        self.get_component_instance().projection_area2 = value


class DetailingAreaToggleButtonIcon(BaseAreaToggleButtonIcon):
    default_texturePath = eveicon.details
    area_name = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/DetailingArea')

    def get_value(self):
        return self.get_component_instance().projection_area3

    def set_value(self, value):
        self.get_component_instance().projection_area3 = value


class TechAreaToggleButtonIcon(BaseAreaToggleButtonIcon):
    default_texturePath = eveicon.tech_area
    area_name = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/TechArea')

    def get_value(self):
        return self.get_component_instance().projection_area4

    def set_value(self, value):
        self.get_component_instance().projection_area4 = value


class AreaToggleButtonMenu(Container, ContextMenuMixin):
    default_width = 32
    default_height = 176
    default_align = Align.ABSOLUTE

    def __init__(self, slot_id, **kw):
        super(AreaToggleButtonMenu, self).__init__(**kw)
        self.primary_btn = PrimaryAreaToggleButtonIcon(parent=self, align=Align.CENTERTOP, slot_id=slot_id)
        self.secondary_btn = SecondaryAreaToggleButtonIcon(parent=self, align=Align.CENTERTOP, slot_id=slot_id)
        self.detail_btn = DetailingAreaToggleButtonIcon(parent=self, align=Align.CENTERTOP, slot_id=slot_id)
        self.tech_btn = TechAreaToggleButtonIcon(parent=self, align=Align.CENTERTOP, slot_id=slot_id)
        self.appear()

    def appear(self):
        animations.FadeTo(self, 0.0, 1.0, duration=uiconst.TIME_ENTRY)
        center_top = self.default_height / 2
        left_offset = 32
        duration = 0.08
        animations.MorphScalar(self.primary_btn, 'left', left_offset, 0, duration=duration)
        animations.MorphScalar(self.primary_btn, 'top', center_top, 0, duration=duration)
        animations.MorphScalar(self.secondary_btn, 'left', left_offset, 0, duration=duration)
        animations.MorphScalar(self.secondary_btn, 'top', center_top, 48, duration=duration)
        animations.MorphScalar(self.detail_btn, 'left', left_offset, 0, duration=duration)
        animations.MorphScalar(self.detail_btn, 'top', center_top, 96, duration=duration)
        animations.MorphScalar(self.tech_btn, 'left', left_offset, 0, duration=duration)
        animations.MorphScalar(self.tech_btn, 'top', center_top, 144, duration=duration)
