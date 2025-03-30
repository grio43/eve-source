#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\purchasepanels\currencySelectionPanel.py
from carbonui import uiconst
from eve.client.script.ui.shared.vgs.priceTag import PriceTagMedium
from eve.client.script.ui.view.aurumstore.purchasepanels.basePurchasePanel import BasePurchasePanel
from eve.client.script.ui.view.aurumstore.shared.paymentselector import PaymentSelector

class PurchaseCurrencySelectionPanel(BasePurchasePanel):

    def ApplyAttributes(self, attributes):
        super(PurchaseCurrencySelectionPanel, self).ApplyAttributes(attributes)
        self.offer = attributes.offer
        defaultValue = attributes.defaultValue
        onSelect = attributes.onSelect
        self.priceTags = {pricing.currency:PriceTagMedium(align=uiconst.CENTER, currency=pricing.currency, price=pricing.price, basePrice=pricing.basePrice, showBasePrice=False) for pricing in self.offer.offerPricings}
        self.selector = PaymentSelector(parent=self, optionsDict=self.priceTags, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, defaultValue=defaultValue, onSelect=onSelect)

    def GetSelectedCurrency(self):
        return self.selector.GetSelectedValue()

    def SetSelectedCurrency(self, currency):
        self.selector.SelectValue(currency)

    def SetQuantity(self, value):
        for pricing in self.offer.offerPricings:
            priceTag = self.priceTags[pricing.currency]
            priceTag.UpdatePrice(value * pricing.price, value * pricing.basePrice)
