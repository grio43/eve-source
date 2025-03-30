#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datetimeutils\monolithext.py
import datetime
from datetimeutils.RFC3339 import POSIX_EPOCH, HUNDREDS_OF_NANOSECONDS, unix_to_blue

def FromBlueTime(timestamp):
    from datetimeutils import filetime_to_datetime
    return filetime_to_datetime(timestamp)


def date_to_blue(py_date):
    import datetime
    dt = datetime.datetime(py_date.year, py_date.month, py_date.day, 0, 0, 0)
    unix_time = long((dt - POSIX_EPOCH).total_seconds())
    return unix_to_blue(unix_time)


def timedelta_to_filetime_delta(timedelta):
    return long(timedelta.total_seconds() * HUNDREDS_OF_NANOSECONDS)


def filetime_delta_to_timedelta(filetime_delta):
    seconds = filetime_delta / HUNDREDS_OF_NANOSECONDS
    return datetime.timedelta(seconds=seconds)
