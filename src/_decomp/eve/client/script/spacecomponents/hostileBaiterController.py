#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\spacecomponents\hostileBaiterController.py
from eve.client.script.spacecomponents.countercontroller import BaseCounterController
from spacecomponents.client.messages import MSG_ON_HOSTILE_BAITER_TIMER_UPDATED
from spacecomponents.common.componentConst import HOSTILE_BAITER
import blue
import logging
logger = logging.getLogger(__name__)
ACTIVE_TIMER_COLOR = (1.0, 0.27, 0.29, 1.0)
PAUSED_TIMER_COLOR = (1.0, 1.0, 0.27, 1.0)
LABEL_UNLOCKING = 'UI/Inflight/SpaceComponents/ProximityLock/Unlocking'
LABEL_CONTESTED = 'UI/Inflight/SpaceComponents/ProximityLock/Contested'

class HostileBaiterCounterController(BaseCounterController):
    __componentClass__ = HOSTILE_BAITER
    __counterColor__ = ACTIVE_TIMER_COLOR
    __pausedColor__ = PAUSED_TIMER_COLOR
    __counterLabel__ = 'UI/Inflight/SpaceComponents/HostileBaiter/TimerLabel'
    __counterLabelPaused__ = 'UI/Inflight/SpaceComponents/HostileBaiter/TimerLabelBlocked'
    __timerFunc__ = blue.os.GetSimTime
    __countsDown__ = False

    def __init__(self, *args):
        BaseCounterController.__init__(self, *args)
        self.componentRegistry.SubscribeToItemMessage(self.itemID, MSG_ON_HOSTILE_BAITER_TIMER_UPDATED, self.UpdateTimerState)

    def UpdateTimerState(self, instance, slimItem):
        if slimItem.component_hostileBaiter is None:
            return
        if instance.completeAtTime is None:
            if self.timer is not None:
                self.RemoveTimer()
        elif self.timer is None:
            self.AddTimer(instance.completeAtTime, instance.attributes.rewardWaitDuration, instance.pausedAtTime)
        else:
            self.ChangeTimer(instance.completeAtTime, instance.attributes.rewardWaitDuration, instance.pausedAtTime)
