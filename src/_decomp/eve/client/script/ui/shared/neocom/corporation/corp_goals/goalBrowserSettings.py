#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_goals\goalBrowserSettings.py
from carbonui.services.setting import SessionSettingBool, SessionSettingEnum, CharSettingEnum
from characterdata import careerpath
have_participated_in_filter_setting = SessionSettingBool(False)
have_unclaimed_rewards_for_filter_setting = SessionSettingBool(False)
can_contribute_to_setting = SessionSettingBool(False)
_options = [None] + careerpath.get_career_paths().keys()
career_path_filter_setting = SessionSettingEnum(None, _options)
sort_by_options = ['name',
 'name_reversed',
 'date_created',
 'date_created_reversed',
 'time_remaining',
 'time_remaining_reversed',
 'progress',
 'progress_reversed',
 'num_jumps',
 'num_jumps_reversed']
sort_by_setting = CharSettingEnum('ActiveCorpProjectsSortBy', 'name', sort_by_options)
