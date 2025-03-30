#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\buySkinDialogue.py
from carbonui import Align, uiconst
from carbonui.primitives.container import Container
from cosmetics.client.shipSkinTradingSvc import get_ship_skin_trading_svc
from cosmetics.client.ships.ship_skin_signals import on_skin_listing_expired
from cosmetics.client.ships.skins.errors import get_listing_error_text
from cosmetics.common.ships.skins.util import Currency
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.pages.cards.skinListingCard import SkinListingCard
from eve.client.script.ui.cosmetics.ship.pages.store import storeSignals
from eve.client.script.ui.cosmetics.ship.pages.store.buyComponentDialogue import BuyComponentDialogue
from eve.common.lib.appConst import corpHeraldry
from localization import GetByLabel

class BuySkinDialogue(BuyComponentDialogue):
    __notifyevents__ = ['OnCharacterLPBalanceChange_Local']
    default_windowID = 'BuySkinDialogue'
    default_caption = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/BuySkin')

    def __init__(self, listing, *args, **kwargs):
        super(BuySkinDialogue, self).__init__(listing, *args, **kwargs)
        on_skin_listing_expired.connect(self._on_skin_listing_expired)

    def Close(self, setClosed = False, *args, **kwargs):
        try:
            super(BuySkinDialogue, self).Close(setClosed, *args, **kwargs)
        finally:
            on_skin_listing_expired.disconnect(self._on_skin_listing_expired)

    def construct_card(self):
        card_container = Container(name='card_container', parent=self.content, align=Align.TOTOP, height=SkinListingCard.default_height)
        card = SkinListingCard(name='card', parent=card_container, align=Align.CENTER, listing=self.listing)
        card._on_selected = lambda *args, **kwargs: None
        card.is_selected = True

    def construct_item_delivery_notice(self):
        pass

    def construct_activate_now_checkbox(self):
        pass

    def update_buyer_fee(self):
        self.buyer_fee.amount = self.get_buyer_fee_amount()

    def get_buyer_fee_amount(self):
        if self.listing is None:
            return
        target_id = self.listing.target.target_id
        if target_id is None:
            return
        buyer_fee, error = get_ship_skin_trading_svc().get_buyer_fee_for_listing(self.listing)
        if error:
            ShowQuickMessage(GetByLabel(get_listing_error_text(error)))
            return
        else:
            return buyer_fee.lp_amount * self.purchase_quantity

    def purchase_listing(self):
        return get_ship_skin_trading_svc().purchase_listing(listing_id=self.listing.identifier, quantity=self.quantity)

    def on_buy_success(self):
        storeSignals.on_skin_listing_selected(None, None)
        self.SetModalResult(uiconst.ID_OK)

    def load_buy_button_tooltip_panel(self, tooltip_panel, *args):
        if self.listing.is_targeted_at_another_character:
            return GetByLabel('UI/Personalization/ShipSkins/SKINR/TargetedAtAnotherCharacter')
        if self.listing.is_targeted_at_another_organization:
            return GetByLabel('UI/Personalization/ShipSkins/SKINR/TargetedAtAnotherOrganization')
        return super(BuySkinDialogue, self).load_buy_button_tooltip_panel(tooltip_panel, *args)

    @property
    def insufficient_funds_hint(self):
        currencies = []
        if self.listing.currency == Currency.ISK and not self.has_enough_isk:
            currencies.append(GetByLabel('UI/Common/ISK'))
        if self.listing.currency == Currency.PLEX and not self.has_enough_plex:
            currencies.append(GetByLabel('UI/Common/PLEX'))
        if self.requires_evermarks and not self.has_enough_evermarks:
            currencies.append(GetByLabel('UI/Wallet/WalletWindow/EM'))
        return u'{base} ({currencies})'.format(base=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InsufficientFunds'), currencies=u'/'.join(currencies))

    def has_sufficient_funds(self):
        if self.requires_evermarks and not self.has_enough_evermarks:
            return False
        return super(BuySkinDialogue, self).has_sufficient_funds()

    @property
    def is_allowed_to_purchase(self):
        if self.listing.is_targeted_at_another_character or self.listing.is_targeted_at_another_organization:
            return False
        return super(BuySkinDialogue, self).is_allowed_to_purchase

    @property
    def requires_evermarks(self):
        return self.buyer_fee.amount is not None

    @property
    def has_enough_evermarks(self):
        return sm.GetService('loyaltyPointsWalletSvc').GetCharacterEvermarkBalance() >= self.buyer_fee.amount

    def _on_skin_listing_expired(self, listing_id):
        if self.listing and self.listing.identifier == listing_id:
            self.kill_threads()
            self.buy_button.disable()

    def OnCharacterLPBalanceChange_Local(self, issuerCorpID, lpBefore, lpAfter):
        if issuerCorpID == corpHeraldry:
            self.update()
