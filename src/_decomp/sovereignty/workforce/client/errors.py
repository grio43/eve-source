#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\workforce\client\errors.py


class SovWorkforceError(Exception):
    pass


class SovWorkforceGetConfigError(SovWorkforceError):
    pass


class SovWorkforceGetConfigForbiddenError(SovWorkforceGetConfigError):
    pass


class SovWorkforceGetConfigInternalError(SovWorkforceError):
    pass


class SovWorkforceConfigureError(SovWorkforceError):
    pass


class SovWorkforceConfigureForbiddenError(SovWorkforceConfigureError):
    pass


class SovWorkforceConfigureInternalError(SovWorkforceConfigureError):
    pass


class SovWorkforceGetStateError(SovWorkforceError):
    pass


class SovWorkforceGetStateForbiddenError(SovWorkforceGetStateError):
    pass


class SovWorkforceGetStateInternalError(SovWorkforceGetStateError):
    pass


class SovWorkforceGetNetworkableHubsError(SovWorkforceError):
    pass
