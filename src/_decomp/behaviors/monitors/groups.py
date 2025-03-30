#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\groups.py
from ballpark.entities.entitygroup import MESSAGE_ON_ENTITY_GROUP_MEMBERSHIP_CHANGED
from behaviors.groups.mixin import GroupTaskMixin, EntityGroupNotFound
from behaviors.tasks import Task
import logging
logger = logging.getLogger(__name__)

class GroupMembershipMonitor(Task, GroupTaskMixin):

    def OnEnter(self):
        self.SubscribeMembershipChanges()
        self.SetStatusToSuccess()

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeMembershipChanges()
            self.SetStatusToInvalid()

    def OnMembershipChanged(self, _):
        if self.IsInvalid():
            return
        self.behaviorTree.RequestReset(requestedBy=self)

    def SubscribeMembershipChanges(self):
        messenger = self.GetGroupMessenger()
        messenger.SubscribeToMessage(MESSAGE_ON_ENTITY_GROUP_MEMBERSHIP_CHANGED, self.OnMembershipChanged)

    def UnsubscribeMembershipChanges(self):
        try:
            messenger = self.GetGroupMessenger()
            messenger.UnsubscribeFromMessage(MESSAGE_ON_ENTITY_GROUP_MEMBERSHIP_CHANGED, self.OnMembershipChanged)
        except EntityGroupNotFound:
            logger.debug('The entity group can not be found')
