#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\ammoloadingUtils.py
from caching.memoize import Memoize
from evetypes import GetGroupID, GetVolume
from dogma import const as dogmaConst

@Memoize
def GetRequiredSpace(chargeTypeID, quantity):
    return GetVolume(chargeTypeID) * quantity


@Memoize
def GetChargeGroupsForLauncher(moduleTypeID, dogmaStaticMgr):
    ret = set()
    for chargeGroupAttribute in dogmaStaticMgr.GetChargeGroupAttributes():
        chargeGroup = dogmaStaticMgr.GetTypeAttribute2(moduleTypeID, chargeGroupAttribute)
        if chargeGroup > 0:
            ret.add(int(chargeGroup))

    return ret


@Memoize
def CanModuleBeLoadedWithCharges(moduleTypeID, dogmaStaticMgr):
    return bool(GetChargeGroupsForLauncher(moduleTypeID, dogmaStaticMgr))


@Memoize
def GetModuleCapacityForAmmoType(moduleTypeID, ammoTypeID, dogmaStaticMgr):
    moduleCapacity = dogmaStaticMgr.GetTypeAttribute2(moduleTypeID, dogmaConst.attributeCapacity)
    chargeSize = dogmaStaticMgr.GetTypeAttribute2(ammoTypeID, dogmaConst.attributeVolume)
    return int(moduleCapacity / chargeSize + 1e-07)


@Memoize
def IsChargeCompatibleWithLauncher(ammoTypeID, moduleTypeID, dogmaStaticMgr):
    if GetGroupID(ammoTypeID) in GetChargeGroupsForLauncher(moduleTypeID, dogmaStaticMgr):
        requiredChargeSize = dogmaStaticMgr.GetTypeAttribute2(moduleTypeID, dogmaConst.attributeChargeSize)
        if requiredChargeSize and requiredChargeSize == dogmaStaticMgr.GetTypeAttribute2(ammoTypeID, dogmaConst.attributeChargeSize):
            return True
        if not requiredChargeSize and GetModuleCapacityForAmmoType(moduleTypeID, ammoTypeID, dogmaStaticMgr) > 0:
            return True
    return False
