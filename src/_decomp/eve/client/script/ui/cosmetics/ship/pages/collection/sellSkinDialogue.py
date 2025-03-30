#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\collection\sellSkinDialogue.py
import eveicon
import math
import uthread2
from carbonui import Align, AxisAlignment, ButtonStyle, ButtonVariant, Density, uiconst
from carbonui import TextBody, TextColor, TextDetail, TextHeader
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.comboEntryData import ComboEntryData
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.window import Window
from carbonui.decorative.divider_line import DividerLine
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from cosmetics.client.ships.skins.errors import get_listing_error_text
from cosmetics.client.shipSkinTradingSvc import get_ship_skin_trading_svc
from cosmetics.common.ships.skins.util import Currency
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship import tradingUtil
from eve.client.script.ui.cosmetics.ship.controls.buyerFee import SellSKINBuyerFee
from eve.client.script.ui.cosmetics.ship.tradingUtil import SellAvailability
from eve.client.script.ui.cosmetics.ship.pages.store.tooltipInfoIcons import HubTaxRateSkillsInfoIcon
from eve.client.script.ui.shared.market.singleLineEditMarketPrice import SingleLineEditMarketPrice
from eve.common.script.util.eveFormat import FmtAmt, FmtISK
from eveui.autocomplete.player.field import CharOrCorpOrAllianceField
from localization import GetByLabel

class SellSkinDialogue(Window):
    __notifyevents__ = ['OnSessionChanged']
    default_windowID = 'SellSkinDialogue'
    default_iconNum = 'res:/UI/Texture/WindowIcons/paint_tool.png'
    default_caption = GetByLabel('UI/Personalization/ShipSkins/SKINR/SellSkin')
    default_fixedWidth = 515
    default_fixedHeight = 480
    default_isMinimizable = False
    default_isStackable = False
    default_isCollapseable = False

    def __init__(self, skin_license, *args, **kwargs):
        super(SellSkinDialogue, self).__init__(*args, **kwargs)
        self.skin_license = skin_license
        self.is_layout_done = False
        self.update_thread = None
        self.sell_skin_thread = None
        self._tax_rate = None
        self._broker_fee = None
        self._buyer_fee_amount = None
        self.construct_layout()
        sm.RegisterNotify(self)

    def Close(self, setClosed = False, *args, **kwargs):
        try:
            self.kill_threads()
            sm.UnregisterNotify(self)
        finally:
            super(SellSkinDialogue, self).Close(setClosed, *args, **kwargs)

    def kill_threads(self):
        self.kill_update_thread()
        self.kill_sell_skin_thread()

    def kill_update_thread(self):
        if self.update_thread is not None:
            self.update_thread.kill()
            self.update_thread = None

    def kill_sell_skin_thread(self):
        if self.sell_skin_thread is not None:
            self.sell_skin_thread.kill()
            self.sell_skin_thread = None

    def construct_layout(self):
        self.content.padding = (32, 32, 32, 32)
        self.construct_duration()
        self.construct_availability()
        self.construct_search()
        self.construct_listing()
        DividerLine(parent=self.content, align=Align.TOTOP, padTop=32)
        self.construct_buyer_fee()
        self.construct_service_fee()
        self.construct_listing_cost()
        self.construct_profit()
        DividerLine(parent=self.content, align=Align.TOTOP, padTop=16)
        self.construct_buttons()
        self.is_layout_done = True
        self.update_async()

    def construct_duration(self):
        duration_container = Container(name='duration_container', parent=self.content, align=Align.TOTOP, height=32)
        TextHeader(name='duration_label', parent=duration_container, align=Align.CENTERLEFT, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/SellListingDuration'), bold=True)
        options = tradingUtil.get_sell_duration_options()
        self.duration_combo = Combo(name='duration_combo', parent=duration_container, align=Align.TORIGHT, options=options, select=options[-1], callback=self.on_input_change, maxVisibleEntries=len(options), width=160)

    def construct_listing(self):
        self.listing_container = Container(name='listing_container', parent=self.content, align=Align.TOTOP, height=32, padTop=16)
        self.construct_copies()
        self.construct_amount()
        self.construct_currency()

    def construct_availability(self):
        availability_container = Container(name='availability_container', parent=self.content, align=Align.TOTOP, height=32, padTop=16)
        TextHeader(name='availability_label', parent=availability_container, align=Align.CENTERLEFT, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/ListingAvailability'), bold=True)
        options = tradingUtil.get_sell_availability_options()
        self.availability_combo = Combo(name='availability_combo', parent=availability_container, align=Align.TORIGHT, options=options, select=options[-1], callback=self.on_availability_change, maxVisibleEntries=len(options), width=160)

    def construct_search(self):
        self.search_container = Container(name='search_container', parent=self.content, align=Align.TOTOP, height=52, padTop=8, display=False)
        header_container = Container(name='header_container', parent=self.search_container, align=Align.TOTOP, height=16)
        Sprite(name='icon', parent=header_container, align=Align.TOLEFT, texturePath=eveicon.pilot_or_organization, color=TextColor.SECONDARY, pos=(0, 0, 16, 16))
        TextDetail(name='label', parent=header_container, align=Align.TOLEFT, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/SellTargetSearchHeader'), color=TextColor.SECONDARY, padLeft=4)
        self.search_field = CharOrCorpOrAllianceField(name='search_field', parent=self.search_container, align=Align.TOTOP, placeholder=GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/SellTargetSearchPlaceholder'), show_suggestions_on_focus=True, padTop=4)
        self.search_field.autocomplete_controller.on_fetch_start.connect(self.on_search_fetch_start)
        self.search_field.autocomplete_controller.on_completed.connect(self.on_search_completed)

    def on_search_fetch_start(self, *args):
        self.update_async()

    def on_search_completed(self, *args):
        self.update_async()

    def construct_copies(self):
        copies_container = ContainerAutoSize(name='copies_container', parent=self.listing_container, align=Align.TOLEFT, height=32)
        TextHeader(name='copies_label', parent=copies_container, align=Align.TOLEFT, text=GetByLabel('UI/Industry/Copies'), bold=True, padTop=4)
        self.copies_edit = SingleLineEditInteger(name='copies_edit', parent=copies_container, align=Align.TOLEFT, density=Density.EXPANDED, width=56, minValue=1, maxValue=self.skin_license.nb_unactivated, setvalue=1, OnChange=self.on_input_change, padLeft=10)

    def construct_amount(self):
        self.amount_container = ContainerAutoSize(name='amount_container', parent=self.listing_container, align=Align.TORIGHT, height=32, padLeft=10)
        self.amount_edit = SingleLineEditMarketPrice(name='amount_edit', parent=self.amount_container, align=Align.TOLEFT, density=Density.EXPANDED, minValue=1, setvalue=10, decimalPlaces=0, OnChange=self.on_input_change, width=160, isTickActivated=False)

    def construct_currency(self):
        currency_container = ContainerAutoSize(name='currency_container', parent=self.listing_container, align=Align.TORIGHT, height=32)
        TextHeader(name='currency_label', parent=currency_container, align=Align.TOLEFT, text=GetByLabel('UI/Market/Marketbase/Price'), bold=True, padTop=4)
        options = [ComboEntryData(label=GetByLabel('UI/Common/ISK'), returnValue=Currency.ISK, icon=eveicon.isk), ComboEntryData(label=GetByLabel('UI/Common/PLEX'), returnValue=Currency.PLEX, icon=eveicon.plex)]
        self.currency_combo = Combo(name='currency_combo', parent=currency_container, align=Align.TOLEFT, options=options, select=Currency.PLEX, callback=self.on_currency_change, maxVisibleEntries=len(options), width=56, padLeft=10)

    def construct_buyer_fee(self):
        self.buyer_fee = SellSKINBuyerFee(name='buyer_fee', parent=self.content, align=Align.TOTOP, padTop=24, display=False)

    def construct_service_fee(self):
        self.service_fee_container = Container(name='service_fee_container', parent=self.content, align=Align.TOTOP, height=18, padTop=20)
        label_container = ContainerAutoSize(name='label_container', parent=self.service_fee_container, align=Align.TOLEFT, state=uiconst.UI_NORMAL, hint=GetByLabel('UI/Personalization/ShipSkins/SKINR/ServiceFeeHint'))
        TextBody(name='service_fee_label', parent=label_container, align=Align.TOLEFT, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/ServiceFee'), color=TextColor.SECONDARY)
        HubTaxRateSkillsInfoIcon(parent=ContainerAutoSize(parent=label_container, align=Align.TOLEFT, padLeft=4), align=Align.CENTERLEFT)
        amount_container = ContainerAutoSize(name='amount_container', parent=self.service_fee_container, align=Align.TORIGHT, state=uiconst.UI_NORMAL, hint=GetByLabel('UI/Personalization/ShipSkins/SKINR/ServiceFeeHint'))
        self.service_fee_amount_label = TextBody(name='service_fee_amount_label', parent=amount_container, align=Align.TOLEFT, color=TextColor.SECONDARY)

    def construct_listing_cost(self):
        listing_cost_container = Container(name='listing_cost_container', parent=self.content, align=Align.TOTOP, height=18, padTop=8)
        label_container = ContainerAutoSize(name='label_container', parent=listing_cost_container, align=Align.TOLEFT, state=uiconst.UI_NORMAL, hint=GetByLabel('UI/Personalization/ShipSkins/SKINR/ListingCostHint'))
        TextBody(name='listing_cost_label', parent=label_container, align=Align.TOLEFT, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/ListingCost'), color=TextColor.SECONDARY)
        amount_container = ContainerAutoSize(name='amount_container', parent=listing_cost_container, align=Align.TORIGHT, state=uiconst.UI_NORMAL, hint=GetByLabel('UI/Personalization/ShipSkins/SKINR/ListingCostHint'))
        self.listing_cost_amount_label = TextBody(name='listing_cost_amount_label', parent=amount_container, align=Align.TOLEFT, color=TextColor.SECONDARY, padLeft=4)

    def construct_profit(self):
        profit_container = Container(name='profit_container', parent=self.content, align=Align.TOTOP, height=28, padTop=16)
        TextHeader(name='profit_label', parent=profit_container, align=Align.TOLEFT, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/TotalProfit'), bold=True)
        self.profit_amount_label = TextHeader(name='profit_amount_label', parent=profit_container, align=Align.TORIGHT, bold=True, padLeft=4)
        currency_icon_container = Container(name='currency_icon_container', parent=profit_container, align=Align.TORIGHT, width=20)
        self.currency_icon = Sprite(name='currency_icon', parent=currency_icon_container, align=Align.CENTER, pos=(0, 0, 20, 20), padBottom=4)

    def construct_buttons(self):
        button_group = ButtonGroup(name='button_group', parent=self.content, align=Align.TOBOTTOM, button_alignment=AxisAlignment.CENTER, density=Density.EXPANDED, button_size_mode=ButtonSizeMode.STRETCH)
        self.sell_button = Button(name='sell_button', label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Collection/Sell'), variant=ButtonVariant.PRIMARY, func=self.on_sell_button)
        button_group.add_button(self.sell_button)
        self.cancel_button = Button(name='cancel_button', label=GetByLabel('UI/Common/Buttons/Cancel'), variant=ButtonVariant.GHOST, func=self.on_cancel_button)
        button_group.add_button(self.cancel_button)

    def on_input_change(self, *args):
        self.update_async()

    def on_availability_change(self, combobox, key, value):
        self.search_container.display = value == SellAvailability.SPECIFIC
        self.update_async()

    def on_currency_change(self, *args):
        self.update_amount_edit()
        self.update_async()

    @uthread2.debounce(wait=0.2)
    def update_async(self):
        if not self.is_layout_done:
            return
        self.kill_update_thread()
        self.update_thread = uthread2.start_tasklet(self.update)

    def update(self):
        self.update_fee_and_tax_values()
        self.update_buyer_fee()
        self.update_service_fee()
        self.update_listing_cost()
        self.update_profit()
        self.update_currency()
        self.update_buttons()
        self.update_size()

    def update_fee_and_tax_values(self):
        self._tax_rate = self.get_tax_rate()
        self._broker_fee = self.get_broker_fee()
        self._buyer_fee_amount = self.get_buyer_fee_amount()

    def update_buyer_fee(self):
        self.buyer_fee.amount = self.buyer_fee_amount

    def update_service_fee(self):
        if self.tax_rate is None:
            self.service_fee_amount_label.text = None
            return
        self.service_fee_amount_label.text = '{tax}%'.format(tax=self.tax_rate)
        self.service_fee_amount_label.color = eveColor.SUCCESS_GREEN if self.tax_rate == 0 else TextColor.SECONDARY

    def update_listing_cost(self):
        if self.broker_fee is None:
            self.listing_cost_amount_label.text = None
            return
        self.listing_cost_amount_label.text = FmtISK(-self.broker_fee)
        self.listing_cost_amount_label.color = eveColor.SUCCESS_GREEN if self.broker_fee == 0 else TextColor.SECONDARY

    def update_profit(self):
        if self.tax_rate is None or self.broker_fee is None:
            self.profit_amount_label.text = None
            return
        tax_rate_percent = self.tax_rate / 100.0
        if self.currency == Currency.PLEX:
            profit = math.floor(self.price - self.price * tax_rate_percent)
            self.profit_amount_label.text = FmtAmt(profit)
        else:
            profit = self.price - self.price * tax_rate_percent - self.broker_fee
            self.profit_amount_label.text = FmtISK(profit)
        self.profit_amount_label.color = self.get_profit_text_color(profit)

    def get_profit_text_color(self, profit):
        if profit > 0:
            return TextColor.SUCCESS
        elif profit < 0:
            return TextColor.DANGER
        else:
            return TextColor.NORMAL

    def update_currency(self):
        if self.currency == Currency.ISK:
            self.currency_icon.texturePath = eveicon.isk
            self.currency_icon.color = eveColor.WHITE
        elif self.currency == Currency.PLEX:
            self.currency_icon.texturePath = eveicon.plex
            self.currency_icon.color = eveColor.PLEX_YELLOW

    def update_availabilities(self):
        select = self.availability_combo.selectedValue
        options = tradingUtil.get_sell_availability_options()
        self.availability_combo.LoadOptions(options, select)
        self.search_container.display = self.availability_combo.selectedValue == SellAvailability.SPECIFIC

    def update_amount_edit(self):
        value = self.amount
        if self.currency == Currency.ISK:
            self.amount_edit.decimalPlaces = 2
            self.amount_edit.ActivateTickAlignment()
        elif self.currency == Currency.PLEX:
            self.amount_edit.decimalPlaces = 0
            self.amount_edit.DeactivateTickAlignment()
        self.amount_edit.SetValue(value, docallback=False)

    def update_buttons(self):
        if self.is_valid:
            self.sell_button.style = ButtonStyle.NORMAL
            self.sell_button.hint = None
            return
        self.sell_button.style = ButtonStyle.DANGER
        if not self.has_sufficient_funds:
            self.sell_button.hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InsufficientISKFunds')
        elif not self.has_valid_target:
            self.sell_button.hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InvalidListingTarget')

    def update_size(self):
        if self.buyer_fee_amount:
            if self.sell_availability == SellAvailability.SPECIFIC:
                self.SetFixedHeight(610)
            else:
                self.SetFixedHeight(550)
        elif self.sell_availability == SellAvailability.SPECIFIC:
            self.SetFixedHeight(540)
        else:
            self.SetFixedHeight(self.default_fixedHeight)

    def on_sell_button(self, *args):
        if self.is_valid:
            self.sell_skin_async()

    def sell_skin_async(self):
        self.kill_sell_skin_thread()
        self.sell_skin_thread = uthread2.StartTasklet(self.sell_skin)

    def sell_skin(self):
        self.sell_button.busy = True
        self.sell_button.disabled = True
        try:
            svc = get_ship_skin_trading_svc()
            error = svc.create_listing(currency=self.currency, price=int(self.amount), skin_hex=self.skin_license.skin_hex, duration_in_seconds=int(self.duration), quantity=int(self.copies), target_id=self.sell_target_type_id)
            if error:
                ShowQuickMessage(GetByLabel(get_listing_error_text(error)))
            else:
                self.SetModalResult(uiconst.ID_OK)
        except Exception as e:
            raise RuntimeError('Unsupported error occurred when creating skin listing: %s' % e)
        finally:
            self.sell_skin_thread = None
            self.sell_button.busy = False
            self.sell_button.disabled = False

    def get_tax_rate(self):
        tax_rate, error = get_ship_skin_trading_svc().get_tax_rate(target_id=self.sell_target_type_id)
        if error:
            self.show_error_message(error)
            return None
        else:
            return tax_rate

    def get_broker_fee(self):
        broker_fees, error = get_ship_skin_trading_svc().get_broker_fees_per_duration(target_id=self.sell_target_type_id)
        if error:
            self.show_error_message(error)
            return None
        else:
            return broker_fees[self.duration]

    def get_buyer_fee_amount(self):
        target_id = self.sell_target_type_id
        if target_id is None:
            return
        else:
            buyer_fee, error = get_ship_skin_trading_svc().get_predicted_buyer_fee(skin_hex=self.skin_license.skin_hex, target_id=target_id)
            if error:
                self.show_error_message(error)
                return
            return buyer_fee.lp_amount

    def on_cancel_button(self, *args):
        self.SetModalResult(uiconst.ID_CANCEL)

    def OnSessionChanged(self, isRemote, session, change):
        if 'corprole' in change or 'corpid' in change or 'allianceid' in change:
            self.Close()

    @uthread2.debounce(wait=0.2)
    def show_error_message(self, error):
        ShowQuickMessage(GetByLabel(get_listing_error_text(error)))

    @property
    def has_sufficient_funds(self):
        if self.broker_fee is None:
            return False
        return sm.GetService('wallet').GetWealth() >= self.broker_fee

    @property
    def has_valid_target(self):
        if self.sell_availability == SellAvailability.SPECIFIC and self.sell_target_type_id is None:
            return False
        return True

    @property
    def tax_rate(self):
        return self._tax_rate

    @property
    def broker_fee(self):
        return self._broker_fee

    @property
    def buyer_fee_amount(self):
        return self._buyer_fee_amount

    @property
    def is_valid(self):
        return self.has_sufficient_funds and self.has_valid_target

    @property
    def currency(self):
        return self.currency_combo.GetValue()

    @property
    def price(self):
        return self.amount * self.copies

    @property
    def amount(self):
        return self.amount_edit.GetValue()

    @property
    def copies(self):
        return self.copies_edit.GetValue()

    @property
    def duration(self):
        return self.duration_combo.GetValue()

    @property
    def sell_availability(self):
        return self.availability_combo.GetValue()

    @property
    def sell_target(self):
        return self.search_field.completed_suggestion

    @property
    def sell_target_type_id(self):
        availability = self.sell_availability
        if availability == SellAvailability.MY_CORPORATION:
            return session.corpid
        if availability == SellAvailability.MY_ALLIANCE:
            return session.allianceid
        if availability == SellAvailability.SPECIFIC:
            sell_target = self.sell_target
            if sell_target:
                return sell_target.owner_id
            return None
