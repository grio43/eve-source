#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\lpOffers\exceptions.py
from eveexceptions import UserError

class InsufficientBalanceError(StandardError):
    pass


class MissingCorpRoleError(StandardError):
    pass


class WrongCorporationMembershipError(StandardError):
    pass


class TransfersDisabledError(UserError):
    pass
