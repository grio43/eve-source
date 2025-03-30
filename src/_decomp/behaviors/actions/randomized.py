#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\randomized.py
from ccpProfile import TimedFunction
import random
from behaviors.tasks import Task

class PostRandomIntegerToBlackboard(Task):

    @TimedFunction('behaviors::actions::randomized::PostRandomIntegerToBlackboard::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        self.SendBlackboardValue(self.attributes.blackboardAddress, random.randint(self.attributes.minValue, self.attributes.maxValue))


class ScaleValueRandomized(Task):

    @TimedFunction('behaviors::actions::randomized::ScaleValueRandomized::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        value = self.GetLastBlackboardValue(self.attributes.valueAddress)
        scalar = random.uniform(self.attributes.minValue, self.attributes.maxValue)
        self.SendBlackboardValue(self.attributes.valueAddress, value * scalar)
