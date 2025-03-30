#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fastcheckout\client\offerEntry.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.vgs.const import COLOR_PLEX
from fastcheckout.client.offerinfopanels.plexOffersInfoPanel import PlexOffersInfoPanel
from fastcheckout.client.purchasepanels.purchaseButton import PurchaseButton
from fastcheckout.const import OFFER_ENTRY_WIDTH, FRAME_COLOR, OFFER_ENTRY_COLOR
from localization import GetByLabel

class OfferEntry(Container):
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOLEFT
    default_width = OFFER_ENTRY_WIDTH

    def ApplyAttributes(self, attributes):
        super(OfferEntry, self).ApplyAttributes(attributes)
        self.offer = attributes.get('offer', None)
        self.purchase_func = attributes.get('func', None)
        self.base_price = attributes.get('basePrice', None)
        self.base_quantity = attributes.get('baseQuantity', None)
        self.is_on_sale = 'savings' in self.offer and self.offer['savings'] > 0 or self.offer['baseQuantity'] < self.offer['quantity']
        self.savings_label = None
        self.construct_layout()
        self.set_labels()

    def construct_layout(self):
        Container(name='OverFlowContainer', parent=self, align=uiconst.TOTOP, height=20)
        self.message_container = Container(name='MessageContainer', parent=self, align=uiconst.TOBOTTOM, height=20, bgColor=COLOR_PLEX, opacity=0)
        self.message_label = Label(name='TopMessageLabel', parent=self.message_container, align=uiconst.CENTER, uppercase=True, fontsize=12, color=Color.BLACK, bold=True)
        main_container = Container(name='MainContainer', parent=self, align=uiconst.TOALL, bgColor=OFFER_ENTRY_COLOR)
        PlexOffersInfoPanel(parent=main_container, offer=self.offer, basePrice=self.base_price, baseQuantity=self.base_quantity, align=uiconst.TOALL, isOnSale=self.is_on_sale)
        self.frame = Frame(parent=main_container, color=FRAME_COLOR, idx=1)
        PurchaseButton(name='buyPlexOfferButton', parent=Container(name='ButtonContainer', parent=main_container, align=uiconst.TOBOTTOM, height=30, top=10), align=uiconst.CENTER, width=110, height=29, text=GetByLabel('UI/FastCheckout/Buy'), fontsize=18, func=lambda *args: self.purchase_func(self.offer))

    def set_labels(self):
        if 'highlight' in self.offer and self.offer['highlight']:
            self.show_message()
            self.frame.SetRGBA(*COLOR_PLEX)
            self.message_label.SetText(GetByLabel('UI/FastCheckout/MinimumRequired'))
        elif 'Popular' in self.offer['tags']:
            self.show_message()
            self.message_label.SetText(GetByLabel('UI/FastCheckout/MostPopular'))

    def show_message(self):
        self.message_container.SetOpacity(1)
