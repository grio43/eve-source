#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\brennivin\platformutils.py
import os as _os
import struct as _struct
import sys as _sys
try:
    import multiprocessing as _multiprocessing
except ImportError:
    _multiprocessing = None

from .dochelpers import ignore as _ignore
EXE_MAYA = 'Maya Python'
EXE_MAYA27 = 'Maya Python 2.7'
EXE_EXEFILE = 'Exefile Python'
EXE_VANILLA26 = 'Pure Python 2.6'
EXE_VANILLA27 = 'Pure Python 2.7'

def get_interpreter_flavor(_exepath = _ignore, _vinfo = _ignore):
    _exepath = _exepath or _sys.executable
    _vinfo = _vinfo or _sys.version_info

    def getType(path):
        path = path.lower().replace('_debug.exe', '.exe').replace('_internal.exe', '.exe')
        if path.endswith(('exefile.exe', 'exefileconsole.exe')):
            return EXE_EXEFILE
        if path.endswith(('maya.exe', 'mayabatch.exe', 'mayapy.exe')):
            if _vinfo[1] == 6:
                return EXE_MAYA
            if _vinfo[1] == 7:
                return EXE_MAYA27
        if path.endswith(('python.exe', 'pythonw.exe', 'python')):
            try:
                import stackless
                return EXE_EXEFILE
            except ImportError:
                if _vinfo[1] == 6:
                    return EXE_VANILLA26
                if _vinfo[1] == 7:
                    return EXE_VANILLA27

        raise NameError("Could not identify executable path '%s'" % path)

    return getType(_exepath)


def is_64bit_windows():
    return 'PROGRAMFILES(x86)' in _os.environ


def is_64bit_process(_structmod = _ignore):
    _structmod = _structmod or _struct
    size = _structmod.calcsize('P')
    if size == 8:
        return True
    if size == 4:
        return False
    raise OSError('Could not determine process architecture for %s' % size)


def cpu_count(_multiprocmod = _ignore):
    _multiprocmod = _multiprocmod or _multiprocessing
    if _multiprocessing:
        try:
            return _multiprocmod.cpu_count()
        except (NotImplementedError, AttributeError):
            pass

    try:
        res = int(_os.environ['NUMBER_OF_PROCESSORS'])
        if res > 0:
            return res
    except (KeyError, ValueError):
        pass

    raise SystemError('Number of processors could not be determined.')
