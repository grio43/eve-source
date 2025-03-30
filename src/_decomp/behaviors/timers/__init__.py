#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\timers\__init__.py
import uthread2

class Timer(object):

    def __init__(self, manager, timerID, time, channel):
        self._manager = manager
        self._id = timerID
        self._time = time
        self._channel = channel
        self._channel.SendMessage(self._id)
        self._timerThread = uthread2.StartTasklet(self._OnTimeout)

    def _OnTimeout(self):
        uthread2.SleepSim(self._time)
        self.ClearTimer()

    def ClearTimer(self):
        self._channel.SendMessage(None)
        self._manager.RemoveTimer(self._id)

    def Stop(self):
        self._timerThread.kill()


class TimerManager(object):

    def __init__(self):
        self._activeTimers = {}
        self._nextTimerID = 1

    def StartTimer(self, time, channel):
        self._activeTimers[self._nextTimerID] = Timer(self, self._nextTimerID, time, channel)
        self._nextTimerID += 1

    def RemoveTimer(self, timerID):
        if timerID in self._activeTimers:
            del self._activeTimers[timerID]

    def ClearTimer(self, timerID):
        timer = self._activeTimers.get(timerID)
        if timer is not None:
            timer.Stop()
            timer.ClearTimer()
