#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dateutil\parser.py
from __future__ import unicode_literals
import datetime
import string
import time
import collections
import re
from io import StringIO
from calendar import monthrange, isleap
from six import text_type, binary_type, integer_types
from . import relativedelta
from . import tz
__all__ = [u'parse', u'parserinfo']

class _timelex(object):
    _split_decimal = re.compile(u'([\\.,])')

    def __init__(self, instream):
        if isinstance(instream, binary_type):
            instream = instream.decode()
        if isinstance(instream, text_type):
            instream = StringIO(instream)
        if getattr(instream, u'read', None) is None:
            raise TypeError(u'Parser must be a string or character stream, not {itype}'.format(itype=instream.__class__.__name__))
        self.instream = instream
        self.charstack = []
        self.tokenstack = []
        self.eof = False

    def get_token(self):
        if self.tokenstack:
            return self.tokenstack.pop(0)
        seenletters = False
        token = None
        state = None
        while not self.eof:
            if self.charstack:
                nextchar = self.charstack.pop(0)
            else:
                nextchar = self.instream.read(1)
                while nextchar == u'\x00':
                    nextchar = self.instream.read(1)

            if not nextchar:
                self.eof = True
                break
            elif not state:
                token = nextchar
                if self.isword(nextchar):
                    state = u'a'
                elif self.isnum(nextchar):
                    state = u'0'
                elif self.isspace(nextchar):
                    token = u' '
                    break
                else:
                    break
            elif state == u'a':
                seenletters = True
                if self.isword(nextchar):
                    token += nextchar
                elif nextchar == u'.':
                    token += nextchar
                    state = u'a.'
                else:
                    self.charstack.append(nextchar)
                    break
            elif state == u'0':
                if self.isnum(nextchar):
                    token += nextchar
                elif nextchar == u'.' or nextchar == u',' and len(token) >= 2:
                    token += nextchar
                    state = u'0.'
                else:
                    self.charstack.append(nextchar)
                    break
            elif state == u'a.':
                seenletters = True
                if nextchar == u'.' or self.isword(nextchar):
                    token += nextchar
                elif self.isnum(nextchar) and token[-1] == u'.':
                    token += nextchar
                    state = u'0.'
                else:
                    self.charstack.append(nextchar)
                    break
            elif state == u'0.':
                if nextchar == u'.' or self.isnum(nextchar):
                    token += nextchar
                elif self.isword(nextchar) and token[-1] == u'.':
                    token += nextchar
                    state = u'a.'
                else:
                    self.charstack.append(nextchar)
                    break

        if state in (u'a.', u'0.') and (seenletters or token.count(u'.') > 1 or token[-1] in u'.,'):
            l = self._split_decimal.split(token)
            token = l[0]
            for tok in l[1:]:
                if tok:
                    self.tokenstack.append(tok)

        if state == u'0.' and token.count(u'.') == 0:
            token = token.replace(u',', u'.')
        return token

    def __iter__(self):
        return self

    def __next__(self):
        token = self.get_token()
        if token is None:
            raise StopIteration
        return token

    def next(self):
        return self.__next__()

    @classmethod
    def split(cls, s):
        return list(cls(s))

    @classmethod
    def isword(cls, nextchar):
        return nextchar.isalpha()

    @classmethod
    def isnum(cls, nextchar):
        return nextchar.isdigit()

    @classmethod
    def isspace(cls, nextchar):
        return nextchar.isspace()


class _resultbase(object):

    def __init__(self):
        for attr in self.__slots__:
            setattr(self, attr, None)

    def _repr(self, classname):
        l = []
        for attr in self.__slots__:
            value = getattr(self, attr)
            if value is not None:
                l.append(u'%s=%s' % (attr, repr(value)))

        return u'%s(%s)' % (classname, u', '.join(l))

    def __len__(self):
        return sum((getattr(self, attr) is not None for attr in self.__slots__))

    def __repr__(self):
        return self._repr(self.__class__.__name__)


class parserinfo(object):
    JUMP = [u' ',
     u'.',
     u',',
     u';',
     u'-',
     u'/',
     u"'",
     u'at',
     u'on',
     u'and',
     u'ad',
     u'm',
     u't',
     u'of',
     u'st',
     u'nd',
     u'rd',
     u'th']
    WEEKDAYS = [(u'Mon', u'Monday'),
     (u'Tue', u'Tuesday'),
     (u'Wed', u'Wednesday'),
     (u'Thu', u'Thursday'),
     (u'Fri', u'Friday'),
     (u'Sat', u'Saturday'),
     (u'Sun', u'Sunday')]
    MONTHS = [(u'Jan', u'January'),
     (u'Feb', u'February'),
     (u'Mar', u'March'),
     (u'Apr', u'April'),
     (u'May', u'May'),
     (u'Jun', u'June'),
     (u'Jul', u'July'),
     (u'Aug', u'August'),
     (u'Sep', u'Sept', u'September'),
     (u'Oct', u'October'),
     (u'Nov', u'November'),
     (u'Dec', u'December')]
    HMS = [(u'h', u'hour', u'hours'), (u'm', u'minute', u'minutes'), (u's', u'second', u'seconds')]
    AMPM = [(u'am', u'a'), (u'pm', u'p')]
    UTCZONE = [u'UTC', u'GMT', u'Z']
    PERTAIN = [u'of']
    TZOFFSET = {}

    def __init__(self, dayfirst = False, yearfirst = False):
        self._jump = self._convert(self.JUMP)
        self._weekdays = self._convert(self.WEEKDAYS)
        self._months = self._convert(self.MONTHS)
        self._hms = self._convert(self.HMS)
        self._ampm = self._convert(self.AMPM)
        self._utczone = self._convert(self.UTCZONE)
        self._pertain = self._convert(self.PERTAIN)
        self.dayfirst = dayfirst
        self.yearfirst = yearfirst
        self._year = time.localtime().tm_year
        self._century = self._year // 100 * 100

    def _convert(self, lst):
        dct = {}
        for i, v in enumerate(lst):
            if isinstance(v, tuple):
                for v in v:
                    dct[v.lower()] = i

            else:
                dct[v.lower()] = i

        return dct

    def jump(self, name):
        return name.lower() in self._jump

    def weekday(self, name):
        if len(name) >= 3:
            try:
                return self._weekdays[name.lower()]
            except KeyError:
                pass

    def month(self, name):
        if len(name) >= 3:
            try:
                return self._months[name.lower()] + 1
            except KeyError:
                pass

    def hms(self, name):
        try:
            return self._hms[name.lower()]
        except KeyError:
            return None

    def ampm(self, name):
        try:
            return self._ampm[name.lower()]
        except KeyError:
            return None

    def pertain(self, name):
        return name.lower() in self._pertain

    def utczone(self, name):
        return name.lower() in self._utczone

    def tzoffset(self, name):
        if name in self._utczone:
            return 0
        return self.TZOFFSET.get(name)

    def convertyear(self, year, century_specified = False):
        if year < 100 and not century_specified:
            year += self._century
            if abs(year - self._year) >= 50:
                if year < self._year:
                    year += 100
                else:
                    year -= 100
        return year

    def validate(self, res):
        if res.year is not None:
            res.year = self.convertyear(res.year, res.century_specified)
        if res.tzoffset == 0 and not res.tzname or res.tzname == u'Z':
            res.tzname = u'UTC'
            res.tzoffset = 0
        elif res.tzoffset != 0 and res.tzname and self.utczone(res.tzname):
            res.tzoffset = 0
        return True


class _ymd(list):

    def __init__(self, tzstr, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.century_specified = False
        self.tzstr = tzstr

    @staticmethod
    def token_could_be_year(token, year):
        try:
            return int(token) == year
        except ValueError:
            return False

    @staticmethod
    def find_potential_year_tokens(year, tokens):
        return [ token for token in tokens if _ymd.token_could_be_year(token, year) ]

    def find_probable_year_index(self, tokens):
        for index, token in enumerate(self):
            potential_year_tokens = _ymd.find_potential_year_tokens(token, tokens)
            if len(potential_year_tokens) == 1 and len(potential_year_tokens[0]) > 2:
                return index

    def append(self, val):
        if hasattr(val, u'__len__'):
            if val.isdigit() and len(val) > 2:
                self.century_specified = True
        elif val > 100:
            self.century_specified = True
        super(self.__class__, self).append(int(val))

    def resolve_ymd(self, mstridx, yearfirst, dayfirst):
        len_ymd = len(self)
        year, month, day = (None, None, None)
        if len_ymd > 3:
            raise ValueError(u'More than three YMD values')
        elif len_ymd == 1 or mstridx != -1 and len_ymd == 2:
            if mstridx != -1:
                month = self[mstridx]
                del self[mstridx]
            if len_ymd > 1 or mstridx == -1:
                if self[0] > 31:
                    year = self[0]
                else:
                    day = self[0]
        elif len_ymd == 2:
            if self[0] > 31:
                year, month = self
            elif self[1] > 31:
                month, year = self
            elif dayfirst and self[1] <= 12:
                day, month = self
            else:
                month, day = self
        elif len_ymd == 3:
            if mstridx == 0:
                month, day, year = self
            elif mstridx == 1:
                if self[0] > 31 or yearfirst and self[2] <= 31:
                    year, month, day = self
                else:
                    day, month, year = self
            elif mstridx == 2:
                if self[1] > 31:
                    day, year, month = self
                else:
                    year, day, month = self
            elif self[0] > 31 or self.find_probable_year_index(_timelex.split(self.tzstr)) == 0 or yearfirst and self[1] <= 12 and self[2] <= 31:
                if dayfirst and self[2] <= 12:
                    year, day, month = self
                else:
                    year, month, day = self
            elif self[0] > 12 or dayfirst and self[1] <= 12:
                day, month, year = self
            else:
                month, day, year = self
        return (year, month, day)


class parser(object):

    def __init__(self, info = None):
        self.info = info or parserinfo()

    def parse(self, timestr, default = None, ignoretz = False, tzinfos = None, **kwargs):
        if default is None:
            effective_dt = datetime.datetime.now()
            default = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            effective_dt = default
        res, skipped_tokens = self._parse(timestr, **kwargs)
        if res is None:
            raise ValueError(u'Unknown string format')
        if len(res) == 0:
            raise ValueError(u'String does not contain a date.')
        repl = {}
        for attr in (u'year', u'month', u'day', u'hour', u'minute', u'second', u'microsecond'):
            value = getattr(res, attr)
            if value is not None:
                repl[attr] = value

        if u'day' not in repl:
            cyear = default.year if res.year is None else res.year
            cmonth = default.month if res.month is None else res.month
            cday = default.day if res.day is None else res.day
            if cday > monthrange(cyear, cmonth)[1]:
                repl[u'day'] = monthrange(cyear, cmonth)[1]
        ret = default.replace(**repl)
        if res.weekday is not None and not res.day:
            ret = ret + relativedelta.relativedelta(weekday=res.weekday)
        if not ignoretz:
            if isinstance(tzinfos, collections.Callable) or tzinfos and res.tzname in tzinfos:
                if isinstance(tzinfos, collections.Callable):
                    tzdata = tzinfos(res.tzname, res.tzoffset)
                else:
                    tzdata = tzinfos.get(res.tzname)
                if isinstance(tzdata, datetime.tzinfo):
                    tzinfo = tzdata
                elif isinstance(tzdata, text_type):
                    tzinfo = tz.tzstr(tzdata)
                elif isinstance(tzdata, integer_types):
                    tzinfo = tz.tzoffset(res.tzname, tzdata)
                else:
                    raise ValueError(u'Offset must be tzinfo subclass, tz string, or int offset.')
                ret = ret.replace(tzinfo=tzinfo)
            elif res.tzname and res.tzname in time.tzname:
                ret = ret.replace(tzinfo=tz.tzlocal())
            elif res.tzoffset == 0:
                ret = ret.replace(tzinfo=tz.tzutc())
            elif res.tzoffset:
                ret = ret.replace(tzinfo=tz.tzoffset(res.tzname, res.tzoffset))
        if kwargs.get(u'fuzzy_with_tokens', False):
            return (ret, skipped_tokens)
        else:
            return ret

    class _result(_resultbase):
        __slots__ = [u'year',
         u'month',
         u'day',
         u'weekday',
         u'hour',
         u'minute',
         u'second',
         u'microsecond',
         u'tzname',
         u'tzoffset',
         u'ampm']

    def _parse(self, timestr, dayfirst = None, yearfirst = None, fuzzy = False, fuzzy_with_tokens = False):
        if fuzzy_with_tokens:
            fuzzy = True
        info = self.info
        if dayfirst is None:
            dayfirst = info.dayfirst
        if yearfirst is None:
            yearfirst = info.yearfirst
        res = self._result()
        l = _timelex.split(timestr)
        last_skipped_token_i = -2
        skipped_tokens = list()
        try:
            ymd = _ymd(timestr)
            mstridx = -1
            len_l = len(l)
            i = 0
            while i < len_l:
                try:
                    value_repr = l[i]
                    value = float(value_repr)
                except ValueError:
                    value = None

                if value is not None:
                    len_li = len(l[i])
                    i += 1
                    if len(ymd) == 3 and len_li in (2, 4) and res.hour is None and (i >= len_l or l[i] != u':' and info.hms(l[i]) is None):
                        s = l[i - 1]
                        res.hour = int(s[:2])
                        if len_li == 4:
                            res.minute = int(s[2:])
                    elif len_li == 6 or len_li > 6 and l[i - 1].find(u'.') == 6:
                        s = l[i - 1]
                        if not ymd and l[i - 1].find(u'.') == -1:
                            ymd.append(s[:2])
                            ymd.append(s[2:4])
                            ymd.append(s[4:])
                        else:
                            res.hour = int(s[:2])
                            res.minute = int(s[2:4])
                            res.second, res.microsecond = _parsems(s[4:])
                    elif len_li in (8, 12, 14):
                        s = l[i - 1]
                        ymd.append(s[:4])
                        ymd.append(s[4:6])
                        ymd.append(s[6:8])
                        if len_li > 8:
                            res.hour = int(s[8:10])
                            res.minute = int(s[10:12])
                            if len_li > 12:
                                res.second = int(s[12:])
                    elif i < len_l and info.hms(l[i]) is not None or i + 1 < len_l and l[i] == u' ' and info.hms(l[i + 1]) is not None:
                        if l[i] == u' ':
                            i += 1
                        idx = info.hms(l[i])
                        while True:
                            if idx == 0:
                                res.hour = int(value)
                                if value % 1:
                                    res.minute = int(60 * (value % 1))
                            elif idx == 1:
                                res.minute = int(value)
                                if value % 1:
                                    res.second = int(60 * (value % 1))
                            elif idx == 2:
                                res.second, res.microsecond = _parsems(value_repr)
                            i += 1
                            if i >= len_l or idx == 2:
                                break
                            try:
                                value_repr = l[i]
                                value = float(value_repr)
                            except ValueError:
                                break
                            else:
                                i += 1
                                idx += 1
                                if i < len_l:
                                    newidx = info.hms(l[i])
                                    if newidx is not None:
                                        idx = newidx

                    elif i == len_l and l[i - 2] == u' ' and info.hms(l[i - 3]) is not None:
                        idx = info.hms(l[i - 3]) + 1
                        if idx == 1:
                            res.minute = int(value)
                            if value % 1:
                                res.second = int(60 * (value % 1))
                            elif idx == 2:
                                res.second, res.microsecond = _parsems(value_repr)
                                i += 1
                    elif i + 1 < len_l and l[i] == u':':
                        res.hour = int(value)
                        i += 1
                        value = float(l[i])
                        res.minute = int(value)
                        if value % 1:
                            res.second = int(60 * (value % 1))
                        i += 1
                        if i < len_l and l[i] == u':':
                            res.second, res.microsecond = _parsems(l[i + 1])
                            i += 2
                    elif i < len_l and l[i] in (u'-', u'/', u'.'):
                        sep = l[i]
                        ymd.append(value_repr)
                        i += 1
                        if i < len_l and not info.jump(l[i]):
                            try:
                                ymd.append(l[i])
                            except ValueError:
                                value = info.month(l[i])
                                if value is not None:
                                    ymd.append(value)
                                    mstridx = len(ymd) - 1
                                else:
                                    return (None, None)

                            i += 1
                            if i < len_l and l[i] == sep:
                                i += 1
                                value = info.month(l[i])
                                if value is not None:
                                    ymd.append(value)
                                    mstridx = len(ymd) - 1
                                else:
                                    ymd.append(l[i])
                                i += 1
                    elif i >= len_l or info.jump(l[i]):
                        if i + 1 < len_l and info.ampm(l[i + 1]) is not None:
                            res.hour = int(value)
                            if res.hour < 12 and info.ampm(l[i + 1]) == 1:
                                res.hour += 12
                            elif res.hour == 12 and info.ampm(l[i + 1]) == 0:
                                res.hour = 0
                            i += 1
                        else:
                            ymd.append(value)
                        i += 1
                    elif info.ampm(l[i]) is not None:
                        res.hour = int(value)
                        if res.hour < 12 and info.ampm(l[i]) == 1:
                            res.hour += 12
                        elif res.hour == 12 and info.ampm(l[i]) == 0:
                            res.hour = 0
                        i += 1
                    else:
                        if not fuzzy:
                            return (None, None)
                        i += 1
                    continue
                value = info.weekday(l[i])
                if value is not None:
                    res.weekday = value
                    i += 1
                    continue
                value = info.month(l[i])
                if value is not None:
                    ymd.append(value)
                    mstridx = len(ymd) - 1
                    i += 1
                    if i < len_l:
                        if l[i] in (u'-', u'/'):
                            sep = l[i]
                            i += 1
                            ymd.append(l[i])
                            i += 1
                            if i < len_l and l[i] == sep:
                                i += 1
                                ymd.append(l[i])
                                i += 1
                        elif i + 3 < len_l and l[i] == l[i + 2] == u' ' and info.pertain(l[i + 1]):
                            try:
                                value = int(l[i + 3])
                            except ValueError:
                                pass
                            else:
                                ymd.append(str(info.convertyear(value)))

                            i += 4
                    continue
                value = info.ampm(l[i])
                if value is not None:
                    val_is_ampm = True
                    if fuzzy and res.ampm is not None:
                        val_is_ampm = False
                    if res.hour is None:
                        if fuzzy:
                            val_is_ampm = False
                        else:
                            raise ValueError(u'No hour specified with ' + u'AM or PM flag.')
                    elif not 0 <= res.hour <= 12:
                        if fuzzy:
                            val_is_ampm = False
                        else:
                            raise ValueError(u'Invalid hour specified for ' + u'12-hour clock.')
                    if val_is_ampm:
                        if value == 1 and res.hour < 12:
                            res.hour += 12
                        elif value == 0 and res.hour == 12:
                            res.hour = 0
                        res.ampm = value
                    i += 1
                    continue
                if res.hour is not None and len(l[i]) <= 5 and res.tzname is None and res.tzoffset is None and not [ x for x in l[i] if x not in string.ascii_uppercase ]:
                    res.tzname = l[i]
                    res.tzoffset = info.tzoffset(res.tzname)
                    i += 1
                    if i < len_l and l[i] in (u'+', u'-'):
                        l[i] = (u'+', u'-')[l[i] == u'+']
                        res.tzoffset = None
                        if info.utczone(res.tzname):
                            res.tzname = None
                    continue
                if res.hour is not None and l[i] in (u'+', u'-'):
                    signal = (-1, 1)[l[i] == u'+']
                    i += 1
                    len_li = len(l[i])
                    if len_li == 4:
                        res.tzoffset = int(l[i][:2]) * 3600 + int(l[i][2:]) * 60
                    elif i + 1 < len_l and l[i + 1] == u':':
                        res.tzoffset = int(l[i]) * 3600 + int(l[i + 2]) * 60
                        i += 2
                    elif len_li <= 2:
                        res.tzoffset = int(l[i][:2]) * 3600
                    else:
                        return (None, None)
                    i += 1
                    res.tzoffset *= signal
                    if i + 3 < len_l and info.jump(l[i]) and l[i + 1] == u'(' and l[i + 3] == u')' and 3 <= len(l[i + 2]) <= 5 and not [ x for x in l[i + 2] if x not in string.ascii_uppercase ]:
                        res.tzname = l[i + 2]
                        i += 4
                    continue
                if not (info.jump(l[i]) or fuzzy):
                    return (None, None)
                if last_skipped_token_i == i - 1:
                    skipped_tokens[-1] += l[i]
                else:
                    skipped_tokens.append(l[i])
                last_skipped_token_i = i
                i += 1

            year, month, day = ymd.resolve_ymd(mstridx, yearfirst, dayfirst)
            if year is not None:
                res.year = year
                res.century_specified = ymd.century_specified
            if month is not None:
                res.month = month
            if day is not None:
                res.day = day
        except (IndexError, ValueError, AssertionError):
            return (None, None)

        if not info.validate(res):
            return (None, None)
        elif fuzzy_with_tokens:
            return (res, tuple(skipped_tokens))
        else:
            return (res, None)


DEFAULTPARSER = parser()

def parse(timestr, parserinfo = None, **kwargs):
    if parserinfo:
        return parser(parserinfo).parse(timestr, **kwargs)
    else:
        return DEFAULTPARSER.parse(timestr, **kwargs)


class _tzparser(object):

    class _result(_resultbase):
        __slots__ = [u'stdabbr',
         u'stdoffset',
         u'dstabbr',
         u'dstoffset',
         u'start',
         u'end']

        class _attr(_resultbase):
            __slots__ = [u'month',
             u'week',
             u'weekday',
             u'yday',
             u'jyday',
             u'day',
             u'time']

        def __repr__(self):
            return self._repr(u'')

        def __init__(self):
            _resultbase.__init__(self)
            self.start = self._attr()
            self.end = self._attr()

    def parse(self, tzstr):
        res = self._result()
        l = _timelex.split(tzstr)
        try:
            len_l = len(l)
            i = 0
            while i < len_l:
                j = i
                while j < len_l and not [ x for x in l[j] if x in u'0123456789:,-+' ]:
                    j += 1

                if j != i:
                    if not res.stdabbr:
                        offattr = u'stdoffset'
                        res.stdabbr = u''.join(l[i:j])
                    else:
                        offattr = u'dstoffset'
                        res.dstabbr = u''.join(l[i:j])
                    i = j
                    if i < len_l and (l[i] in (u'+', u'-') or l[i][0] in u'0123456789'):
                        if l[i] in (u'+', u'-'):
                            signal = (1, -1)[l[i] == u'+']
                            i += 1
                        else:
                            signal = -1
                        len_li = len(l[i])
                        if len_li == 4:
                            setattr(res, offattr, (int(l[i][:2]) * 3600 + int(l[i][2:]) * 60) * signal)
                        elif i + 1 < len_l and l[i + 1] == u':':
                            setattr(res, offattr, (int(l[i]) * 3600 + int(l[i + 2]) * 60) * signal)
                            i += 2
                        elif len_li <= 2:
                            setattr(res, offattr, int(l[i][:2]) * 3600 * signal)
                        else:
                            return None
                        i += 1
                    if res.dstabbr:
                        break
                else:
                    break

            if i < len_l:
                for j in range(i, len_l):
                    if l[j] == u';':
                        l[j] = u','

                i += 1
            if i >= len_l:
                pass
            elif 8 <= l.count(u',') <= 9 and not [ y for x in l[i:] if x != u',' for y in x if y not in u'0123456789' ]:
                for x in (res.start, res.end):
                    x.month = int(l[i])
                    i += 2
                    if l[i] == u'-':
                        value = int(l[i + 1]) * -1
                        i += 1
                    else:
                        value = int(l[i])
                    i += 2
                    if value:
                        x.week = value
                        x.weekday = (int(l[i]) - 1) % 7
                    else:
                        x.day = int(l[i])
                    i += 2
                    x.time = int(l[i])
                    i += 2

                if i < len_l:
                    if l[i] in (u'-', u'+'):
                        signal = (-1, 1)[l[i] == u'+']
                        i += 1
                    else:
                        signal = 1
                    res.dstoffset = (res.stdoffset + int(l[i])) * signal
            elif l.count(u',') == 2 and l[i:].count(u'/') <= 2 and not [ y for x in l[i:] if x not in (u',', u'/', u'J', u'M', u'.', u'-', u':') for y in x if y not in u'0123456789' ]:
                for x in (res.start, res.end):
                    if l[i] == u'J':
                        i += 1
                        x.jyday = int(l[i])
                    elif l[i] == u'M':
                        i += 1
                        x.month = int(l[i])
                        i += 1
                        i += 1
                        x.week = int(l[i])
                        if x.week == 5:
                            x.week = -1
                        i += 1
                        i += 1
                        x.weekday = (int(l[i]) - 1) % 7
                    else:
                        x.yday = int(l[i]) + 1
                    i += 1
                    if i < len_l and l[i] == u'/':
                        i += 1
                        len_li = len(l[i])
                        if len_li == 4:
                            x.time = int(l[i][:2]) * 3600 + int(l[i][2:]) * 60
                        elif i + 1 < len_l and l[i + 1] == u':':
                            x.time = int(l[i]) * 3600 + int(l[i + 2]) * 60
                            i += 2
                            if i + 1 < len_l and l[i + 1] == u':':
                                i += 2
                                x.time += int(l[i])
                        elif len_li <= 2:
                            x.time = int(l[i][:2]) * 3600
                        else:
                            return None
                        i += 1
                    i += 1

        except (IndexError, ValueError, AssertionError):
            return None

        return res


DEFAULTTZPARSER = _tzparser()

def _parsetz(tzstr):
    return DEFAULTTZPARSER.parse(tzstr)


def _parsems(value):
    if u'.' not in value:
        return (int(value), 0)
    else:
        i, f = value.split(u'.')
        return (int(i), int(f.ljust(6, u'0')[:6]))
