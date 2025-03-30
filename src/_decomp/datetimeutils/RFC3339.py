#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datetimeutils\RFC3339.py
from datetime import datetime, timedelta
POSIX_EPOCH = datetime(1970, 1, 1, 0, 0)
EPOCH_AS_FILETIME = 116444736000000000L
HUNDREDS_OF_NANOSECONDS = 10000000
HUNDREDS_OF_NANOS_TO_MS = 10000.0
BLUETIME_STRP = '%Y-%m-%d %H:%M:%S'
DTM_RFC_FORMAT = '%04d-%02d-%02dT%02d:%02d:%02d.%06dZ'
DT_RFC_FORMAT = '%04d-%02d-%02dT%02d:%02d:%02dZ'
D_RFC_FORMAT = '%04d-%02d-%02d'
DATETIME_STRF = '%Y-%m-%dT%H:%M:%SZ'

def blue_to_datetime_micro(blue_ts):
    if blue_ts is None:
        return
    dto = _blue_to_date_time(blue_ts)
    return DTM_RFC_FORMAT % (dto.year,
     dto.month,
     dto.day,
     dto.hour,
     dto.minute,
     dto.second,
     dto.microsecond)


def blue_to_datetime(blue_ts):
    if blue_ts is None:
        return
    dto = _blue_to_date_time(blue_ts)
    return DT_RFC_FORMAT % (dto.year,
     dto.month,
     dto.day,
     dto.hour,
     dto.minute,
     dto.second)


def blue_to_date(blue_ts):
    if blue_ts is None:
        return
    dto = _blue_to_date_time(blue_ts)
    return D_RFC_FORMAT % (dto.year, dto.month, dto.day)


def blue_date_to_blue(blue_string):
    if blue_string is None:
        return
    blue_dt = datetime.strptime(blue_string, BLUETIME_STRP)
    unix_time = long((blue_dt - POSIX_EPOCH).total_seconds())
    return unix_to_blue(unix_time)


def datetime_to_blue(dt_string):
    timestamp = None
    try:
        unix_time = _date_time_to_unix(dt_string)
        timestamp = unix_to_blue(unix_time)
    finally:
        return timestamp


def date_to_blue(d_string):
    timestamp = None
    try:
        d_string = _remove_time_part(d_string)
        unix_time = _date_to_unix(d_string)
        timestamp = unix_to_blue(unix_time)
    finally:
        return timestamp


def unix_to_blue(unix_time):
    return long(unix_time * HUNDREDS_OF_NANOSECONDS + EPOCH_AS_FILETIME)


def blue_to_unix(blue_ts):
    return long((blue_ts - EPOCH_AS_FILETIME) / HUNDREDS_OF_NANOSECONDS)


def blue_to_unix_ms(blue_ts):
    return (blue_ts - EPOCH_AS_FILETIME) / HUNDREDS_OF_NANOS_TO_MS


def _blue_to_date_time(blue_ts):
    seconds_since_epoch, _nanoseconds = divmod(blue_ts - EPOCH_AS_FILETIME, HUNDREDS_OF_NANOSECONDS)
    return POSIX_EPOCH + timedelta(seconds=seconds_since_epoch, microseconds=_nanoseconds / 10)


def _date_to_unix(dt_string):
    year, month, day = dt_string.split('-')
    dt = datetime(int(year), int(month), int(day), 0, 0, 0)
    return long((dt - POSIX_EPOCH).total_seconds())


def _date_time_to_unix(dt_string):
    dt_string = _remove_ns_part(dt_string)
    date, time = dt_string.split('T')
    year, month, day = date.split('-')
    hour, minute, second = time[:-1].split(':')
    dt = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    return long((dt - POSIX_EPOCH).total_seconds())


def _remove_time_part(d_string):
    ix = d_string.find('T')
    if ix >= 0:
        d_string = d_string[:ix]
    return d_string


def _remove_ns_part(dt_string):
    ix = dt_string.find('.')
    if ix >= 0:
        dt_string = '%sZ' % dt_string[:ix]
    return dt_string
