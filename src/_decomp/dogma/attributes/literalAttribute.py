#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\literalAttribute.py
from dogma.attributes import AttributeInterface

class LiteralAttribute(AttributeInterface):
    __slots__ = ['value', 'item']

    def __init__(self, value):
        self.value = value
        self.item = None

    def __str__(self):
        return 'LiteralAttribute value %s' % self.value

    def GetBaseValue(self):
        return self.value

    def GetValue(self):
        return self.value

    def AddOutgoingModifier(self, op, attribute):
        pass

    def RemoveOutgoingModifier(self, op, attribute):
        pass

    def CheckIntegrity(self):
        return True
