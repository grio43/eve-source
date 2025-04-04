#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sentry_sdk\__init__.py
from sentry_sdk.hub import Hub, init
from sentry_sdk.scope import Scope
from sentry_sdk.transport import Transport, HttpTransport
from sentry_sdk.client import Client
from sentry_sdk.api import *
from sentry_sdk.api import __all__ as api_all
from sentry_sdk.consts import VERSION
__all__ = api_all + ['Hub',
 'Scope',
 'Client',
 'Transport',
 'HttpTransport',
 'init',
 'integrations']
from sentry_sdk.debug import init_debug_support
init_debug_support()
del init_debug_support
