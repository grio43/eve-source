#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\common\errors.py


class ServiceUnavailable(RuntimeError):
    pass


class GenericError(RuntimeError):
    pass


class UnknownMercenaryDen(RuntimeError):
    pass


class RegistrationInvalid(RuntimeError):
    REASON_UNKNONWN = 'MercenaryDen_DeploymentFailed'
    REASON_SKILL_LIMITS = 'MercenaryDen_DeploymentFailed_SkillLimits'
    REASON_SKYHOOK_ALREADY_OCCUPIED = 'MercenaryDen_DeploymentFailed_SkyhookAlreadyOccupied'
    REASON_SKYHOOK_NOT_FOUND = 'MercenaryDen_DeploymentFailed_RequiresNearbySkyhook'
    REASON_SKYHOOK_OFFLINE = 'MercenaryDen_DeploymentFailed_RequiresOnlineSkyhook'
    REASON_PLANET_DOES_NOT_SUPPORT_DENS = 'MercenaryDen_DeploymentFailed_MustBeTemperatePlanet'
    REASON_MAXIMUM_DENS_REACHED = 'MercenaryDen_DeploymentFailed_MaximumDensReached'

    def __init__(self, reason, arguments = None):
        self.reason = reason
        self.arguments = arguments or {}


class UnknownActivity(RuntimeError):
    pass


class ActivityAlreadyStarted(RuntimeError):
    pass


class ActivityValidationFailed(RuntimeError):
    pass


class GetMaximumDensError(Exception):
    pass


class GetMaximumDensInternalError(GetMaximumDensError):
    pass
