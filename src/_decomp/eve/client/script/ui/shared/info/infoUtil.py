#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\infoUtil.py
import sys
from collections import defaultdict
import dogma.const
import dogma.data
import eveformat
import evetypes
import localization
from carbon.common.script.util.mathCommon import FloatCloseEnough
from carbonui import uiconst
from dogma.attributes.format import GetFormattedAttributeAndValue
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.fittingScreen.fittingUtil import allPowerEffects
from eve.client.script.ui.shared.info.attribute import IsModified, IsMutated
from eve.client.script.ui.shared.dynamicItem.mutationBar import MutationBar
import inventorycommon.const as invConst
OVERLOAD_ATTRIBUTE = 'overLoadAttribute'
attributesWithUnknownHighIsGood = (dogma.const.attributeMass, dogma.const.attributeMassAddition, dogma.const.attributeDrawback)

def GetAttributeTooltipTitleAndDescription(attributeID):
    if attributeID:
        attributeInfo = dogma.data.get_attribute(attributeID)
        tooltipTitleID = getattr(attributeInfo, 'tooltipTitleID', None)
        if tooltipTitleID:
            tooltipDescriptionID = attributeInfo.tooltipDescriptionID
            return (localization.GetByMessageID(tooltipTitleID), localization.GetByMessageID(tooltipDescriptionID))
    return (None, None)


fittingAttributeIDs = [dogma.const.attributeCpuOutput,
 dogma.const.attributePowerOutput,
 dogma.const.attributeUpgradeCapacity,
 dogma.const.attributeHiSlots,
 dogma.const.attributeMedSlots,
 dogma.const.attributeLowSlots,
 dogma.const.attributeServiceSlots,
 dogma.const.attributeTurretSlotsLeft,
 dogma.const.attributeUpgradeSlotsLeft,
 dogma.const.attributeLauncherSlotsLeft]

def GetFittingAttributeIDs():
    return fittingAttributeIDs


def GetColoredText(attribute, text):
    return GetColoredTextWithCustomColors(attribute, text, positiveChange=eveColor.SUCCESS_GREEN, negativeChange=eveColor.DANGER_RED, unknown=eveColor.SAND_YELLOW)


def GetColoredTextWithCustomColors(attribute, text, positiveChange, negativeChange, unknown):
    if IsModified(attribute) and _IsValidValue(attribute.value) and _IsValidValue(attribute.baseValue):
        if attribute.isSame and IsMutated(attribute):
            if attribute.isMutationPositive:
                color = positiveChange
            else:
                color = negativeChange
        elif attribute.isSame:
            color = unknown
        elif attribute.isBetter and IsMutated(attribute):
            if attribute.isMutationPositive:
                color = positiveChange
            else:
                color = negativeChange
        elif attribute.attributeID in attributesWithUnknownHighIsGood:
            color = unknown
        elif attribute.isBetter:
            color = positiveChange
        else:
            color = negativeChange
    elif IsMutated(attribute):
        if attribute.isMutationPositive:
            color = positiveChange
        else:
            color = negativeChange
    else:
        return text
    return eveformat.color(text, color)


def _IsValidValue(value):
    return value is not None and not isinstance(value, basestring)


def PrepareInfoTextForAttributeHint(textLabel, attribute, itemID = None, extraModifyingAttrIDs = None, extraModifyingFactors = None):
    if not attribute:
        return
    if textLabel.state == uiconst.UI_DISABLED:
        textLabel.state = uiconst.UI_NORMAL
    textLabel.LoadTooltipPanel = LoadAttributeTooltipPanel
    textLabel.modifiedAttribute = attribute
    textLabel.itemID = itemID
    textLabel.extraModifyingAttrIDs = extraModifyingAttrIDs or []
    textLabel.extraModifyingFactors = extraModifyingFactors or []


def LoadAttributeTooltipPanel(panel, owner):
    panel.margin = (8, 8, 8, 0)
    attribute = getattr(owner, 'modifiedAttribute', None)
    itemID = getattr(owner, 'itemID', None)
    extraModifyingAttrIDs = getattr(owner, 'extraModifyingAttrIDs', None) or []
    extraModifyingFactors = getattr(owner, 'extraModifyingFactors', None) or []
    if attribute is None:
        return
    if IsMutated(attribute):
        text = localization.GetByLabel('UI/InfoWindow/AttributeIsMutated')
        panel.AddLabelMedium(text=text)
        MutationBar(parent=panel, align=uiconst.TOPLEFT, top=4, attribute=attribute, barWidth=60)
    if IsModified(attribute):
        panel.margin = (8, 8, 8, 8)
        if attribute.baseValue is None:
            text = localization.GetByLabel('UI/InfoWindow/AttributeModified')
            panel.AddLabelMedium(text=text)
        else:
            affectedByTextList = GetAffectedByTextList(attribute.attributeID, itemID)
            for mAttrID in extraModifyingAttrIDs:
                affectedByTextList += GetAffectedByTextList(mAttrID, itemID)

            affectedByTextList += GetExtraModifyingFactorsList(extraModifyingFactors)
            affectedByText = GetAffectedByText(affectedByTextList) or ''
            if affectedByText:
                text = localization.GetByLabel('UI/InfoWindow/AttributeModifiedByWithBaseValue', affectedByText=affectedByText, baseAttributeValue=attribute.displayBaseValue)
            else:
                text = localization.GetByLabel('UI/InfoWindow/AttributeModifiedWithBaseValue', baseAttributeValue=attribute.displayBaseValue)
            panel.AddLabelMedium(text=text)


def GetAffectedByText(textList):
    if textList:
        return '<br>'.join(textList)


def GetAffectedByTextList(attributeID, itemID):
    if not itemID:
        return
    infoSvc = sm.GetService('info')
    dogmaLocation = infoSvc.GetDogmaLocation(itemID)
    dogmaItem = dogmaLocation.SafeGetDogmaItem(itemID)
    if not dogmaItem:
        return
    itemAttributes = dogmaItem.attributes
    attribRoot = None
    if attributeID in itemAttributes:
        attribRoot = itemAttributes[attributeID]
    if not attribRoot:
        return
    makesHigher = defaultdict(list)
    makesLower = defaultdict(list)
    textList = []
    externalFactorsMakeHigher = False
    externalFactorsMakeLower = False
    if not infoSvc.IsItemSimulated(itemID):
        try:
            clientValue = dogmaLocation.GetAttributeValue(itemID, attributeID)
            attrName = dogma.data.get_attribute_name(attributeID)
            godmaVal = sm.GetService('godma').GetStateManager().GetAttribute(itemID, attrName)
            if not FloatCloseEnough(godmaVal, clientValue):
                externalFactorsMakeHigher = godmaVal > clientValue
                externalFactorsMakeLower = clientValue > godmaVal
        except (KeyError, RuntimeError, ZeroDivisionError):
            sys.exc_clear()

    HarvestModifiers(attribRoot, makesHigher, makesLower)
    for direction, dictToUse, externalFactorsActive in [(u'\u2191', makesHigher, externalFactorsMakeHigher), (u'\u2193', makesLower, externalFactorsMakeLower)]:
        if dictToUse:
            for what, typeList in dictToUse.iteritems():
                countDict = defaultdict(int)
                for typeID in typeList:
                    countDict[typeID] += 1

                for typeID, typeCount in countDict.iteritems():
                    if what == OVERLOAD_ATTRIBUTE:
                        cat = localization.GetByLabel('UI/InfoWindow/OverloadedModule')
                    else:
                        cat = evetypes.GetCategoryName(typeID)
                    typeText = ' %s %s: %s%s ' % (direction,
                     cat,
                     '%sx ' % typeCount if typeCount > 1 else '',
                     evetypes.GetName(typeID))
                    textList.append(typeText)

        if externalFactorsActive:
            textList.append(' %s %s' % (direction, localization.Get('UI/InfoWindow/ExternalFactors')))

    return textList


def HarvestModifiers(curAttrib, makesHigher, makesLower):
    modifiers = curAttrib.GetIncomingModifiers()
    if not modifiers:
        return
    for opIdx, attrib in modifiers:
        val = attrib.GetValue()
        dictToUse = None
        if opIdx in (dogma.const.dgmAssPreMul, dogma.const.dgmAssPostMul):
            if val > 1.0:
                dictToUse = makesHigher
            elif val < 1.0:
                dictToUse = makesLower
        elif opIdx == dogma.const.dgmAssPostPercent:
            if val > 0.0:
                dictToUse = makesHigher
            elif val < 0.0:
                dictToUse = makesLower
        elif opIdx in (dogma.const.dgmAssPreDiv, dogma.const.dgmAssPostDiv):
            if val < 1.0:
                dictToUse = makesHigher
            elif val > 1.0:
                dictToUse = makesLower
        elif opIdx == dogma.const.dgmAssModAdd:
            if val > 0.0:
                dictToUse = makesHigher
            elif val < 0.0:
                dictToUse = makesLower
        elif opIdx == dogma.const.dgmAssModSub:
            if val < 0.0:
                dictToUse = makesHigher
            elif val > 0.0:
                dictToUse = makesLower
        if dictToUse is None:
            continue
        skills = getattr(attrib, 'skills', [])
        if skills:
            dictToUse[attrib.__class__.__name__].extend(skills)
        else:
            invItem = getattr(attrib, 'invItem', None)
            if invItem:
                typeID = attrib.invItem.typeID
                if IsOverloadAttribute(attrib, typeID):
                    dictToUse[OVERLOAD_ATTRIBUTE].append(typeID)
                else:
                    dictToUse[attrib.__class__.__name__].append(typeID)
        HarvestModifiers(attrib, makesHigher, makesLower)

    return (makesHigher, makesLower)


def GetExtraModifyingFactorsList(extraModifyingFactors):
    ret = []
    for factorText, direction in extraModifyingFactors:
        text = ''
        if direction > 0:
            text = u'\u2191 '
        elif direction < 0:
            text = u'\u2193 '
        text += factorText
        ret.append(text)

    return ret


overloadingAttributesByTypeID = {}

def IsOverloadAttribute(attrib, typeID):
    if getattr(attrib, 'attribID', None):
        overloadingAttributes = overloadingAttributesByTypeID.get(typeID, None)
        if overloadingAttributes is None:
            overloadingAttributes = GetOverloadingAttributes(typeID)
            overloadingAttributesByTypeID[typeID] = overloadingAttributes
        if attrib.attribID in overloadingAttributes:
            return True
    return False


def GetOverloadingAttributes(typeID):
    overloadingAttributes = set()
    for e in dogma.data.get_type_effects(typeID):
        if dogma.data.get_effect_category(e.effectID) != dogma.const.dgmEffOverload:
            continue
        effect = dogma.data.get_effect(e.effectID)
        for m in effect.modifierInfo:
            if m.modifyingAttributeID:
                overloadingAttributes.add(m.modifyingAttributeID)

    return overloadingAttributes


hybridTexturePath = 'res:/UI/Texture/classes/ShipTree/attributes/hybridTurrets.png'
projectileTexturePath = 'res:/UI/Texture/classes/ShipTree/attributes/projectileTurrets.png'
energyTexturePath = 'res:/UI/Texture/classes/ShipTree/attributes/energyTurrets.png'
precursorTexturePath = 'res:/UI/Texture/classes/ShipTree/attributes/precursor.png'
missileTexturePath = 'res:/UI/Texture/classes/ShipTree/attributes/missiles.png'
iconPathsForGroupIDs = {invConst.groupHybridWeapon: hybridTexturePath,
 invConst.groupProjectileWeapon: projectileTexturePath,
 invConst.groupEnergyWeapon: energyTexturePath,
 invConst.groupPrecursorTurret: precursorTexturePath,
 invConst.groupHybridAmmo: hybridTexturePath,
 invConst.groupAdvancedRailgunCharge: hybridTexturePath,
 invConst.groupAdvancedBlasterCharge: hybridTexturePath,
 invConst.groupProjectileAmmo: projectileTexturePath,
 invConst.groupAdvancedArtilleryAmmo: projectileTexturePath,
 invConst.groupAdvancedAutocannonAmmo: projectileTexturePath,
 invConst.groupFrequencyCrystal: energyTexturePath,
 invConst.groupAdvancedBeamLaserCrystal: energyTexturePath,
 invConst.groupAdvancedPulseLaserCrystal: energyTexturePath,
 invConst.groupChargeBottle: precursorTexturePath,
 invConst.groupAdvancedChargeBottle: precursorTexturePath}
iconPathForChargeSizes = {1: 'res:/UI/Texture/classes/Fitting/Small.png',
 2: 'res:/UI/Texture/classes/Fitting/Medium.png',
 3: 'res:/UI/Texture/classes/Fitting/Large.png',
 4: 'res:/UI/Texture/classes/Fitting/XLarge.png'}

def GetWeaonSystemIconForTypeID(typeID):
    groupID = evetypes.GetGroupID(typeID)
    iconPath = iconPathsForGroupIDs.get(groupID, None)
    if iconPath:
        return iconPath
    typeEffects = dogma.data.get_type_effects(typeID)
    usesMissiles = any((x for x in typeEffects if x.effectID in (dogma.const.effectUseMissiles, dogma.const.effectDotMissileLaunching)))
    if usesMissiles:
        return missileTexturePath
    isMissile = any((x for x in typeEffects if x.effectID in (dogma.const.effectMissileLaunching, dogma.const.effectFofMissileLaunching)))
    if isMissile:
        return missileTexturePath


def GetIconAndLabelForChargeSize(typeID):
    chargeAttributeValue = dogma.data.get_type_attribute(typeID, dogma.const.attributeChargeSize)
    if not chargeAttributeValue:
        return (None, '')
    groupID = evetypes.GetGroupID(typeID)
    if groupID not in iconPathsForGroupIDs:
        return (None, '')
    texturePath = iconPathForChargeSizes.get(int(chargeAttributeValue), None)
    formattedInfo = GetFormattedAttributeAndValue(dogma.const.attributeChargeSize, chargeAttributeValue)
    label = '%s: %s' % (formattedInfo.displayName, formattedInfo.value)
    return (texturePath, label)


def GetEffectIconIdAndLabelID(typeID):
    for effect in dogma.data.get_type_effects(typeID):
        if effect.effectID in allPowerEffects:
            powerType = effect.effectID
            effectInfo = dogma.data.get_effect(powerType)
            break
    else:
        return (None, '')

    return (effectInfo.iconID, effectInfo.displayNameID)


usedWithAttributes = [dogma.const.attributeChargeGroup1,
 dogma.const.attributeChargeGroup2,
 dogma.const.attributeChargeGroup3,
 dogma.const.attributeChargeGroup4,
 dogma.const.attributeChargeGroup5,
 dogma.const.attributeLauncherGroup,
 dogma.const.attributeLauncherGroup2,
 dogma.const.attributeLauncherGroup3,
 dogma.const.attributeLauncherGroup4,
 dogma.const.attributeLauncherGroup5,
 dogma.const.attributeLauncherGroup6]

def GetUsedWithText(typeID):
    textList = []
    for eachAttribute in usedWithAttributes:
        usedWithGroup = dogma.data.get_type_attribute(typeID, eachAttribute, None)
        if usedWithGroup:
            textList.append('- %s' % evetypes.GetGroupNameByGroup(int(usedWithGroup)))

    if textList:
        textList.insert(0, '%s:' % localization.GetByLabel('UI/InfoWindow/TabNames/UsedWith'))
    return '<br>'.join(textList)
