#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\spacecomponents\jumppolarizationcontroller.py
from eve.client.script.spacecomponents.countercontroller import BaseCounterController
from spacecomponents.client.messages import MSG_ON_JUMP_POLARIZATION_UPDATED
from spacecomponents.common.componentConst import JUMP_POLARIZATION_CLASS
import blue
POLARIZED_TIMER_COLOR = (1.0, 0.5, 0.0, 1.0)

class JumpPolarizationCounterController(BaseCounterController):
    __componentClass__ = JUMP_POLARIZATION_CLASS
    __counterColor__ = POLARIZED_TIMER_COLOR
    __counterLabel__ = 'UI/Inflight/SpaceComponents/JumpPolarization/Polarized'
    __timerFunc__ = blue.os.GetSimTime
    __countsDown__ = True
    __soundFinishedEvent__ = 'bounty_open_play'

    def __init__(self, *args):
        BaseCounterController.__init__(self, *args)
        self.componentRegistry.SubscribeToItemMessage(self.itemID, MSG_ON_JUMP_POLARIZATION_UPDATED, self.UpdateTimerState)

    def UpdateTimerState(self, instance, slimItem):
        if instance.isPolarized:
            if self.timer is None:
                self.AddTimer(instance.polarizationEndTime, instance.polarizationDuration)
            else:
                self.timer.SetExpiryTime(instance.polarizationEndTime, long(instance.polarizationDuration * const.SEC))
        else:
            self.RemoveTimer()
