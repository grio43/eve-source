#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipfitting\fitting.py
from collections import defaultdict
import inventorycommon
import inventorycommon.const as invconst
from inventorycommon.util import IsShipFittingFlag, IsSubsystemFlag
import logging
import evetypes
from utillib import KeyVal
logger = logging.getLogger(__name__)
INVALID_FITTING_ID = -1

class Fitting(object):

    def __init__(self, fitData, shipInv):
        self.itemTypes = defaultdict(lambda : 0)
        self.modulesByFlag = {}
        self.dronesByType = {}
        self.fightersByType = {}
        self.chargesByType = {}
        self.fuelByType = {}
        self.implantsByType = {}
        self.rigsToFit = {}
        self.numSubSystems = 0
        for typeID, flag, qty in fitData:
            groupID = evetypes.GetGroupID(typeID)
            categoryID = evetypes.GetCategoryID(typeID)
            if self._IsRig(flag):
                self.rigsToFit[flag] = typeID
            if self._IsSubsystem(flag):
                self.numSubSystems += 1
            if self._IsModule(flag):
                self.modulesByFlag[flag] = typeID
            elif self._IsDrone(flag):
                self.dronesByType[typeID] = qty
            elif self._IsFighter(flag):
                self.fightersByType[typeID] = qty
            elif self._IsFuel(flag, groupID):
                self.fuelByType[typeID] = qty
            elif self._IsImplant(flag, categoryID):
                self.implantsByType[typeID] = qty
            elif self._IsAmmo(flag, groupID):
                self.chargesByType[typeID] = qty
            else:
                logger.error('LoadFitting::flag neither fitting nor drone bay %s, %s', typeID, flag)
                continue
            skipType = False
            if shipInv:
                for item in shipInv.List(flag):
                    if item.typeID == typeID:
                        itemQty = item.stacksize
                        if itemQty == qty:
                            skipType = True
                            break
                        else:
                            qty -= itemQty

            if skipType:
                continue
            self.itemTypes[typeID] += qty

    def _IsSubsystem(self, flag):
        return IsSubsystemFlag(flag)

    def _IsRig(self, flag):
        return invconst.flagRigSlot0 <= flag <= invconst.flagRigSlot7

    def _IsModule(self, flag):
        return IsShipFittingFlag(flag) and flag != invconst.flagHiddenModifers

    def _IsDrone(self, flag):
        return flag == invconst.flagDroneBay

    def _IsFighter(self, flag):
        return flag == invconst.flagFighterBay

    def _IsFuel(self, flag, groupID):
        return flag == invconst.flagCargo and groupID == invconst.groupIceProduct

    def _IsImplant(self, flag, categoryID):
        return flag == invconst.flagCargo and categoryID == invconst.categoryImplant

    def _IsAmmo(self, flag, groupID):
        return flag == invconst.flagCargo

    def GetQuantityByType(self):
        return self.itemTypes

    def GetChargesByType(self):
        return self.chargesByType

    def GetIceByType(self):
        return self.fuelByType

    def GetModulesByFlag(self):
        return self.modulesByFlag

    def FittingHasRigs(self):
        return bool(self.rigsToFit)

    def GetRigsByFlag(self):
        return self.rigsToFit

    def GetDronesByType(self):
        return self.dronesByType

    def GetFigthersByType(self):
        return self.fightersByType

    def GetFittingSubSystemNumber(self):
        return self.numSubSystems

    def GetImplantsByType(self):
        return self.implantsByType

    def GetKeyValForApplyingFit(self):
        return KeyVal(chargesByType=self.GetChargesByType(), dronesByType=self.GetDronesByType(), fightersByTypeID=self.GetFigthersByType(), iceByType=self.GetIceByType(), modulesByFlag=self.GetModulesByFlag(), implantsByTypeID=self.GetImplantsByType())
