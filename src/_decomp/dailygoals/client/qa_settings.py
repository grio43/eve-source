#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dailygoals\client\qa_settings.py
from carbonui.services.setting import UserSettingNumeric, UserSettingBool
daily_goals_get_goals_force_errors = UserSettingBool('daily_goals_get_goals_force_errors', default_value=False)
daily_goals_get_goals_randomize_errors = UserSettingBool('daily_goals_get_goals_randomize_errors', default_value=False)
daily_goals_get_goals_force_delay = UserSettingNumeric('daily_goals_get_goals_force_delay', default_value=0, min_value=0, max_value=5)
daily_goals_use_mock = UserSettingBool('daily_goals_use_mock', default_value=False)
