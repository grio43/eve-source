#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcaster\landingPadUtil.py
from inventorycommon.const import typeDeathlessShipcaster
from shipcaster.shipcasterConst import DEFAULT_MAX_LANDING_PAD_LINKS

def GetMaxLandingPadLinks(typeID):
    if typeID == typeDeathlessShipcaster:
        return 2
    return DEFAULT_MAX_LANDING_PAD_LINKS
