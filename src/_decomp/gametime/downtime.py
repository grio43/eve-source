#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\gametime\downtime.py
import datetimeutils
import monolithconfig
from datetime import datetime, timedelta, time, date
from caching.memoize import Memoize
import logging
from carbon.common.lib.const import DAY
logger = logging.getLogger(__name__)

@Memoize
def get_downtime_start_time():
    cluster_down_time_raw = monolithconfig.get_value('DowntimeStarts', 'zcluster')
    if not cluster_down_time_raw:
        logger.warning('DowntimeStarts not defined in zcluster config. Defaulting to 11:00:00.')
        return time(11, 0)
    return datetime.strptime(cluster_down_time_raw, '%H:%M:%S').time()


@Memoize
def get_last_downtime():
    downtime = get_last_downtime_datetime()
    return datetimeutils.datetime_to_filetime(downtime)


def get_last_downtime_datetime():
    downtime_time = get_downtime_start_time()
    now = datetime.now()
    downtime_datetime = datetime.combine(now.date(), downtime_time)
    if now < downtime_datetime:
        downtime_datetime += timedelta(days=-1)
    return downtime_datetime


def get_next_downtime():
    return get_last_downtime() + DAY


def get_next_downtime_datetime():
    return get_last_downtime_datetime() + timedelta(days=1)


def is_downtime_done_today():
    return get_last_downtime_datetime().date() == date.today()
