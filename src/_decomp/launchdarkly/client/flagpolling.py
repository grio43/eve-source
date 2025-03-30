#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\launchdarkly\client\flagpolling.py
import json
from collections import defaultdict
import uthread2

class FlagPolling:

    def __init__(self, client, logger, polling_seconds = 1):
        self.client = client
        self.logger = logger
        self.flag_state = defaultdict(object)
        self.flag_callbacks = defaultdict(list)
        self.polling_seconds = polling_seconds
        uthread2.StartTasklet(self._poll_flags)

    def _poll_flags(self):
        while self.client:
            if not self.client.is_initialized():
                uthread2.sleep(1)
                continue
            try:
                json_flags = self.client.all_flags()
                flags = json.loads(json_flags)
            except:
                self.logger.exception('failed to get all flags')
                uthread2.sleep(self.polling_seconds)
                continue

            for key, variation in flags.items():
                if key not in self.flag_state.keys():
                    self.logger.debug('new flag: %s', key)
                    self.flag_state[key] = variation
                    self._change_detected(key, False)
                    continue
                if self.flag_state[key] != variation:
                    self.logger.debug('flag changed (key=%s old=%s new=%s)', key, self.flag_state[key], variation)
                    self.flag_state[key] = variation
                    self._change_detected(key, False)
                    continue

            for key in self.flag_state.keys():
                if key not in flags.keys():
                    self.logger.debug('flag deleted: %s', key)
                    del self.flag_state[key]
                    self._change_detected(key, True)

            uthread2.sleep(self.polling_seconds)

    def _change_detected(self, flag_key, deleted):
        for callback, fallback in self.flag_callbacks[flag_key]:
            self._trigger_callback(callback, flag_key, fallback, deleted)

    @staticmethod
    def _get_callback_tuple(flag_fallback, callback):
        return (callback, flag_fallback)

    def _trigger_callback(self, callback, flag_key, flag_fallback, flag_deleted, with_tasklet = True):
        try:
            if with_tasklet:
                uthread2.StartTasklet(callback, self.client, flag_key, flag_fallback, flag_deleted)
            else:
                callback(self.client, flag_key, flag_fallback, flag_deleted)
        except Exception as e:
            self.logger.exception('failed to trigger callback for flag (%s)', flag_key)

    def notify_flag(self, flag_key, flag_fallback, callback):
        if not flag_key:
            raise ValueError('flag_key cannot be empty')
        if not callable(callback):
            raise TypeError('callback must be callable')
        callback_tuple = self._get_callback_tuple(flag_fallback, callback)
        if callback_tuple in self.flag_callbacks[flag_key]:
            self.logger.warn('attempted duplicate callback registration: %s', callback)
            return
        self.flag_callbacks[flag_key].append((callback, flag_fallback))
        self.logger.debug('subscribed to %s', flag_key)
        self._trigger_callback(callback, flag_key, flag_fallback, False, with_tasklet=False)

    def cancel_notify_flag(self, flag_key, flag_fallback, callback):
        callback_tuple = self._get_callback_tuple(flag_fallback, callback)
        if callback_tuple not in self.flag_callbacks[flag_key]:
            return
        index = self.flag_callbacks[flag_key].index(callback_tuple)
        del self.flag_callbacks[flag_key][index]
