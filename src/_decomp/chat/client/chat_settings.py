#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\client\chat_settings.py
import itertools
from carbonui.fontconst import EVE_MEDIUM_FONTSIZE
from carbonui.services.setting import _BaseSettingBool, _BaseSettingEnum, UserSettingBool, UserSettingEnum, UserSettingNumeric
from carbonui.text.settings import get_font_size_for_preset
from .const import AVAILABLE_FONT_SIZES, ChatMessageMode
OPEN_CHANNELS_SETTING_KEY = 'chatchannels'
elevated_chat_highlighting_setting = UserSettingBool(settings_key='chatHightlighting', default_value=False)
global_font_size_setting = UserSettingEnum(settings_key='chatWindowGlobalSize', default_value=None, options=itertools.chain([None], AVAILABLE_FONT_SIZES))
show_message_timestamp_setting = UserSettingBool(settings_key='timestampchat', default_value=False)
highlight_my_messages_setting = UserSettingBool(settings_key='myMsgHighlighted', default_value=False)
default_light_background_setting = UserSettingBool(settings_key='chat_light_background_default', default_value=True)
default_font_size_setting = UserSettingEnum(settings_key='chat_font_size_default', default_value=lambda : get_font_size_for_preset(EVE_MEDIUM_FONTSIZE), options=AVAILABLE_FONT_SIZES)
default_show_member_list_setting = UserSettingBool(settings_key='chat_show_member_list_default', default_value=True)
default_compact_member_entries_setting = UserSettingBool(settings_key='chat_compact_member_entries', default_value=False)
default_message_mode_setting = UserSettingEnum(settings_key='chat_message_mode_default', default_value=ChatMessageMode.SMALL_PORTRAIT, options=(ChatMessageMode.TEXT_ONLY, ChatMessageMode.SMALL_PORTRAIT, ChatMessageMode.LARGE_PORTRAIT))
auto_collapse_messages = UserSettingBool(settings_key='chat_auto_collapse_messages', default_value=False)
auto_collapse_message_lines = UserSettingNumeric(settings_key='chat_auto_collapse_message_lines', default_value=5, min_value=2, max_value=10)

class ApplyFontSizeGloballySetting(_BaseSettingBool):

    def __init__(self, font_size_setting):
        self._font_size_setting = font_size_setting
        super(ApplyFontSizeGloballySetting, self).__init__(settings_key=None, default_value=False)

    def get(self):
        return global_font_size_setting.get() is not None

    def _set(self, value):
        if value:
            global_font_size_setting.set(self._font_size_setting.get())
        else:
            global_font_size_setting.set(None)


class EffectiveFontSizeSetting(_BaseSettingEnum):

    def __init__(self, font_size_setting):
        self._font_size_setting = font_size_setting
        super(EffectiveFontSizeSetting, self).__init__(settings_key=None, default_value=self._get_default_font_size, options=font_size_setting.options)
        font_size_setting.on_change.connect(self._on_font_size_changed)
        global_font_size_setting.on_change.connect(self._on_global_font_size_changed)

    def get(self):
        global_font_size = global_font_size_setting.get()
        if global_font_size is not None:
            return global_font_size
        else:
            return self._font_size_setting.get()

    def _set(self, value):
        if global_font_size_setting.get() is None:
            self._font_size_setting.set(value)
        else:
            global_font_size_setting.set(value)

    def _get_default_font_size(self):
        return self._font_size_setting.get_default()

    def _on_font_size_changed(self, value):
        self._trigger_on_change(self.get())

    def _on_global_font_size_changed(self, value):
        self._trigger_on_change(self.get())
