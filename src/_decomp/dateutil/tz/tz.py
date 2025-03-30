#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dateutil\tz\tz.py
import datetime
import struct
import time
import sys
import os
import bisect
import copy
from operator import itemgetter
from contextlib import contextmanager
from six import string_types, PY3
from ._common import tzname_in_python2, _tzinfo, _total_seconds
from ._common import tzrangebase, enfold
try:
    from .win import tzwin, tzwinlocal
except ImportError:
    tzwin = tzwinlocal = None

ZERO = datetime.timedelta(0)
EPOCH = datetime.datetime.utcfromtimestamp(0)
EPOCHORDINAL = EPOCH.toordinal()

class tzutc(datetime.tzinfo):

    def utcoffset(self, dt):
        return ZERO

    def dst(self, dt):
        return ZERO

    @tzname_in_python2
    def tzname(self, dt):
        return 'UTC'

    def is_ambiguous(self, dt):
        return False

    def __eq__(self, other):
        if not isinstance(other, (tzutc, tzoffset)):
            return NotImplemented
        return isinstance(other, tzutc) or isinstance(other, tzoffset) and other._offset == ZERO

    __hash__ = None

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '%s()' % self.__class__.__name__

    __reduce__ = object.__reduce__


class tzoffset(datetime.tzinfo):

    def __init__(self, name, offset):
        self._name = name
        try:
            offset = _total_seconds(offset)
        except (TypeError, AttributeError):
            pass

        self._offset = datetime.timedelta(seconds=offset)

    def utcoffset(self, dt):
        return self._offset

    def dst(self, dt):
        return ZERO

    def is_ambiguous(self, dt):
        return False

    @tzname_in_python2
    def tzname(self, dt):
        return self._name

    def __eq__(self, other):
        if not isinstance(other, tzoffset):
            return NotImplemented
        return self._offset == other._offset

    __hash__ = None

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, repr(self._name), int(_total_seconds(self._offset)))

    __reduce__ = object.__reduce__


class tzlocal(_tzinfo):

    def __init__(self):
        super(tzlocal, self).__init__()
        self._std_offset = datetime.timedelta(seconds=-time.timezone)
        if time.daylight:
            self._dst_offset = datetime.timedelta(seconds=-time.altzone)
        else:
            self._dst_offset = self._std_offset
        self._dst_saved = self._dst_offset - self._std_offset
        self._hasdst = bool(self._dst_saved)

    def utcoffset(self, dt):
        if dt is None and self._hasdst:
            return
        elif self._isdst(dt):
            return self._dst_offset
        else:
            return self._std_offset

    def dst(self, dt):
        if dt is None and self._hasdst:
            return
        elif self._isdst(dt):
            return self._dst_offset - self._std_offset
        else:
            return ZERO

    @tzname_in_python2
    def tzname(self, dt):
        return time.tzname[self._isdst(dt)]

    def is_ambiguous(self, dt):
        naive_dst = self._naive_is_dst(dt)
        return not naive_dst and naive_dst != self._naive_is_dst(dt - self._dst_saved)

    def _naive_is_dst(self, dt):
        timestamp = _datetime_to_timestamp(dt)
        return time.localtime(timestamp + time.timezone).tm_isdst

    def _isdst(self, dt, fold_naive = True):
        if not self._hasdst:
            return False
        dstval = self._naive_is_dst(dt)
        fold = getattr(dt, 'fold', None)
        if self.is_ambiguous(dt):
            if fold is not None:
                return not self._fold(dt)
            else:
                return True
        return dstval

    def __eq__(self, other):
        if not isinstance(other, tzlocal):
            return NotImplemented
        return self._std_offset == other._std_offset and self._dst_offset == other._dst_offset

    __hash__ = None

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '%s()' % self.__class__.__name__

    __reduce__ = object.__reduce__


class _ttinfo(object):
    __slots__ = ['offset',
     'delta',
     'isdst',
     'abbr',
     'isstd',
     'isgmt',
     'dstoffset']

    def __init__(self):
        for attr in self.__slots__:
            setattr(self, attr, None)

    def __repr__(self):
        l = []
        for attr in self.__slots__:
            value = getattr(self, attr)
            if value is not None:
                l.append('%s=%s' % (attr, repr(value)))

        return '%s(%s)' % (self.__class__.__name__, ', '.join(l))

    def __eq__(self, other):
        if not isinstance(other, _ttinfo):
            return NotImplemented
        return self.offset == other.offset and self.delta == other.delta and self.isdst == other.isdst and self.abbr == other.abbr and self.isstd == other.isstd and self.isgmt == other.isgmt and self.dstoffset == other.dstoffset

    __hash__ = None

    def __ne__(self, other):
        return not self == other

    def __getstate__(self):
        state = {}
        for name in self.__slots__:
            state[name] = getattr(self, name, None)

        return state

    def __setstate__(self, state):
        for name in self.__slots__:
            if name in state:
                setattr(self, name, state[name])


class _tzfile(object):
    attrs = ['trans_list',
     'trans_idx',
     'ttinfo_list',
     'ttinfo_std',
     'ttinfo_dst',
     'ttinfo_before',
     'ttinfo_first']

    def __init__(self, **kwargs):
        for attr in self.attrs:
            setattr(self, attr, kwargs.get(attr, None))


class tzfile(_tzinfo):

    def __init__(self, fileobj, filename = None):
        super(tzfile, self).__init__()
        file_opened_here = False
        if isinstance(fileobj, string_types):
            self._filename = fileobj
            fileobj = open(fileobj, 'rb')
            file_opened_here = True
        elif filename is not None:
            self._filename = filename
        elif hasattr(fileobj, 'name'):
            self._filename = fileobj.name
        else:
            self._filename = repr(fileobj)
        if fileobj is not None:
            if not file_opened_here:
                fileobj = _ContextWrapper(fileobj)
            with fileobj as file_stream:
                tzobj = self._read_tzfile(file_stream)
            self._set_tzdata(tzobj)

    def _set_tzdata(self, tzobj):
        for attr in _tzfile.attrs:
            setattr(self, '_' + attr, getattr(tzobj, attr))

    def _read_tzfile(self, fileobj):
        out = _tzfile()
        if fileobj.read(4).decode() != 'TZif':
            raise ValueError('magic not found')
        fileobj.read(16)
        ttisgmtcnt, ttisstdcnt, leapcnt, timecnt, typecnt, charcnt = struct.unpack('>6l', fileobj.read(24))
        if timecnt:
            out.trans_list = list(struct.unpack('>%dl' % timecnt, fileobj.read(timecnt * 4)))
        else:
            out.trans_list = []
        if timecnt:
            out.trans_idx = struct.unpack('>%dB' % timecnt, fileobj.read(timecnt))
        else:
            out.trans_idx = []
        ttinfo = []
        for i in range(typecnt):
            ttinfo.append(struct.unpack('>lbb', fileobj.read(6)))

        abbr = fileobj.read(charcnt).decode()
        if leapcnt:
            leap = struct.unpack('>%dl' % (leapcnt * 2), fileobj.read(leapcnt * 8))
        if ttisstdcnt:
            isstd = struct.unpack('>%db' % ttisstdcnt, fileobj.read(ttisstdcnt))
        if ttisgmtcnt:
            isgmt = struct.unpack('>%db' % ttisgmtcnt, fileobj.read(ttisgmtcnt))
        out.ttinfo_list = []
        for i in range(typecnt):
            gmtoff, isdst, abbrind = ttinfo[i]
            gmtoff = 60 * ((gmtoff + 30) // 60)
            tti = _ttinfo()
            tti.offset = gmtoff
            tti.dstoffset = datetime.timedelta(0)
            tti.delta = datetime.timedelta(seconds=gmtoff)
            tti.isdst = isdst
            tti.abbr = abbr[abbrind:abbr.find('\x00', abbrind)]
            tti.isstd = ttisstdcnt > i and isstd[i] != 0
            tti.isgmt = ttisgmtcnt > i and isgmt[i] != 0
            out.ttinfo_list.append(tti)

        out.trans_idx = [ out.ttinfo_list[idx] for idx in out.trans_idx ]
        out.ttinfo_std = None
        out.ttinfo_dst = None
        out.ttinfo_before = None
        if out.ttinfo_list:
            if not out.trans_list:
                out.ttinfo_std = out.ttinfo_first = out.ttinfo_list[0]
            else:
                for i in range(timecnt - 1, -1, -1):
                    tti = out.trans_idx[i]
                    if not out.ttinfo_std and not tti.isdst:
                        out.ttinfo_std = tti
                    elif not out.ttinfo_dst and tti.isdst:
                        out.ttinfo_dst = tti
                    if out.ttinfo_std and out.ttinfo_dst:
                        break
                else:
                    if out.ttinfo_dst and not out.ttinfo_std:
                        out.ttinfo_std = out.ttinfo_dst

                for tti in out.ttinfo_list:
                    if not tti.isdst:
                        out.ttinfo_before = tti
                        break
                else:
                    out.ttinfo_before = out.ttinfo_list[0]

        laststdoffset = None
        for i, tti in enumerate(out.trans_idx):
            if not tti.isdst:
                offset = tti.offset
                laststdoffset = offset
            else:
                if laststdoffset is not None:
                    tti.dstoffset = tti.offset - laststdoffset
                    out.trans_idx[i] = tti
                offset = laststdoffset or 0
            out.trans_list[i] += offset

        laststdoffset = None
        for i in reversed(range(len(out.trans_idx))):
            tti = out.trans_idx[i]
            if tti.isdst:
                if not (tti.dstoffset or laststdoffset is None):
                    tti.dstoffset = tti.offset - laststdoffset
            else:
                laststdoffset = tti.offset
            if not isinstance(tti.dstoffset, datetime.timedelta):
                tti.dstoffset = datetime.timedelta(seconds=tti.dstoffset)
            out.trans_idx[i] = tti

        out.trans_idx = tuple(out.trans_idx)
        out.trans_list = tuple(out.trans_list)
        return out

    def _find_last_transition(self, dt):
        if not self._trans_list:
            return None
        timestamp = _datetime_to_timestamp(dt)
        idx = bisect.bisect_right(self._trans_list, timestamp)
        return idx - 1

    def _get_ttinfo(self, idx):
        if idx is None or idx + 1 == len(self._trans_list):
            return self._ttinfo_std
        if idx < 0:
            return self._ttinfo_before
        return self._trans_idx[idx]

    def _find_ttinfo(self, dt):
        idx = self._resolve_ambiguous_time(dt)
        return self._get_ttinfo(idx)

    def is_ambiguous(self, dt, idx = None):
        if idx is None:
            idx = self._find_last_transition(dt)
        timestamp = _datetime_to_timestamp(dt)
        tti = self._get_ttinfo(idx)
        if idx is None or idx <= 0:
            return False
        od = self._get_ttinfo(idx - 1).offset - tti.offset
        tt = self._trans_list[idx]
        return timestamp < tt + od

    def _resolve_ambiguous_time(self, dt):
        idx = self._find_last_transition(dt)
        _fold = self._fold(dt)
        if idx is None or idx == 0:
            return idx
        idx_offset = int(not _fold and self.is_ambiguous(dt, idx))
        return idx - idx_offset

    def utcoffset(self, dt):
        if dt is None:
            return
        if not self._ttinfo_std:
            return ZERO
        return self._find_ttinfo(dt).delta

    def dst(self, dt):
        if dt is None:
            return
        if not self._ttinfo_dst:
            return ZERO
        tti = self._find_ttinfo(dt)
        if not tti.isdst:
            return ZERO
        return tti.dstoffset

    @tzname_in_python2
    def tzname(self, dt):
        if not self._ttinfo_std or dt is None:
            return
        return self._find_ttinfo(dt).abbr

    def __eq__(self, other):
        if not isinstance(other, tzfile):
            return NotImplemented
        return self._trans_list == other._trans_list and self._trans_idx == other._trans_idx and self._ttinfo_list == other._ttinfo_list

    __hash__ = None

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, repr(self._filename))

    def __reduce__(self):
        return self.__reduce_ex__(None)

    def __reduce_ex__(self, protocol):
        return (self.__class__, (None, self._filename), self.__dict__)


class tzrange(tzrangebase):

    def __init__(self, stdabbr, stdoffset = None, dstabbr = None, dstoffset = None, start = None, end = None):
        global relativedelta
        from dateutil import relativedelta
        self._std_abbr = stdabbr
        self._dst_abbr = dstabbr
        try:
            stdoffset = _total_seconds(stdoffset)
        except (TypeError, AttributeError):
            pass

        try:
            dstoffset = _total_seconds(dstoffset)
        except (TypeError, AttributeError):
            pass

        if stdoffset is not None:
            self._std_offset = datetime.timedelta(seconds=stdoffset)
        else:
            self._std_offset = ZERO
        if dstoffset is not None:
            self._dst_offset = datetime.timedelta(seconds=dstoffset)
        elif dstabbr and stdoffset is not None:
            self._dst_offset = self._std_offset + datetime.timedelta(hours=+1)
        else:
            self._dst_offset = ZERO
        if dstabbr and start is None:
            self._start_delta = relativedelta.relativedelta(hours=+2, month=4, day=1, weekday=relativedelta.SU(+1))
        else:
            self._start_delta = start
        if dstabbr and end is None:
            self._end_delta = relativedelta.relativedelta(hours=+1, month=10, day=31, weekday=relativedelta.SU(-1))
        else:
            self._end_delta = end
        self._dst_base_offset_ = self._dst_offset - self._std_offset
        self.hasdst = bool(self._start_delta)

    def transitions(self, year):
        if not self.hasdst:
            return None
        base_year = datetime.datetime(year, 1, 1)
        start = base_year + self._start_delta
        end = base_year + self._end_delta
        return (start, end)

    def __eq__(self, other):
        if not isinstance(other, tzrange):
            return NotImplemented
        return self._std_abbr == other._std_abbr and self._dst_abbr == other._dst_abbr and self._std_offset == other._std_offset and self._dst_offset == other._dst_offset and self._start_delta == other._start_delta and self._end_delta == other._end_delta

    @property
    def _dst_base_offset(self):
        return self._dst_base_offset_


class tzstr(tzrange):

    def __init__(self, s, posix_offset = False):
        global parser
        from dateutil import parser
        self._s = s
        res = parser._parsetz(s)
        if res is None:
            raise ValueError('unknown string format')
        if res.stdabbr in ('GMT', 'UTC') and not posix_offset:
            res.stdoffset *= -1
        tzrange.__init__(self, res.stdabbr, res.stdoffset, res.dstabbr, res.dstoffset, start=False, end=False)
        if not res.dstabbr:
            self._start_delta = None
            self._end_delta = None
        else:
            self._start_delta = self._delta(res.start)
            if self._start_delta:
                self._end_delta = self._delta(res.end, isend=1)
        self.hasdst = bool(self._start_delta)

    def _delta(self, x, isend = 0):
        from dateutil import relativedelta
        kwargs = {}
        if x.month is not None:
            kwargs['month'] = x.month
            if x.weekday is not None:
                kwargs['weekday'] = relativedelta.weekday(x.weekday, x.week)
                if x.week > 0:
                    kwargs['day'] = 1
                else:
                    kwargs['day'] = 31
            elif x.day:
                kwargs['day'] = x.day
        elif x.yday is not None:
            kwargs['yearday'] = x.yday
        elif x.jyday is not None:
            kwargs['nlyearday'] = x.jyday
        if not kwargs:
            if not isend:
                kwargs['month'] = 4
                kwargs['day'] = 1
                kwargs['weekday'] = relativedelta.SU(+1)
            else:
                kwargs['month'] = 10
                kwargs['day'] = 31
                kwargs['weekday'] = relativedelta.SU(-1)
        if x.time is not None:
            kwargs['seconds'] = x.time
        else:
            kwargs['seconds'] = 7200
        if isend:
            delta = self._dst_offset - self._std_offset
            kwargs['seconds'] -= delta.seconds + delta.days * 86400
        return relativedelta.relativedelta(**kwargs)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, repr(self._s))


class _tzicalvtzcomp(object):

    def __init__(self, tzoffsetfrom, tzoffsetto, isdst, tzname = None, rrule = None):
        self.tzoffsetfrom = datetime.timedelta(seconds=tzoffsetfrom)
        self.tzoffsetto = datetime.timedelta(seconds=tzoffsetto)
        self.tzoffsetdiff = self.tzoffsetto - self.tzoffsetfrom
        self.isdst = isdst
        self.tzname = tzname
        self.rrule = rrule


class _tzicalvtz(_tzinfo):

    def __init__(self, tzid, comps = []):
        super(_tzicalvtz, self).__init__()
        self._tzid = tzid
        self._comps = comps
        self._cachedate = []
        self._cachecomp = []

    def _find_comp(self, dt):
        if len(self._comps) == 1:
            return self._comps[0]
        dt = dt.replace(tzinfo=None)
        try:
            return self._cachecomp[self._cachedate.index((dt, self._fold(dt)))]
        except ValueError:
            pass

        lastcompdt = None
        lastcomp = None
        for comp in self._comps:
            compdt = self._find_compdt(comp, dt)
            if compdt and (not lastcompdt or lastcompdt < compdt):
                lastcompdt = compdt
                lastcomp = comp

        if not lastcomp:
            for comp in self._comps:
                if not comp.isdst:
                    lastcomp = comp
                    break
            else:
                lastcomp = comp[0]

        self._cachedate.insert(0, (dt, self._fold(dt)))
        self._cachecomp.insert(0, lastcomp)
        if len(self._cachedate) > 10:
            self._cachedate.pop()
            self._cachecomp.pop()
        return lastcomp

    def _find_compdt(self, comp, dt):
        if comp.tzoffsetdiff < ZERO and self._fold(dt):
            dt -= comp.tzoffsetdiff
        compdt = comp.rrule.before(dt, inc=True)
        return compdt

    def utcoffset(self, dt):
        if dt is None:
            return
        return self._find_comp(dt).tzoffsetto

    def dst(self, dt):
        comp = self._find_comp(dt)
        if comp.isdst:
            return comp.tzoffsetdiff
        else:
            return ZERO

    @tzname_in_python2
    def tzname(self, dt):
        return self._find_comp(dt).tzname

    def __repr__(self):
        return '<tzicalvtz %s>' % repr(self._tzid)

    __reduce__ = object.__reduce__


class tzical(object):

    def __init__(self, fileobj):
        global rrule
        from dateutil import rrule
        if isinstance(fileobj, string_types):
            self._s = fileobj
            fileobj = open(fileobj, 'r')
            file_opened_here = True
        else:
            self._s = getattr(fileobj, 'name', repr(fileobj))
            fileobj = _ContextWrapper(fileobj)
        self._vtz = {}
        with fileobj as fobj:
            self._parse_rfc(fobj.read())

    def keys(self):
        return list(self._vtz.keys())

    def get(self, tzid = None):
        if tzid is None:
            if len(self._vtz) == 0:
                raise ValueError('no timezones defined')
            elif len(self._vtz) > 1:
                raise ValueError('more than one timezone available')
            tzid = next(iter(self._vtz))
        return self._vtz.get(tzid)

    def _parse_offset(self, s):
        s = s.strip()
        if not s:
            raise ValueError('empty offset')
        if s[0] in ('+', '-'):
            signal = (-1, +1)[s[0] == '+']
            s = s[1:]
        else:
            signal = +1
        if len(s) == 4:
            return (int(s[:2]) * 3600 + int(s[2:]) * 60) * signal
        if len(s) == 6:
            return (int(s[:2]) * 3600 + int(s[2:4]) * 60 + int(s[4:])) * signal
        raise ValueError('invalid offset: ' + s)

    def _parse_rfc(self, s):
        lines = s.splitlines()
        if not lines:
            raise ValueError('empty string')
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            if not line:
                del lines[i]
            elif i > 0 and line[0] == ' ':
                lines[i - 1] += line[1:]
                del lines[i]
            else:
                i += 1

        tzid = None
        comps = []
        invtz = False
        comptype = None
        for line in lines:
            if not line:
                continue
            name, value = line.split(':', 1)
            parms = name.split(';')
            if not parms:
                raise ValueError('empty property name')
            name = parms[0].upper()
            parms = parms[1:]
            if invtz:
                if name == 'BEGIN':
                    if value in ('STANDARD', 'DAYLIGHT'):
                        pass
                    else:
                        raise ValueError('unknown component: ' + value)
                    comptype = value
                    founddtstart = False
                    tzoffsetfrom = None
                    tzoffsetto = None
                    rrulelines = []
                    tzname = None
                elif name == 'END':
                    if value == 'VTIMEZONE':
                        if comptype:
                            raise ValueError('component not closed: ' + comptype)
                        if not tzid:
                            raise ValueError('mandatory TZID not found')
                        if not comps:
                            raise ValueError('at least one component is needed')
                        self._vtz[tzid] = _tzicalvtz(tzid, comps)
                        invtz = False
                    elif value == comptype:
                        if not founddtstart:
                            raise ValueError('mandatory DTSTART not found')
                        if tzoffsetfrom is None:
                            raise ValueError('mandatory TZOFFSETFROM not found')
                        if tzoffsetto is None:
                            raise ValueError('mandatory TZOFFSETFROM not found')
                        rr = None
                        if rrulelines:
                            rr = rrule.rrulestr('\n'.join(rrulelines), compatible=True, ignoretz=True, cache=True)
                        comp = _tzicalvtzcomp(tzoffsetfrom, tzoffsetto, comptype == 'DAYLIGHT', tzname, rr)
                        comps.append(comp)
                        comptype = None
                    else:
                        raise ValueError('invalid component end: ' + value)
                elif comptype:
                    if name == 'DTSTART':
                        rrulelines.append(line)
                        founddtstart = True
                    elif name in ('RRULE', 'RDATE', 'EXRULE', 'EXDATE'):
                        rrulelines.append(line)
                    elif name == 'TZOFFSETFROM':
                        if parms:
                            raise ValueError('unsupported %s parm: %s ' % (name, parms[0]))
                        tzoffsetfrom = self._parse_offset(value)
                    elif name == 'TZOFFSETTO':
                        if parms:
                            raise ValueError('unsupported TZOFFSETTO parm: ' + parms[0])
                        tzoffsetto = self._parse_offset(value)
                    elif name == 'TZNAME':
                        if parms:
                            raise ValueError('unsupported TZNAME parm: ' + parms[0])
                        tzname = value
                    elif name == 'COMMENT':
                        pass
                    else:
                        raise ValueError('unsupported property: ' + name)
                elif name == 'TZID':
                    if parms:
                        raise ValueError('unsupported TZID parm: ' + parms[0])
                    tzid = value
                elif name in ('TZURL', 'LAST-MODIFIED', 'COMMENT'):
                    pass
                else:
                    raise ValueError('unsupported property: ' + name)
            elif name == 'BEGIN' and value == 'VTIMEZONE':
                tzid = None
                comps = []
                invtz = True

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, repr(self._s))


if sys.platform != 'win32':
    TZFILES = ['/etc/localtime', 'localtime']
    TZPATHS = ['/usr/share/zoneinfo',
     '/usr/lib/zoneinfo',
     '/usr/share/lib/zoneinfo',
     '/etc/zoneinfo']
else:
    TZFILES = []
    TZPATHS = []

def gettz(name = None):
    tz = None
    if not name:
        try:
            name = os.environ['TZ']
        except KeyError:
            pass

    if name is None or name == ':':
        for filepath in TZFILES:
            if not os.path.isabs(filepath):
                filename = filepath
                for path in TZPATHS:
                    filepath = os.path.join(path, filename)
                    if os.path.isfile(filepath):
                        break
                else:
                    continue

            if os.path.isfile(filepath):
                try:
                    tz = tzfile(filepath)
                    break
                except (IOError, OSError, ValueError):
                    pass

        else:
            tz = tzlocal()

    else:
        if name.startswith(':'):
            name = name[:-1]
        if os.path.isabs(name):
            if os.path.isfile(name):
                tz = tzfile(name)
            else:
                tz = None
        else:
            for path in TZPATHS:
                filepath = os.path.join(path, name)
                if not os.path.isfile(filepath):
                    filepath = filepath.replace(' ', '_')
                    if not os.path.isfile(filepath):
                        continue
                try:
                    tz = tzfile(filepath)
                    break
                except (IOError, OSError, ValueError):
                    pass

            else:
                tz = None
                if tzwin is not None:
                    try:
                        tz = tzwin(name)
                    except WindowsError:
                        tz = None

                if not tz:
                    from dateutil.zoneinfo import get_zonefile_instance
                    tz = get_zonefile_instance().get(name)
                if not tz:
                    for c in name:
                        if c in '0123456789':
                            try:
                                tz = tzstr(name)
                            except ValueError:
                                pass

                            break
                    else:
                        if name in ('GMT', 'UTC'):
                            tz = tzutc()
                        elif name in time.tzname:
                            tz = tzlocal()

    return tz


def datetime_exists(dt, tz = None):
    if tz is None:
        if dt.tzinfo is None:
            raise ValueError('Datetime is naive and no time zone provided.')
        tz = dt.tzinfo
    dt = dt.replace(tzinfo=None)
    dt_rt = dt.replace(tzinfo=tz).astimezone(tzutc()).astimezone(tz)
    dt_rt = dt_rt.replace(tzinfo=None)
    return dt == dt_rt


def datetime_ambiguous(dt, tz = None):
    if tz is None:
        if dt.tzinfo is None:
            raise ValueError('Datetime is naive and no time zone provided.')
        tz = dt.tzinfo
    is_ambiguous_fn = getattr(tz, 'is_ambiguous', None)
    if is_ambiguous_fn is not None:
        try:
            return tz.is_ambiguous(dt)
        except:
            pass

    dt = dt.replace(tzinfo=tz)
    wall_0 = enfold(dt, fold=0)
    wall_1 = enfold(dt, fold=1)
    same_offset = wall_0.utcoffset() == wall_1.utcoffset()
    same_dst = wall_0.dst() == wall_1.dst()
    return not (same_offset and same_dst)


def _datetime_to_timestamp(dt):
    return _total_seconds(dt.replace(tzinfo=None) - EPOCH)


class _ContextWrapper(object):

    def __init__(self, context):
        self.context = context

    def __enter__(self):
        return self.context

    def __exit__(*args, **kwargs):
        pass
