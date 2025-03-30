#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\ship\field.py
from eveui.autocomplete import AutocompleteField
from eveui.autocomplete.ship.provider import ShipTypeProvider, ShipClassProvider

class ShipField(AutocompleteField):

    def __init__(self, include_type = True, type_filter = None, include_class = True, **kwargs):
        providers = []
        if include_type:
            providers.append(ShipTypeProvider(type_filter=type_filter))
        if include_class:
            providers.append(ShipClassProvider())
        kwargs['provider'] = providers
        kwargs.setdefault('suggestion_list_min_width', 360)
        super(ShipField, self).__init__(**kwargs)
