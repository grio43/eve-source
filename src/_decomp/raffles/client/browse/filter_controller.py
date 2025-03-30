#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\browse\filter_controller.py
import copy
import signals
import inventorycommon.const as invConst
import eveformat
import evetypes
from eveui.autocomplete import ItemTypeSuggestion, ItemGroupSuggestion
from raffles import TICKET_COUNT_POOL
from raffles.client.localization import get_blueprint_type_name
from raffles.common.const import BlueprintType
from raffles.client.util import deserialize_filter_settings, serialize_filter_settings
TICKET_PRICE_INCREMENTS = (0, 1000000, 10000000, 100000000, None)
allowed_categories = (invConst.categoryBlueprint,
 invConst.categoryShipSkin,
 invConst.categoryShip,
 invConst.categoryFighter,
 invConst.categoryDrone,
 invConst.categoryApparel)
default_settings = {'item_suggestion': None,
 'meta_group_id': None,
 'solar_system_id': None,
 'min_ticket_price': TICKET_PRICE_INCREMENTS[0],
 'max_ticket_price': TICKET_PRICE_INCREMENTS[-1],
 'min_ticket_count': TICKET_COUNT_POOL[0],
 'max_ticket_count': TICKET_COUNT_POOL[-1],
 'blueprint_type': BlueprintType.all}

class FilterController(object):

    def __init__(self):
        self.on_change = signals.Signal(signalName='on_change')
        self._active_settings = copy.deepcopy(default_settings)
        self._load_filter()
        self._current_settings = copy.deepcopy(self._active_settings)

    @property
    def is_default(self):
        return self._current_settings == default_settings

    @property
    def current_settings(self):
        return self._current_settings

    def get(self):
        if self.has_changes:
            self._active_settings = copy.deepcopy(self._current_settings)
            self._save_filter()
        if self.has_active_settings:
            return self._stripped_settings()
        return (None, None)

    def _stripped_settings(self):
        filters = {}
        constraints = {}
        self._check_add_item(filters)
        self._check_add_key('solar_system_id', filters)
        self._check_add_key('meta_group_id', filters)
        if self.is_blueprint:
            self._check_add_key('blueprint_type', filters)
        self._check_add_key('min_ticket_price', constraints)
        self._check_add_key('max_ticket_price', constraints)
        self._check_add_key('min_ticket_count', constraints)
        self._check_add_key('max_ticket_count', constraints)
        return (filters, constraints)

    def _check_add_item(self, container):
        item_suggestion = self._active_settings['item_suggestion']
        if item_suggestion == default_settings['item_suggestion']:
            return
        for key in ('type_id', 'group_id', 'category_id'):
            value = getattr(item_suggestion, key, None)
            if value is not None:
                container[key] = value
                break

    def _check_add_key(self, key, container):
        if self._active_settings[key] != default_settings[key]:
            if self._active_settings[key] is not None:
                container[key] = int(self._active_settings[key])

    def reset_filter(self):
        if not self.can_reset:
            return
        self._current_settings = copy.deepcopy(default_settings)
        self.on_change()

    @property
    def has_active_settings(self):
        return self._active_settings != default_settings

    @property
    def can_reset(self):
        return self._current_settings != default_settings

    @property
    def has_changes(self):
        return self._current_settings != self._active_settings

    @property
    def item_suggestion(self):
        return self._current_settings['item_suggestion']

    @item_suggestion.setter
    def item_suggestion(self, value):
        self._edit_filter('item_suggestion', value)

    @property
    def type_id(self):
        item_suggestion = self._current_settings['item_suggestion']
        if not item_suggestion:
            return None
        return getattr(item_suggestion, 'type_id', None)

    @type_id.setter
    def type_id(self, value):
        if value:
            self.item_suggestion = ItemTypeSuggestion(value)
        else:
            self.item_suggestion = None

    @property
    def group_id(self):
        item_suggestion = self._current_settings['item_suggestion']
        if not item_suggestion:
            return None
        if hasattr(item_suggestion, 'type_id'):
            return None
        return getattr(item_suggestion, 'group_id', None)

    @group_id.setter
    def group_id(self, value):
        if value:
            self.item_suggestion = ItemGroupSuggestion(value)
        else:
            self.item_suggestion = None

    @property
    def category_id(self):
        item_suggestion = self._current_settings['item_suggestion']
        if not item_suggestion:
            return None
        if hasattr(item_suggestion, 'group_id'):
            return None
        return getattr(item_suggestion, 'category_id', None)

    @property
    def blueprint_type(self):
        return self._current_settings['blueprint_type']

    @blueprint_type.setter
    def blueprint_type(self, value):
        self._edit_filter('blueprint_type', value)

    @property
    def is_blueprint(self):
        category_id = None
        if self.type_id:
            category_id = evetypes.GetCategoryID(self.type_id)
        elif self.group_id:
            category_id = evetypes.GetCategoryIDByGroup(self.group_id)
        elif self.category_id:
            category_id = self.category_id
        return category_id == invConst.categoryBlueprint

    @property
    def blueprint_options(self):
        return [ (get_blueprint_type_name(t), t) for t in BlueprintType ]

    @property
    def meta_group_id(self):
        return self._current_settings['meta_group_id']

    @meta_group_id.setter
    def meta_group_id(self, value):
        self._edit_filter('meta_group_id', value)

    @property
    def solar_system_id(self):
        return self._current_settings['solar_system_id']

    @solar_system_id.setter
    def solar_system_id(self, value):
        self._edit_filter('solar_system_id', value)

    @property
    def ticket_price(self):
        return (self._current_settings['min_ticket_price'], self._current_settings['max_ticket_price'])

    @ticket_price.setter
    def ticket_price(self, value):
        self.edit_filter_many(('min_ticket_price', value[0]), ('max_ticket_price', value[1]))

    @property
    def min_ticket_price_label(self):
        value = self._current_settings['min_ticket_price']
        if value == TICKET_PRICE_INCREMENTS[0]:
            return ''
        else:
            return eveformat.isk_readable_short(value)

    @property
    def max_ticket_price_label(self):
        value = self._current_settings['max_ticket_price']
        if value == TICKET_PRICE_INCREMENTS[-1]:
            return ''
        else:
            return eveformat.isk_readable_short(value)

    @property
    def ticket_count(self):
        return (self._current_settings['min_ticket_count'], self._current_settings['max_ticket_count'])

    @ticket_count.setter
    def ticket_count(self, value):
        self.edit_filter_many(('min_ticket_count', value[0]), ('max_ticket_count', value[1]))

    @property
    def min_ticket_count_label(self):
        value = self._current_settings['min_ticket_count']
        if value == TICKET_COUNT_POOL[0]:
            return ''
        else:
            return eveformat.number_readable_short(value)

    @property
    def max_ticket_count_label(self):
        value = self._current_settings['max_ticket_count']
        if value == TICKET_COUNT_POOL[-1]:
            return ''
        else:
            return eveformat.number_readable_short(value)

    @property
    def ticket_price_increments(self):
        return TICKET_PRICE_INCREMENTS

    @property
    def ticket_count_increments(self):
        return TICKET_COUNT_POOL

    def filter_category(self, category_id):
        return category_id in allowed_categories

    def edit_filter_many(self, *changes):
        did_change = False
        for key, value in changes:
            if key not in self._current_settings:
                raise AttributeError('No attribute {}'.format(key))
            if self._current_settings[key] == value:
                continue
            self._current_settings[key] = value
            did_change = True

        if did_change:
            self.on_change()

    def _edit_filter(self, key, value):
        if self._current_settings[key] == value:
            return
        self._current_settings[key] = value
        self.on_change()

    def _load_filter(self):
        data = settings.char.ui.Get('raffles_browse_filter', None)
        if not data:
            return
        filter_settings = deserialize_filter_settings(data)
        for key in default_settings.iterkeys():
            if key in filter_settings:
                self._active_settings[key] = filter_settings[key]

    def _save_filter(self):
        data = serialize_filter_settings(self._active_settings)
        settings.char.ui.Set('raffles_browse_filter', data)
