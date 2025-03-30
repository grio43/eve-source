#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\publicGateway\grpc\backoff.py
import time
import functools
import logging
from publicGateway.grpc.exceptions import BackedOffException
logger = logging.getLogger(__name__)
MAX_BACK_OFF_WINDOW = 300.0

def backoff_if_error(initial_timeout_duration = 0.1, timeout_scale_factor = 2.0, whitelist_errors = None):
    if whitelist_errors is None:
        whitelist_errors = []

    def _decorator(func):

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            if _wrapper.backed_off_until_time and time.time() < _wrapper.backed_off_until_time:
                raise BackedOffException('Backed off due to too many errors - please wait %s s' % (_wrapper.backed_off_until_time - time.time()))
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                if type(e) in whitelist_errors:
                    raise
                if _wrapper.timeout_duration:
                    _wrapper.timeout_duration = min(MAX_BACK_OFF_WINDOW, _wrapper.timeout_duration * timeout_scale_factor)
                else:
                    _wrapper.timeout_duration = initial_timeout_duration
                _wrapper.backed_off_until_time = time.time() + _wrapper.timeout_duration
                raise

            _clear_backoff()
            return result

        def _clear_backoff():
            _wrapper.backed_off_until_time = None
            _wrapper.timeout_duration = None

        _clear_backoff()
        _wrapper.clear_backoff = _clear_backoff
        return _wrapper

    return _decorator
