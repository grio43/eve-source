#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\controllers\test\test_offerPurchase.py
from eve.client.script.ui.shared.vgs.controllers.offerPurchase import OfferPurchaseController, PurchaseFailureError
import mock
import unittest
from testsuites.testcases import ClientTestCase
from vgs.client.store import Store
from vgs.client.vgsClient import PurchaseFailedError
from vgs.common.utils import Offer, ProductQuantity, OfferPricing
OFFER = Offer(id=101, name='offer name', description='offer description', href='offer href', offerPricings=[OfferPricing('PLX', 1001.0, 9999)], goodsID='123123', canPurchase=True, singlePurchase=True, imageUrl='image url', productQuantities={1: ProductQuantity(10, 1, 'product name', '')}, categories=[], label='label')

class OfferPurchaseControllerTest(ClientTestCase):

    def setUp(self):
        super(OfferPurchaseControllerTest, self).setUp()
        self.store = mock.Mock(spec=Store)
        self.controller = OfferPurchaseController(OFFER, self.store)

    @unittest.skip('This test fails and needs fixing')
    def test_PurchaseHappyPath(self):
        self.controller.Buy()
        self.store.BuyOffer.assert_called_once_with(OFFER, quantity=1)

    def test_PurchaseFailure(self):
        self.store.BuyOffer.side_effect = PurchaseFailedError()
        with self.assertRaises(PurchaseFailureError):
            self.controller.Buy()


if __name__ == '__main__':
    unittest.main()
