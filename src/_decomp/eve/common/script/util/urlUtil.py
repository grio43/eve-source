#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\urlUtil.py
import blue

def IsClientLaunchedThroughSteam():
    return blue.os.HasStartupArg('steamUser')


def AppendSteamOriginIfApplies(str):
    if IsClientLaunchedThroughSteam():
        return str + '_steam'
    return str
