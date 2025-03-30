#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\resourcewars\client\rwinfopanelcountdowntimer.py
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelLargeBold
import gametime
from localization.formatters import FormatTimeIntervalShort
import uthread2

class CountdownTimerLabel(EveLabelLargeBold):
    CRITICAL_COLOR = (0.929, 0.11, 0.141, 1.0)
    JINGLE_TIME = 120 * gametime.SEC
    WARNING_TIME = 60 * gametime.SEC

    def ApplyAttributes(self, attributes):
        EveLabelMediumBold.ApplyAttributes(self, attributes)
        self.deadline = attributes.get('deadline', None)
        self.criticalTime = attributes.get('criticalTime', None)
        self.rwService = attributes.rwService
        self.countdownThread = None
        self.secondsRemaining = 0
        self.Start()

    def SetDeadline(self, deadline, criticalTime):
        self.deadline = deadline
        self.criticalTime = criticalTime

    def _SetCriticalColor(self, criticalTime):
        if criticalTime == self.criticalTime:
            self.SetTextColor(self.CRITICAL_COLOR)

    def _PlayJingle(self):
        sm.GetService('audio').SendUIEvent('res_wars_timer_play')

    def _PlayWarning(self):
        if self.rwService.has_a_hauler_been_filled_past_half_capacity():
            sm.GetService('audio').SendUIEvent('voc_rw_aura_everysecondcounts_aura_play')
        else:
            sm.GetService('audio').SendUIEvent('voc_rw_aura_withdrawaladvised_aura_play')

    def TickThread(self):
        if self.criticalTime is not None:
            secondsUntilCritical = gametime.GetSecondsUntilSimTime(self.criticalTime)
            if secondsUntilCritical <= 0.0:
                self._SetCriticalColor(self.criticalTime)
            else:
                uthread2.call_after_simtime_delay(self._SetCriticalColor, secondsUntilCritical, self.criticalTime)
        while self.deadline is not None and not self.destroyed:
            secondsRemaining = gametime.GetSecondsUntilSimTime(self.deadline)
            if secondsRemaining <= 0:
                self.deadline = None
                return
            timeRemaining = int(secondsRemaining * gametime.SEC + 0.5)
            if timeRemaining <= self.JINGLE_TIME and self.secondsRemaining > self.JINGLE_TIME:
                self._PlayJingle()
            if timeRemaining <= self.WARNING_TIME and self.secondsRemaining > self.WARNING_TIME:
                self._PlayWarning()
            self.secondsRemaining = timeRemaining
            deadlineText = FormatTimeIntervalShort(timeRemaining, showFrom='minute')
            self.SetText(deadlineText)
            sleep_time = secondsRemaining % 1.0
            if sleep_time < 0.01:
                sleep_time += 1.0
            uthread2.sleep_sim(sleep_time)

    def Start(self):
        if self.deadline is None:
            return
        self.countdownThread = uthread2.start_tasklet(self.TickThread)

    def Stop(self):
        self.deadline = None
        self.criticalTime = None
        if self.countdownThread is not None:
            self.countdownThread.kill()
        self.countdownThread = None

    def InitiateCountdown(self, deadline, criticalTime):
        self.Stop()
        self.deadline = deadline
        self.criticalTime = criticalTime
        self.Start()
