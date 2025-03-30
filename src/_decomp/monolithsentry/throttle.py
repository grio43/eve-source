#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithsentry\throttle.py
import math
import time
import monolithmetrics
import logging
logger = logging.getLogger(__name__)

class Throttle:

    def __init__(self, message_rate, window_seconds):
        self.message_rate = message_rate
        self.throttle_window_seconds = float(window_seconds)
        try:
            self.messages_per_second = self.message_rate / self.throttle_window_seconds
        except ZeroDivisionError:
            raise ValueError('window_seconds must be larger than 0')

        self.allowance = self.message_rate
        self.last_throttle_check = time.time()

    def throttled(self):
        current_time = time.time()
        seconds_passed = current_time - self.last_throttle_check
        self.last_throttle_check = current_time
        self.allowance += seconds_passed * self.messages_per_second
        if self.allowance > self.message_rate:
            self.allowance = self.message_rate
        if self.allowance < 1.0 and not math.isclose(self.allowance, 1.0, rel_tol=0.0, abs_tol=0.01):
            monolithmetrics.increment(metric='monolithsentry.throttled')
            logger.warn('Exception report throttled')
            return True
        self.allowance -= 1.0
        monolithmetrics.increment(metric='monolithsentry.captured')
        return False

    def __str__(self):
        return 'Throttle <message_rate=%s throttle_window_seconds=%s allowance=%s last_throttle_check=%s>' % (self.message_rate,
         self.throttle_window_seconds,
         self.allowance,
         self.last_throttle_check)
