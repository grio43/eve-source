#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sentry_sdk\integrations\logging.py
from __future__ import absolute_import
import logging
import datetime
from sentry_sdk.hub import Hub
from sentry_sdk.utils import to_string, event_from_exception, current_stacktrace, capture_internal_exceptions
from sentry_sdk.integrations import Integration
from sentry_sdk._compat import iteritems
if False:
    from logging import LogRecord
    from typing import Any
    from typing import Dict
    from typing import Optional
DEFAULT_LEVEL = logging.INFO
DEFAULT_EVENT_LEVEL = logging.ERROR
_IGNORED_LOGGERS = set(['sentry_sdk.errors'])

def ignore_logger(name):
    _IGNORED_LOGGERS.add(name)


class LoggingIntegration(Integration):
    identifier = 'logging'

    def __init__(self, level = DEFAULT_LEVEL, event_level = DEFAULT_EVENT_LEVEL):
        self._handler = None
        self._breadcrumb_handler = None
        if level is not None:
            self._breadcrumb_handler = BreadcrumbHandler(level=level)
        if event_level is not None:
            self._handler = EventHandler(level=event_level)

    def _handle_record(self, record):
        if self._handler is not None and record.levelno >= self._handler.level:
            self._handler.handle(record)
        if self._breadcrumb_handler is not None and record.levelno >= self._breadcrumb_handler.level:
            self._breadcrumb_handler.handle(record)

    @staticmethod
    def setup_once():
        old_callhandlers = logging.Logger.callHandlers

        def sentry_patched_callhandlers(self, record):
            try:
                return old_callhandlers(self, record)
            finally:
                if record.name not in _IGNORED_LOGGERS:
                    integration = Hub.current.get_integration(LoggingIntegration)
                    if integration is not None:
                        integration._handle_record(record)

        logging.Logger.callHandlers = sentry_patched_callhandlers


def _can_record(record):
    return record.name not in _IGNORED_LOGGERS


def _breadcrumb_from_record(record):
    return {'ty': 'log',
     'level': _logging_to_event_level(record.levelname),
     'category': record.name,
     'message': record.message,
     'timestamp': datetime.datetime.fromtimestamp(record.created),
     'data': _extra_from_record(record)}


def _logging_to_event_level(levelname):
    return {'critical': 'fatal'}.get(levelname.lower(), levelname.lower())


COMMON_RECORD_ATTRS = frozenset(('args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName', 'levelname', 'levelno', 'linenno', 'lineno', 'message', 'module', 'msecs', 'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated', 'stack', 'tags', 'thread', 'threadName'))

def _extra_from_record(record):
    return {k:v for k, v in iteritems(vars(record)) if k not in COMMON_RECORD_ATTRS and not k.startswith('_')}


class EventHandler(logging.Handler, object):

    def emit(self, record):
        with capture_internal_exceptions():
            self.format(record)
            return self._emit(record)

    def _emit(self, record):
        if not _can_record(record):
            return
        hub = Hub.current
        if hub.client is None:
            return
        hint = None
        client_options = hub.client.options
        if record.exc_info is not None and record.exc_info[0] is not None:
            event, hint = event_from_exception(record.exc_info, client_options=client_options, mechanism={'type': 'logging',
             'handled': True})
        elif record.exc_info and record.exc_info[0] is None:
            event = {}
            hint = None
            with capture_internal_exceptions():
                event['threads'] = {'values': [{'stacktrace': current_stacktrace(client_options['with_locals']),
                             'crashed': False,
                             'current': True}]}
        else:
            event = {}
        event['level'] = _logging_to_event_level(record.levelname)
        event['logger'] = record.name
        event['logentry'] = {'message': to_string(record.msg),
         'params': record.args}
        event['extra'] = _extra_from_record(record)
        hub.capture_event(event, hint=hint)


SentryHandler = EventHandler

class BreadcrumbHandler(logging.Handler, object):

    def emit(self, record):
        with capture_internal_exceptions():
            self.format(record)
            return self._emit(record)

    def _emit(self, record):
        if not _can_record(record):
            return
        Hub.current.add_breadcrumb(_breadcrumb_from_record(record), hint={'log_record': record})
