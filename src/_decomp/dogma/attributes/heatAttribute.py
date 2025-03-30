#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\heatAttribute.py
import gametime
from dogma.attributes import Attribute
from dogma.const import attributeHeatHi, attributeHeatDissipationRateHi, attributeHeatCapacityHi
from dogma.const import attributeHeatMed, attributeHeatDissipationRateMed, attributeHeatCapacityMed
from dogma.const import attributeHeatLow, attributeHeatDissipationRateLow, attributeHeatCapacityLow
from dogma.const import attributeHeatGenerationMultiplier, dgmTauConstant
from math import exp
import weakref

def CalculateHeat(currentHeat, timeDiff, incomingHeat, dissipationRate, heatGenerationMul, heatCap):
    if incomingHeat < 5e-08:
        currentHeat *= exp(-timeDiff / 1000 * dissipationRate)
        if round(currentHeat, 0) <= 0:
            currentHeat = 0.0
    else:
        hgm = heatGenerationMul
        hc = heatCap
        currentHeat = hc - hc * exp(-timeDiff / 1000 * incomingHeat * hgm) + currentHeat * exp(-timeDiff / 1000 * incomingHeat * hgm)
    return currentHeat


class HeatAttribute(Attribute):
    __slots__ = ['heatGenerationMultiplierAttribute',
     'heatDissipationRateAttribute',
     'prevCap',
     'lastCalcTime',
     'incomingHeat']

    def __init__(self, attribID, baseValue, dogmaItem, dogmaLM, staticAttr):
        super(HeatAttribute, self).__init__(attribID, baseValue, dogmaItem, dogmaLM, staticAttr)
        dissipationAttributeByHeatID = {attributeHeatHi: attributeHeatDissipationRateHi,
         attributeHeatMed: attributeHeatDissipationRateMed,
         attributeHeatLow: attributeHeatDissipationRateLow}
        heatCapacityByHeatID = {attributeHeatHi: attributeHeatCapacityHi,
         attributeHeatMed: attributeHeatCapacityMed,
         attributeHeatLow: attributeHeatCapacityLow}
        self.heatGenerationMultiplierAttribute = weakref.proxy(self.item.attributes[attributeHeatGenerationMultiplier])
        self.capAttrib = weakref.proxy(self.item.attributes[heatCapacityByHeatID[attribID]])
        self.heatDissipationRateAttribute = weakref.proxy(self.item.attributes[dissipationAttributeByHeatID[attribID]])
        capVal = self.capAttrib.GetValue()
        self.currentValue = min(capVal, self.currentValue)
        self.prevCap = capVal
        self.lastCalcTime = gametime.GetSimTime()
        self.incomingHeat = Attribute(None, 0, dogmaItem, dogmaLM, staticAttr)

    def Update(self):
        currentTime = gametime.GetSimTime()
        timeDiff = (currentTime - self.lastCalcTime) / float(dgmTauConstant)
        incHeat = self.incomingHeat.GetValue()
        self.currentValue = CalculateHeat(self.currentValue, timeDiff, incHeat, self.heatDissipationRateAttribute.GetValue(), self.heatGenerationMultiplierAttribute.GetValue(), self.capAttrib.GetValue())
        self.dirty = False
        self.lastCalcTime = currentTime
        return self.currentValue

    def GetValue(self):
        if self.dirty or self.lastCalcTime != gametime.GetSimTime():
            self.Update()
        return self.currentValue

    def GetFullHeatInfo(self):
        if self.dirty or self.lastCalcTime != gametime.GetSimTime():
            self.MarkDirty()
            self.Update()
        return (self.currentValue, self.lastCalcTime, self.capAttrib.GetValue())

    def GetHeatMessage(self):
        if self.dirty or self.lastCalcTime != gametime.GetSimTime():
            self.MarkDirty()
            self.Update()
        return (self.currentValue,
         self.capAttrib.currentValue,
         self.incomingHeat.GetValue(),
         self.heatGenerationMultiplierAttribute.currentValue,
         self.heatDissipationRateAttribute.currentValue,
         self.lastCalcTime)

    def SetBaseValue(self, newBaseValue, asPercentage = False):
        if self.currentValue != newBaseValue:
            if asPercentage:
                newBaseValue *= self.capAttrib.GetValue()
            self.currentValue = newBaseValue
            self.lastCalcTime = gametime.GetSimTime()
            self.MarkDirty()

    def AddIncomingModifier(self, op, attribute):
        self.Update()
        self.incomingHeat.AddIncomingModifier(op, attribute)

    def RemoveIncomingModifier(self, op, attribute):
        self.Update()
        self.incomingHeat.RemoveIncomingModifier(op, attribute)

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
