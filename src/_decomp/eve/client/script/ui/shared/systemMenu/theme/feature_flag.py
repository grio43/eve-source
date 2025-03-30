#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\theme\feature_flag.py
_is_custom_color_themes_enabled = None
IS_CUSTOM_COLOR_THEMES_ENABLED_KEY = 'pathfinder-custom-color-themes-available'
IS_CUSTOM_COLOR_THEMES_ENABLED_DEFAULT = False

def is_custom_color_themes_enabled():
    global _is_custom_color_themes_enabled
    if _is_custom_color_themes_enabled is None:
        import launchdarkly
        launchdarkly.get_client().notify_flag(flag_key=IS_CUSTOM_COLOR_THEMES_ENABLED_KEY, flag_fallback=IS_CUSTOM_COLOR_THEMES_ENABLED_DEFAULT, callback=_update_is_custom_color_themes_enabled)
    return _is_custom_color_themes_enabled


def _update_is_custom_color_themes_enabled(ld_client, flag_key, flag_fallback, flag_deleted):
    global _is_custom_color_themes_enabled
    new_value = ld_client.get_bool_variation(feature_key=flag_key, fallback=flag_fallback)
    if _is_custom_color_themes_enabled != new_value:
        _is_custom_color_themes_enabled = new_value
        _handle_is_custom_color_themes_enabled_changed()


def _handle_is_custom_color_themes_enabled_changed():
    sm.GetService('uiColor').TriggerUpdate()


def is_only_tint_active_window_setting_enabled():
    return is_custom_color_themes_enabled()
