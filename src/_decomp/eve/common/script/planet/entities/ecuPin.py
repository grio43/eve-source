#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\planet\entities\ecuPin.py
import math
import blue
from carbon.common.script.util.format import FmtDate
from eve.common.lib import appConst as const
from eve.common.script.planet.entities.basePin import BasePin
from eve.common.script.planet.entities.basePin import STATE_ACTIVE, STATE_IDLE
from eve.common.script.util import planetCommon
from eveexceptions import UserError
EXTRACTOR_MAX_CYCLES = 120
PROGRAM_INSTALLATION_COOLDOWN = 1 * const.MIN

class EcuPin(BasePin):
    __slots__ = ['programType',
     'qtyPerCycle',
     'cycleTime',
     'installTime',
     'expiryTime',
     'heads',
     'headRadius']

    def __init__(self, typeID):
        BasePin.__init__(self, typeID)
        self.programType = None
        self.qtyPerCycle = 0
        self.cycleTime = None
        self.installTime = None
        self.expiryTime = None
        self.heads = []
        self.headRadius = None

    def GetCycleTime(self):
        return self.cycleTime

    def GetBaseCycleTime(self):
        return self.eventHandler.GetTypeAttribute(self.typeID, const.attributePinCycleTime)

    def GetBaseExtractionQty(self):
        return self.eventHandler.GetTypeAttribute(self.typeID, const.attributePinExtractionQuantity)

    def GetAreaOfInfluence(self):
        return self.eventHandler.GetTypeAttribute(self.typeID, const.attributeEcuAreaOfInfluence)

    def CanAccept(self, typeID, quantity):
        return 0

    def AddCommodity(self, typeID, quantity):
        return 0

    def Run(self, runTime):
        self.lastRunTime = runTime
        if self.programType is None:
            return {}
        products = {}
        if self.IsActive():
            products[self.programType] = self.GetProgramOutput(runTime)
            if self.expiryTime <= runTime:
                self.SetState(STATE_IDLE)
        return products

    def CanInstallProgram(self, runTime):
        if self.programType is None:
            return True
        if runTime is not None:
            if self.expiryTime <= runTime:
                return True
            nextEditTime = self.installTime + PROGRAM_INSTALLATION_COOLDOWN
            if nextEditTime <= runTime:
                return True
            raise UserError('CantInstallProgramNeedsCooldown', {'ecu': (const.UE_TYPEID, self.typeID),
             'timeDiff': FmtDate(nextEditTime - runTime)})
        else:
            return True

    def GetNextEditTime(self):
        if self.installTime is None:
            return
        return self.installTime + PROGRAM_INSTALLATION_COOLDOWN

    def InstallProgram(self, programType, cycleTime, expiryTime, qtyPerCycle, headRadius, lastRunTime = None, installTime = None):
        if qtyPerCycle <= 0:
            self.LogError('ownerID', self.ownerID, '| ECU pin error, zero qtyPerCycle. Defaulting to', EXTRACTOR_MAX_CYCLES, 'cycles to extract')
            return
        self.programType = int(programType)
        self.qtyPerCycle = qtyPerCycle
        self.expiryTime = expiryTime
        self.cycleTime = cycleTime
        self.SetState(STATE_ACTIVE)
        if lastRunTime is not None:
            self.lastRunTime = lastRunTime
        else:
            self.lastRunTime = blue.os.GetWallclockTime()
        if installTime is not None:
            self.installTime = installTime
        else:
            self.installTime = self.lastRunTime
        self.headRadius = headRadius
        return self.lastRunTime

    def ClearProgram(self):
        self.programType = None
        self.qtyPerCycle = 0
        self.expiryTime = None
        self.installTime = None
        self.SetState(STATE_IDLE)

    def CanActivate(self):
        if self.activityState < STATE_ACTIVE:
            return False
        return self.programType is not None

    def IsActive(self):
        return self.programType is not None and self.activityState > STATE_IDLE

    def GetProgramInformation(self):
        if self.programType is None:
            return
        return [self.id,
         int(self.programType),
         self.cycleTime / const.MIN if self.cycleTime is not None else None,
         self.qtyPerCycle,
         self.installTime,
         self.expiryTime,
         self.headRadius]

    def GetProgramParameters(self):
        if self.programType is not None:
            return (self.qtyPerCycle, self.cycleTime, int((self.expiryTime - self.installTime) / self.cycleTime))

    def IsProducer(self):
        return True

    def IsNeedingAttention(self):
        return not self.GetProducts() or not self.IsActive() or self.IsExpired()

    def IsExtractor(self):
        return True

    def GetProducts(self):
        if self.programType is None:
            return {}
        else:
            return {self.programType: self.qtyPerCycle}

    def GetProductMaxOutput(self):
        if self.programType is None:
            return {}
        return {self.programType: self.GetMaxOutput()}

    def GetTimeToExpiry(self):
        if self.activityState <= STATE_IDLE:
            return 0
        return self.expiryTime - blue.os.GetWallclockTime()

    def IsExpired(self):
        if not self.expiryTime:
            return False
        if self.expiryTime < blue.os.GetWallclockTime():
            return True
        return False

    def Serialize(self, full = False):
        data = BasePin.Serialize(self, full)
        data.cycleTime = self.cycleTime
        data.programType = int(self.programType) if self.programType is not None else None
        data.qtyPerCycle = self.qtyPerCycle
        data.expiryTime = self.expiryTime
        data.installTime = self.installTime
        data.headRadius = self.headRadius
        data.heads = self.heads[:]
        return data

    def GetExtractionType(self):
        if self.programType is not None:
            return int(self.programType)

    def HasDifferingProgram(self, otherPin):
        if self.installTime != otherPin.installTime:
            return True
        if self.GetCycleTime() != otherPin.GetCycleTime():
            return True
        if self.qtyPerCycle != otherPin.qtyPerCycle:
            return True
        if self.programType != otherPin.programType:
            return True
        if self.expiryTime != otherPin.expiryTime:
            return True
        return False

    def FindHead(self, index):
        for head in self.heads:
            if head[0] == index:
                return head

    def GetNumHeads(self):
        return len(self.heads)

    def AddHead(self, headID = None, latitude = None, longitude = None):
        if len(self.heads) >= planetCommon.ECU_MAX_HEADS:
            return
        else:
            if latitude is None:
                latitude = self.latitude
            if longitude is None:
                longitude = self.longitude
            if headID is not None:
                self.heads.append((headID, latitude, longitude))
                self.heads.sort()
                return headID
            newHeadIndex = self.GetNextAvailableHeadID()
            self.heads.insert(newHeadIndex, (newHeadIndex, latitude, longitude))
            return newHeadIndex

    def GetNextAvailableHeadID(self):
        lastHead = None
        currHeadIDs = [ head[0] for head in self.heads ]
        for i in xrange(planetCommon.ECU_MAX_HEADS):
            if i not in currHeadIDs:
                return i

        raise UserError('CannotInstallMoreExtractors')

    def RemoveHead(self, index):
        headIdx = None
        for idx, head in enumerate(self.heads):
            if head[0] == index:
                headIdx = idx

        if headIdx is not None:
            self.heads.pop(headIdx)

    def SetHeads(self, heads):
        self.heads = heads[:]

    def SetHeadPosition(self, headID, latitude, longitude):
        self.RemoveHead(headID)
        self.AddHead(headID, latitude, longitude)

    def SetExtractorHeadRadius(self, radius):
        self.headRadius = radius

    def GetExtractorHeadRadius(self):
        if self.headRadius is None:
            self.headRadius = 0.01
        return self.headRadius

    def GetPowerUsage(self, numHeads = None):
        if numHeads is None:
            numHeads = len(self.heads)
        ecuPowerLoad = self.eventHandler.GetTypeAttribute(self.typeID, const.attributePowerLoad)
        return ecuPowerLoad + self.GetExtractorHeadPowerUsage() * numHeads

    def GetExtractorHeadPowerUsage(self):
        return self.eventHandler.GetTypeAttribute(self.typeID, const.attributeExtractorHeadPower)

    def GetCpuUsage(self, numHeads = None):
        if numHeads is None:
            numHeads = len(self.heads)
        ecuCpuLoad = self.eventHandler.GetTypeAttribute(self.typeID, const.attributeCpuLoad)
        return ecuCpuLoad + self.GetExtractorHeadCpuUsage() * numHeads

    def GetExtractorHeadCpuUsage(self):
        return self.eventHandler.GetTypeAttribute(self.typeID, const.attributeExtractorHeadCPU)

    def GetMaxOutput(self, baseOutput = None, cycleTime = None):
        if baseOutput is None:
            baseOutput = self.qtyPerCycle
        if cycleTime is None:
            cycleTime = self.cycleTime
        scalar = self.GetAttribute(const.attributeEcuNoiseFactor) + 1
        return int(scalar * baseOutput) * cycleTime / const.SEC / 900.0

    def GetAttribute(self, attributeID):
        return self.eventHandler.GetTypeAttribute(self.typeID, attributeID)

    def GetProgramOutput(self, currentTime, baseValue = None, cycleTime = None, startTime = None):
        if baseValue is None:
            baseValue = self.qtyPerCycle
        if cycleTime is None or cycleTime <= 0:
            cycleTime = self.cycleTime
        if startTime is None:
            startTime = self.installTime
        decayFactor = self.GetAttribute(const.attributeEcuDecayFactor)
        noiseFactor = self.GetAttribute(const.attributeEcuNoiseFactor)
        timeDiff = currentTime - startTime
        if cycleTime <= 0:
            cycleNum = 0
        else:
            cycleNum = max((timeDiff + const.SEC) / cycleTime - 1, 0)
        barWidth = cycleTime / const.SEC / 900.0
        t = (cycleNum + 0.5) * barWidth
        decayValue = baseValue / (1 + t * decayFactor)
        f1 = 1.0 / 12
        f2 = 1.0 / 5
        f3 = 1.0 / 2
        phaseShift = baseValue ** 0.7
        sinA = math.cos(phaseShift + t * f1)
        sinB = math.cos(phaseShift / 2 + t * f2)
        sinC = math.cos(t * f3)
        sinStuff = (sinA + sinB + sinC) / 3
        sinStuff = max(0, sinStuff)
        barHeight = decayValue * (1 + noiseFactor * sinStuff)
        return int(barWidth * barHeight)

    def GetProgramOutputPrediction(self, baseValue, cycleTime, length):
        vals = []
        startTime = 0
        for i in xrange(length):
            currentTime = (i + 1) * cycleTime
            vals.append(self.GetProgramOutput(currentTime, baseValue, cycleTime, startTime))

        return vals
