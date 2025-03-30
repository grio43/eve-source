#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\common\exceptions.py


class NotEnoughAnalysisPointsToTakeFromPlayer(ValueError):
    pass


class NoActiveClassificationTaskError(Exception):
    pass


class UnexpectedMmosResultError(Exception):
    pass


class TooFewPolygonsMmosResultError(UnexpectedMmosResultError):
    pass


class TooFewVerticesMmosResultError(UnexpectedMmosResultError):
    pass


class NoConnectionToAPIError(Exception):
    pass


class MissingKeyError(Exception):
    pass


class NotAllowedToGainExperience(Exception):

    def __init__(self, total_skill_points):
        self.total_skill_points = total_skill_points
