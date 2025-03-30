#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\neocomSettings.py
from carbonui import uiconst
from carbonui.services.setting import CharSettingBool, CharSettingEnum, CharSettingNumeric
from eve.client.script.ui.services.uiColorSettings import show_window_bg_blur_setting
from eve.client.script.ui.shared.neocom.neocom import neocomConst
neocom_allow_blink_setting = CharSettingBool('neoblink', True)
neocom_allow_badges_setting = CharSettingBool('enableInventoryBadging', True)
neocom_align_setting = CharSettingEnum('neocomAlign', neocomConst.NEOCOM_DEFAULT_ALIGN, (uiconst.TOLEFT, uiconst.TORIGHT))
neocom_width_setting = CharSettingNumeric('neocomWidth', neocomConst.NEOCOM_DEFAULT_WIDTH, neocomConst.NEOCOM_MINSIZE, neocomConst.NEOCOM_MAXSIZE)

class NeocomLightBackgroundSetting(CharSettingBool):

    def __init__(self):
        super(NeocomLightBackgroundSetting, self).__init__(settings_key='neocom_light_background_enabled', default_value=None)
        show_window_bg_blur_setting.on_change.connect(self._on_show_window_bg_blur_changed)

    def get_default(self):
        return show_window_bg_blur_setting.get()

    def _on_show_window_bg_blur_changed(self, value):
        stored_value = self.settings_path.Get(self.settings_key, None)
        if stored_value is None:
            self._trigger_on_change(self.get_default())


neocom_light_background_setting = NeocomLightBackgroundSetting()
