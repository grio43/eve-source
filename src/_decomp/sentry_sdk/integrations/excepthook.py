#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sentry_sdk\integrations\excepthook.py
import sys
from sentry_sdk.hub import Hub
from sentry_sdk.utils import capture_internal_exceptions, event_from_exception
from sentry_sdk.integrations import Integration
if False:
    from typing import Callable

class ExcepthookIntegration(Integration):
    identifier = 'excepthook'
    always_run = False

    def __init__(self, always_run = False):
        if not isinstance(always_run, bool):
            raise ValueError('Invalid value for always_run: %s (must be type boolean)' % (always_run,))
        self.always_run = always_run

    @staticmethod
    def setup_once():
        sys.excepthook = _make_excepthook(sys.excepthook)


def _make_excepthook(old_excepthook):

    def sentry_sdk_excepthook(exctype, value, traceback):
        hub = Hub.current
        integration = hub.get_integration(ExcepthookIntegration)
        if integration is not None and _should_send(integration.always_run):
            with capture_internal_exceptions():
                event, hint = event_from_exception((exctype, value, traceback), client_options=hub.client.options, mechanism={'type': 'excepthook',
                 'handled': False})
                hub.capture_event(event, hint=hint)
        return old_excepthook(exctype, value, traceback)

    return sentry_sdk_excepthook


def _should_send(always_run = False):
    if always_run:
        return True
    if hasattr(sys, 'ps1'):
        return False
    return True
