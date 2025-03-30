#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\studioSettings.py
from carbonui.services.setting import CharSettingEnum, SessionSettingBool
from eve.client.script.ui.shared.shipTree import shipTreeConst
from eve.common.lib import appConst

def get_default_faction():
    return appConst.factionByRace[session.raceID]


selected_faction_id_setting = CharSettingEnum('studio_selected_faction_id', get_default_faction)
only_shown_owned_design_elements_setting = SessionSettingBool(True)
pattern_rotation_follow_camera_setting = SessionSettingBool(False)
