#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sentry_sdk\transport.py
from __future__ import print_function
import json
import io
import urllib3
import certifi
import gzip
from datetime import datetime, timedelta
from sentry_sdk.consts import VERSION
from sentry_sdk.utils import Dsn, logger, capture_internal_exceptions
from sentry_sdk.worker import BackgroundWorker
if False:
    from sentry_sdk.consts import ClientOptions
    from typing import Type
    from typing import Any
    from typing import Optional
    from typing import Dict
    from typing import Union
    from typing import Callable
    from urllib3.poolmanager import PoolManager
    from urllib3.poolmanager import ProxyManager
try:
    from urllib.request import getproxies
except ImportError:
    from urllib import getproxies

class Transport(object):
    parsed_dsn = None

    def __init__(self, options = None):
        self.options = options
        if options and options['dsn']:
            self.parsed_dsn = Dsn(options['dsn'])
        else:
            self.parsed_dsn = None

    def capture_event(self, event):
        raise NotImplementedError()

    def flush(self, timeout, callback = None):
        pass

    def kill(self):
        pass

    def __del__(self):
        try:
            self.kill()
        except Exception:
            pass


class HttpTransport(Transport):

    def __init__(self, options):
        Transport.__init__(self, options)
        self._worker = BackgroundWorker()
        self._auth = self.parsed_dsn.to_auth('sentry.python/%s' % VERSION)
        self._disabled_until = None
        self._retry = urllib3.util.Retry()
        self.options = options
        self._pool = self._make_pool(self.parsed_dsn, http_proxy=options['http_proxy'], https_proxy=options['https_proxy'], ca_certs=options['ca_certs'])
        from sentry_sdk import Hub
        self.hub_cls = Hub

    def _send_event(self, event):
        if self._disabled_until is not None:
            if datetime.utcnow() < self._disabled_until:
                return
            self._disabled_until = None
        body = io.BytesIO()
        with gzip.GzipFile(fileobj=body, mode='w') as f:
            f.write(json.dumps(event, allow_nan=False).encode('utf-8'))
        logger.debug('Sending %s event [%s] to %s project:%s' % (event.get('level') or 'error',
         event['event_id'],
         self.parsed_dsn.host,
         self.parsed_dsn.project_id))
        response = self._pool.request('POST', str(self._auth.store_api_url), body=body.getvalue(), headers={'X-Sentry-Auth': str(self._auth.to_header()),
         'Content-Type': 'application/json',
         'Content-Encoding': 'gzip'})
        try:
            if response.status == 429:
                self._disabled_until = datetime.utcnow() + timedelta(seconds=self._retry.get_retry_after(response) or 60)
                return
            if response.status >= 300 or response.status < 200:
                logger.error('Unexpected status code: %s (body: %s)', response.status, response.data)
        finally:
            response.close()

        self._disabled_until = None

    def _get_pool_options(self, ca_certs):
        return {'num_pools': 2,
         'cert_reqs': 'CERT_REQUIRED',
         'ca_certs': ca_certs or certifi.where()}

    def _make_pool(self, parsed_dsn, http_proxy, https_proxy, ca_certs):
        proxy = None
        if parsed_dsn.scheme == 'https' and https_proxy != '':
            proxy = https_proxy or getproxies().get('https')
        if not proxy and http_proxy != '':
            proxy = http_proxy or getproxies().get('http')
        opts = self._get_pool_options(ca_certs)
        if proxy:
            return urllib3.ProxyManager(proxy, **opts)
        else:
            return urllib3.PoolManager(**opts)

    def capture_event(self, event):
        hub = self.hub_cls.current

        def send_event_wrapper():
            with hub:
                with capture_internal_exceptions():
                    self._send_event(event)

        self._worker.submit(send_event_wrapper)

    def flush(self, timeout, callback = None):
        logger.debug('Flushing HTTP transport')
        if timeout > 0:
            self._worker.flush(timeout, callback)

    def kill(self):
        logger.debug('Killing HTTP transport')
        self._worker.kill()


class _FunctionTransport(Transport):

    def __init__(self, func):
        Transport.__init__(self)
        self._func = func

    def capture_event(self, event):
        self._func(event)


def make_transport(options):
    ref_transport = options['transport']
    if ref_transport is None:
        transport_cls = HttpTransport
    else:
        try:
            issubclass(ref_transport, type)
        except TypeError:
            if callable(ref_transport):
                return _FunctionTransport(ref_transport)
            return ref_transport

        transport_cls = ref_transport
    if options['dsn']:
        return transport_cls(options)
