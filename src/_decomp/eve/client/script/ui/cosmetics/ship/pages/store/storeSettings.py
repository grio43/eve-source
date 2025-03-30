#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\storeSettings.py
from carbonui.services.setting import CharSettingEnum, SessionSettingEnum, SessionSettingNumeric
from cosmetics.client.ships.skins.live_data.skin_listing_target import SellerMembershipType, ListingTargetType, ListedTo
from cosmetics.common.ships.skins.util import SkinListingOrder, ComponentListingOrder
from eve.common.lib import appConst
skins_sort_by_options = [(SkinListingOrder.EXPIRES_AT, False),
 (SkinListingOrder.EXPIRES_AT, True),
 (SkinListingOrder.NAME, False),
 (SkinListingOrder.NAME, True)]
skins_sort_by_setting = CharSettingEnum('StoreSkinBrowserSortBy', skins_sort_by_options[0], skins_sort_by_options)
skins_hull_type_filter_setting = SessionSettingEnum(None)
components_sort_by_options = [(ComponentListingOrder.NAME, False),
 (ComponentListingOrder.NAME, True),
 (ComponentListingOrder.PRICE, False),
 (ComponentListingOrder.PRICE, True),
 (ComponentListingOrder.COLOR_SHADE, False),
 (ComponentListingOrder.COLOR_SHADE, True)]
components_sort_by_setting = CharSettingEnum('StoreComponentBrowserSortBy', components_sort_by_options[0], components_sort_by_options)
nanocoating_finish_filter_setting = SessionSettingEnum(None)
listed_by_setting = SessionSettingEnum(SellerMembershipType.UNSPECIFIED)
listed_to_setting = SessionSettingEnum(ListedTo.PUBLIC)
emphasized_ship_type_id = SessionSettingNumeric(0, 0, appConst.maxInt)
