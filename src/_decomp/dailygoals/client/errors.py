#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dailygoals\client\errors.py


class GoalError(RuntimeError):

    def __init__(self, message):
        super(GoalError, self).__init__(self)
        self.message = message

    def __str__(self):
        return self.message


class GoalMessengerError(GoalError):

    def __init__(self, request, status_code):
        message = '{request} returning with status code {status_code}'.format(request=request, status_code=status_code)
        self.status_code = status_code
        super(GoalMessengerError, self).__init__(message)


class GoalNotRedeemableToCurrentLocation(GoalError):

    def __init__(self, player_location, goal_id):
        message = 'Unable to redeem {goal_id} to location {location}'.format(goal_id=goal_id, location=player_location)
        super(GoalNotRedeemableToCurrentLocation, self).__init__(message)
