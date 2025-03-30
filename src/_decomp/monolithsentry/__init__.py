#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithsentry\__init__.py
import logging
import eveexceptions
import socket
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from monolithsentry.transport import RequestsSessionTransport
from monolithsentry.throttle import Throttle
from monolithsentry.environment import get_environment
from monolithsentry.dsn import get_config_dsn
from monolithsentry.minidump import set_sentry_crash_key
from monolithsentry.tags import get_tags
from monolithsentry.quasar_tags import get_quasar_tags
from monolithsentry.machonet_context import *
from monolithsentry.geoip2_tags import set_geo_tags
from monolithsentry.session_info import get_session_info
from monolithsentry.user_info import get_user_info
import monolithconfig
throttle = Throttle(1.0, 60.0)
_public_gateway_svc = None

def init(hardcoded_dsn):
    dsn_override = get_config_dsn()
    if dsn_override:
        hardcoded_dsn = dsn_override
    sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)
    server_name = socket.gethostname() if hasattr(socket, 'gethostname') else None
    if monolithconfig.on_client():
        server_name = get_environment()
    release = '{}.{}'.format(monolithconfig.get_value('version', 'boot'), monolithconfig.get_value('build', 'boot'))
    sentry_sdk.init(dsn=hardcoded_dsn, transport=RequestsSessionTransport, default_integrations=False, before_send=_preprocessor, release=release, environment=get_environment(), integrations=[sentry_logging], with_locals=True, server_name=server_name)
    with sentry_sdk.configure_scope() as scope:
        tags = get_tags()
        for k, v in tags.iteritems():
            scope.set_tag(k, v)

    import logmodule
    logmodule.sentry_client = capture_exception


def set_public_gateway_service_reference(public_gateway_svc):
    global _public_gateway_svc
    _public_gateway_svc = public_gateway_svc


def capture_exception(message, exc_info = None, extra = None, new_tags = None):
    with sentry_sdk.push_scope() as scope:
        if extra:
            for k, v in extra.iteritems():
                scope.set_extra(k, v)

        if new_tags:
            for k, v in new_tags.iteritems():
                scope.set_tag(k, v)

        scope.set_extra('message', message)
        sentry_sdk.capture_exception(error=exc_info)


def capture_error(message, extra = None, new_tags = None):
    with sentry_sdk.push_scope() as scope:
        if extra:
            for k, v in extra.iteritems():
                scope.set_extra(k, v)

        if new_tags:
            for k, v in new_tags.iteritems():
                scope.set_tag(k, v)

        sentry_sdk.capture_message(message, 'error')


def _preprocessor(event, hint):
    if throttle.throttled():
        return
    if monolithconfig.on_client():
        if 'exc_info' in hint:
            exc_type, _, _ = hint['exc_info']
            if exc_type == eveexceptions.UserError:
                return
    sane_session_info = get_session_info()
    if sane_session_info:
        event['extra']['session'] = sane_session_info
    event['user'] = get_user_info()
    if _public_gateway_svc is not None:
        event['tags'].update(get_quasar_tags(_public_gateway_svc))
    return event
