#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithsentry\transport.py
from sentry_sdk.transport import Transport
from sentry_sdk.consts import VERSION
import requests
import logging
import json
from uthread2 import StartTasklet
logger = logging.getLogger(__name__)

class RequestsSessionTransport(Transport):

    def __init__(self, options):
        Transport.__init__(self, options)
        self.options = options
        self.session = requests.Session()
        self._auth = self.parsed_dsn.to_auth('sentry.python/%s' % VERSION)

    def capture_event(self, event):
        StartTasklet(self._send, event)

    def _send(self, event):
        headers = {'X-Sentry-Auth': str(self._auth.to_header()),
         'Content-Type': 'application/json'}
        data = json.dumps(event).encode('utf-8')
        try:
            self.session.post(str(self._auth.store_api_url), data=data, headers=headers)
        except Exception as e:
            logger.warn('Sentry send failed: {0}'.format(e))

    def flush(self, timeout, callback = None):
        pass

    def kill(self):
        pass

    def __del__(self):
        try:
            self.kill()
        except Exception:
            pass
