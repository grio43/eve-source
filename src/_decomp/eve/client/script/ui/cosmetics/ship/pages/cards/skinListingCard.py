#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\cards\skinListingCard.py
import eveformat
import eveicon
import evetypes
import uthread2
from carbon.common.script.util.format import FmtAmt
from carbonui import Align, PickState, TextBody, TextColor, TextDetail, uiconst
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from cosmetics.client.ships.qa.menus import is_qa, get_qa_menu_for_skin_listing_card
from cosmetics.client.ships.ship_skin_signals import on_skin_listing_expired
from cosmetics.client.shipSkinTradingSvc import get_ship_skin_trading_svc
from cosmetics.common.ships.skins.util import Currency
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.cosmetics.ship.pages.cards import cardConst
from eve.client.script.ui.cosmetics.ship.pages.cards.cardConst import CardBackground, CardOutline, CardMask
from eve.client.script.ui.cosmetics.ship.pages.cards.baseSkinCard import SkinCard
from eve.client.script.ui.cosmetics.ship.pages.store import storeSignals
from eve.client.script.ui.cosmetics.ship.pages.store.skinListingDragData import SkinListingDragData
from eveservices.menu import GetMenuService
from inventorycommon.const import typeLoyaltyPointsHeraldry
from localization import GetByLabel
_EXPIRED_CONTENT_OPACITY = 0.5

class SkinListingCard(SkinCard):
    default_height = cardConst.card_height + 16
    isDragObject = True

    def __init__(self, listing, *args, **kwargs):
        self.listing = listing
        self.name = str(self.listing.identifier)
        self._expired = self.listing.is_expired
        self._buyer_fee_amount = None
        self._update_label_thread = None
        self._update_buyer_fee_amount_thread = None
        super(SkinListingCard, self).__init__(*args, **kwargs)
        self._update_label_thread = uthread2.start_tasklet(self.update_remaining_time_label_thread)
        if self._expired:
            self._set_expired(animate=False)
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
            self.kill_update_label_thread()
            self.kill_update_buyer_fee_amount_thread()
        finally:
            super(SkinListingCard, self).Close()

    def kill_update_label_thread(self):
        if self._update_label_thread:
            self._update_label_thread.kill()

    def kill_update_buyer_fee_amount_thread(self):
        if self._update_buyer_fee_amount_thread:
            self._update_buyer_fee_amount_thread.kill()

    def disconnect_signals(self):
        on_skin_listing_expired.disconnect(self._on_skin_listing_expired)

    def connect_signals(self):
        on_skin_listing_expired.connect(self._on_skin_listing_expired)

    def construct_layout(self):
        self.construct_character_targeted_cross()
        self.construct_cost_container()
        self.construct_remaining_time_label()
        self.construct_buyer_fee()
        self.construct_seller_character_name()
        if self.listing.is_targeted_at_any_organization and self.listing.branded:
            self.update_buyer_fee_amount_async()
        super(SkinListingCard, self).construct_layout()

    def get_live_rendered_icon_skin_design(self):
        return self.listing.skin_design

    def construct_outline(self):
        super(SkinListingCard, self).construct_outline()
        if self.listing.branded:
            self.construct_branded_logo()

    def construct_branded_logo(self):
        branded_logo_container = Container(name='branded_logo_container', parent=self.content, align=Align.TOPLEFT, pos=(8, 10, 40, 40))
        icon = GetLogoIcon(name='icon', parent=branded_logo_container, align=Align.CENTER, state=uiconst.UI_NORMAL, itemID=self.listing.target.target_id, pos=(0, 0, 32, 32))
        icon.OnClick = self.on_icon_click

    def on_icon_click(self, *args):
        sm.GetService('info').ShowInfo(typeID=cfg.eveowners.Get(self.listing.target.target_id).typeID, itemID=self.listing.target.target_id)

    def construct_character_targeted_cross(self):
        self.character_targeted_cross = Sprite(name='character_targeted_cross', parent=self, align=Align.CENTER, pickState=PickState.OFF, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/cards/listing/targeted_character_cross.png', color=eveColor.WHITE, opacity=0.1, pos=(0, -29, 162, 136), display=False)

    def construct_cost_container(self):
        self.cost_cont = ContainerAutoSize(name='const_cont', parent=self, align=Align.CENTERBOTTOM, opacity=0.5, top=58, pickState=PickState.OFF)
        self.cost_icon = Sprite(parent=self.cost_cont, align=Align.CENTERLEFT, pos=(0, 0, 16, 16))
        self.cost_label = TextBody(parent=self.cost_cont, align=Align.CENTERLEFT, left=20)

    def construct_remaining_time_label(self):
        self.time_remaining_container = Container(name='time_remaining_container', parent=self, align=Align.TOBOTTOM, opacity=0.0, width=self.default_width, height=16, padLeft=10, padRight=10)
        self.remaining_time_label = TextDetail(name='remaining_time_label', parent=self.time_remaining_container, align=Align.CENTERLEFT, color=TextColor.SECONDARY, maxLines=1, autoFadeSides=16)

    def construct_buyer_fee(self):
        self.buyer_fee_container = ContainerAutoSize(name='buyer_fee_container', parent=self, align=Align.CENTERBOTTOM, pickState=PickState.OFF, height=20, opacity=0.0, top=58)
        ItemIcon(name='evermarks_icon', parent=self.buyer_fee_container, align=Align.CENTERLEFT, width=20, height=20, typeID=typeLoyaltyPointsHeraldry)
        self.buyer_fee_label = TextBody(name='buyer_fee_label', parent=self.buyer_fee_container, align=Align.CENTERLEFT, color=eveColor.SUCCESS_GREEN, left=24)

    def construct_seller_character_name(self):
        container_width = cardConst.card_width - 60
        self.seller_character_container = Container(name='seller_character_container', parent=self, align=Align.CENTERBOTTOM, pickState=PickState.OFF, width=container_width, height=20, opacity=0.0, top=58)
        text = self.seller_character_text
        text_width, _ = TextBody.MeasureTextSize(text) if text else (0, 0)
        self.seller_character_label = TextBody(name='seller_character_label', parent=self.seller_character_container, align=Align.CENTER if text_width < container_width else Align.TOLEFT, text=text, maxLines=1, color=eveColor.FOCUS_BLUE, autoFadeSides=10)

    def update(self):
        super(SkinListingCard, self).update()
        self.update_character_targeted_cross()
        self.update_cost()
        self.update_time_remaining_container()
        self.update_buyer_fee()
        self.update_targeted_character_name()

    def update_character_targeted_cross(self):
        self.character_targeted_cross.display = self.listing.is_targeted_at_any_character
        target_opacity = 0.5 if self.is_hovered or self.is_selected else 0.1
        animations.FadeTo(self.character_targeted_cross, self.character_targeted_cross.opacity, target_opacity, self.ANIM_DURATION)

    def update_cost(self):
        self._update_cost_label()
        target_opacity = 1.0 if self.is_hovered or self.is_selected else 0.5
        animations.FadeTo(self.cost_cont, self.cost_cont.opacity, target_opacity, self.ANIM_DURATION)
        if self._buyer_fee_amount is not None or self.listing.is_targeted_at_any_character:
            target_top = 78 if self.is_hovered or self.is_selected else 58
            animations.MorphScalar(self.cost_cont, 'top', self.cost_cont.top, target_top, self.ANIM_DURATION)

    def _update_cost_label(self):
        if self._expired:
            self.cost_label.text = GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ListingExpired')
            self.cost_label.left = 0
            self.cost_icon.display = False
        else:
            self.cost_label.text = eveformat.number(self.listing.price)
            self.cost_label.left = 20
            self.cost_icon.display = True
            if self.listing.currency == Currency.PLEX:
                self.cost_icon.texturePath = eveicon.plex
                self.cost_icon.color = eveColor.PLEX_YELLOW
            else:
                self.cost_icon.texturePath = eveicon.isk
                self.cost_icon.color = eveColor.WHITE

    def update_time_remaining_container(self):
        target_opacity = 1.0 if self.is_hovered or self.is_selected else 0.0
        animations.FadeTo(self.time_remaining_container, self.time_remaining_container.opacity, target_opacity, self.ANIM_DURATION)

    def update_buyer_fee(self):
        if self._buyer_fee_amount is None:
            self.buyer_fee_label.text = None
            self.buyer_fee_container.opacity = 0.0
        else:
            self.buyer_fee_label.text = FmtAmt(self._buyer_fee_amount)
            target_opacity = 1.0 if self.is_hovered or self.is_selected else 0.0
            animations.FadeTo(self.buyer_fee_container, self.buyer_fee_container.opacity, target_opacity, self.ANIM_DURATION)

    def update_targeted_character_name(self):
        if not self.listing.is_targeted_at_any_character:
            return
        target_opacity = 1.0 if self.is_hovered or self.is_selected else 0.0
        animations.FadeTo(self.seller_character_container, self.seller_character_container.opacity, target_opacity, self.ANIM_DURATION)

    def update_buyer_fee_amount_async(self):
        self.kill_update_buyer_fee_amount_thread()
        uthread2.start_tasklet(self.update_buyer_fee_amount)

    def update_buyer_fee_amount(self):
        self._buyer_fee_amount = self.get_buyer_fee_amount()

    def update_stack_lines(self):
        if not self.is_stack:
            return
        self.stack_lines_container.display = True
        target_opacity = 1.0 if self.is_hovered or self.is_selected else 0.5
        animations.FadeTo(self.stack_lines_container, self.stack_lines_container.opacity, target_opacity, self.ANIM_DURATION)

    def update_stack_numbers(self):
        self.stack_numbers_container.display = self.is_stack
        self.stack_numbers_label.text = self.listing.quantity if self.is_stack else None

    def get_top_line_color(self):
        if self.listing.branded:
            if self.is_selected:
                return eveColor.SUCCESS_GREEN
            return eveColor.WHITE
        return super(SkinListingCard, self).get_top_line_color()

    def get_top_line_corner_color(self):
        if self.listing.branded:
            if self.is_selected:
                return eveColor.SUCCESS_GREEN
            return eveColor.WHITE
        return super(SkinListingCard, self).get_top_line_corner_color()

    def get_skin_tier_level(self):
        return self.listing.skin_design.tier_level

    def get_outline_color(self):
        if self.listing.branded:
            return eveColor.SUCCESS_GREEN
        return eveColor.FOCUS_BLUE

    def get_outline_texture(self):
        if self.listing.is_targeted_at_any_character:
            if self.is_stack:
                return CardOutline.TARGETED_AT_CHARACTER_STACK
            return CardOutline.TARGETED_AT_CHARACTER
        if self.listing.is_targeted_at_any_organization:
            if self.is_stack:
                return CardOutline.TARGETED_AT_ORGANIZATION_STACK
            return CardOutline.TARGETED_AT_ORGANIZATION
        if self.is_stack:
            return CardOutline.PUBLIC_STACK
        return CardOutline.PUBLIC

    def get_background_texture(self):
        if self.listing.is_targeted_at_any_character:
            if self.is_stack:
                return CardBackground.TARGETED_AT_CHARACTER_STACK
            return CardBackground.TARGETED_AT_CHARACTER
        if self.listing.is_targeted_at_any_organization:
            if self.listing.branded:
                if self.is_stack:
                    return CardBackground.TARGETED_AT_ORGANIZATION_BRANDED_STACK
                return CardBackground.TARGETED_AT_ORGANIZATION_BRANDED
            elif self.is_stack:
                return CardBackground.TARGETED_AT_ORGANIZATION_STACK
            else:
                return CardBackground.TARGETED_AT_ORGANIZATION
        if self.is_stack:
            return CardBackground.PUBLIC_STACK
        return CardBackground.PUBLIC

    def get_mask_texture(self):
        if self.listing.is_targeted_at_any_character:
            if self.is_stack:
                return CardMask.TARGETED_AT_CHARACTER_STACK
            return CardMask.TARGETED_AT_CHARACTER
        if self.listing.is_targeted_at_any_organization:
            if self.is_stack:
                return CardMask.TARGETED_AT_ORGANIZATION_STACK
            return CardMask.TARGETED_AT_ORGANIZATION
        if self.is_stack:
            return CardMask.PUBLIC_STACK
        return CardMask.PUBLIC

    def _on_selected(self):
        storeSignals.on_skin_listing_selected(self.listing, self)

    def OnClick(self, *args):
        if self.is_selected:
            return
        super(SkinListingCard, self).OnClick(*args)

    def get_skin_name(self):
        return self.listing.name

    def update_remaining_time_label_thread(self):
        while not self.destroyed:
            self.remaining_time_label.text = self.listing.time_remaining_text
            uthread2.Sleep(0.5)

    def _on_skin_listing_expired(self, listing_id):
        if self.listing and self.listing.identifier == listing_id and not self._expired:
            self.kill_update_label_thread()
            self.remaining_time_label.text = None
            self._set_expired()

    def _set_expired(self, animate = True):
        self._expired = True
        self._update_cost_label()
        if animate:
            animations.FadeTo(self.content, self.content.opacity, _EXPIRED_CONTENT_OPACITY, self.ANIM_DURATION)
        else:
            self.content.opacity = _EXPIRED_CONTENT_OPACITY

    def get_buyer_fee_amount(self):
        if self.listing is None or self.listing.target is None:
            return
        buyer_fee, error = get_ship_skin_trading_svc().get_buyer_fee_for_listing(self.listing)
        if error:
            return
        elif buyer_fee.lp_amount > 0:
            return buyer_fee.lp_amount
        else:
            return

    def GetMenu(self):
        menu_data = MenuData()
        type_id = self.listing.skin_design.ship_type_id
        menu_data.AddEntry(text=evetypes.GetName(type_id), subMenuData=lambda : GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=type_id, includeMarketDetails=True))
        if is_qa():
            menu_data.AddEntry('QA:', subMenuData=lambda : get_qa_menu_for_skin_listing_card(self, self.listing.identifier))
        return menu_data

    def GetDragData(self):
        return SkinListingDragData(self.listing)

    @property
    def is_stack(self):
        return self.listing.quantity > 1

    @property
    def seller_character_text(self):
        if not self.listing.is_targeted_at_any_character:
            return None
        elif self.listing.seller_id == session.charid:
            return cfg.eveowners.Get(self.listing.target.target_id).name
        else:
            return cfg.eveowners.Get(self.listing.seller_id).name
