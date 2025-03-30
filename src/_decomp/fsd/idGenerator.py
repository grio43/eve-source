#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\idGenerator.py
import contextlib
import urllib2
import json
SERVER_URL = 'https://fsdid.evetech.net'
BEHAVIOR_TREE_ID = 'BehaviorTreeID'
DUNGEON_ID = 'dungeonID'
DUNGEON_ROOM_ID = 'dungeonRoomID'
DUNGEON_ROOM_OBJECT_ID = 'dungeonRoomObjectID'
DUNGEON_ENTITY_ID = 'dungeonEntityID'
DUNGEON_TRIGGER_ID = 'dungeonTriggerID'
DUNGEON_TRIGGER_EVENT_ID = 'dungeonTriggerEventID'
DUNGEON_PATH_STEP_ID = 'dungeonPathStepID'
EVE_TYPE_ID = 'eveTypeID'
ENVIRONMENT_TEMPLATE_ID = 'EnvironmentTemplateID'
FITTING_ID = 'FittingID'
ICON_ID = 'IconID'
LOCALIZATION_PROJECT_ID = 'LocalizationProject'
LOOT_TABLE_CATEGORY_ID = 'LootTableCategoryID'
LOOT_TABLE_ID = 'LootTableID'
MATERIAL_SET_ID = 'MaterialSetID'
MESSAGE_GROUP_ID = 'MessageGroup'
MESSAGE_ID = 'Message'
NPC_FLEET_COUNTER_TABLE_ID = 'NpcFleetCounterTableID'
NPC_SPAWN_TABLE_ID = 'NpcSpawnTableID'
SCENE_ROW_ID = 'SceneRowID'
TALE_ID = 'TaleID'
TYPE_LIST_ID = 'TypeListID'
RACE_ID = 'raceID'
BLOODLINE_ID = 'bloodlineID'
ANCESTRY_ID = 'ancestryID'
PAPERDOLL_RESOURCE_ID = 'PaperdollResourceID'
PAPERDOLL_PORTRAIT_RESOURCE_ID = 'PaperdollPortraitResourceID'
PAPERDOLL_AVATAR_BEHAVIOR_ID = 'PaperdollAvatarBehaviorID'
LOCATION_LIST_ID = 'locationListID'
TagID = 'TagID'
ITEM_TRADER_RECIPE = 'itemTraderRecipeID'
_TEMP_COUNTER_VALUES = {}

class IDGeneratorError(Exception):
    pass


class TempCountersDict(dict):

    def __init__(self, *args, **kwargs):
        super(TempCountersDict, self).__init__(*args, **kwargs)
        self._all_counters_zero = False

    def __getitem__(self, key):
        self._set_counter_init_zero(key)
        val = super(TempCountersDict, self).__getitem__(key)
        self._increment_counter(key, val)
        return val

    def get(self, key):
        self._set_counter_init_zero(key)
        val = super(TempCountersDict, self).get(key)
        if val is not None:
            self._increment_counter(key, val)
        return val

    def zero_out_all_counters(self):
        self._all_counters_zero = True

    def _set_counter_init_zero(self, counter):
        if self._all_counters_zero and counter not in self:
            super(TempCountersDict, self).__setitem__(counter, 0)

    def _increment_counter(self, counter, val):
        super(TempCountersDict, self).__setitem__(counter, val + 1)


def _get_response(url, custom404 = None):
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError as e:
        if e.code == 404 and custom404 is not None:
            raise IDGeneratorError(custom404)
        raise IDGeneratorError('Could not connect to {}'.format(url))

    return response


def get_all_counters():
    response = _get_response(SERVER_URL)
    return json.load(response)


def create_new_counter(counter):
    url = '{}/CreateCounter/{}'.format(SERVER_URL, counter)
    response = _get_response(url, 'Counter {} already exists'.format(counter))
    return json.load(response)


def get_counter(counter):
    global _TEMP_COUNTER_VALUES
    temp_value = _TEMP_COUNTER_VALUES.get(counter)
    if temp_value is not None:
        return temp_value
    url = '{}/GetCounter/{}'.format(SERVER_URL, counter)
    response = _get_response(url, 'Counter {} does not exist'.format(counter))
    return json.load(response)['value']


def increment_counter(counter, increment):
    if increment < 1:
        raise IDGeneratorError('Increment must be greater than 0, got {}'.format(increment))
    url = '{}/GetCounterRange/{}/{}'.format(SERVER_URL, counter, increment)
    response = _get_response(url, 'Counter {} does not exist'.format(counter))
    result = json.load(response)
    return (result['begin'], result['end'])


@contextlib.contextmanager
def _set_counters(counter_values = None, zero_out_all = False):
    global _TEMP_COUNTER_VALUES
    if zero_out_all:
        _TEMP_COUNTER_VALUES = TempCountersDict({})
        _TEMP_COUNTER_VALUES.zero_out_all_counters()
        yield
    else:
        _TEMP_COUNTER_VALUES = TempCountersDict(counter_values)
        yield
    _TEMP_COUNTER_VALUES = {}


def zero_out_all_counters():
    return _set_counters(zero_out_all=True)
