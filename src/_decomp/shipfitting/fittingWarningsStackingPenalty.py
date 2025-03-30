#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipfitting\fittingWarningsStackingPenalty.py
from collections import defaultdict
import evetypes
import dogma.data as dogma_data
import dogma.const as dogmaConst
from brennivin.itertoolsext import Bundle
ITEM_MODIFIER = 1
NOT_ITEM_MOTIFIER = 2

def FindModulesWithStackingPenalty(fittedModules):
    typeIDs = {x for x, _ in fittedModules}
    nonStackableByTypeID, nonStackableByTypeIDTargeted = _FindModulesWithStackingPenalty(set(typeIDs))
    nonStackableAttributes = defaultdict(set)
    nonStackableAttributesTargeted = defaultdict(set)
    for eachTypeID, eachFlagID in fittedModules:
        nonStackable = nonStackableByTypeID.get(eachTypeID, [])
        nonStackableTarget = nonStackableByTypeIDTargeted.get(eachTypeID, [])
        if not nonStackable and not nonStackableTarget:
            continue
        for x in nonStackable:
            nonStackableAttributes[x.modifiedAttributeID, x.operation, x.skillTypeID, x.domain].add((eachTypeID, eachFlagID))

        for x in nonStackableTarget:
            nonStackableAttributesTargeted[x.modifiedAttributeID, x.operation, x.skillTypeID, x.domain].add((eachTypeID, eachFlagID))

    return (nonStackableAttributes, nonStackableAttributesTargeted)


def _FindModulesWithStackingPenalty(typeIDs):
    nonStackableByTypeID = {}
    nonStackableByTypeIDTargeted = {}
    ghostFittingEffectCompiler = sm.GetService('ghostFittingEffectCompiler')
    typesWithPythonEffect = set()
    pythonEffects = set()
    for typeID in typeIDs:
        if not IsModuleOfInterestForStacking(typeID):
            continue
        nonStackable = []
        nonStackableTargeted = []
        effectList = dogma_data.get_type_effects(typeID)
        for each in effectList:
            effect = dogma_data.get_effect(each.effectID)
            if effect.effectCategory == dogmaConst.dgmEffOverload:
                continue
            effectFromCompiler = ghostFittingEffectCompiler.effects.get(effect.effectID)
            if effectFromCompiler and effectFromCompiler.isPythonEffect:
                domainToUse = 'target' if effect.effectCategory == dogmaConst.dgmEffTarget else 'shipID'
                modifierInfo = _GetModifierInfoFromPythonEffect(effectFromCompiler, domainToUse)
                typesWithPythonEffect.add(typeID)
                pythonEffects.add(effect.effectID)
            else:
                modifierInfo = effect.modifierInfo
            for m in modifierInfo or []:
                modifiedAttributeID = m.modifiedAttributeID
                modifyingAttributeID = m.modifyingAttributeID
                if modifiedAttributeID is None:
                    continue
                modifiedAttribute = dogma_data.get_attribute(modifiedAttributeID)
                modifyingAttribute = dogma_data.get_attribute(modifyingAttributeID)
                if modifiedAttribute.stackable:
                    continue
                x = Bundle(typeID=typeID, modifiedAttributeID=modifiedAttributeID, modifyingAttributeID=modifyingAttributeID, cat=modifyingAttribute.categoryID, effectID=each.effectID, operation=m.operation, domain=(m.domain, ITEM_MODIFIER if m.func == 'ItemModifier' else NOT_ITEM_MOTIFIER), skillTypeID=m.skillTypeID)
                if effect.effectCategory == dogmaConst.dgmEffTarget:
                    nonStackableTargeted.append(x)
                else:
                    modifyingValue = dogma_data.get_type_attribute(typeID, modifyingAttributeID)
                    goodChange = IsItGoodChange(modifyingValue, m.operation, modifiedAttribute.highIsGood)
                    if goodChange:
                        nonStackable.append(x)

        if nonStackable:
            nonStackableByTypeID[typeID] = nonStackable
        if nonStackableTargeted:
            nonStackableByTypeIDTargeted[typeID] = nonStackableTargeted

    return (nonStackableByTypeID, nonStackableByTypeIDTargeted)


def IsItGoodChange(modifyingValue, operation, wantHigh):
    if modifyingValue is None:
        return False
    if operation in (dogmaConst.dgmAssModAdd, dogmaConst.dgmAssModSub):
        return False
    goodChange = False
    if wantHigh:
        if operation in (dogmaConst.dgmAssPreMul, dogmaConst.dgmAssPostMul):
            goodChange = modifyingValue > 1.0
        elif operation == dogmaConst.dgmAssPostPercent:
            goodChange = modifyingValue > 0
        elif operation in (dogmaConst.dgmAssPreDiv, dogmaConst.dgmAssPostDiv):
            goodChange = modifyingValue < 1.0
    elif operation in (dogmaConst.dgmAssPreMul, dogmaConst.dgmAssPostMul):
        goodChange = modifyingValue < 1.0 and modifyingValue != 0
    elif operation == dogmaConst.dgmAssPostPercent:
        goodChange = modifyingValue < 0
    elif operation in (dogmaConst.dgmAssPreDiv, dogmaConst.dgmAssPostDiv):
        goodChange = modifyingValue > 1.0
    return goodChange


def _GetModifierInfoFromPythonEffect(effectFromCompiler, domainToUse):
    modifierInfo = []
    for operation, toAttribID, fromAttribID in effectFromCompiler.MODIFIER_CHANGES:
        x = Bundle(operation=operation, modifiedAttributeID=toAttribID, modifyingAttributeID=fromAttribID, domain=(domainToUse, ITEM_MODIFIER), skillTypeID=None, func='ItemModifier')
        modifierInfo.append(x)

    for operation, skillTypeID, toAttribID, fromAttribID in effectFromCompiler.SKILL_MODIFIER_CHANGES_FOR_LOCATION:
        x = Bundle(operation=operation, modifiedAttributeID=toAttribID, modifyingAttributeID=fromAttribID, domain=(domainToUse, NOT_ITEM_MOTIFIER), skillTypeID=skillTypeID, func='LocationRequiredSkillModifier')
        modifierInfo.append(x)

    return modifierInfo


def IsModuleOfInterestForStacking(typeID):
    if not evetypes.IsPublished(typeID):
        return False
    if evetypes.GetCategoryID(typeID) not in (const.categoryModule, const.categoryStructureModule):
        return False
    return True


def Test():
    typeIDs = [ x for x in evetypes.Iterate() if IsModuleOfInterestForStacking(x) ]
    x, y = _FindModulesWithStackingPenalty(typeIDs)
    return (x, y)


def FindModulesWithStackingPenaltyTest():
    allTypeIDs = {x for x in evetypes.Iterate()}
    typesPenalized = _FindModulesWithStackingPenalty(allTypeIDs)
    missingText = {}
    textButNotInList = set()
    correct = set()
    for eachTypeID in evetypes.Iterate():
        if not evetypes.IsPublished(eachTypeID):
            continue
        if evetypes.GetCategoryID(eachTypeID) not in (const.categoryModule, const.categoryStructureModule):
            continue
        desc = evetypes.GetDescription(eachTypeID).lower()
        isPenaltyText = desc.find('penalty') >= 0 and desc.find('same attribute') >= 0
        containsWarning = isPenaltyText or desc.find('diminishing returns') >= 0
        if containsWarning:
            if eachTypeID not in typesPenalized:
                textButNotInList.add(eachTypeID)
                continue
        elif eachTypeID in typesPenalized:
            missingText[eachTypeID] = typesPenalized[eachTypeID]
            continue
        correct.add(eachTypeID)

    print '-------------- correct ------------------- = ', len(correct)
    print '-------------- Missing text ------------------- = ', len(missingText)
    print '-------------- Missing stacking ------------------- = ', len(textButNotInList)
    PrintList(textButNotInList)


def PrintList(typeIDs):
    grouped = []
    for eachTypeID in typeIDs:
        sortValue = (evetypes.GetGroupID(eachTypeID), evetypes.GetName(eachTypeID))
        grouped.append((sortValue, eachTypeID))

    import localization
    grouped = [ y[1] for y in sorted(grouped) ]
    for eachTypeID in grouped:
        print '- ', evetypes.GetName(eachTypeID), eachTypeID
