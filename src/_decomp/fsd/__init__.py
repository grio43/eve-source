#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\__init__.py
import logging
import os
import platform
CONSTANT_DIRECTORIES = ['eve', 'packages']
_branch_root = None
logger = logging.getLogger(__name__)
try:
    unicode('')
except NameError:
    unicode = str

if platform.system() == 'Windows':

    def GetFullName(path):
        from ctypes import create_unicode_buffer, windll
        if os.path.exists(path):
            BUFFER_SIZE = 500
            buf = create_unicode_buffer(BUFFER_SIZE)
            get_long_path_name = windll.kernel32.GetLongPathNameW
            get_long_path_name(unicode(path), buf, BUFFER_SIZE)
            return buf.value
        else:
            return path


else:

    def GetFullName(path):
        return path


def AbsJoin(*paths):
    return os.path.abspath(os.path.join(*paths))


def GetBranchRoot():
    global _branch_root
    if _branch_root is not None:
        return _branch_root
    path = os.path.abspath(__file__)
    while path:
        list_path = path.split(os.sep)[0:-1]
        drive, tail = list_path[0], list_path[1:]
        if tail:
            path = os.path.join(drive, os.sep, *tail)
            if all((os.path.exists(os.path.join(path, dirs)) for dirs in CONSTANT_DIRECTORIES)):
                _branch_root = GetFullName(os.path.abspath(path))
                return _branch_root
        else:
            raise RuntimeError('The file you are running is not inside the Perforce branch hierarchy, thus we are unable to resolve your branch root path')


def GetBranchName():
    return os.path.basename(GetFullName(GetBranchRoot()))


def GetBranchType():
    d = os.path.dirname(GetBranchRoot())
    _, branch_type = os.path.split(d)
    return branch_type
