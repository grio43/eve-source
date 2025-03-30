#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\launchdarkly\client\featureflag.py
import launchdarkly

def create_boolean_flag_check(launchdarkly_key, fallback_value, on_flag_changed_callback = None):
    boolean_flag = NotifyBooleanFlag(launchdarkly_key, fallback_value, on_flag_changed_callback)
    return boolean_flag.is_enabled


def create_integer_flag_check(launchdarkly_key, fallback_value, on_flag_changed_callback = None):
    integer_flag = NotifyIntegerFlag(launchdarkly_key, fallback_value, on_flag_changed_callback)
    return integer_flag.get_value


def create_string_flag_check(launchdarkly_key, fallback_value, on_flag_changed_callback = None):
    string_flag = NotifyStringFlag(launchdarkly_key, fallback_value, on_flag_changed_callback)
    return string_flag.get_value


def create_float_flag_check(launchdarkly_key, fallback_value, on_flag_changed_callback = None):
    integer_flag = NotifyFloatFlag(launchdarkly_key, fallback_value, on_flag_changed_callback)
    return integer_flag.get_value


class BaseNotifyFlag(object):

    def __init__(self, launchdarkly_key, fallback_value, on_flag_changed_callback = None):
        self._value = None
        self._launchdarkly_key = launchdarkly_key
        self._fallback_value = fallback_value
        self._on_flag_changed_callback = on_flag_changed_callback

    def _get_value_from_launchdarkly_client(self, ld_client, flag_key, flag_fallback):
        raise NotImplementedError('Must implement getter in derived class for the specific type of flag')

    def _get_launchdarkly_client(self):
        return launchdarkly.get_client()

    def get_value(self):
        if self._value is None:
            self._get_launchdarkly_client().notify_flag(flag_key=self._launchdarkly_key, flag_fallback=self._fallback_value, callback=self._update_state)
        return self._value

    def _update_state(self, ld_client, flag_key, flag_fallback, flag_deleted):
        old_value = self._value
        self._value = self._get_value_from_launchdarkly_client(ld_client, flag_key, flag_fallback)
        if old_value is not None and old_value != self._value:
            self.on_flag_changed(old_value=old_value, new_value=self._value)

    def on_flag_changed(self, old_value, new_value):
        if callable(self._on_flag_changed_callback):
            self._on_flag_changed_callback(old_value, new_value)


class NotifyBooleanFlag(BaseNotifyFlag):

    def is_enabled(self):
        return self.get_value()

    def _get_value_from_launchdarkly_client(self, ld_client, flag_key, flag_fallback):
        return ld_client.get_bool_variation(feature_key=flag_key, fallback=flag_fallback)


class NotifyIntegerFlag(BaseNotifyFlag):

    def _get_value_from_launchdarkly_client(self, ld_client, flag_key, flag_fallback):
        return ld_client.get_int_variation(feature_key=flag_key, fallback=flag_fallback)


class NotifyStringFlag(BaseNotifyFlag):

    def _get_value_from_launchdarkly_client(self, ld_client, flag_key, flag_fallback):
        return ld_client.get_string_variation(feature_key=flag_key, fallback=flag_fallback)


class NotifyFloatFlag(BaseNotifyFlag):

    def _get_value_from_launchdarkly_client(self, ld_client, flag_key, flag_fallback):
        return ld_client.get_double_variation(feature_key=flag_key, fallback=flag_fallback)
