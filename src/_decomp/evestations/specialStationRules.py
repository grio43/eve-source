#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evestations\specialStationRules.py
from eve.common.script.util.facwarCommon import GetOccupierFWFactions, GetPirateFWFactions
from eve.common.lib import appConst
from inventorycommon.const import stationFulcrumZarzakh

def is_restricted_by_special_station_rules(station_id, service_id, char_id):
    rule = _get_rule_for_sevice_in_station_id(station_id, service_id)
    if not rule:
        return False
    is_access_restricted = rule.is_access_restricted(char_id)
    return is_access_restricted


def check_is_restricted_by_special_station_rules(station_id, service_id, char_id):
    rule = _get_rule_for_sevice_in_station_id(station_id, service_id)
    if not rule:
        return False
    rule.check_is_access_restricted(station_id, service_id, char_id)


def _get_rule_for_sevice_in_station_id(station_id, service_id):
    special_station_rules = _get_station_rules()
    rules_for_station = special_station_rules.get(station_id)
    if not rules_for_station:
        return
    rule = rules_for_station.get(service_id)
    return rule


_station_rules = None

def _get_station_rules():
    global _station_rules
    if not _station_rules:
        _station_rules = {stationFulcrumZarzakh: {appConst.stationServiceDocking: RuleInBannedFwFaction(bannded_faction_ids=GetOccupierFWFactions()),
                                 appConst.stationServiceJumpCloneFacility: RuleNotInAllowedFwFaction(allowed_factions_ids=GetPirateFWFactions()),
                                 appConst.stationServiceOfficeRental: RuleCorpNotInAllowedFwFaction(allowed_factions_ids=GetPirateFWFactions())}}
    return _station_rules


class RuleBase(object):

    def is_access_restricted(self, char_id):
        pass

    def check_is_access_restricted(self, station_id, service_id, char_id):
        if self.is_access_restricted(char_id):
            return self._raise_user_error(station_id, service_id, char_id)

    def _raise_user_error(self, station_id, service_id, char_id):
        raise UserError('UnableToUseStationService')


class RuleInBannedFwFaction(RuleBase):

    def __init__(self, bannded_faction_ids):
        self._banned_faction_ids = bannded_faction_ids

    def is_access_restricted(self, char_id):
        faction_id = sm.GetService('facWarMgr').GetCharacterEnrolledFaction(char_id)
        return faction_id in self._banned_faction_ids

    def _raise_user_error(self, station_id, service_id, char_id):
        raise UserError('MilitiaUnableToUseService', {'stationName': (const.UE_LOCID, station_id)})


class RuleNotInAllowedFwFaction(RuleBase):

    def __init__(self, allowed_factions_ids):
        self._allowed_faction_ids = allowed_factions_ids

    def is_access_restricted(self, char_id):
        faction_id = sm.GetService('facWarMgr').GetCharacterEnrolledFaction(char_id)
        return faction_id not in self._allowed_faction_ids

    def _raise_user_error(self, station_id, service_id, char_id):
        raise UserError('NotInRightMilitiaUnableToUseService', {'stationName': (const.UE_LOCID, station_id)})


class RuleCorpNotInAllowedFwFaction(RuleBase):

    def __init__(self, allowed_factions_ids):
        self._allowed_faction_ids = allowed_factions_ids

    def is_access_restricted(self, char_id):
        char_corp_id = sm.GetService('corporationSvc').GetCorporationIDForCharacter(char_id)
        faction_id = sm.GetService('facWarMgr').GetCorporationWarFactionID(char_corp_id)
        return faction_id not in self._allowed_faction_ids

    def _raise_user_error(self, station_id, service_id, char_id):
        raise UserError('CorporationUnableToUseService', {'stationName': (const.UE_LOCID, station_id)})
