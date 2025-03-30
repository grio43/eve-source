#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\spacecomponents\linkWithShipController.py
from eve.client.script.spacecomponents.countercontroller import BaseCounterController
from spacecomponents.client.messages import MSG_ON_LINKWITHSHIP_TIMER_UPDATED
from spacecomponents.common.componentConst import LINK_WITH_SHIP
import blue
import logging
from spacecomponents.common.components.linkWithShip import LINKSTATE_RUNNING
logger = logging.getLogger(__name__)
LINK_TIMER_COLOR = (0.19, 0.7, 9.0, 1.0)

class LinkWithShipCounterController(BaseCounterController):
    __componentClass__ = LINK_WITH_SHIP
    __counterColor__ = LINK_TIMER_COLOR
    __counterLabel__ = 'UI/Inflight/SpaceComponents/LinkWithShip/TimerLabel'
    __timerFunc__ = blue.os.GetSimTime
    __countsDown__ = False

    def __init__(self, *args):
        BaseCounterController.__init__(self, *args)
        self.componentRegistry.SubscribeToItemMessage(self.itemID, MSG_ON_LINKWITHSHIP_TIMER_UPDATED, self.UpdateTimerState)

    def UpdateTimerState(self, instance, slimItem):
        if slimItem.component_linkWithShip is None:
            return
        if instance.linkState == LINKSTATE_RUNNING:
            if self.timer is None:
                self.AddTimer(instance.linkCompleteAtTime, instance.attributes.linkDuration)
        elif self.timer is not None:
            self.RemoveTimer()
