#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\test\test_retry.py
from eve.common.script.util.retry import retry_with_exponential_backoff
from mock import Mock
from stackless_response_router.exceptions import TimeoutException
from testsuites.testcases import ServerClientTestCase

class TestRetry(ServerClientTestCase):

    def test_with_the_default_one_attempt_tries_once(self):
        self._test_retry(retries_needed=1, max_attempts=1, expected_calls=1)

    def test_with_the_default_one_attempt_tries_once_even_if_it_times_out(self):
        self._test_retry(retries_needed=1, max_attempts=1, expected_calls=1, should_raise_exception_class=TimeoutException)

    def test_with_the_default_one_attempt_tries_once_even_if_it_should_retry(self):
        self._test_retry(retries_needed=1, max_attempts=1, expected_calls=1, force_retry=True)

    def test_with_multiple_attempts_tries_once_if_enough(self):
        self._test_retry(retries_needed=1, max_attempts=10, expected_calls=1)

    def test_with_multiple_timeout_attempts_tries_twice_if_needed(self):
        self._test_retry(retries_needed=2, max_attempts=10, expected_calls=2)

    def test_with_multiple_timeout_attempts_tries_max_times_if_needed(self):
        self._test_retry(retries_needed=10, max_attempts=10, expected_calls=10)

    def test_with_multiple_timeout_attempts_times_out_if_more_than_max_attempts_needed(self):
        self._test_retry(retries_needed=11, max_attempts=10, expected_calls=10, should_timeout=True)

    def test_with_multiple_attempts_and_special_should_retry_tries_max_times_if_needed(self):
        self._test_retry(retries_needed=10, max_attempts=10, expected_calls=10, force_retry=True)

    def test_with_multiple_attempts_and_special_should_retry_stops_trying_if_more_than_max_attempts_needed(self):
        self._test_retry(retries_needed=11, max_attempts=10, expected_calls=10, force_retry=True)

    def test_with_the_default_one_attempt_propagates_exceptions_other_than_timeout(self):
        self._test_retry(retries_needed=1, max_attempts=1, expected_calls=1, should_raise_exception_class=Exception)

    def test_with_multiple_attempts_propagates_exceptions_other_than_timeout_right_away(self):
        self._test_retry(retries_needed=1, max_attempts=10, expected_calls=1, should_raise_exception_class=Exception)

    def _test_retry(self, retries_needed, max_attempts, expected_calls, force_retry = False, should_timeout = False, should_raise_exception_class = None):
        retries_tracker = RetriesTracker(retries_needed, should_raise_exception_class, force_retry)
        if should_timeout:
            expected_exception = TimeoutException
        else:
            expected_exception = should_raise_exception_class
        if expected_exception:
            with self.assertRaises(expected_exception):
                retry_with_exponential_backoff(func=retries_tracker.do, max_attempts=max_attempts, retry_delay_in_seconds=1, jitter=True, waiter=Mock(), should_retry=lambda result: force_retry or isinstance(result, TimeoutException))
        else:
            retry_with_exponential_backoff(func=retries_tracker.do, max_attempts=max_attempts, retry_delay_in_seconds=1, jitter=True, waiter=Mock(), should_retry=lambda result: force_retry or isinstance(result, TimeoutException))
        print 'retries_tracker.number_of_calls', retries_tracker.number_of_calls, 'expected', expected_calls
        self.assertEqual(retries_tracker.number_of_calls, expected_calls)


class RetriesTracker(object):

    def __init__(self, retries_needed, should_raise_exception_class, force_retry):
        self.retries_needed = retries_needed
        self.should_raise_exception_class = should_raise_exception_class
        self.force_retry = force_retry
        self.number_of_calls = 0

    def do(self):
        self.number_of_calls += 1
        if self.should_raise_exception_class:
            raise self.should_raise_exception_class('RetriesTracker encountered an existential crisis')
        if self.number_of_calls < self.retries_needed:
            if self.force_retry:
                return Mock()
            raise TimeoutException('RetriesTracker went on vacation, try again later')
        else:
            return Mock()
