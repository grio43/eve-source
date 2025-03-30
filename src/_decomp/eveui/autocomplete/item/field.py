#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\item\field.py
from eveui.autocomplete.field import AutocompleteField
from eveui.autocomplete.item.provider import ItemTypeProvider, ItemGroupProvider, ItemCategoryProvider

class ItemField(AutocompleteField):

    def __init__(self, include_type = True, type_filter = None, include_group = True, group_filter = None, include_category = True, category_filter = None, **kwargs):
        providers = []
        if include_type:
            providers.append(ItemTypeProvider(type_filter=type_filter))
        if include_group:
            providers.append(ItemGroupProvider(group_filter=group_filter))
        if include_category:
            providers.append(ItemCategoryProvider(category_filter=category_filter))
        kwargs['provider'] = providers
        kwargs.setdefault('suggestion_list_min_width', 360)
        super(ItemField, self).__init__(**kwargs)


class ItemTypeField(ItemField):

    def __init__(self, type_filter = None, **kwargs):
        super(ItemTypeField, self).__init__(type_filter=type_filter, include_category=False, include_group=False, **kwargs)
