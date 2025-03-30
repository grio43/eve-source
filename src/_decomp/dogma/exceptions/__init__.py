#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\exceptions\__init__.py
__author__ = 'unnar'
from eveexceptions import UserError

class ItemExpiredError(Exception):
    pass


class EmbarkOnlineError(UserError):
    propagate = True


class EffectFailedButShouldBeStopped(Exception):
    pass
