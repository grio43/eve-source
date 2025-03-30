#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\loginrewards\common\timekeeper.py
from datetime import timedelta, time
import gametime
import datetimeutils
from datetimeutils import find_earliest_time_after_datetime

class TimeKeeper(object):

    def __init__(self, utc_campaign_start_hours = 0, utc_campaign_start_minutes = 0):
        self.dateline = time(hour=utc_campaign_start_hours, minute=utc_campaign_start_minutes)

    def get_current_reward_date(self):
        return self.get_reward_date_from_timestamp(gametime.GetWallclockTime())

    def get_reward_date_from_timestamp(self, timestamp):
        timestampInDateTime = datetimeutils.FromBlueTime(timestamp)
        return (timestampInDateTime + timedelta(hours=-self.dateline.hour, minutes=-self.dateline.minute)).date()

    def get_hours_until_next_reward_date(self):
        right_now = datetimeutils.FromBlueTime(gametime.GetWallclockTime())
        next_reward_date = find_earliest_time_after_datetime(right_now, self.dateline)
        return int((next_reward_date - right_now).total_seconds() / 3600)

    def get_next_reward_date(self):
        right_now = datetimeutils.FromBlueTime(gametime.GetWallclockTime())
        next_reward_date = find_earliest_time_after_datetime(right_now, self.dateline)
        return next_reward_date
