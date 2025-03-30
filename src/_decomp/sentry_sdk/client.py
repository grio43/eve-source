#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sentry_sdk\client.py
import os
import uuid
import random
from datetime import datetime
from sentry_sdk._compat import string_types, text_type, iteritems
from sentry_sdk.utils import handle_in_app, get_type_name, capture_internal_exceptions, current_stacktrace, logger
from sentry_sdk.serializer import Serializer
from sentry_sdk.transport import make_transport
from sentry_sdk.consts import DEFAULT_OPTIONS, SDK_INFO
from sentry_sdk.integrations import setup_integrations
from sentry_sdk.utils import ContextVar
if False:
    from sentry_sdk.consts import ClientOptions
    from sentry_sdk.scope import Scope
    from typing import Any
    from typing import Dict
    from typing import Optional
_client_init_debug = ContextVar('client_init_debug')

def get_options(*args, **kwargs):
    if args and (isinstance(args[0], string_types) or args[0] is None):
        dsn = args[0]
        args = args[1:]
    else:
        dsn = None
    rv = dict(DEFAULT_OPTIONS)
    options = dict(*args, **kwargs)
    if dsn is not None and options.get('dsn') is None:
        options['dsn'] = dsn
    for key, value in iteritems(options):
        if key not in rv:
            raise TypeError('Unknown option %r' % (key,))
        rv[key] = value

    if rv['dsn'] is None:
        rv['dsn'] = os.environ.get('SENTRY_DSN')
    if rv['release'] is None:
        rv['release'] = os.environ.get('SENTRY_RELEASE')
    if rv['environment'] is None:
        rv['environment'] = os.environ.get('SENTRY_ENVIRONMENT')
    return rv


class Client(object):

    def __init__(self, *args, **kwargs):
        old_debug = _client_init_debug.get(False)
        try:
            self.options = options = get_options(*args, **kwargs)
            _client_init_debug.set(options['debug'])
            self.transport = make_transport(options)
            request_bodies = ('always', 'never', 'small', 'medium')
            if options['request_bodies'] not in request_bodies:
                raise ValueError('Invalid value for request_bodies. Must be one of {}'.format(request_bodies))
            self.integrations = setup_integrations(options['integrations'], with_defaults=options['default_integrations'])
        finally:
            _client_init_debug.set(old_debug)

    @property
    def dsn(self):
        return self.options['dsn']

    def _prepare_event(self, event, hint, scope):
        if event.get('timestamp') is None:
            event['timestamp'] = datetime.utcnow()
        if scope is not None:
            event = scope.apply_to_event(event, hint)
            if event is None:
                return
        if self.options['attach_stacktrace'] and 'exception' not in event and 'stacktrace' not in event and 'threads' not in event:
            with capture_internal_exceptions():
                event['threads'] = {'values': [{'stacktrace': current_stacktrace(self.options['with_locals']),
                             'crashed': False,
                             'current': True}]}
        for key in ('release', 'environment', 'server_name', 'dist'):
            if event.get(key) is None and self.options[key] is not None:
                event[key] = text_type(self.options[key]).strip()

        if event.get('sdk') is None:
            sdk_info = dict(SDK_INFO)
            sdk_info['integrations'] = sorted(self.integrations.keys())
            event['sdk'] = sdk_info
        if event.get('platform') is None:
            event['platform'] = 'python'
        event = handle_in_app(event, self.options['in_app_exclude'], self.options['in_app_include'])
        if event is not None:
            event = Serializer().serialize_event(event)
        before_send = self.options['before_send']
        if before_send is not None:
            new_event = None
            with capture_internal_exceptions():
                new_event = before_send(event, hint)
            if new_event is None:
                logger.info('before send dropped event (%s)', event)
            event = new_event
        return event

    def _is_ignored_error(self, event, hint):
        exc_info = hint.get('exc_info')
        if exc_info is None:
            return False
        type_name = get_type_name(exc_info[0])
        full_name = '%s.%s' % (exc_info[0].__module__, type_name)
        for errcls in self.options['ignore_errors']:
            if isinstance(errcls, string_types):
                if errcls == full_name or errcls == type_name:
                    return True
            elif issubclass(exc_info[0], errcls):
                return True

        return False

    def _should_capture(self, event, hint, scope = None):
        if scope is not None and not scope._should_capture:
            return False
        if self.options['sample_rate'] < 1.0 and random.random() >= self.options['sample_rate']:
            return False
        if self._is_ignored_error(event, hint):
            return False
        return True

    def capture_event(self, event, hint = None, scope = None):
        if self.transport is None:
            return
        if hint is None:
            hint = {}
        rv = event.get('event_id')
        if rv is None:
            event['event_id'] = rv = uuid.uuid4().hex
        if not self._should_capture(event, hint, scope):
            return
        event = self._prepare_event(event, hint, scope)
        if event is None:
            return
        self.transport.capture_event(event)
        return rv

    def close(self, timeout = None, callback = None):
        if self.transport is not None:
            self.flush(timeout=timeout, callback=callback)
            self.transport.kill()
            self.transport = None

    def flush(self, timeout = None, callback = None):
        if self.transport is not None:
            if timeout is None:
                timeout = self.options['shutdown_timeout']
            self.transport.flush(timeout=timeout, callback=callback)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()
