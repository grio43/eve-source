#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\dep_util.py
__revision__ = '$Id: dep_util.py 82110 2010-06-20 13:38:51Z kristjan.jonsson $'
import os
from distutils.errors import DistutilsFileError

def newer(source, target):
    if not os.path.exists(source):
        raise DistutilsFileError("file '%s' does not exist" % os.path.abspath(source))
    if not os.path.exists(target):
        return True
    return os.stat(source).st_mtime > os.stat(target).st_mtime


def newer_pairwise(sources, targets):
    if len(sources) != len(targets):
        raise ValueError, "'sources' and 'targets' must be same length"
    n_sources = []
    n_targets = []
    for source, target in zip(sources, targets):
        if newer(source, target):
            n_sources.append(source)
            n_targets.append(target)

    return (n_sources, n_targets)


def newer_group(sources, target, missing = 'error'):
    if not os.path.exists(target):
        return True
    target_mtime = os.stat(target).st_mtime
    for source in sources:
        if not os.path.exists(source):
            if missing == 'error':
                pass
            elif missing == 'ignore':
                continue
            elif missing == 'newer':
                return True
        if os.stat(source).st_mtime > target_mtime:
            return True

    return False
