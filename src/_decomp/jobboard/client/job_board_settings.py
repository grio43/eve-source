#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\job_board_settings.py
from carbonui.services.setting import CharSettingEnum, CharSettingBool, SessionSettingBool
sort_by_setting = CharSettingEnum('BrowseSortBy', 'relevance', ['relevance',
 'num_jumps',
 'num_jumps_reversed',
 'name',
 'name_reversed',
 'time_remaining',
 'time_remaining_reversed'])
guidance_highlighting_disabled_setting = CharSettingBool('guidance_highlighting_disabled', False)
fixed_expanded_side_navigation_setting = CharSettingBool('fixed_expanded_side_navigation', False)
list_view_setting = CharSettingBool('opportunities_list_view', False)
open_opportunities_on_startup_setting = CharSettingBool('open_opportunities_on_startup', True)
redeem_to_current_location = SessionSettingBool(False)
_feature_display_setting = {}

def get_display_feature_setting(feature_id):
    if feature_id not in _feature_display_setting:
        _feature_display_setting[feature_id] = CharSettingBool('opportunities_display_{}'.format(feature_id), True)
    return _feature_display_setting[feature_id]
