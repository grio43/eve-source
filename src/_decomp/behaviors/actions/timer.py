#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\timer.py
import logging
import random
import uthread2
from behaviors import status
from behaviors.tasks import Task
from ccpProfile import TimedFunction
logger = logging.getLogger(__name__)

class TimeoutAction(Task):

    def __init__(self, attributes):
        super(TimeoutAction, self).__init__(attributes)

    @TimedFunction('behaviors::actions::timer::TimeoutAction::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        timeoutThread = uthread2.StartTasklet(self._TimeoutThread)
        self.SetContextValue('timeoutThread', timeoutThread)

    def CleanUp(self):
        super(TimeoutAction, self).CleanUp()
        timeoutThread = self.GetContextValue('timeoutThread')
        if timeoutThread:
            timeoutThread.kill()

    def _TimeoutThread(self):
        timeoutSeconds = self._GetTimeoutSeconds()
        logger.debug('OnTimeout started timeoutSeconds %s', timeoutSeconds)
        uthread2.SleepSim(timeoutSeconds)
        logger.debug('OnTimeout waking up')
        self._OnTimeout()

    def _OnTimeout(self):
        raise NotImplementedError

    def _GetTimeoutSeconds(self):
        if getattr(self.attributes, 'timeoutMilliSecondsAddress', None):
            return self.GetLastBlackboardValue(self.attributes.timeoutMilliSecondsAddress) / 1000
        return self.attributes.timeoutSeconds


class FailUntilTimeoutAction(Task):

    @TimedFunction('behaviors::actions::timer::FailUntilTimeoutAction::OnEnter')
    def OnEnter(self):
        resetValue = self.GetLastBlackboardValue(self.attributes.triggerAddress)
        if resetValue:
            self.SetStatusToSuccess()
            self.SendBlackboardValue(self.attributes.triggerAddress, False)
        else:
            self.SetStatusToFailed()
        channel = self.GetChannelFromAddress(self.attributes.timerAddress)
        timerValue = channel.GetLastMessageValue()
        if timerValue is None:
            self.SetStatusToFailed()
            self.context.timerManager.StartTimer(self.attributes.timeoutSeconds, channel)
        channel.AddObserver(self._OnTimeout)

    def _OnTimeout(self, name, message):
        if message.value is None and not self.IsInvalid():
            self.SendBlackboardValue(self.attributes.triggerAddress, True)
            channel = self.GetChannelFromAddress(self.attributes.timerAddress)
            self.context.timerManager.StartTimer(self.attributes.timeoutSeconds, channel)
            self.behaviorTree.RequestReset(requestedBy=self)

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeToBlackboard(self.attributes.timerAddress, self._OnTimeout)
        super(FailUntilTimeoutAction, self).CleanUp()


class SucceedAfterTimeoutAction(TimeoutAction):

    @TimedFunction('behaviors::actions::timer::SucceedAfterTimeoutAction::OnEnter')
    def OnEnter(self):
        super(SucceedAfterTimeoutAction, self).OnEnter()
        self.SetStatusToSuspended()

    def _OnTimeout(self):
        if not self.IsInvalid():
            self.SetStatusToSuccess()
            self.status.OnUpdated(self)
            self.behaviorTree.StartTaskNextTick(self)


class ClearValueAndResetAfterTimeout(TimeoutAction):

    def _OnTimeout(self):
        self.SendBlackboardValue(self.attributes.targetAddress, None)
        self.behaviorTree.RequestReset(requestedBy=self)


class BlockWhileTimeout(Task):

    @TimedFunction('behaviors::actions::timer::BlockWhileTimeout::OnEnter')
    def OnEnter(self):
        timerValue = self.GetLastBlackboardValue(self.attributes.timerAddress)
        if self.attributes.maxRandomTimeoutSeconds:
            secondsUntilReset = random.randint(self.attributes.timeoutSeconds, self.attributes.maxRandomTimeoutSeconds)
        else:
            secondsUntilReset = self.attributes.timeoutSeconds
        if timerValue is None:
            channel = self.GetChannelFromAddress(self.attributes.timerAddress)
            self.context.timerManager.StartTimer(secondsUntilReset, channel)
        self.status = status.TaskSuspendedStatus
        self.SubscribeToBlackboard(self.attributes.timerAddress, self._OnTimeout)

    def OnExit(self):
        self.UnsubscribeToBlackboard(self.attributes.timerAddress, self._OnTimeout)

    def _OnTimeout(self, name, message):
        if self.IsInvalid():
            return
        if message.value is None:
            self.SetStatusToSuccess()
            self.behaviorTree.StartTaskNextTick(self)

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeToBlackboard(self.attributes.timerAddress, self._OnTimeout)
        super(BlockWhileTimeout, self).CleanUp()


class ClearTimer(Task):

    def OnEnter(self):
        timer_id = self.GetLastBlackboardValue(self.attributes.timerAddress)
        if timer_id is not None:
            self.context.timerManager.ClearTimer(timer_id)
        self.SetStatusToSuccess()
