#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\text.py
import eveformat.client
import localization
from homestation.validation import ChangeHomeStationValidationError, SelfDestructCloneValidationError

class Label(object):

    def __init__(self, label, _placeholder = None):
        self.label = label
        self._placeholder = _placeholder

    def __call__(self, **kwargs):
        if self._placeholder and not localization.IsValidLabel(self.label):
            return self._placeholder.format(**kwargs)
        return localization.GetByLabel(self.label, **kwargs)


title_change_home_station = Label('UI/HomeStation/TitleChangeHomeStation')
header_change_home_station = Label('UI/HomeStation/TitleChangeHomeStation')
header_corporation_offices = Label('UI/HomeStation/HeaderCorporationOffices')
header_current_home_station = Label('UI/HomeStation/HeaderCurrentHomeStation')
header_current_station = Label('UI/HomeStation/HeaderCurrentStation')
header_school_station = Label('UI/HomeStation/HeaderSchoolStation')
header_self_destruct_clone = Label('UI/HomeStation/HeaderSelfDestructClone')
description_change_home_station = Label('UI/HomeStation/DescriptionChangeHomeStation')
description_self_destruct_clone = Label('UI/HomeStation/DescriptionSelfDestructClone')
action_cancel = Label('UI/Common/Buttons/Cancel')
action_select_new_home_station = Label('UI/HomeStation/ActionSelectNewHomeStation')
action_self_destruct_clone = Label('UI/HomeStation/ActionSelfDestructClone')
action_set_destination = Label('UI/Commands/SetDestination')
action_set_home_station = Label('UI/Medical/Clone/SetHomeStationButton')
feedback_destination_set = Label('UI/Inflight/DestinationSet')
hint_home_station_benefits = Label('UI/HomeStation/HintHomeStationBenefits')
hint_corporation_offices_header = Label('UI/HomeStation/HintCorporationOfficesHeader')
hint_school_station_header = Label('UI/HomeStation/HintSchoolStationHeader')
hint_already_in_home_station = Label('UI/Medical/ErrorAlreadyAtHomeStation')
no_content_hint_corporation_offices = Label('UI/HomeStation/NoContentHintCorporationOffices')
no_content_hint_current_station = Label('UI/HomeStation/NoContentHintCurrentStation')
no_content_hint_school_station = Label('UI/HomeStation/NoContentHintSchoolStation')
warning_self_destruct_clone = Label('UI/HomeStation/WarningSelfDestructClone')
fallback_station_info_card = Label('UI/HomeStation/FallbackStationInfoCard')
remote_change_cooldown_info_card = Label('UI/HomeStation/RemoteChangeCooldownInfoCard')
just_a_moment = Label('UI/HomeStation/JustAMoment')
error_loading_home_station_candidates = Label('UI/HomeStation/ErrorLoadingHomeStationCandidates')
bracket_hint = Label('UI/HomeStation/BracketHint')

def station_name(station_id):
    return _get_cfg().evelocations.Get(station_id).name


def prime_station_names(station_ids):
    _get_cfg().evelocations.Prime(station_ids)


def solar_system_trace(solar_system_id):
    cfg = _get_cfg()
    solar_system = cfg.mapSystemCache.Get(solar_system_id)
    constellation = cfg.mapConstellationCache.Get(solar_system.constellationID)
    constellation_name = cfg.evelocations.Get(solar_system.constellationID).name
    region_name = cfg.evelocations.Get(constellation.regionID).name
    solar_system_name = eveformat.solar_system_with_security_and_jumps(solar_system_id)
    return u'{} > {} > {}'.format(region_name, constellation_name, solar_system_name)


def describe_change_home_station_validation_error(error):
    label = _validation_error_description_by_error.get(error, _default_validation_error)
    return label()


_default_validation_error = Label('UI/HomeStation/Validation/UnexpectedError')
_validation_error_description_by_error = {ChangeHomeStationValidationError.UNHANDLED_EXCEPTION: _default_validation_error,
 ChangeHomeStationValidationError.STATION_IN_WORMHOLE: Label('UI/HomeStation/Validation/StationInWormhole'),
 ChangeHomeStationValidationError.ALREADY_SET_AS_HOME_STATION: Label('UI/HomeStation/Validation/AlreadySetAsHomeStation'),
 ChangeHomeStationValidationError.REMOTE_COOLDOWN: Label('UI/HomeStation/Validation/RemoteCooldown'),
 ChangeHomeStationValidationError.FAC_WAR_ENEMY_STATION: Label('UI/HomeStation/Validation/FacWarEnemyStation'),
 ChangeHomeStationValidationError.INVALID_CANDIDATE: Label('UI/HomeStation/Validation/InvalidCandidate'),
 ChangeHomeStationValidationError.TRIGLAVIAN_SYSTEM: Label('UI/HomeStation/Validation/TriglavianSystem')}

def describe_self_destruct_clone_validation_error(error):
    label = _self_destruct_clone_validation_error_description.get(error, _default_validation_error)
    return label()


_self_destruct_clone_validation_error_description = {SelfDestructCloneValidationError.UNHANDLED_EXCEPTION: _default_validation_error,
 SelfDestructCloneValidationError.ALREADY_IN_HOME_STATION: Label('UI/Medical/ErrorAlreadyAtHomeStation'),
 SelfDestructCloneValidationError.NOT_DOCKED: Label('UI/HomeStation/Validation/NotDocked'),
 SelfDestructCloneValidationError.NOT_IN_CAPSULE: Label('UI/HomeStation/Validation/NotInCapsule')}

def _get_cfg():
    import __builtin__
    return __builtin__.cfg
