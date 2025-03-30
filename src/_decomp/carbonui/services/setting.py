#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\services\setting.py
import uuid
from signals import Signal

class _UserSettingMixin(object):

    @property
    def settings_path(self):
        return settings.user.ui


class _CharSettingMixin(object):

    @property
    def settings_path(self):
        return settings.char.ui


class _PublicSettingMixin(object):

    @property
    def settings_path(self):
        return settings.public.ui


class _DeviceSettingMixin(object):

    @property
    def settings_path(self):
        return settings.public.device


class _AudioSettingMixin(object):

    @property
    def settings_path(self):
        return settings.public.audio


class _WindowSettingMixin(object):

    @property
    def settings_path(self):
        return settings.char.windows


class _SuppressSettingMixin(object):

    @property
    def settings_path(self):
        return settings.user.suppress


class _BaseSetting(object):

    def __init__(self, settings_key, default_value):
        super(_BaseSetting, self).__init__()
        self.settings_key = settings_key
        self._default_value = default_value
        self.on_change = Signal('%s.on_change (%s)' % (self.__class__.__name__, self.settings_key))

    def get(self):
        return self.settings_path.Get(self.settings_key, self.get_default())

    def is_default(self):
        return self.is_equal(self.get_default())

    def get_default(self):
        if callable(self._default_value):
            return self._default_value()
        else:
            return self._default_value

    def is_equal(self, value):
        return value == self.get()

    def set(self, value):
        self._validate(value)
        if not self.is_equal(value):
            self._set(value)
            self._trigger_on_change(value)

    def _trigger_on_change(self, value):
        self.on_change(value)

    def _set(self, value):
        self.settings_path.Set(self.settings_key, value)

    def _validate(self, value):
        return True

    def reset(self):
        self.set(self.get_default())


class _BaseSettingEnum(_BaseSetting):

    def __init__(self, settings_key, default_value, options = None):
        super(_BaseSettingEnum, self).__init__(settings_key, default_value)
        self.options = tuple(options) if options else None

    def _validate(self, value):
        if self.options and value not in self.options:
            raise ValueError('Unexpected settings value %s (allowed values: %s)' % (value, repr(self.options)))


class _BaseSettingBool(_BaseSetting):

    def enable(self):
        self.set(True)

    def disable(self):
        self.set(False)

    def toggle(self):
        self.set(not self.is_enabled())

    def is_enabled(self):
        return self.get()


class _BaseSettingNumeric(_BaseSetting):

    def __init__(self, settings_key, default_value, min_value, max_value):
        super(_BaseSettingNumeric, self).__init__(settings_key, default_value)
        self.min_value = min_value
        self.max_value = max_value

    def _validate(self, value):
        if value < self.min_value:
            raise ValueError('Unexpected settings value %s (min_value=%s)' % (value, self.min_value))
        elif value > self.max_value:
            raise ValueError('Unexpected settings value %s (max_value=%s)' % (value, self.max_value))


class _BaseSettingString(_BaseSetting):
    pass


class _BaseSettingUUID(_BaseSetting):

    def __init__(self, settings_key, default_value):
        super(_BaseSettingUUID, self).__init__(settings_key, default_value)

    def _validate(self, value):
        if value is None:
            return True
        try:
            uuid.UUID(value)
        except ValueError:
            raise ValueError('Unexpected settings value %s (not a valid uuid) ' % value)

    def get(self):
        value = super(_BaseSettingUUID, self).get()
        if value is None:
            return
        else:
            return uuid.UUID(value)

    def set(self, value):
        strValue = str(value) if value is not None else None
        self._validate(strValue)
        self.settings_path.Set(self.settings_key, strValue)
        self.on_change(value)


class CharSettingBool(_BaseSettingBool, _CharSettingMixin):
    pass


class CharSettingNumeric(_BaseSettingNumeric, _CharSettingMixin):
    pass


class CharSettingEnum(_BaseSettingEnum, _CharSettingMixin):
    pass


class CharSettingString(_BaseSettingString, _CharSettingMixin):
    pass


class CharSettingUUID(_BaseSettingUUID, _CharSettingMixin):
    pass


class UserSettingBool(_BaseSettingBool, _UserSettingMixin):
    pass


class UserSettingNumeric(_BaseSettingNumeric, _UserSettingMixin):
    pass


class UserSettingEnum(_BaseSettingEnum, _UserSettingMixin):
    pass


class UserSettingString(_BaseSettingString, _UserSettingMixin):
    pass


class UserSettingUUID(_BaseSettingUUID, _UserSettingMixin):
    pass


class PublicSettingBool(_BaseSettingBool, _PublicSettingMixin):
    pass


class PublicSettingNumeric(_BaseSettingNumeric, _PublicSettingMixin):
    pass


class PublicSettingEnum(_BaseSettingEnum, _PublicSettingMixin):
    pass


class PublicSettingString(_BaseSettingString, _PublicSettingMixin):
    pass


class DeviceSettingBool(_BaseSettingBool, _DeviceSettingMixin):
    pass


class DeviceSettingEnum(_BaseSettingEnum, _DeviceSettingMixin):
    pass


class AudioSettingBool(_BaseSettingBool, _AudioSettingMixin):
    pass


class AudioSettingNumeric(_BaseSettingNumeric, _AudioSettingMixin):
    pass


class AudioSettingEnum(_BaseSettingEnum, _AudioSettingMixin):
    pass


class SuppressSettingBool(_BaseSettingBool, _SuppressSettingMixin):
    pass


class SessionSettingBool(_BaseSettingBool):

    def __init__(self, default_value):
        super(SessionSettingBool, self).__init__(None, default_value)
        self._value = default_value

    def _set(self, value):
        self._value = value

    def get(self):
        return self._value


class SessionSettingNumeric(_BaseSettingNumeric):

    def __init__(self, default_value, min_value, max_value):
        super(SessionSettingNumeric, self).__init__(None, default_value, min_value, max_value)
        self._value = default_value

    def _set(self, value):
        self._value = value

    def get(self):
        return self._value


class SessionSettingEnum(_BaseSettingEnum):

    def __init__(self, default_value, options = None):
        super(SessionSettingEnum, self).__init__(None, default_value, options=None)
        self._value = default_value

    def _set(self, value):
        self._value = value

    def get(self):
        return self._value
