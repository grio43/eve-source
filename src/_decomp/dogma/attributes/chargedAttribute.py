#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\chargedAttribute.py
import gametime
from dogma.attributes import Attribute
from math import exp, sqrt
from dogma.dogmaLogging import LogTraceback
from dogma.const import dgmTauConstant
import weakref

class ChargedAttribute(Attribute):

    def __init__(self, attribID, baseValue, dogmaItem, dogmaLM, staticAttr):
        super(ChargedAttribute, self).__init__(attribID, baseValue, dogmaItem, dogmaLM, staticAttr)
        self.rechargeRateAttribute = weakref.proxy(self.item.attributes[staticAttr.chargeRechargeTimeID])
        capVal = self.capAttrib.GetValue()
        self.currentValue = min(capVal, self.currentValue)
        self.prevCap = capVal
        self.lastCalcTime = gametime.GetSimTime()
        self.rechargeRate = self.rechargeRateAttribute.GetValue() / 5.0
        self.rechargeRateAttribute.AddNonModifyingDependant(self)

    def Update(self):
        capVal = self.capAttrib.GetValue()
        self.rechargeRate = self.rechargeRateAttribute.GetValue() / 5.0
        rechargeDelayFactor = self.rechargeRate
        if capVal == 0:
            self.currentValue = 0
            self.prevCap = 0
            return
        if capVal != self.prevCap:
            if self.prevCap > 0:
                oldRatio = self.currentValue / self.prevCap
                self.currentValue = oldRatio * capVal
            self.prevCap = capVal
        if capVal <= self.currentValue:
            self.currentValue = capVal
            return
        if rechargeDelayFactor == 0:
            self.lastCalcTime = gametime.GetSimTime()
            return
        currentTime = gametime.GetSimTime()
        timeDiff_ms = (currentTime - self.lastCalcTime) / float(dgmTauConstant)
        if timeDiff_ms < -0.0001:
            return
        oldRatio = self.currentValue / capVal
        root = sqrt(oldRatio)
        rootBlendFactor = exp(-timeDiff_ms / rechargeDelayFactor)
        rootBlended = (root - 1.0) * rootBlendFactor + 1.0
        newRatio = rootBlended ** 2
        self.currentValue = newRatio * capVal
        self.lastCalcTime = currentTime

    def GetValue(self):
        if self.dirty or self.lastCalcTime != gametime.GetSimTime():
            self.Update()
        return self.currentValue

    def GetFullChargedInfo(self):
        if self.dirty or self.lastCalcTime != gametime.GetSimTime():
            self.Update()
        return (self.currentValue, self.prevCap, self.rechargeRate)

    def MarkDirty(self, silent = False):
        super(ChargedAttribute, self).MarkDirty(silent)
        if not silent:
            self.Update()

    def SetBaseValue(self, newBaseValue):
        if self.currentValue != newBaseValue:
            self.currentValue = newBaseValue
            self.lastCalcTime = gametime.GetSimTime()
            self.MarkDirty()

    def AddIncomingModifier(self, op, attribute):
        LogTraceback('Cannot modify a charged attribute!')

    def RemoveIncomingModifier(self, op, attribute):
        LogTraceback('Cannot modify a charged attribute!')

    def ResetBaseValue(self):
        self.Update()
        self.currentValue = self.typeValue

    def IncreaseBaseValue(self, addAmount):
        self.Update()
        self.currentValue += addAmount

    def DecreaseBaseValue(self, decAmount):
        self.Update()
        self.currentValue -= decAmount

    def GetPersistData(self):
        self.Update()
        return self.currentValue
