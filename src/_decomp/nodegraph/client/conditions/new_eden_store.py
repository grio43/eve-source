#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\new_eden_store.py
from nodegraph.client.conditions.base import Condition

class CanPurchaseAnyOffers(Condition):
    atom_id = 586

    def __init__(self, offer_list = None, **kwargs):
        super(Condition, self).__init__(**kwargs)
        self.offer_list = offer_list

    @staticmethod
    def _can_purchase_offer(offer_id):
        offer_id = 'VEVC-{}'.format(offer_id)
        response = sm.RemoteSvc('storeManager').can_purchase_offer(offer_id)
        if response:
            return response['canPurchase']
        return False

    def validate(self, **kwargs):
        if not self.offer_list:
            return None
        for offer in self.offer_list:
            if self._can_purchase_offer(offer):
                return True

        return False
