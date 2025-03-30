#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datetimeutils\parsers\timedelta.py
import datetime
import re
_string_types = tuple({type(u''), type('')})
_PERIOD_PART = re.compile('([+-]?(?:\\d+(?:\\.(?:\\d+)?)?|\\.\\d+))\\s*([a-z]+)\\s*', re.IGNORECASE)
_KEYWORDS = {'d': 'days',
 'day': 'days',
 'days': 'days',
 'h': 'hours',
 'hr': 'hours',
 'hrs': 'hours',
 'hour': 'hours',
 'hours': 'hours',
 'm': 'minutes',
 'i': 'minutes',
 'min': 'minutes',
 'mins': 'minutes',
 'minute': 'minutes',
 'minutes': 'minutes',
 's': 'seconds',
 'sec': 'seconds',
 'secs': 'seconds',
 'second': 'seconds',
 'seconds': 'seconds',
 'w': 'weeks',
 'wk': 'weeks',
 'wks': 'weeks',
 'week': 'weeks',
 'weeks': 'weeks'}

def _parse_split(string):
    if string and isinstance(string, _string_types):
        buf = []
        string = string.strip().lower()
        for match in _PERIOD_PART.finditer(string):
            buf.append(match.groups())

        return buf or None


def _timedelta_keywords(list_of_lists):
    kw_map = {}
    for num, kw in list_of_lists:
        kw_map[_KEYWORDS[kw]] = float(num)

    return kw_map


def str_to_timedelta(string, default = 0):
    if default == 0:
        default = datetime.timedelta(seconds=0)
    res = _parse_split(string)
    if res:
        try:
            return datetime.timedelta(**_timedelta_keywords(res))
        except (ValueError, KeyError, IndexError):
            return default

    else:
        return default
