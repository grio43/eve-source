#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\test\test_timer.py
from datetime import datetime
from eve.client.script.ui.control.timer import CountdownTimer
from gametime import SEC
from mock import Mock
from testsuites.testcases import ClientTestCase

class TestTimer(ClientTestCase):

    def test_calculate_seconds_left_can_show_more_than_1_day(self):
        time_now = datetime(day=22, month=11, year=2024, hour=15, minute=45, second=0)
        time_to_countdown_to = datetime(day=23, month=11, year=2024, hour=17, minute=0, second=0)
        timer = CountdownTimer(fetch_timestamp_to_countdown_to=lambda : time_to_countdown_to)
        timer._get_now = lambda : time_now
        actual_seconds_left = timer._calculate_seconds_left()
        expected_seconds_left = (86400 + 3600 + 900) * SEC
        self.assertEqual(actual_seconds_left, expected_seconds_left)

    def test_calculate_seconds_left_can_show_between_1_hour_and_1_day(self):
        time_now = datetime(day=22, month=11, year=2024, hour=15, minute=45, second=0)
        time_to_countdown_to = datetime(day=22, month=11, year=2024, hour=17, minute=0, second=0)
        timer = CountdownTimer(fetch_timestamp_to_countdown_to=lambda : time_to_countdown_to)
        timer._get_now = lambda : time_now
        actual_seconds_left = timer._calculate_seconds_left()
        expected_seconds_left = (3600 + 900) * SEC
        self.assertEqual(actual_seconds_left, expected_seconds_left)

    def test_calculate_seconds_left_can_show_between_1_minute_and_1_hour(self):
        time_now = datetime(day=22, month=11, year=2024, hour=15, minute=45, second=0)
        time_to_countdown_to = datetime(day=22, month=11, year=2024, hour=16, minute=0, second=0)
        timer = CountdownTimer(fetch_timestamp_to_countdown_to=lambda : time_to_countdown_to)
        timer._get_now = lambda : time_now
        actual_seconds_left = timer._calculate_seconds_left()
        expected_seconds_left = 900 * SEC
        self.assertEqual(actual_seconds_left, expected_seconds_left)

    def test_calculate_seconds_left_can_show_between_1_second_and_1_minute(self):
        time_now = datetime(day=22, month=11, year=2024, hour=15, minute=45, second=0)
        time_to_countdown_to = datetime(day=22, month=11, year=2024, hour=15, minute=45, second=10)
        timer = CountdownTimer(fetch_timestamp_to_countdown_to=lambda : time_to_countdown_to)
        timer._get_now = lambda : time_now
        actual_seconds_left = timer._calculate_seconds_left()
        expected_seconds_left = 10 * SEC
        self.assertEqual(actual_seconds_left, expected_seconds_left)

    def test_calculate_seconds_left_supports_negatives(self):
        time_now = datetime(day=22, month=11, year=2024, hour=15, minute=45, second=0)
        time_to_countdown_to = datetime(day=22, month=11, year=2024, hour=15, minute=44, second=0)
        timer = CountdownTimer(fetch_timestamp_to_countdown_to=lambda : time_to_countdown_to)
        timer._get_now = lambda : time_now
        actual_seconds_left = timer._calculate_seconds_left()
        expected_seconds_left = -60 * SEC
        self.assertEqual(actual_seconds_left, expected_seconds_left)

    def test_timer_updates_stop_timer_if_fetching_returns_none(self):
        time_now = datetime(day=22, month=11, year=2024, hour=15, minute=45, second=0)
        time_to_countdown_to = None
        timer = CountdownTimer(fetch_timestamp_to_countdown_to=lambda : time_to_countdown_to)
        timer._get_now = lambda : time_now
        timer.stop_timer = Mock(wraps=timer.stop_timer)
        timer._update()
        timer.stop_timer.assert_called_once_with()

    def test_timer_updates_stop_timer_if_fetching_returns_negative_over_one_year(self):
        time_now = datetime(day=22, month=11, year=2024, hour=15, minute=45, second=0)
        time_to_countdown_to = datetime(day=22, month=11, year=2022, hour=15, minute=45, second=0)
        timer = CountdownTimer(fetch_timestamp_to_countdown_to=lambda : time_to_countdown_to)
        timer._get_now = lambda : time_now
        timer.stop_timer = Mock(wraps=timer.stop_timer)
        timer._update()
        timer.stop_timer.assert_called_once_with()

    def test_timer_stops_timer_if_fetching_returns_negative_between_two_minutes_and_one_year(self):
        time_now = datetime(day=22, month=11, year=2024, hour=15, minute=45, second=0)
        time_to_countdown_to = datetime(day=22, month=10, year=2024, hour=15, minute=45, second=0)
        timer = CountdownTimer(fetch_timestamp_to_countdown_to=lambda : time_to_countdown_to)
        timer._get_now = lambda : time_now
        timer.stop_timer = Mock(wraps=timer.stop_timer)
        timer._update()
        timer.stop_timer.assert_called_once_with()

    def test_timer_does_not_stop_timer_if_fetching_returns_negative_under_two_minutes(self):
        time_now = datetime(day=22, month=11, year=2024, hour=15, minute=44, second=0)
        time_to_countdown_to = datetime(day=22, month=11, year=2024, hour=15, minute=45, second=0)
        timer = CountdownTimer(fetch_timestamp_to_countdown_to=lambda : time_to_countdown_to)
        timer._get_now = lambda : time_now
        timer.stop_timer = Mock(wraps=timer.stop_timer)
        timer._update()
        self.assertFalse(timer.stop_timer.called)

    def test_timer_interval_is_increased_if_fetching_returns_negative_under_two_minutes(self):
        time_now = datetime(day=22, month=11, year=2024, hour=15, minute=45, second=0)
        time_to_countdown_to = datetime(day=22, month=11, year=2024, hour=15, minute=44, second=0)
        timer = CountdownTimer(fetch_timestamp_to_countdown_to=lambda : time_to_countdown_to)
        timer._get_now = lambda : time_now
        timer._increase_timer_interval = Mock(wraps=timer._increase_timer_interval)
        timer.stop_timer = Mock(wraps=timer.stop_timer)
        timer._update()
        timer._increase_timer_interval.assert_called_once_with()
        self.assertFalse(timer.stop_timer.called)

    def test_fetching_attempts_do_not_exceed_maximum_when_fetching_returns_negative_under_two_minutes(self):
        time_now = datetime(day=22, month=11, year=2024, hour=15, minute=45, second=0)
        time_to_countdown_to = datetime(day=22, month=11, year=2024, hour=15, minute=44, second=0)
        fetch_timestamp_to_countdown_to = Mock(return_value=time_to_countdown_to)
        timer = CountdownTimer(fetch_timestamp_to_countdown_to=fetch_timestamp_to_countdown_to, msecs_between_updates=1, max_fetching_attempts=5)
        timer._get_now = lambda : time_now
        timer._reset_timestamp_to_countdown_to = Mock(wraps=timer._reset_timestamp_to_countdown_to)
        timer._increase_timer_interval = Mock(wraps=timer._increase_timer_interval)
        self.is_timer_running = True

        def stop_timer(*args, **kwargs):
            self.is_timer_running = False

        timer.stop_timer = stop_timer
        while self.is_timer_running:
            timer._update()

        self.assertEqual(fetch_timestamp_to_countdown_to.call_count, 5)
        self.assertEqual(timer._increase_timer_interval.call_count, 5)
        self.assertEqual(timer._increase_timer_interval.call_count, 5)

    def test_fetching_attempts_only_fetch_once_when_fetching_returns_positive(self):
        time_now = datetime(day=22, month=11, year=2024, hour=15, minute=45, second=0)
        time_to_countdown_to = datetime(day=22, month=11, year=2024, hour=15, minute=46, second=0)
        fetch_timestamp_to_countdown_to = Mock(return_value=time_to_countdown_to)
        timer = CountdownTimer(fetch_timestamp_to_countdown_to=fetch_timestamp_to_countdown_to, msecs_between_updates=1, max_fetching_attempts=5)
        timer._get_now = lambda : time_now
        timer._reset_timestamp_to_countdown_to = Mock(wraps=timer._reset_timestamp_to_countdown_to)
        timer._increase_timer_interval = Mock(wraps=timer._increase_timer_interval)
        timer._update()
        timer._update()
        self.assertEqual(fetch_timestamp_to_countdown_to.call_count, 1)
        self.assertEqual(timer._reset_timestamp_to_countdown_to.call_count, 0)
        self.assertEqual(timer._increase_timer_interval.call_count, 0)

    def test_fetching_attempts_only_fetch_once_when_fetching_returns_negative_over_two_minutes(self):
        time_now = datetime(day=22, month=11, year=2024, hour=15, minute=48, second=0)
        time_to_countdown_to = datetime(day=22, month=11, year=2024, hour=15, minute=45, second=0)
        fetch_timestamp_to_countdown_to = Mock(return_value=time_to_countdown_to)
        timer = CountdownTimer(fetch_timestamp_to_countdown_to=fetch_timestamp_to_countdown_to, msecs_between_updates=1, max_fetching_attempts=5)
        timer._get_now = lambda : time_now
        timer._reset_timestamp_to_countdown_to = Mock(wraps=timer._reset_timestamp_to_countdown_to)
        timer._increase_timer_interval = Mock(wraps=timer._increase_timer_interval)
        self.is_timer_running = True

        def stop_timer(*args, **kwargs):
            self.is_timer_running = False

        timer.stop_timer = stop_timer
        while self.is_timer_running:
            timer._update()

        self.assertEqual(fetch_timestamp_to_countdown_to.call_count, 1)
        self.assertEqual(timer._reset_timestamp_to_countdown_to.call_count, 0)
        self.assertEqual(timer._increase_timer_interval.call_count, 0)
