#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\default\settings.py
from overviewPresets.overviewSettingsConst import SETTING_OVERVIEW_ID, SETTING_DEFAULT_OVERVIEW_ID, SETTING_INFORMED_OF_UPDATE

class DefaultOverviewSettings(object):

    def set_overview(self, overview_id):
        settings.user.defaultoverview.Set(SETTING_OVERVIEW_ID, overview_id)

    def set_default_overview(self, default_id):
        settings.user.defaultoverview.Set(SETTING_DEFAULT_OVERVIEW_ID, default_id)

    def set_informed_of_update(self, switch_offered):
        settings.user.defaultoverview.Set(SETTING_INFORMED_OF_UPDATE, int(switch_offered))

    def get_overview(self):
        return settings.user.defaultoverview.Get(SETTING_OVERVIEW_ID, None)

    def get_default_overview(self):
        return settings.user.defaultoverview.Get(SETTING_DEFAULT_OVERVIEW_ID, None)

    def get_informed_of_update(self):
        return settings.user.defaultoverview.Get(SETTING_INFORMED_OF_UPDATE, 0)

    def get_settings_report(self):
        overview_id = self.get_overview()
        default_id = self.get_default_overview()
        informed_of_update = self.get_informed_of_update()
        return 'User ID: {user_id}, Character ID: {character_id}, Overview ID: {overview_id}, Default Overview ID: {default_id}, Informed of Update: {informed_of_update}'.format(user_id=session.userid, character_id=session.charid, overview_id=overview_id, default_id=default_id, informed_of_update=informed_of_update)
