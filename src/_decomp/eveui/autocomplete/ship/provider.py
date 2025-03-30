#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\ship\provider.py
import appConst
import evetypes
import threadutils
from eveui.autocomplete import NameCacheProvider, NameCache
from eveui.autocomplete.item.provider import TypeNameCache
from eveui.autocomplete.ship.suggestion import ShipTypeSuggestion, ShipClassSuggestion
from shipgroup import ALL_GROUPS, get_ship_tree_group_name

class ShipTypeProvider(NameCacheProvider):

    def __init__(self, type_filter = None, score_function = None, include_unpublished = False):
        self._type_filter = type_filter
        self._include_unpublished = include_unpublished
        super(ShipTypeProvider, self).__init__(cache=TypeNameCache.instance(), suggestion_type=ShipTypeSuggestion, filter=self._filter, score=score_function)

    def _filter(self, type_id):
        if self._type_filter is not None and not self._type_filter(type_id):
            return False
        if not evetypes.GetCategoryID(type_id) == appConst.categoryShip:
            return False
        if not self._include_unpublished and not (evetypes.IsPublished(type_id) and evetypes.IsGroupPublished(type_id) and evetypes.IsCategoryPublished(type_id)):
            return False
        return True


class ShipClassProvider(NameCacheProvider):

    def __init__(self, type_filter = None, score_function = None, include_unpublished = False):
        self._type_filter = type_filter
        self._include_unpublished = include_unpublished
        super(ShipClassProvider, self).__init__(cache=ShipClassNameCache.instance(), suggestion_type=ShipClassSuggestion, score=score_function)


class ShipClassNameCache(NameCache):

    def prime(self):
        cache = {}
        for group_id in ALL_GROUPS:
            cache[group_id] = get_ship_tree_group_name(group_id)
            threadutils.be_nice(5)

        return cache
