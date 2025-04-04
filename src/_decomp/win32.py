#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\win32.py
import ctypes
from ctypes import *
from ctypes.wintypes import *
SIZE_T = c_size_t
DWORDLONG = c_uint64
CF_UNICODETEXT = 13

def GetClipboardData():
    if not ctypes.windll.user32.OpenClipboard(0):
        raise ctypes.WinError()
    try:
        if not ctypes.windll.user32.IsClipboardFormatAvailable(CF_UNICODETEXT):
            return
        data = ctypes.windll.user32.GetClipboardData(CF_UNICODETEXT)
        if not data:
            raise ctypes.WinError()
        ld = ctypes.windll.kernel32.GlobalLock(data)
        if not ld:
            raise ctypes.WinError()
        try:
            return ctypes.c_wchar_p(ld).value
        finally:
            ctypes.windll.kernel32.GlobalUnlock(data)

    finally:
        if not ctypes.windll.user32.CloseClipboard():
            raise ctypes.WinError()


def SetConsoleTitle(title):
    if not ctypes.windll.kernel32.SetConsoleTitleW(unicode(title)):
        raise ctypes.WinError()


def GetCurrentProcessId():
    return ctypes.windll.kernel32.GetCurrentProcessId()


def StructToKeyval(s):
    import utillib as util
    d = dict(((k, getattr(s, k)) for k, t in s._fields_))
    return util.KeyVal(**d)


class PROCESS_MEMORY_COUNTERS_EX(Structure):
    _fields_ = [('cb', DWORD),
     ('PageFaultCount', DWORD),
     ('PeakWorkingSetSize', SIZE_T),
     ('WorkingSetSize', SIZE_T),
     ('QuotaPeakPagedPoolUsage', SIZE_T),
     ('QuotaPagedPoolUsage', SIZE_T),
     ('QuotaPeakNonPagedPoolUsage', SIZE_T),
     ('QuotaNonPagedPoolUsage', SIZE_T),
     ('PagefileUsage', SIZE_T),
     ('PeakPagefileUsage', SIZE_T),
     ('PrivateUsage', SIZE_T)]


def GetProcessMemoryInfo():
    f = windll.Kernel32.GetCurrentProcess
    f.retval = HANDLE
    h = f()
    counters = PROCESS_MEMORY_COUNTERS_EX()
    windll.Psapi.GetProcessMemoryInfo(HANDLE(h), byref(counters), sizeof(counters))
    return StructToKeyval(counters)


class MEMORYSTATUSEX(Structure):
    _fields_ = [('dwLength', DWORD),
     ('dwMemoryLoad', DWORD),
     ('ullTotalPhys', DWORDLONG),
     ('ullAvailPhys', DWORDLONG),
     ('ullTotalPageFile', DWORDLONG),
     ('ullAvailPageFile', DWORDLONG),
     ('ullTotalVirtual', DWORDLONG),
     ('ullAvailVirtual', DWORDLONG),
     ('ullAvailExtendedVirtual', DWORDLONG)]


def GlobalMemoryStatus():
    counters = MEMORYSTATUSEX()
    counters.dwLength = sizeof(counters)
    windll.Kernel32.GlobalMemoryStatusEx(byref(counters))
    return StructToKeyval(counters)


class PERFORMANCE_INFORMATION(Structure):
    _fields_ = [('cb', DWORD),
     ('CommitTotal', SIZE_T),
     ('CommitLimit', SIZE_T),
     ('CommitPeak', SIZE_T),
     ('PhysicalTotal', SIZE_T),
     ('PhysicalAvailable', SIZE_T),
     ('SystemCache', SIZE_T),
     ('KernelTotal', SIZE_T),
     ('KernelPaged', SIZE_T),
     ('KernelNonPaged', SIZE_T),
     ('PageSize', SIZE_T),
     ('HandleCount', DWORD),
     ('ProcessCount', DWORD),
     ('ThreadCount', DWORD)]


def GetPerformanceInfo():
    counters = PERFORMANCE_INFORMATION()
    windll.Psapi.GetPerformanceInfo(byref(counters), sizeof(counters))
    return StructToKeyval(counters)


def GetProcessWorkingSetSize():
    f = windll.Kernel32.GetCurrentProcess
    f.retval = HANDLE
    h = f()
    min, max = SIZE_T(), SIZE_T()
    flags = DWORD()
    try:
        windll.Kernel32.GetProcessWorkingSetSizeEx(HANDLE(h), byref(min), byref(max), byref(flags))
    except:
        windll.Kernel32.GetProcessWorkingSetSize(HANDLE(h), byref(min), byref(max))

    return (min.value, max.value, flags.value)
