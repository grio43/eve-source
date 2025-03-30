#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\decorators\timers.py
from behaviors.decorators import Decorator
import logging
from ccpProfile import TimedFunction
import random
logger = logging.getLogger(__name__)

class CooldownTimer(Decorator):

    @TimedFunction('behaviors::decorators::timers::CooldownTimer::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        channel = self.GetChannelFromAddress(self.attributes.timerAddress)
        timerValue = channel.GetLastMessageValue()
        if timerValue is None:
            super(CooldownTimer, self).OnEnter()
            self.context.timerManager.StartTimer(self.GetTimeoutSeconds(), channel)
        channel.AddObserver(self.OnTimeout)

    def GetTimeoutSeconds(self):
        return self.attributes.timeoutSeconds

    def OnTimeout(self, name, message):
        if message.value is None and not self.IsInvalid():
            self.behaviorTree.RequestReset(requestedBy=self)

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeToBlackboard(self.attributes.timerAddress, self.OnTimeout)
        super(CooldownTimer, self).CleanUp()


class RandomCooldownTimer(CooldownTimer):

    def GetTimeoutSeconds(self):
        return random.randint(self.attributes.minTimeoutSeconds, self.attributes.maxTimeoutSeconds)
