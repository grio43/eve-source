#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sentry_sdk\integrations\modules.py
from __future__ import absolute_import
from sentry_sdk.hub import Hub
from sentry_sdk.integrations import Integration
from sentry_sdk.scope import add_global_event_processor
if False:
    from typing import Any
    from typing import Dict
    from typing import Tuple
    from typing import Iterator
_installed_modules = None

def _generate_installed_modules():
    try:
        import pkg_resources
    except ImportError:
        return

    for info in pkg_resources.working_set:
        yield (info.key, info.version)


def _get_installed_modules():
    global _installed_modules
    if _installed_modules is None:
        _installed_modules = dict(_generate_installed_modules())
    return _installed_modules


class ModulesIntegration(Integration):
    identifier = 'modules'

    @staticmethod
    def setup_once():

        @add_global_event_processor
        def processor(event, hint):
            if Hub.current.get_integration(ModulesIntegration) is not None:
                event['modules'] = dict(_get_installed_modules())
            return event
