#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\uiColorSettings.py
from carbonui.services.setting import CharSettingNumeric, CharSettingBool
window_transparency_setting = CharSettingNumeric('windowTransparency', 1.0, min_value=0.0, max_value=1.0)
window_transparency_noblur_setting = CharSettingNumeric('windowTransparencyNoBlur', 0.05, min_value=0.0, max_value=1.0)
window_transparency_light_mode_setting = CharSettingNumeric('windowTransparencyLightMode', 1.0, min_value=0.0, max_value=1.0)
_get_legacy_blur_setting = lambda : settings.char.windows.Get('enableWindowBlur', True)
show_window_bg_blur_setting = CharSettingBool('enableWindowBlur', _get_legacy_blur_setting)
_get_legacy_ship_setting = lambda : settings.char.windows.Get('shiptheme', False)
color_theme_by_ship_faction_setting = CharSettingBool('shiptheme', _get_legacy_ship_setting)
