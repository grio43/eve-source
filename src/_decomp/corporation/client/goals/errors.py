#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\client\goals\errors.py


class GoalError(RuntimeError):

    def __init__(self, message):
        super(GoalError, self).__init__(self)
        self.message = message

    def __str__(self):
        return self.message


class GoalNotFound(GoalError):

    def __init__(self, goal_id, corporation_id = None):
        if corporation_id:
            message = 'Failed to find goal with ID {goal_id} for corporation {corporation_name}'.format(goal_id=goal_id, corporation_name=cfg.eveowners.Get(corporation_id).name)
        else:
            message = 'Failed to find goal with ID {goal_id}'.format(goal_id=goal_id)
        super(GoalNotFound, self).__init__(message)


class GoalMessengerError(GoalError):

    def __init__(self, request, status_code):
        message = '{request} returning with status code {status_code}'.format(request=request, status_code=status_code)
        super(GoalMessengerError, self).__init__(message)


class AtGoalCapacity(GoalError):
    pass


class BadRequestToReserveAsset(GoalError):
    pass


class WalletAccessForbidden(GoalError):
    pass


class InternalErrorReservingAsset(GoalError):
    pass


class GoalPaymentHasNoEntitlement(GoalError):
    pass


class InsufficientFunds(GoalError):
    pass


class InvalidExpirationTime(GoalError):
    pass
