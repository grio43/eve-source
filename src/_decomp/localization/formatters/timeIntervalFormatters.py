#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localization\formatters\timeIntervalFormatters.py
import numbers
import eve.common.lib.appConst as appConst
import langutils
import pytelemetry.zoning as telemetry
from datetimeutils import filetime_to_datetime
from dateutil import relativedelta
from localization.formatters import listFormatters
from localization.formatters import numericFormatters
TIME_CATEGORY_YEAR = 'year'
TIME_CATEGORY_MONTH = 'month'
TIME_CATEGORY_DAY = 'day'
TIME_CATEGORY_HOUR = 'hour'
TIME_CATEGORY_MINUTE = 'minute'
TIME_CATEGORY_SECOND = 'second'
TIME_CATEGORY_MILLISECOND = 'millisecond'
TIME_PART_KEYS = [TIME_CATEGORY_YEAR,
 TIME_CATEGORY_MONTH,
 TIME_CATEGORY_DAY,
 TIME_CATEGORY_HOUR,
 TIME_CATEGORY_MINUTE,
 TIME_CATEGORY_SECOND,
 TIME_CATEGORY_MILLISECOND]
QUANTITY_TIME_SHORT_MAP = {2: '/Carbon/UI/Common/DateTimeQuantity/DateTimeShort2Elements',
 3: '/Carbon/UI/Common/DateTimeQuantity/DateTimeShort3Elements',
 4: '/Carbon/UI/Common/DateTimeQuantity/DateTimeShort4Elements',
 5: '/Carbon/UI/Common/DateTimeQuantity/DateTimeShort5Elements',
 6: '/Carbon/UI/Common/DateTimeQuantity/DateTimeShort6Elements',
 7: '/Carbon/UI/Common/DateTimeQuantity/DateTimeShort7Elements'}
QUANTITY_TIME_SHORT_WRITTEN_MAP = {2: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/DateTimeShortWritten2Elements',
 3: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/DateTimeShortWritten3Elements',
 4: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/DateTimeShortWritten4Elements',
 5: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/DateTimeShortWritten5Elements',
 6: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/DateTimeShortWritten6Elements',
 7: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/DateTimeShortWritten7Elements'}
QUANTITY_TIME_SHORT_WRITTEN_UNITS_MAP = {TIME_CATEGORY_YEAR: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/Year',
 TIME_CATEGORY_MONTH: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/Month',
 TIME_CATEGORY_DAY: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/Day',
 TIME_CATEGORY_HOUR: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/Hour',
 TIME_CATEGORY_MINUTE: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/Minute',
 TIME_CATEGORY_SECOND: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/Second',
 TIME_CATEGORY_MILLISECOND: '/Carbon/UI/Common/WrittenDateTimeQuantityShort/Millisecond'}
SMALL_WRITTEN_QUANTITY_TIME_MAP = {TIME_CATEGORY_YEAR: '/Carbon/UI/Common/WrittenDateTimeQuantity/LessThanOneYear',
 TIME_CATEGORY_MONTH: '/Carbon/UI/Common/WrittenDateTimeQuantity/LessThanOneMonth',
 TIME_CATEGORY_DAY: '/Carbon/UI/Common/WrittenDateTimeQuantity/LessThanOneDay',
 TIME_CATEGORY_HOUR: '/Carbon/UI/Common/WrittenDateTimeQuantity/LessThanOneHour',
 TIME_CATEGORY_MINUTE: '/Carbon/UI/Common/WrittenDateTimeQuantity/LessThanOneMinute',
 TIME_CATEGORY_SECOND: '/Carbon/UI/Common/WrittenDateTimeQuantity/LessThanOneSecond',
 TIME_CATEGORY_MILLISECOND: '/Carbon/UI/Common/WrittenDateTimeQuantity/LessThanOneMillisecond'}
TIME_INTERVAL_UNITS_VALUE_MAP = {TIME_CATEGORY_YEAR: appConst.YEAR365,
 TIME_CATEGORY_MONTH: appConst.MONTH30,
 TIME_CATEGORY_DAY: appConst.DAY,
 TIME_CATEGORY_HOUR: appConst.HOUR,
 TIME_CATEGORY_MINUTE: appConst.MIN,
 TIME_CATEGORY_SECOND: appConst.SEC,
 TIME_CATEGORY_MILLISECOND: appConst.MSEC}

def GetByLabel(label, languageID = None, **kwargs):
    import localization
    return localization.GetByLabel(label, languageID, **kwargs)


@telemetry.ZONE_FUNCTION
def _FormatTimeIntervalGetParts(value, showFrom, showTo, roundUp = False):
    if value < 0:
        raise ValueError('Time value must be a positive number. value = %s' % value)
    if isinstance(value, float):
        import log
        log.LogTraceback('float value passed in for time interval')
        value = long(value) * const.SEC
    if not isinstance(value, numbers.Integral):
        raise ValueError('TimeInterval should be a blue time (long), recieved ', type(value).__name__, '.')
    try:
        startShowing = TIME_PART_KEYS.index(showFrom)
    except ValueError:
        raise ValueError('Unknown value %s for showFrom' % showFrom)

    try:
        stopShowing = TIME_PART_KEYS.index(showTo)
    except ValueError:
        raise ValueError('Unknown value %s for showTo' % showFrom)

    if stopShowing < startShowing:
        raise ValueError('The from/to pair %s/%s is not a valid combination for TimeInterval.' % (showFrom, showTo))
    if roundUp:
        roundUnit = TIME_INTERVAL_UNITS_VALUE_MAP[showTo]
        value += roundUnit if value % roundUnit > 0 else 0
    returnValues = []
    doShow = False
    for k in TIME_PART_KEYS:
        if k == showFrom:
            doShow = True
        if doShow:
            val = value / TIME_INTERVAL_UNITS_VALUE_MAP[k]
            returnValues.append((k, val))
            value -= TIME_INTERVAL_UNITS_VALUE_MAP[k] * val
            if k == showTo:
                break

    return returnValues


@telemetry.ZONE_FUNCTION
def FormatTimeIntervalShort(value, showFrom = 'year', showTo = 'second'):
    timeParts = _FormatTimeIntervalGetParts(value, showFrom, showTo)
    kwargs = {}
    for i, (partName, part) in enumerate(timeParts):
        key = 'value%s' % (i + 1)
        if partName == TIME_CATEGORY_MILLISECOND:
            kwargs[key] = numericFormatters.FormatNumeric(part, leadingZeroes=3)
        else:
            kwargs[key] = numericFormatters.FormatNumeric(part, leadingZeroes=2)

    if len(timeParts) == 1:
        return kwargs['value1']
    else:
        return GetByLabel(QUANTITY_TIME_SHORT_MAP[len(timeParts)], **kwargs)


def FormatTimeInterval(value, color1 = None, color2 = None):
    timeParts = _FormatTimeIntervalGetParts(value, 'day', 'second')
    timeParts = [ value for _, value in timeParts ]
    color1 = color1 or '#AAFFFFFF'
    color2 = color2 or '#AA999999'
    firstIdx = FindFirstNonZeroIdx(timeParts)
    colors = []
    for i in xrange(4):
        if i >= firstIdx:
            colors.append(color1)
        else:
            colors.append(color2)

    if firstIdx == 0:
        return GetByLabel('/Carbon/UI/Common/DateTimeQuantity/TimeIntervalWithDays', days=timeParts[0], colorDays=colors[0], colorHours=colors[1], hours=timeParts[1], colorMinutes=colors[2], minutes=timeParts[2], colorSeconds=colors[3], seconds=timeParts[3])
    else:
        return GetByLabel('/Carbon/UI/Common/DateTimeQuantity/TimeInterval', colorHours=colors[1], hours=timeParts[1], colorMinutes=colors[2], minutes=timeParts[2], colorSeconds=colors[3], seconds=timeParts[3])


def FindFirstNonZeroIdx(values):
    for i, value in enumerate(values):
        if value:
            return i

    return len(values)


@telemetry.ZONE_FUNCTION
def FormatTimeIntervalShortWritten(value, showFrom = 'year', showTo = 'second'):
    timeParts = _FormatTimeIntervalGetParts(value, showFrom, showTo, roundUp=True)
    kwargs = {}
    lastIdx = len(timeParts) - 1
    for i, (partName, part) in enumerate(timeParts):
        key = 'value%s' % (len(kwargs) + 1)
        if part > 0 or i == lastIdx and not kwargs:
            kwargs[key] = GetByLabel(QUANTITY_TIME_SHORT_WRITTEN_UNITS_MAP[partName], value=part)

    length = len(kwargs)
    if length == 1:
        return kwargs['value1']
    else:
        return GetByLabel(QUANTITY_TIME_SHORT_WRITTEN_MAP[length], **kwargs)


@telemetry.ZONE_FUNCTION
def FormatTimeIntervalWritten(value, showFrom = 'year', showTo = 'second', languageID = None, maxParts = None):
    timeParts = _FormatTimeIntervalGetParts(value, showFrom, showTo)
    timeParts = dict(timeParts)
    return _GetFormattedTimeString(showTo, languageID, maxParts, timeParts)


def _GetFormattedTimeString(showTo, languageID, maxParts, timeParts):
    languageID = langutils.any_to_comfy_language(languageID, default=langutils.get_session_language())
    timeList = []
    if timeParts.get('year', 0) > 0:
        timeList.append(GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Year', languageID=languageID, years=timeParts['year']))
    if timeParts.get('month', 0) > 0:
        timeList.append(GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Month', languageID=languageID, months=timeParts['month']))
    if timeParts.get('week', 0) > 0:
        timeList.append(GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Week', languageID=languageID, weeks=timeParts['week']))
    if timeParts.get('day', 0) > 0:
        timeList.append(GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Day', languageID=languageID, days=timeParts['day']))
    if timeParts.get('hour', 0) > 0:
        timeList.append(GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Hour', languageID=languageID, hours=timeParts['hour']))
    if timeParts.get('minute', 0) > 0:
        timeList.append(GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Minute', languageID=languageID, minutes=timeParts['minute']))
    if timeParts.get('second', 0) > 0:
        timeList.append(GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Second', languageID=languageID, seconds=timeParts['second']))
    if timeParts.get('millisecond', 0) > 0:
        timeList.append(GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Millisecond', languageID=languageID, milliseconds=timeParts['millisecond']))
    if maxParts:
        timeList = timeList[:maxParts]
    length = len(timeList)
    if length == 0:
        dateTimeQuantityLabel = SMALL_WRITTEN_QUANTITY_TIME_MAP[showTo]
        return GetByLabel(dateTimeQuantityLabel, languageID=languageID)
    if length == 1:
        return timeList[0]
    if languageID == langutils.LANG_JA:
        return u''.join(timeList)
    if languageID == langutils.LANG_KO:
        return u' '.join(timeList)
    firstPart = listFormatters.FormatGenericList(timeList[:-1], languageID=languageID)
    lastPart = timeList[-1]
    return GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/ListForm', languageID=languageID, firstPart=firstPart, secondPart=lastPart)


@telemetry.ZONE_FUNCTION
def FormatDateTimeIntervalWritten(startTime, endTime, showFrom = 'year', showTo = 'second', languageID = None, maxParts = None):
    dt1 = filetime_to_datetime(endTime)
    dt2 = filetime_to_datetime(startTime)
    deltaForDates = relativedelta.relativedelta(dt1, dt2)
    timePartsToUse = TIME_PART_KEYS[TIME_PART_KEYS.index(showFrom):TIME_PART_KEYS.index(showTo) + 1]
    timeParts = {}
    for eachPart in timePartsToUse:
        eachPartPlural = eachPart + 's'
        num = getattr(deltaForDates, eachPartPlural, 0)
        if num:
            timeParts[eachPart] = num

    timeParts = dict(timeParts)
    return _GetFormattedTimeString(showTo, languageID, maxParts, timeParts)


@telemetry.ZONE_FUNCTION
def FormatSpecificDurationWritten(duration, type = 'year', languageID = None, maxParts = None):
    timeParts = {}
    timeParts[type] = duration
    timeParts = dict(timeParts)
    return _GetFormattedTimeString(type, languageID, maxParts, timeParts)
