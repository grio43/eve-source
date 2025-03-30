#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evestations\standingsrestriction.py
from eveprefs import boot
from eveexceptions import UserError
from eve.common.lib import appConst
from eve.common.script.sys.idCheckers import IsStation, IsCharacter, IsFaction
from fsdBuiltData.common.base import BuiltDataLoader
from log import LogWarn
try:
    import stationStandingsRestrictionsLoader
except ImportError:
    stationStandingsRestrictionsLoader = None

class StationStandingsRestrictions(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/stationStandingsRestrictions.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/stationStandingsRestrictions.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/stationStandingsRestrictions.fsdbinary'
    __loader__ = stationStandingsRestrictionsLoader


_restricted_services = [appConst.stationServiceReprocessingPlant,
 appConst.stationServiceRepairFacilities,
 appConst.stationServiceFactory,
 appConst.stationServiceFitting,
 appConst.stationServiceDocking,
 appConst.stationServiceOfficeRental,
 appConst.stationServiceJumpCloneFacility]
_requires_corporation = [appConst.stationServiceOfficeRental]
_error_messages = {appConst.stationServiceOfficeRental: 'StandingsRestrictionCorporationGeneric'}
_default_error_message = 'StandingsRestrictionGeneric'
_restriction_labels = {appConst.stationServiceReprocessingPlant: 'UI/Station/ReprocessingPlant',
 appConst.stationServiceRepairFacilities: 'UI/Station/Repairshop',
 appConst.stationServiceFactory: 'UI/Industry/Industry',
 appConst.stationServiceFitting: 'UI/Station/Fitting',
 appConst.stationServiceDocking: 'UI/StructureSettings/ServiceDocking',
 appConst.stationServiceOfficeRental: 'UI/StructureSettings/ServiceCorpOffices',
 appConst.stationServiceJumpCloneFacility: 'UI/Medical/JumpClone'}

def check_station_standings_restriction(service_id, station_id, comparing_id):
    if _is_invalid(service_id, station_id):
        return
    station = cfg.stations.Get(station_id)
    _check_standings(service_id, station.ownerID, comparing_id)
    faction_id = getattr(cfg.mapSystemCache.Get(station.solarSystemID), 'factionID', None)
    if faction_id:
        _check_standings(service_id, faction_id, comparing_id)


def get_station_standings_restriction(service_id, station_id, comparing_id):
    try:
        check_station_standings_restriction(service_id, station_id, comparing_id)
    except UserError as error:
        return error.dict


def is_station_standings_restricted(service_id, station_id, comparing_id):
    try:
        check_station_standings_restriction(service_id, station_id, comparing_id)
    except UserError:
        return True

    return False


def get_station_standings_restriction_info(service_id, station_id):
    if _is_invalid(service_id, station_id):
        return
    station = cfg.stations.Get(station_id)
    required_standing = _get_required_standings(service_id, station.ownerID)
    if required_standing:
        return {'from_id': station.ownerID,
         'required_standing': required_standing}
    faction_id = getattr(cfg.mapSystemCache.Get(station.solarSystemID), 'factionID', None)
    if faction_id:
        required_standing = _get_required_standings(service_id, faction_id)
        if required_standing:
            return {'from_id': faction_id,
             'required_standing': required_standing}


def get_station_standings_restriction_info_many(service_ids, station_id):
    for service_id in service_ids:
        restriction = get_station_standings_restriction_info(service_id, station_id)
        if restriction:
            return restriction


def get_all_station_standings_restrictions(owner_id):
    restrictions = StationStandingsRestrictions.GetData().get(owner_id, None)
    if not restrictions:
        return {}
    return restrictions.services


def get_all_station_standings_restrictions_personal(owner_id):
    service_restrictions = get_all_station_standings_restrictions(owner_id)
    return {service_id:value for service_id, value in service_restrictions.iteritems() if service_id not in _requires_corporation}


def get_all_station_standings_restrictions_corporate(owner_id):
    service_restrictions = get_all_station_standings_restrictions(owner_id)
    return {service_id:value for service_id, value in service_restrictions.iteritems() if service_id in _requires_corporation}


def get_station_standings_restriction_label(service_id):
    return _restriction_labels[service_id]


def _is_invalid(service_id, station_id):
    if not IsStation(station_id):
        LogWarn('Can only check standings restrictions for stations')
        return True
    if service_id not in _restricted_services:
        return True


def _check_standings(service_id, from_id, to_id):
    required_standing = _get_required_standings(service_id, from_id)
    if required_standing is None:
        return
    current_standing = round(_get_standing(from_id, to_id), 2)
    required_standing = round(required_standing, 2)
    if current_standing < required_standing:
        raise UserError(_error_messages.get(service_id, _default_error_message), {'from_id': from_id,
         'to_id': to_id,
         'current_standing': current_standing,
         'required_standing': required_standing})


def _get_required_standings(service_id, owner_id):
    service_restrictions = get_all_station_standings_restrictions(owner_id)
    return service_restrictions.get(service_id, None)


def _get_standing(from_id, to_id):
    if boot.role == 'client':
        return sm.GetService('standing').GetStandingWithSkillBonus(from_id, to_id)
    is_from_faction = IsFaction(from_id)
    is_to_character = IsCharacter(to_id)
    standing_matrix = sm.GetService('standingMgr').GetStandingMatrix(from_id, to_id, adjustForSkills=is_to_character)
    if is_from_faction:
        standing_values = standing_matrix.faction
    else:
        standing_values = standing_matrix.corp
    if is_to_character:
        return standing_values.char
    else:
        return standing_values.corp
