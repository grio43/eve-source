#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\launchdarkly\loader.py
import logging
import monolithconfig
import time
from uthread2 import Event
logger = logging.getLogger('LaunchDarkly')
_client_instance = None
_loader_event = None

def get_client():
    global _client_instance
    global _loader_event
    if _client_instance:
        logger.info('Return existing instance - {c}'.format(c=_client_instance))
        return _client_instance
    if _loader_event is None:
        _loader_event = Event()
    else:
        logger.info('Wait for another instance to finish loading: STARTED')
        start_time = time.time()
        _loader_event.wait()
        end_time = time.time()
        logger.info('Wait for another instance to finish loading: DONE - waited {s} seconds'.format(s=end_time - start_time))
    if _client_instance:
        logger.info('Loading ended, return existing instance - {c}'.format(c=_client_instance))
        return _client_instance
    try:
        if monolithconfig.on_client():
            from launchdarkly.client.client_sdk import Client, get_sdk_key
            logger.info('Load instance for EVE Client: STARTED')
            _client_instance = Client(sdk=_get_sdk(), sdk_key=get_sdk_key(), tenant=monolithconfig.get_client_tenant(), eve_user=monolithconfig.get_client_token_user())
            logger.info('Load instance for EVE Client: DONE - {c}'.format(c=_client_instance))
            return _client_instance
        if monolithconfig.on_server() or monolithconfig.on_proxy():
            logger.info('Load instance for EVE Server: STARTED')
            from launchdarkly.server.server_sdk import Client
            _client_instance = Client(sdk=_get_sdk(), tenant=monolithconfig.get_client_tenant())
            logger.info('Load instance for EVE Server: DONE - {c}'.format(c=_client_instance))
            return _client_instance
        raise NotImplementedError()
    except Exception as exc:
        logger.exception('Error when getting LaunchDarkly client: {exc}'.format(exc=exc))
        raise exc
    finally:
        _loader_event.set()


def reset_client():
    global _client_instance
    global _loader_event
    logger.info('Reset instance: STARTED')
    if _client_instance:
        _client_instance.release()
    _client_instance = None
    if _loader_event:
        _loader_event.set()
    _loader_event = None
    logger.info('Reset instance: DONE')


def _get_sdk():
    if monolithconfig.on_client():
        import launchdarkly_stackless_client_sdk
        return launchdarkly_stackless_client_sdk
    if monolithconfig.on_server() or monolithconfig.on_proxy():
        import launchdarkly_stackless_server_sdk
        return launchdarkly_stackless_server_sdk
    raise ImportError('role unsupported')
