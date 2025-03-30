#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\homepage\savedDesignsSettings.py
from carbonui.services.setting import CharSettingEnum
from cosmetics.common.ships.skins.util import SkinListingOrder
designs_sort_by_options = [(SkinListingOrder.NAME, False), (SkinListingOrder.NAME, True)]
designs_sort_by_setting = CharSettingEnum('SavedDesignsBrowserSortBy', designs_sort_by_options[0], designs_sort_by_options)
