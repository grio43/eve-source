#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dynamicItem\const.py
import evetypes
from eve.client.script.ui import eveColor
COLOR_DECAYED = (0.756, 0.152, 0.176)
COLOR_GRAVID = (0.8, 0.768, 0.345)
COLOR_NEGATIVE = eveColor.DANGER_RED[:3]
COLOR_POSITIVE = eveColor.SUCCESS_GREEN[:3]
COLOR_UNSTABLE = (1.0, 0.556, 0.176)
ABNORMAL_TYPE_LIST_ID = 53
DECAYED_TYPE_LIST_ID = 52
GRAVID_TYPE_LIST_ID = 54
UNSTABLE_TYPE_LIST_ID = 55

def GetAbnormalTypes():
    return evetypes.GetTypeIDsByListID(ABNORMAL_TYPE_LIST_ID)


def GetDecayedTypes():
    return evetypes.GetTypeIDsByListID(DECAYED_TYPE_LIST_ID)


def GetGravidTypes():
    return evetypes.GetTypeIDsByListID(GRAVID_TYPE_LIST_ID)


def GetUnstableTypes():
    return evetypes.GetTypeIDsByListID(UNSTABLE_TYPE_LIST_ID)
