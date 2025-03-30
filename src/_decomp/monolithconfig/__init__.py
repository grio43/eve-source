#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithconfig\__init__.py
from collections import defaultdict
import logging
import uthread2
from eveprefs import prefs, boot
try:
    import blue
except ImportError:
    blue = None

import monolithconfig.synonyms
_monolith_config_service_manager = None
_group_callbacks = defaultdict(list)
log = logging.getLogger('monolithconfig')
live_servers = ['tranquility', 'serenity']
test_servers = ['bond',
 'duality',
 'eternity',
 'helix',
 'osmosis',
 'singularity',
 'bacchus',
 'chaos',
 'entropy',
 'fractal',
 'multiplicity',
 'pulsar',
 'thunderdome',
 'winston',
 'cosmos']
GLOBAL_CONFIG_GROUP = 'global_config_group'
SSO_TOKEN_ARG_NAME = '/ssoToken='
SERVER_ARG_NAME = '/server:'
REFRESH_TOKEN_ARG_NAME = '/refreshToken='

def set_service_manager(service_manager):
    global _monolith_config_service_manager
    if _monolith_config_service_manager is not None:
        return
    _monolith_config_service_manager = service_manager
    _trigger_all_callbacks()


def _trigger_all_callbacks():
    global _group_callbacks
    for group in _group_callbacks.keys():
        _trigger_group_callback(group)


def _trigger_group_callback(group):
    if group not in _group_callbacks:
        return
    for callback in _group_callbacks[group]:
        _trigger_callback(callback, group)


def _trigger_callback(callback, group):
    try:
        uthread2.StartTasklet(callback)
    except Exception as e:
        log.exception('Failed to execute callback on group update: (%s)', group)


def flush(group = None):
    if group is None:
        return
    _trigger_group_callback(group)


def defer_global_config_updates():
    uthread2.StartTasklet(trigger_global_config_updates)


def trigger_global_config_updates():
    flush(GLOBAL_CONFIG_GROUP)


def _get_boot_role():
    if boot is None:
        return ''
    return boot.role


def on_proxy():
    if _get_boot_role() == 'proxy':
        return True
    return False


def on_client():
    if _get_boot_role() == 'client':
        return True
    return False


def on_server():
    if _get_boot_role() == 'server':
        return True
    return False


def _get_service_manager():
    return _monolith_config_service_manager


def _get_macho_net():
    service_manager = _get_service_manager()
    if service_manager is None:
        return
    return service_manager.GetService('machoNet')


def _get_cache_service():
    if on_client():
        return
    if on_server():
        service_manager = _get_service_manager()
        if service_manager is None:
            return
        return service_manager.GetService('cache')
    if on_proxy():
        macho_net = _get_macho_net()
        if macho_net is None:
            return
        return macho_net.session.ConnectToAnyService('cache')


def _global_config_get(key):
    macho_net = _get_macho_net()
    if macho_net is None:
        return
    try:
        result = macho_net.GetGlobalConfig().get(key, None)
    except Exception as e:
        result = None

    return result


def _cache_get(group, key):
    if group is None:
        return
    cache_service = _get_cache_service()
    if cache_service is None:
        return
    try:
        result = cache_service.Setting(group, key, valueIfNotFound=None)
    except Exception as e:
        result = None

    return result


def _prefs_get(key):
    try:
        result = prefs.GetValue(key, None)
    except Exception as e:
        result = None

    return result


def _boot_get(key):
    try:
        result = boot.GetValue(key, None)
    except Exception as e:
        result = None

    return result


def _get_cmd_arg(arg_name):
    cmd_args = blue.pyos.GetArg()
    for entry in cmd_args:
        if entry.startswith(arg_name):
            return entry[len(arg_name):]

    return ''


def get_value(config_key, config_group = None):
    if config_group:
        if config_group == 'prefs':
            result = _prefs_get(config_key)
            if result is not None:
                return unicode(result)
        if config_group == 'boot':
            result = _boot_get(config_key)
            if result is not None:
                return unicode(result)
        result = _cache_get(config_group, config_key)
        if result is not None:
            return unicode(result)
        if config_group == 'gc':
            result = _global_config_get(config_key)
            if result is not None:
                return unicode(result)
        composite_key = config_group + '.' + config_key
        result = get_value(composite_key)
        if result is not None:
            return unicode(result)
    result = _global_config_get(config_key)
    if result is not None:
        return unicode(result)
    result = _prefs_get(config_key)
    if result is not None:
        return unicode(result)
    result = _boot_get(config_key)
    if result is not None:
        return unicode(result)
    return result


def enabled(config_key, config_group = None):
    result = get_value(config_key, config_group)
    result = unicode(result).lower()
    if result in synonyms.ENABLED:
        return True
    if result in synonyms.DISABLED:
        return False
    return False


def add_watch_group_callback(callback, config_group):
    _group_callbacks[config_group].append(callback)
    _trigger_callback(callback, config_group)


def add_global_config_callback(callback):
    add_watch_group_callback(callback, GLOBAL_CONFIG_GROUP)


def get_tier():
    if on_client():
        return get_client_tier()
    return get_server_tier()


def get_client_tier():
    tier = 'dev'
    user_token = get_user_token()
    if not user_token:
        return tier
    try:
        tier = user_token['tier']
    except KeyError as e:
        return tier

    tier = tier.lower()
    if tier in ('production', 'prod'):
        tier = 'live'
    return tier


def get_client_token_user():
    user_token = get_user_token()
    if not user_token:
        return
    subject = None
    try:
        subject = user_token['sub']
    except KeyError as e:
        return subject

    subject_parts = subject.split(':')
    if len(subject_parts) != 3:
        return
    if subject_parts[0] != 'USER':
        return
    if subject_parts[1] != 'EVE':
        return
    return subject_parts[2]


def get_client_tenant():
    tenant = None
    user_token = monolithconfig.get_user_token()
    if user_token:
        try:
            tenant = user_token['tenant']
        except Exception:
            pass

    if not user_token:
        tenant = blue.os.GetStartupArgValue('tenant')
    if not tenant:
        server_name = get_client_server_name()
        tenant = server_name
    if not tenant:
        tenant = get_value('clusterName', 'prefs')
    return tenant


def get_client_region():
    region = None
    user_token = get_user_token()
    if user_token:
        try:
            region = user_token['region']
        except Exception as e:
            pass

    return region


def get_refresh_token():
    refresh_token = _get_cmd_arg(REFRESH_TOKEN_ARG_NAME)
    if not refresh_token:
        refresh_token = None
        log.warning('Empty refresh token in cmd args')
    return refresh_token


def get_user_jwt():
    return _get_cmd_arg(SSO_TOKEN_ARG_NAME)


def get_user_token():
    user_token = get_user_jwt()
    if not user_token:
        log.warning('Empty user_token token in cmd args')
        return
    try:
        import jwt
        user_token = jwt.decode(user_token, verify=False)
    except Exception:
        user_token = None

    return user_token


def get_client_server_name():
    server_name = _get_cmd_arg(SERVER_ARG_NAME)
    if not server_name:
        log.warning('Empty server name in cmd args')
        return ''
    return server_name


def get_server_tier():
    cluster_mode = get_value('clusterMode', 'prefs')
    if not cluster_mode:
        return 'dev'
    cluster_name = get_value('clusterName', 'prefs')
    if cluster_name.lower() in live_servers:
        return 'live'
    if cluster_name.lower() in test_servers:
        return 'test'
    if cluster_mode == 'LOCAL':
        return 'dev'
    if cluster_mode == 'TEST':
        return 'test'
    if cluster_mode == 'LIVE':
        return 'live'
    return 'dev'


def get_cluster_name():
    machonet = _get_macho_net()
    if not machonet:
        return
    return machonet.GetConnectedClusterName()
