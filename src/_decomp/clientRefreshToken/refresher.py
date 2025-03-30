#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\clientRefreshToken\refresher.py
import uthread2
import requests
import datetime
import logging
from discovery_hacks import discover_refresh_parameters_from_user_token
logger = logging.getLogger(__name__)

class Refresher(object):

    def __init__(self, initial_user_token_payload, initial_refresh_token):
        client_id, token_endpoint = discover_refresh_parameters_from_user_token(initial_user_token_payload)
        self.client_id = client_id
        self.refresh_token = initial_refresh_token
        self.token_endpoint = token_endpoint
        self.access_token = None
        self.expires = None
        self.callbacks = []
        uthread2.StartTasklet(self._maintain_fresh_token)

    def _maintain_fresh_token(self):
        while True:
            try:
                self._refresh()
                self.broadcast(self.access_token)
                uthread2.sleep(self.expires - 90)
            except requests.HTTPError as http_error:
                reportHTTPError(http_error, message='token refresh request failed')
            except Exception as e:
                logger.exception('refreshing access token failed')
            finally:
                uthread2.sleep(1)

    def add_callback(self, callback):
        if not callable(callback):
            logger.warning('callback not callable: %s', callback)
            return
        self.callbacks.append(callback)
        callback(self.access_token)

    def broadcast(self, *args):
        for callback in self.callbacks:
            callback(*args)

    def _refresh(self):
        body = {'grant_type': 'refresh_token',
         'client_id': self.client_id,
         'refresh_token': self.refresh_token}
        response = requests.post(self.token_endpoint, data=body)
        response.raise_for_status()
        content = response.json()
        access_token = content['access_token']
        if not access_token:
            raise RuntimeError('access token empty on refresh')
        refresh_token = content['refresh_token']
        if not refresh_token:
            raise RuntimeError('refresh token empty on refresh')
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires = content['expires_in']
        logger.debug('token refreshed, expires in %s', datetime.timedelta(seconds=self.expires))


def reportHTTPError(http_error, message = ''):
    extra = dict()
    try:
        resp_data = http_error.response.json()
        extra.update(resp_data)
    except ValueError:
        extra['response_content'] = str(http_error.response.content)

    if not message:
        message = str(http_error)
    logger.exception(message, extra=extra)
