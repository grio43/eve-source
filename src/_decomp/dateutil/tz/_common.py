#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dateutil\tz\_common.py
from six import PY3
from datetime import datetime, timedelta, tzinfo
import copy
ZERO = timedelta(0)
__all__ = ['tzname_in_python2', 'enfold']

def tzname_in_python2(namefunc):

    def adjust_encoding(*args, **kwargs):
        name = namefunc(*args, **kwargs)
        if name is not None and not PY3:
            name = name.encode()
        return name

    return adjust_encoding


if hasattr(datetime, 'fold'):

    def enfold(dt, fold = 1):
        return dt.replace(fold=fold)


else:

    class _DatetimeWithFold(datetime):
        __slots__ = ()

        @property
        def fold(self):
            return 1


    def enfold(dt, fold = 1):
        if getattr(dt, 'fold', 0) == fold:
            return dt
        args = dt.timetuple()[:6]
        args += (dt.microsecond, dt.tzinfo)
        if fold:
            return _DatetimeWithFold(*args)
        else:
            return datetime(*args)


class _tzinfo(tzinfo):

    def is_ambiguous(self, dt):
        dt = dt.replace(tzinfo=self)
        wall_0 = enfold(dt, fold=0)
        wall_1 = enfold(dt, fold=1)
        same_offset = wall_0.utcoffset() == wall_1.utcoffset()
        same_dt = wall_0.replace(tzinfo=None) == wall_1.replace(tzinfo=None)
        return same_dt and not same_offset

    def _fold_status(self, dt_utc, dt_wall):
        if self.is_ambiguous(dt_wall):
            delta_wall = dt_wall - dt_utc
            _fold = int(delta_wall == dt_utc.utcoffset() - dt_utc.dst())
        else:
            _fold = 0
        return _fold

    def _fold(self, dt):
        return getattr(dt, 'fold', 0)

    def _fromutc(self, dt):
        if not isinstance(dt, datetime):
            raise TypeError('fromutc() requires a datetime argument')
        if dt.tzinfo is not self:
            raise ValueError('dt.tzinfo is not self')
        dtoff = dt.utcoffset()
        if dtoff is None:
            raise ValueError('fromutc() requires a non-None utcoffset() result')
        dtdst = dt.dst()
        if dtdst is None:
            raise ValueError('fromutc() requires a non-None dst() result')
        delta = dtoff - dtdst
        if delta:
            dt += delta
            dtdst = enfold(dt, fold=1).dst()
            if dtdst is None:
                raise ValueError('fromutc(): dt.dst gave inconsistent results; cannot convert')
        return dt + dtdst

    def fromutc(self, dt):
        dt_wall = self._fromutc(dt)
        _fold = self._fold_status(dt, dt_wall)
        return enfold(dt_wall, fold=_fold)


class tzrangebase(_tzinfo):

    def __init__(self):
        raise NotImplementedError('tzrangebase is an abstract base class')

    def utcoffset(self, dt):
        isdst = self._isdst(dt)
        if isdst is None:
            return
        elif isdst:
            return self._dst_offset
        else:
            return self._std_offset

    def dst(self, dt):
        isdst = self._isdst(dt)
        if isdst is None:
            return
        elif isdst:
            return self._dst_base_offset
        else:
            return ZERO

    @tzname_in_python2
    def tzname(self, dt):
        if self._isdst(dt):
            return self._dst_abbr
        else:
            return self._std_abbr

    def fromutc(self, dt):
        if not isinstance(dt, datetime):
            raise TypeError('fromutc() requires a datetime argument')
        if dt.tzinfo is not self:
            raise ValueError('dt.tzinfo is not self')
        transitions = self.transitions(dt.year)
        if transitions is None:
            return dt + self.utcoffset(dt)
        dston, dstoff = transitions
        dston -= self._std_offset
        dstoff -= self._std_offset
        utc_transitions = (dston, dstoff)
        dt_utc = dt.replace(tzinfo=None)
        isdst = self._naive_isdst(dt_utc, utc_transitions)
        if isdst:
            dt_wall = dt + self._dst_offset
        else:
            dt_wall = dt + self._std_offset
        _fold = int(not isdst and self.is_ambiguous(dt_wall))
        return enfold(dt_wall, fold=_fold)

    def is_ambiguous(self, dt):
        if not self.hasdst:
            return False
        start, end = self.transitions(dt.year)
        dt = dt.replace(tzinfo=None)
        return end <= dt < end + self._dst_base_offset

    def _isdst(self, dt):
        if not self.hasdst:
            return False
        elif dt is None:
            return
        transitions = self.transitions(dt.year)
        if transitions is None:
            return False
        dt = dt.replace(tzinfo=None)
        isdst = self._naive_isdst(dt, transitions)
        if not isdst and self.is_ambiguous(dt):
            return not self._fold(dt)
        else:
            return isdst

    def _naive_isdst(self, dt, transitions):
        dston, dstoff = transitions
        dt = dt.replace(tzinfo=None)
        if dston < dstoff:
            isdst = dston <= dt < dstoff
        else:
            isdst = not dstoff <= dt < dston
        return isdst

    @property
    def _dst_base_offset(self):
        return self._dst_offset - self._std_offset

    __hash__ = None

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '%s(...)' % self.__class__.__name__

    __reduce__ = object.__reduce__


def _total_seconds(td):
    return ((td.seconds + td.days * 86400) * 1000000 + td.microseconds) // 1000000


_total_seconds = getattr(timedelta, 'total_seconds', _total_seconds)
