#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\structures\exceptions.py


class StructurePaintError(StandardError):
    pass


class InvalidDataError(StandardError):
    pass


class InsufficientRolesError(StandardError):
    pass


class InsufficientBalanceError(StandardError):
    pass


class StructureTypeNotEligibleError(StandardError):
    pass


class LicenseNotFoundException(StandardError):
    pass


class ForbiddenRequestError(StandardError):
    pass
