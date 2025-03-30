#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fastcheckout\client\offerinfopanels\baseOfferInfoPanel.py
import carbonui.const as uiconst
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.transform import Transform
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.vgs.const import COLOR_PLEX
from eve.client.script.ui.shared.vgs.currency import get_price_text

class BaseOfferInfoPanel(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(BaseOfferInfoPanel, self).ApplyAttributes(attributes)
        self.offer = attributes.get('offer', None)
        self.basePrice = attributes.get('basePrice', None)
        self.base_quantity = attributes.get('baseQuantity', None)
        self.isOnSale = attributes.get('isOnSale', False)

    def construct_name(self):
        text = self.offer.name
        self.offer_name_container = Container(name='OfferNameContainer', parent=self, align=uiconst.TOTOP, height=30, top=20)
        self.offer_name = Label(name='OfferName', parent=self.offer_name_container, align=uiconst.CENTER, color=COLOR_PLEX, fontsize=18, uppercase=True, text=text)

    def construct_icon(self):
        self.iconContainer = Container(name='IconContainer', parent=self, align=uiconst.TOTOP, height=100)

    def construct_price(self):
        self.price_container = Transform(name='OfferPriceContainer', parent=self, align=uiconst.TOTOP, height=25, top=0, scalingCenter=(0.5, 0.5))
        self.offer_price = Label(name='OfferPrice', parent=self.price_container, align=uiconst.CENTER, fontsize=20.45, bold=True, color=Color.WHITE)

    def set_labels(self):
        price_text = get_price_text(self.offer['price'], self.offer['currency'])
        self.offer_price.SetText(price_text)

    def animate_sales(self):
        pass

    def construct_sales_layout(self):
        pass

    def animate_purchase(self):
        pass

    def set_sales_colors(self):
        pass
