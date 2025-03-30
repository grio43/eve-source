#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\mgt\helpers\bookmark.py
import evetypes
import logging
import traceback
from evetypes import TYPE_LIST_BOOKMARKS_NOT_TREATED_AS_SOLAR_SYSTEMS
from inventorycommon import const as inventoryconst
logger = logging.getLogger(__name__)
CATEGORIES_TO_NOT_TREAT_AS_SOLAR_SYSTEM = {inventoryconst.categoryStructure, inventoryconst.categoryOrbital, inventoryconst.categorySovereigntyStructure}
GROUPS_TO_NOT_TREAT_AS_SOLAR_SYSTEM = {inventoryconst.groupMercenaryDen, inventoryconst.groupSkyhook}

class BookmarksNotTreatedAsSolarSystemsHelper(object):
    _categories_to_not_treat_as_solar_system = None
    _groups_to_not_treat_as_solar_system = None
    _types_to_not_treat_as_solar_system = None
    _type_list = None
    _instance = None
    _last_instance_id = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._last_instance_id += 1
            cls._instance = BookmarksNotTreatedAsSolarSystemsHelper()
        return cls._instance

    def __init__(self):
        if not self._type_list:
            try:
                self._type_list = evetypes.GetTypeList(TYPE_LIST_BOOKMARKS_NOT_TREATED_AS_SOLAR_SYSTEMS)
            except Exception as e:
                logger.exception('Failed to get type list for TYPE_LIST_BOOKMARKS_NOT_TREATED_AS_SOLAR_SYSTEMS (%s) - %s', TYPE_LIST_BOOKMARKS_NOT_TREATED_AS_SOLAR_SYSTEMS, traceback.format_exc())

        if not self._categories_to_not_treat_as_solar_system:
            if not self._type_list:
                self._categories_to_not_treat_as_solar_system = CATEGORIES_TO_NOT_TREAT_AS_SOLAR_SYSTEM
                self._groups_to_not_treat_as_solar_system = GROUPS_TO_NOT_TREAT_AS_SOLAR_SYSTEM
                self._types_to_not_treat_as_solar_system = evetypes.GetTypeIDsByCategories(CATEGORIES_TO_NOT_TREAT_AS_SOLAR_SYSTEM)
                self._types_to_not_treat_as_solar_system.update(evetypes.GetTypeIDsByGroups(GROUPS_TO_NOT_TREAT_AS_SOLAR_SYSTEM))
            else:
                self._categories_to_not_treat_as_solar_system = set(self._type_list.includedCategoryIDs) - set(self._type_list.excludedCategoryIDs)
                self._groups_to_not_treat_as_solar_system = set(self._type_list.includedGroupIDs) - set(self._type_list.excludedGroupIDs)
                self._types_to_not_treat_as_solar_system = evetypes.GetTypeIDsFromTypeList(self._type_list)

    @classmethod
    def should_treat_as_solar_system(cls, category_id = None, group_id = None, type_id = None):
        helper = cls.get_instance()
        if type_id and type_id in helper._types_to_not_treat_as_solar_system:
            return False
        if group_id and group_id in helper._groups_to_not_treat_as_solar_system:
            return False
        if category_id and category_id in helper._categories_to_not_treat_as_solar_system:
            return False
        return True


def should_treat_bookmark_as_solar_system(category_id = None, group_id = None, type_id = None):
    return BookmarksNotTreatedAsSolarSystemsHelper.should_treat_as_solar_system(category_id, group_id, type_id)
