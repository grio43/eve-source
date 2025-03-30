#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\watchdog\observers\winapi.py
import ctypes.wintypes
from functools import reduce
LPVOID = ctypes.wintypes.LPVOID
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
FILE_NOTIFY_CHANGE_FILE_NAME = 1
FILE_NOTIFY_CHANGE_DIR_NAME = 2
FILE_NOTIFY_CHANGE_ATTRIBUTES = 4
FILE_NOTIFY_CHANGE_SIZE = 8
FILE_NOTIFY_CHANGE_LAST_WRITE = 16
FILE_NOTIFY_CHANGE_LAST_ACCESS = 32
FILE_NOTIFY_CHANGE_CREATION = 64
FILE_NOTIFY_CHANGE_SECURITY = 256
FILE_FLAG_BACKUP_SEMANTICS = 33554432
FILE_FLAG_OVERLAPPED = 1073741824
FILE_LIST_DIRECTORY = 1
FILE_SHARE_READ = 1
FILE_SHARE_WRITE = 2
FILE_SHARE_DELETE = 4
OPEN_EXISTING = 3
VOLUME_NAME_NT = 2
FILE_ACTION_CREATED = 1
FILE_ACTION_DELETED = 2
FILE_ACTION_MODIFIED = 3
FILE_ACTION_RENAMED_OLD_NAME = 4
FILE_ACTION_RENAMED_NEW_NAME = 5
FILE_ACTION_DELETED_SELF = 65534
FILE_ACTION_OVERFLOW = 65535
FILE_ACTION_ADDED = FILE_ACTION_CREATED
FILE_ACTION_REMOVED = FILE_ACTION_DELETED
FILE_ACTION_REMOVED_SELF = FILE_ACTION_DELETED_SELF
THREAD_TERMINATE = 1
WAIT_ABANDONED = 128
WAIT_IO_COMPLETION = 192
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258
ERROR_OPERATION_ABORTED = 995

class OVERLAPPED(ctypes.Structure):
    _fields_ = [('Internal', LPVOID),
     ('InternalHigh', LPVOID),
     ('Offset', ctypes.wintypes.DWORD),
     ('OffsetHigh', ctypes.wintypes.DWORD),
     ('Pointer', LPVOID),
     ('hEvent', ctypes.wintypes.HANDLE)]


def _errcheck_bool(value, func, args):
    if not value:
        raise ctypes.WinError()
    return args


def _errcheck_handle(value, func, args):
    if not value:
        raise ctypes.WinError()
    if value == INVALID_HANDLE_VALUE:
        raise ctypes.WinError()
    return args


def _errcheck_dword(value, func, args):
    if value == 4294967295L:
        raise ctypes.WinError()
    return args


kernel32 = ctypes.WinDLL('kernel32')
ReadDirectoryChangesW = kernel32.ReadDirectoryChangesW
ReadDirectoryChangesW.restype = ctypes.wintypes.BOOL
ReadDirectoryChangesW.errcheck = _errcheck_bool
ReadDirectoryChangesW.argtypes = (ctypes.wintypes.HANDLE,
 LPVOID,
 ctypes.wintypes.DWORD,
 ctypes.wintypes.BOOL,
 ctypes.wintypes.DWORD,
 ctypes.POINTER(ctypes.wintypes.DWORD),
 ctypes.POINTER(OVERLAPPED),
 LPVOID)
CreateFileW = kernel32.CreateFileW
CreateFileW.restype = ctypes.wintypes.HANDLE
CreateFileW.errcheck = _errcheck_handle
CreateFileW.argtypes = (ctypes.wintypes.LPCWSTR,
 ctypes.wintypes.DWORD,
 ctypes.wintypes.DWORD,
 LPVOID,
 ctypes.wintypes.DWORD,
 ctypes.wintypes.DWORD,
 ctypes.wintypes.HANDLE)
CloseHandle = kernel32.CloseHandle
CloseHandle.restype = ctypes.wintypes.BOOL
CloseHandle.argtypes = (ctypes.wintypes.HANDLE,)
CancelIoEx = kernel32.CancelIoEx
CancelIoEx.restype = ctypes.wintypes.BOOL
CancelIoEx.errcheck = _errcheck_bool
CancelIoEx.argtypes = (ctypes.wintypes.HANDLE, ctypes.POINTER(OVERLAPPED))
CreateEvent = kernel32.CreateEventW
CreateEvent.restype = ctypes.wintypes.HANDLE
CreateEvent.errcheck = _errcheck_handle
CreateEvent.argtypes = (LPVOID,
 ctypes.wintypes.BOOL,
 ctypes.wintypes.BOOL,
 ctypes.wintypes.LPCWSTR)
SetEvent = kernel32.SetEvent
SetEvent.restype = ctypes.wintypes.BOOL
SetEvent.errcheck = _errcheck_bool
SetEvent.argtypes = (ctypes.wintypes.HANDLE,)
WaitForSingleObjectEx = kernel32.WaitForSingleObjectEx
WaitForSingleObjectEx.restype = ctypes.wintypes.DWORD
WaitForSingleObjectEx.errcheck = _errcheck_dword
WaitForSingleObjectEx.argtypes = (ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD, ctypes.wintypes.BOOL)
CreateIoCompletionPort = kernel32.CreateIoCompletionPort
CreateIoCompletionPort.restype = ctypes.wintypes.HANDLE
CreateIoCompletionPort.errcheck = _errcheck_handle
CreateIoCompletionPort.argtypes = (ctypes.wintypes.HANDLE,
 ctypes.wintypes.HANDLE,
 LPVOID,
 ctypes.wintypes.DWORD)
GetQueuedCompletionStatus = kernel32.GetQueuedCompletionStatus
GetQueuedCompletionStatus.restype = ctypes.wintypes.BOOL
GetQueuedCompletionStatus.errcheck = _errcheck_bool
GetQueuedCompletionStatus.argtypes = (ctypes.wintypes.HANDLE,
 LPVOID,
 LPVOID,
 ctypes.POINTER(OVERLAPPED),
 ctypes.wintypes.DWORD)
PostQueuedCompletionStatus = kernel32.PostQueuedCompletionStatus
PostQueuedCompletionStatus.restype = ctypes.wintypes.BOOL
PostQueuedCompletionStatus.errcheck = _errcheck_bool
PostQueuedCompletionStatus.argtypes = (ctypes.wintypes.HANDLE,
 ctypes.wintypes.DWORD,
 ctypes.wintypes.DWORD,
 ctypes.POINTER(OVERLAPPED))
GetFinalPathNameByHandleW = kernel32.GetFinalPathNameByHandleW
GetFinalPathNameByHandleW.restype = ctypes.wintypes.DWORD
GetFinalPathNameByHandleW.errcheck = _errcheck_dword
GetFinalPathNameByHandleW.argtypes = (ctypes.wintypes.HANDLE,
 ctypes.wintypes.LPWSTR,
 ctypes.wintypes.DWORD,
 ctypes.wintypes.DWORD)

class FILE_NOTIFY_INFORMATION(ctypes.Structure):
    _fields_ = [('NextEntryOffset', ctypes.wintypes.DWORD),
     ('Action', ctypes.wintypes.DWORD),
     ('FileNameLength', ctypes.wintypes.DWORD),
     ('FileName', ctypes.c_char * 1)]


LPFNI = ctypes.POINTER(FILE_NOTIFY_INFORMATION)
WATCHDOG_FILE_FLAGS = FILE_FLAG_BACKUP_SEMANTICS
WATCHDOG_FILE_SHARE_FLAGS = reduce(lambda x, y: x | y, [FILE_SHARE_READ, FILE_SHARE_WRITE, FILE_SHARE_DELETE])
WATCHDOG_FILE_NOTIFY_FLAGS = reduce(lambda x, y: x | y, [FILE_NOTIFY_CHANGE_FILE_NAME,
 FILE_NOTIFY_CHANGE_DIR_NAME,
 FILE_NOTIFY_CHANGE_ATTRIBUTES,
 FILE_NOTIFY_CHANGE_SIZE,
 FILE_NOTIFY_CHANGE_LAST_WRITE,
 FILE_NOTIFY_CHANGE_SECURITY,
 FILE_NOTIFY_CHANGE_LAST_ACCESS,
 FILE_NOTIFY_CHANGE_CREATION])
BUFFER_SIZE = 64000
PATH_BUFFER_SIZE = 2048

def _parse_event_buffer(readBuffer, nBytes):
    results = []
    while nBytes > 0:
        fni = ctypes.cast(readBuffer, LPFNI)[0]
        ptr = ctypes.addressof(fni) + FILE_NOTIFY_INFORMATION.FileName.offset
        filename = ctypes.string_at(ptr, fni.FileNameLength)
        results.append((fni.Action, filename.decode('utf-16')))
        numToSkip = fni.NextEntryOffset
        if numToSkip <= 0:
            break
        readBuffer = readBuffer[numToSkip:]
        nBytes -= numToSkip

    return results


def _is_observed_path_deleted(handle, path):
    buff = ctypes.create_unicode_buffer(PATH_BUFFER_SIZE)
    GetFinalPathNameByHandleW(handle, buff, PATH_BUFFER_SIZE, VOLUME_NAME_NT)
    return buff.value != path


def _generate_observed_path_deleted_event():
    path = ctypes.create_unicode_buffer('.')
    event = FILE_NOTIFY_INFORMATION(0, FILE_ACTION_DELETED_SELF, len(path), path.value.encode('utf-8'))
    event_size = ctypes.sizeof(event)
    buff = ctypes.create_string_buffer(PATH_BUFFER_SIZE)
    ctypes.memmove(buff, ctypes.addressof(event), event_size)
    return (buff, event_size)


def get_directory_handle(path):
    return CreateFileW(path, FILE_LIST_DIRECTORY, WATCHDOG_FILE_SHARE_FLAGS, None, OPEN_EXISTING, WATCHDOG_FILE_FLAGS, None)


def close_directory_handle(handle):
    try:
        CancelIoEx(handle, None)
        CloseHandle(handle)
    except OSError:
        try:
            CloseHandle(handle)
        except Exception:
            return


def read_directory_changes(handle, path, recursive):
    event_buffer = ctypes.create_string_buffer(BUFFER_SIZE)
    nbytes = ctypes.wintypes.DWORD()
    try:
        ReadDirectoryChangesW(handle, ctypes.byref(event_buffer), len(event_buffer), recursive, WATCHDOG_FILE_NOTIFY_FLAGS, ctypes.byref(nbytes), None, None)
    except OSError as e:
        if e.winerror == ERROR_OPERATION_ABORTED:
            return ([], 0)
        if _is_observed_path_deleted(handle, path):
            return _generate_observed_path_deleted_event()
        raise e

    try:
        int_class = long
    except NameError:
        int_class = int

    return (event_buffer.raw, int_class(nbytes.value))


class WinAPINativeEvent(object):

    def __init__(self, action, src_path):
        self.action = action
        self.src_path = src_path

    @property
    def is_added(self):
        return self.action == FILE_ACTION_CREATED

    @property
    def is_removed(self):
        return self.action == FILE_ACTION_REMOVED

    @property
    def is_modified(self):
        return self.action == FILE_ACTION_MODIFIED

    @property
    def is_renamed_old(self):
        return self.action == FILE_ACTION_RENAMED_OLD_NAME

    @property
    def is_renamed_new(self):
        return self.action == FILE_ACTION_RENAMED_NEW_NAME

    @property
    def is_removed_self(self):
        return self.action == FILE_ACTION_REMOVED_SELF

    def __repr__(self):
        return '<%s: action=%d, src_path=%r>' % (type(self).__name__, self.action, self.src_path)


def read_events(handle, path, recursive):
    buf, nbytes = read_directory_changes(handle, path, recursive)
    events = _parse_event_buffer(buf, nbytes)
    return [ WinAPINativeEvent(action, src_path) for action, src_path in events ]
