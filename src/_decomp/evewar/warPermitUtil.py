#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evewar\warPermitUtil.py


def GetLabelPathForAllowWar(allowWar):
    if allowWar is None:
        return 'UI/WarPermit/CorpStatusWarPermitUnknown'
    elif allowWar:
        return 'UI/WarPermit/CorpStatusWarAllowed'
    else:
        return 'UI/WarPermit/CorpStatusWarNotAllowed'
