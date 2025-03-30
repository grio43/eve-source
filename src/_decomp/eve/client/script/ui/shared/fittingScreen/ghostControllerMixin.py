#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\ghostControllerMixin.py
import signals
from carbon.common.script.util.timerstuff import AutoTimer
from corruptionsuppression.client.systemEffectsClient import CorruptionWarpSpeedIncreaserCheckerClient
from crimewatch.util import GetKillReportHashValue
from dogma import const as dogmaConst
from eve.client.script.ui.shared.fitting.fittingUtil import GHOST_FITTABLE_CATEGORIES, ModifiedAttribute, GetEffectiveHp, CanFitFromSourceLocation, GetAlignTimeForShip
import evetypes
from eve.client.script.ui.shared.fittingScreen.tryFit import TryFitter, FAKE_ITEM_GUID, FAKE_ITEM_LOCATION_GUID
from eve.common.script.util.eveCommonUtils import GetKillMailInfo
from inventorycommon.util import IsSubsystemFlagVisible
from shipfitting.droneUtil import GetDroneBandwidth
from shipfitting.fittingDogmaLocationUtil import CapacitorSimulator, GetFuelUsage, GetAllDpsInfo, GetAlphaStrike, GetTotalFighterDps, GetFullAndPartialSquadrons
EFFECTIVE_HP = 'effectiveHp'
ALIGN_TIME = 'alignTime'
FUEL_USAGE = 'fuelUsage'
ALPHA_STRIKE = 'alphaStrike'
CAP_DELTA = 'delta'
CAP_DELTA_PERCENTAGE = 'deltaPercentage'
LOAD_BALANCE = 'loadBalance'
TTL = 'TTL'
PASSIVE_RECHARGE = 'passiveRecharge'
TOTAL_DPS = 'totalDps'
TOTAL_DPS_WITH_RELOAD = 'totalDpsWithReload'
FIGHTER_DPS = 'fighterDps'
FIGHTER_FULL = 'fighterFullSquadrons'
FIGHTER_PARTIAL = 'fighterPartialSquadrons'
ACTIVE_DRONES = 'activeDrones'
DRONE_BANDWITH_USAGE = 'droneBandwithUsage'
DRONE_BANDWITH = 'droneBandwidth'
DRONE_DPS = 'droneDps'

class GhostControllerMixin(object):
    __notifyevents__ = []

    def __init__(self, itemID, typeID = None):
        self.actuallyFittedSubsystemInfo = None
        self.on_slots_changed = signals.Signal(signalName='on_slots_changed')
        self.on_simulation_state_changed = signals.Signal(signalName='on_simulation_state_changed')
        self.on_gauge_preview_changed = signals.Signal(signalName='on_gauge_preview_changed')
        self.on_drone_bay_open = signals.Signal(signalName='on_drone_bay_open')
        self.attributesBeforePreviewfitting = {}
        self.previewItemThread = None
        self.previewItemPending = None

    def OnFittingSlotsChanged(self, *args):
        self.on_slots_changed()
        self._UpdateSlots()

    def OnSubSystemsChanged(self, *args):
        self.on_subsystem_fitted(animate=False)

    def OnSubSystemsReallyChanged(self):
        slotsToOffline = []
        for eachSlotController in self.slotsByFlagID.itervalues():
            if eachSlotController.GetModule() and not eachSlotController.IsOnlineable() and eachSlotController.IsOnline():
                slotsToOffline.append(eachSlotController.GetFlagID())

        if slotsToOffline:
            sm.GetService('ghostFittingSvc').OfflineSlotList(slotsToOffline)
        self.on_subsystem_really_changed()

    def OnSimulatedShipLoaded(self, itemID, typeID = None):
        self.SetDogmaLocation()
        self.UpdateItem(itemID, typeID)

    def IsSimulated(self):
        return self.isShipSimulated

    def SetSimulationState(self, simulationOn = False):
        self.isShipSimulated = simulationOn

    def SetPreviewFittedItem(self, ghostItem = None, force = False):
        self.previewItemPending = ghostItem
        if force:
            if self.previewItemThread:
                self.previewItemThread.KillTimer()
            self._SetPreviewFittedItem()
        elif not self.previewItemThread:
            self.previewItemThread = AutoTimer(100, self._SetPreviewFittedItem)

    def _SetPreviewFittedItem(self):
        self.previewItemThread = None
        ghostItem = self.previewItemPending
        self.ResetPreviewItemInfo()
        if ghostItem and evetypes.GetCategoryID(ghostItem.typeID) not in GHOST_FITTABLE_CATEGORIES:
            return
        dogmaItem = None
        previouslyFitted = self.actuallyFittedSubsystemInfo
        if ghostItem:
            desiredFlag = int(self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(ghostItem.typeID, dogmaConst.attributeSubSystemSlot))
            isSubsystemFlag = IsSubsystemFlagVisible(desiredFlag)
            if isSubsystemFlag:
                self.TryFitPreviouslyFittedType(previouslyFitted)
            self.attributesBeforePreviewfitting = self.GetCurrentAttributeValues()
            if isSubsystemFlag:
                self.RemoveModuleAndRememberIt(desiredFlag)
            dogmaItem = self.ghostFittingExtension.PreviewFitItem(ghostItem)
        else:
            self.actuallyFittedSubsystemInfo = None
            self.TryFitPreviouslyFittedType(previouslyFitted)
            sm.GetService('ghostFittingSvc').SendOnFeedbackTextChanged(None)
        self.previewFittedItem = dogmaItem
        self.on_item_ghost_fitted()
        self.on_stats_changed()

    def RemoveModuleAndRememberIt(self, desiredFlag, *args):
        dogmaItem = self.dogmaLocation.GetSubSystemInFlag(None, desiredFlag)
        if dogmaItem:
            if not getattr(dogmaItem, 'isPreviewItem', False):
                self.actuallyFittedSubsystemInfo = (desiredFlag, dogmaItem.typeID)
            self.ghostFittingExtension.UnFitItem(dogmaItem)

    def ResetPreviewItemInfo(self):
        self.attributesBeforePreviewfitting = {}
        self.RemovePreviewItem()

    def RemovePreviewItem(self):
        if self.previewFittedItem:
            dogmaItem = self.dogmaLocation.SafeGetDogmaItem(self.previewFittedItem.itemID)
            if dogmaItem and getattr(dogmaItem, 'isPreviewItem', False):
                self.ghostFittingExtension.UnFitItem(dogmaItem)

    def TryFitPreviouslyFittedType(self, previouslyFitted):
        if not previouslyFitted:
            return
        flagID, moduleTypeID = previouslyFitted
        dogmaItemInSlot = self.dogmaLocation.GetSubSystemInFlag(None, flagID)
        if not dogmaItemInSlot or getattr(dogmaItemInSlot, 'isPreviewItem', False):
            shipID = self.dogmaLocation.GetCurrentShipID()
            dogmaItem, errorInfo = sm.GetService('ghostFittingSvc').FitModuleToShipAndChangeState(shipID, flagID, moduleTypeID, ignoreSubsystemChange=True)
        self.actuallyFittedSubsystemInfo = None

    def OnSimulationStateChanged(self):
        self.on_simulation_state_changed()

    def OnPreviewCPU(self, cpuValue, powergridValue, calibrationValue):
        self.on_gauge_preview_changed(cpuValue, powergridValue, calibrationValue)

    def OpenFakeDroneBay(self, *args):
        self.on_drone_bay_open()

    def OpenFakeFighterBay(self, *args):
        self.on_drone_bay_open()

    def OnDropData(self, dragObj, nodes):
        if not nodes:
            return
        if not CanFitFromSourceLocation(nodes):
            return
        recs = []
        fakeRecs = []
        for node in nodes:
            guid = getattr(node, '__guid__', None)
            if getattr(node, 'rec', None):
                recs.append(node.rec)
            elif guid in FAKE_ITEM_GUID:
                fakeRecs.append(node)
            elif guid in FAKE_ITEM_LOCATION_GUID and getattr(node, 'typeID', None):
                if evetypes.GetCategoryID(node.typeID) == const.categoryStructure:
                    fakeRecs.append(node)

        if recs or fakeRecs:
            return TryFitter().TryFit(recs, fakeRecs, self, self.GetItemID())
        firstNode = nodes[0]
        firstNodeGuid = getattr(firstNode, '__guid__', None)
        if firstNodeGuid == 'listentry.FittingEntry':
            fitting = firstNode.fitting
            sm.GetService('ghostFittingSvc').SimulateFitting(fitting)
        elif firstNodeGuid == 'listentry.KillMail':
            hashValue = GetKillReportHashValue(node.mail)
            self._SimulateFittingFromKillReport(node.mail.killID, hashValue)
        elif firstNodeGuid == 'TextLink':
            url = node.url
            if url.startswith('killReport:'):
                killID, hashValue = url.split(':')[1:]
                killID = int(killID)
                self._SimulateFittingFromKillReport(killID, hashValue)
            elif url.startswith('fitting:'):
                fittingString = url[len('fitting:'):]
                fitting, truncated = sm.StartService('fittingSvc').GetFittingFromString(fittingString)
                self._SimulateFitting(fitting)

    def _SimulateFittingFromKillReport(self, killID, hashValue):
        kill = sm.RemoteSvc('warStatisticMgr').GetKillMail(killID, hashValue)
        _, items = GetKillMailInfo(kill)
        fitting = sm.GetService('fittingSvc').GetFittingFromItems(kill.victimShipTypeID, items)
        self._SimulateFitting(fitting)

    def _SimulateFitting(self, fitting):
        from eve.client.script.ui.services.menuSvcExtras.openFunctions import SimulateFitting
        SimulateFitting(fitting)

    def GetCurrentAttributeValues(self):
        delta, deltaPercentage, loadBalance, TTL_value = self._GetCapSimulatorValues()
        activeDroneNumInfo, droneBandwidthUsageInfo, droneDpsInfo = self.GetDroneInfo()
        fullInfo, partialInfo = self.GetFullAndPartialSquadrons()
        attributeValueDict = {dogmaConst.attributeScanResolution: self.GetScanResolution().value,
         dogmaConst.attributeMaxTargetRange: self.GetMaxTargetRange().value,
         dogmaConst.attributeMaxLockedTargets: self.GetMaxTargets().value,
         dogmaConst.attributeSignatureRadius: self.GetSignatureRadius().value,
         dogmaConst.attributeScanRadarStrength: self.GetScanRadarStrength().value,
         dogmaConst.attributeScanMagnetometricStrength: self.GetScanMagnetometricStrength().value,
         dogmaConst.attributeScanGravimetricStrength: self.GetScanGravimetricStrength().value,
         dogmaConst.attributeScanLadarStrength: self.GetScanLadarStrength().value,
         dogmaConst.attributeMass: self.GetMass().value,
         dogmaConst.attributeAgility: self.GetAgility().value,
         dogmaConst.attributeBaseWarpSpeed: self.GetBaseWarpSpeed().value,
         dogmaConst.attributeWarpSpeedMultiplier: self.GetWarpSpeedMultiplier().value,
         dogmaConst.attributeMaxVelocity: self.GetMaxVelocity().value,
         dogmaConst.attributeCpuLoad: self.GetCPULoad().value,
         dogmaConst.attributeCpuOutput: self.GetCPUOutput().value,
         dogmaConst.attributePowerLoad: self.GetPowerLoad().value,
         dogmaConst.attributePowerOutput: self.GetPowerOutput().value,
         dogmaConst.attributeUpgradeLoad: self.GetCalibrationLoad().value,
         dogmaConst.attributeUpgradeCapacity: self.GetCalibrationOutput().value,
         dogmaConst.attributeShieldCapacity: self.GetShieldHp().value,
         dogmaConst.attributeArmorHP: self.GetArmorHp().value,
         dogmaConst.attributeHp: self.GetStructureHp().value,
         dogmaConst.attributeShieldRechargeRate: self.GetRechargeRate().value,
         dogmaConst.attributeShieldEmDamageResonance: self.GetShieldEmDamageResonance().value,
         dogmaConst.attributeShieldExplosiveDamageResonance: self.GetShieldExplosiveDamageResonance().value,
         dogmaConst.attributeShieldKineticDamageResonance: self.GetShieldKineticDamageResonance().value,
         dogmaConst.attributeShieldThermalDamageResonance: self.GetShieldThermalDamageResonance().value,
         dogmaConst.attributeArmorEmDamageResonance: self.GetArmorEmDamageResonance().value,
         dogmaConst.attributeArmorExplosiveDamageResonance: self.GetArmorExplosiveDamageResonance().value,
         dogmaConst.attributeArmorKineticDamageResonance: self.GetArmorKineticDamageResonance().value,
         dogmaConst.attributeArmorThermalDamageResonance: self.GetArmorThermalDamageResonance().value,
         dogmaConst.attributeEmDamageResonance: self.GetStructureEmDamageResonance().value,
         dogmaConst.attributeExplosiveDamageResonance: self.GetStructureExplosiveDamageResonance().value,
         dogmaConst.attributeKineticDamageResonance: self.GetStructureKineticDamageResonance().value,
         dogmaConst.attributeThermalDamageResonance: self.GetStructureThermalDamageResonance().value,
         dogmaConst.attributeDroneControlDistance: self.GetDroneControlRange().value,
         dogmaConst.attributeCapacity: self.GetCargoCapacity().value,
         dogmaConst.attributeDroneCapacity: self.GetDroneCapacity().value,
         dogmaConst.attributeCapacitorCapacity: self.GetCapacitorCapacity().value,
         dogmaConst.attributeRechargeRate: self.GetCapRechargeRate().value,
         CAP_DELTA: delta,
         CAP_DELTA_PERCENTAGE: deltaPercentage,
         LOAD_BALANCE: loadBalance,
         TTL: TTL_value,
         EFFECTIVE_HP: self.GetEffectiveHp().value,
         ALIGN_TIME: self.GetAlignTime().value,
         FUEL_USAGE: self.GetFuelUsage().value,
         PASSIVE_RECHARGE: self.GetPassiveRechargeRate().value,
         TOTAL_DPS: self.GetTotalDps().value,
         TOTAL_DPS_WITH_RELOAD: self.GetTotalDpsWithReload().value,
         ALPHA_STRIKE: self.GetAlphaStrike().value,
         ACTIVE_DRONES: activeDroneNumInfo.value,
         DRONE_BANDWITH: self.GetDroneBandwidth().value,
         DRONE_BANDWITH_USAGE: droneBandwidthUsageInfo.value,
         DRONE_DPS: droneDpsInfo.value,
         FIGHTER_DPS: self.GetFighterDps().value,
         FIGHTER_FULL: fullInfo.value,
         FIGHTER_PARTIAL: partialInfo.value}
        return attributeValueDict

    def GetScanResolution(self):
        return self.GetStatsInfo(dogmaConst.attributeScanResolution)

    def GetMaxTargetRange(self):
        return self.GetStatsInfo(dogmaConst.attributeMaxTargetRange)

    def GetMaxTargets(self):
        return self.GetStatsInfo(dogmaConst.attributeMaxLockedTargets)

    def GetSignatureRadius(self):
        return self.GetStatsInfo(dogmaConst.attributeSignatureRadius, higherIsBetter=False)

    def GetScanRadarStrength(self):
        return self.GetStatsInfo(dogmaConst.attributeScanRadarStrength)

    def GetScanMagnetometricStrength(self):
        return self.GetStatsInfo(dogmaConst.attributeScanMagnetometricStrength)

    def GetScanGravimetricStrength(self):
        return self.GetStatsInfo(dogmaConst.attributeScanGravimetricStrength)

    def GetScanLadarStrength(self):
        return self.GetStatsInfo(dogmaConst.attributeScanLadarStrength)

    def GetMass(self):
        return self.GetStatsInfo(dogmaConst.attributeMass, higherIsBetter=False)

    def GetAgility(self):
        return self.GetStatsInfo(dogmaConst.attributeAgility, higherIsBetter=False)

    def GetBaseWarpSpeed(self):
        return self.GetStatsInfo(dogmaConst.attributeBaseWarpSpeed)

    def GetWarpSpeedMultiplier(self):
        return self.GetStatsInfo(dogmaConst.attributeWarpSpeedMultiplier)

    def GetMaxVelocity(self):
        return self.GetStatsInfo(dogmaConst.attributeMaxVelocity)

    def GetCPULoad(self):
        return self.GetStatsInfo(dogmaConst.attributeCpuLoad, higherIsBetter=False)

    def GetCPUOutput(self):
        return self.GetStatsInfo(dogmaConst.attributeCpuOutput)

    def GetPowerLoad(self):
        return self.GetStatsInfo(dogmaConst.attributePowerLoad, higherIsBetter=False)

    def GetPowerOutput(self):
        return self.GetStatsInfo(dogmaConst.attributePowerOutput)

    def GetCalibrationLoad(self):
        return self.GetStatsInfo(dogmaConst.attributeUpgradeLoad, higherIsBetter=False)

    def GetCalibrationOutput(self):
        return self.GetStatsInfo(dogmaConst.attributeUpgradeCapacity)

    def GetShieldHp(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldCapacity)

    def GetArmorHp(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorHP)

    def GetStructureHp(self):
        return self.GetStatsInfo(dogmaConst.attributeHp)

    def GetRechargeRate(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldRechargeRate)

    def GetShieldEmDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldEmDamageResonance, higherIsBetter=False)

    def GetShieldExplosiveDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldExplosiveDamageResonance, higherIsBetter=False)

    def GetShieldKineticDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldKineticDamageResonance, higherIsBetter=False)

    def GetShieldThermalDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldThermalDamageResonance, higherIsBetter=False)

    def GetArmorEmDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorEmDamageResonance, higherIsBetter=False)

    def GetArmorExplosiveDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorExplosiveDamageResonance, higherIsBetter=False)

    def GetArmorKineticDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorKineticDamageResonance, higherIsBetter=False)

    def GetArmorThermalDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorThermalDamageResonance, higherIsBetter=False)

    def GetStructureEmDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeEmDamageResonance, higherIsBetter=False)

    def GetStructureExplosiveDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeExplosiveDamageResonance, higherIsBetter=False)

    def GetStructureKineticDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeKineticDamageResonance, higherIsBetter=False)

    def GetStructureThermalDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeThermalDamageResonance, higherIsBetter=False)

    def GetCargoCapacity(self):
        return self.GetStatsInfo(dogmaConst.attributeCapacity)

    def GetDroneCapacity(self):
        return self.GetStatsInfo(dogmaConst.attributeDroneCapacity)

    def GetCapacitorCapacity(self):
        return self.GetStatsInfo(dogmaConst.attributeCapacitorCapacity)

    def GetCapRechargeRate(self):
        return self.GetStatsInfo(dogmaConst.attributeRechargeRate, higherIsBetter=False)

    def GetFighterCapacity(self):
        return self.GetStatsInfo(dogmaConst.attributeFighterCapacity)

    def GetStatsInfo(self, attributeID, higherIsBetter = True):
        oldValue = self.attributesBeforePreviewfitting.get(attributeID, None)
        currentValue = self.GetAttribute(attributeID)
        currentValue = round(currentValue, 10)
        return ModifiedAttribute(value=currentValue, oldValue=oldValue, higherIsBetter=higherIsBetter, attributeID=attributeID)

    def GetEffectiveHp(self):
        oldValue = self.attributesBeforePreviewfitting.get(EFFECTIVE_HP, None)
        currentValue = GetEffectiveHp(self)
        return ModifiedAttribute(value=currentValue, oldValue=oldValue)

    def GetAlignTime(self):
        oldValue = self.attributesBeforePreviewfitting.get(ALIGN_TIME, None)
        currentValue = GetAlignTimeForShip(self.dogmaLocation)
        return ModifiedAttribute(value=currentValue, oldValue=oldValue, higherIsBetter=False)

    def GetFuelUsage(self):
        oldValue = self.attributesBeforePreviewfitting.get(FUEL_USAGE, None)
        currentValue = GetFuelUsage(self.dogmaLocation)
        return ModifiedAttribute(value=currentValue, oldValue=oldValue, higherIsBetter=False)

    def GetPassiveRechargeRate(self):
        oldValue = self.attributesBeforePreviewfitting.get(PASSIVE_RECHARGE, None)
        shieldCapacity = self.GetAttribute(dogmaConst.attributeShieldCapacity)
        shieldRR = self.GetAttribute(dogmaConst.attributeShieldRechargeRate)
        hpPerSec = int(2.5 * shieldCapacity / (shieldRR / 1000.0))
        return ModifiedAttribute(value=hpPerSec, oldValue=oldValue)

    def _GetCapSimulatorValues(self):
        dogmaLocation = self.dogmaLocation
        peakRechargeRate, totalCapNeed, loadBalance, TTL_value = CapacitorSimulator(dogmaLocation, dogmaLocation.GetCurrentShipID())
        delta = round((peakRechargeRate - totalCapNeed) * 1000, 2)
        deltaPercentage = round((peakRechargeRate - totalCapNeed) / peakRechargeRate * 100, 1)
        return (delta,
         deltaPercentage,
         loadBalance,
         TTL_value)

    def GetCapSimulatorInfos(self):
        delta, deltaPercentage, loadBalance, TTL_value = self._GetCapSimulatorValues()
        oldValue = self.attributesBeforePreviewfitting.get(CAP_DELTA, None)
        deltaInfo = ModifiedAttribute(value=delta, oldValue=oldValue)
        oldValue = self.attributesBeforePreviewfitting.get(CAP_DELTA_PERCENTAGE, None)
        deltaPercentageInfo = ModifiedAttribute(value=deltaPercentage, oldValue=oldValue)
        oldValue = self.attributesBeforePreviewfitting.get(LOAD_BALANCE, None)
        loadBalanceInfo = ModifiedAttribute(value=loadBalance, oldValue=oldValue)
        oldValue = self.attributesBeforePreviewfitting.get(TTL, None)
        ttlInfo = ModifiedAttribute(value=TTL_value or 0, oldValue=oldValue)
        return [deltaInfo,
         deltaPercentageInfo,
         loadBalanceInfo,
         ttlInfo]

    def GetTotalDps(self):
        oldValue = self.attributesBeforePreviewfitting.get(TOTAL_DPS, None)
        allDpsInfo = self._GetAllDpsInfo()
        totalDps = allDpsInfo.totalDps
        return ModifiedAttribute(value=totalDps, oldValue=oldValue)

    def GetTotalDpsWithReload(self):
        oldValue = self.attributesBeforePreviewfitting.get(TOTAL_DPS_WITH_RELOAD, None)
        allDpsInfo = self._GetAllDpsInfo()
        totalDpsWithReload = allDpsInfo.totalDpsWithReload
        return ModifiedAttribute(value=totalDpsWithReload, oldValue=oldValue)

    def _GetAllDpsInfo(self):
        dogmaLocation = self.dogmaLocation
        shipID = dogmaLocation.GetCurrentShipID()
        allDpsInfo = GetAllDpsInfo(shipID, dogmaLocation)
        return allDpsInfo

    def GetAlphaStrike(self):
        oldValue = self.attributesBeforePreviewfitting.get(ALPHA_STRIKE, None)
        alphaStrike = GetAlphaStrike(self.dogmaLocation)
        return ModifiedAttribute(value=alphaStrike, oldValue=oldValue)

    def GetDroneInfo(self):
        activeDrones = self.dogmaLocation.GetActiveDrones()
        activeDroneNumInfo = self._GetActiveDronesNum(activeDrones)
        droneBandwidthUsageInfo = self._GetDroneBandWidthUsage(activeDrones)
        droneDpsInfo = self._GetDroneDps(activeDrones)
        return (activeDroneNumInfo, droneBandwidthUsageInfo, droneDpsInfo)

    def _GetActiveDronesNum(self, activeDrones):
        oldValue = self.attributesBeforePreviewfitting.get(ACTIVE_DRONES, None)
        numActiveDrones = sum((qty for qty in activeDrones.itervalues()))
        return ModifiedAttribute(value=numActiveDrones, oldValue=oldValue)

    def _GetDroneBandWidthUsage(self, activeDrones):
        oldValue = self.attributesBeforePreviewfitting.get(DRONE_BANDWITH_USAGE, None)
        shipID = self.dogmaLocation.GetCurrentShipID()
        bandwidthUsed, _ = GetDroneBandwidth(shipID, self.dogmaLocation, activeDrones)
        return ModifiedAttribute(value=bandwidthUsed, oldValue=oldValue, higherIsBetter=False)

    def _GetDroneDps(self, activeDrones):
        oldValue = self.attributesBeforePreviewfitting.get(DRONE_DPS, None)
        shipID = self.dogmaLocation.GetCurrentShipID()
        droneDps, _ = self.dogmaLocation.GetOptimalDroneDamage2(shipID, activeDrones)
        return ModifiedAttribute(value=droneDps, oldValue=oldValue)

    def GetDroneBandwidth(self):
        return self.GetStatsInfo(dogmaConst.attributeDroneBandwidth)

    def GetDroneControlRange(self):
        attributeID = const.attributeDroneControlDistance
        oldValue = self.attributesBeforePreviewfitting.get(attributeID, None)
        currentValue = self.dogmaLocation.GetAttributeValue(session.charid, attributeID)
        return ModifiedAttribute(value=currentValue, oldValue=oldValue, attributeID=attributeID)

    def GetFighterDps(self):
        totalFighterDps = GetTotalFighterDps(self.dogmaLocation)
        oldValue = self.attributesBeforePreviewfitting.get(FIGHTER_DPS, None)
        return ModifiedAttribute(value=totalFighterDps, oldValue=oldValue)

    def GetFullAndPartialSquadrons(self):
        full, partial = GetFullAndPartialSquadrons(self.dogmaLocation)
        oldValueFull = self.attributesBeforePreviewfitting.get(FIGHTER_FULL, None)
        oldValuePartial = self.attributesBeforePreviewfitting.get(FIGHTER_PARTIAL, None)
        return (ModifiedAttribute(value=full, oldValue=oldValueFull), ModifiedAttribute(value=partial, oldValue=oldValuePartial))

    def GetCorruptionWarpSpeedIncrease(self):
        corruptionWarpSpeedChecker = CorruptionWarpSpeedIncreaserCheckerClient(session.solarsystemid2)
        corruptionWarpSpeedIncrease = corruptionWarpSpeedChecker.GetWarpSpeedIncrease(session.warfactionid)
        return corruptionWarpSpeedIncrease
