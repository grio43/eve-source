#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\vgs\client\vgsClient.py
import logging
from vgs.common.const import PLX_CURRENCY, GMS_CURRENCY, INGAME_STORE_ID
from vgs.common.utils import create_offer_from_json, create_category_from_json, create_product_from_json
log = logging.getLogger(__name__)

class StoreUnavailableError(Exception):
    pass


class PurchaseFailedError(Exception):
    pass


class VgsClient:

    def __init__(self):
        self.available = True

    def clear_cache(self):
        self.available = True

    def get_plex_account_balance(self):
        balance = sm.RemoteSvc('vaultManager').get_account_balance(PLX_CURRENCY)
        return balance or 0

    def get_gem_account_balance(self):
        balance = sm.RemoteSvc('vaultManager').get_account_balance(GMS_CURRENCY)
        return balance or 0

    def get_offers(self, store_id = INGAME_STORE_ID):
        if not self.available:
            raise StoreUnavailableError()
        offers = sm.RemoteSvc('storeManager').get_offers(store_id)
        if not offers:
            self.available = False
            raise StoreUnavailableError()
        return [ create_offer_from_json(json) for json in offers if 'products' in json and len(json['products']) ]

    def get_categories(self, store_id = INGAME_STORE_ID):
        if not self.available:
            raise StoreUnavailableError()
        categories = sm.RemoteSvc('storeManager').get_categories(store_id)
        if not categories:
            self.available = False
            raise StoreUnavailableError()
        return [ create_category_from_json(json) for json in categories ]

    def get_products(self, store_id = INGAME_STORE_ID):
        if not self.available:
            raise StoreUnavailableError()
        products = sm.RemoteSvc('storeManager').get_products(store_id)
        if not products:
            self.available = False
            raise StoreUnavailableError()
        return [ create_product_from_json(json) for json in products ]

    def buy_offer(self, offer_id, currency, qty = 1, to_character_id = None, message = None, is_game_time = False, store_id = INGAME_STORE_ID):
        result = sm.RemoteSvc('storeManager').buy_offer(offer_id, currency, qty, from_character_id=session.charid, to_character_id=to_character_id, message=message, is_game_time=is_game_time, store_id=INGAME_STORE_ID)
        if not result:
            raise PurchaseFailedError()
        return result
