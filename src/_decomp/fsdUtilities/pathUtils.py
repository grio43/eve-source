#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdUtilities\pathUtils.py
from fsd import GetBranchRoot, AbsJoin

def GetStaticDataPath(path = None):
    if path is None:
        return GetAbsoluteBranchPath('eve/staticData/')
    else:
        return GetAbsoluteBranchPath('eve/staticData/', path)


def GetAbsoluteBranchPath(*paths):
    return AbsJoin(GetBranchRoot(), *paths)
