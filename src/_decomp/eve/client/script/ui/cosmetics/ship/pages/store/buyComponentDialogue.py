#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\buyComponentDialogue.py
import carbonui
import eveformat
import eveicon
import uthread2
from carbonui import Align, AxisAlignment, ButtonStyle, ButtonVariant, Density, TextColor, TextHeader, uiconst, TextAlign, PickState
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.window import Window
from carbonui.decorative.divider_line import DividerLine
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from cosmetics.client.shipSkinComponentTradingSvc import get_ship_skin_component_trading_svc
from cosmetics.client.ships.skins.errors import get_listing_error_text
from cosmetics.common.ships.skins.util import Currency
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.infoNotice import InfoNotice
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.controls.buyerFee import BuySKINBuyerFee
from eve.client.script.ui.cosmetics.ship.pages.cards.componentListingCard import ComponentListingCard
from eve.client.script.ui.cosmetics.ship.pages.store import storeSignals
from eve.client.script.ui.shared.neocom.wallet.buyMissingPlexDialog import BuyMissingPlexDialog
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException

class BuyComponentDialogue(Window):
    default_windowID = 'BuyComponentDialogue'
    default_iconNum = 'res:/UI/Texture/WindowIcons/paint_tool.png'
    default_caption = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/BuyElement')
    default_fixedWidth = 515
    default_isMinimizable = False
    default_isStackable = False
    default_isCollapseable = False

    def __init__(self, listing, *args, **kwargs):
        super(BuyComponentDialogue, self).__init__(*args, **kwargs)
        self.listing = listing
        self.buy_thread = None
        self.construct_layout()

    def Close(self, setClosed = False, *args, **kwargs):
        try:
            self.kill_threads()
        finally:
            super(BuyComponentDialogue, self).Close(setClosed, *args, **kwargs)

    def kill_threads(self):
        if self.buy_thread is not None:
            self.buy_thread.kill()
            self.buy_thread = None

    def construct_content_cont(self):
        return ContainerAutoSize(parent=self.sr.maincontainer, name='main', align=uiconst.TOTOP, padding=self.content_padding)

    def construct_layout(self):
        self.content.on_size_changed.connect(self.on_content_size_changed)
        self.construct_card()
        name = self.listing.name_with_quantity if hasattr(self.listing, 'name_with_quantity') else ''
        carbonui.TextHeader(parent=self.content, align=Align.TOTOP, text=name, textAlign=TextAlign.CENTER, padTop=-16)
        DividerLine(parent=self.content, align=Align.TOTOP, padTop=32)
        self.construct_buyer_fee()
        self.construct_price()
        self.construct_quantity()
        DividerLine(parent=self.content, align=Align.TOTOP, padTop=16)
        self.construct_activate_now_checkbox()
        self.construct_item_delivery_notice()
        self.construct_buttons()
        self.update()

    def construct_activate_now_checkbox(self):
        self.activate_now_checkbox = Checkbox(name='activate_now_checkbox', parent=self.content, align=Align.TOTOP, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ActivateNow'), hint=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ActivateNowHint'), padTop=16, checked=True, callback=self.on_activate_now_checkbox)

    def on_activate_now_checkbox(self, *args):
        self.update_item_delivery_notice()

    def on_content_size_changed(self, width, height):
        _, height = self.GetWindowSizeForContentSize(height=height)
        self.SetFixedHeight(height)

    def construct_card(self):
        card_container = ContainerAutoSize(name='card_container', parent=self.content, align=Align.TOTOP, padTop=16)
        card = BuyComponentListingCard(name='card', parent=card_container, align=Align.CENTERTOP, listing=self.listing)
        card._on_selected = lambda *args, **kwargs: None
        card.is_selected = True

    def construct_item_delivery_notice(self):
        self.item_delivery_notice = InfoNotice(name='item_delivery_notice', parent=self.content, align=uiconst.TOTOP, labelText=GetByLabel('UI/Personalization/ShipSkins/SKINR/ItemDeliveryNotice'), padTop=16)
        self.item_delivery_notice.noticeLabel.maxLines = None

    def construct_price(self):
        price_container = Container(name='price_container', parent=self.content, align=Align.TOTOP, height=32, padTop=16)
        TextHeader(name='price_label', parent=price_container, align=Align.TOLEFT, text=GetByLabel('UI/Market/Marketbase/Price'), bold=True, padTop=4)
        self.amount_label = TextHeader(name='amount_label', parent=price_container, align=Align.TORIGHT, state=uiconst.UI_NORMAL, bold=True, padTop=4)
        icon_container = Container(name='icon_container', parent=price_container, align=Align.TORIGHT, width=16, padRight=4)
        self.currency_icon = Sprite(name='currency_icon', parent=icon_container, align=Align.CENTER, pos=(0, 0, 16, 16))

    def construct_buyer_fee(self):
        self.buyer_fee = BuySKINBuyerFee(name='buyer_fee', parent=self.content, align=Align.TOTOP, padTop=16, display=False)

    def construct_quantity(self):
        quantity_container = Container(name='quantity_container', parent=self.content, align=Align.TOTOP, height=32, padTop=8)
        TextHeader(name='quantity_label', parent=quantity_container, align=Align.TOLEFT, text=GetByLabel('UI/Common/Quantity'), bold=True, padTop=4)
        quantity_edit_max_value = self.listing.quantity
        if quantity_edit_max_value < 0:
            quantity_edit_max_value = SingleLineEditInteger.default_maxValue
        self.quantity_edit = SingleLineEditInteger(name='quantity_edit', parent=quantity_container, align=Align.TORIGHT, density=Density.EXPANDED, minValue=1, maxValue=quantity_edit_max_value, setvalue=1, OnChange=self.on_input_change, width=125)

    def on_input_change(self, *args):
        self.update()

    def construct_buttons(self):
        button_group = ButtonGroup(name='button_group', parent=self.content, align=Align.TOTOP, button_alignment=AxisAlignment.CENTER, density=Density.EXPANDED, button_size_mode=ButtonSizeMode.STRETCH, padTop=16)
        self.buy_button = Button(name='buy_button', label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/Buy'), variant=ButtonVariant.PRIMARY, func=self.on_buy_button)
        button_group.add_button(self.buy_button)
        self.cancel_button = Button(name='cancel_button', label=GetByLabel('UI/Common/Buttons/Cancel'), variant=ButtonVariant.GHOST, func=self.on_cancel_button)
        button_group.add_button(self.cancel_button)

    def update(self):
        self.update_buyer_fee()
        self.update_amount_label()
        self.update_currency_icon()
        self.update_buttons()
        self.update_item_delivery_notice()

    def update_amount_label(self):
        self.amount_label.text = eveformat.number(self.total_price)
        if self.listing.currency == Currency.PLEX and self.has_enough_plex:
            self.amount_label.color = TextColor.NORMAL
            self.amount_label.hint = None
        elif self.listing.currency == Currency.ISK and self.has_enough_isk:
            self.amount_label.color = TextColor.NORMAL
            self.amount_label.hint = None
        else:
            self.amount_label.color = TextColor.DANGER
            self.amount_label.hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InsufficientFunds')

    def update_currency_icon(self):
        self.currency_icon.hint = self.get_currency_hint()
        self.currency_icon.texturePath = self.get_currency_icon()
        self.currency_icon.color = self.get_currency_color()

    def update_buttons(self):
        self.buy_button.LoadTooltipPanel = self.load_buy_button_tooltip_panel
        self.buy_button.style = self.get_buy_button_style()

    def update_item_delivery_notice(self):
        if hasattr(self, 'item_delivery_notice'):
            self.item_delivery_notice.display = not self.activate_now_checkbox.checked

    def update_buyer_fee(self):
        pass

    def has_sufficient_funds(self):
        if self.listing.currency == Currency.ISK:
            return self.has_enough_isk
        elif self.listing.currency == Currency.PLEX:
            return self.has_enough_plex
        else:
            return False

    @property
    def has_enough_isk(self):
        return sm.GetService('wallet').GetWealth() >= self.get_required_amount()

    @property
    def has_enough_plex(self):
        return sm.GetService('vgsService').GetPLEXBalance() >= self.get_required_amount()

    def get_required_amount(self):
        return self.listing.price * self.purchase_quantity

    def load_buy_button_tooltip_panel(self, tooltip_panel, *args):
        if self.has_sufficient_funds():
            return
        tooltip_panel.columns = 1
        tooltip_panel.LoadStandardSpacing()
        tooltip_panel.AddLabelMedium(text=self.insufficient_funds_hint, wrapWidth=300, color=eveColor.DANGER_RED)
        if self.listing.currency == Currency.PLEX and not self.has_enough_plex:
            tooltip_panel.pickState = PickState.ON
            button_group = ButtonGroup(parent=tooltip_panel, align=Align.TOTOP, button_size_mode=ButtonSizeMode.DYNAMIC, padTop=8)
            Button(parent=button_group, label=GetByLabel('UI/Wallet/BuyMore'), func=self.on_buy_more_plex_button, texturePath=eveicon.plex, style=ButtonStyle.MONETIZATION)

    @property
    def insufficient_funds_hint(self):
        currencies = []
        if self.listing.currency == Currency.ISK and not self.has_enough_isk:
            currencies.append(GetByLabel('UI/Common/ISK'))
        if self.listing.currency == Currency.PLEX and not self.has_enough_plex:
            currencies.append(GetByLabel('UI/Common/PLEX'))
        return u'{base} ({currencies})'.format(base=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InsufficientFunds'), currencies=u'/'.join(currencies))

    def on_buy_more_plex_button(self, *args):
        buy_missing_plex_dialog = BuyMissingPlexDialog(required_amount=self.get_required_amount())
        buy_missing_plex_dialog.ShowModal()
        self.SetModalResult(uiconst.ID_CANCEL)

    def get_buy_button_style(self):
        if self.is_allowed_to_purchase:
            return ButtonStyle.NORMAL
        return ButtonStyle.DANGER

    @property
    def is_allowed_to_purchase(self):
        return self.has_sufficient_funds()

    @property
    def purchase_quantity(self):
        return self.quantity_edit.GetValue()

    def get_currency_hint(self):
        if self.listing.currency == Currency.ISK:
            return GetByLabel('UI/Common/ISK')
        elif self.listing.currency == Currency.PLEX:
            return GetByLabel('UI/Common/PLEX')
        else:
            return None

    def get_currency_icon(self):
        if self.listing.currency == Currency.ISK:
            return eveicon.isk
        elif self.listing.currency == Currency.PLEX:
            return eveicon.plex
        else:
            return None

    def get_currency_color(self):
        if self.listing.currency == Currency.PLEX:
            return eveColor.PLEX_YELLOW
        return eveColor.WHITE

    def on_buy_button(self, *args):
        if self.is_allowed_to_purchase:
            self.buy_thread = uthread2.StartTasklet(self._buy_async)

    def _buy_async(self):
        self.buy_button.busy = True
        self.buy_button.disabled = True
        try:
            error = self.purchase_listing()
            if error:
                ShowQuickMessage(GetByLabel(get_listing_error_text(error)))
            else:
                self.on_buy_success()
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
        finally:
            self.buy_thread = None
            self.buy_button.busy = False
            self.buy_button.disabled = False

    def on_buy_success(self):
        storeSignals.on_component_listing_selected(None)
        self.SetModalResult(uiconst.ID_OK)

    def purchase_listing(self):
        return get_ship_skin_component_trading_svc().purchase_listing(listing=self.listing, quantity=self.quantity, immediately_activate=self.activate_now_checkbox.checked)

    def on_cancel_button(self, *args):
        self.SetModalResult(uiconst.ID_CANCEL)

    @property
    def quantity(self):
        return self.quantity_edit.GetValue()

    @property
    def total_price(self):
        return self.listing.price * self.quantity


class BuyComponentListingCard(ComponentListingCard):

    def get_component_name(self):
        return ''
