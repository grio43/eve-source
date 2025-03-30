#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithhoneycomb\__init__.py
SAFE_SAMPLE_RATE = int(1000000)
try:
    import uthread
except ImportError:
    pass

import __builtin__
import monolithmetrics
import monolithconfig
import monolithgeoip2
import libhoney
import logging
import utillib
import atexit
import socket
import blue
import time
import sys
from globalConfig import MONOLITH_HONEYCOMB_PUBLIC_KEY_CONFIG, MONOLITH_HONEYCOMB_DATASET_CONFIG, MONOLITH_HONEYCOMB_SHUTDOWN_SLEEP_MS_CONFIG, MONOLITH_HONEYCOMB_SHUTDOWN_SLEEP_MS_DEFAULT, MONOLITH_HONEYCOMB_MAX_SHUTDOWN_MS_CONFIG, MONOLITH_HONEYCOMB_MAX_SHUTDOWN_MS_DEFAULT
from stackless_tracing.attributes import CLIENT_FIELD_USER, CLIENT_FIELD_CHARACTER, CLIENT_FIELD_CORPORATION, CLIENT_FIELD_ALLIANCE, CLIENT_FIELD_SOLAR_SYSTEM_2
from stackless_tracing.attributes import CLIENT_FIELD_SERVER_ARG, CLIENT_FIELD_MACHINE
from stackless_tracing.attributes import CLUSTER_FIELD_MACHONET_MACHINE_ID, CLUSTER_FIELD_MACHONET_NODE_GROUP, CLUSTER_FIELD_MACHONET_NODE_INDEX, CLUSTER_FIELD_MACHONET_NODE_SERVICE_MASK, CLUSTER_FIELD_MACHONET_NODE_ID, CLIENT_FIELD_COUNTRY
from stackless_tracing.attributes import BOOT_ROLE, BRANCH_NAME, CLUSTER_MODE, CLIENT_FIELD_MACHONET_ADDRESS, TENANT, HOST_NAME
SESSION_CHANGE_IX_VALUE_NEW = 1
CLIENT_SESSION_FIELDS = {'userid': CLIENT_FIELD_USER,
 'charid': CLIENT_FIELD_CHARACTER,
 'corpid': CLIENT_FIELD_CORPORATION,
 'allianceid': CLIENT_FIELD_ALLIANCE,
 'solarsystemid2': CLIENT_FIELD_SOLAR_SYSTEM_2}
CONFIG_GROUP = 'honeycomb'
GLOBAL_CONFIG = 'gc'
logger = logging.getLogger(__name__)
_trace_sample_rate = SAFE_SAMPLE_RATE
_active_clients = {}
_machonet = None

def init(service_manager):
    global _machonet
    machonet = service_manager.GetService('machoNet')
    if machonet is None:
        logger.error('cannot initialize without machonet')
        return
    _machonet = machonet
    if monolithconfig.on_client():
        service_manager.RegisterForNotifyEvent(sys.modules[__name__], 'OnSessionChanged')
    atexit.register(shutdown)


def shutdown():
    global _active_clients
    total_clients = len(_active_clients)
    sleep_ms, max_sleep_ms = _get_shutdown_parameters()
    expected_max_ms = max_sleep_ms * total_clients
    logger.info('{}: monolithhoneycomb.shutdown {} clients. sleep_ms {}, max_sleep_ms {}, per client'.format(monolithconfig._get_boot_role(), total_clients, sleep_ms, max_sleep_ms))
    start_time = time.time()
    ret = []
    calls = []
    for client in _active_clients.itervalues():
        calls.append((client.stackless_close, (sleep_ms, max_sleep_ms)))

    try:
        ret = uthread.parallel(calls) or []
    except Exception as e:
        logger.error('error closing libhoney client for shutdown: {}'.format(e))
        return

    end_time = time.time()
    total_duration_ms = (end_time - start_time) * 1000
    try:
        for line in ret:
            duration_ms, start_size, end_size, i = line
            if duration_ms < max_sleep_ms and end_size == 0:
                logger.info('{} libhoney.stackless_close successfully flushed ~{} events in {} attempts over {} milliseconds'.format(monolithconfig._get_boot_role(), start_size, i, duration_ms))
            else:
                logger.warn('{} libhoney.stackless_close flushed ~{}/{} events in {} attempts over {} milliseconds'.format(monolithconfig._get_boot_role(), start_size - end_size, start_size, i, duration_ms))

    except Exception as e:
        logger.error(e)

    if total_duration_ms < expected_max_ms:
        logger.info('monolithhoneycomb.shutdown {} clients in {} milliseconds'.format(total_clients, total_duration_ms))
    else:
        logger.warning('monolithhoneycomb.shutdown took too long shutting down {} clients in {} milliseconds'.format(total_clients, total_duration_ms))


def update_config():
    if _machonet is None:
        logger.warn('update_config called without initialized machonet')
        return
    new_writekey = _write_key()
    for client in _active_clients.itervalues():
        client.writekey = new_writekey
        client.dataset = _dataset()


monolithconfig.add_global_config_callback(update_config)
monolithconfig.add_watch_group_callback(update_config, CONFIG_GROUP)

def new_client(client_name, sample_rate):
    if _machonet is None:
        logger.error('new monolithhoneycomb client requested before module init')
        return
    if client_name in _active_clients:
        logger.warn('client already exists')
        return _active_clients[client_name]
    writekey = _write_key()
    if writekey is None or len(writekey) == 0:
        return
    sample_rate = _safe_sample_rate(sample_rate)
    dataset = _dataset()
    client = libhoney.client.Client(writekey=writekey, dataset=dataset, sample_rate=sample_rate)
    _set_context_fields(client)
    _active_clients[client_name] = client
    monolithmetrics.gauge('monolithhoneycomb.active_clients', len(_active_clients))
    return client


def macho_net():
    if _machonet is None:
        logger.error('monolithhoneycomb has not initialized')
    return _machonet


def _safe_sample_rate(sample_rate):
    try:
        sample_rate = int(sample_rate)
        if sample_rate < 1:
            raise ValueError
    except (TypeError, ValueError):
        sample_rate = SAFE_SAMPLE_RATE
        logger.warn('invalid sample rate supplied. using default safe sample rate %d', SAFE_SAMPLE_RATE)

    return sample_rate


def _write_key():
    if monolithconfig.on_client():
        writekey = monolithconfig.get_value(MONOLITH_HONEYCOMB_PUBLIC_KEY_CONFIG, GLOBAL_CONFIG)
    else:
        writekey = monolithconfig.get_value('writekey', CONFIG_GROUP)
    return writekey


def _dataset():
    dataset = monolithconfig.get_value(MONOLITH_HONEYCOMB_DATASET_CONFIG)
    return dataset


def _set_context_fields(client):
    cluster_mode = monolithconfig.get_value('clusterMode', 'prefs')
    boot_role = monolithconfig.get_value('role', 'boot')
    boot_codename = monolithconfig.get_value('codename', 'boot')
    machine_name = socket.gethostname()
    client.add_field(CLUSTER_MODE, cluster_mode)
    client.add_field(BOOT_ROLE, boot_role)
    client.add_field(BRANCH_NAME, boot_codename)
    client.add_field(HOST_NAME, machine_name)
    if monolithconfig.on_client():
        client.add_field(CLIENT_FIELD_SERVER_ARG, utillib.GetServerName())
        client.add_field(TENANT, monolithconfig.get_cluster_name().lower())
        client.add_field(CLIENT_FIELD_MACHINE, blue.os.GetStartupArgValue('machineHash'))
        session = getattr(__builtin__, 'session', None)
        if session is None:
            return
        change = {k:(None, getattr(session, k)) for k in CLIENT_SESSION_FIELDS.keys()}
        _update_client_session_fields(client, change)
        _set_client_address_and_country_fields(client, session)
    else:
        cluster_name = monolithconfig.get_value('clusterName', 'prefs')
        client.add_field(CLUSTER_FIELD_MACHONET_MACHINE_ID, _machonet.machineID)
        client.add_field(CLUSTER_FIELD_MACHONET_NODE_GROUP, getattr(_machonet, 'clusterGroup', None))
        client.add_field(CLUSTER_FIELD_MACHONET_NODE_INDEX, _machonet.nodeIndex)
        client.add_field(CLUSTER_FIELD_MACHONET_NODE_SERVICE_MASK, _machonet.serviceMask)
        client.add_field(CLUSTER_FIELD_MACHONET_NODE_ID, _machonet.nodeID)
        client.add_field(TENANT, cluster_name.lower())


def _get_shutdown_parameters():
    sleep_ms = monolithconfig.get_value(MONOLITH_HONEYCOMB_SHUTDOWN_SLEEP_MS_CONFIG, GLOBAL_CONFIG)
    if sleep_ms is None:
        sleep_ms = MONOLITH_HONEYCOMB_SHUTDOWN_SLEEP_MS_DEFAULT
    max_sleep_ms = monolithconfig.get_value(MONOLITH_HONEYCOMB_MAX_SHUTDOWN_MS_CONFIG, GLOBAL_CONFIG)
    if max_sleep_ms is None:
        max_sleep_ms = MONOLITH_HONEYCOMB_MAX_SHUTDOWN_MS_DEFAULT
    return (float(sleep_ms), float(max_sleep_ms))


def _handle_client_context(isRemote, sess, change):
    if not monolithconfig.on_client():
        return
    for client in _active_clients.itervalues():
        _update_client_session_fields(client, change)


def _update_client_session_fields(client, change):
    for key in change:
        if key in CLIENT_SESSION_FIELDS:
            client.add_field(CLIENT_SESSION_FIELDS[key], change[key][SESSION_CHANGE_IX_VALUE_NEW])


def _set_client_address_and_country_fields(client, session):
    address = session.address
    if address is None:
        return
    parts = address.split(':')
    ip = parts[0]
    country_name = _get_country_name(ip)
    client.add_field(CLIENT_FIELD_COUNTRY, country_name)
    client.add_field(CLIENT_FIELD_MACHONET_ADDRESS, ip)


def _get_country_name(ip):
    try:
        country_info = monolithgeoip2.country(ip)
        if country_info is None:
            return 'N/A'
        return country_info.country.name
    except Exception:
        return 'N/A'


OnSessionChanged = _handle_client_context
