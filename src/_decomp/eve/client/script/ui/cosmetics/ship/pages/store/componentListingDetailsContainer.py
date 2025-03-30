#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\componentListingDetailsContainer.py
import logging
from eveui import Sprite
import eveicon
from carbonui import Align, Density, ButtonStyle, ButtonVariant, uiconst, PickState, TextBody
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from cosmetics.common.ships.skins.util import Currency
from eve.client.script.ui import eveColor
from eve.client.script.ui.cosmetics.ship.controls.componentInfo import ComponentInfo
from eve.client.script.ui.cosmetics.ship.controls.costInfo import CostInfo
from eve.client.script.ui.cosmetics.ship.pages.store.buyComponentDialogue import BuyComponentDialogue
from eve.client.script.ui.shared.neocom.wallet.buyMissingPlexDialog import BuyMissingPlexDialog
from localization import GetByLabel
log = logging.getLogger(__name__)

class ComponentListingDetailsContainer(Container):

    def __init__(self, listing, **kw):
        super(ComponentListingDetailsContainer, self).__init__(**kw)
        self.listing = listing
        self.construct_layout()
        sm.GetService('vgsService').GetStore().GetAccount().accountAurumBalanceChanged.connect(self.on_plex_amount_changed)

    def on_plex_amount_changed(self, *args):
        self.update_buttons()

    def construct_layout(self):
        self.right_cont = ContainerAutoSize(parent=self, align=Align.TORIGHT)
        self.left_cont = Container(name='left_cont', parent=self, clipChildren=True, padRight=8)
        self.construct_buttons()
        self.construct_cost_info()
        self.update()

    def construct_cost_info(self):
        CostInfo(name='cost_info', parent=self.buy_btn, align=Align.TOBOTTOM, cost=self.listing.price, currency=self.listing.currency, top=44)

    def construct_buttons(self):
        button_group = ButtonGroup(parent=self.right_cont, align=Align.BOTTOMRIGHT, density=Density.EXPANDED, button_size_mode=ButtonSizeMode.DYNAMIC)
        Button(parent=button_group, hint=GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'), func=self.on_view_on_market_button, texturePath=eveicon.market_details, variant=ButtonVariant.GHOST)
        self.buy_btn = Button(parent=button_group, label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/BuyElement'), func=self.on_buy_button, variant=ButtonVariant.PRIMARY)
        self.buy_btn.LoadTooltipPanel = self.LoadBuyButtonTooltipPanel

    def update_component_info(self):
        self.left_cont.Flush()
        if not self.listing:
            return
        ComponentInfo(name='component_info', parent=self.left_cont, align=Align.TOBOTTOM, component_data=self.listing.get_component_data(), license_type=self.listing.license_type, runs_remaining=self.listing.bundle_size)
        if self.listing.is_limited_offer():
            self._construct_limited_offer_label()

    def _construct_limited_offer_label(self):
        limited_offer_cont = Container(parent=self.left_cont, height=32, align=Align.TOBOTTOM, padBottom=4)
        icon_container = Container(name='icon_container', parent=limited_offer_cont, align=Align.TOLEFT, pos=(0, 0, 32, 32))
        Sprite(name='icon', parent=icon_container, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath=eveicon.clock, pos=(0, 0, 16, 16))
        name_container = ContainerAutoSize(name='name_container', parent=limited_offer_cont, align=Align.TOLEFT)
        TextBody(name='name_label', parent=name_container, align=Align.CENTER, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/LimitedOffer', valid_until=self.listing.valid_until_seconds), padding=(0, 0, 0, 0))

    def on_view_on_market_button(self, *args):
        sm.GetService('marketutils').ShowMarketDetails(self.listing.component_item_type_id)

    def on_buy_button(self, *args):
        if self.has_sufficient_funds():
            dialogue = BuyComponentDialogue(listing=self.listing)
            dialogue.ShowModal()

    def appear(self):
        self.state = uiconst.UI_PICKCHILDREN
        animations.FadeTo(self, 0.0, 1.0, duration=0.3)

    def disappear(self):
        self.state = uiconst.UI_DISABLED
        animations.FadeTo(self, self.opacity, 0.0, duration=0.3)

    def update(self):
        self.update_component_info()
        self.update_buttons()

    def update_buttons(self):
        if self.has_sufficient_funds():
            self.buy_btn.style = ButtonStyle.NORMAL
        else:
            self.buy_btn.style = ButtonStyle.DANGER

    def LoadBuyButtonTooltipPanel(self, tooltipPanel, *args):
        if self.has_sufficient_funds():
            return
        tooltipPanel.columns = 1
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.AddLabelMedium(text=self.insufficient_funds_hint, wrapWidth=300, color=eveColor.DANGER_RED)
        if self.listing.currency == Currency.PLEX:
            tooltipPanel.pickState = PickState.ON
            button_group = ButtonGroup(parent=tooltipPanel, align=Align.TOTOP, button_size_mode=ButtonSizeMode.DYNAMIC, padTop=8)
            Button(parent=button_group, label=GetByLabel('UI/Wallet/BuyMore'), func=self.on_buy_more_plex_button, texturePath=eveicon.plex, style=ButtonStyle.MONETIZATION)

    @property
    def insufficient_funds_hint(self):
        return u'{base} ({plex})'.format(base=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InsufficientFunds'), plex=GetByLabel('UI/Common/PLEX'))

    def on_buy_more_plex_button(self, *args):
        buy_missing_plex_dialog = BuyMissingPlexDialog(required_amount=self.listing.price)
        buy_missing_plex_dialog.ShowModal()

    def has_sufficient_funds(self):
        if self.listing.currency == Currency.ISK:
            return sm.GetService('wallet').GetWealth() >= self.listing.price
        elif self.listing.currency == Currency.PLEX:
            return sm.GetService('vgsService').GetPLEXBalance() >= self.listing.price
        else:
            return False
