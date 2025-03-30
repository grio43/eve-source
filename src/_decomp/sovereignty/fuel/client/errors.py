#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\fuel\client\errors.py


class SovFuelGetCapacityError(Exception):
    pass


class SovFuelGetCapacityForbiddenError(SovFuelGetCapacityError):
    pass


class SovFuelGetCapacityInternalError(SovFuelGetCapacityError):
    pass


class SovFuelGetLevelsError(Exception):
    pass


class SovFuelGetLevelsForbiddenError(SovFuelGetLevelsError):
    pass


class SovFuelGetLevelInternalError(SovFuelGetLevelsError):
    pass


class SovFuelGetBurnRateError(Exception):
    pass


class SovFuelGetBurnRateForbiddenError(SovFuelGetBurnRateError):
    pass


class SovFuelGetBurnRateInternalError(SovFuelGetBurnRateError):
    pass


class SovFuelAddRequestError(Exception):
    pass


class SovFuelAddRequestForbiddenError(SovFuelAddRequestError):
    pass


class SovFuelAddRequestNotFoundError(SovFuelAddRequestError):
    pass


class SovFuelAddRequestInternalError(SovFuelAddRequestError):
    pass
