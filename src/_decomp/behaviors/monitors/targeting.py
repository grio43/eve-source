#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\targeting.py
import logging
from ballpark.messenger.const import MESSAGE_TARGET_LOST
from behaviors.tasks import Task
from ccpProfile import TimedFunction
logger = logging.getLogger(__name__)

class TargetLostMonitor(Task):

    @TimedFunction('behaviors::monitors::targeting::TargetLostMonitor::OnEnter')
    def OnEnter(self):
        self.SetTarget(self.GetLastBlackboardValue(self.attributes.targetAddress))
        if self.targetId:
            self.SubscribeItem(self.context.myItemId, MESSAGE_TARGET_LOST, self.OnTargetLost)
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeItem(self.context.myItemId, MESSAGE_TARGET_LOST, self.OnTargetLost)
            self.SetStatusToInvalid()

    @TimedFunction('behaviors::monitors::targeting::TargetLostMonitor::OnTargetLost')
    def OnTargetLost(self, targetId, reason):
        if self.IsInvalid():
            return
        if self.targetId == targetId:
            logger.debug('%s: OnTargetLost target=%s reason=%s requesting reset', self.context.myItemId, targetId, reason)
            self.behaviorTree.RequestReset(requestedBy=self)

    def SetTarget(self, targetId):
        self.targetId = targetId
