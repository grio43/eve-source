#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sentry_sdk\api.py
import inspect
from contextlib import contextmanager
from sentry_sdk.hub import Hub
from sentry_sdk.scope import Scope
if False:
    from typing import Any
    from typing import Optional
    from typing import overload
    from typing import Callable
    from typing import Dict
    from contextlib import ContextManager
else:

    def overload(x):
        return x


__all__ = []

def public(f):
    __all__.append(f.__name__)
    return f


def hubmethod(f):
    f.__doc__ = '%s\n\n%s' % ('Alias for `Hub.%s`' % f.__name__, inspect.getdoc(getattr(Hub, f.__name__)))
    return public(f)


@hubmethod
def capture_event(event, hint = None):
    hub = Hub.current
    if hub is not None:
        return hub.capture_event(event, hint)


@hubmethod
def capture_message(message, level = None):
    hub = Hub.current
    if hub is not None:
        return hub.capture_message(message, level)


@hubmethod
def capture_exception(error = None):
    hub = Hub.current
    if hub is not None:
        return hub.capture_exception(error)


@hubmethod
def add_breadcrumb(crumb = None, hint = None, **kwargs):
    hub = Hub.current
    if hub is not None:
        return hub.add_breadcrumb(crumb, hint, **kwargs)


@overload
def configure_scope():
    pass


@overload
def configure_scope(callback):
    pass


@hubmethod
def configure_scope(callback = None):
    hub = Hub.current
    if hub is not None:
        return hub.configure_scope(callback)
    elif callback is None:

        @contextmanager
        def inner():
            yield Scope()

        return inner()
    else:
        return


@overload
def push_scope():
    pass


@overload
def push_scope(callback):
    pass


@hubmethod
def push_scope(callback = None):
    hub = Hub.current
    if hub is not None:
        return hub.push_scope(callback)
    elif callback is None:

        @contextmanager
        def inner():
            yield Scope()

        return inner()
    else:
        return


@hubmethod
def flush(timeout = None, callback = None):
    hub = Hub.current
    if hub is not None:
        return hub.flush(timeout=timeout, callback=callback)


@hubmethod
def last_event_id():
    hub = Hub.current
    if hub is not None:
        return hub.last_event_id()
