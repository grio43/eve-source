#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datetimeutils\__init__.py
import datetime
import re
import time
__version__ = (2, 3, 0, 0)
from datetimeutils.monolithext import *
from datetimeutils.parsers.timedelta import str_to_timedelta
_string_types = tuple({type(u''), type('')})
_number_types = tuple({type(0), type(18446744073709551615L)})
_NOT_SUPPLIED = object()
FILETIME_NULL_DATE = datetime.datetime(1601, 1, 1, 0, 0, 0)
ISODATE_REGEX = re.compile('^(?:(?P<year>[0]{0,3}[1-9]\\d{0,3})[- /.,\\\\](?P<month>1[012]|0?\\d)[- /.,\\\\](?P<day>3[01]|[012]?\\d))?(?:[ @Tt]{0,1}(?:(?P<hour>[2][0-3]|[01]?\\d)[ .:,](?P<minute>[012345]?\\d))?(?:[ .:,](?P<second>[012345]?\\d)(?:[ .:,](?P<millisecond>\\d{0,6}))?)?)?')
DATE_REXEX = re.compile('(?P<year>[0]{0,3}[1-9]\\d{0,3})[- /.,\\\\](?P<month>1[012]|0?\\d)[- /.,\\\\](?P<day>3[01]|[012]?\\d)')
REVERSE_DATETIME_REXEX = re.compile('(?P<day>3[01]|[012]?\\d)[- /.,\\\\](?P<month>1[012]|0?\\d)[- /.,\\\\](?P<year>[12][0189]\\d{2})(?:[ @Tt]{0,1}(?:(?P<hour>[2][0-3]|[01]?\\d)[ .:,](?P<minute>[012345]?\\d))?(?:[ .:,](?P<second>[012345]?\\d)(?:[ .:,](?P<millisecond>\\d{0,6}))?)?)?')
REVERSE_US_DATETIME_REXEX = re.compile('(?P<month>1[012]|0?\\d)[- /.,\\\\](?P<day>3[01]|[012]?\\d)[- /.,\\\\](?P<year>[12][0189]\\d{2})(?:[ @Tt]{0,1}(?:(?P<hour>[2][0-3]|[01]?\\d)[ .:,](?P<minute>[012345]?\\d))?(?:[ .:,](?P<second>[012345]?\\d)(?:[ .:,](?P<millisecond>\\d{0,6}))?)?)?')
MEAN_MONTH = 30.436875
MEAN_YEAR = 365.2425
FILETIME_UNIXTIME_DIFF = 11644473600L
FILETIME_SEC_TICKS = 10000000

def filetime_to_datetime(filetime):
    return FILETIME_NULL_DATE + datetime.timedelta(microseconds=filetime / 10)


def datetime_to_filetime(dt):
    if not isinstance(dt, datetime.datetime) and isinstance(dt, datetime.date):
        dt = datetime.datetime.combine(dt, datetime.time(0, 0, 0))
    delta = dt - FILETIME_NULL_DATE
    return 10 * ((delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds)


def datetime_to_timestamp(dt):
    if not isinstance(dt, datetime.datetime) and isinstance(dt, datetime.date):
        dt = datetime.datetime.combine(dt, datetime.time(0, 0, 0))
    return int(time.mktime(dt.timetuple()))


def regex_to_datetime(string, regex_pattern):
    match = regex_pattern.match(string.strip())
    if match:
        parts = match.groupdict()
        found_date = False
        if parts['year'] and parts['month'] and parts['day']:
            date_part = datetime.date(int(parts['year']), int(parts['month']), int(parts['day']))
            found_date = True
        else:
            date_part = datetime.date.today()
        found_time = False
        if parts['hour'] and parts['minute']:
            time_part = datetime.time(int(parts['hour']), int(parts['minute']), int(parts['second'] or 0), int(parts['millisecond'] or 0))
            found_time = True
        else:
            time_part = datetime.time()
        if found_date or found_time:
            return datetime.datetime.combine(date_part, time_part)


def isostr_to_datetime(string):
    match = ISODATE_REGEX.match(string.strip())
    if match:
        parts = match.groupdict()
        found_date = False
        if parts['year'] and parts['month'] and parts['day']:
            date_part = datetime.date(int(parts['year']), int(parts['month']), int(parts['day']))
            found_date = True
        else:
            date_part = datetime.date.today()
        found_time = False
        if parts['hour'] and parts['minute']:
            time_part = datetime.time(int(parts['hour']), int(parts['minute']), int(parts['second'] or 0), int(parts['millisecond'] or 0))
            found_time = True
        else:
            time_part = datetime.time()
        if found_date or found_time:
            return datetime.datetime.combine(date_part, time_part)


def any_to_datetime(temporal_object, default = _NOT_SUPPLIED, utc = True):
    if default == _NOT_SUPPLIED:
        default = temporal_object
    try:
        if isinstance(temporal_object, datetime.datetime):
            return temporal_object
        if isinstance(temporal_object, datetime.date):
            return datetime.datetime.combine(temporal_object, datetime.time())
        if isinstance(temporal_object, float):
            if temporal_object > 29999999999L:
                temporal_object = int(temporal_object)
            elif utc:
                return datetime.datetime.utcfromtimestamp(temporal_object)
            else:
                return datetime.datetime.fromtimestamp(temporal_object)

        if isinstance(temporal_object, _number_types):
            if temporal_object > 29999999999L:
                return filetime_to_datetime(temporal_object)
            elif utc:
                return datetime.datetime.utcfromtimestamp(temporal_object)
            else:
                return datetime.datetime.fromtimestamp(temporal_object)
        if isinstance(temporal_object, _string_types):
            value = regex_to_datetime(temporal_object, REVERSE_DATETIME_REXEX)
            if value:
                return value
            value = regex_to_datetime(temporal_object, REVERSE_US_DATETIME_REXEX)
            if value:
                return value
            value = isostr_to_datetime(temporal_object)
            if value:
                return value
    except (OverflowError, ValueError):
        pass

    return default


def _div_and_rest(total, chunk):
    divs = int(total / chunk)
    return (divs, total - chunk * divs)


def split_delta(delta, include_weeks = True, include_months = True, include_years = True):
    parts = {'1st': None,
     '2nd': None,
     'is_past': False}
    if delta.total_seconds() < 0:
        parts['is_past'] = True
        delta = datetime.timedelta(seconds=-delta.total_seconds())
    days = abs(delta.days)
    if include_years:
        parts['years'], days = _div_and_rest(days, MEAN_YEAR)
        if parts['years']:
            parts['1st'] = 'years'
    if include_months:
        parts['months'], days = _div_and_rest(days, MEAN_MONTH)
        if parts['months']:
            if not parts['1st']:
                parts['1st'] = 'months'
            else:
                parts['2nd'] = 'months'
    if include_weeks:
        parts['weeks'], days = _div_and_rest(days, 7)
        if not parts['1st'] and parts['weeks']:
            parts['1st'] = 'weeks'
        elif not parts['2nd'] and parts['weeks']:
            parts['2nd'] = 'weeks'
    parts['days'] = int(days)
    if not parts['1st'] and parts['days']:
        parts['1st'] = 'days'
    elif not parts['2nd'] and parts['days']:
        parts['2nd'] = 'days'
    seconds = abs(delta.seconds)
    parts['hours'], seconds = _div_and_rest(seconds, 3600)
    if not parts['1st'] and parts['hours']:
        parts['1st'] = 'hours'
    elif not parts['2nd'] and parts['hours']:
        parts['2nd'] = 'hours'
    parts['minutes'], seconds = _div_and_rest(seconds, 60)
    if not parts['1st'] and parts['minutes']:
        parts['1st'] = 'minutes'
    elif not parts['2nd'] and parts['minutes']:
        parts['2nd'] = 'minutes'
    parts['seconds'] = int(seconds)
    if not parts['1st'] and parts['seconds']:
        parts['1st'] = 'seconds'
    elif not parts['2nd'] and parts['seconds']:
        parts['2nd'] = 'seconds'
    return parts


def deltastr(delta, default = ''):
    if not isinstance(delta, datetime.timedelta):
        return default
    parts = split_delta(delta)
    if parts['1st']:
        first_key = parts['1st']
        if first_key == 'seconds':
            return 'a few seconds'
        first_value = parts[first_key]
        if first_value > 1:
            return '%s %s' % (first_value, first_key)
        first_key = first_key[:-1]
        if parts['2nd'] and parts['2nd'] != 'seconds':
            second_key = parts['2nd']
            second_value = parts[second_key]
            if second_value < 2:
                second_key = second_key[:-1]
            return '%s %s and %s %s' % (first_value,
             first_key,
             second_value,
             second_key)
        else:
            return '%s %s' % (first_value, first_key)
    else:
        return 'a few seconds'


def ago(delta_or_date, default = '', utc = True):
    if utc:
        now = datetime.datetime.utcnow()
    else:
        now = datetime.datetime.now()
    if isinstance(delta_or_date, datetime.datetime):
        delta_or_date = now - delta_or_date
    elif isinstance(delta_or_date, datetime.date):
        delta_or_date = now.date() - delta_or_date
    elif isinstance(delta_or_date, datetime.time):
        delta_or_date = datetime.datetime.combine(now.date(), delta_or_date)
    return deltastr(delta_or_date, default)


def find_earliest_time_after_datetime(dt, time):
    dt_with_time_replaced = datetime.datetime.combine(dt.date(), time)
    if dt_with_time_replaced <= dt:
        dt_with_time_replaced += datetime.timedelta(days=1)
    return dt_with_time_replaced


def find_earliest_time_and_weekday_after_datetime(dt, time_of_day, day_of_week):
    dt_with_time_replaced = datetime.datetime.combine(dt.date(), time_of_day)
    if dt_with_time_replaced <= dt:
        dt_with_time_replaced += datetime.timedelta(days=1)
    days_to_advance = (day_of_week - dt_with_time_replaced.weekday()) % 7
    return dt_with_time_replaced + datetime.timedelta(days=days_to_advance)


def dt_midnight(dt):
    if isinstance(dt, datetime.datetime):
        dt = dt.date()
    if isinstance(dt, datetime.date):
        return datetime.datetime.combine(dt, datetime.time())
    return dt


def dt_from_now(days = 0, hours = 0, minutes = 0, seconds = 0, weeks = 0):
    return datetime.datetime.now() + datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds, weeks=weeks)


def dt_ago(days = 0, hours = 0, minutes = 0, seconds = 0, weeks = 0):
    return datetime.datetime.now() - datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds, weeks=weeks)


def date_from_now(days = 0, weeks = 0):
    return dt_midnight(dt_from_now(days, weeks))


def date_ago(days = 0, weeks = 0):
    return dt_midnight(dt_ago(days, weeks))


def str_to_relative_datetime(str_value):
    str_value = str_value.strip().lower()
    if str_value in ('now', 'today'):
        return datetime.datetime.now()
    elif str_value == 'yesterday':
        return datetime.datetime.now() - datetime.timedelta(days=1)
    elif str_value == 'tomorrow':
        return datetime.datetime.now() + datetime.timedelta(days=1)
    else:
        return None


def str_to_2dates(str_value):
    try:
        match = DATE_REXEX.findall(str_value.strip())
        if match:
            if len(match) == 2:
                if len(match[0]) == 3 and len(match[1]) == 3:
                    date_from = datetime.date(int(match[0][0]), int(match[0][1]), int(match[0][2]))
                    date_to = datetime.date(int(match[1][0]), int(match[1][1]), int(match[1][2]))
                    return (date_from, date_to)
        return None
    except Exception:
        return None


def serialize(temporal_object):
    if isinstance(temporal_object, (datetime.datetime, datetime.date, datetime.time)):
        return temporal_object.isoformat()
    elif isinstance(temporal_object, datetime.timedelta):
        return temporal_object.total_seconds()
    else:
        return temporal_object


def to_str(temporal_object):
    return str(serialize(temporal_object))
