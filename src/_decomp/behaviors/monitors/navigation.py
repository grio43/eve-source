#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\navigation.py
from ballpark.const import DESTINY_MODE_WARP
from ballpark.messenger.const import MESSAGE_ON_BALL_MODE_CHANGED
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task

class GroupMemberWarpModeChangedMonitor(Task, GroupTaskMixin):

    def __init__(self, attributes = None):
        super(GroupMemberWarpModeChangedMonitor, self).__init__(attributes)
        self.trackedItemIds = None

    def OnEnter(self):
        self.SetStatusToSuccess()
        self.trackedItemIds = self.GetItemsToTrack()
        for itemId in self.trackedItemIds:
            self.SubscribeItem(itemId, MESSAGE_ON_BALL_MODE_CHANGED, self.OnItemBallModeChanged)

    def CleanUp(self):
        if self.IsInvalid():
            return
        for itemId in self.trackedItemIds:
            self.UnsubscribeItem(itemId, MESSAGE_ON_BALL_MODE_CHANGED, self.OnItemBallModeChanged)

        self.SetStatusToInvalid()

    def GetItemsToTrack(self):
        return self.GetMemberIdList()

    def OnItemBallModeChanged(self, oldMode, newMode):
        if self.IsInvalid():
            return
        if DESTINY_MODE_WARP in (oldMode, newMode):
            self.behaviorTree.RequestReset(requestedBy=self)
