#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\osutils\subst.py
import os
from . import win32api
from osutils import systemcall

class SubstError(Exception):
    pass


class SubstInvalidParameterError(SubstError):
    pass


class SubstPathNotFoundError(SubstError):
    pass


class SubstIncorrectNumberOfParamsError(SubstError):
    pass


class SubstDriveAlreadySubstedError(SubstError):
    pass


def _parse_drive_mapping_to_tuples(substoutput):
    lines = substoutput.splitlines()
    for li in lines:
        words = li.split('=>')
        drive = words[0][:2]
        path = words[-1].strip()
        yield (drive, path.lower())


def _parse_result_for_err(out = '', err = ''):
    lines = (out or '').splitlines() + (err or '').splitlines()
    for li in lines:
        if li.startswith('Invalid parameter - '):
            raise SubstInvalidParameterError, li
        if li.startswith('Path not found - '):
            raise SubstPathNotFoundError, li
        if li.startswith('Incorrect number of parameters - '):
            raise SubstIncorrectNumberOfParamsError, li
        if li == 'Drive already SUBSTed':
            raise SubstDriveAlreadySubstedError, li


def _get_mapped_drives_using_systemcall():
    out, err = systemcall('subst')
    return tuple(_parse_drive_mapping_to_tuples(out))


def _get_mapped_drives_using_win32api():

    def _getDrivePath():
        pattern = '\\??\\'
        zeroendChar = '\x00'
        isexisting = reversed(bin(win32api.GetLogicalDrives())[2:])
        for i, exists in enumerate(isexisting):
            if exists == '0':
                continue
            drive = chr(65 + i) + ':'
            dospath = win32api.QueryDosDevice(drive)
            if not dospath.startswith(pattern):
                continue
            path = dospath.split(pattern)[-1].rstrip(zeroendChar)
            yield (drive, path)

    return tuple(_getDrivePath())


def get_mapped_drives():
    if win32api:
        return _get_mapped_drives_using_win32api()
    return _get_mapped_drives_using_systemcall()


GetMappedDrives = get_mapped_drives

def _set_drive_mapping_using_win32api(drive, path):
    win32api.DefineDosDevice(0, drive, path)


def _set_drive_mapping_using_systemcall(drive, path):
    out, err = systemcall('subst', drive, path)
    _parse_result_for_err(out, err)


def set_drive_mapping(drive, path):
    if win32api:
        _set_drive_mapping_using_win32api(drive, path)
    else:
        _set_drive_mapping_using_systemcall(drive, path)


SetDriveMapping = set_drive_mapping

def delete_drive_mapping(drive):
    out, err = systemcall('subst', '/D', drive)
    _parse_result_for_err(out, err)


DeleteDriveMapping = delete_drive_mapping

def get_subst_path(path):
    for drive, substpath in get_mapped_drives():
        if path.lower().startswith(drive.lower()):
            return path
        if path.lower().startswith(substpath.lower()):
            return path.lower().replace(substpath.lower(), drive)

    raise SubstPathNotFoundError(path)


GetSubstedPath = get_subst_path

def get_unsubst_path(path):

    def testArg(p):
        if p is None:
            raise ValueError('path cannot be None')

    testArg(path)
    driveToPath = dict(((k.lower(), v) for k, v in get_mapped_drives()))

    def getUnsubst(p):
        testArg(p)
        p = os.path.abspath(p)
        head, tail = os.path.splitdrive(p)
        if tail.startswith(os.path.sep):
            tail = tail[1:]
        real = driveToPath.get(head.lower())
        if real is None:
            return p
        return os.path.join(real, tail)

    if isinstance(path, basestring):
        return getUnsubst(path)
    return map(getUnsubst, path)


GetUnsubstedPath = get_unsubst_path
