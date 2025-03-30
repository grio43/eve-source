#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\controllers\offerPurchase.py
from eve.client.script.ui.shared.vgs.currency import OFFER_CURRENCY_PLEX
from eve.client.script.ui.shared.vgs.events import LogPurchaseOffer
import evetypes
import signals
from eve.client.script.ui.view.aurumstore.shared.offerpricing import get_offer_price_in_currency
from inventorycommon.const import categoryShipSkin

class PurchaseFailureError(Exception):
    pass


class NotEnoughAurumError(PurchaseFailureError):
    pass


class OfferPurchaseController(object):

    def __init__(self, offer, store):
        self.offer = offer
        self.store = store
        self.account = store.GetAccount()
        self.onAurBalanceChanged = signals.Signal(signalName='onAurBalanceChanged')
        self.account.SubscribeToAurumBalanceChanged(self.onAurBalanceChanged)

    @property
    def balance(self):
        return self.account.GetAurumBalance()

    @property
    def totalPrice(self):
        return get_offer_price_in_currency(self.offer, OFFER_CURRENCY_PLEX)

    def Buy(self, toCharacterID = None, message = None):
        if self.balance < self.totalPrice:
            raise NotEnoughAurumError()
        try:
            self.store.BuyOffer(self.offer, qty=1, toCharacterID=toCharacterID, message=message)
        except Exception as e:
            raise PurchaseFailureError(e)
        else:
            LogPurchaseOffer(self.offer.id, 1)

    def IsProductActivatable(self):
        if len(self.offer.productQuantities) != 1:
            return False
        return evetypes.GetCategoryID(self.activatableProductTypeID) == categoryShipSkin

    @property
    def activatableProductTypeID(self):
        return self.offer.productQuantities.values()[0].typeId
