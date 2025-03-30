#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\attributeInterface.py
from dogma.dogmaLogging import LogWarn, LogTraceback

class AttributeInterface(object):
    __slots__ = ['__weakref__']

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return '<' + self.__str__() + ' at ' + '0x%x' % id(self) + '>'

    def friendlyStr(self):
        return str(self)

    def performantStr(self):
        return str(self)

    def AddModifierTo(self, operation, toAttrib):
        self.AddOutgoingModifier(operation, toAttrib)
        toAttrib.AddIncomingModifier(operation, self)

    def RemoveModifierTo(self, operation, toAttrib):
        self.RemoveOutgoingModifier(operation, toAttrib)
        toAttrib.RemoveIncomingModifier(operation, self)

    def GetIncomingModifiers(self):
        return []

    def GetOutgoingModifiers(self):
        return []

    def RemoveAllModifiers(self):
        pass

    def IsAnOrphan(self):
        return False

    def CheckIntegrity(self):
        if self.IsAnOrphan():
            LogWarn("CheckIntegrity: 'Orphan' Attribute detected (its dogmaItem has gone!):", self)
            LogWarn('TraceReferrers is BEING SUPPRESSED in case it overloads the node! (Sorry)')
            LogTraceback('Orphan Attribute!')
            return False
        else:
            return True

    def GetBaseValue(self):
        return '<no base value reported>'

    def GetValue(self):
        return '<no value reported>'

    def AddOutgoingModifier(self, operation, toAttrib):
        raise NotImplementedError('AttributeInterface does not implement AddOutgoingModifier')

    def RemoveOutgoingModifier(self, operation, toAttrib):
        raise NotImplementedError('AttributeInterface does not implement RemoveOutgoingModifier')
