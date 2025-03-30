#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\timer.py
from carbon.common.script.util.timerstuff import AutoTimer
from datetime import datetime
from gametime import DAY, HOUR, MIN, SEC
from localization.formatters.timeIntervalFormatters import FormatTimeIntervalShortWritten
from logging import getLogger
from signals import Signal
logger = getLogger('CountdownTimer')

def get_time_left_text(seconds_left):
    if seconds_left > DAY:
        show_from = 'day'
        show_to = 'hour'
    elif seconds_left > HOUR:
        show_from = 'hour'
        show_to = 'minute'
    elif seconds_left > 10 * MIN:
        show_from = 'minute'
        show_to = 'minute'
    elif seconds_left > MIN:
        show_from = 'minute'
        show_to = 'second'
    else:
        show_from = 'second'
        show_to = 'second'
    return FormatTimeIntervalShortWritten(seconds_left, showFrom=show_from, showTo=show_to)


class CountdownTimer(object):
    DEFAULT_MSECS_BETWEEN_UPDATES = 250
    DEFAULT_MAX_FETCHING_ATTEMPTS = 1

    def __init__(self, fetch_timestamp_to_countdown_to, msecs_between_updates = DEFAULT_MSECS_BETWEEN_UPDATES, max_fetching_attempts = DEFAULT_MAX_FETCHING_ATTEMPTS):
        self._fetch_timestamp_to_countdown_to = fetch_timestamp_to_countdown_to
        self._msecs_between_updates = msecs_between_updates
        self._max_fetching_attempts = max_fetching_attempts
        self._timestamp_to_countdown_to = None
        self._text = None
        self._update_timer = None
        self._fetching_attempts = 0
        self.on_updated = Signal('CountdownTimer::on_updated')

    def start_timer(self):
        self.stop_timer()
        self._update()
        self._update_timer = AutoTimer(interval=self._msecs_between_updates, method=self._update)

    def stop_timer(self):
        if self._update_timer:
            self._update_timer.KillTimer()
            self._update_timer = None
        self._update_text(text='')

    @property
    def timestamp_to_countdown_to(self):
        if self._timestamp_to_countdown_to is None and self._fetching_attempts < self._max_fetching_attempts:
            self._fetching_attempts += 1
            self._timestamp_to_countdown_to = self._fetch_timestamp_to_countdown_to()
            logger.info('Fetched timestamp to countdown to: %s', self._timestamp_to_countdown_to)
        return self._timestamp_to_countdown_to

    def _reset_timestamp_to_countdown_to(self):
        self._timestamp_to_countdown_to = None

    def _calculate_seconds_left(self):
        now = self._get_now()
        seconds_left = int((self.timestamp_to_countdown_to - now).total_seconds())
        return seconds_left * SEC

    def _get_now(self):
        return datetime.utcnow()

    def _handle_negative_countdowns(self, seconds_left):
        seconds_left = abs(seconds_left)
        if seconds_left <= 2 * MIN:
            logger.info('Attempted to update CountdownTimer with a negative time under 2 minutes (%s: %s), keep trying', seconds_left, get_time_left_text(seconds_left))
            self._reset_timestamp_to_countdown_to()
            self._increase_timer_interval()
        else:
            logger.info('Attempted to update CountdownTimer with a negative time above 2 minutes (%s: %s), stop timer', seconds_left, get_time_left_text(seconds_left))
            self.stop_timer()
            if seconds_left > 365 * DAY:
                logger.error('CountdownTimer received negative time above 1 year (%s: %s)', seconds_left, get_time_left_text(seconds_left))

    def _update(self):
        try:
            seconds_left = self._calculate_seconds_left()
        except TypeError as exc:
            logger.info('Failed to calculate seconds left in CountdownTimer: %s', exc)
            self.stop_timer()
            return

        if seconds_left <= 0:
            self._handle_negative_countdowns(seconds_left)
            return
        text = get_time_left_text(seconds_left)
        self._update_text(text)
        self._reset_timer_interval_if_needed()

    def _increase_timer_interval(self):
        if not self._update_timer:
            return
        msecs_between_updates = self._msecs_between_updates * max(1, self._fetching_attempts) * 5
        self._update_timer.Reset(msecs_between_updates)

    def _reset_timer_interval_if_needed(self):
        self._fetching_attempts = 0
        if not self._update_timer:
            return
        if self._update_timer.interval == self._msecs_between_updates:
            return
        self._update_timer.Reset(self._msecs_between_updates)

    def _update_text(self, text):
        if text != self._text:
            self.on_updated(text)
            self._text = text
