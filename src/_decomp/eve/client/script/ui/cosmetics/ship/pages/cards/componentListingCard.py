#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\cards\componentListingCard.py
import eveformat
import eveicon
from carbonui import Align, TextBody, PickState, SpriteEffect, uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from cosmetics.common.ships.skins.static_data.component_category import ComponentCategory
from cosmetics.common.ships.skins.util import Currency
from eve.client.script.ui import eveColor
from eve.client.script.ui.cosmetics.ship.controls.numRunsIndicator import NumRunsIndicator
from eve.client.script.ui.cosmetics.ship.pages.cards.baseComponentCard import ComponentCard
from eve.client.script.ui.cosmetics.ship.pages.store import storeSignals
from eveservices.menu import GetMenuService
from localization import GetByLabel

class ComponentListingCard(ComponentCard):

    def __init__(self, listing, *args, **kwargs):
        self.listing = listing
        self.name = str(self.listing.identifier)
        super(ComponentListingCard, self).__init__(*args, **kwargs)

    def construct_layout(self):
        self.construct_cost_container()
        super(ComponentListingCard, self).construct_layout()

    def construct_cost_container(self):
        self.cost_cont = ContainerAutoSize(name='const_cont', parent=self, align=Align.CENTERBOTTOM, opacity=0.5, top=58, pickState=PickState.OFF)
        self.cost_icon = Sprite(parent=self.cost_cont, align=Align.CENTERLEFT, pos=(0, 0, 16, 16))
        self.cost_label = TextBody(parent=self.cost_cont, align=Align.CENTERLEFT, left=20)

    def get_background_texture(self):
        if self.listing.component_license.get_component_data().category == ComponentCategory.PATTERN:
            return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/components/pattern_background.png'
        else:
            return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/components/material_background.png'

    def get_rarity(self):
        return self.listing.component_license.get_component_data().rarity

    def has_unlimited_uses(self):
        return self.listing.component_license.license_type is ComponentLicenseType.UNLIMITED

    def get_uses_remaining(self):
        return self.listing.component_license.remaining_license_uses

    def get_component_name(self):
        return self.listing.component_license.name

    def get_top_line_color(self):
        if self.listing.is_limited_offer():
            return eveColor.LEAFY_GREEN
        return super(ComponentListingCard, self).get_top_line_color()

    def get_highlight_color(self):
        if self.listing.is_limited_offer():
            return eveColor.LEAFY_GREEN
        return super(ComponentListingCard, self).get_highlight_color()

    def get_highlight_opacity(self):
        if self.listing.is_limited_offer():
            return 1.0
        return super(ComponentListingCard, self).get_highlight_opacity()

    def construct_icon(self):
        super(ComponentListingCard, self).construct_icon()
        if self.listing.component_license.get_component_data().category == ComponentCategory.PATTERN:
            self.icon = Sprite(name='icon', parent=self.icon_container, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath=self.listing.component_license.get_component_data().icon_file_path, textureSecondaryPath='res:/UI/Texture/classes/Cosmetics/Ship/cards/components/pattern_icon_mask.png', spriteEffect=SpriteEffect.MODULATE, glow=False, width=80, height=80)
        else:
            self.icon = Sprite(name='icon', parent=self.icon_container, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath=self.listing.component_license.get_component_data().icon_file_path, textureSecondaryPath='res:/UI/Texture/classes/Cosmetics/Ship/pages/studio/nanocoating_mask.png', spriteEffect=SpriteEffect.MODULATE, glow=False, width=64, height=64)
            Sprite(name='icon_ring', parent=self, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/cards/components/material_ring.png', width=90, height=90, top=49)

    def construct_usage_indicator(self):
        self.usage_container = NumRunsIndicator(name='usage_container', parent=self, align=Align.TOPRIGHT, opacity=0.5, width=self.USAGE_ICON_SIZE, height=self.USAGE_ICON_SIZE, top=self.CORNER_ICON_OFFSET, left=self.CORNER_ICON_OFFSET, num_runs=self.get_uses_remaining(), licence_type=self.listing.component_license.license_type)

    def update(self):
        super(ComponentListingCard, self).update()
        self.update_usage_indicator()
        self.update_cost()

    def update_usage_indicator(self):
        target_opacity = 1.0 if self.is_hovered or self.is_selected else 0.5
        animations.FadeTo(self.usage_container, self.usage_container.opacity, target_opacity, self.ANIM_DURATION)

    def update_cost(self):
        self.cost_label.text = eveformat.number(self.listing.price)
        if self.listing.currency == Currency.PLEX:
            self.cost_icon.texturePath = eveicon.plex
            self.cost_icon.color = icon_color = eveColor.PLEX_YELLOW
        else:
            self.cost_icon.texturePath = eveicon.isk
            self.cost_icon.color = eveColor.WHITE
        target_opacity = 1.0 if self.is_hovered or self.is_selected else 0.5
        animations.FadeTo(self.cost_cont, self.cost_cont.opacity, target_opacity, self.ANIM_DURATION)

    def _on_selected(self):
        storeSignals.on_component_listing_selected(self.listing)

    def OnClick(self, *args):
        if self.is_selected:
            return
        super(ComponentListingCard, self).OnClick(*args)

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=self.listing.component_item_type_id, includeMarketDetails=True)

    def GetHint(self):
        if self.listing.is_limited_offer():
            return GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/LimitedOffer', valid_until=self.listing.valid_until_seconds)
