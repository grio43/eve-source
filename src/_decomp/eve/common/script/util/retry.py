#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\retry.py
from logging import getLogger
from random import uniform
from stackless_response_router.exceptions import TimeoutException
from uthread2 import Sleep
logger = getLogger('retry_with_backoff')

def retry_with_exponential_backoff(func, max_attempts = 1, retry_delay_in_seconds = 1, jitter = True, waiter = Sleep, should_retry = lambda exc: isinstance(exc, TimeoutException), *args, **kwargs):
    for attempt in range(1, max_attempts + 1):
        try:
            result = func(*args, **kwargs)
            if should_retry(result):
                if attempt < max_attempts:
                    logger.info('Retry condition met for the result, retrying in %s seconds (attempt %s/%s)', retry_delay_in_seconds, attempt, max_attempts)
                    waiter(retry_delay_in_seconds)
                    retry_delay_in_seconds *= 2
                    if jitter:
                        retry_delay_in_seconds += uniform(0, 1)
                    continue
                else:
                    logger.info('Retry condition met, max attempts reached (%s)', max_attempts)
            return result
        except Exception as exc:
            if should_retry(exc):
                if attempt < max_attempts:
                    logger.info('Retry condition met for exception %s, retrying in %s seconds (attempt %s/%s)', exc.__class__.__name__, retry_delay_in_seconds, attempt, max_attempts)
                    waiter(retry_delay_in_seconds)
                    retry_delay_in_seconds *= 2
                    if jitter:
                        retry_delay_in_seconds += uniform(0, 1)
                    continue
                else:
                    logger.info('Retry condition met for exception %s, max attempts reached (%s)', exc.__class__.__name__, max_attempts)
            raise
