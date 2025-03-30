#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\eventlogger.py
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task

class LogTaskEvent(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        self.context.eventLogger.log_behavior_task(self.attributes.behaviorEvent, self.context.mySlimItem.ownerID, self.behaviorTree.behaviorId, self.context.mySlimItem.typeID)


class LogGroupDestruction(Task, GroupTaskMixin):

    def OnEnter(self):
        self.SetStatusToSuccess()
        self.context.eventLogger.log_behavior_group_destroyed(self.GetGroupOwnerId(), self.behaviorTree.GetBehaviorId(), self.GetLastBlackboardValue(self.attributes.combatTargetsAddress))
