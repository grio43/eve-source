#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\randomized.py
import random
from behaviors.tasks import Task
from carbon.common.lib.const import SEC
from ccpProfile import TimedFunction

class RandomChanceCondition(Task):

    @TimedFunction('behaviors::conditions::randomized::RandomChanceCondition::OnEnter')
    def OnEnter(self):
        if self.attributes.chance >= random.random():
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()


class CachedRandomChanceCondition(Task):

    @TimedFunction('behaviors::conditions::randomized::CachedRandomChanceCondition::OnEnter')
    def OnEnter(self):
        randomValue = self.GetLastBlackboardValue(self.attributes.randomValueAddress, maxAge=self.attributes.cacheTimeInSeconds * SEC)
        if randomValue is None:
            randomValue = random.random()
            self.SendBlackboardValue(self.attributes.randomValueAddress, randomValue)
        if self.attributes.chance >= randomValue:
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()
