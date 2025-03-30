#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sentry_sdk\integrations\__init__.py
from __future__ import absolute_import
from threading import Lock
from sentry_sdk._compat import iteritems
from sentry_sdk.utils import logger
if False:
    from typing import Iterator
    from typing import Dict
    from typing import List
    from typing import Set
    from typing import Type
    from typing import Callable
_installer_lock = Lock()
_installed_integrations = set()

def nope():
    return []


iter_default_integrations = nope

def setup_integrations(integrations, with_defaults = True):
    integrations = dict(((integration.identifier, integration) for integration in integrations or ()))
    logger.debug('Setting up integrations (with default = %s)', with_defaults)
    if with_defaults:
        for integration_cls in iter_default_integrations():
            if integration_cls.identifier not in integrations:
                instance = integration_cls()
                integrations[instance.identifier] = instance

    for identifier, integration in iteritems(integrations):
        with _installer_lock:
            if identifier not in _installed_integrations:
                logger.debug('Setting up previously not enabled integration %s', identifier)
                try:
                    type(integration).setup_once()
                except NotImplementedError:
                    if getattr(integration, 'install', None) is not None:
                        logger.warn('Integration %s: The install method is deprecated. Use `setup_once`.', identifier)
                        integration.install()
                    else:
                        raise

                _installed_integrations.add(identifier)

    for identifier in integrations:
        logger.debug('Enabling integration %s', identifier)

    return integrations


class Integration(object):
    install = None
    identifier = None

    @staticmethod
    def setup_once():
        raise NotImplementedError()
