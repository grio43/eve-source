#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\effects\util.py
from dogma import const as dogmaconst
from dogma.effects.modifiereffect import ModifierEffect
import modifiers
import sideeffect
import telemetry
from eveexceptions import UserError

@telemetry.ZONE_METHOD
def CreateEffect(effectInfo):
    mods = []
    side_effects = []
    for effectDict in effectInfo.modifierInfo:
        funcType = effectDict.func
        modifierClass = modifiers.GetModifierClassByTypeString(funcType)
        sideeffectClass = sideeffect.GetSideEffectClassByTypeString(funcType)
        if modifierClass is not None:
            mods.append(modifierClass(effectDict))
        elif sideeffectClass is not None:
            side_effects.append(sideeffectClass(effectDict))
        else:
            raise RuntimeError("Can't create effect from modifierInfo. Unknown funcType type '%s'." % funcType)

    return ModifierEffect(effectInfo, mods, side_effects)


def GetEffectDuration(dogmaLM, itemID, env):
    effect = dogmaLM.broker.effects[env.effectID]
    duration_attribute_id = effect.durationAttributeID
    duration = dogmaLM.GetAttributeValue(itemID, duration_attribute_id)
    return duration


def PreCheckRange(dogmaLM, env, errorName, itemID, shipID, targetID):
    from dogma.effects.restricted.util import get_effect_max_effective_range_with_falloff
    maxEffectRange = get_effect_max_effective_range_with_falloff(dogmaLM, env.effectID, itemID)
    distance = dogmaLM.ballpark.DistanceBetween(shipID, targetID)
    if distance > maxEffectRange:
        raise UserError(errorName, {'target': targetID,
         'item': env.itemTypeID,
         'distance': int(maxEffectRange)})


def PreCheckType(dogmaLM, env, errorName, validTargetCategoryIDs, targetID):
    if dogmaLM.inventory2.GetItem(targetID).categoryID not in validTargetCategoryIDs:
        raise UserError(errorName, {'target': targetID,
         'item': env.itemTypeID})


def PreCheckIfImmune(dogmaLM, targetID):
    if dogmaLM.GetAttributeValue(targetID, dogmaconst.attributeDisallowOffensiveModifiers):
        raise UserError('DeniedActivateTargetModuleDisallowed')


def PreCheckResist(dogmaLM, env, errorName, itemID, resistAttribute, targetID):
    targetResistAttribute = dogmaLM.GetAttributeValue(itemID, resistAttribute)
    if targetResistAttribute:
        if dogmaLM.GetAttributeValue(targetID, int(targetResistAttribute)) < 0.01:
            raise UserError(errorName, {'target': targetID,
             'item': env.itemTypeID})


def SetInterimAttribute(dogmaLM, itemID, sourceAttribute, targetAttribute, modifier, floorAttribute = None):
    newValue = dogmaLM.GetAttributeValue(itemID, sourceAttribute) * modifier
    if floorAttribute:
        floorValue = dogmaLM.GetAttributeValue(itemID, floorAttribute)
        if newValue < floorValue:
            dogmaLM.SetAttributeValue(itemID, targetAttribute, floorValue)
            return
    dogmaLM.SetAttributeValue(itemID, targetAttribute, newValue)


def CalcResistanceModifier(dogmaLM, sourceItemID, sourceResistanceID, targetItemID):
    targetResistanceID = dogmaLM.GetAttributeValue(sourceItemID, sourceResistanceID)
    if targetResistanceID:
        return dogmaLM.GetAttributeValue(targetItemID, targetResistanceID)
    else:
        return 1


def CalcCloudFactorModifier(dogmaLM, itemID, cloudSizeAttributeID, targetID):
    cloudSize = dogmaLM.GetAttributeValue(itemID, cloudSizeAttributeID)
    if cloudSize > 1:
        return dogmaLM.GetCloudFactor(targetID, cloudSize)
    else:
        return 1
