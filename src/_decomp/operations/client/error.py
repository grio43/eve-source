#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\client\error.py


class FailedToActivateOperationError(Exception):
    pass


class OperationNotReplayable(FailedToActivateOperationError):
    pass


class ReplayCancelledByUser(FailedToActivateOperationError):
    pass


class FailedToActivateDueToPrerequisites(FailedToActivateOperationError):
    pass


class FailedToActivateByServer(FailedToActivateOperationError):
    pass


class FailedToActivateInUnknownSpace(FailedToActivateOperationError):
    pass
