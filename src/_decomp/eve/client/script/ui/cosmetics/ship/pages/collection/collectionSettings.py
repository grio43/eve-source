#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\collection\collectionSettings.py
from carbonui.services.setting import CharSettingEnum, SessionSettingEnum
from cosmetics.common.ships.skins.util import SkinListingOrder, ComponentListingOrder
skins_sort_by_options = [(SkinListingOrder.NAME, False), (SkinListingOrder.NAME, True)]
skins_sort_by_setting = CharSettingEnum('CollectionSkinBrowserSortBy', skins_sort_by_options[0], skins_sort_by_options)
skins_hull_type_filter_setting = SessionSettingEnum(None)
components_sort_by_options = [(ComponentListingOrder.NAME, False),
 (ComponentListingOrder.NAME, True),
 (ComponentListingOrder.COLOR_SHADE, False),
 (ComponentListingOrder.COLOR_SHADE, True)]
components_sort_by_setting = CharSettingEnum('CollectionComponentBrowserSortBy', components_sort_by_options[0], components_sort_by_options)
