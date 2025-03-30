#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\blackboards.py
from behaviors.tasks import Task
from ccpProfile import TimedFunction

class BlackboardMessageMonitor(Task):

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeToBlackboard(self.attributes.messageAddress, self.OnBlackboardUpdate)
            self.SetStatusToInvalid()

    @TimedFunction('behaviors::monitors::blackboards::BlackboardMessageMonitor::OnBlackboardUpdate')
    def OnBlackboardUpdate(self, name, message):
        if not self.IsInvalid():
            self.behaviorTree.RequestReset(requestedBy=self)

    @TimedFunction('behaviors::monitors::blackboards::BlackboardMessageMonitor::OnEnter')
    def OnEnter(self):
        self.SubscribeToBlackboard(self.attributes.messageAddress, self.OnBlackboardUpdate)
        self.SetStatusToSuccess()


class BlackboardMessageMonitorBlocking(BlackboardMessageMonitor):

    @TimedFunction('behaviors::monitors::blackboards::BlackboardMessageMonitorBlocking::OnEnter')
    def OnEnter(self):
        self.SubscribeToBlackboard(self.attributes.messageAddress, self.OnBlackboardUpdate)
        message = self.GetLastBlackboardValue(self.attributes.messageAddress)
        if message is not None:
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()


class BlackboardFlagOnMessageUpdate(Task):

    def OnEnter(self):
        self.SubscribeToBlackboard(self.attributes.messageAddress, self.OnBlackboardUpdate)
        self.SetStatusToSuccess()

    def CleanUp(self):
        if self.IsInvalid():
            return
        self.UnsubscribeToBlackboard(self.attributes.messageAddress, self.OnBlackboardUpdate)
        self.SetStatusToInvalid()

    def OnBlackboardUpdate(self, name, message):
        if self.IsInvalid():
            return
        self.SendBlackboardValue(self.attributes.flagAddress, True)
