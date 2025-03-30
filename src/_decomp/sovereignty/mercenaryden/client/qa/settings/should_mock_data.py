#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\qa\settings\should_mock_data.py
from carbonui.services.setting import UserSettingBool
from sovereignty.mercenaryden.client.qa.settings.base import BaseQASetting
SETTING_SHOULD_MOCK = UserSettingBool('should_mock_mercenary_den_data', default_value=False)

class ShouldMockSetting(BaseQASetting):

    def is_enabled(self):
        return SETTING_SHOULD_MOCK.is_enabled()

    def register_to_updates(self, callback):
        SETTING_SHOULD_MOCK.on_change.connect(callback)

    def unregister_from_updates(self, callback):
        SETTING_SHOULD_MOCK.on_change.disconnect(callback)
