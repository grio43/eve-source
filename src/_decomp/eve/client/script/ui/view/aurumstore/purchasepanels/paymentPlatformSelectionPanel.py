#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\purchasepanels\paymentPlatformSelectionPanel.py
from carbonui import uiconst
from eve.client.script.ui.shared.vgs.kiringPaymentProvider import get_element_for_payment_provider
from eve.client.script.ui.view.aurumstore.purchasepanels.basePurchasePanel import BasePurchasePanel
from eve.client.script.ui.view.aurumstore.shared.paymentselector import PaymentSelector
from kiring.client.apigateway import KIRING_PAYMENT_OPTIONS

class PaymentPlatformSelectionPanel(BasePurchasePanel):

    def ApplyAttributes(self, attributes):
        super(PaymentPlatformSelectionPanel, self).ApplyAttributes(attributes)
        defaultValue = attributes.defaultValue
        selectorOptionsDict = {paymentOptionId:get_element_for_payment_provider(paymentOptionId)(parent=self, align=uiconst.CENTER) for name, paymentOptionId in KIRING_PAYMENT_OPTIONS}
        self.selector = PaymentSelector(parent=self, optionsDict=selectorOptionsDict, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, defaultValue=defaultValue)

    def GetSelectedPaymentMethod(self):
        return self.selector.GetSelectedValue()
