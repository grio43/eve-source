#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\spacecomponents\proximitylockcontroller.py
import blue
import localization
from carbon.common.lib.const import SEC
from eve.client.script.spacecomponents.countercontroller import BaseCounterController
from spacecomponents.client.messages import MSG_ON_PROXIMITY_LOCK_TIMER_UPDATED
from spacecomponents.common.componentConst import PROXIMITY_LOCK_CLASS
COLOR_TIMER = (0.6, 0.1, 0.0, 1.0)
LABEL_UNLOCKING = 'UI/Inflight/SpaceComponents/ProximityLock/Unlocking'
LABEL_CONTESTED = 'UI/Inflight/SpaceComponents/ProximityLock/Contested'
SOUND_END = 'counter_proximity_lock_end_play'
SOUND_PAUSED = 'counter_proximity_lock_paused_play'
SOUND_RESUMED = 'counter_proximity_lock_resumed_play'
SOUND_START = 'counter_proximity_lock_start_play'

class ProximityLockCounterController(BaseCounterController):
    __componentClass__ = PROXIMITY_LOCK_CLASS
    __counterColor__ = COLOR_TIMER
    __counterLabel__ = LABEL_UNLOCKING
    __timerFunc__ = blue.os.GetSimTime
    __countsDown__ = True
    __soundFinishedEvent__ = SOUND_END

    def __init__(self, *args):
        super(ProximityLockCounterController, self).__init__(*args)
        self._unlocks_at = None
        self.paused_at = None
        self.duration = None
        self.subscribe(MSG_ON_PROXIMITY_LOCK_TIMER_UPDATED, self.UpdateTimerState)

    @property
    def unlocks_at(self):
        if self.is_paused:
            time_remaining = self._unlocks_at - self.paused_at
            return self.get_current_time() + time_remaining
        else:
            return self._unlocks_at

    @unlocks_at.setter
    def unlocks_at(self, unlocks_at):
        self._unlocks_at = unlocks_at

    @property
    def is_paused(self):
        return self.paused_at is not None

    def on_finished(self):
        self.RemoveTimer()

    def on_paused(self):
        if self.timer is None:
            self.AddTimer(self.unlocks_at, self.duration / SEC)
        self.timer.SetExpiryTime(self.unlocks_at, self.duration, timerPaused=self.paused_at)
        PlaySound(SOUND_PAUSED)

    def on_resumed(self):
        if self.timer is None:
            self.AddTimer(self.unlocks_at, self.duration / SEC)
        else:
            self.timer.SetExpiryTime(self.unlocks_at, self.duration)
        PlaySound(SOUND_RESUMED)

    def on_started(self):
        if not self.timer:
            self.AddTimer(self.unlocks_at, self.duration / SEC)
        PlaySound(SOUND_START)

    def get_current_time(self):
        return self.__timerFunc__()

    def subscribe(self, message_type, callback):
        self.componentRegistry.SubscribeToItemMessage(self.itemID, message_type, callback)

    @property
    def endTime(self):
        endTime = self.unlocks_at
        if endTime is None:
            endTime = 0
        return endTime

    @endTime.setter
    def endTime(self, endTime):
        self.unlocks_at = endTime

    def UpdateTimerState(self, instance, _):
        if instance.time_remaining is None:
            return
        self.duration = instance.duration
        self.paused_at = instance.paused_at
        self.unlocks_at = self.get_current_time() + instance.time_remaining
        if self.is_paused:
            self.on_paused()
        elif instance.time_remaining == instance.attributes.durationSeconds * SEC:
            self.on_started()
        elif not self.is_paused:
            self.on_resumed()
        else:
            self.on_finished()

    def GetCounterLabel(self):
        if self.is_paused:
            return localization.GetByLabel(LABEL_CONTESTED)
        else:
            return super(ProximityLockCounterController, self).GetCounterLabel()


def PlaySound(sound_event):
    sm.GetService('audio').SendUIEvent(sound_event)
