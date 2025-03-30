#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\cards\skinLicenseCard.py
import evetypes
from carbonui import Align, TextAlign, TextBody
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.shipSkinLicensesSvc import get_ship_skin_license_svc
from eve.client.script.ui import eveColor
from eve.client.script.ui.cosmetics.ship import shipUtil
from eve.client.script.ui.cosmetics.ship.pages.cards.baseSkinCard import SkinCard
from eve.client.script.ui.cosmetics.ship.pages.cards.cardConst import CardOutline
from eve.client.script.ui.cosmetics.ship.pages.collection import collectionSignals
from eveservices.menu import GetMenuService
from localization import GetByLabel

class BaseSkinLicenseCard(SkinCard):

    def __init__(self, skin_license, *args, **kwargs):
        self.license_id = skin_license.skin_hex
        self.skin_license = skin_license
        super(BaseSkinLicenseCard, self).__init__(*args, **kwargs)
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(BaseSkinLicenseCard, self).Close()

    def connect_signals(self):
        ship_skin_signals.on_skin_license_activated.connect(self.on_skin_license_activated)
        ship_skin_signals.on_skin_state_set.connect(self.on_skin_state_set)

    def disconnect_signals(self):
        ship_skin_signals.on_skin_license_activated.disconnect(self.on_skin_license_activated)
        ship_skin_signals.on_skin_state_set.disconnect(self.on_skin_state_set)

    def get_live_rendered_icon_skin_design(self):
        return self.skin_license.skin_design

    def get_background_texture(self):
        pass

    def get_outline_texture(self):
        if self.is_stack:
            return CardOutline.DEFAULT_STACK
        return CardOutline.DEFAULT

    def get_skin_tier_level(self):
        return self.skin_license.tier_level

    def get_skin_name(self):
        return self.skin_license.name

    def get_top_line_color(self):
        if self.is_selected:
            return self.get_highlight_color()
        else:
            return eveColor.WHITE

    def get_top_line_corner_color(self):
        if self.is_selected:
            return self.get_highlight_color()
        else:
            return eveColor.WHITE

    def get_highlight_color(self):
        return eveColor.CRYO_BLUE

    def on_skin_license_activated(self, license_id):
        self.update()

    def on_skin_state_set(self, _ship_instance_id, skin_state):
        self.update()

    def OnClick(self, *args):
        if self.is_selected:
            return
        super(BaseSkinLicenseCard, self).OnClick(*args)

    def GetMenu(self):
        menu_data = MenuData()
        type_id = self.skin_license.skin_design.ship_type_id
        menu_data.AddEntry(text=evetypes.GetName(type_id), subMenuData=lambda : GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=type_id, includeMarketDetails=True))
        return menu_data

    @property
    def is_stack(self):
        return self.skin_license.nb_unactivated > 1


class ActivatedSkinLicenseCard(BaseSkinLicenseCard):
    ship_glow = False

    def get_label_color(self):
        if shipUtil.is_currently_applied_skin(self.skin_license.skin_hex):
            return eveColor.CRYO_BLUE
        else:
            return super(ActivatedSkinLicenseCard, self).get_label_color()

    def get_outline_texture(self):
        return CardOutline.DEFAULT

    def get_background_texture(self):
        return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/activated_bg.png'

    def _on_selected(self):
        collectionSignals.on_activated_skin_license_selected(self.skin_license)


class UnactivatedSkinLicenseCard(BaseSkinLicenseCard):

    def __init__(self, skin_license, *args, **kwargs):
        self.is_new = False
        self.is_animating = False
        super(UnactivatedSkinLicenseCard, self).__init__(skin_license, *args, **kwargs)

    def construct_layout(self):
        self.construct_unactivated_label()
        super(UnactivatedSkinLicenseCard, self).construct_layout()

    def construct_unactivated_label(self):
        self.unactivated_container = Container(name='unactivated_container', parent=self, align=Align.TOBOTTOM_NOPUSH, opacity=0.5, top=55, height=20)
        TextBody(name='unactivated_label', parent=self.unactivated_container, align=Align.TOTOP, textAlign=TextAlign.CENTER, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/Unactivated'))

    def update_stack_lines(self):
        if not self.is_stack:
            return
        self.stack_lines_container.display = True
        target_opacity = 1.0 if self.is_hovered or self.is_selected else 0.5
        animations.FadeTo(self.stack_lines_container, self.stack_lines_container.opacity, target_opacity, self.ANIM_DURATION)

    def update_stack_numbers(self):
        if not self.is_stack:
            self.stack_numbers_container.display = False
        else:
            self.stack_numbers_container.display = True
            self.stack_numbers_label.text = self.skin_license.nb_unactivated

    def update(self):
        self.is_new = get_ship_skin_license_svc().is_license_new(self.license_id)
        super(UnactivatedSkinLicenseCard, self).update()
        self.update_unactivated_label()
        if self.is_new:
            if not self.is_animating:
                self.start_new_highlight_animation()
        else:
            self.stop_new_highlight_animation()

    def update_unactivated_label(self):
        self.unactivated_container.display = True
        target_opacity = 1.0 if self.is_hovered or self.is_selected else 0.5
        animations.FadeTo(self.unactivated_container, self.unactivated_container.opacity, target_opacity, self.ANIM_DURATION)

    def start_new_highlight_animation(self):
        self.is_animating = True
        animations.MorphScalar(obj=self.top_line, attrName='glowBrightness', startVal=self.top_line.glowBrightness, endVal=1.5, duration=1.0, timeOffset=0.5, callback=self.on_new_highlight_animation_in_complete)
        animations.MorphScalar(obj=self.top_left_corner, attrName='glowBrightness', startVal=self.top_left_corner.glowBrightness, endVal=1.5, duration=1.0, timeOffset=0.5)
        animations.MorphScalar(obj=self.top_right_corner, attrName='glowBrightness', startVal=self.top_right_corner.glowBrightness, endVal=1.5, duration=1.0, timeOffset=0.5)
        animations.MorphScalar(obj=self.highlight_bottom, attrName='glowBrightness', startVal=self.highlight_bottom.glowBrightness, endVal=1.5, duration=1.0, timeOffset=0.5)

    def on_new_highlight_animation_in_complete(self, *args):
        animations.MorphScalar(obj=self.top_line, attrName='glowBrightness', startVal=self.top_line.glowBrightness, endVal=self.GLOW_AMOUNT, duration=1.0, timeOffset=1.0, callback=self.on_new_highlight_animation_out_complete)
        animations.MorphScalar(obj=self.top_left_corner, attrName='glowBrightness', startVal=self.top_left_corner.glowBrightness, endVal=self.GLOW_AMOUNT, duration=1.0, timeOffset=1.0)
        animations.MorphScalar(obj=self.top_right_corner, attrName='glowBrightness', startVal=self.top_right_corner.glowBrightness, endVal=self.GLOW_AMOUNT, duration=1.0, timeOffset=1.0)
        animations.MorphScalar(obj=self.highlight_bottom, attrName='glowBrightness', startVal=self.highlight_bottom.glowBrightness, endVal=self.GLOW_AMOUNT, duration=1.0, timeOffset=1.0)

    def on_new_highlight_animation_out_complete(self, *args):
        if self.is_new:
            self.start_new_highlight_animation()

    def stop_new_highlight_animation(self):
        animations.StopAnimation(self.top_line, 'glowBrightness')
        animations.StopAnimation(self.top_right_corner, 'glowBrightness')
        animations.StopAnimation(self.top_left_corner, 'glowBrightness')
        animations.StopAnimation(self.highlight_bottom, 'glowBrightness')
        self.top_line.glowBrightness = self.GLOW_AMOUNT
        self.top_left_corner.glowBrightness = self.GLOW_AMOUNT
        self.top_right_corner.glowBrightness = self.GLOW_AMOUNT
        self.highlight_bottom.glowBrightness = self.GLOW_AMOUNT
        self.is_animating = False

    def get_background_texture(self):
        return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/background.png'

    def get_top_line_color(self):
        if self.is_new:
            return eveColor.DUSKY_ORANGE
        return super(UnactivatedSkinLicenseCard, self).get_top_line_color()

    def get_top_line_opacity(self):
        if self.is_new:
            return 1.0
        return super(UnactivatedSkinLicenseCard, self).get_top_line_opacity()

    def get_top_line_corner_color(self):
        if self.is_new:
            return eveColor.DUSKY_ORANGE
        return super(UnactivatedSkinLicenseCard, self).get_top_line_corner_color()

    def get_highlight_color(self):
        if self.is_new:
            return eveColor.DUSKY_ORANGE
        return super(UnactivatedSkinLicenseCard, self).get_highlight_color()

    def get_highlight_opacity(self):
        if self.is_new:
            return 1.0
        return super(UnactivatedSkinLicenseCard, self).get_highlight_opacity()

    def _on_selected(self):
        collectionSignals.on_unactivated_skin_license_selected(self.skin_license)

    def OnClick(self, *args):
        if self.is_selected:
            return
        get_ship_skin_license_svc().set_license_is_new_flag(self.license_id, is_new=False)
        super(UnactivatedSkinLicenseCard, self).OnClick(*args)
