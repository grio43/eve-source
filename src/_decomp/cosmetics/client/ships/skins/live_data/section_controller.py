#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\live_data\section_controller.py
from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
from cosmetics.client.shipSkinComponentTradingSvc import get_ship_skin_component_trading_svc
from cosmetics.client.shipSkinDesignSvc import get_ship_skin_design_svc
from cosmetics.client.shipSkinLicensesSvc import get_ship_skin_license_svc
from cosmetics.client.shipSkinSequencingSvc import get_ship_skin_sequencing_svc
from cosmetics.client.ships.skins.live_data.paginationController import PaginationController
from cosmetics.client.ships.skins.static_data.collection_section import CollectionSection
from cosmetics.common.ships.skins.static_data.component_category import ComponentCategory
from cosmetics.common.ships.skins.util import ComponentListingOrder, SkinListingOrder
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.pages.cards.baseSkinCard import BlankSkinCard
from eve.client.script.ui.cosmetics.ship.pages.cards.componentLicenseCard import BlankMaterialComponentCard, BlankPatternComponentCard
from eve.client.script.ui.cosmetics.ship.pages.collection import collectionSettings
from eve.client.script.ui.cosmetics.ship.pages.homepage.savedDesignsSettings import designs_sort_by_setting
from eve.client.script.ui.cosmetics.ship.pages.store import storeSettings
from eve.client.script.ui.cosmetics.ship.pages.store.storeSettings import components_sort_by_setting
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException

class BaseSection(object):
    name = None
    category = None
    page_id = None
    pagination_controller = None

    def __init__(self, num_per_page = None, apply_sorting = True, apply_filtering = True):
        self.num_per_page = num_per_page
        self.pagination_controller = self._get_pagination_controller()
        self.apply_sorting = apply_sorting
        self.apply_filtering = apply_filtering

    def _get_pagination_controller(self):
        return PaginationController()

    def get_card_controllers(self, page_num = None):
        if page_num is None or not self.pagination_controller.initialized:
            controllers = self._get_card_controllers_filtered_and_sorted()
            self.reset_pagination_controller(controllers)
        return self.pagination_controller.get_page(page_num or 0)

    def reset_pagination_controller(self, controllers):
        self.pagination_controller.reset(controllers, self.num_per_page)

    def _get_all_card_controllers(self):
        return []

    def _get_card_controllers_filtered_and_sorted(self):
        controllers = self._get_all_card_controllers()
        if self.apply_filtering:
            controllers = self._filter_controllers(controllers)
        if self.apply_sorting:
            controllers = self._sort_controllers(controllers)
        return controllers

    def _sort_controllers(self, controllers):
        return controllers

    def _filter_controllers(self, controllers):
        return controllers

    def get_num_entries(self):
        return len(self._get_all_card_controllers())

    def get_page_id_and_args(self):
        return (self.page_id, self.category)

    def get_name(self):
        return GetByLabel(self.name)

    def is_paginated(self):
        return self.pagination_controller.has_more_than_one_page()

    @property
    def blank_card_class(self):
        return None


def _get_listing_sort_key(component_listing, sort_by):
    if sort_by == ComponentListingOrder.EXPIRES_AT:
        return component_listing.valid_until
    if sort_by == ComponentListingOrder.NAME:
        return component_listing.name.lower()
    if sort_by == ComponentListingOrder.PRICE:
        return component_listing.price
    if sort_by == ComponentListingOrder.COLOR_SHADE:
        return component_listing.get_component_data().color_shade_sort_index


class BaseStoreComponentsSectionController(BaseSection):
    page_id = SkinrPage.STORE_COMPONENTS

    def _sort_controllers(self, controllers):
        expiring_soon_controllers = []
        other_controllers = []
        for controller in controllers:
            if controller.is_limited_offer():
                expiring_soon_controllers.append(controller)
            else:
                other_controllers.append(controller)

        sort_by, ascending = components_sort_by_setting.get()
        sorted_controllers = sorted(expiring_soon_controllers, key=lambda l: _get_listing_sort_key(l, sort_by), reverse=ascending)
        sorted_controllers.extend(sorted(other_controllers, key=lambda l: _get_listing_sort_key(l, sort_by), reverse=ascending))
        return sorted_controllers

    def _get_all_card_controllers(self):
        try:
            return get_ship_skin_component_trading_svc().get_category_listings(self.category)
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            return []


class StoreNanocoatingComponentsSection(BaseStoreComponentsSectionController):
    category = ComponentCategory.MATERIAL
    name = 'UI/Personalization/ShipSkins/SKINR/Studio/Nanocoatings'

    @property
    def blank_card_class(self):
        return BlankMaterialComponentCard

    def get_num_entries(self):
        all_controllers = self._get_all_card_controllers()
        return len(self._filter_controllers(all_controllers))

    def _filter_controllers(self, controllers):
        finish = storeSettings.nanocoating_finish_filter_setting.get()
        if not finish:
            return controllers
        return [ c for c in controllers if c.get_component_data().finish == finish ]


class StoreMetallicComponentsSection(BaseStoreComponentsSectionController):
    category = ComponentCategory.METALLIC
    name = 'UI/Personalization/ShipSkins/SKINR/Studio/Metallics'

    @property
    def blank_card_class(self):
        return BlankMaterialComponentCard


class StorePatternComponentsSection(BaseStoreComponentsSectionController):
    category = ComponentCategory.PATTERN
    name = 'UI/Personalization/ShipSkins/SKINR/Studio/Patterns'

    @property
    def blank_card_class(self):
        return BlankPatternComponentCard


def _get_skin_license_sort_key(component_listing, sort_by):
    if sort_by == ComponentListingOrder.NAME:
        return component_listing.name.lower()


class CollectionBaseSkinsSection(BaseSection):
    page_id = SkinrPage.COLLECTION_SKINS

    def _filter_controllers(self, controllers):
        type_id = collectionSettings.skins_hull_type_filter_setting.get()
        if not type_id:
            return controllers
        return [ l for l in controllers if l.skin_design.ship_type_id in [type_id] ]

    def _sort_controllers(self, controllers):
        sort_by, reverse = collectionSettings.skins_sort_by_setting.get()
        return sorted(controllers, key=lambda l: _get_skin_license_sort_key(l, sort_by), reverse=reverse)

    @property
    def blank_card_class(self):
        return BlankSkinCard


class CollectionAllActivatedSkinsSection(CollectionBaseSkinsSection):
    category = CollectionSection.SKINS_3RD_PARTY_ACTIVATED
    name = 'UI/Personalization/ShipSkins/SKINR/Collection/ActivatedSkins'

    def _get_all_card_controllers(self):
        try:
            return get_ship_skin_license_svc().get_my_activated_licenses()
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            return []


class CollectionAllUnactivatedSkinsSection(CollectionBaseSkinsSection):
    category = CollectionSection.SKINS_3RD_PARTY_UNACTIVATED
    name = 'UI/Personalization/ShipSkins/SKINR/Collection/UnactivatedSkins'

    def _get_all_card_controllers(self):
        try:
            return get_ship_skin_license_svc().get_my_unactivated_licenses()
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            return []


def _get_component_license_sort_key(component_listing, sort_by):
    if sort_by == ComponentListingOrder.NAME:
        return component_listing.name.lower()
    if sort_by == ComponentListingOrder.COLOR_SHADE:
        return component_listing.get_component_data().color_shade_sort_index


class BaseCollectionComponentsSection(BaseSection):
    page_id = SkinrPage.COLLECTION_COMPONENTS

    def _get_all_card_controllers(self):
        try:
            return get_ship_skin_component_svc().get_all_owned_licenses_in_category(category=self.category)
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            return []

    def _sort_controllers(self, controllers):
        sort_by, reverse = collectionSettings.components_sort_by_setting.get()
        return sorted(controllers, key=lambda l: _get_component_license_sort_key(l, sort_by), reverse=reverse)


class CollectionNanocoatingComponentsSection(BaseCollectionComponentsSection):
    category = ComponentCategory.MATERIAL
    name = 'UI/Personalization/ShipSkins/SKINR/Studio/Nanocoatings'

    @property
    def blank_card_class(self):
        return BlankMaterialComponentCard


class CollectionMetallicComponentsSection(BaseCollectionComponentsSection):
    category = ComponentCategory.METALLIC
    name = 'UI/Personalization/ShipSkins/SKINR/Studio/Metallics'

    @property
    def blank_card_class(self):
        return BlankMaterialComponentCard


class CollectionPatternComponentsSection(BaseCollectionComponentsSection):
    category = ComponentCategory.PATTERN
    name = 'UI/Personalization/ShipSkins/SKINR/Studio/Patterns'

    @property
    def blank_card_class(self):
        return BlankPatternComponentCard


class SequencingInProgressSection(BaseSection):
    page_id = SkinrPage.STUDIO
    name = 'UI/Personalization/ShipSkins/SKINR/Studio/SequencingInProgress'

    @property
    def blank_card_class(self):
        return BlankPatternComponentCard

    def _get_all_card_controllers(self):
        try:
            svc = get_ship_skin_sequencing_svc()
            return svc.get_all_my_active_sequencing_jobs().values()
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            return []


class SavedDesignsSection(BaseSection):
    page_id = SkinrPage.STUDIO
    category = SkinrPage.STUDIO_SAVED_DESIGNS
    name = 'UI/Personalization/ShipSkins/SKINR/Studio/SavedDesigns'

    @property
    def blank_card_class(self):
        return BlankSkinCard

    def _get_all_card_controllers(self):
        try:
            return get_ship_skin_design_svc().get_all_owned_designs().items()
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            return []

    def _sort_controllers(self, controllers):
        sort_by, ascending = designs_sort_by_setting.get()
        return sorted(controllers, key=lambda l: _get_saved_design_sort_key(l, sort_by), reverse=ascending)


def _get_saved_design_sort_key(design_data, sort_by):
    skin_design_id, skin_design = design_data
    if sort_by == SkinListingOrder.NAME:
        return skin_design.name.lower()
    return skin_design
