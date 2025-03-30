#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\npcs\npccorporations.py
from collections import defaultdict
from collections import namedtuple
import evetypes
from caching import Memoize
from eveprefs import boot
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import npcCorporationsLoader
    import corporationActivitiesLoader
except ImportError:
    npcCorporationsLoader = None
    corporationActivitiesLoader = None

CorporationTickerProps = ['corporationID',
 'tickerName',
 'shape1',
 'shape2',
 'shape3',
 'color1',
 'color2',
 'color3']
CorporationTicker = namedtuple('CorporationTicker', CorporationTickerProps)
OWNER_AURA_IDENTIFIER = -1
OWNER_SYSTEM_IDENTIFIER = -2
OWNER_NAME_OVERRIDES = {OWNER_AURA_IDENTIFIER: 'UI/Agents/AuraAgentName',
 OWNER_SYSTEM_IDENTIFIER: 'UI/Chat/ChatEngine/EveSystem'}

class NpcCorporationsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/npcCorporations.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/npcCorporations.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/npcCorporations.fsdbinary'
    __loader__ = npcCorporationsLoader


class CorporationActivitiesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/corporationActivities.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/corporationActivities.fsdbinary'
    __loader__ = corporationActivitiesLoader


def get_npc_corporations():
    return NpcCorporationsLoader.GetData()


def get_npc_corporation_ids():
    return get_npc_corporations().keys()


@Memoize
def get_npc_corporation_id_name_mapping():
    return {corp_id:get_npc_corporation_name(corp_id, corp) for corp_id, corp in iter_npc_corporations()}


def iter_npc_corporations():
    for corporation_id, corporation in get_npc_corporations().iteritems():
        yield (corporation_id, corporation)


def iter_npc_corporation_ids():
    for corporation_id in get_npc_corporations().iterkeys():
        yield corporation_id


def _get_npc_corporation(corporation_id):
    return get_npc_corporations()[corporation_id]


def get_npc_corporation(corporation_id, default = None):
    try:
        return _get_npc_corporation(corporation_id)
    except KeyError:
        return default


def get_corporation_station_id(corporation_id, default = None):
    try:
        return _get_npc_corporation(corporation_id).stationID
    except KeyError:
        return default


def get_corporation_main_activity_id(corporation_id, default = None):
    try:
        return _get_npc_corporation(corporation_id).mainActivityID
    except KeyError:
        return default


def get_corporation_secondary_activity_id(corporation_id, default = None):
    try:
        return _get_npc_corporation(corporation_id).secondaryActivityID
    except KeyError:
        return default


def get_corporation_size_factor(corporation_id, default = None):
    try:
        return _get_npc_corporation(corporation_id).sizeFactor
    except KeyError:
        return default


def get_corporation_faction_id(corporation_id, default = None):
    try:
        return _get_npc_corporation(corporation_id).factionID
    except KeyError:
        return default


def get_corporation_friend_id(corporation_id, default = None):
    try:
        return _get_npc_corporation(corporation_id).friendID
    except KeyError:
        return default


def get_corporation_exchange_rates(corporation_id, default = None):
    try:
        return _get_npc_corporation(corporation_id).exchangeRates
    except KeyError:
        return default


def get_corporation_lp_offer_tables(corporation_id, default = None):
    try:
        return _get_npc_corporation(corporation_id).lpOfferTables
    except KeyError:
        return default


@Memoize
def get_all_corporation_trades():
    return {corp_id:corp.corporationTrades or {} for corp_id, corp in iter_npc_corporations()}


@Memoize
def get_corporation_trades_filtered(filter_attribute, filter_value):
    return {corp_id:corp.corporationTrades or {} for corp_id, corp in iter_npc_corporations() if getattr(corp, filter_attribute) == filter_value}


def get_corporation_trades(corporation_id, default = None):
    try:
        default = {} if default is None else default
        return _get_npc_corporation(corporation_id).corporationTrades or default
    except KeyError:
        return default


def get_supply_demand_for_type(corporation_id, type_id, default = None):
    corp = _get_npc_corporation(corporation_id)
    if corp is None or corp.corporationTrades is None:
        return default
    return corp.corporationTrades.get(type_id, default)


@Memoize
def get_corporation_ids_by_faction_ids():
    corp_ids_by_faction_id = defaultdict(list)
    for corporation_id, corporation in iter_npc_corporations():
        corp_ids_by_faction_id[corporation.factionID].append(corporation_id)

    return dict(corp_ids_by_faction_id)


def get_corporation_ids_by_faction_id(faction_id, default = None):
    return get_corporation_ids_by_faction_ids().get(faction_id, default)


@Memoize
def get_factions_with_corporations():
    return [ corp.factionID for corp_id, corp in iter_npc_corporations() if corp.factionID ]


def get_corporation_divisions(corporation_id, default = None):
    try:
        return _get_npc_corporation(corporation_id).divisions or default
    except KeyError:
        return default


def get_npc_corporation_name_id(corporation_id, default = None):
    try:
        return _get_npc_corporation(corporation_id).nameID
    except KeyError:
        return default


def get_npc_corporation_name(corporation_id, corporation = None, language_id = None, important = False):
    if corporation_id in OWNER_NAME_OVERRIDES:
        return _get_message(OWNER_NAME_OVERRIDES[corporation_id], language_id, important)
    if not corporation:
        corporation = get_npc_corporation(corporation_id)
    return _get_message(getattr(corporation, 'nameID', None), language_id, important)


def get_npc_corporation_description(corporation_id, corporation = None, language_id = None):
    if not corporation:
        corporation = get_npc_corporation(corporation_id)
    return _get_message(getattr(corporation, 'descriptionID', None), language_id)


def npc_corporation_exists(corporation_id):
    return corporation_id in get_npc_corporations()


def _get_message(message_id, language_id = None, important = False):
    import localization
    if important and boot.role == 'client':
        return localization.GetImportantByMessageID(message_id)
    return localization.GetByMessageID(message_id, language_id)


@Memoize
def get_corporation_station_count(corporation_id):
    return len({station.stationID for station in cfg.stations if station.ownerID == corporation_id})


@Memoize
def get_corporation_station_system_count(corporation_id):
    return len({station.solarSystemID for station in cfg.stations if station.ownerID == corporation_id})


@Memoize
def get_corporation_trade_types():
    return {typeID for trades in get_all_corporation_trades().itervalues() for typeID in trades}


@Memoize
def get_corporation_trade_groups_by_category():
    category_groups = defaultdict(set)
    for type_id in get_corporation_trade_types():
        group_id = evetypes.GetGroupID(type_id)
        category_groups[evetypes.GetCategoryIDByGroup(group_id)].add(group_id)

    return category_groups


def get_supply_demand_by_faction(faction_id):
    faction_type_supply_demand = defaultdict(float)
    for corpID, trades in get_corporation_trades_filtered('factionID', faction_id).iteritems():
        for type_id, supply_demand in trades.iteritems():
            faction_type_supply_demand[type_id] += supply_demand

    return faction_type_supply_demand


def get_supply_by_types():
    type_supply_demand = defaultdict(float)
    for corpID, trades in get_all_corporation_trades().iteritems():
        for type_id, supply_demand in trades.iteritems():
            if supply_demand > 0.0:
                type_supply_demand[type_id] += supply_demand

    return type_supply_demand


def get_demand_by_types():
    type_supply_demand = defaultdict(float)
    for corpID, trades in get_all_corporation_trades().iteritems():
        for type_id, supply_demand in trades.iteritems():
            if supply_demand < 0.0:
                type_supply_demand[type_id] += supply_demand

    return type_supply_demand


def get_corporation_activities():
    return CorporationActivitiesLoader.GetData()


def iter_activities():
    for activityID, activity in get_corporation_activities().iteritems():
        yield (activityID, activity)


def get_activity(activity_id, default = None):
    return get_corporation_activities().get(activity_id, default)


def get_corporation_activity_name(activity_id, activity = None):
    if activity is None:
        activity = get_activity(activity_id)
    if activity:
        return _get_message(activity.nameID)


def get_corporation_ticker_name(corporation_id):
    corporation = _get_npc_corporation(corporation_id)
    return corporation.tickerName


def get_designer_description(corporation_id):
    corporation = _get_npc_corporation(corporation_id)
    return corporation.DesignerDescriptionID
