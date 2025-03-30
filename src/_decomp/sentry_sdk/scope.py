#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sentry_sdk\scope.py
from copy import copy
from collections import deque
from functools import wraps
from itertools import chain
from sentry_sdk.utils import logger, capture_internal_exceptions
if False:
    from typing import Any
    from typing import Callable
    from typing import Dict
    from typing import Optional
    from typing import Deque
    from typing import List
global_event_processors = []

def add_global_event_processor(processor):
    global_event_processors.append(processor)


def _attr_setter(fn):
    return property(fset=fn, doc=fn.__doc__)


def _disable_capture(fn):

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        if not self._should_capture:
            return
        try:
            self._should_capture = False
            return fn(self, *args, **kwargs)
        finally:
            self._should_capture = True

    return wrapper


class Scope(object):
    __slots__ = ('_level', '_name', '_fingerprint', '_transaction', '_user', '_tags', '_contexts', '_extras', '_breadcrumbs', '_event_processors', '_error_processors', '_should_capture', '_span')

    def __init__(self):
        self._event_processors = []
        self._error_processors = []
        self._name = None
        self.clear()

    @_attr_setter
    def level(self, value):
        self._level = value

    @_attr_setter
    def fingerprint(self, value):
        self._fingerprint = value

    @_attr_setter
    def transaction(self, value):
        self._transaction = value

    @_attr_setter
    def user(self, value):
        self._user = value

    def set_span_context(self, span_context):
        self._span = span_context

    def set_tag(self, key, value):
        self._tags[key] = value

    def remove_tag(self, key):
        self._tags.pop(key, None)

    def set_context(self, key, value):
        self._contexts[key] = value

    def remove_context(self, key):
        self._contexts.pop(key, None)

    def set_extra(self, key, value):
        self._extras[key] = value

    def remove_extra(self, key):
        self._extras.pop(key, None)

    def clear(self):
        self._level = None
        self._fingerprint = None
        self._transaction = None
        self._user = None
        self._tags = {}
        self._contexts = {}
        self._extras = {}
        self.clear_breadcrumbs()
        self._should_capture = True
        self._span = None

    def clear_breadcrumbs(self):
        self._breadcrumbs = deque()

    def add_event_processor(self, func):
        self._event_processors.append(func)

    def add_error_processor(self, func, cls = None):
        if cls is not None:
            real_func = func

            def func(event, exc_info):
                try:
                    is_inst = isinstance(exc_info[1], cls)
                except Exception:
                    is_inst = False

                if is_inst:
                    return real_func(event, exc_info)
                return event

        self._error_processors.append(func)

    @_disable_capture
    def apply_to_event(self, event, hint = None):

        def _drop(event, cause, ty):
            logger.info('%s (%s) dropped event (%s)', ty, cause, event)

        if self._level is not None:
            event['level'] = self._level
        event.setdefault('breadcrumbs', []).extend(self._breadcrumbs)
        if event.get('user') is None and self._user is not None:
            event['user'] = self._user
        if event.get('transaction') is None and self._transaction is not None:
            event['transaction'] = self._transaction
        if event.get('fingerprint') is None and self._fingerprint is not None:
            event['fingerprint'] = self._fingerprint
        if self._extras:
            event.setdefault('extra', {}).update(self._extras)
        if self._tags:
            event.setdefault('tags', {}).update(self._tags)
        if self._contexts:
            event.setdefault('contexts', {}).update(self._contexts)
        if self._span is not None:
            event.setdefault('contexts', {})['trace'] = {'trace_id': self._span.trace_id,
             'span_id': self._span.span_id}
        exc_info = hint.get('exc_info') if hint is not None else None
        if exc_info is not None:
            for processor in self._error_processors:
                new_event = processor(event, exc_info)
                if new_event is None:
                    return _drop(event, processor, 'error processor')
                event = new_event

        for processor in chain(global_event_processors, self._event_processors):
            new_event = event
            with capture_internal_exceptions():
                new_event = processor(event, hint)
            if new_event is None:
                return _drop(event, processor, 'event processor')
            event = new_event

        return event

    def __copy__(self):
        rv = object.__new__(self.__class__)
        rv._level = self._level
        rv._name = self._name
        rv._fingerprint = self._fingerprint
        rv._transaction = self._transaction
        rv._user = self._user
        rv._tags = dict(self._tags)
        rv._contexts = dict(self._contexts)
        rv._extras = dict(self._extras)
        rv._breadcrumbs = copy(self._breadcrumbs)
        rv._event_processors = list(self._event_processors)
        rv._error_processors = list(self._error_processors)
        rv._should_capture = self._should_capture
        rv._span = self._span
        return rv

    def __repr__(self):
        return '<%s id=%s name=%s>' % (self.__class__.__name__, hex(id(self)), self._name)
