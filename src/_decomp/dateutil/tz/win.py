#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dateutil\tz\win.py
import datetime
import struct
from six.moves import winreg
from six import text_type
try:
    import ctypes
    from ctypes import wintypes
except ValueError:
    raise ImportError('Running tzwin on non-Windows system')

from ._common import tzname_in_python2, _tzinfo
from ._common import tzrangebase
__all__ = ['tzwin', 'tzwinlocal', 'tzres']
ONEWEEK = datetime.timedelta(7)
TZKEYNAMENT = 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Time Zones'
TZKEYNAME9X = 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Time Zones'
TZLOCALKEYNAME = 'SYSTEM\\CurrentControlSet\\Control\\TimeZoneInformation'

def _settzkeyname():
    handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    try:
        winreg.OpenKey(handle, TZKEYNAMENT).Close()
        TZKEYNAME = TZKEYNAMENT
    except WindowsError:
        TZKEYNAME = TZKEYNAME9X

    handle.Close()
    return TZKEYNAME


TZKEYNAME = _settzkeyname()

class tzres(object):
    p_wchar = ctypes.POINTER(wintypes.WCHAR)

    def __init__(self, tzres_loc = 'tzres.dll'):
        user32 = ctypes.WinDLL('user32')
        user32.LoadStringW.argtypes = (wintypes.HINSTANCE,
         wintypes.UINT,
         wintypes.LPWSTR,
         ctypes.c_int)
        self.LoadStringW = user32.LoadStringW
        self._tzres = ctypes.WinDLL(tzres_loc)
        self.tzres_loc = tzres_loc

    def load_name(self, offset):
        resource = self.p_wchar()
        lpBuffer = ctypes.cast(ctypes.byref(resource), wintypes.LPWSTR)
        nchar = self.LoadStringW(self._tzres._handle, offset, lpBuffer, 0)
        return resource[:nchar]

    def name_from_string(self, tzname_str):
        if not tzname_str.startswith('@'):
            return tzname_str
        name_splt = tzname_str.split(',-')
        try:
            offset = int(name_splt[1])
        except:
            raise ValueError('Malformed timezone string.')

        return self.load_name(offset)


class tzwinbase(tzrangebase):

    def __init__(self):
        raise NotImplementedError('tzwinbase is an abstract base class')

    def __eq__(self, other):
        if not isinstance(other, tzwinbase):
            return NotImplemented
        return self._std_offset == other._std_offset and self._dst_offset == other._dst_offset and self._stddayofweek == other._stddayofweek and self._dstdayofweek == other._dstdayofweek and self._stdweeknumber == other._stdweeknumber and self._dstweeknumber == other._dstweeknumber and self._stdhour == other._stdhour and self._dsthour == other._dsthour and self._stdminute == other._stdminute and self._dstminute == other._dstminute and self._std_abbr == other._std_abbr and self._dst_abbr == other._dst_abbr

    @staticmethod
    def list():
        with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as handle:
            with winreg.OpenKey(handle, TZKEYNAME) as tzkey:
                result = [ winreg.EnumKey(tzkey, i) for i in range(winreg.QueryInfoKey(tzkey)[0]) ]
        return result

    def display(self):
        return self._display

    def transitions(self, year):
        if not self.hasdst:
            return None
        dston = picknthweekday(year, self._dstmonth, self._dstdayofweek, self._dsthour, self._dstminute, self._dstweeknumber)
        dstoff = picknthweekday(year, self._stdmonth, self._stddayofweek, self._stdhour, self._stdminute, self._stdweeknumber)
        dstoff -= self._dst_base_offset
        return (dston, dstoff)

    def _get_hasdst(self):
        return self._dstmonth != 0

    @property
    def _dst_base_offset(self):
        return self._dst_base_offset_


class tzwin(tzwinbase):

    def __init__(self, name):
        self._name = name
        with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as handle:
            tzkeyname = text_type('{kn}\\{name}').format(kn=TZKEYNAME, name=name)
            with winreg.OpenKey(handle, tzkeyname) as tzkey:
                keydict = valuestodict(tzkey)
        self._std_abbr = keydict['Std']
        self._dst_abbr = keydict['Dlt']
        self._display = keydict['Display']
        tup = struct.unpack('=3l16h', keydict['TZI'])
        stdoffset = -tup[0] - tup[1]
        dstoffset = stdoffset - tup[2]
        self._std_offset = datetime.timedelta(minutes=stdoffset)
        self._dst_offset = datetime.timedelta(minutes=dstoffset)
        self._stdmonth, self._stddayofweek, self._stdweeknumber, self._stdhour, self._stdminute = tup[4:9]
        self._dstmonth, self._dstdayofweek, self._dstweeknumber, self._dsthour, self._dstminute = tup[12:17]
        self._dst_base_offset_ = self._dst_offset - self._std_offset
        self.hasdst = self._get_hasdst()

    def __repr__(self):
        return 'tzwin(%s)' % repr(self._name)

    def __reduce__(self):
        return (self.__class__, (self._name,))


class tzwinlocal(tzwinbase):

    def __init__(self):
        with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as handle:
            with winreg.OpenKey(handle, TZLOCALKEYNAME) as tzlocalkey:
                keydict = valuestodict(tzlocalkey)
            self._std_abbr = keydict['StandardName']
            self._dst_abbr = keydict['DaylightName']
            try:
                tzkeyname = text_type('{kn}\\{sn}').format(kn=TZKEYNAME, sn=self._std_abbr)
                with winreg.OpenKey(handle, tzkeyname) as tzkey:
                    _keydict = valuestodict(tzkey)
                    self._display = _keydict['Display']
            except OSError:
                self._display = None

        stdoffset = -keydict['Bias'] - keydict['StandardBias']
        dstoffset = stdoffset - keydict['DaylightBias']
        self._std_offset = datetime.timedelta(minutes=stdoffset)
        self._dst_offset = datetime.timedelta(minutes=dstoffset)
        tup = struct.unpack('=8h', keydict['StandardStart'])
        self._stdmonth, self._stdweeknumber, self._stdhour, self._stdminute = tup[1:5]
        self._stddayofweek = tup[7]
        tup = struct.unpack('=8h', keydict['DaylightStart'])
        self._dstmonth, self._dstweeknumber, self._dsthour, self._dstminute = tup[1:5]
        self._dstdayofweek = tup[7]
        self._dst_base_offset_ = self._dst_offset - self._std_offset
        self.hasdst = self._get_hasdst()

    def __repr__(self):
        return 'tzwinlocal()'

    def __str__(self):
        return 'tzwinlocal(%s)' % repr(self._std_abbr)

    def __reduce__(self):
        return (self.__class__, ())


def picknthweekday(year, month, dayofweek, hour, minute, whichweek):
    first = datetime.datetime(year, month, 1, hour, minute)
    weekdayone = first.replace(day=(dayofweek - first.isoweekday()) % 7 + 1)
    wd = weekdayone + (whichweek - 1) * ONEWEEK
    if wd.month != month:
        wd -= ONEWEEK
    return wd


def valuestodict(key):
    dout = {}
    size = winreg.QueryInfoKey(key)[1]
    tz_res = None
    for i in range(size):
        key_name, value, dtype = winreg.EnumValue(key, i)
        if dtype == winreg.REG_DWORD or dtype == winreg.REG_DWORD_LITTLE_ENDIAN:
            if value & 2147483648L:
                value = value - 4294967296L
        elif dtype == winreg.REG_SZ:
            if value.startswith('@tzres'):
                tz_res = tz_res or tzres()
                value = tz_res.name_from_string(value)
            value = value.rstrip('\x00')
        dout[key_name] = value

    return dout
