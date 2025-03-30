#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\attribute.py
import dogma.data as dogma_data
from carbon.common.script.util import mathCommon
from dogma.attributes import format
MIN_IN_MS = 60000
CLOSE_ENOUGH_TOLERANCE = 1e-06

def FloatCloseEnough(a, b):
    return mathCommon.FloatCloseEnough(a, b, CLOSE_ENOUGH_TOLERANCE)


def CreateAttribute(attributeID, value, baseValue = None):
    if baseValue is None:
        attribute = Attribute(attributeID, value)
    else:
        attribute = ModifiedAttribute(Attribute(attributeID, baseValue), value)
    return attribute


def IsModified(attribute):
    return hasattr(attribute, 'baseValue')


def IsMutated(attribute):
    return hasattr(attribute, 'sourceValue')


class Attribute(object):

    def __init__(self, attributeID, value):
        self.attributeID = attributeID
        self.value = value
        self._info = dogma_data.get_attribute(attributeID)

    @property
    def displayName(self):
        return dogma_data.get_attribute_display_name(self.attributeID)

    @property
    def displayValue(self):
        return self.Format(self.value)

    @property
    def highIsGood(self):
        return self._info.highIsGood

    @property
    def iconID(self):
        return self._info.iconID

    @property
    def unitID(self):
        return self._info.unitID

    @property
    def isPublished(self):
        return self._info.published

    def Format(self, value):
        if self._info.unitID == const.unitMilliseconds and value >= 5 * MIN_IN_MS:
            info = format.GetFormattedAttributeAndValueAllowZero(self.attributeID, value / MIN_IN_MS / 60, const.unitHour)
        else:
            info = format.GetFormattedAttributeAndValueAllowZero(self.attributeID, value)
        return info.value

    def FormatDiff(self, diff):
        return format.GetFormattedDiff(self.attributeID, diff)


class ModifiedAttribute(object):

    def __init__(self, attribute, value):
        self._attribute = attribute
        self.value = value

    def __getattr__(self, name):
        return getattr(self._attribute, name)

    @property
    def baseValue(self):
        return self._attribute.value

    @property
    def displayBaseValue(self):
        return self.Format(self.baseValue)

    @property
    def isSame(self):
        return FloatCloseEnough(self.value, self.baseValue)

    @property
    def isBetter(self):
        if self.isSame:
            return False
        elif self.highIsGood:
            return self.value > self.baseValue
        else:
            return self.value < self.baseValue


class MutatedAttribute(object):

    def __init__(self, attribute, sourceValue, minValue, maxValue, highIsGood = None):
        self._attribute = attribute
        self._highIsGood = highIsGood
        self._maxValue = max(minValue, maxValue)
        self._minValue = min(minValue, maxValue)
        self.sourceValue = sourceValue

    def __getattr__(self, name):
        return getattr(self._attribute, name)

    @property
    def highIsGood(self):
        if self._highIsGood is not None:
            return self._highIsGood
        else:
            return self._attribute.highIsGood

    @property
    def mutationMax(self):
        return self._maxValue

    @property
    def mutationMin(self):
        return self._minValue

    @property
    def mutationHigh(self):
        if self.highIsGood:
            return self._maxValue
        else:
            return self._minValue

    @property
    def mutationLow(self):
        if self.highIsGood:
            return self._minValue
        else:
            return self._maxValue

    @property
    def displaySourceValue(self):
        return self.Format(self.sourceValue)

    @property
    def displayMutationHigh(self):
        return self.Format(self.mutationHigh)

    @property
    def displayMutationLow(self):
        return self.Format(self.mutationLow)

    @property
    def isMutationPositive(self):
        return self.highIsGood and self.value > self.sourceValue or not self.highIsGood and self.value < self.sourceValue
