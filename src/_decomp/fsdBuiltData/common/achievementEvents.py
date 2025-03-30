#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\achievementEvents.py
from fsdBuiltData.common.base import BuiltDataLoader
import achievementEventsLoader

class AchievementEvents(BuiltDataLoader):
    __loader__ = achievementEventsLoader
    __resBuiltFile__ = 'res:/staticData/achievementEvents.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/achievementEvents.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/achievementEvents.fsdbinary'

    @classmethod
    def GetName(cls, eventID):
        return cls.GetAchievementEvent(eventID).name

    @classmethod
    def GetDescription(cls, eventID):
        return cls.GetAchievementEvent(eventID).description

    @classmethod
    def GetAchievementEvent(cls, eventID):
        return cls.GetData().get(eventID, None)
