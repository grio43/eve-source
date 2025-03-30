#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterdata\factions.py
from collections import namedtuple
from caching import Memoize
from eveprefs import boot
from fsdBuiltData.common.base import BuiltDataLoader
from inventorycommon.const import ownerNone
from npcs.npccorporations import get_corporation_faction_id
try:
    import factionsLoader
except ImportError:
    factionsLoader = None

Faction = namedtuple('Faction', ['nameID',
 'descriptionID',
 'shortDescriptionID',
 'corporationID',
 'iconID',
 'uniqueName',
 'militiaCorporationID',
 'sizeFactor',
 'solarSystemID',
 'memberRaces',
 'npcTag'])

class FactionsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/factions.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/factions.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/factions.fsdbinary'
    __loader__ = factionsLoader


def get_factions():
    return FactionsLoader.GetData()


def get_faction_data(faction_id):
    return get_factions()[faction_id]


def get_faction(faction_id):
    faction = get_factions()[faction_id]
    return Faction(faction.nameID, faction.descriptionID, faction.shortDescriptionID, faction.corporationID or ownerNone, faction.iconID, faction.uniqueName, faction.militiaCorporationID, faction.sizeFactor, faction.solarSystemID, faction.memberRaces, faction.npcTag)


def iter_factions():
    for faction_id in iter_faction_ids():
        yield (faction_id, get_faction(faction_id))


def iter_faction_ids():
    for faction_id in get_factions().iterkeys():
        yield faction_id


def get_faction_ids():
    return get_factions().keys()


def faction_exists(faction_id):
    return faction_id in get_factions()


def get_faction_races(faction_id):
    faction = get_faction(faction_id)
    return faction.memberRaces


@Memoize
def get_station_count(faction_id):
    return len({station.stationID for station in cfg.stations if get_corporation_faction_id(station.ownerID) == faction_id})


@Memoize
def get_station_system_count(faction_id):
    return len({station.solarSystemID for station in cfg.stations if get_corporation_faction_id(station.ownerID) == faction_id})


def get_faction_name(faction_id, faction = None, language_id = None, important = False):
    if not faction:
        faction = get_faction(faction_id)
    return _get_message(faction.nameID, language_id, important)


def get_faction_description(faction_id, faction = None):
    if not faction:
        faction = get_faction(faction_id)
    return _get_message(faction.descriptionID)


def get_faction_short_description(faction_id, faction = None):
    if not faction:
        faction = get_faction(faction_id)
    if faction.shortDescriptionID:
        return _get_message(faction.shortDescriptionID)


def get_faction_logo_flat(faction_id):
    import eveicon
    if not faction_id:
        return
    logo_id = get_faction_data(faction_id).flatLogo
    if logo_id:
        return eveicon.get(logo_id)


def get_faction_logo_flat_with_name(faction_id, fallback_without_name = True):
    import eveicon
    if not faction_id:
        return
    faction_data = get_faction_data(faction_id)
    logo_id = faction_data.flatLogoWithName or (faction_data.flatLogo if fallback_without_name else None)
    if logo_id:
        return eveicon.get(logo_id)


def _get_message(message_id, language_id = None, important = False):
    import localization
    if important and boot.role == 'client':
        return localization.GetImportantByMessageID(message_id)
    return localization.GetByMessageID(message_id, language_id)
