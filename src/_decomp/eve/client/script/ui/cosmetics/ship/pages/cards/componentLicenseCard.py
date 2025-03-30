#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\cards\componentLicenseCard.py
from carbonui import Align, SpriteEffect, uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from cosmetics.common.ships.skins.static_data.component_category import ComponentCategory
from eve.client.script.ui import eveColor
from eve.client.script.ui.cosmetics.ship.controls.numRunsIndicator import NumRunsIndicator
from eve.client.script.ui.cosmetics.ship.pages.cards.baseComponentCard import ComponentCard, BlankComponentCard
from eve.client.script.ui.cosmetics.ship.pages.collection import collectionSignals
from eveservices.menu import GetMenuService

class ComponentLicenceCard(ComponentCard):

    def __init__(self, component_license, *args, **kwargs):
        self.component_license = component_license
        self.is_new = False
        self.is_animating = False
        super(ComponentLicenceCard, self).__init__(*args, **kwargs)

    def get_background_texture(self):
        if self.component_license.get_component_data().category == ComponentCategory.PATTERN:
            return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/components/pattern_background.png'
        else:
            return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/components/material_background.png'

    def construct_icon(self):
        super(ComponentLicenceCard, self).construct_icon()
        if self.component_license.get_component_data().category == ComponentCategory.PATTERN:
            self.icon = Sprite(name='icon', parent=self.icon_container, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath=self.component_license.get_component_data().icon_file_path, textureSecondaryPath='res:/UI/Texture/classes/Cosmetics/Ship/cards/components/pattern_icon_mask.png', spriteEffect=SpriteEffect.MODULATE, glow=False, width=80, height=80)
        else:
            self.icon = Sprite(name='icon', parent=self.icon_container, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath=self.component_license.get_component_data().icon_file_path, textureSecondaryPath='res:/UI/Texture/classes/Cosmetics/Ship/pages/studio/nanocoating_mask.png', spriteEffect=SpriteEffect.MODULATE, glow=False, width=64, height=64)
            Sprite(name='icon_ring', parent=self, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/cards/components/material_ring.png', width=90, height=90, top=49)

    def construct_usage_indicator(self):
        self.usage_container = NumRunsIndicator(name='usage_container', parent=self, align=Align.TOPRIGHT, opacity=0.5, width=self.USAGE_ICON_SIZE, height=self.USAGE_ICON_SIZE, top=self.CORNER_ICON_OFFSET, left=self.CORNER_ICON_OFFSET, num_runs=self.get_uses_remaining(), licence_type=self.component_license.license_type)

    def update(self):
        self.is_new = get_ship_skin_component_svc().is_component_new(self.component_license.component_id)
        super(ComponentLicenceCard, self).update()
        self.update_usage_indicator()
        if self.is_new:
            if not self.is_animating:
                self.start_new_highlight_animation()
        else:
            self.stop_new_highlight_animation()

    def update_usage_indicator(self):
        target_opacity = 1.0 if self.is_hovered or self.is_selected else 0.5
        animations.FadeTo(self.usage_container, self.usage_container.opacity, target_opacity, self.ANIM_DURATION)

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

    def get_top_line_color(self):
        if self.is_new:
            return eveColor.DUSKY_ORANGE
        return super(ComponentLicenceCard, self).get_top_line_color()

    def get_top_line_opacity(self):
        if self.is_new:
            return 1.0
        return super(ComponentLicenceCard, self).get_top_line_opacity()

    def get_highlight_color(self):
        if self.is_new:
            return eveColor.DUSKY_ORANGE
        return super(ComponentLicenceCard, self).get_highlight_color()

    def get_highlight_opacity(self):
        if self.is_new:
            return 1.0
        return super(ComponentLicenceCard, self).get_highlight_opacity()

    def get_rarity(self):
        return self.component_license.get_component_data().rarity

    def has_unlimited_uses(self):
        return self.component_license.license_type is ComponentLicenseType.UNLIMITED

    def get_uses_remaining(self):
        return self.component_license.remaining_license_uses

    def get_component_name(self):
        return self.component_license.name

    def _on_selected(self):
        collectionSignals.on_component_license_selected(self.component_license)

    def OnClick(self, *args):
        if self.is_selected:
            return
        get_ship_skin_component_svc().set_component_is_new_flag(self.component_license.component_id, False)
        super(ComponentLicenceCard, self).OnClick(*args)

    def GetMenu(self):
        for type_id, component_item_data in self.component_license.get_component_data().component_item_data_by_type_id.items():
            if component_item_data.component_id == self.component_license.component_id:
                return GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=type_id, includeMarketDetails=True)


class BlankMaterialComponentCard(BlankComponentCard):

    def get_background_texture(self):
        return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/components/material_blank.png'


class BlankPatternComponentCard(BlankComponentCard):

    def get_background_texture(self):
        return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/components/pattern_blank.png'
