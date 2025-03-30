#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sentry_sdk\integrations\django\__init__.py
from __future__ import absolute_import
import sys
import weakref
from django import VERSION as DJANGO_VERSION
from django.db.models.query import QuerySet
from django.core import signals
if False:
    from typing import Any
    from typing import Dict
    from typing import Tuple
    from typing import Union
    from sentry_sdk.integrations.wsgi import _ScopedResponse
    from typing import Callable
    from django.core.handlers.wsgi import WSGIRequest
    from django.http.response import HttpResponse
    from django.http.request import QueryDict
    from django.utils.datastructures import MultiValueDict
    from typing import List
try:
    from django.urls import resolve
except ImportError:
    from django.core.urlresolvers import resolve

from sentry_sdk import Hub
from sentry_sdk.hub import _should_send_default_pii
from sentry_sdk.scope import add_global_event_processor
from sentry_sdk.serializer import add_global_repr_processor
from sentry_sdk.utils import capture_internal_exceptions, event_from_exception, safe_repr, format_and_strip, transaction_from_function, walk_exception_chain
from sentry_sdk.integrations import Integration
from sentry_sdk.integrations.logging import ignore_logger
from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware
from sentry_sdk.integrations._wsgi_common import RequestExtractor
from sentry_sdk.integrations.django.transactions import LEGACY_RESOLVER
from sentry_sdk.integrations.django.templates import get_template_frame_from_exception
if DJANGO_VERSION < (1, 10):

    def is_authenticated(request_user):
        return request_user.is_authenticated()


else:

    def is_authenticated(request_user):
        return request_user.is_authenticated


class DjangoIntegration(Integration):
    identifier = 'django'
    transaction_style = None

    def __init__(self, transaction_style = 'url'):
        TRANSACTION_STYLE_VALUES = ('function_name', 'url')
        if transaction_style not in TRANSACTION_STYLE_VALUES:
            raise ValueError('Invalid value for transaction_style: %s (must be in %s)' % (transaction_style, TRANSACTION_STYLE_VALUES))
        self.transaction_style = transaction_style

    @staticmethod
    def setup_once():
        install_sql_hook()
        ignore_logger('django.server')
        ignore_logger('django.request')
        from django.core.handlers.wsgi import WSGIHandler
        old_app = WSGIHandler.__call__

        def sentry_patched_wsgi_handler(self, environ, start_response):
            if Hub.current.get_integration(DjangoIntegration) is None:
                return old_app(self, environ, start_response)
            return SentryWsgiMiddleware(lambda *a, **kw: old_app(self, *a, **kw))(environ, start_response)

        WSGIHandler.__call__ = sentry_patched_wsgi_handler
        from django.core.handlers.base import BaseHandler
        old_get_response = BaseHandler.get_response

        def sentry_patched_get_response(self, request):
            hub = Hub.current
            integration = hub.get_integration(DjangoIntegration)
            if integration is not None:
                with hub.configure_scope() as scope:
                    scope.add_event_processor(_make_event_processor(weakref.ref(request), integration))
            return old_get_response(self, request)

        BaseHandler.get_response = sentry_patched_get_response
        signals.got_request_exception.connect(_got_request_exception)

        @add_global_event_processor
        def process_django_templates(event, hint):
            exc_info = hint.get('exc_info', None)
            if exc_info is None:
                return event
            exception = event.get('exception', None)
            if exception is None:
                return event
            values = exception.get('values', None)
            if values is None:
                return event
            for exception, (_, exc_value, _) in zip(reversed(values), walk_exception_chain(exc_info)):
                frame = get_template_frame_from_exception(exc_value)
                if frame is not None:
                    frames = exception.get('stacktrace', {}).get('frames', [])
                    for i in reversed(range(len(frames))):
                        f = frames[i]
                        if f.get('function') in ('parse', 'render') and f.get('module') == 'django.template.base':
                            i += 1
                            break
                    else:
                        i = len(frames)

                    frames.insert(i, frame)

            return event

        @add_global_repr_processor
        def _django_queryset_repr(value, hint):
            if not isinstance(value, QuerySet) or value._result_cache:
                return NotImplemented
            return u'<%s from %s at 0x%x>' % (value.__class__.__name__, value.__module__, id(value))


def _make_event_processor(weak_request, integration):

    def event_processor(event, hint):
        request = weak_request()
        if request is None:
            return event
        try:
            if integration.transaction_style == 'function_name':
                event['transaction'] = transaction_from_function(resolve(request.path).func)
            elif integration.transaction_style == 'url':
                event['transaction'] = LEGACY_RESOLVER.resolve(request.path)
        except Exception:
            pass

        with capture_internal_exceptions():
            DjangoRequestExtractor(request).extract_into_event(event)
        if _should_send_default_pii():
            with capture_internal_exceptions():
                _set_user_info(request, event)
        return event

    return event_processor


def _got_request_exception(request = None, **kwargs):
    hub = Hub.current
    integration = hub.get_integration(DjangoIntegration)
    if integration is not None:
        event, hint = event_from_exception(sys.exc_info(), client_options=hub.client.options, mechanism={'type': 'django',
         'handled': False})
        hub.capture_event(event, hint=hint)


class DjangoRequestExtractor(RequestExtractor):

    def env(self):
        return self.request.META

    def cookies(self):
        return self.request.COOKIES

    def raw_data(self):
        return self.request.body

    def form(self):
        return self.request.POST

    def files(self):
        return self.request.FILES

    def size_of_file(self, file):
        return file.size

    def parsed_body(self):
        try:
            return self.request.data
        except AttributeError:
            return RequestExtractor.parsed_body(self)


def _set_user_info(request, event):
    user_info = event.setdefault('user', {})
    user = getattr(request, 'user', None)
    if user is None or not is_authenticated(user):
        return
    try:
        user_info['id'] = str(user.pk)
    except Exception:
        pass

    try:
        user_info['email'] = user.email
    except Exception:
        pass

    try:
        user_info['username'] = user.get_username()
    except Exception:
        pass


class _FormatConverter(object):

    def __init__(self, param_mapping):
        self.param_mapping = param_mapping
        self.params = []

    def __getitem__(self, val):
        self.params.append(self.param_mapping.get(val))
        return '%s'


def format_sql(sql, params):
    rv = []
    if isinstance(params, dict):
        conv = _FormatConverter(params)
        if params:
            sql = sql % conv
            params = conv.params
        else:
            params = ()
    for param in params or ():
        if param is None:
            rv.append('NULL')
        param = safe_repr(param)
        rv.append(param)

    return (sql, rv)


def record_sql(sql, params, cursor = None):
    hub = Hub.current
    if hub.get_integration(DjangoIntegration) is None:
        return
    real_sql = None
    real_params = None
    try:
        real_sql, real_params = format_sql(sql, params)
        if real_sql:
            real_sql = format_and_strip(real_sql, real_params)
    except Exception:
        pass

    if not real_sql and cursor and hasattr(cursor, 'mogrify'):
        try:
            if cursor and hasattr(cursor, 'mogrify'):
                real_sql = cursor.mogrify(sql, params)
                if isinstance(real_sql, bytes):
                    real_sql = real_sql.decode(cursor.connection.encoding)
        except Exception:
            pass

    if real_sql:
        with capture_internal_exceptions():
            hub.add_breadcrumb(message=real_sql, category='query')


def install_sql_hook():
    try:
        from django.db.backends.utils import CursorWrapper
    except ImportError:
        from django.db.backends.util import CursorWrapper

    try:
        real_execute = CursorWrapper.execute
        real_executemany = CursorWrapper.executemany
    except AttributeError:
        return

    def record_many_sql(sql, param_list, cursor):
        for params in param_list:
            record_sql(sql, params, cursor)

    def execute(self, sql, params = None):
        try:
            return real_execute(self, sql, params)
        finally:
            record_sql(sql, params, self.cursor)

    def executemany(self, sql, param_list):
        try:
            return real_executemany(self, sql, param_list)
        finally:
            record_many_sql(sql, param_list, self.cursor)

    CursorWrapper.execute = execute
    CursorWrapper.executemany = executemany
    ignore_logger('django.db.backends')
