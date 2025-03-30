#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\sections\baseSkinsSection.py
from cosmetics.client.shipSkinTradingSvc import get_ship_skin_trading_svc
from cosmetics.client.ships.skins.live_data.section_controller import BaseSection
from cosmetics.common.ships.skins.util import SkinListingOrder
from eve.client.script.ui.cosmetics.ship.pages.cards.baseSkinCard import BlankSkinCard
from eve.client.script.ui.cosmetics.ship.pages.store.storeSettings import skins_sort_by_setting

class BaseSkinsSection(BaseSection):

    def _get_pagination_controller(self):
        return get_ship_skin_trading_svc().get_pagination_controller()

    def get_card_controllers(self, page_num = None):
        order_by, ascending = skins_sort_by_setting.get()
        if page_num is None:
            self.reset_pagination_controller(order_by, ascending)
        return self.pagination_controller.get_page(page_num or 0)

    def reset_pagination_controller(self, order_by, ascending):
        self.pagination_controller.reset(self.get_type_filter(), order_by, ascending, self.num_per_page)

    def get_type_filter(self):
        return []

    @property
    def blank_card_class(self):
        return BlankSkinCard


def _get_skin_listing_sort_key(listing, sort_by):
    if sort_by == SkinListingOrder.EXPIRES_AT:
        return listing.valid_until
    if sort_by == SkinListingOrder.NAME:
        return listing.name.lower()
