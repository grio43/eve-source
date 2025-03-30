#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingUtil.py
import dogma.const
import dogma.data
import eveformat
import evetypes
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.fittingScreen.ghostFittingUtil import GetOriganlItemIDFromItemKey
from inventorycommon.const import categoryCharge, flagAutoFit, groupFrequencyCrystal
from shipfitting.fittingStuff import GetSlotListForTypeID
from utillib import KeyVal
PASSIVESHIELDRECHARGE = 0
SHIELDBOOSTRATEACTIVE = 1
ARMORREPAIRRATEACTIVE = 2
HULLREPAIRRATEACTIVE = 3

def GetColoredText(isBetter, text):
    if isBetter is None:
        return text
    if isBetter:
        color = eveColor.SUCCESS_GREEN
    else:
        color = eveColor.DANGER_RED
    return eveformat.color(text, color)


def IsEffectActivatable(isDefault, effectInfo):
    return isDefault and effectInfo.effectCategory in (dogma.const.dgmEffActivation, dogma.const.dgmEffTarget) and effectInfo.effectName != 'online'


def GetDefaultAndOverheatEffectForType(typeID):
    possibleEffects = dogma.data.get_type_effects(typeID)
    typeEffectInfo = KeyVal(defaultEffect=None, overloadEffect=None, isActivatable=False)
    for typeEffect in possibleEffects:
        effect = dogma.data.get_effect(typeEffect.effectID)
        if typeEffect.isDefault:
            typeEffectInfo.isActivatable = IsEffectActivatable(typeEffect.isDefault, effect)
            typeEffectInfo.defaultEffect = effect
        if effect.effectCategory == dogma.const.dgmEffOverload:
            typeEffectInfo.overloadEffect = effect

    return typeEffectInfo


def IsCharge(typeID):
    return evetypes.GetCategoryID(typeID) in (categoryCharge, groupFrequencyCrystal)


allPowerEffects = (dogma.const.effectHiPower,
 dogma.const.effectMedPower,
 dogma.const.effectLoPower,
 dogma.const.effectSubSystem,
 dogma.const.effectRigSlot,
 dogma.const.effectServiceSlot)

def GetFlagIdToUse(dogmaStaticMgr, typeID, flag, flagsInUse):
    flagsForType = GetSlotListForTypeID(dogmaStaticMgr, typeID)
    if flag not in flagsForType:
        return None
    if flag != flagAutoFit:
        return flag
    return GetNextAvailableFlag(dogmaStaticMgr, typeID, flagsInUse)


def GetNextAvailableFlag(dogmaStaticMgr, typeID, flagsInUse):
    flagsForType = GetSlotListForTypeID(dogmaStaticMgr, typeID)
    for x in flagsForType:
        if x not in flagsInUse:
            return x


def GetOriginalItemID(itemID):
    if isinstance(itemID, basestring):
        return GetOriganlItemIDFromItemKey(itemID)
    return itemID
