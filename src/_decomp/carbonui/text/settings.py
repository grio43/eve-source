#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\text\settings.py
from carbonui import fontconst
from carbonui.services.setting import CharSettingBool
font_shadow_enabled_setting = CharSettingBool(settings_key='global_font_shadow_enabled', default_value=True)

class FontSizeOption(object):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    EXTRA_SMALL = 4
    EXTRA_LARGE = 5


def get_font_size_setting():
    return settings.public.ui.Get('clientFontSize', get_default_font_size_setting(session.languageID))


def set_font_size_setting(value):
    current_value = settings.public.ui.Get('clientFontSize')
    if current_value != value:
        settings.public.ui.Set('clientFontSize', value)
        _notify_font_size_changed()


def _notify_font_size_changed():
    update_font_size_factor()
    sm.ScatterEvent('OnFontSizeChanged')


def update_font_size_factor():
    fontconst.fontSizeFactor = get_font_size_factor()


def get_font_size_factor():
    setting = get_font_size_setting()
    if setting == FontSizeOption.EXTRA_LARGE:
        return 1.3
    elif setting == FontSizeOption.LARGE:
        return 1.2
    elif setting == FontSizeOption.MEDIUM:
        return 1.1
    else:
        return 1.0


def get_font_size_for_preset(font_size_preset):
    selected_font_size_option = get_font_size_setting()
    font_sizes_by_setting = _get_font_sizes_by_setting()
    font_sizes = font_sizes_by_setting.get(selected_font_size_option)
    if font_sizes is None:
        font_sizes = font_sizes_by_setting[FontSizeOption.MEDIUM]
    return font_sizes[font_size_preset]


def check_convert_font_size(fontsize):
    if fontsize < 0:
        return get_font_size_for_preset(fontsize)
    else:
        return fontsize


_is_new_font_size_options_enabled = None
NEW_FONT_SIZE_OPTIONS_ENABLED_KEY = 'pathfinder-new-font-size-options-available'
NEW_FONT_SIZE_OPTIONS_ENABLED_DEFAULT = False

def _update_new_font_size_options_enabled(ld_client, flag_key, flag_fallback, flag_deleted):
    global _is_new_font_size_options_enabled
    new_value = ld_client.get_bool_variation(feature_key=flag_key, fallback=flag_fallback)
    if _is_new_font_size_options_enabled != new_value:
        _is_new_font_size_options_enabled = new_value
        _handle_font_size_setting_feature_flag_changed()


def is_new_font_size_options_enabled():
    if _is_new_font_size_options_enabled is None:
        import launchdarkly
        launchdarkly.get_client().notify_flag(flag_key=NEW_FONT_SIZE_OPTIONS_ENABLED_KEY, flag_fallback=NEW_FONT_SIZE_OPTIONS_ENABLED_DEFAULT, callback=_update_new_font_size_options_enabled)
    return _is_new_font_size_options_enabled


def _get_font_sizes_by_setting():
    if is_new_font_size_options_enabled():
        return _NEW_FONT_SIZES_BY_SETTING
    else:
        return _OLD_FONT_SIZES_BY_SETTING


_OLD_FONT_SIZES_BY_SETTING = {FontSizeOption.SMALL: {fontconst.EVE_SMALL_FONTSIZE: 10,
                        fontconst.EVE_MEDIUM_FONTSIZE: 12,
                        fontconst.EVE_LARGE_FONTSIZE: 14,
                        fontconst.EVE_XLARGE_FONTSIZE: 17,
                        fontconst.EVE_DETAIL_FONTSIZE: 10,
                        fontconst.EVE_BODY_FONTSIZE: 12,
                        fontconst.EVE_HEADER_FONTSIZE: 16,
                        fontconst.EVE_HEADLINE_FONTSIZE: 22,
                        fontconst.EVE_DISPLAY_FONTSIZE: 39},
 FontSizeOption.MEDIUM: {fontconst.EVE_SMALL_FONTSIZE: 11,
                         fontconst.EVE_MEDIUM_FONTSIZE: 13,
                         fontconst.EVE_LARGE_FONTSIZE: 15,
                         fontconst.EVE_XLARGE_FONTSIZE: 18,
                         fontconst.EVE_DETAIL_FONTSIZE: 11,
                         fontconst.EVE_BODY_FONTSIZE: 13,
                         fontconst.EVE_HEADER_FONTSIZE: 17,
                         fontconst.EVE_HEADLINE_FONTSIZE: 23,
                         fontconst.EVE_DISPLAY_FONTSIZE: 40},
 FontSizeOption.LARGE: {fontconst.EVE_SMALL_FONTSIZE: 12,
                        fontconst.EVE_MEDIUM_FONTSIZE: 14,
                        fontconst.EVE_LARGE_FONTSIZE: 16,
                        fontconst.EVE_XLARGE_FONTSIZE: 19,
                        fontconst.EVE_DETAIL_FONTSIZE: 12,
                        fontconst.EVE_BODY_FONTSIZE: 14,
                        fontconst.EVE_HEADER_FONTSIZE: 18,
                        fontconst.EVE_HEADLINE_FONTSIZE: 24,
                        fontconst.EVE_DISPLAY_FONTSIZE: 41}}
_NEW_FONT_SIZES_BY_SETTING = {FontSizeOption.EXTRA_SMALL: {fontconst.EVE_SMALL_FONTSIZE: 10,
                              fontconst.EVE_MEDIUM_FONTSIZE: 12,
                              fontconst.EVE_LARGE_FONTSIZE: 14,
                              fontconst.EVE_XLARGE_FONTSIZE: 17,
                              fontconst.EVE_DETAIL_FONTSIZE: 10,
                              fontconst.EVE_BODY_FONTSIZE: 12,
                              fontconst.EVE_HEADER_FONTSIZE: 16,
                              fontconst.EVE_HEADLINE_FONTSIZE: 22,
                              fontconst.EVE_DISPLAY_FONTSIZE: 38},
 FontSizeOption.SMALL: {fontconst.EVE_SMALL_FONTSIZE: 11,
                        fontconst.EVE_MEDIUM_FONTSIZE: 13,
                        fontconst.EVE_LARGE_FONTSIZE: 15,
                        fontconst.EVE_XLARGE_FONTSIZE: 18,
                        fontconst.EVE_DETAIL_FONTSIZE: 10,
                        fontconst.EVE_BODY_FONTSIZE: 12,
                        fontconst.EVE_HEADER_FONTSIZE: 16,
                        fontconst.EVE_HEADLINE_FONTSIZE: 22,
                        fontconst.EVE_DISPLAY_FONTSIZE: 39},
 FontSizeOption.MEDIUM: {fontconst.EVE_SMALL_FONTSIZE: 12,
                         fontconst.EVE_MEDIUM_FONTSIZE: 14,
                         fontconst.EVE_LARGE_FONTSIZE: 16,
                         fontconst.EVE_XLARGE_FONTSIZE: 19,
                         fontconst.EVE_DETAIL_FONTSIZE: 12,
                         fontconst.EVE_BODY_FONTSIZE: 14,
                         fontconst.EVE_HEADER_FONTSIZE: 18,
                         fontconst.EVE_HEADLINE_FONTSIZE: 24,
                         fontconst.EVE_DISPLAY_FONTSIZE: 40},
 FontSizeOption.LARGE: {fontconst.EVE_SMALL_FONTSIZE: 13,
                        fontconst.EVE_MEDIUM_FONTSIZE: 15,
                        fontconst.EVE_LARGE_FONTSIZE: 17,
                        fontconst.EVE_XLARGE_FONTSIZE: 20,
                        fontconst.EVE_DETAIL_FONTSIZE: 13,
                        fontconst.EVE_BODY_FONTSIZE: 15,
                        fontconst.EVE_HEADER_FONTSIZE: 19,
                        fontconst.EVE_HEADLINE_FONTSIZE: 25,
                        fontconst.EVE_DISPLAY_FONTSIZE: 41},
 FontSizeOption.EXTRA_LARGE: {fontconst.EVE_SMALL_FONTSIZE: 14,
                              fontconst.EVE_MEDIUM_FONTSIZE: 16,
                              fontconst.EVE_LARGE_FONTSIZE: 18,
                              fontconst.EVE_XLARGE_FONTSIZE: 21,
                              fontconst.EVE_DETAIL_FONTSIZE: 14,
                              fontconst.EVE_BODY_FONTSIZE: 16,
                              fontconst.EVE_HEADER_FONTSIZE: 20,
                              fontconst.EVE_HEADLINE_FONTSIZE: 26,
                              fontconst.EVE_DISPLAY_FONTSIZE: 42}}

def _handle_font_size_setting_feature_flag_changed():
    if not is_new_font_size_options_enabled():
        migration_map = {FontSizeOption.EXTRA_SMALL: FontSizeOption.SMALL,
         FontSizeOption.EXTRA_LARGE: FontSizeOption.LARGE}
        current_value = get_font_size_setting()
        if current_value in migration_map:
            set_font_size_setting(migration_map[current_value])
        else:
            _notify_font_size_changed()
    else:
        _notify_font_size_changed()


DEFAULT_FONT_SIZE_BY_LANGUAGE_ID = {'ko': FontSizeOption.LARGE,
 'zh': FontSizeOption.LARGE,
 'ja': FontSizeOption.LARGE}

def get_default_font_size_setting(language_id):
    return DEFAULT_FONT_SIZE_BY_LANGUAGE_ID.get(language_id.lower(), FontSizeOption.MEDIUM)


def migrate_existing_font_size_settings_down_one_size(user_id, char_id):
    migration_flag = '__migrate_existing_font_size_settings_down_one_size__'
    if settings.public.ui.Get(migration_flag, False):
        return
    current_value = settings.public.ui.Get('clientFontSize', None)
    default_value = get_default_font_size_setting(session.languageID)
    new_font_size_option_by_old = {FontSizeOption.SMALL: FontSizeOption.EXTRA_SMALL,
     FontSizeOption.MEDIUM: FontSizeOption.SMALL,
     FontSizeOption.LARGE: FontSizeOption.MEDIUM}
    new_value = new_font_size_option_by_old.get(current_value, default_value)
    set_font_size_setting(new_value)
    settings.public.ui.Set(migration_flag, True)
