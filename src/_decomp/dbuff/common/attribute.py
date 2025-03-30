#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dbuff\common\attribute.py
from dogma.attributes import AttributeInterface

class DynamicBuffAttribute(AttributeInterface):
    __slots__ = ['outgoingModifiers', 'item', 'outputValue']

    def __init__(self, outputValue):
        self.outputValue = outputValue
        self.outgoingModifiers = set()
        self.item = None

    def __str__(self):
        return 'DynamicBuffAttribute(%s) -> %s outputs' % (self.outputValue, len(self.outgoingModifiers))

    def AddOutgoingModifier(self, op, outgoingAttrib):
        self.outgoingModifiers.add((op, outgoingAttrib))

    def RemoveOutgoingModifier(self, op, outgoingAttrib):
        try:
            self.outgoingModifiers.remove((op, outgoingAttrib))
        except KeyError:
            pass

    def GetOutgoingModifiers(self):
        return list(self.outgoingModifiers)

    def CheckIntegrity(self):
        return True

    def GetBaseValue(self):
        return self.outputValue

    def GetValue(self):
        return self.outputValue

    def SetOutputValue(self, value):
        if value is None:
            raise TypeError('Cannot set dbuff output to None')
        if value == self.outputValue:
            return
        self.outputValue = value
        for op, outgoing in self.outgoingModifiers:
            outgoing.MarkDirty()
