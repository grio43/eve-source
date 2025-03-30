#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\upgrades\client\errors.py


class SovUpgradeNotFoundError(Exception):
    pass


class SovUpgradeDataUnavailableError(Exception):
    pass


class SovUpgradeDataAccessRestrictedError(SovUpgradeDataUnavailableError):
    pass


class SovInstalledUpgradeError(Exception):
    pass


class SovUpgradeInstallError(Exception):
    pass


class SovUpgradeInstallBadRequestError(SovUpgradeInstallError):
    pass


class SovUpgradeInstallUnauthorizedError(SovUpgradeInstallError):
    pass


class SovUpgradeInstallNotFoundError(SovUpgradeInstallError):
    pass


class SovUpgradeInstallConflictError(SovUpgradeInstallError):
    pass


class SovUpgradeInstallInternalError(SovUpgradeInstallError):
    pass


class SovUpgradeUninstallError(Exception):
    pass


class SovUpgradeUninstallForbiddenError(SovUpgradeUninstallError):
    pass


class SovUpgradeUninstallNotFoundError(SovUpgradeUninstallError):
    pass


class SovUpgradeUninstallInternalErrorError(SovUpgradeUninstallError):
    pass
