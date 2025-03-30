#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\vgs\client\store.py
import contextlib
import logging
from collections import defaultdict
from eve.common.lib.vgsConst import CATEGORYTAG_GAMETIME, CATEGORYTAG_GEM, CATEGORYTAG_PLEX
from vgs.client.account import Account
from vgs.common.const import INGAME_STORE_ID
log = logging.getLogger(__name__)

class PurchaseInProgressError(Exception):
    pass


class Store:

    def __init__(self, vgs_client, lockImpl, store_id = INGAME_STORE_ID):
        self.vgs_client = vgs_client
        self.store_id = store_id
        self.loading_lock = lockImpl()
        self._reset_variables()
        self.purchase_in_progress = False
        self.account = Account(vgs_client)

    def ClearCache(self):
        self._reset_variables()
        self.account.ClearCache()
        self.vgs_client.clear_cache()

    def _reset_variables(self):
        self.products_by_id = None
        self.offers_by_id = None
        self.offers_by_product_id = None
        self.offers_by_tag_id = None
        self.categories_by_id = None
        self.root_categories_by_id = None
        self.tags_by_id = None

    def GetAccount(self):
        return self.account

    def _prime_search_index(self):
        self.offers_by_product_id = {}
        self.offers_by_tag_id = defaultdict(list)
        for product in self.get_products().itervalues():
            self.offers_by_product_id[product.id] = []

        for offer in self.GetOffers().itervalues():
            for tag in offer.categories:
                if tag in self.tags_by_id.keys():
                    self.offers_by_tag_id[tag].append(offer.id)

            for product_id in offer.productQuantities:
                try:
                    self.offers_by_product_id[product_id].append(offer.id)
                except KeyError:
                    log.debug('_PrimeSearchIndex: productID %s was not found while indexing offer %s', product_id, offer)

    def GetOffers(self):
        if self.offers_by_id is None:
            with self.loading_lock:
                if self.offers_by_id is None:
                    offers = self.vgs_client.get_offers(self.store_id)
                    self.offers_by_id = {offer.id:offer for offer in offers}
        return self.offers_by_id

    def GetOffer(self, offer_id):
        return self.GetOffers()[offer_id]

    def GetProduct(self, product_id):
        return self.get_products()[product_id]

    def get_products(self):
        if self.products_by_id is None:
            self.products_by_id = {product.id:product for product in self.vgs_client.get_products(self.store_id)}
        return self.products_by_id

    def BuyOffer(self, offer, currency, qty = 1, toCharacterID = None, message = None):
        with self._purchase_context():
            result = self.vgs_client.buy_offer(offer.id, currency=currency, qty=qty, to_character_id=toCharacterID, message=message, is_game_time=self.IsGametimeOffer(offer), store_id=self.store_id)
            self.ClearCache()
            return result

    def IsGametimeOffer(self, offer):
        category_tags = self._get_category_tags_for_offer(offer)
        if not category_tags:
            return False
        return CATEGORYTAG_GAMETIME in category_tags

    def IsItemOffer(self, offer):
        productQuantities = offer.productQuantities
        for product in productQuantities.itervalues():
            if product.typeId > 0:
                return True

        return False

    def IsPlexOffer(self, offer):
        category_tags = self._get_category_tags_for_offer(offer)
        if not category_tags:
            return False
        return CATEGORYTAG_PLEX in category_tags

    def IsGemOffer(self, offer):
        category_tags = self._get_category_tags_for_offer(offer)
        if not category_tags:
            return False
        return CATEGORYTAG_GEM in category_tags

    @contextlib.contextmanager
    def _purchase_context(self):
        if self.purchase_in_progress:
            raise PurchaseInProgressError()
        self.purchase_in_progress = True
        try:
            yield
        finally:
            self.purchase_in_progress = False

    def SearchOffers(self, search_string):
        search_string = search_string.lower()
        if self.tags_by_id is None:
            self._process_categories()
        if self.offers_by_product_id is None:
            self._prime_search_index()
        matched_offer_ids = set()
        for offer in self.offers_by_id.itervalues():
            if search_string in offer.name.lower():
                matched_offer_ids.add(offer.id)

        for product in self.get_products().itervalues():
            if search_string in product.name.lower():
                matched_offer_ids.update(self.offers_by_product_id[product.id])

        for tag in self.tags_by_id.itervalues():
            if tag.name.lower().startswith(search_string):
                matched_offer_ids.update(self.offers_by_tag_id[tag.id])

        return [ self.offers_by_id[offerId] for offerId in matched_offer_ids ]

    def SearchOffersByTypeIDs(self, type_ids):
        offers = self.GetOffers()
        matched_offers = []
        for offer in offers.itervalues():
            products = offer.productQuantities.itervalues()
            product_type_ids = [ product.typeId for product in products ]
            if any((type_id in product_type_ids for type_id in type_ids)):
                matched_offers.append(offer)

        return matched_offers

    def SearchOffersByCategoryIDs(self, category_ids):
        offers = self.GetOffers()
        matched_offers = []
        for offer in offers.itervalues():
            if any((category_id in offer.categories for category_id in category_ids)):
                matched_offers.append(offer)

        return matched_offers

    def _process_categories(self):
        categories = self.vgs_client.get_categories(self.store_id)
        self.root_categories_by_id = {}
        self.tags_by_id = {}
        self.categories_by_id = {category.id:category for category in categories}
        for category in categories:
            if category.parentId:
                self.categories_by_id[category.parentId].subcategories.add(category.id)

        for category in categories:
            if category.parentId is None:
                if len(category.subcategories) > 0:
                    self.root_categories_by_id[category.id] = category
                else:
                    self.tags_by_id[category.id] = category

        offers = self.GetOffers()
        sub_cat_ids_seen_by_cat_id = defaultdict(set)
        for offer in offers.itervalues():
            for category in self.root_categories_by_id.itervalues():
                for sub_cat_id in category.subcategories:
                    if sub_cat_id in offer.categories:
                        category.tagIds.update((tag_id for tag_id in offer.categories if tag_id in self.tags_by_id))
                        sub_cat_ids_seen_by_cat_id[category.id].add(sub_cat_id)

        for category in self.root_categories_by_id.itervalues():
            category.subcategories.intersection_update(sub_cat_ids_seen_by_cat_id[category.id])

    def GetCategories(self):
        if not self.categories_by_id:
            self._process_categories()
        return self.categories_by_id

    def GetRootCategoryList(self):
        if not self.root_categories_by_id:
            self._process_categories()
        return self.root_categories_by_id.values()

    def GetTags(self):
        if not self.tags_by_id:
            self._process_categories()
        return self.tags_by_id

    def GetTagsByCategoryId(self, category_id):
        category = self.categories_by_id.get(category_id)
        if category.parentId is not None:
            category = self.categories_by_id.get(category.parentId)
        tags_by_id = self.GetTags()
        return [ tags_by_id[tagId] for tagId in category.tagIds ]

    def GetCategoryIdByCategoryTag(self, category_tag):
        for category in self.GetCategories().values():
            if category_tag in category.categoryTags:
                return category.id

    def GetFilteredOffers(self, category_id, currency, tags = set()):
        category_ids = {category_id}
        if category_id in self.categories_by_id:
            category = self.categories_by_id[category_id]
            category_ids.update({sub_category_id for sub_category_id in category.subcategories})
        offers = []
        for offer in self.GetOffers().itervalues():
            if category_ids.isdisjoint(offer.categories):
                continue
            if tags and not tags.issubset(offer.categories):
                continue
            if currency is not None:
                currencies_available = [ pricing.currency for pricing in offer.offerPricings ]
                if currency not in currencies_available:
                    continue
            offers.append(offer)

        return offers

    def _get_category_tags_for_offer(self, offer):
        category_tags = set()
        all_categories = self.GetCategories()
        for category_id in offer.categories:
            if category_id in all_categories:
                for tag in all_categories[category_id].categoryTags:
                    category_tags.add(tag)

        return category_tags

    def GetSubCategoryId(self, categories):
        for category_id in categories:
            if category_id not in self.root_categories_by_id and category_id not in self.tags_by_id:
                return category_id
