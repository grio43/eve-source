#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\osutils\__init__.py
import ctypes
import logging
import os
import shutil
import stat
import subprocess
import threading
import time
try:
    import pythoncom
    import win32com.client as win32client
except ImportError:
    pythoncom, win32client = (None, None)

from brennivin.osutils import *
from brennivin.platformutils import cpu_count
from brennivin.zipfileutils import FileComparisonError, compare_zip_files
from . import win32api
logger = logging.getLogger(__name__)
CompareZipFiles = compare_zip_files
AbsPathEx = abspathex
ChangeCwd = change_cwd
ChangeEnviron = change_environ
ChangeExt = change_ext
Copy = copy
GetCrcFromFilename = crc_from_filename
FindFiles = iter_files
ListDirEx = listdirex
MkTemp = mktemp
PathComponents = path_components
GetFilenameWithoutExt = purename
SetReadonly = set_readonly
SplitPath = path_split = split3

def common_prefix(filepaths, sep = os.sep):

    def getCommonDrive(filepaths_):
        drives = set()
        for p in filepaths_:
            drive, _ = os.path.splitdrive(p)
            drives.add(drive)

        if len(drives) == 1:
            return drives.pop()

    result = os.path.commonprefix(filepaths).rpartition(sep)[0]
    if result:
        return result
    result = getCommonDrive(filepaths)
    if result:
        return result
    return ''


CommonPrefix = common_prefix

def get_modified_time(filename):
    return os.stat(filename)[stat.ST_MTIME]


def _iter_processes_systemcall():
    out, err = systemcall('tasklist')
    if err:
        raise RuntimeError('EnumerateProcesses error: %s' % err)
    try:
        lines = filter(None, out.split('\n'))
        lines.pop(0)

        def getColumnWidths(line):
            columns = line.split(' ')
            return map(len, columns)

        columnWidths = getColumnWidths(lines.pop(0))
        names = ['imagename', 'pid']
        columnWidths = columnWidths[:len(names)]

        def parseLine(line):
            columns = {}
            for i, width in enumerate(columnWidths):
                name = names[i]
                prevoffset = sum(columnWidths[:i]) + i
                snippet = line[prevoffset:prevoffset + width]
                columns[name] = snippet.strip()

            return columns

        for l in lines:
            yield parseLine(l)

    except Exception:
        logger.error('Failed to parse: %s', out)
        raise


def _iter_processes_win32():
    try:
        WMI = win32client.GetObject('winmgmts:')
    except pythoncom.com_error:
        for p in _iter_processes_systemcall():
            yield p

    else:
        processes = WMI.InstancesOf('Win32_Process')
        for p in processes:
            yield {'imagename': p.Name,
             'pid': str(p.ProcessId)}


def iter_processes():
    if win32client:
        return _iter_processes_win32()
    else:
        return _iter_processes_systemcall()


EnumerateProcesses = iter_processes

def iter_drives():
    out, err = systemcall('wmic', 'logicaldisk', 'get', 'caption')
    if err:
        raise RuntimeError('EnumerateDrives error: %s', err)
    lines = out.split('\n')[1:]
    for li in lines:
        yield li.strip()


EnumerateDrives = iter_drives

def get_top_level_windows():
    ret = []
    user32 = ctypes.windll.user32
    title = ctypes.c_buffer(' ' * 256)
    hwnd = user32.GetForegroundWindow()
    while hwnd:
        n = user32.GetWindowTextA(hwnd, title, 255)
        if n:
            ret.append((hwnd, title.value))
        hwnd = user32.GetWindow(hwnd, 2)

    del title
    return ret


GetTopLevelWindows = get_top_level_windows

def get_windows_with_title(titleSubstring):
    ret = tuple(((hwnd, title) for hwnd, title in get_top_level_windows() if titleSubstring in title))
    return ret


GetWindowsWithTitle = get_windows_with_title

def is_proc_running(pid):
    pid = str(pid)
    for pinfo in iter_processes():
        if pid == pinfo['pid']:
            return True

    return False


IsProcessRunning = is_proc_running

def kill(pid):
    systemcall('taskkill', '/F', '/T', '/PID', str(pid))


Kill = kill

def getppid(pid = None):
    if getattr(os, 'getppid', None):
        if pid is not None:
            raise ValueError('getppid with args only supported on Windows right now.')
        return os.getppid()
    if pid is None:
        pid = os.getpid()
    return win32api.getppid(pid)


NumberOfCPUs = cpu_count

def _should_print(s, skipWhitespace):
    if not skipWhitespace:
        return True
    return s and not s.isspace()


def redirect_output(subproc, redirect, attr = 'stdout', skipWhitespaceLines = False):
    stream = getattr(subproc, attr)

    def inner():
        while True:
            out = stream.readline()
            if not out and subproc.poll() is not None:
                return
            if _should_print(out, skipWhitespaceLines):
                redirect(out.rstrip('\n\r'))

    t = threading.Thread(name='logredirect_pid%s' % subproc.pid, target=inner)
    t.start()
    return t


RedirectOutput = redirect_output

def _missingfile(winerr):
    return winerr.errno == 2 and winerr.winerror in (2, 3)


def REMOVE_READONLY(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
        os.remove(path)
    except WindowsError as ex:
        if _missingfile(ex):
            return
        raise


def safe_rmtree(path, timeout = 2, onerror = None):
    endtime = time.clock() + timeout
    while True:
        try:
            shutil.rmtree(path, onerror=onerror)
            return
        except WindowsError as ex:
            if _missingfile(ex):
                return
            if time.clock() > endtime:
                raise


SafeRmTree = safe_rmtree

def safe_copyfile(src, dst, timeout = 2):
    endtime = time.clock() + timeout
    while True:
        try:
            shutil.copyfile(src, dst)
            return
        except IOError:
            if time.clock() > endtime:
                raise


SafeCopyfile = safe_copyfile

def same_file(f1, f2):

    def get_read_handle(filename):
        if os.path.isdir(filename):
            dwFlagsAndAttributes = win32api.Win32FileConstants.FILE_FLAG_BACKUP_SEMANTICS
        else:
            dwFlagsAndAttributes = 0
        return win32api.CreateFile(filename, win32api.Win32FileConstants.GENERIC_READ, win32api.Win32FileConstants.FILE_SHARE_READ, None, win32api.Win32FileConstants.OPEN_EXISTING, dwFlagsAndAttributes, None)

    def get_unique_id(hFile):
        info = win32api.GetFileInformationByHandle(hFile)
        return (info.dwVolumeSerialNumber, info.nFileIndexHigh, info.nFileIndexLow)

    hFile1, hFile2 = (None, None)
    try:
        hFile1 = get_read_handle(f1)
        hFile2 = get_read_handle(f2)
        are_equal = get_unique_id(hFile1) == get_unique_id(hFile2)
    finally:
        if hFile2:
            win32api.CloseHandle(hFile2)
        if hFile1:
            win32api.CloseHandle(hFile1)

    return are_equal


SameFile = same_file

def systemcall(*args):
    cmd = '"%s"' % subprocess.list2cmdline(args)
    stdin, out, err = os.popen3(cmd)
    return (out.read(), err.read())


SystemCall = systemcall

def watch_process(pid, func, cancelToken = None, sleepS = 0.05):
    if not is_proc_running(pid):
        func()
        return

    def loop():
        while True:
            if cancelToken and cancelToken.is_set():
                return
            if is_proc_running(pid):
                time.sleep(sleepS)
                continue
            func()
            return

    import threadutils
    t = threadutils.ExceptionalThread(target=loop)
    t.daemon = True
    t.start()
    return t


WatchProcess = watch_process
