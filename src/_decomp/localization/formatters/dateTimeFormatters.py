#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localization\formatters\dateTimeFormatters.py
import time
import calendar
import blue
import eveLocalization
import pytelemetry.zoning as telemetry
from localization.uiutil import PrepareLocalizationSafeString
from localization import logger

@telemetry.ZONE_FUNCTION
def FormatDateTime(value, **kwargs):
    formatStringList = []
    if kwargs.get('dateFormat', 'short') in ('full', 'long', 'medium', 'short'):
        formatStringList.append('%Y.%m.%d')
    timeFormat = kwargs.get('timeFormat', 'short')
    if timeFormat in ('full', 'long', 'medium'):
        formatStringList.append('%H:%M:%S')
    elif timeFormat == 'short':
        formatStringList.append('%H:%M')
    formatString = ' '.join(formatStringList)
    if isinstance(value, long):
        value = value + eveLocalization.GetTimeDelta() * const.SEC
        year, month, weekday, day, hour, minute, second, msec = blue.os.GetTimeParts(value)
        day_of_year = 1
        is_daylight_savings = -1
        value = (year,
         month,
         day,
         hour,
         minute,
         second,
         weekday,
         day_of_year,
         is_daylight_savings)
    elif isinstance(value, (time.struct_time, tuple)):
        value = calendar.timegm(value)
        value = time.gmtime(value + eveLocalization.GetTimeDelta())
    elif isinstance(value, float):
        value = time.gmtime(value + eveLocalization.GetTimeDelta())
    else:
        logger.LogTraceback('datetime only accepts blue time or Python time as values, but we received a ', type(value).__name__, '.')
        return None
    return PrepareLocalizationSafeString(time.strftime(formatString, value), 'time')
