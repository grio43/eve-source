#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\settings.py
import functools
import localization
import logging
import weakref
import signals
from carbonui.observable import Observable
from carbonui.services.setting import CharSettingBool, UserSettingEnum, _BaseSettingBool, _WindowSettingMixin
from carbonui.text.settings import is_new_font_size_options_enabled, migrate_existing_font_size_settings_down_one_size
logger = logging.getLogger('windowSettings')
only_tint_active_window = CharSettingBool(settings_key='only_tint_active_window', default_value=True)
window_compact_mode_default_setting = CharSettingBool(settings_key='window_compact_mode_default', default_value=False)
COMPACT_MODE_BY_WINDOW_ID_KEY = 'compactWindows'

class WindowCompactModeSetting(_WindowSettingMixin, _BaseSettingBool):
    __instances = weakref.WeakSet()

    def __init__(self, window_id, default_value):
        if isinstance(window_id, tuple):
            window_id = window_id[0]
        super(WindowCompactModeSetting, self).__init__(settings_key=window_id, default_value=default_value)
        self.__instances.add(self)
        window_compact_mode_default_setting.on_change.connect(self._on_default_changed)

    @classmethod
    def clear_all(cls):
        for setting in set(cls.__instances):
            setting.clear()

    def get(self):
        if self.settings_key is None:
            return self.get_default()
        else:
            value = self._get()
            if value is None:
                return self.get_default()
            return value

    def _get(self):
        compact_mode_by_window_id = self.settings_path.Get(COMPACT_MODE_BY_WINDOW_ID_KEY, {})
        return compact_mode_by_window_id.get(self.settings_key, None)

    def _on_default_changed(self, value):
        stored_value = self._get()
        if stored_value is None:
            self._trigger_on_change(self.get_default())

    def _set(self, value):
        compact_mode_by_window_id = self.settings_path.Get(COMPACT_MODE_BY_WINDOW_ID_KEY, {})
        if value == self.get_default():
            try:
                compact_mode_by_window_id.pop(self.settings_key)
            except KeyError:
                pass

        else:
            compact_mode_by_window_id[self.settings_key] = value
        self.settings_path.Set(COMPACT_MODE_BY_WINDOW_ID_KEY, compact_mode_by_window_id)

    def clear(self):
        compact_mode_by_window_id = self.settings_path.Get(COMPACT_MODE_BY_WINDOW_ID_KEY, {})
        if self.settings_key in compact_mode_by_window_id:
            value = compact_mode_by_window_id.pop(self.settings_key)
            self.settings_path.Set(COMPACT_MODE_BY_WINDOW_ID_KEY, compact_mode_by_window_id)
            default = self.get_default()
            if value != default:
                self._trigger_on_change(default)


class WindowMarginMode(object):
    NORMAL = 1
    COMPACT = 2


class WindowMarginModeOption(object):
    AUTO = 0
    NORMAL = 1
    COMPACT = 2
    _ALL = (AUTO, NORMAL, COMPACT)
    _NAME_LABEL_BY_VALUE = {AUTO: 'UI/SystemMenu/GeneralSettings/Windows/WindowMarginModeAutoTitle',
     NORMAL: 'UI/SystemMenu/GeneralSettings/Windows/WindowMarginModeNormalTitle',
     COMPACT: 'UI/SystemMenu/GeneralSettings/Windows/WindowMarginModeCompactTitle'}
    _HINT_LABEL_BY_VALUE = {AUTO: 'UI/SystemMenu/GeneralSettings/Windows/WindowMarginModeAutoHint',
     NORMAL: None,
     COMPACT: None}
    _SORT_KEY_BY_VALUE = {AUTO: 0,
     NORMAL: 1,
     COMPACT: 2}

    @classmethod
    def iter(cls):
        return iter(cls._ALL)

    @classmethod
    def get_name(cls, value):
        return localization.GetByLabel(cls._NAME_LABEL_BY_VALUE[value])

    @classmethod
    def get_hint(cls, value):
        hint_label = cls._HINT_LABEL_BY_VALUE[value]
        if hint_label is not None:
            return localization.GetByLabel(hint_label)

    @classmethod
    def get_sort_key(cls, value):
        return cls._SORT_KEY_BY_VALUE[value]


class WindowMarginModeStorage(Observable):
    DEFAULT_WINDOW_MARGIN_MODE = WindowMarginMode.NORMAL

    def __init__(self):
        self.setting = UserSettingEnum(settings_key='window_margin_mode', options=list(WindowMarginModeOption.iter()), default_value=WindowMarginModeOption.AUTO)
        self._get_resolution = None
        self._on_changed = signals.Signal('{}.on_changed'.format(self.__class__.__name__))
        self._value = None
        self.setting.on_change.connect(self._on_setting_changed)

    @property
    def value(self):
        if self._value is None:
            self.refresh()
        return self._value

    @property
    def on_changed(self):
        return self._on_changed

    def initialize(self, get_resolution, service_manager):
        self._get_resolution = get_resolution
        service_manager.RegisterForNotifyEvent(self, 'OnEndChangeDevice')
        service_manager.RegisterForNotifyEvent(self, 'OnSettingsLoaded')
        self.refresh()

    def refresh(self):
        old_value = self._value
        self._value = self._resolve()
        if old_value is not None and old_value != self._value:
            self._on_changed(self)

    def _resolve(self):
        mode = self.setting.get()
        if mode == WindowMarginModeOption.AUTO:
            if self._get_resolution is not None:
                width, height = self._get_resolution()
                if height < 1080:
                    return WindowMarginMode.COMPACT
                else:
                    return WindowMarginMode.NORMAL
            else:
                return self.DEFAULT_WINDOW_MARGIN_MODE
        else:
            if mode == WindowMarginModeOption.NORMAL:
                return WindowMarginMode.NORMAL
            if mode == WindowMarginModeOption.COMPACT:
                return WindowMarginMode.COMPACT

    def _on_setting_changed(self, value):
        self.refresh()

    def OnEndChangeDevice(self):
        self.refresh()

    def OnSettingsLoaded(self):
        self.refresh()


window_margin_mode = WindowMarginModeStorage()

def GetRegisteredState(windowID, statename, default = None):
    if windowID is None:
        return 0
    if type(windowID) == tuple:
        windowID, _ = windowID
    settingsByWindowID = settings.char.windows.Get('%sWindows' % statename, {})
    if windowID in settingsByWindowID:
        return settingsByWindowID[windowID]
    else:
        return default


def RegisterState(windowID, statename, value):
    if windowID is None:
        return
    if type(windowID) == tuple:
        windowID, subWindowID = windowID
    key = '%sWindows' % statename
    settingsByWindowID = settings.char.windows.Get(key, {})
    settingsByWindowID[windowID] = value
    settings.char.windows.Set(key, settingsByWindowID)


def GetSettingsVersion():
    return 1


def ValidateSettings(user_id, char_id):
    logger.info('Validate Window Settings, user: %s, char: %s', user_id, char_id)
    reset_window_settings_if_outdated()
    migrate = functools.partial(run_migration, user_id=user_id, char_id=char_id)
    migrate(migrate_window_settings_from_user_to_char)
    migrate(clear_stored_compact_window_settings_that_match_the_default, ignore_failure=True)
    if is_new_font_size_options_enabled():
        migrate(migrate_existing_font_size_settings_down_one_size, ignore_failure=True)


def run_migration(migration, user_id = None, char_id = None, ignore_failure = False):
    logger.info('Running settings migration: {}'.format(getattr(migration, '__name__', 'unknown')))
    try:
        migration(user_id, char_id)
    except Exception:
        if ignore_failure:
            logger.exception('Settings migration failed')
        else:
            raise


def migrate_window_settings_from_user_to_char(user_id, char_id):
    if not settings.char.windows.Get('__usercopy__', False):
        oldUserSettings = settings.user.windows.GetValues()
        logger.info('CONVERTING SETTINGS FROM USER TO CHAR userID=%s, charID=%s, settings:%s', user_id, char_id, oldUserSettings.keys())
        for settingKey in oldUserSettings.keys():
            oldValue = settings.user.windows.Get(settingKey)
            settings.char.windows.Set(settingKey, oldValue)

        settings.char.windows.Set('__usercopy__', True)


def clear_stored_compact_window_settings_that_match_the_default(user_id, char_id):
    if char_id is None:
        return
    migration_flag = '__clear_stored_compact_window_settings_that_match_the_default__'
    if settings.char.windows.Get(migration_flag, False):
        return
    migrated = {}
    compact_mode_by_window_id = settings.char.windows.Get(COMPACT_MODE_BY_WINDOW_ID_KEY, {})
    for window_id, compact_mode in compact_mode_by_window_id.items():
        if compact_mode:
            migrated[window_id] = compact_mode

    settings.char.windows.Set(COMPACT_MODE_BY_WINDOW_ID_KEY, migrated)
    settings.char.windows.Set(migration_flag, True)


def reset_window_settings_if_outdated():
    version = GetSettingsVersion()
    if settings.char.windows.Get('__version__', None) != version:
        ResetAllWindowSettings()


def ResetAllWindowSettings():
    settings.char.Remove('windows')
    version = GetSettingsVersion()
    logger.info('Starting new window settings with version=%s', version)
    settings.char.windows.Set('__version__', version)
    settings.char.windows.Set('__usercopy__', True)
