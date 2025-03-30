#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\item\provider.py
import evetypes
import threadutils
from eveui.autocomplete.provider import NameCache, NameCacheProvider
from eveui.autocomplete.item.suggestion import ItemTypeSuggestion, ItemGroupSuggestion, ItemCategorySuggestion

class ItemTypeProvider(NameCacheProvider):

    def __init__(self, type_filter = None, score_function = None, include_unpublished = False):
        self._type_filter = type_filter
        self._include_unpublished = include_unpublished
        super(ItemTypeProvider, self).__init__(cache=TypeNameCache.instance(), suggestion_type=ItemTypeSuggestion, filter=self._filter, score=score_function)

    def _filter(self, type_id):
        if self._type_filter is not None and not self._type_filter(type_id):
            return False
        if not self._include_unpublished and not (evetypes.IsPublished(type_id) and evetypes.IsGroupPublished(type_id) and evetypes.IsCategoryPublished(type_id)):
            return False
        return True


class ItemGroupProvider(NameCacheProvider):

    def __init__(self, group_filter = None):
        super(ItemGroupProvider, self).__init__(cache=GroupNameCache.instance(), suggestion_type=ItemGroupSuggestion, filter=group_filter)


class ItemCategoryProvider(NameCacheProvider):

    def __init__(self, category_filter = None):
        super(ItemCategoryProvider, self).__init__(cache=CategoryNameCache.instance(), suggestion_type=ItemCategorySuggestion, filter=category_filter)


class TypeNameCache(NameCache):

    def prime(self):
        cache = {}
        for type_id in evetypes.Iterate():
            cache[type_id] = evetypes.GetName(type_id, important=False)
            threadutils.BeNice(5)

        return cache


class GroupNameCache(NameCache):

    def prime(self):
        cache = {}
        for group_id in evetypes.IterateGroups():
            is_group_published = evetypes.IsGroupPublishedByGroup(group_id)
            is_category_published = evetypes.IsCategoryPublishedByGroup(group_id)
            if is_group_published and is_category_published:
                cache[group_id] = evetypes.GetGroupNameByGroup(group_id, important=False)
            threadutils.be_nice(5)

        return cache


class CategoryNameCache(NameCache):

    def prime(self):
        cache = {}
        for category_id in evetypes.IterateCategories():
            if evetypes.IsCategoryPublishedByCategory(category_id):
                cache[category_id] = evetypes.GetCategoryNameByCategory(category_id, important=False)
            threadutils.be_nice(5)

        return cache
