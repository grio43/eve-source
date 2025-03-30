#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\sys\buildversion.py
from eveprefs import boot

def GetBuildVersionAsInt():
    try:
        return int(boot.build)
    except ValueError:
        return 0
