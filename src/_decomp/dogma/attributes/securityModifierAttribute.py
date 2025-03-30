#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\securityModifierAttribute.py
from dogma.attributes import Attribute
from dogma.const import attributeHiSecModifier, attributeLowSecModifier, attributeNullSecModifier
from eveuniverse.security import securityClassHighSec, securityClassLowSec, securityClassZeroSec
from dogma.dogmaLogging import LogTraceback

class SecurityModifierAttribute(Attribute):

    def __init__(self, attribID, dogmaItem, dogmaLM, staticAttr):
        securityLevel = dogmaLM.GetSecurityClass()
        attributeID = None
        if securityLevel == securityClassHighSec:
            attributeID = attributeHiSecModifier
        elif securityLevel == securityClassLowSec:
            attributeID = attributeLowSecModifier
        elif securityLevel == securityClassZeroSec:
            attributeID = attributeNullSecModifier
        if attributeID is not None:
            baseValue = dogmaItem.GetValue(attributeID)
        else:
            baseValue = -1
            LogTraceback('Got a weird security class from dogmaLocation')
        super(SecurityModifierAttribute, self).__init__(attribID, baseValue, dogmaItem, dogmaLM, staticAttr)

    def SetBaseValue(self, newBaseValue):
        pass
