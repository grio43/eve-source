#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\skinListingDetailsContainer.py
import blue
import logging
import carbonui
import eveicon
import uthread2
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.shared.neocom.wallet.buyMissingPlexDialog import BuyMissingPlexDialog
from localization import GetByLabel
from carbonui import Align, Density, ButtonStyle, ButtonVariant, TextColor, TextAlign, uiconst, PickState
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from cosmetics.client.shipSkinTradingSvc import get_ship_skin_trading_svc
from cosmetics.client.ships.link.ship_skin_listing_link_creation import create_link
from cosmetics.client.ships.ship_skin_signals import on_skin_listing_expired
from cosmetics.client.ships.skins.errors import get_listing_error_text
from cosmetics.common.ships.skins.util import Currency
from eve.client.script.ui.cosmetics.ship.controls.characterInfo import MadeByCharacterInfo, ListedByCharacterInfo, TargetedAtCharacterInfo
from eve.client.script.ui.cosmetics.ship.controls.costInfo import BuyersFeeCostInfo, CostInfo
from eve.client.script.ui.cosmetics.ship.controls.organizationInfo import OrganizationInfo
from eve.client.script.ui.cosmetics.ship.controls.shipName import ShipName
from eve.client.script.ui.cosmetics.ship.controls.tierIndicator import TierIndicator
from eve.client.script.ui.cosmetics.ship.pages.store.buySkinDialogue import BuySkinDialogue
from eve.client.script.ui.cosmetics.ship.pages.store.skinListingDragData import SkinListingDragData
from eve.client.script.ui.shared.neocom.wallet import walletSignals
from eve.common.lib.appConst import corpHeraldry
log = logging.getLogger(__name__)

class SkinListingDetailsContainer(Container):
    __notifyevents__ = ['OnCharacterLPBalanceChange_Local']

    def __init__(self, listing, **kw):
        super(SkinListingDetailsContainer, self).__init__(**kw)
        self.listing = listing
        self.targeted_at_info = None
        self._expired = self.listing.is_expired
        self._buyer_fee_amount = None
        self._update_buyer_fee_thread = None
        self.construct_layout()
        self.connect_signals()

    def Close(self):
        try:
            self.kill_update_buyer_fee_thread()
            self.disconnect_signals()
        finally:
            super(SkinListingDetailsContainer, self).Close()

    def kill_update_buyer_fee_thread(self):
        if self._update_buyer_fee_thread:
            self._update_buyer_fee_thread.kill()
            self._update_buyer_fee_thread = None

    def disconnect_signals(self):
        sm.GetService('vgsService').GetStore().GetAccount().accountAurumBalanceChanged.disconnect(self.on_plex_amount_changed)
        walletSignals.on_personal_isk_balance_changed.disconnect(self.on_personal_isk_balance_changed)
        on_skin_listing_expired.disconnect(self._on_skin_listing_expired)
        self.on_size_changed.disconnect(self.on_size_changed_signal)

    def connect_signals(self):
        sm.GetService('vgsService').GetStore().GetAccount().accountAurumBalanceChanged.connect(self.on_plex_amount_changed)
        walletSignals.on_personal_isk_balance_changed.connect(self.on_personal_isk_balance_changed)
        on_skin_listing_expired.connect(self._on_skin_listing_expired)
        self.on_size_changed.connect(self.on_size_changed_signal)

    def on_personal_isk_balance_changed(self, balance, change):
        self.update_buttons()

    def on_plex_amount_changed(self, *args):
        self.update()

    def _on_skin_listing_expired(self, listing_id):
        if self.listing and self.listing.identifier == listing_id and not self._expired:
            self._set_expired()

    def on_size_changed_signal(self, width, height):
        if self.made_by_character_info and self.listed_by_character_info and self.button_group:
            w1 = self.made_by_character_info.default_width
            w2 = self.listed_by_character_info.default_width
            w3 = self.button_group.width
            treshold = width - w1 - w2 - w3 - 32
            use_compact_mode = treshold < 0
            self.made_by_character_info.compact_mode = use_compact_mode
            self.listed_by_character_info.compact_mode = use_compact_mode
            if self.targeted_at_info:
                self.targeted_at_info.compact_mode = use_compact_mode
        self.cost_info_container.width = max(self.cost_info.width, self.buyers_fee_cost_info.width)

    def construct_layout(self):
        self.construct_character_info()
        self.construct_targeted_at_info()
        self.construct_buttons()
        self.construct_cost_info()
        self.construct_share_icon()
        self.construct_name_and_tier_cont()
        self.construct_ship_name()
        self.update()
        if self._expired:
            self._set_expired(animate=False)
        self.on_size_changed_signal(*self.GetAbsoluteSize())

    def construct_ship_name(self):
        self.ship_name = ShipName(name='ship_name', parent=self, align=Align.CENTERTOP)

    def construct_character_info(self):
        self.character_info_container = ContainerAutoSize(name='character_info_container', parent=self, align=Align.BOTTOMLEFT, height=64)
        self.made_by_character_info = MadeByCharacterInfo(name='made_by_character_info', parent=self.character_info_container, align=Align.TOLEFT)
        self.listed_by_character_info = ListedByCharacterInfo(name='listed_by_character_info', parent=self.character_info_container, align=Align.TOLEFT, padLeft=16)

    def construct_targeted_at_info(self):
        self.targeted_at_info_container = ContainerAutoSize(name='targeted_at_info_container', parent=self, align=Align.BOTTOMLEFT, height=64, top=80)
        if self.listing.is_targeted_at_any_character:
            self.targeted_at_info = TargetedAtCharacterInfo(name='targeted_at_info', parent=self.targeted_at_info_container, align=Align.TOLEFT)
            self.targeted_at_info.character_id = self.listing.target.target_id
            return
        if self.listing.is_targeted_at_any_organization:
            self.targeted_at_info = OrganizationInfo(name='targeted_at_info', parent=self.targeted_at_info_container, align=Align.TOLEFT, organization_id=self.listing.target.target_id)

    def construct_name_and_tier_cont(self):
        name_and_tier_cont = ContainerAutoSize(name='name_and_tier_cont', parent=self, align=Align.CENTERBOTTOM, width=TierIndicator.default_width, top=104)
        name_and_link = Container(name='name_and_link_cont', parent=name_and_tier_cont, align=Align.TOTOP, height=30)
        carbonui.TextHeadline(parent=name_and_link, align=Align.CENTER, text=self.listing.skin_design.name, color=TextColor.HIGHLIGHT)
        carbonui.TextBody(parent=name_and_tier_cont, align=Align.TOTOP, text=self.listing.skin_design.line_name, color=TextColor.HIGHLIGHT, textAlign=TextAlign.CENTER)
        self.tier_indicator = TierIndicator(parent=name_and_tier_cont, align=Align.TOTOP, tier_level=self.listing.skin_design.tier_level, padTop=8)

    def construct_cost_info(self):
        self.cost_info_container = ContainerAutoSize(name='cost_info_container', parent=self, align=Align.BOTTOMRIGHT, minWidth=self.buy_or_cancel_btn.width, height=100, top=44)
        self.buyers_fee_cost_info = BuyersFeeCostInfo(name='buyers_fee_cost_info', parent=self.cost_info_container, align=Align.TOBOTTOM, cost=self.listing.price, listing=self.listing, minWidth=self.buy_or_cancel_btn.width, display=False)
        self.cost_info = CostInfo(name='cost_info', parent=self.cost_info_container, align=Align.TOBOTTOM, cost=self.listing.price, currency=self.listing.currency, minWidth=self.buy_or_cancel_btn.width)

    def construct_share_icon(self):
        share_btn = ButtonIcon(parent=self.buttonCont, align=Align.TORIGHT, texturePath='res:/UI/Texture/classes/HyperNet/hyperlink_icon.png', hint=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/DragToShareShipSkinListing'), state=uiconst.UI_NORMAL, func=self.on_share_button_click, iconSize=28, padRight=4)
        share_btn.MakeDragObject()
        share_btn.GetDragData = lambda : SkinListingDragData(self.listing)

    def construct_buttons(self):
        self.buttonCont = ContainerAutoSize(name='button_container', parent=self, align=Align.BOTTOMRIGHT, height=40)
        self.button_group = ButtonGroup(parent=self.buttonCont, align=Align.TORIGHT, density=Density.EXPANDED, button_size_mode=ButtonSizeMode.DYNAMIC)
        if self.is_buy_button():
            buy_or_cancel_btn_func = self.on_buy_button
            buy_or_cancel_btn_label = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/BuySkin')
        else:
            buy_or_cancel_btn_func = self.on_cancel_button
            buy_or_cancel_btn_label = GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/RemoveListing')
        self.buy_or_cancel_btn = Button(parent=self.button_group, align=Align.BOTTOMRIGHT, label=buy_or_cancel_btn_label, func=buy_or_cancel_btn_func, variant=ButtonVariant.PRIMARY)
        self.buy_or_cancel_btn.LoadTooltipPanel = self.LoadBuyButtonTooltipPanel

    def LoadBuyButtonTooltipPanel(self, tooltipPanel, *args):
        if not self.buy_or_cancel_btn.hint:
            return
        tooltipPanel.columns = 1
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.AddLabelMedium(text=self.buy_or_cancel_btn.hint, wrapWidth=300, color=eveColor.DANGER_RED)
        if self.listing.currency == Currency.PLEX and not self.has_enough_plex:
            tooltipPanel.pickState = PickState.ON
            button_group = ButtonGroup(parent=tooltipPanel, align=Align.TOTOP, button_size_mode=ButtonSizeMode.DYNAMIC, padTop=8)
            Button(parent=button_group, label=GetByLabel('UI/Wallet/BuyMore'), func=self.on_buy_more_plex_button, texturePath=eveicon.plex, style=ButtonStyle.MONETIZATION)

    def on_buy_more_plex_button(self, *args):
        buy_missing_plex_dialog = BuyMissingPlexDialog(required_amount=self.listing.price)
        buy_missing_plex_dialog.ShowModal()

    def is_buy_button(self):
        return self.listing.seller_id != session.charid

    def on_share_button_click(self, *args):
        try:
            link = create_link(listing_id=self.listing.identifier, name=self.listing.name)
            blue.clipboard.SetClipboardData(link)
            ShowQuickMessage(GetByLabel('UI/Personalization/ShipSkins/SKINR/LinkCopiedToClipboard'))
        except OSError as e:
            ShowQuickMessage(GetByLabel('UI/Personalization/ShipSkins/SKINR/LinkClipboardError'))

    def on_cancel_button(self, *args):
        if uicore.Message('ConfirmRemoveSkinListing', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        try:
            error = get_ship_skin_trading_svc().cancel_listing(listing_id=self.listing.identifier)
            if error:
                ShowQuickMessage(GetByLabel(get_listing_error_text(error)))
        except Exception as e:
            raise RuntimeError('Unsupported error occurred during listing cancellation: %s' % e)

    def on_buy_button(self, *args):
        if self.is_allowed_to_purchase:
            dialogue = BuySkinDialogue(listing=self.listing)
            dialogue.ShowModal()

    def appear(self):
        self.state = uiconst.UI_PICKCHILDREN
        animations.FadeTo(self, 0.0, 1.0, duration=0.3)

    def disappear(self):
        self.state = uiconst.UI_DISABLED
        animations.FadeTo(self, self.opacity, 0.0, duration=0.3)

    def update(self):
        self.update_character_info()
        self.update_buttons()
        self.update_ship_name()
        self.update_buyer_fee_async()

    def update_character_info(self):
        self.made_by_character_info.character_id = self.listing.skin_design.creator_character_id
        self.listed_by_character_info.character_id = self.listing.seller_id

    def update_buttons(self):
        if self.listing.seller_id == session.charid:
            self.buy_or_cancel_btn.style = ButtonStyle.NORMAL
            self.buy_or_cancel_btn.hint = None
            return
        if self.listing.is_targeted_at_another_character:
            self.buy_or_cancel_btn.style = ButtonStyle.DANGER
            self.buy_or_cancel_btn.hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/TargetedAtAnotherCharacter')
            return
        if self.listing.is_targeted_at_another_organization:
            self.buy_or_cancel_btn.style = ButtonStyle.DANGER
            self.buy_or_cancel_btn.hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/TargetedAtAnotherOrganization')
            return
        if not self.has_sufficient_funds():
            self.buy_or_cancel_btn.style = ButtonStyle.DANGER
            self.buy_or_cancel_btn.hint = self.insufficient_funds_hint
            return
        self.buy_or_cancel_btn.style = ButtonStyle.NORMAL
        self.buy_or_cancel_btn.hint = None

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

    def update_ship_name(self):
        self.ship_name.ship_type_id = self.listing.skin_design.ship_type_id if self.listing else None

    def has_sufficient_funds(self):
        if self.listing.seller_id == session.charid:
            return True
        if self.requires_evermarks and not self.has_enough_evermarks:
            return False
        if self.listing.currency == Currency.ISK:
            return self.has_enough_isk
        if self.listing.currency == Currency.PLEX:
            return self.has_enough_plex
        return False

    @property
    def has_enough_plex(self):
        return sm.GetService('vgsService').GetPLEXBalance() >= self.listing.price

    @property
    def requires_evermarks(self):
        return self._buyer_fee_amount is not None

    @property
    def has_enough_evermarks(self):
        return sm.GetService('loyaltyPointsWalletSvc').GetCharacterEvermarkBalance() >= self._buyer_fee_amount

    @property
    def has_enough_isk(self):
        return sm.GetService('wallet').GetWealth() >= self.listing.price

    @property
    def is_allowed_to_purchase(self):
        if self.listing.is_targeted_at_another_character or self.listing.is_targeted_at_another_organization:
            return False
        return self.has_sufficient_funds()

    def update_buyer_fee_async(self):
        self.kill_update_buyer_fee_thread()
        self._update_thread = uthread2.start_tasklet(self.update_buyer_fee)

    def update_buyer_fee(self):
        self._buyer_fee_amount = self.get_buyer_fee_amount()
        self.buyers_fee_cost_info.buyer_fee_amount = self._buyer_fee_amount
        if self._buyer_fee_amount is None:
            return
        self.update_buttons()

    def get_buyer_fee_amount(self):
        if self.listing is None:
            return
        buyer_fee, error = get_ship_skin_trading_svc().get_buyer_fee_for_listing(self.listing)
        if error:
            ShowQuickMessage(GetByLabel(get_listing_error_text(error)))
            return
        if buyer_fee.lp_amount > 0:
            return buyer_fee.lp_amount

    def _set_expired(self, animate = True):
        self._expired = True
        self.buy_or_cancel_btn.disable(animate=animate)

    def OnCharacterLPBalanceChange_Local(self, issuerCorpID, lpBefore, lpAfter):
        if issuerCorpID == corpHeraldry:
            self.update_buyer_fee_async()
