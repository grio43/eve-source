#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\client\visibilityrestrictions.py
import uthread2
import gametime
USER_AGE_REQUIREMENT = 2 * gametime.DAY

class SeasonVisibilityRestrictions(object):

    def __init__(self, cc, on_visibility_changed):
        self.cc = cc
        self.info_panel_activation_thread = None
        self.on_visibility_changed = on_visibility_changed
        blue_user_age = self._get_blue_user_age()
        self._is_season_visible = blue_user_age > USER_AGE_REQUIREMENT
        if not self._is_season_visible:
            self._schedule_info_panel_appearing()

    def _get_blue_user_age(self):
        char_data = self.cc.GetCharacterSelectionData(force=False)
        blue_creation_date_time = char_data.GetUserCreationDate()
        blue_user_age = gametime.GetWallclockTime() - blue_creation_date_time
        return blue_user_age

    def _appear(self):
        self._is_season_visible = True
        self.on_visibility_changed()

    def _schedule_info_panel_appearing(self):
        blue_user_age = self._get_blue_user_age()
        seconds_until_season_is_visible = (USER_AGE_REQUIREMENT - blue_user_age) / gametime.SEC
        if seconds_until_season_is_visible * gametime.SEC < gametime.DAY:
            uthread2.call_after_wallclocktime_delay(self._appear, seconds_until_season_is_visible)

    def is_season_visible(self):
        return self._is_season_visible
