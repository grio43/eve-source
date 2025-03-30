#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\util.py
from eve.common.script.sys.eveCfg import IsBlueprint
import eveformat.client
import evetypes
import inventorycommon.const as invconst
import inventorycommon.typeHelpers
import logging
from eveui.autocomplete import ItemTypeSuggestion, ItemGroupSuggestion, ItemCategorySuggestion
from .localization import Text
logger = logging.getLogger(__name__)

def get_group_id(type_id):
    return evetypes.GetGroupID(type_id)


def get_category_id(type_id):
    return evetypes.GetCategoryID(type_id)


def get_meta_group_id(type_id):
    return evetypes.GetMetaGroupIDOrNone(type_id)


def get_item_name(type_id, item_id = None):
    group_id = evetypes.GetGroupID(type_id)
    name = None
    if item_id and group_id == invconst.groupBiomass:
        name = cfg.evelocations.Get(item_id).name
    if not name:
        name = evetypes.GetName(type_id)
    return name


def get_item_group_name(type_id):
    return evetypes.GetGroupName(type_id)


def get_market_estimate_text(type_id, item_id):
    estimate = get_market_estimate(type_id, item_id)
    if estimate is None:
        return Text.market_estimate(value=Text.unknown_value())
    return Text.market_estimate(value=eveformat.isk_readable(estimate))


def get_market_estimate(type_id, item_id):
    if _is_blueprint_copy(type_id, item_id):
        return None
    return inventorycommon.typeHelpers.GetAveragePrice(type_id)


def _is_blueprint_copy(type_id, item_id):
    if not IsBlueprint(type_id):
        return
    try:
        bp_data = sm.GetService('blueprintSvc').GetBlueprintItemMemoized(item_id)
        if not bp_data.original:
            return True
    except Exception as error:
        pass


def character_name(character_id, linkify = False):
    try:
        character_info = cfg.eveowners.Get(character_id)
    except KeyError:
        logger.warning('Failed to find character {}'.format(character_id), exc_info=True)
        return u'[no character: {}]'.format(character_id)

    if not linkify or not character_info.typeID:
        return character_info.name
    return u'<a href=showinfo:{type_id}//{character_id}>{name}</a>'.format(type_id=character_info.typeID, character_id=character_id, name=character_info.name)


def station_name(station_id, linkify = False):
    try:
        station = cfg.stations.Get(station_id)
    except KeyError:
        logger.warning('Failed to find station {}'.format(station_id), exc_info=True)
        return u'[no station: {}]'.format(station_id)

    station_type_id = station.stationTypeID
    station_name = sm.GetService('ui').GetStationName(station_id)
    if not linkify:
        return station_name
    return u'<a href=showinfo:{type_id}//{station_id}>{name}</a>'.format(type_id=station_type_id, station_id=station_id, name=station_name)


def serialize_filter_settings(filter_settings):
    serialized = {}
    for key, value in filter_settings.iteritems():
        if key == 'item_suggestion':
            if value is not None:
                if isinstance(value, ItemTypeSuggestion):
                    value = (value.type_id, 'type_id')
                elif isinstance(value, ItemGroupSuggestion):
                    value = (value.group_id, 'group_id')
                elif isinstance(value, ItemCategorySuggestion):
                    value = (value.category_id, 'category_id')
                else:
                    raise TypeError('Unknown item suggestion type', value)
        serialized[key] = value

    return serialized


def deserialize_filter_settings(serialized):
    filter_settings = {}
    for key, value in serialized.iteritems():
        if key == 'item_suggestion':
            if value is not None:
                value_id, value_type = value
                if value_type == 'type_id':
                    value = ItemTypeSuggestion(value_id)
                elif value_type == 'group_id':
                    value = ItemGroupSuggestion(value_id)
                elif value_type == 'category_id':
                    value = ItemCategorySuggestion(value_id)
                else:
                    raise TypeError('Unknown item suggestion type', value_type)
        filter_settings[key] = value

    return filter_settings
