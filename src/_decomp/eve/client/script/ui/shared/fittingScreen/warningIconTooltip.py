#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\warningIconTooltip.py
from collections import defaultdict
import evetypes
import inventorycommon
from carbonui.primitives.container import Container
from carbonui import const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from dogma.attributes.format import GetFormattedAttributeAndValue
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveHeaderLarge, EveLabelMediumBold
import shipfitting.fittingWarnings as fittingWarnings
import shipfitting.fittingWarningConst as fittingWarningConst
from eve.client.script.ui.shared.info.infoConst import TAB_TRAITS
from eve.client.script.ui.shared.neocom.skillConst import COLOR_SKILL_2
from fsdBuiltData.common.iconIDs import GetIconFile
from localization import GetByLabel
import dogma.data as dogma_data
ICON_SIZE = 20

def AddSlotsToWarningDict(warningSlotDict, warningID, updateSet):
    warningLevel = fittingWarnings.GetWarningLevelFromWarningID(warningID)
    warningSlotDict[warningLevel].update(updateSet)


def EvaluateFitAndPopulateTooltip(tooltipPanel, fittingController, warningLevel, fullVersion = False):
    tooltipPanel.warningLevel = 0
    tooltipPanel.Flush()
    headerLabel = False
    warningSlotDict = defaultdict(set)
    fitResults = fittingWarnings.EvaluateFit(fittingController)
    if fitResults is None:
        return
    fitResults = fittingWarnings.FilterResultsForWarningLevel(fitResults, [warningLevel])
    activeWarnings = fittingWarnings.GetActiveWarningsByLevelFromResults(fitResults)
    if activeWarnings:
        color = fittingWarnings.GetColorForLevel(warningLevel)
        headerLabelPath = fittingWarnings.GetHeaderForLevel(warningLevel)
        if headerLabelPath:
            headerText = GetByLabel(headerLabelPath)
            headerLabel = EveHeaderLarge(text=headerText)
            headerLabel.SetRGBA(*color)
            tooltipPanel.AddCell(headerLabel, colSpan=tooltipPanel.columns, cellPadding=(6, 4, 0, 4))
    currentWarningID = fittingWarningConst.WARNING_MISSING_SUBSYSTEMS
    missingSubsystems = fitResults.get(currentWarningID, None)
    if missingSubsystems:
        AddWarningAndAddToSlotDict(tooltipPanel, currentWarningID, fullVersion, set(missingSubsystems), warningSlotDict)
        if fullVersion:
            AddSubsystemSlotsToTooltip(tooltipPanel, missingSubsystems)
    currentWarningID = fittingWarningConst.WARNING_MODULES_IN_INVALID_FLAGS
    modulesInInvalidSlots = fitResults.get(currentWarningID, None)
    if modulesInInvalidSlots:
        PrepareFlagsAndAddWarning(tooltipPanel, currentWarningID, fullVersion, warningSlotDict, modulesInInvalidSlots)
    currentWarningID = fittingWarningConst.WARNING_OVER_CPU
    if fitResults.get(currentWarningID, None):
        AddWarningAndAddToSlotDict(tooltipPanel, currentWarningID, fullVersion, {-currentWarningID}, warningSlotDict)
    currentWarningID = fittingWarningConst.WARNING_OVER_POWERGRID
    if fitResults.get(currentWarningID, None):
        semiflagIDs = {-currentWarningID}
        AddWarningAndAddToSlotDict(tooltipPanel, currentWarningID, fullVersion, semiflagIDs, warningSlotDict)
    currentWarningID = fittingWarningConst.WARNING_OVER_CALIBRATION
    if fitResults.get(currentWarningID, None):
        semiflagIDs = set(const.rigSlotFlags)
        AddWarningAndAddToSlotDict(tooltipPanel, currentWarningID, fullVersion, semiflagIDs, warningSlotDict)
    currentWarningID = fittingWarningConst.WARNING_OVERLOADED_CARGO
    if fitResults.get(currentWarningID, None):
        flagIDs = [const.flagCargo]
        AddWarningAndAddToSlotDict(tooltipPanel, currentWarningID, fullVersion, flagIDs, warningSlotDict)
    for currentWarningID in [fittingWarningConst.WARNING_DUAL_TANKED, fittingWarningConst.WARNING_MULTI_TANKED]:
        tankingModules = fitResults.get(currentWarningID, None)
        if tankingModules:
            flagIDs = {x[1] for x in tankingModules}
            AddSlotsToWarningDict(warningSlotDict, currentWarningID, flagIDs)
            AddWarning(tooltipPanel, currentWarningID, fullVersion, flagIDs)

    for currentWarningID in [fittingWarningConst.WARNING_ARMOR_TANKED_SHIELD_SHIP, fittingWarningConst.WARNING_SHIELD_TANKED_ARMOR_SHIP]:
        wrongModules = fitResults.get(currentWarningID, None)
        if wrongModules:
            PrepareFlagsAndAddWarning(tooltipPanel, currentWarningID, fullVersion, warningSlotDict, wrongModules)

    currentWarningID = fittingWarningConst.WARNING_NOT_PROVIDING_BONUS
    notProvidingBonus = fitResults.get(currentWarningID, None)
    if notProvidingBonus:
        PrepareFlagsAndAddWarning(tooltipPanel, currentWarningID, fullVersion, warningSlotDict, notProvidingBonus)
        if fullVersion:
            AddModuleRows(tooltipPanel, notProvidingBonus, currentWarningID)
    currentWarningID = fittingWarningConst.WARNING_MIXING_TURRET_GROUPS
    mixedTurrets = fitResults.get(currentWarningID, None)
    if mixedTurrets:
        flagIDs = set()
        for each in mixedTurrets.itervalues():
            flagIDs.update({x[1] for x in each})

        AddWarningAndAddToSlotDict(tooltipPanel, currentWarningID, fullVersion, flagIDs, warningSlotDict)
        if fullVersion:
            AddTurretOrLauncherGroups(tooltipPanel, mixedTurrets, currentWarningID)
    currentWarningID = fittingWarningConst.WARNING_MIXING_LAUNCHER_GROUPS
    mixedLaunchers = fitResults.get(currentWarningID, None)
    if mixedLaunchers:
        flagIDs = set()
        for each in mixedLaunchers.itervalues():
            flagIDs.update({x[1] for x in each})

        AddWarningAndAddToSlotDict(tooltipPanel, currentWarningID, fullVersion, flagIDs, warningSlotDict)
        if fullVersion:
            AddTurretOrLauncherGroups(tooltipPanel, mixedLaunchers, currentWarningID)
    currentWarningID = fittingWarningConst.WARNING_MIXING_TURRET_SIZES
    mixedTurretSizes = fitResults.get(currentWarningID, None)
    if mixedTurretSizes:
        flagIDs = set()
        for each in mixedTurretSizes.itervalues():
            flagIDs.update({x[1] for x in each})

        AddWarningAndAddToSlotDict(tooltipPanel, currentWarningID, fullVersion, flagIDs, warningSlotDict)
        if fullVersion:
            AddTurretSizes(tooltipPanel, mixedTurretSizes, currentWarningID)
    currentWarningID = fittingWarningConst.WARNING_OFFLINE_MODULES
    offlineModules = fitResults.get(currentWarningID, None)
    if offlineModules:
        PrepareFlagsAndAddWarning(tooltipPanel, currentWarningID, fullVersion, warningSlotDict, offlineModules)
        if fullVersion:
            AddModuleRows(tooltipPanel, offlineModules, currentWarningID)
    currentWarningID = fittingWarningConst.WARNING_POLARIZED_WEAPONS
    polarizedWeapons = fitResults.get(currentWarningID, None)
    if polarizedWeapons:
        PrepareFlagsAndAddWarning(tooltipPanel, currentWarningID, fullVersion, warningSlotDict, polarizedWeapons)
    for currentWarningID in [fittingWarningConst.WARNING_MISSING_REQ_CHARGES, fittingWarningConst.WARNING_MISSING_OPTIONAL_CHARGES]:
        missingCharges = fitResults.get(currentWarningID, None)
        if missingCharges:
            PrepareFlagsAndAddWarning(tooltipPanel, currentWarningID, fullVersion, warningSlotDict, missingCharges)

    currentWarningID = fittingWarningConst.WARNING_UNDERSIZED_PROP_MOD
    undersizedPropMods = fitResults.get(currentWarningID, None)
    if undersizedPropMods:
        PrepareFlagsAndAddWarning(tooltipPanel, currentWarningID, fullVersion, warningSlotDict, undersizedPropMods)
    currentWarningID = fittingWarningConst.WARNING_INEFFICIENT_PROP_MOD
    inefficientPropMods = fitResults.get(currentWarningID, None)
    if inefficientPropMods:
        PrepareFlagsAndAddWarning(tooltipPanel, currentWarningID, fullVersion, warningSlotDict, inefficientPropMods)
    for currentWarningID in [fittingWarningConst.WARNING_STACKING_PENALTY_MED, fittingWarningConst.WARNING_STACKING_PENALTY_LOW, fittingWarningConst.WARNING_STACKING_PENALTY_TARGETED_LOW]:
        stackingPenalty = fitResults.get(currentWarningID, None)
        if stackingPenalty:
            flagIDs = set()
            for each in stackingPenalty.itervalues():
                flagIDs.update({x[1] for x in each})

            AddSlotsToWarningDict(warningSlotDict, currentWarningID, flagIDs)
            AddWarning(tooltipPanel, currentWarningID, fullVersion, flagIDs)
            if fullVersion:
                AddAttributes(tooltipPanel, stackingPenalty, currentWarningID)

    currentWarningID = fittingWarningConst.WARNING_DISABLED_BUBBLE_IMMUNITY
    modulesDisablingBubbleImmunity = fitResults.get(currentWarningID, None)
    if modulesDisablingBubbleImmunity:
        PrepareFlagsAndAddWarning(tooltipPanel, currentWarningID, fullVersion, warningSlotDict, modulesDisablingBubbleImmunity)
    slotsLevelLow = warningSlotDict[fittingWarningConst.WARNING_LEVEL_LOW]
    slotsLevelMedium = warningSlotDict[fittingWarningConst.WARNING_LEVEL_MEDIUM]
    slotsLevelHigh = warningSlotDict[fittingWarningConst.WARNING_LEVEL_HIGH]
    slotsLevelLow = slotsLevelLow - slotsLevelMedium - slotsLevelHigh
    slotsLevelMedium = slotsLevelMedium - slotsLevelHigh
    warningSlotDict = {x:fittingWarningConst.WARNING_LEVEL_HIGH for x in slotsLevelHigh}
    warningSlotDict.update({x:fittingWarningConst.WARNING_LEVEL_MEDIUM for x in slotsLevelMedium})
    warningSlotDict.update({x:fittingWarningConst.WARNING_LEVEL_LOW for x in slotsLevelLow})
    fittingController.ChangeFittingWarningDisplay(warningSlotDict)
    if headerLabel and headerLabel.parent:
        cell = headerLabel.parent
        cell.state = uiconst.UI_NORMAL
        cell.OnMouseEnter = (OnMouseEnterContainer, warningSlotDict)
        cell.OnMouseExit = OnMouseExitContainer


def PrepareFlagsAndAddWarning(tooltipPanel, currentWarningID, fullVersion, flagIDsDict, notProvidingBonus):
    flagIDs = {x[1] for x in notProvidingBonus}
    AddWarningAndAddToSlotDict(tooltipPanel, currentWarningID, fullVersion, flagIDs, flagIDsDict)


def AddWarningAndAddToSlotDict(tooltipPanel, currentWarningID, fullVersion, flagIDs, warningSlotDict):
    AddWarning(tooltipPanel, currentWarningID, fullVersion, flagIDs)
    AddSlotsToWarningDict(warningSlotDict, currentWarningID, flagIDs)


def AddWarning(tooltipPanel, warningID, fullVersion = False, flagIDs = ()):
    warningLevel, textPath, _ = fittingWarningConst.warningsByWarningID[warningID]
    color = fittingWarnings.GetColorForLevel(warningLevel)
    hint = GetQuestionMarkHint(warningID)
    faintColor = color[:3] + (0.25,)
    row = tooltipPanel.AddRow()
    row.OnMouseEnter = (OnMouseEnterContainer, {flagID:warningLevel for flagID in flagIDs})
    row.OnMouseExit = OnMouseExitContainer
    row.state = uiconst.UI_NORMAL
    row.hint = hint
    tooltipPanel.warningLevel = max(tooltipPanel.warningLevel, warningLevel)
    tooltipPanel.FillRow()
    iconObj = Sprite(pos=(0,
     0,
     ICON_SIZE,
     ICON_SIZE), align=uiconst.CENTERLEFT)
    row.AddCell(iconObj, cellPadding=(0, 0, 10, 0))
    iconObj.LoadIcon(fittingWarningConst.WARNING_PATH, ignoreSize=True)
    iconObj.SetRGBA(*color)
    labelColSpan = tooltipPanel.columns - 1 - bool(fullVersion)
    label = EveLabelMediumBold(text=GetByLabel(textPath), align=uiconst.CENTERLEFT, bold=True, width=350, autoFitToText=True)
    cell = row.AddCell(label, cellPadding=(6, 4, 0, 4), colSpan=labelColSpan)
    if fullVersion:
        questionmarkLabel = EveLabelMedium(name='questionMark', text='?', align=uiconst.CENTERRIGHT, bold=True)
        cell = row.AddCell(questionmarkLabel, cellPadding=(6, 0, 6, 0), colSpan=labelColSpan)
        questionmarkLabel.SetRGBA(*color)


def GetQuestionMarkHint(warningID):
    _, _, hintPath = fittingWarningConst.warningsByWarningID[warningID]
    if warningID in (fittingWarningConst.WARNING_ARMOR_TANKED_SHIELD_SHIP, fittingWarningConst.WARNING_SHIELD_TANKED_ARMOR_SHIP, fittingWarningConst.WARNING_WRONG_TANKING):
        fittingController = sm.GetService('ghostFittingSvc').GetGhostFittingController()
        hint = GetByLabel(hintPath, shipTypeID=fittingController.GetTypeID())
    elif warningID in (fittingWarningConst.WARNING_OVER_CPU_POWER, fittingWarningConst.WARNING_OVER_CPU, fittingWarningConst.WARNING_OVER_POWERGRID):
        hint = GetByLabel(hintPath, cpuMgmtLink=__GetSkillText(const.typeElectronics), weaponUpgradesLink=__GetSkillText(const.typeWeaponUpgrades), advancedWeaponUpgradesLink=__GetSkillText(const.typeAdvancedWeaponUpgrades), powerGridMgmtLink=__GetSkillText(const.typeEngineering))
    else:
        hint = GetByLabel(hintPath) if hintPath else None
    return hint


def __GetSkillText(skillTypeID):
    skillName = evetypes.GetName(skillTypeID)
    color = Color.RGBtoHex(*COLOR_SKILL_2)
    return '<font color=%s><b>%s</b></font>' % (color, skillName)


def AddModuleRows(tooltipPanel, modules, warningID):
    warningLevel = fittingWarnings.GetWarningLevelFromWarningID(warningID)
    sortedModules = sorted(modules, key=lambda x: const.moduleSlotFlags.index(x[1]))
    for eachTypeID, eachFlagID in sortedModules:
        texturePath = inventorycommon.typeHelpers.GetIconFile(eachTypeID)
        cell = _AddRowForGroupingAndItsWeapons(tooltipPanel, evetypes.GetName(eachTypeID), texturePath, [(eachTypeID, eachFlagID)], warningLevel)
        cell.GetMenu = lambda *args: sm.GetService('menu').GetMenuFromItemIDTypeID(itemID=None, typeID=eachTypeID)


def AddTurretOrLauncherGroups(tooltipPanel, mixedTurrets, warningID):
    weaponGroupsAndNames = [ (groupID, evetypes.GetGroupNameByGroup(groupID)) for groupID, weapons in mixedTurrets.iteritems() if weapons ]
    weaponGroupsAndNames.sort(key=lambda x: x[1])
    warningLevel = fittingWarnings.GetWarningLevelFromWarningID(warningID)
    for eachGroup, eachGroupName in weaponGroupsAndNames:
        weapons = mixedTurrets[eachGroup]
        texturePath = fittingWarnings.GetIconPathForTurretGroup(eachGroup)
        _AddRowForGroupingAndItsWeapons(tooltipPanel, eachGroupName, texturePath, weapons, warningLevel)


def AddTurretSizes(tooltipPanel, turretSizes, warningID):
    sizeAttributeInUse = turretSizes.keys()
    sizeAttributeInUse.sort()
    warningLevel = fittingWarnings.GetWarningLevelFromWarningID(warningID)
    for eachSize in sizeAttributeInUse:
        turrets = turretSizes[eachSize]
        groupingName = GetValueName(const.attributeChargeSize, eachSize)
        texturePath = fittingWarnings.GetIconPathForSizes(eachSize)
        _AddRowForGroupingAndItsWeapons(tooltipPanel, groupingName, texturePath, turrets, warningLevel)


def AddAttributes(tooltipPanel, attributeInfo, warningID):
    attributesByModules = defaultdict(list)
    for k, v in attributeInfo.iteritems():
        attributesByModules[tuple(v)].append(k)

    for v in attributesByModules.itervalues():
        v.sort(key=lambda x: dogma_data.get_attribute_display_name(x[0]))

    sortedAttributes = [ (dogma_data.get_attribute_display_name(x[0]), x[0], y) for x, y in attributeInfo.iteritems() ]
    sortedAttributes.sort()
    warningLevel = fittingWarnings.GetWarningLevelFromWarningID(warningID)
    attributeAdded = defaultdict(list)
    for moduleInfoList, attrList in attributesByModules.iteritems():
        sortedModuleList = sorted(moduleInfoList)
        for attributeID, op, skillTypeID, domain in attrList:
            attrText = dogma_data.get_attribute_display_name(attributeID)
            if skillTypeID:
                attrText = '%s<br>%s' % (attrText, GetByLabel('UI/Fitting/FittingWindow/Warnings/ForEquipmentRequiringSkill', skillName=evetypes.GetName(skillTypeID)))
            modulesAlreadyAddedForAttrName = attributeAdded.get(attrText.lower(), [])
            if sortedModuleList in modulesAlreadyAddedForAttrName:
                continue
            attributeAdded[attrText.lower()].append(sortedModuleList)
            iconID = dogma_data.get_attribute_icon_id(attributeID)
            iconFile = GetIconFile(iconID)
            _AddRowForGroupingAndItsWeapons(tooltipPanel, attrText, iconFile, moduleInfoList, warningLevel)


def _AddRowForGroupingAndItsWeapons(tooltipPanel, groupingName, texturePath, itemTypes, warningLevel, addExtraTypeText = False):
    typeIDs = {typeID for typeID, flagID in itemTypes}
    flagIDs = {flagID for typeID, flagID in itemTypes}
    if addExtraTypeText:
        typeNames = [ evetypes.GetName(typeID) for typeID in typeIDs ]
        typeNames.sort()
        typeText = ', '.join(typeNames[:2])
        if len(typeNames) > 2:
            typeText += '...'
        text = '%s (%s)' % (groupingName, typeText)
    else:
        text = groupingName
    tooltipPanel.FillRow()
    tooltipPanel.AddCell()
    c = Container(height=ICON_SIZE, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
    c.flagIDs = flagIDs
    c.OnMouseEnter = (OnMouseEnterContainer, {flagID:warningLevel for _, flagID in itemTypes})
    c.OnMouseExit = OnMouseExitContainer
    iconObj = Sprite(parent=c, pos=(0,
     0,
     ICON_SIZE,
     ICON_SIZE), align=uiconst.CENTERLEFT, texturePath=texturePath)
    l = EveLabelMedium(parent=c, align=uiconst.CENTERLEFT, left=ICON_SIZE + 2, text=text)
    c.width = l.left + l.textwidth
    c.height = max(c.height, l.height + 4)
    tooltipPanel.AddCell(cellObject=c, colSpan=tooltipPanel.columns - 1)
    return c


def OnMouseEnterContainer(warningSlotDict):
    if warningSlotDict:
        fittingController = sm.GetService('ghostFittingSvc').GetGhostFittingController()
        fittingController.ChangeFittingWarningDisplay(warningSlotDict)


def OnMouseExitContainer(*args):
    fittingController = sm.GetService('ghostFittingSvc').GetGhostFittingController()
    fittingController.ChangeFittingWarningDisplay({})


def AddSubsystemSlotsToTooltip(tooltipPanel, missingSubsystems):
    for eachFlagID in missingSubsystems:
        groupID, iconPath = fittingWarningConst.SUBSYSTEM_INFO_BY_SLOT[eachFlagID]
        groupName = evetypes.GetGroupNameByGroup(groupID)
        tooltipPanel.FillRow()
        tooltipPanel.AddCell()
        c = ContainerAutoSize(height=ICON_SIZE)
        iconObj = Sprite(parent=c, pos=(0,
         0,
         ICON_SIZE,
         ICON_SIZE), align=uiconst.CENTERLEFT, texturePath=iconPath)
        EveLabelMedium(parent=c, align=uiconst.CENTERLEFT, left=30, text=groupName)
        tooltipPanel.AddCell(cellObject=c, colSpan=tooltipPanel.columns - 1)


def GetValueName(attributeID, value):
    formatInfo = GetFormattedAttributeAndValue(attributeID, value)
    return formatInfo.value
