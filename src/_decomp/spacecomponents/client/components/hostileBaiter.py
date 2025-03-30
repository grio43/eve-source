#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\hostileBaiter.py
import logging
from gametime import GetSecondsSinceWallclockTime
from spacecomponents.client.messages import MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_HOSTILE_BAITER_TIMER_UPDATED, MSG_ON_ADDED_TO_SPACE, MSG_ON_LOAD_OBJECT
from spacecomponents.common.components.component import Component
logger = logging.getLogger(__name__)
REMOTE_CALL_INITIATE_LINK = 'InitiateLink'

class HostileBaiter(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        self.completeAtTime = None
        self.pausedAtTime = None
        self.rewardGivenAtTime = None
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_LOAD_OBJECT, self.OnLoadObject)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)

    def OnAddedToSpace(self, slimItem):
        self.OnSlimItemUpdated(slimItem)

    def OnLoadObject(self, ball):
        self._UpdateModel(ball)

    def OnSlimItemUpdated(self, slimItem):
        if slimItem.component_hostileBaiter is not None:
            self.completeAtTime = slimItem.component_hostileBaiter[0]
            self.pausedAtTime = slimItem.component_hostileBaiter[1]
            self.rewardGivenAtTime = slimItem.component_hostileBaiter[2]
            self.SendMessage(MSG_ON_HOSTILE_BAITER_TIMER_UPDATED, self, slimItem)
        ball = sm.GetService('michelle').GetBall(self.itemID)
        if ball is not None:
            self._UpdateModel(ball)

    def _UpdateModel(self, ball):
        try:
            model = ball.GetModel()
        except AttributeError:
            return

        if model is not None:
            remainingDuration = self._GetRemainingDuration()
            totalDuration = self.attributes.rewardWaitDuration
            model.SetControllerVariable('HostileBaiter_Active', float(self.completeAtTime is not None))
            model.SetControllerVariable('HostileBaiter_Paused', float(self.pausedAtTime is not None))
            model.SetControllerVariable('HostileBaiter_Completed', float(self.rewardGivenAtTime is not None))
            model.SetControllerVariable('HostileBaiter_RemainingDuration', float(remainingDuration))
            model.SetControllerVariable('HostileBaiter_TotalDuration', float(totalDuration))

    def _GetRemainingDuration(self):
        if self.completeAtTime is not None:
            remainingDuration = -GetSecondsSinceWallclockTime(self.completeAtTime)
        else:
            remainingDuration = self.attributes.rewardWaitDuration
        return remainingDuration
