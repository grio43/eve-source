#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\launchdarkly\client\client_sdk.py
import logging
import json
from launchdarkly.logparser import LogParser
from launchdarkly.client.flagpolling import FlagPolling

def get_sdk_key():
    import monolithconfig
    import launchdarkly.client.const as keys
    tier = monolithconfig.get_client_tier()
    if tier == 'dev':
        return keys.DEV_KEY
    elif tier == 'test':
        return keys.TEST_KEY
    elif tier == 'live':
        return keys.LIVE_KEY
    else:
        return keys.PLAYGROUND_KEY


class Client(FlagPolling, LogParser):

    def __init__(self, sdk, sdk_key, tenant, eve_user = None):
        self.logger = logging.getLogger(__name__)
        self.native_sdk = sdk
        self._eve_user_id = eve_user
        self._ld_user_key = None
        self._tenant = tenant
        self._eve_character_id = None
        self._client_language = None
        self.last_attributes = {}
        default_ld_user = sdk.User('anon')
        default_ld_user.enable_anonymous()
        client_config = self.native_sdk.Config(sdk_key)
        self.native_client = self.native_sdk.Client(client_config, default_ld_user)
        self.logger.info('client created')
        self._set_ld_user_attributes(default_ld_user)
        LogParser.__init__(self, sdk=sdk, client=self.native_client, logger=self.logger)
        FlagPolling.__init__(self, client=self.native_client, logger=self.logger)

    def __getattr__(self, name):
        return getattr(self.native_client, name)

    def _set_ld_user_attributes(self, ld_user):
        self.last_attributes = {'characterID': self._eve_character_id,
         'userID': self._eve_user_id,
         'languageID': self._client_language,
         'tenant': self._tenant}
        ld_user.set_custom_attributes_json(json.dumps(self.last_attributes))
        self.logger.debug('LD user attributes updated: %s', self.last_attributes)

    def character_select(self, user_id, character_id, language_id):
        self._eve_user_id = user_id
        self._client_language = language_id
        self._eve_character_id = character_id
        self._ld_user_key = character_id
        self._update_ld_user()

    def _update_ld_user(self):
        ld_user = self.native_sdk.User(str(self._ld_user_key))
        self._set_ld_user_attributes(ld_user)
        self.native_client.identify(ld_user)
        self.native_client.await_initialized(500)

    def release(self):
        self.native_client.release()
