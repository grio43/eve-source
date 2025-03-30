#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipModuleButton\moduleButtonTooltip.py
import appConst
import carbonui.const as uiconst
import dogma.data as dogma_data
import gametime
from carbonui.primitives.container import Container
from carbon.common.script.util.timerstuff import AutoTimer
from dogma import units
from dogma.const import attributeSpeedBoostFactor, attributeMassAddition, attributeSpeedFactor, attributeMaxVelocity
from dogma.const import attributeMass
from eve.client.script.ui.control.tooltips import TooltipPanel, ShortcutHint
from eve.client.script.ui.crimewatch.crimewatchConst import Colors as CrimeWatchColors
import math
from carbon.common.script.util.format import FmtDist
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.inflight import shipHud
from eve.client.script.ui.inflight.shipModuleButton.attributeValueRowContainer import AttributeValueRowContainer
from eve.client.script.ui.shared.fittingScreen import ACTIVE, OVERHEATED
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.client.script.ui.util.uix import GetTechLevelIcon
from eve.common.lib import appConst as const
from eve.common.script.sys.eveCfg import GetActiveShip
import evetypes
from inventorycommon.const import groupPropulsionModule
from localization.formatters import FormatTimeIntervalShort
from shipfitting.fittingDogmaLocationUtil import GetTurretDps, GetLauncherDps, GetMissleDamageMultiplier, GetDotDps
import localization
from carbonui.uicore import uicore
import blue
from utillib import KeyVal
RESISTANCE_BONUS_ATTRIBUTES = [const.attributeEmDamageResistanceBonus,
 const.attributeExplosiveDamageResistanceBonus,
 const.attributeKineticDamageResistanceBonus,
 const.attributeThermalDamageResistanceBonus]

class TooltipModuleWrapper(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = ModuleButtonTooltip(parent=parent, owner=owner, idx=idx)
        return self.tooltipPanel


class ModuleButtonTooltip(TooltipPanel):
    infoFunctionNamesForCategories = {}
    infoFunctionNames = {const.groupCompressors: 'AddCompressorInfo',
     const.groupMiningLaser: 'AddMiningLaserInfo',
     const.groupStripMiner: 'AddMiningLaserInfo',
     const.groupFrequencyMiningLaser: 'AddMiningLaserInfo',
     const.groupGasCloudHarvester: 'AddMiningLaserInfo',
     const.groupGasCloudHoarder: 'AddMiningLaserInfo',
     const.groupEnergyVampire: 'AddEnergyVampireInfo',
     const.groupEnergyDestabilizer: 'AddEnergyDestabilizerInfo',
     const.groupArmorRepairUnit: 'AddArmorRepairersInfo',
     const.groupFueledArmorRepairer: 'AddArmorRepairersInfo',
     const.groupFueledRemoteArmorRepairer: 'AddArmorRepairersInfo',
     const.groupPrecursorRepairer: 'AddArmorRepairersInfo',
     const.groupHullRepairUnit: 'AddHullRepairersInfo',
     const.groupShieldBooster: 'AddShieldBoosterInfo',
     const.groupFueledShieldBooster: 'AddShieldBoosterInfo',
     const.groupTrackingComputer: 'AddTrackingComputerInfo',
     const.groupTrackingLink: 'AddTrackingComputerInfo',
     const.groupSmartBomb: 'AddSmartBombInfo',
     const.groupPropulsionModule: 'AddPropulsionModuleInfo',
     const.groupStasisWeb: 'AddStasisWebInfo',
     const.groupWarpScrambler: 'AddWarpScramblerInfo',
     const.groupCapacitorBooster: 'AddCapacitorBoosterInfo',
     const.groupEnergyTransferArray: 'AddEnergyTransferArrayInfo',
     const.groupShieldTransporter: 'AddShieldTransporterInfo',
     const.groupArmorRepairProjector: 'AddArmorRepairProjectorInfo',
     const.groupRemoteHullRepairer: 'AddRemoteHullRepairInfo',
     const.groupArmorHardener: 'AddArmorHardenerInfo',
     const.groupArmorCoating: 'AddArmorHardenerInfo',
     const.groupShieldHardener: 'AddArmorHardenerInfo',
     const.groupShieldAmplifier: 'AddArmorHardenerInfo',
     const.groupArmorPlatingEnergized: 'AddArmorHardenerInfo',
     const.groupElectronicCounterMeasureBurst: 'AddECMInfo',
     const.groupElectronicCounterMeasures: 'AddECMInfo',
     const.groupElectronicCounterCounterMeasures: 'AddECCMInfo',
     const.groupProjectedElectronicCounterCounterMeasures: 'AddECCMInfo',
     const.groupRemoteSensorDamper: 'AddSensorDamperInfo',
     const.groupRemoteSensorBooster: 'AddSensorDamperInfo',
     const.groupSensorBooster: 'AddSensorDamperInfo',
     const.groupTargetBreaker: 'AddTargetBreakerInfo',
     const.groupTargetPainter: 'AddTargetPainterInfo',
     const.groupTrackingDisruptor: 'AddTrackingDisruptorInfo',
     const.groupCloakingDevice: 'AddCloakingDeviceInfo',
     const.groupTractorBeam: 'AddTractorBeamInfo',
     const.groupDamageControl: 'AddDamageControlInfo',
     const.groupArmorResistanceShiftHardener: 'AddArmorResistanceShiftHardenerInfo',
     const.groupSuperWeapon: 'AddSuperWeaponInfo',
     const.groupGangCoordinator: 'AddGangCoordinatorInfo',
     const.groupScanProbeLauncher: 'AddScanProbeLauncherInfo',
     const.groupCynosuralField: 'AddCynoInfo',
     const.groupSiegeModule: 'AddSiegeInfo',
     const.groupStructureStasisWebifier: 'AddStasisWebInfo',
     const.groupStructureECM: 'AddECMInfo',
     const.groupStructureWarpDisruptor: 'AddWarpScramblerInfo',
     const.groupStructureEnergyNeutralizer: 'AddEnergyDestabilizerInfo',
     const.groupStructureDefenseBattery: 'AddStructureDefenseBatteryInfo',
     const.groupStructureDoomsdayWeapon: 'AddSuperWeaponInfo',
     const.groupMissileLauncherDot: 'AddDotWeaponInfo'}
    infoFunctionNamesForTypes = {const.typeStandupRemoteSensorDampener: 'AddSensorDamperInfo',
     const.typeStandupWeaponDisruptor: 'AddTrackingDisruptorInfo',
     const.typeStandupTargetPainter: 'AddTargetPainterInfo'}

    def ApplyAttributes(self, attributes):
        TooltipPanel.ApplyAttributes(self, attributes)
        self.stateManager = sm.StartService('godma').GetStateManager()
        self.dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        self.columns = 4
        self.margin = 16
        self.labelPadding = (4, 8, 4, 8)
        self.cellSpacing = 0
        self.cellPadding = 0
        self.SetBackgroundAlpha(0.75)
        self.controller = getattr(self.owner, 'controller', None)

    def LoadTooltip(self):
        if not self.owner:
            return
        self.ownerGuid = self.owner.__guid__
        if self.ownerGuid == 'xtriui.ModuleButton':
            self.moduleItemID = self.owner.moduleinfo.itemID
        else:
            self.moduleItemID = self.controller.GetModuleID()
        if not self.moduleItemID:
            return
        if self.ownerGuid in ('xtriui.FittingSlot', 'FittingServiceSlot', 'Drones'):
            self.dogmaLocation = sm.GetService('fittingSvc').GetCurrentDogmaLocation()
        else:
            self.dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        self.moduleInfoItem = self.dogmaLocation.GetDogmaItem(self.moduleItemID)
        self.moduleGroupID = evetypes.GetGroupID(self.moduleInfoItem.typeID)
        self.moduleCategoryID = evetypes.GetCategoryID(self.moduleInfoItem.typeID)
        self.numSlaves = self.GetNumberOfSlaves(self.moduleInfoItem, self.ownerGuid)
        if self.stateManager.GetDefaultEffect(self.moduleInfoItem.typeID):
            self.moduleShortcut = self.GetModuleShortcut(self.moduleInfoItem)
        else:
            self.moduleShortcut = None
        self.typeName = evetypes.GetName(self.moduleInfoItem.typeID)
        self.onHUDModuleButton = self.ownerGuid == 'xtriui.ModuleButton'
        self.UpdateToolTips()
        self._toolTooltipUpdateTimer = AutoTimer(1000, self.UpdateToolTips)

    def UpdateToolTips(self):
        if self.destroyed or self.beingDestroyed or self.owner is None:
            self._toolTooltipUpdateTimer = None
            return
        self.Flush()
        if getattr(self.owner, 'charge', None):
            chargeItemID = self.owner.charge.itemID
        elif self.controller and hasattr(self.controller, 'GetCharge') and self.controller.GetCharge():
            chargeItemID = self.controller.GetCharge().itemID
        else:
            chargeItemID = None
        if chargeItemID is None:
            chargeInfoItem = None
        else:
            chargeInfoItem = self.dogmaLocation.GetDogmaItem(chargeItemID)
        moduleDamageInfo = self.GetModuleDamage(self.ownerGuid, self.moduleItemID)
        chargesType, chargesQty = self.GetChargeTypeAndQty(self.moduleInfoItem, chargeInfoItem)
        typeText = self.GetTypeText()
        self.AddTypeAndIcon(label=typeText, typeID=self.moduleInfoItem.typeID, moduleShortcut=self.moduleShortcut, moduleDamageInfo=moduleDamageInfo)
        self.UpdateChargesCont(chargeInfoItem, chargesQty)
        maxRange, falloffDist, bombRadius, _ = self.GetRanges(chargeInfoItem)
        if maxRange > 0:
            self.AddRangeInfo(self.moduleInfoItem.typeID, optimalRange=maxRange, falloff=falloffDist)
        if self.ShouldAddDps(chargesQty):
            self.AddDpsAndDamgeTypeInfo(self.moduleItemID, self.moduleInfoItem.typeID, self.moduleGroupID, chargeInfoItem, self.numSlaves)
        self.AddGroupAndCategoryExtraInfo(chargeInfoItem)
        self.AddTrackingSpeed(self.moduleItemID)
        self.AddCountDownTimes(self.moduleItemID)
        if moduleDamageInfo.repairTimeLeft > 0:
            self.GetTimeLeftRepairingCountDown(moduleDamageInfo.repairTimeLeft)
        if self.onHUDModuleButton:
            safetyLevel = self.owner.GetSafetyWarning()
            if safetyLevel is not None:
                self.AddSafetyLevelWarning(safetyLevel)
        self.AddActivityStatus()

    def AddGroupAndCategoryExtraInfo(self, chargeInfoItem):
        categoryInfoFuncName = self.infoFunctionNamesForCategories.get(self.moduleCategoryID, None)
        goupInfoFuncName = self.infoFunctionNames.get(self.moduleGroupID, None)
        typeInfoFuncName = self.infoFunctionNamesForTypes.get(self.moduleInfoItem.typeID)
        for funcName in (categoryInfoFuncName, goupInfoFuncName, typeInfoFuncName):
            if funcName is None:
                continue
            myInfoFunction = getattr(self, funcName)
            myInfoFunction(self.moduleItemID, chargeInfoItem)

    def GetTypeText(self):
        if self.numSlaves:
            typeText = localization.GetByLabel('UI/Inflight/ModuleRacks/TypeNameWithNumInGroup', numInGroup=self.numSlaves, typeName=self.typeName)
        else:
            typeText = self.typeName
        typeText = '<b>%s</b>' % typeText
        return typeText

    def GetRanges(self, chargeInfoItem):
        return sm.GetService('tactical').FindMaxRange(self.moduleInfoItem, chargeInfoItem, self.dogmaLocation)

    def ShouldAddDps(self, chargesQty):
        shouldAddDps = chargesQty is not None
        return shouldAddDps

    def UpdateChargesCont(self, chargeInfoItem, chargesQty):
        if chargeInfoItem and chargesQty:
            chargeText = self.GetChargeText(chargeInfoItem, chargesQty)
            self.AddTypeAndIcon(label=chargeText, typeID=chargeInfoItem.typeID)

    def GetChargeText(self, chargeInfoItem, chargesQty):
        if chargeInfoItem.groupID in cfg.GetCrystalGroups():
            crystalDamageAmount = self.GetCrystalDamage(chargeInfoItem)
            chargeText = '<b>%s</b>' % evetypes.GetName(chargeInfoItem.typeID)
            if crystalDamageAmount > 0.0:
                damagedText = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleDamaged', color='<color=red>', percentageNum=crystalDamageAmount * 100)
                chargeText += '<br>' + damagedText
        else:
            chargeText = localization.GetByLabel('UI/Inflight/ModuleRacks/AmmoNameWithQty', qty=chargesQty, ammoTypeID=chargeInfoItem.typeID)
        return chargeText

    def GetModuleDamage(self, ownerGuid, moduleItemID):
        moduleDamageInfo = KeyVal(moduleDamage=None, repairingModuleDamage=None, repairTimeLeft=None)
        myShipID = GetActiveShip()
        if myShipID != self.dogmaLocation.GetCurrentShipID():
            return moduleDamageInfo
        showSingleModuleReadout = ownerGuid in ('xtriui.FittingSlot', 'FittingServiceSlot')
        if self.stateManager.IsBeingRepaired(moduleItemID):
            repairingModuleDamage, repairTimeLeft = self.GetTotalDamageWhileRepairing(moduleItemID, showSingleModuleReadout)
            moduleDamageInfo.repairingModuleDamage = int(math.ceil(repairingModuleDamage / self.dogmaLocation.GetAttributeValue(moduleItemID, const.attributeHp) * 100))
            moduleDamageInfo.repairTimeLeft = repairTimeLeft
        else:
            if showSingleModuleReadout:
                damage = self.dogmaLocation.GetAccurateAttributeValue(moduleItemID, const.attributeDamage)
            else:
                damage = uicore.layer.shipui.controller.GetModuleGroupDamage(moduleItemID)
            if damage:
                moduleDamageAmount = int(math.ceil(damage / self.dogmaLocation.GetAttributeValue(moduleItemID, const.attributeHp) * 100))
                moduleDamageInfo.moduleDamage = moduleDamageAmount
        return moduleDamageInfo

    def GetCrystalDamage(self, chargeInfoItem):
        crystalDamageAmount = None
        if chargeInfoItem is not None:
            if self.ownerGuid == 'xtriui.FittingSlot':
                dogmaLocation = sm.GetService('fittingSvc').GetCurrentDogmaLocation()
            else:
                dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            crystalDamageAmount = dogmaLocation.GetAccurateAttributeValue(chargeInfoItem.itemID, const.attributeDamage)
        return crystalDamageAmount

    def GetNumberOfSlaves(self, moduleInfoItem, ownerGuid):
        myShip = GetActiveShip()
        if ownerGuid == 'xtriui.FittingSlot':
            return 0
        else:
            slaves = self.dogmaLocation.GetSlaveModules(moduleInfoItem.itemID, myShip)
            if slaves:
                numSlaves = len(slaves) + 1
            else:
                numSlaves = 0
            return numSlaves

    def GetModuleShortcut(self, moduleInfoItem):
        moduleShortcut = None
        masterModuleID = self.dogmaLocation.GetMasterModuleID(GetActiveShip(), moduleInfoItem.itemID)
        if masterModuleID is not None:
            masterModuleInfoItem = self.dogmaLocation.GetDogmaItem(masterModuleID)
            flagID = masterModuleInfoItem.flagID
        else:
            flagID = moduleInfoItem.flagID
        slotOrder = shipHud.GetSlotOrder()
        if flagID not in slotOrder:
            return
        pos = slotOrder.index(flagID)
        if pos is not None:
            row = pos / 8
            hiMedLo = ('High', 'Medium', 'Low')[row]
            loc = pos % 8
            slotno = loc + 1
            shortcut = uicore.cmd.GetShortcutStringByFuncName('CmdActivate%sPowerSlot%i' % (hiMedLo, slotno))
            if shortcut:
                moduleShortcut = shortcut
        return moduleShortcut

    def GetChargeTypeAndQty(self, moduleInfoItem, chargeInfoItem):
        chargesQty = None
        chargesType = None
        if self.IsChargeCompatible(moduleInfoItem):
            if chargeInfoItem and chargeInfoItem.typeID:
                chargesQty = self.dogmaLocation.GetQuantity(chargeInfoItem.itemID)
                chargesType = chargeInfoItem.typeID
            else:
                chargesQty = 0
        return (chargesType, chargesQty)

    def IsChargeCompatible(self, moduleInfoItem):
        return moduleInfoItem.groupID in cfg.__chargecompatiblegroups__

    def GetEffectiveAttributeValue(self, itemID, attributeID):
        attributeValue = self.dogmaLocation.GetAccurateAttributeValue(itemID, attributeID)
        unitID = dogma_data.get_attribute_unit_id(attributeID)
        if unitID in (const.unitInverseAbsolutePercent, const.unitInversedModifierPercent):
            attributeValue = (1.0 - attributeValue) * 100.0
        elif unitID == const.unitModifierPercent:
            attributeValue = -(1.0 - attributeValue) * 100.0
        return attributeValue

    def GetDuration(self, itemID, durationAttributeID = None):
        if durationAttributeID is None:
            durationAttributeID = const.attributeDuration
        duration = self.GetEffectiveAttributeValue(itemID, durationAttributeID)
        durationInSec = duration / 1000.0
        if durationInSec % 1.0 == 0:
            decimalPlaces = 0
        else:
            decimalPlaces = 1
        unit = units.get_display_name(const.unitMilliseconds)
        durationFormatted = localization.formatters.FormatNumeric(durationInSec, decimalPlaces=decimalPlaces)
        formattedDuration = localization.GetByLabel('UI/InfoWindow/ValueAndUnit', value=durationFormatted, unit=unit)
        return formattedDuration

    def AddSafetyLevelWarning(self, safetyLevel):
        if safetyLevel == const.shipSafetyLevelNone:
            iconColor = CrimeWatchColors.Criminal.GetRGBA()
            text = localization.GetByLabel('UI/Crimewatch/SafetyLevel/ModuleRestrictionTooltip', color=CrimeWatchColors.Criminal.GetHex())
        else:
            iconColor = CrimeWatchColors.Suspect.GetRGBA()
            text = localization.GetByLabel('UI/Crimewatch/SafetyLevel/ModuleRestrictionTooltip', color=CrimeWatchColors.Suspect.GetHex())
        texturePath = 'res:/UI/Texture/Crimewatch/Crimewatch_SuspectCriminal.png'
        icon, label = self.AddRowWithIconAndText(text, texturePath, iconSize=16)
        icon.SetRGBA(*iconColor)

    def AddActivityStatus(self):
        text, color, activityState = self.dogmaLocation.GetActivityState(self.moduleItemID)
        if text:
            self.FillRow()
            self.AddCell(colSpan=2)
            label = self.AddLabelLarge(text=text, colSpan=self.columns - 2, align=uiconst.CENTERLEFT, cellPadding=self.labelPadding, bold=True)
            label.SetRGBA(*color)

    def AddTypeAndIcon(self, label, typeID, moduleShortcut = None, moduleDamageInfo = None, iconSize = 26, minRowSize = 30):
        self.FillRow()
        self.AddSpacer(height=minRowSize, width=0)
        iconCont = Container(pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.CENTER)
        iconObj = Icon(parent=iconCont, pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.TOPLEFT, ignoreSize=True)
        iconObj.LoadIconByTypeID(typeID, size=iconSize, ignoreSize=True)
        techIcon = Icon(parent=iconCont, width=16, height=16, align=uiconst.TOPLEFT, idx=0, top=0)
        GetTechLevelIcon(techIcon, typeID=typeID)
        self.AddCell(iconCont, cellPadding=2)
        if moduleShortcut:
            nameColSpan = self.columns - 3
        else:
            nameColSpan = self.columns - 2
        if moduleDamageInfo:
            repairingText = ''
            if moduleDamageInfo.repairingModuleDamage:
                repairingText = localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/ModuleRepairing')
            damageToShow = moduleDamageInfo.repairingModuleDamage or moduleDamageInfo.moduleDamage
            if damageToShow > 0:
                damagedText = localization.GetByLabel('UI/Inflight/ModuleRacks/ModuleDamaged', color='<color=red>', percentageNum=damageToShow)
                label += '<br>%s%s' % (damagedText, repairingText)
        labelObj = self.AddLabelMedium(text=label, align=uiconst.CENTERLEFT, cellPadding=self.labelPadding, colSpan=nameColSpan)
        if moduleShortcut:
            shortcutObj = ShortcutHint(text=moduleShortcut)
            shortcutObj.width += 10
            shortcutObj.padLeft = 10
            self.AddCell(shortcutObj)
        return (iconObj, labelObj)

    def AddAttributeRow(self, texturePath, attributeValues, minRowSize = 30, spacerWidth = 100):
        self.AddCell()
        self.AddCell()
        self.AddSpacer(colSpan=self.columns - 2, width=spacerWidth, height=0)
        self.FillRow()
        self.AddSpacer(width=0, height=minRowSize)
        self.AddIconCell(texturePath)
        container = AttributeValueRowContainer(attributeValues=attributeValues)
        self.AddCell(container, colSpan=self.columns - 2)
        self.FillRow()

    def AddRangeInfo(self, typeID, optimalRange, falloff):
        text, formattedOptimalRange = self.GetOptimalRangeText(typeID, optimalRange, falloff)
        if not text:
            return
        texturePath = 'res:/UI/Texture/Icons/22_32_15.png'
        self.AddRowWithIconAndText(text, texturePath)

    def GetOptimalRangeText(self, typeID, optimalRange, falloff):
        if optimalRange <= 0:
            return ('', '')
        formattedOptimalRAnge = FmtDist(optimalRange)
        if sm.GetService('clientDogmaStaticSvc').TypeHasEffect(typeID, const.effectLauncherFitted):
            rangeText = localization.GetByLabel('UI/Inflight/ModuleRacks/MaxRange', maxRange=formattedOptimalRAnge)
        elif sm.GetService('clientDogmaStaticSvc').TypeHasEffect(typeID, const.effectTurretFitted) or evetypes.GetCategoryID(typeID) == const.categoryFighter:
            if falloff > 1:
                rangeText = localization.GetByLabel('UI/Inflight/ModuleRacks/OptimalRangeAndFalloff', optimalRange=formattedOptimalRAnge, falloffPlusOptimal=FmtDist(falloff + optimalRange))
            else:
                rangeText = localization.GetByLabel('UI/Inflight/ModuleRacks/OptimalRange', optimalRange=formattedOptimalRAnge)
        elif evetypes.GetGroupID(typeID) == const.groupSmartBomb:
            rangeText = localization.GetByLabel('UI/Inflight/ModuleRacks/AreaOfEffect', range=formattedOptimalRAnge)
        elif falloff > 1:
            rangeText = localization.GetByLabel('UI/Inflight/ModuleRacks/RangeWithFalloff', optimalRange=formattedOptimalRAnge, falloffPlusOptimal=FmtDist(falloff + optimalRange))
        else:
            rangeText = localization.GetByLabel('UI/Inflight/ModuleRacks/Range', optimalRange=formattedOptimalRAnge)
        return (rangeText, formattedOptimalRAnge)

    def GetAmountPerTimeInfo(self, itemID, attributeID, labelPath, chargeMultiplier = 1.0):
        duration = self.GetDuration(itemID)
        amount = self.GetEffectiveAttributeValue(itemID, attributeID)
        amount = amount * chargeMultiplier
        text = localization.GetByLabel(labelPath, duration=duration, amount=amount)
        return (text, duration, amount)

    def AddRowWithIconAndText(self, text, texturePath = None, iconID = None, iconSize = 24, minRowSize = 30):
        self.FillRow()
        self.AddSpacer(height=minRowSize, width=0)
        icon = self.AddIconCell(texturePath or iconID, iconSize=iconSize)
        label = self.AddLabelMedium(text=text, colSpan=self.columns - 2, align=uiconst.CENTERLEFT, cellPadding=self.labelPadding)
        self.FillRow()
        return (icon, label)

    def AddRowWithIconAndTextAndValue(self, text, valueText, texturePath, iconSize = 24, minRowSize = 30):
        self.FillRow()
        self.AddSpacer(height=minRowSize, width=0)
        self.AddIconCell(texturePath, iconSize=iconSize)
        self.AddLabelMedium(text=text, colSpan=1, align=uiconst.CENTERLEFT, cellPadding=self.labelPadding)
        self.AddLabelMedium(text=valueText, align=uiconst.CENTERRIGHT, left=2)
        self.FillRow()

    def AddRowWithIconAndContainer(self, texturePath, container, iconSize = 24, minRowSize = 30):
        self.FillRow()
        self.AddSpacer(height=minRowSize, width=0)
        self.AddIconCell(texturePath, iconSize=iconSize)
        self.AddCell(container, colSpan=self.columns - 1)

    def AddIconCell(self, texturePath = None, iconID = None, iconSize = 24):
        icon = Icon(pos=(0,
         0,
         iconSize,
         iconSize), align=uiconst.CENTER, ignoreSize=True, state=uiconst.UI_DISABLED, icon=texturePath or iconID)
        self.AddCell(icon)
        return icon

    def AddRowForInfoWithOneOrMoreAttributes(self, attributeValues, oneAttributeText, manyAttributesText, headerText, texturePath = ''):
        if len(attributeValues) == 1:
            self.AddRowForSingleAttribute(attributeValues=attributeValues, labelPath=oneAttributeText)
        elif attributeValues:
            self.AddRowAndHeaderForManyAttributes(attributeValues, manyAttributesText, headerText, texturePath)

    def AddRowForSingleAttribute(self, attributeValues, labelPath):
        attributeID, value = attributeValues[0]
        iconID = dogma_data.get_attribute_icon_id(attributeID)
        displayName = dogma_data.get_attribute_display_name(attributeID)
        text = localization.GetByLabel(labelPath, activeName=displayName, activeValue=value)
        self.AddRowWithIconAndText(text=text, iconID=iconID)

    def AddRowAndHeaderForManyAttributes(self, attributeValues, manyAttributesText, headerText, texturePath = ''):
        text = localization.GetByLabel(headerText)
        icon, label = self.AddRowWithIconAndText(text=text, texturePath='', minRowSize=24)
        label.SetAlign(uiconst.BOTTOMLEFT)
        formattedAttributeValues = self.GetFormattedAttributeValues(attributeValues=attributeValues, valueText=manyAttributesText)
        self.AddAttributeRow(texturePath, formattedAttributeValues, minRowSize=0, spacerWidth=65 * len(formattedAttributeValues))

    def GetFormattedAttributeValues(self, attributeValues, valueText):
        attributeValuesText = []
        for attributeID, attributeValue in attributeValues:
            attributeValueText = localization.GetByLabel(valueText, activeValue=attributeValue)
            attributeValuesText.append((attributeID, attributeValueText))

        return attributeValuesText

    def AddDpsAndDamgeTypeInfo(self, itemID, typeID, groupID, charge, numSlaves):
        totalDpsDamage, totalDpsDamageWithReload, texturePath, iconID, damageMultiplier = self.GetDpsDamageTypeInfo(itemID, typeID, groupID, charge, numSlaves)
        if not totalDpsDamage:
            return
        text = localization.GetByLabel('UI/Inflight/ModuleRacks/DamagePerSecond', dps=totalDpsDamage)
        self.AddRowWithIconAndText(text=text, texturePath=texturePath, iconID=iconID)
        self.AddDamageTypes(itemID, charge, damageMultiplier)

    def GetDpsDamageTypeInfo(self, itemID, typeID, groupID, charge, numSlaves):
        isBomb = groupID == const.groupMissileLauncherBomb
        dogmaStaticSvc = sm.GetService('clientDogmaStaticSvc')
        isLauncher = dogmaStaticSvc.TypeHasEffect(typeID, const.effectLauncherFitted) or dogmaStaticSvc.TypeHasEffect(typeID, const.effectUseMissiles)
        isTurret = dogmaStaticSvc.TypeHasEffect(typeID, const.effectTurretFitted)
        if not isLauncher and not isTurret and not isBomb:
            return (None, None, None, None, None)
        GAV = self.dogmaLocation.GetAccurateAttributeValue
        texturePath = None
        iconID = None
        totalDpsDamage = 0
        totalDpsDamageWithReload = 0
        damageMultiplier = 1
        if (isLauncher or isBomb) and charge:
            chargeKey = charge.itemID
            damageMultiplier = GetMissleDamageMultiplier(self.dogmaLocation, itemID, session.charid, GAV)
            totalDpsDamage, totalDpsDamageWithReload = GetLauncherDps(self.dogmaLocation, chargeKey, itemID, session.charid, GAV)
            if isLauncher:
                texturePath = 'res:/UI/Texture/Icons/81_64_16.png'
            else:
                iconID = evetypes.GetIconID(typeID)
        elif isTurret:
            if charge:
                chargeKey = charge.itemID
            else:
                chargeKey = None
            totalDpsDamage, totalDpsDamageWithReload = GetTurretDps(self.dogmaLocation, chargeKey, itemID, GAV)
            damageMultiplier = GAV(itemID, const.attributeDamageMultiplier)
            texturePath = 'res:/UI/Texture/Icons/26_64_1.png'
        if totalDpsDamage == 0:
            return (totalDpsDamage,
             totalDpsDamageWithReload,
             texturePath,
             iconID,
             damageMultiplier)
        if numSlaves:
            totalDpsDamage = numSlaves * totalDpsDamage
            damageMultiplier = numSlaves * damageMultiplier
            totalDpsDamageWithReload = numSlaves * totalDpsDamageWithReload
        return (totalDpsDamage,
         totalDpsDamageWithReload,
         texturePath,
         iconID,
         damageMultiplier)

    def AddDamageTypes(self, itemID, charge, multiplier):
        if charge:
            dmgCausingItemID = charge.itemID
        else:
            dmgCausingItemID = itemID
        damageAttributeValues = self.GetAttributesValues(dmgCausingItemID, multiplier, const.damageTypeAttributes, includeZeros=False)
        if not damageAttributeValues:
            return
        self.AddRowForInfoWithOneOrMoreAttributes(attributeValues=damageAttributeValues, oneAttributeText='UI/Inflight/ModuleRacks/Tooltips/OneDamageTypeText', manyAttributesText='UI/Inflight/ModuleRacks/Tooltips/DamageHitpoints', headerText='UI/Inflight/ModuleRacks/Tooltips/DamageTypesHeader')

    def GetAttributesValues(self, itemID, multiplier, attributeList, includeZeros = True):
        attributeValues = []
        for eachAttributeID in attributeList:
            attributeValue = self.GetEffectiveAttributeValue(itemID, eachAttributeID)
            if not attributeValue and not includeZeros:
                continue
            attributeValue = attributeValue * multiplier
            attributeValues.append((eachAttributeID, attributeValue))

        return attributeValues

    def AddAttributePerTimeInfo(self, itemID, attributeID, labelPath, chargeMultiplier = 1.0):
        text, duration, amount = self.GetAmountPerTimeInfo(itemID=itemID, attributeID=attributeID, labelPath=labelPath, chargeMultiplier=chargeMultiplier)
        iconID = dogma_data.get_attribute_icon_id(attributeID)
        self.AddRowWithIconAndText(text=text, iconID=iconID)

    def AddAttributeInfo(self, itemID, attributeID, labelPath, labelKeyword, skipZeroValue = False):
        value = self.GetEffectiveAttributeValue(itemID, attributeID)
        if value == 0 and skipZeroValue:
            return
        tokenDict = {labelKeyword: value}
        text = localization.GetByLabel(labelPath, **tokenDict)
        iconID = dogma_data.get_attribute_icon_id(attributeID)
        self.AddRowWithIconAndText(text=text, iconID=iconID)

    def AddAttributeInfoWithAttributeName(self, itemID, attributeID, labelPath, skipZeroValue = False):
        activeValue = self.GetEffectiveAttributeValue(itemID, attributeID)
        if activeValue == 0 and skipZeroValue:
            return
        iconID = dogma_data.get_attribute_icon_id(attributeID)
        displayName = dogma_data.get_attribute_display_name(attributeID)
        text = localization.GetByLabel(labelPath, activeValue=activeValue, activeName=displayName)
        self.AddRowWithIconAndText(text=text, iconID=iconID)

    def AddCompressorInfo(self, itemID, *args):
        self.FillRow()
        self.AddSpacer()
        texturePath = 'res:/UI/Texture/Classes/SkillPlan/infoIcon.png'
        range = self.GetEffectiveAttributeValue(itemID, const.attributeMaxRange)
        text = localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/CompressorModuleInfo', range=FmtDist(range))
        self.AddIconCell(texturePath, iconSize=34)
        self.AddLabelMedium(text=text, colSpan=2, align=uiconst.CENTERLEFT, cellPadding=self.labelPadding, wrapWidth=250)
        self.FillRow()

    def AddMiningLaserInfo(self, itemID, chargeInfoItem, *args):
        duration = self.GetDuration(itemID)
        amount = self.GetEffectiveAttributeValue(itemID, const.attributeMiningAmount)
        durationInSec = self.GetEffectiveAttributeValue(itemID, const.attributeDuration) / 1000.0
        amountPerSec = amount / durationInSec
        text = localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/MiningAmountPerTime2', duration=duration, amount=amount, amountPerSec=amountPerSec)
        self.AddRowWithIconAndText(text=text, texturePath='res:/ui/texture/icons/23_64_5.png')

    def AddEnergyVampireInfo(self, itemID, chargeInfoItem):
        self.AddAttributePerTimeInfo(itemID=itemID, attributeID=const.attributePowerTransferAmount, labelPath='UI/Inflight/ModuleRacks/Tooltips/EnergyVampireAmountPerTime')

    def AddEnergyDestabilizerInfo(self, itemID, chargeInfoItem):
        self.AddAttributePerTimeInfo(itemID=itemID, attributeID=const.attributeEnergyNeutralizerAmount, labelPath='UI/Inflight/ModuleRacks/Tooltips/EnergDestabilizedPerTime')

    def AddArmorRepairersInfo(self, itemID, chargeInfoItem):
        if chargeInfoItem:
            chargeMultiplier = self.GetEffectiveAttributeValue(itemID, const.attributeChargedArmorDamageMultiplier)
        else:
            chargeMultiplier = 1.0
        self.AddAttributePerTimeInfo(itemID=itemID, attributeID=const.attributeArmorDamageAmount, labelPath='UI/Inflight/ModuleRacks/Tooltips/ArmorRepairedPerTime', chargeMultiplier=chargeMultiplier)

    def AddHullRepairersInfo(self, itemID, chargeInfoItem):
        self.AddAttributePerTimeInfo(itemID=itemID, attributeID=const.attributeStructureDamageAmount, labelPath='UI/Inflight/ModuleRacks/Tooltips/HullRepairedPerTime')

    def AddShieldBoosterInfo(self, itemID, chargeInfoItem):
        self.AddAttributePerTimeInfo(itemID=itemID, attributeID=const.attributeShieldBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/ShieldBonusPerTime')

    def AddTrackingComputerInfo(self, itemID, chargeInfoItem):
        self.AddAttributeInfo(itemID=itemID, attributeID=const.attributeFalloffBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/TrackingComputerFalloffBonus', labelKeyword='falloffBonus')
        self.AddAttributeInfo(itemID=itemID, attributeID=const.attributeMaxRangeBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/TrackingComputerRangeBonus', labelKeyword='optimalRangeBonus')
        self.AddAttributeInfo(itemID=itemID, attributeID=const.attributeTrackingSpeedBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/TrackingComputerTrackingBonus', labelKeyword='trackingSpeedBonus')

    def AddSmartBombInfo(self, itemID, chargeInfoItem):
        attrID = None
        damage = 0
        for attributeID in const.damageTypeAttributes:
            damage = self.GetEffectiveAttributeValue(itemID, attributeID)
            if damage > 0:
                attrID = attributeID
                break

        attributeInfo = dogma_data.get_attribute(attrID)
        damageType = dogma_data.get_attribute_display_name(attrID)
        iconID = attributeInfo.iconID
        text = localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/SmartBombDamage', amount=damage, damageType=damageType)
        self.AddRowWithIconAndText(text=text, iconID=iconID)

    def AddPropulsionModuleInfo(self, itemID, chargeInfoItem):
        myShipID = self.dogmaLocation.GetActiveShipID()
        if self.dogmaLocation.locationName == 'FittingDogmaLocation':
            _, _, activityState = self.dogmaLocation.GetActivityState(self.moduleItemID)
            maxVelocity = self.dogmaLocation.GetAccurateAttributeValue(myShipID, attributeMaxVelocity)
            if activityState in (ACTIVE, OVERHEATED):
                text = localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/MaxVelocityWith', maxVelocity=maxVelocity)
            else:
                text = localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/MaxVelocityWithout', maxVelocity=maxVelocity)
        else:
            speedFactor, speedBoostFactor = self._GetSpeedBoostForPropulsionModule(itemID)
            currentMass = self.dogmaLocation.GetAccurateAttributeValue(myShipID, attributeMass)
            godmaEffect = self._GetDefaultDogmaEffect(itemID, self.moduleInfoItem.typeID)
            if godmaEffect.isActive:
                maxVelocityWithBonus = self.dogmaLocation.GetAccurateAttributeValue(myShipID, attributeMaxVelocity)
                myMaxVelocity = maxVelocityWithBonus / self._GetVelocityRatio(speedBoostFactor, speedFactor, currentMass)
            else:
                myMaxVelocity, activatedMass = self._GetMyMaxVelocityAndMassOnActivation(itemID, myShipID, currentMass)
                maxVelocityWithBonus = myMaxVelocity * self._GetVelocityRatio(speedBoostFactor, speedFactor, activatedMass)
            text = localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/MaxVelocityWithAndWithoutPropulsion', maxVelocity=myMaxVelocity, maxVelocityWithBonus=maxVelocityWithBonus)
        iconID = dogma_data.get_attribute_icon_id(attributeMaxVelocity)
        self.AddRowWithIconAndText(text=text, iconID=iconID)

    def _GetMyMaxVelocityAndMassOnActivation(self, propulsionItemID, myShipID, currentMass):
        myMaxVelocity = self.dogmaLocation.GetAccurateAttributeValue(myShipID, attributeMaxVelocity)
        typeBaseMass = self.dogmaLocation.GetAttributeValue(myShipID, attributeMass)
        massAddition = self.dogmaLocation.GetAttributeValue(propulsionItemID, attributeMassAddition)
        massFactor = currentMass / typeBaseMass
        massOnActivation = massFactor * (typeBaseMass + massAddition)
        shipItem = self.dogmaLocation.GetDogmaItem(myShipID)
        fittedItems = shipItem.GetFittedItems()
        for fittedModuleItemID, moduleItem in fittedItems.iteritems():
            if propulsionItemID == fittedModuleItemID:
                continue
            if moduleItem.groupID == groupPropulsionModule:
                godmaEffect = self._GetDefaultDogmaEffect(fittedModuleItemID, moduleItem.typeID)
                if godmaEffect.isActive:
                    speedFactor, speedBoostFactor = self._GetSpeedBoostForPropulsionModule(fittedModuleItemID)
                    massAddition = self.dogmaLocation.GetAttributeValue(fittedModuleItemID, attributeMassAddition)
                    massFactor = currentMass / typeBaseMass
                    massOnActivation = massFactor * (currentMass - massAddition)
                    myMaxVelocity = myMaxVelocity / self._GetVelocityRatio(speedBoostFactor, speedFactor, currentMass)
                    break

        return (myMaxVelocity, massOnActivation)

    def _GetDefaultDogmaEffect(self, itemID, typeID):
        effectName = self.stateManager.GetDefaultEffect(typeID).effectName
        godmaItem = self.dogmaLocation.godma.GetItem(itemID)
        return godmaItem.effects[effectName]

    def _GetVelocityRatio(self, speedBoostFactor, speedFactor, mass):
        return 1 + speedBoostFactor * speedFactor * 0.01 / mass

    def _GetSpeedBoostForPropulsionModule(self, moduleItemID):
        speedFactor = self.GetEffectiveAttributeValue(moduleItemID, attributeSpeedFactor)
        speedBoostFactor = self.GetEffectiveAttributeValue(moduleItemID, attributeSpeedBoostFactor)
        return (speedFactor, speedBoostFactor)

    def AddStasisWebInfo(self, itemID, chargeInfoItem):
        attributeID = const.attributeSpeedFactor
        amount = self.GetEffectiveAttributeValue(itemID, attributeID)
        text = localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/VelocityReductionFromWeb', percentage=abs(amount))
        iconID = dogma_data.get_attribute_icon_id(attributeID)
        self.AddRowWithIconAndText(text=text, iconID=iconID)

    def AddWarpScramblerInfo(self, itemID, chargeInfoItem):
        self.AddAttributeInfo(itemID=itemID, attributeID=const.attributeWarpScrambleStrength, labelPath='UI/Inflight/ModuleRacks/Tooltips/WarpScramblerStrength', labelKeyword='strength')

    def AddCapacitorBoosterInfo(self, itemID, chargeInfoItem):
        attributeID = const.attributeCapacitorBonus
        duration = self.GetDuration(itemID)
        if chargeInfoItem is None:
            return
        amount = self.GetEffectiveAttributeValue(chargeInfoItem.itemID, attributeID)
        text = localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/CapacitorBoostPerTime', boostAmount=amount, duration=duration)
        iconID = dogma_data.get_attribute_icon_id(attributeID)
        self.AddRowWithIconAndText(text=text, iconID=iconID)

    def AddEnergyTransferArrayInfo(self, itemID, chargeInfoItem):
        self.AddAttributePerTimeInfo(itemID=itemID, attributeID=const.attributePowerTransferAmount, labelPath='UI/Inflight/ModuleRacks/Tooltips/EnergyTransferredPerTime')

    def AddShieldTransporterInfo(self, itemID, chargeInfoItem):
        self.AddAttributePerTimeInfo(itemID=itemID, attributeID=const.attributeShieldBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/ShieldTransportedPerTime')

    def AddArmorRepairProjectorInfo(self, itemID, chargeInfoItem):
        self.AddAttributePerTimeInfo(itemID=itemID, attributeID=const.attributeArmorDamageAmount, labelPath='UI/Inflight/ModuleRacks/Tooltips/ArmorTransferredPerTime')

    def AddRemoteHullRepairInfo(self, itemID, chargeInfoItem):
        self.AddAttributePerTimeInfo(itemID=itemID, attributeID=const.attributeStructureDamageAmount, labelPath='UI/Inflight/ModuleRacks/Tooltips/HullRemoteRepairedPerTime')

    def AddArmorHardenerInfo(self, itemID, chargeInfoItem):
        damageAttributeValues = self.GetAttributesValues(itemID, 1, RESISTANCE_BONUS_ATTRIBUTES, includeZeros=False)
        self.AddRowForInfoWithOneOrMoreAttributes(attributeValues=damageAttributeValues, oneAttributeText='UI/Inflight/ModuleRacks/Tooltips/ResistanceActiveBonusText', manyAttributesText='UI/Inflight/ModuleRacks/Tooltips/ResistanceActiveBonusValues', headerText='UI/Inflight/ModuleRacks/Tooltips/ResistanceActiveBonusesHeader')

    def AddECMInfo(self, itemID, chargeInfoItem):
        bonusAttributes = [const.attributeScanGravimetricStrengthBonus,
         const.attributeScanLadarStrengthBonus,
         const.attributeScanMagnetometricStrengthBonus,
         const.attributeScanRadarStrengthBonus]
        rows = []
        for attrID in bonusAttributes:
            strength = self.GetEffectiveAttributeValue(itemID, attrID)
            if strength is not None and strength != 0:
                attributeName = dogma_data.get_attribute_display_name(attrID)
                rows.append(localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/ECMStrengthBonus', strength=strength, attributeName=attributeName))

        text = '<br>'.join(rows)
        self.AddRowWithIconAndText(text=text, texturePath='res:/UI/Texture/Icons/4_64_12.png')

    def AddECCMInfo(self, itemID, chargeInfoItem):
        damageTypeAttributes = [const.attributeScanGravimetricStrengthPercent,
         const.attributeScanLadarStrengthPercent,
         const.attributeScanMagnetometricStrengthPercent,
         const.attributeScanRadarStrengthPercent]
        rows = []
        for attrID in damageTypeAttributes:
            strength = self.GetEffectiveAttributeValue(itemID, attrID)
            if strength is not None and strength != 0:
                attributeName = dogma_data.get_attribute_display_name(attrID)
                rows.append(localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/ValuePercentageWithAttributeName', activeValue=strength, activeName=attributeName))

        text = '<br>'.join(rows)
        if text:
            self.AddRowWithIconAndText(text=text, texturePath='res:/UI/Texture/Icons/4_64_12.png')

    def AddSensorDamperInfo(self, itemID, chargeInfoItem):
        bonus = self.GetEffectiveAttributeValue(itemID, const.attributeScanResolutionBonus)
        if bonus != 0:
            self.AddAttributeInfoWithAttributeName(itemID=itemID, attributeID=const.attributeScanResolutionBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/ValuePercentageWithAttributeName')
        bonus = self.GetEffectiveAttributeValue(itemID, const.attributeMaxTargetRangeBonus)
        if bonus != 0:
            self.AddAttributeInfoWithAttributeName(itemID=itemID, attributeID=const.attributeMaxTargetRangeBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/ValuePercentageWithAttributeName')
        self.AddECCMInfo(itemID, chargeInfoItem)

    def AddTargetBreakerInfo(self, itemID, chargeInfoItem):
        self.AddAttributeInfoWithAttributeName(itemID=itemID, attributeID=const.attributeSignatureSuppressorSignatureRadiusBonusPassive, labelPath='UI/Inflight/ModuleRacks/Tooltips/ValuePercentageWithAttributeName')

    def AddTargetPainterInfo(self, itemID, chargeInfoItem):
        self.AddAttributeInfoWithAttributeName(itemID=itemID, attributeID=const.attributeSignatureRadiusBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/ValuePercentageWithAttributeName')

    def AddTrackingDisruptorInfo(self, itemID, chargeInfoItem):
        self.AddAttributeInfoWithAttributeName(itemID=itemID, attributeID=const.attributeFalloffBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/ValuePercentageWithAttributeName', skipZeroValue=True)
        self.AddAttributeInfoWithAttributeName(itemID=itemID, attributeID=const.attributeMaxRangeBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/ValuePercentageWithAttributeName', skipZeroValue=True)
        self.AddAttributeInfoWithAttributeName(itemID=itemID, attributeID=const.attributeTrackingSpeedBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/ValuePercentageWithAttributeName', skipZeroValue=True)
        self.AddAttributeInfoWithAttributeName(itemID=itemID, attributeID=const.attributeMissileVelocityBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/ValuePercentageWithAttributeName', skipZeroValue=True)
        self.AddAttributeInfoWithAttributeName(itemID=itemID, attributeID=const.attributeExplosionDelayBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/ValuePercentageWithAttributeName', skipZeroValue=True)
        self.AddAttributeInfoWithAttributeName(itemID=itemID, attributeID=const.attributeAoeVelocityBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/ValuePercentageWithAttributeName', skipZeroValue=True)
        self.AddAttributeInfoWithAttributeName(itemID=itemID, attributeID=const.attributeAoeCloudSizeBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/ValuePercentageWithAttributeName', skipZeroValue=True)

    def AddCloakingDeviceInfo(self, itemID, chargeInfoItem):
        self.AddAttributeInfoWithAttributeName(itemID=itemID, attributeID=const.attributeMaxVelocityBonus, labelPath='UI/Inflight/ModuleRacks/Tooltips/ValuePercentageWithAttributeName')

    def AddTractorBeamInfo(self, itemID, chargeInfoItem):
        attributeID = const.attributeMaxTractorVelocity
        maxTractorVel = self.GetEffectiveAttributeValue(itemID, attributeID)
        iconID = dogma_data.get_attribute_icon_id(attributeID)
        displayName = dogma_data.get_attribute_display_name(attributeID)
        text = (localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/TractorBeamTractorVelocity', maxTractorVel=maxTractorVel, attributeName=displayName),)
        self.AddRowWithIconAndText(text=text, iconID=iconID)

    def AddDamageControlInfo(self, itemID, chargeInfoItem):
        shieldDamageTypeAttributes = [const.attributeShieldEmDamageResonance,
         const.attributeShieldExplosiveDamageResonance,
         const.attributeShieldKineticDamageResonance,
         const.attributeShieldThermalDamageResonance]
        armorDamageTypeAttributes = [const.attributeArmorEmDamageResonance,
         const.attributeArmorExplosiveDamageResonance,
         const.attributeArmorKineticDamageResonance,
         const.attributeArmorThermalDamageResonance]
        hullDamageTypeAttributes = [const.attributeHullEmDamageResonance,
         const.attributeHullExplosiveDamageResonance,
         const.attributeHullKineticDamageResonance,
         const.attributeHullThermalDamageResonance]
        for damageTypeAttributes, texturePath, headerText in ((shieldDamageTypeAttributes, 'res:/UI/Texture/Icons/1_64_13.png', 'UI/Inflight/ModuleRacks/Tooltips/ShieldDamageResistanceHeader'), (armorDamageTypeAttributes, 'res:/UI/Texture/Icons/1_64_9.png', 'UI/Inflight/ModuleRacks/Tooltips/ArmorDamageResistanceHeader'), (hullDamageTypeAttributes, 'res:/UI/Texture/Icons/2_64_12.png', 'UI/Inflight/ModuleRacks/Tooltips/HullDamageResistanceHeader')):
            attributeValues = self.GetAttributesValues(itemID, 1, damageTypeAttributes, includeZeros=True)
            self.AddRowAndHeaderForManyAttributes(attributeValues=attributeValues, manyAttributesText='UI/Inflight/ModuleRacks/Tooltips/ResistanceActiveBonusValues', headerText=headerText, texturePath=texturePath)

    def AddArmorResistanceShiftHardenerInfo(self, itemID, chargeInfoItem):
        damageTypeAttributes = [const.attributeArmorEmDamageResonance,
         const.attributeArmorExplosiveDamageResonance,
         const.attributeArmorKineticDamageResonance,
         const.attributeArmorThermalDamageResonance]
        attributeValues = self.GetAttributesValues(itemID, 1, damageTypeAttributes, includeZeros=True)
        self.AddRowAndHeaderForManyAttributes(attributeValues=attributeValues, manyAttributesText='UI/Inflight/ModuleRacks/Tooltips/ResistanceActiveBonusValues', headerText='UI/Inflight/ModuleRacks/Tooltips/ArmorDamageResistanceHeader', texturePath='')

    def AddSuperWeaponInfo(self, itemID, chargeInfoItem):
        for attributeID in const.damageTypeAttributes:
            damage = self.GetEffectiveAttributeValue(itemID, attributeID)
            if damage == 0:
                continue
            self.AddAttributeInfoWithAttributeName(itemID=itemID, attributeID=attributeID, labelPath='UI/Inflight/ModuleRacks/Tooltips/SuperWeaponDamage')

        self.AddDurationCountdownTimes(itemID)

    def AddGangCoordinatorInfo(self, itemID, chargeInfoItem):
        commandBonus = self.GetEffectiveAttributeValue(itemID, const.attributeCommandbonus)
        if commandBonus != 0:
            displayName = dogma_data.get_attribute_display_name(const.attributeCommandbonus)
            text = localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/GangCoordinatorCommandBonus', commandBonus=commandBonus, attributeName=displayName)
            self.AddRowWithIconAndText(text=text, texturePath='')
        maxGangModulesAttrName = dogma_data.get_attribute_name(const.attributeMaxGangModules)
        if maxGangModulesAttrName in self.stateManager.GetAttributes(itemID):
            maxGangModules = self.GetEffectiveAttributeValue(itemID, const.attributeMaxGangModules)
            displayName = dogma_data.get_attribute_display_name(const.attributeMaxGangModules)
            text = localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/GangCoordinatorMaxCommandRelays', maxGangModules=maxGangModules, attributeName=displayName)
            self.AddRowWithIconAndText(text=text, texturePath='')

    def AddStructureDefenseBatteryInfo(self, itemID, chargeInfoItem):
        self.AddDamageTypes(itemID, chargeInfoItem, 1)

    def AddScanProbeLauncherInfo(self, itemID, chargeInfoItem):
        if chargeInfoItem:
            self.AddAttributeInfoWithAttributeName(itemID=chargeInfoItem.itemID, attributeID=const.attributeBaseSensorStrength, labelPath='UI/Inflight/ModuleRacks/Tooltips/ScanProbeSensorStrength')

    def AddCynoInfo(self, itemID, chargInfoItem):
        self.AddDurationCountdownTimes(itemID)

    def AddSiegeInfo(self, itemID, chargInfoItem):
        self.AddDurationCountdownTimes(itemID)

    def AddDotWeaponInfo(self, itemID, chargeInfoItem):
        if chargeInfoItem:
            GAV = self.dogmaLocation.GetAccurateAttributeValue
            dotMaxDamagePerTick = GetDotDps(chargeInfoItem.itemID, itemID, GAV)
            text = localization.GetByLabel('UI/Inflight/ModuleRacks/DamagePerSecond', dps=dotMaxDamagePerTick)
            self.AddRowWithIconAndText(text=text, iconID=appConst.iconBreacherPod)
            attributeID = const.attributeDotDuration
            durationText = self.GetDuration(chargeInfoItem.itemID, attributeID)
            displayName = dogma_data.get_attribute_display_name(attributeID)
            text = localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/DotEffectDuration', attributeName=displayName, duration=durationText)
            self.AddRowWithIconAndText(text=text, iconID=dogma_data.get_attribute_icon_id(attributeID))

    def AddTrackingSpeed(self, itemID):
        self.AddAttributeInfoWithAttributeName(itemID=itemID, attributeID=const.attributeTrackingSpeed, labelPath='UI/Inflight/ModuleRacks/Tooltips/WeaponAccuracyScore', skipZeroValue=True)

    def AddCountDownTimes(self, itemID):
        self._AddCountDownTimes(itemID, const.attributeModuleReactivationDelay, self.stateManager.GetCooldownTimes)
        self._AddCountDownTimes(itemID, const.attributeReloadTime, self.stateManager.GetReloadTimes)

    def AddDurationCountdownTimes(self, itemID):
        self._AddCountDownTimes(itemID, const.attributeDuration, self._GetDurationTimeLeft)

    def _AddCountDownTimes(self, itemID, attributeID, getTimeFunc):
        if GetActiveShip() != self.dogmaLocation.GetCurrentShipID():
            return
        itemCountdown = self.dogmaLocation.GetAccurateAttributeValue(itemID, attributeID)
        if not itemCountdown:
            return
        coundDownTimes = getTimeFunc(itemID)
        valueText = self._GetCountdownTime(coundDownTimes)
        if not valueText:
            return
        text = dogma_data.get_attribute_display_name(attributeID)
        self.AddRowWithIconAndTextAndValue(text=text, valueText=valueText, texturePath='')

    def _GetCountdownTime(self, countdownTimes):
        if countdownTimes is None:
            return
        startTime, delayTime = countdownTimes
        now = gametime.GetSimTime()
        finishTime = startTime + delayTime * const.MSEC
        diff = finishTime - now
        if diff < 0:
            return
        return FormatTimeIntervalShort(long(diff), showFrom='minute')

    def _GetDurationTimeLeft(self, itemID):
        return self.stateManager.GetDurationTimeLeft(itemID, self.moduleInfoItem.typeID)

    def GetTimeLeftRepairingCountDown(self, timeLeft):
        valueText = FormatTimeIntervalShort(long(timeLeft), showFrom='minute')
        text = localization.GetByLabel('UI/Inflight/ModuleRacks/Tooltips/RepairTimeLeft')
        self.AddRowWithIconAndTextAndValue(text=text, valueText=valueText, texturePath='')

    def GetTotalDamageWhileRepairing(self, itemID, showSingleModuleReadout = True):
        dogmaLocation = self.dogmaLocation
        currentShipID = dogmaLocation.GetCurrentShipID()
        masterID = dogmaLocation.IsInWeaponBank(currentShipID, itemID)
        if masterID and not showSingleModuleReadout:
            allModulesInBank = dogmaLocation.GetModulesInBank(currentShipID, masterID)
        else:
            allModulesInBank = [itemID]
        maxDamage = 0
        maxTimeLeft = 0
        newNow = blue.os.GetSimTime()
        rateOfRepairInMin = self.stateManager.GetAttribute(session.charid, 'moduleRepairRate')
        rateOfRepair = const.MIN / rateOfRepairInMin
        for eachModuleID in allModulesInBank:
            repairStartTimeStamp = self.stateManager.GetRepairTimeStamp(eachModuleID)
            if not repairStartTimeStamp:
                continue
            moduleDamage = dogmaLocation.GetAccurateAttributeValue(eachModuleID, const.attributeDamage)
            repairTime = int(moduleDamage * rateOfRepair)
            timeLeft = max(0, repairStartTimeStamp + repairTime - newNow)
            damageLeftToRepair = timeLeft / float(repairTime)
            currentDamgeOnModule = moduleDamage * damageLeftToRepair
            maxDamage = max(currentDamgeOnModule, maxDamage)
            maxTimeLeft = max(timeLeft, maxTimeLeft)

        return (maxDamage, maxTimeLeft)
