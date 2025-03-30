#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithhoneycomb_events\__init__.py
import reserved
import event_sample_rates as rates
import monolithconfig
import monolithmetrics
import logging
import random
import sys
from monolithhoneycomb import new_client, SAFE_SAMPLE_RATE, CONFIG_GROUP
from globalConfig import MONOLITH_HONEYCOMB_EVENTS_ENABLED_CONFIG
_enabled = False
_server_honeycomb_client = None
logger = logging.getLogger(__name__)
GLOBAL_CONFIG = 'gc'
SESSION_CHANGE_IX_VALUE_NEW = 1
CLIENT_NAME = 'monolithhoneycomb_events'

def init(service_manager):
    if service_manager is None:
        logger.error('service_manager is required to initialize Honey Events')
        return
    if monolithconfig.on_server() or monolithconfig.on_proxy():
        monolithconfig.add_watch_group_callback(_start_module, CONFIG_GROUP)
    if monolithconfig.on_client():
        service_manager.RegisterForNotifyEvent(sys.modules[__name__], 'OnSessionChanged')
    monolithconfig.add_global_config_callback(global_config_updated)


def send(event_name, field_map = None):
    global _enabled
    if not _enabled:
        return
    if field_map is None:
        field_map = {}
    _send_honeycomb_event(event_name, field_map)


def _send_honeycomb_event(event_name, field_map):
    global _server_honeycomb_client
    if _server_honeycomb_client is None or not _enabled:
        return
    sample_rate = rates.get(event_name)
    if _should_send(sample_rate):
        try:
            event = _create_event_with_fields(event_name, field_map)
            event.sample_rate = sample_rate
            event.send_presampled()
            monolithmetrics.increment(reserved.EVENT_SENT_COUNT, tags=['{}:{}'.format(reserved.EVENT_FIELD_NAME, event_name)])
        except Exception:
            logger.error('error relaying monolith honeycomb event')

    else:
        monolithmetrics.increment(reserved.EVENT_DISCARDED_COUNT, tags=['{}:{}'.format(reserved.EVENT_FIELD_NAME, event_name)])


def global_config_updated():
    global _enabled
    try:
        _enabled = monolithconfig.enabled(MONOLITH_HONEYCOMB_EVENTS_ENABLED_CONFIG, GLOBAL_CONFIG)
        if _enabled and _server_honeycomb_client is None:
            _start_module()
    except Exception as _:
        pass


def _handle_client_session(isRemote, sess, change):
    if 'address' in change and change['address'] is not None:
        _start_module()


def _start_module(*args, **kwargs):
    if _server_honeycomb_client is None:
        _create_client()
    global_config_updated()


def _create_event_with_fields(event_name, field_map = None):
    event = _server_honeycomb_client.new_event()
    _add_fields(event, event_name, field_map)
    return event


def _add_fields(event, event_name, field_dict_map = None):
    event.add_field(reserved.EVENT_FIELD_NAME, event_name)
    if field_dict_map is None:
        return
    event.add(field_dict_map)


def _create_client():
    global _server_honeycomb_client
    _server_honeycomb_client = new_client(CLIENT_NAME, SAFE_SAMPLE_RATE)


def _reset():
    global _server_honeycomb_client
    global _enabled
    _enabled = False
    _server_honeycomb_client = None


def _should_send(sample_rate):
    return random.randint(1, sample_rate) == 1


OnSessionChanged = _handle_client_session
