#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodditests\common\tracker.py
from typeutils import metas
import uthread2
DEFAULT_TEST_TIMEOUT_SECS = 60.0

class TestState(object):
    RUNNING = 0
    SUCCEEDED = 1
    FAILED = 2


class TestTracker(object):
    __metaclass__ = metas.Singleton

    def __init__(self):
        self.active_tests = {}
        self.timeout_failer = TimeoutTestFailer(fail_test=self.fail_test)

    def start_test(self, test_id, timeout = DEFAULT_TEST_TIMEOUT_SECS):
        self.active_tests[test_id] = TestState.RUNNING
        self.timeout_failer.add_timeout(test_id, timeout)
        sm.ScatterEvent('OnTestStarted', test_id)

    def _stop_test(self, test_id, result):
        self.active_tests[test_id] = result
        self.timeout_failer.remove_timeout(test_id)

    def fail_test(self, test_id, reason = ''):
        self._stop_test(test_id, result=TestState.FAILED)
        sm.ScatterEvent('OnTestFailed', test_id, reason)

    def pass_test(self, test_id):
        self._stop_test(test_id, result=TestState.SUCCEEDED)
        sm.ScatterEvent('OnTestSucceeded', test_id)

    def log_test_metadata(self, test_id, key, value):
        sm.ScatterEvent('OnTestMetaDataLogged', test_id, key, value)


class TimeoutTestFailer(object):

    def __init__(self, fail_test):
        self._fail_test = fail_test
        self.timeout_threads = {}

    def add_timeout(self, test_id, timeout):
        self.remove_timeout(test_id)
        self.timeout_threads[test_id] = uthread2.call_after_wallclocktime_delay(tasklet_func=self.timeout, delay=timeout if timeout > 0 else DEFAULT_TEST_TIMEOUT_SECS, test_id=test_id)

    def remove_timeout(self, test_id):
        if test_id in self.timeout_threads:
            self.timeout_threads[test_id].kill()
            del self.timeout_threads[test_id]

    def timeout(self, test_id):
        self._fail_test(test_id)
        if test_id in self.timeout_threads:
            del self.timeout_threads[test_id]
