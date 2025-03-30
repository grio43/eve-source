#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\timers.py
import uthread2
from behaviors import status
from behaviors.tasks import Task
from ccpProfile import TimedFunction

class ResetAfterTimeout(Task):

    def __init__(self, attributes):
        super(ResetAfterTimeout, self).__init__(attributes)
        self.timeoutThread = None

    @TimedFunction('behaviors::monitors::timers::ResetAfterTimeout::OnEnter')
    def OnEnter(self):
        self.status = status.TaskSuccessStatus
        timerValue = self.GetLastBlackboardValue(self.attributes.timerAddress)
        secondsUntilReset = self.attributes.timeoutSeconds
        if timerValue is None:
            self._StartTimer(secondsUntilReset)

    @TimedFunction('behaviors::monitors::timers::ResetAfterTimeout::TimeoutThread')
    def TimeoutThread(self, secondsUntilReset):
        uthread2.SleepSim(secondsUntilReset)
        if self.status == status.TaskInvalidStatus:
            return
        self.SendBlackboardValue(self.attributes.timerAddress, None)
        self.behaviorTree.RequestReset(requestedBy=self)

    def CleanUp(self):
        self.timeoutThread = None
        self.status = status.TaskInvalidStatus

    def _StartTimer(self, secondsUntilReset):
        self.timeoutThread = uthread2.StartTasklet(self.TimeoutThread, secondsUntilReset)
        self.SendBlackboardValue(self.attributes.timerAddress, secondsUntilReset)


class ResetAfterTimeoutBlocks(ResetAfterTimeout):

    @TimedFunction('behaviors::monitors::timers::ResetAfterTimeoutBlocks::OnEnter')
    def OnEnter(self):
        self.status = status.TaskFailureStatus
        timerValue = self.GetLastBlackboardValue(self.attributes.timerAddress)
        secondsUntilReset = self.attributes.timeoutSeconds
        if timerValue is None:
            self.status = status.TaskSuccessStatus
            self._StartTimer(secondsUntilReset)


class StartTimer(Task):

    def __init__(self, attributes):
        super(StartTimer, self).__init__(attributes)

    @TimedFunction('behaviors::monitors::timers::StartTimer::OnEnter')
    def OnEnter(self):
        self.status = status.TaskSuccessStatus
        timerValue = self.GetLastBlackboardValue(self.attributes.timerAddress)
        secondsUntilReset = self.attributes.timeoutSeconds
        if timerValue is None:
            channel = self.GetChannelFromAddress(self.attributes.timerAddress)
            self.context.timerManager.StartTimer(secondsUntilReset, channel)

    def CleanUp(self):
        self.status = status.TaskInvalidStatus


class StartTimerBlocks(StartTimer):

    @TimedFunction('behaviors::monitors::timers::StartTimerBlocks::OnEnter')
    def OnEnter(self):
        self.status = status.TaskFailureStatus
        timerValue = self.GetLastBlackboardValue(self.attributes.timerAddress)
        secondsUntilReset = self.attributes.timeoutSeconds
        if timerValue is None:
            self.status = status.TaskSuccessStatus
            channel = self.GetChannelFromAddress(self.attributes.timerAddress)
            self.context.timerManager.StartTimer(secondsUntilReset, channel)


class SetBooleanValueAndResetAfterTimeout(Task):

    @TimedFunction('behaviors::decorators::timers::SetBooleanValueAndResetAfterTimeout::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        channel = self.GetChannelFromAddress(self.attributes.timerAddress)
        timer_value = channel.GetLastMessageValue()
        if timer_value is None:
            self.context.timerManager.StartTimer(self.attributes.timeoutSeconds, channel)
        channel.AddObserver(self._on_time_out)

    def _on_time_out(self, name, message):
        self.SendBlackboardValue(self.attributes.channelAddress, self.attributes.trueOrFalse)
        if message.value is None and not self.IsInvalid():
            self.behaviorTree.RequestReset(requestedBy=self)
