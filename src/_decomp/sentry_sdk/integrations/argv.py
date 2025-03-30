#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sentry_sdk\integrations\argv.py
from __future__ import absolute_import
import sys
from sentry_sdk.hub import Hub
from sentry_sdk.integrations import Integration
from sentry_sdk.scope import add_global_event_processor
if False:
    from typing import Any
    from typing import Dict

class ArgvIntegration(Integration):
    identifier = 'argv'

    @staticmethod
    def setup_once():

        @add_global_event_processor
        def processor(event, hint):
            if Hub.current.get_integration(ArgvIntegration) is not None:
                extra = event.setdefault('extra', {})
                if isinstance(extra, dict):
                    extra['sys.argv'] = sys.argv
            return event
