#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\skyhook\client\errors.py


class SkyhookError(Exception):
    pass


class SkyhookNotFoundError(SkyhookError):
    pass


class SkyhookAccessForbiddenError(SkyhookError):
    pass


class SkyhookActivateForbiddenError(SkyhookError):
    pass


class SkyhookDeactivateForbiddenError(SkyhookError):
    pass


class SkyhookDeactivateInternalError(SkyhookError):
    pass


class SkyhookBadRequestError(SkyhookError):
    pass
