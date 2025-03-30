#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\validation.py
import abc
import logging
from eveexceptions import UserError
log = logging.getLogger(__name__)

class ChangeHomeStationValidationError(UserError):
    UNHANDLED_EXCEPTION = 0
    STATION_IN_WORMHOLE = 1
    ALREADY_SET_AS_HOME_STATION = 2
    REMOTE_COOLDOWN = 3
    FAC_WAR_ENEMY_STATION = 4
    INVALID_CANDIDATE = 5
    TRIGLAVIAN_SYSTEM = 6

    def __init__(self, errors):
        super(ChangeHomeStationValidationError, self).__init__('ChangeHomeStationValidationError')
        self.errors = errors

    def __str__(self):
        return 'ChangeHomeStationValidationError: {}'.format(str(self.errors))


def is_remote(is_current_station, is_school_hq):
    return not (is_current_station or is_school_hq)


def is_remote_change(new_home_station_id, docked_id, school_hq_id):
    return is_remote(is_current_station=new_home_station_id == docked_id, is_school_hq=new_home_station_id == school_hq_id)


class SelfDestructCloneValidatorBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def in_capsule(self):
        pass

    @abc.abstractproperty
    def docked_id(self):
        pass

    @abc.abstractproperty
    def home_station_id(self):
        pass

    @property
    def is_docked(self):
        return self.docked_id is not None

    @property
    def in_home_station(self):
        return self.is_docked and self.docked_id == self.home_station_id

    def validate(self):
        errors = []
        try:
            if self.in_home_station:
                errors.append(SelfDestructCloneValidationError.ALREADY_IN_HOME_STATION)
            if not self.is_docked:
                errors.append(SelfDestructCloneValidationError.NOT_DOCKED)
            if not self.in_capsule:
                errors.append(SelfDestructCloneValidationError.NOT_IN_CAPSULE)
        except Exception:
            log.exception('Unhandled exception during validation')
            errors.append(SelfDestructCloneValidationError.UNHANDLED_EXCEPTION)

        return errors


class SelfDestructCloneValidationError(UserError):
    UNHANDLED_EXCEPTION = 0
    NOT_DOCKED = 1
    NOT_IN_CAPSULE = 2
    ALREADY_IN_HOME_STATION = 3

    def __init__(self, errors):
        super(SelfDestructCloneValidationError, self).__init__('SelfDestructCloneValidationError')
        self.errors = errors

    def __str__(self):
        return 'SelfDestructCloneValidationError: {}'.format(str(self.errors))
