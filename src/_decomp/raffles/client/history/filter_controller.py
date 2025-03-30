#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\history\filter_controller.py
import copy
import signals
import inventorycommon.const as invConst
import eveformat
import evetypes
from raffles import TICKET_COUNT_POOL
from raffles.client.constants import BlueprintType
from raffles.client.localization import Text, get_blueprint_type_name
from raffles.client.util import deserialize_filter_settings, serialize_filter_settings
TICKET_PRICE_INCREMENTS = (0, 1000000, 10000000, 100000000, None)
allowed_categories = (invConst.categoryBlueprint,
 invConst.categoryShipSkin,
 invConst.categoryShip,
 invConst.categoryFighter,
 invConst.categoryDrone,
 invConst.categoryApparel)

def get_sort_options():
    return [(Text.sort_default(), None),
     (Text.sort_item_name(), 'item_name'),
     (Text.ticket_count_label(), 'ticket_count'),
     (Text.ticket_price(), 'ticket_price'),
     (Text.total_price(), 'total_price'),
     (Text.sort_end_time(), 'end_time')]


default_sort_direction = {None: False,
 'item_name': False,
 'ticket_count': True,
 'ticket_price': True,
 'total_price': True,
 'end_time': True}
default_settings = {'item_suggestion': None,
 'meta_group_id': None,
 'solar_system_id': None,
 'min_ticket_price': TICKET_PRICE_INCREMENTS[0],
 'max_ticket_price': TICKET_PRICE_INCREMENTS[-1],
 'min_ticket_count': TICKET_COUNT_POOL[0],
 'max_ticket_count': TICKET_COUNT_POOL[-1],
 'show_joined': True,
 'show_created': True,
 'show_active': True,
 'show_finished': True,
 'show_public': True,
 'show_private': True,
 'blueprint_type': BlueprintType.all}

class FilterController(object):

    def __init__(self):
        self.on_change = signals.Signal(signalName='on_change')
        self.on_sorting_changed = signals.Signal(signalName='on_sorting_changed')
        self._current_settings = copy.deepcopy(default_settings)
        self._sorting = (None, default_sort_direction[None])
        self._load_sorting()
        self._load_filter()

    @property
    def is_default(self):
        return self._current_settings == default_settings and self.is_default_sort

    @property
    def is_default_sort(self):
        return self._sorting is None or self.sort_id is None

    @property
    def current_settings(self):
        settings = {k:v for k, v in self._current_settings.iteritems()}
        settings['sorting'] = self._sorting
        return settings

    @property
    def sorting(self):
        return self._sorting

    @property
    def sort_id(self):
        return self._sorting[0]

    @sort_id.setter
    def sort_id(self, sort_id):
        self.sorting = (sort_id, default_sort_direction.get(sort_id))

    @property
    def sort_direction(self):
        return self._sorting[1]

    @sort_direction.setter
    def sort_direction(self, sort_direction):
        self.sorting = (self.sort_id, sort_direction)

    @sorting.setter
    def sorting(self, sorting):
        if self._sorting == sorting:
            return
        self._sorting = sorting
        self._save_sorting()
        self.on_sorting_changed()

    @property
    def scroll_position(self):
        return settings.char.ui.Get('raffles_history_scroll', 0)

    @scroll_position.setter
    def scroll_position(self, scroll_position):
        settings.char.ui.Set('raffles_history_scroll', scroll_position)

    @property
    def can_reset(self):
        return self._current_settings != default_settings or self.sort_id

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

    @property
    def group_id(self):
        item_suggestion = self._current_settings['item_suggestion']
        if not item_suggestion:
            return None
        if hasattr(item_suggestion, 'type_id'):
            return None
        return getattr(item_suggestion, 'group_id', None)

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

    def edit_setting(self, id, value):
        self._edit_filter(id, value)

    def get_setting(self, id):
        return self._current_settings[id]

    def reset_all(self):
        self.reset_settings(default_settings.keys())
        self.reset_sorting()

    def reset_settings(self, names):
        changes = [ (name, default_settings[name]) for name in names ]
        self.edit_filter_many(*changes)

    def reset_sorting(self):
        self.sorting = (None, default_sort_direction[None])

    def has_setting_changes(self, id):
        return self._current_settings[id] != default_settings[id]

    def filter_category(self, category_id):
        return category_id in allowed_categories

    def edit_filter_many(self, *changes):
        did_change = False
        did_sorting_change = False
        for key, value in changes:
            if key == 'sorting':
                self._sorting = value
                did_sorting_change = True
                continue
            if key not in self._current_settings:
                raise AttributeError('No attribute {}'.format(key))
            if self._current_settings[key] != value:
                self._current_settings[key] = value
                did_change = True

        if did_change:
            self._save_filter()
            self.on_change()
        if did_sorting_change:
            self._save_sorting()
            self.on_sorting_changed()

    def _edit_filter(self, key, value):
        if self._current_settings[key] == value:
            return
        self._current_settings[key] = value
        self._save_filter()
        self.on_change()

    def _load_filter(self):
        data = settings.char.ui.Get('raffles_history_filter', None)
        if not data:
            return
        filter_settings = deserialize_filter_settings(data)
        for key in default_settings.iterkeys():
            if key in filter_settings:
                self._current_settings[key] = filter_settings[key]

    def _save_filter(self):
        data = serialize_filter_settings(self._current_settings)
        settings.char.ui.Set('raffles_history_filter', data)

    def _load_sorting(self):
        self._sorting = settings.char.ui.Get('raffles_history_sort', (None, False))

    def _save_sorting(self):
        settings.char.ui.Set('raffles_history_sort', self._sorting)
