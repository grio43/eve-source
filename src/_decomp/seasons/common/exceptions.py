#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\common\exceptions.py


class ChallengeForCharacterNotFoundError(Exception):
    pass


class NotEnoughChallengeTypesAvailableError(Exception):
    pass


class ChallengeTypeNotFoundError(Exception):
    pass


class ChallengeAlreadyExpiredError(Exception):
    pass


class ChallengeAlreadyCompletedError(Exception):
    pass


class ChallengeChainIsCircularError(Exception):
    pass


class SeasonNotSelectedError(Exception):
    pass
