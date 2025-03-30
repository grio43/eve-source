#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\moduleRestrictions.py
import dogma.const as dogmaConst
from eveuniverse.security import securityClassLowSec, securityClassHighSec
from eveexceptions import UserError

def CheckAllowedInCurrentSecurityClass(dogmaLM, itemID):
    if dogmaLM.securityClass == securityClassLowSec:
        _CheckDisallowedInEmpire(dogmaLM, itemID, dogmaConst.attributeAllowInFullyCorruptedLowSec)
    elif dogmaLM.securityClass == securityClassHighSec:
        _CheckDisallowedInEmpire(dogmaLM, itemID, dogmaConst.attributeAllowInFullyCorruptedHighSec)
        _CheckDisallowedInHighSec(dogmaLM, itemID)


def _CheckDisallowedInEmpire(dogmaLM, itemID, allowedExceptionAttribute):
    disallowedInEmpire = dogmaLM.GetAttributeValue(itemID, dogmaConst.attributeDisallowInEmpireSpace)
    if not disallowedInEmpire:
        return
    if dogmaLM.IsFullyCorrupted():
        allowInFullyCorruptSystem = dogmaLM.GetAttributeValue(itemID, allowedExceptionAttribute)
        if allowInFullyCorruptSystem:
            return
    raise UserError('CantInEmpireSpace')


def _CheckDisallowedInHighSec(dogmaLM, itemID):
    disallowedInHighSec = dogmaLM.GetAttributeValue(itemID, dogmaConst.attributeDisallowInHighSec)
    if not disallowedInHighSec:
        return
    if dogmaLM.IsFullyCorrupted():
        allowInFullyCorruptHighSecSystem = dogmaLM.GetAttributeValue(itemID, dogmaConst.attributeAllowInFullyCorruptedHighSec)
        if allowInFullyCorruptHighSecSystem:
            return
    raise UserError('CantInHighSecSpace')
