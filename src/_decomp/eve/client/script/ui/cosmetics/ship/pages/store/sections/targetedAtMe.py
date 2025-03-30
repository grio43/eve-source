#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\sections\targetedAtMe.py
from carbonui import Align
from carbonui.primitives.container import Container
from cosmetics.client.ships.skins.live_data.skin_listing_target import ListingTargetType, SellerMembershipType
from cosmetics.client.ships.skins.static_data.store_section import StoreSection
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.pages.store import storeSettings
from eve.client.script.ui.cosmetics.ship.pages.store.sections.baseSkinsSection import BaseSkinsSection
from eve.client.script.ui.cosmetics.ship.pages.store.sections.baseSkinsSectionContainer import BaseSkinsSectionContainer, SortByMenuButtonIcon, MAX_NUM_PER_PAGE

class StoreSkinListingsTargetedAtMeSection(BaseSkinsSection):
    page_id = SkinrPage.STORE_SKINS
    category = StoreSection.SKINS_TARGETED_AT_ME
    name = 'UI/Personalization/ShipSkins/SKINR/Store/TargetedAtMe'

    def reset_pagination_controller(self, order_by, ascending):
        self.pagination_controller.reset(self.get_type_filter(), order_by, ascending, self.num_per_page, ListingTargetType.CHARACTER, SellerMembershipType.UNSPECIFIED)

    def get_type_filter(self):
        if self.apply_filtering:
            ship_type = storeSettings.skins_hull_type_filter_setting.get()
            if ship_type:
                return [ship_type]
            return []
        else:
            return []


class StoreSkinListingsTargetedAtMeSectionContainer(BaseSkinsSectionContainer):

    def _set_section_controller(self, section_controller = None):
        self.section_controller = StoreSkinListingsTargetedAtMeSection(num_per_page=None, apply_filtering=False)


class StoreViewAllSkinListingsTargetedAtMeSectionContainer(StoreSkinListingsTargetedAtMeSectionContainer):

    def _set_section_controller(self, section_controller = None):
        self.section_controller = StoreSkinListingsTargetedAtMeSection(MAX_NUM_PER_PAGE)

    def construct_filter_and_sorting(self):
        SortByMenuButtonIcon(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT)

    def construct_pagination_container(self):
        self.pagination_container = Container(name='pagination_container', parent=self, align=Align.TOTOP, height=32)
