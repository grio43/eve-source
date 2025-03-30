#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingDogmaLocation.py
import weakref
import dbuff.common.registry
import dogma.data as dogma_data
import dynamicitemattributes
import threadutils
from carbon.common.lib import telemetry
from dogma.attributes.limit import LimitAttributeOnItem
from dogma.dogmaWrappers import WrappedMethod
from dogma.effects.environment import Environment
from dogma.items.baseDogmaItem import BaseDogmaItem
from dogma.items.fighterDogmaItem import GhostFighterDogmaItem
from dogma.items.structureDogmaItem import GhostStructureDogmaItem
from dogma.items.structureModuleDogmaItem import GhostStructureModuleDogmaItem
from eve.client.script.ui.shared.fitting.fittingUtil import GetSensorStrengthAttribute, GetFighterNumByTypeIDsInTubes
from eve.client.script.ui.shared.fittingScreen import FAKE_FLAGID
from eve.client.script.ui.shared.fittingScreen.ghostFittingUtil import GhostFittingDataObject, GetOriganlItemIDFromItemKey
from eve.client.script.ui.shared.fittingScreen.moduleStateUtil import GetTextForCurrentStateForDogmaItem
from eve.common.script.dogma.baseDogmaLocation import BaseDogmaLocation
from dogma.items.droneDogmaItem import GhostDroneDogmaItem
from dogma.items.moduleDogmaItem import GhostModuleDogmaItem
from dogma.items.shipDogmaItem import GhostShipDogmaItem
from eveuniverse.security import securityClassZeroSec
import inventorycommon.const as invConst
from inventorycommon.util import IsShipFittable, IsStructureFittable, IsFighterTubeFlag
from shipfitting.fittingDogmaLocationUtil import GetFittingItemDragData, GetTurretMissileAndAoeDps, CapacitorSimulator, GetAlphaStrike
from shipfitting.droneUtil import GetOptimalDroneDamage, SelectedDroneTracker
import uthread
import log
import blue
from shipfitting.fittingStuff import IsRigSlot
from utillib import KeyVal
MAX_CARGO = 2000000000
BURST_EFFECTS = [const.effectModuleBonusIndustrialInvulnerability,
 const.effectModuleTitanBurst,
 const.effectModuleBonusWarfareLinkArmor,
 const.effectModuleBonusWarfareLinkInfo,
 const.effectModuleBonusWarfareLinkMining,
 const.effectModuleBonusWarfareLinkShield,
 const.effectModuleBonusWarfareLinkSkirmish,
 const.effectChargeBonusWarfareCharge]
SPEED_ATTRIBUTES_REQUIRING_MODULE_UPDATE = {const.attributeSpeedFactor}
SPEED_CHANGING_EFFECTS = {const.effectModuleBonusAfterburner, const.effectModuleBonusMicrowarpdrive}

class FittingDogmaLocation(BaseDogmaLocation):
    __notifyevents__ = ['OnServerBrainUpdated']

    def __init__(self, broker, charBrain = None):
        BaseDogmaLocation.__init__(self, broker)
        self.manualEffectCategories = {const.dgmEffActivation: True,
         const.dgmEffTarget: True,
         const.dgmEffArea: True}
        self.godma = sm.GetService('godma')
        self.scatterAttributeChanges = True
        self.dogmaStaticMgr = sm.GetService('clientDogmaStaticSvc')
        self.effectCompiler = sm.GetService('ghostFittingEffectCompiler')
        self.instanceFlagQuantityCache = {}
        self.effectRefreshInfo = []
        self.shipID = None
        self.SetEffectsNeedingRefreshDict()
        self.InitDbuffRegistry()
        self.brain = None
        self.shipIDBeingDisembarked = None
        if charBrain:
            self.SetBrainData(session.charid, charBrain)
        self.selectedDronesTracker = SelectedDroneTracker()
        self.locationName = 'FittingDogmaLocation'
        self.RegisterCallback(const.attributeActivationBlocked, self.OnActivationBlockedChanged)
        sm.RegisterNotify(self)

    def InitDbuffRegistry(self):
        modifierApplier = dbuff.common.registry.ModifierApplier(self)
        self.dbuffRegistry = dbuff.common.registry.BuffRegistry(modifierApplier, None, None)

    def SetEffectsNeedingRefreshDict(self):
        self.effectsNeedRefreshDict = {const.attributeMass: SPEED_CHANGING_EFFECTS}

    def SetBrainData(self, charID, brain):
        self.brain = brain

    def GetBrainData(self, charID):
        return self.brain

    def HasBrainData(self, charID):
        return self.brain is not None

    def GetCurrentShipID(self):
        return self.shipID

    def GetActiveShipID(self, characterID = None):
        return self.shipID

    def CheckApplyBrainEffects(self, shipID):
        return self.IsItemIdInDogmaItems(shipID)

    def IsItemIdInDogmaItems(self, itemID):
        return itemID in self.dogmaItems

    def OnServerBrainUpdated(self, brainData):
        self.LogInfo('FittingDogmaLocation:OnServerBrainUpdated received for character %s' % session.charid)
        shipID = self.GetCurrentShipID()
        if shipID is None:
            self.ProcessBrainData(session.charid, brainData)
            return
        with self.brainUpdate.Event(shipID):
            self.RemoveBrainEffects(shipID, session.charid, 'fittingDogmaLocation.OnServerBrainUpdated')
            self.ProcessBrainData(session.charid, brainData)
            self.ApplyBrainEffects(shipID, session.charid, 'fittingDogmaLocation.OnServerBrainUpdated')

    def CheckPowerCpuRequirementForOnlineModules(self, shipID):
        pass

    def LoadMyShip(self, typeID):
        myCharID = session.charid
        self.LoadItem(myCharID)
        s = GhostFittingDataObject(None, 0, typeID)
        itemKey = s.GetItemKey()
        self.LoadItem(itemKey, invItem=s)
        self.pilotsByShipID[itemKey] = myCharID
        shipDogmaItem = self.GetDogmaItem(itemKey)
        charDogmaItem = self.GetDogmaItem(myCharID)
        oldShipID = self.shipID
        self.shipIDBeingDisembarked = oldShipID
        self.ResetOldShip(oldShipID, itemKey)
        self.shipID = itemKey
        charDogmaItem.SetLocation(self.shipID, shipDogmaItem, const.flagPilot)
        self.MakeShipActive(self.shipID, oldShipID)
        return shipDogmaItem

    def ResetOldShip(self, oldShipID, newShipID):
        charID = session.charid
        oldShipItem = self.dogmaItems.get(oldShipID)
        if oldShipItem is None:
            return
        oldShipItem.isBeingDisembarked = True
        try:
            self.RemoveBrainEffects(oldShipID, charID, 'fittingDogmaLocation.ResetOldShip')
            self.UninstallPilotFromShipAndItems(oldShipID)
        finally:
            oldShipItem.isBeingDisembarked = False

        self.selectedDronesTracker.Clear()
        self._RemoveItemsFromHolds()
        oldShipItem.HandlePilotChange(None)
        self.UnfitItemFromLocation(oldShipID, charID)
        self.UnloadItem(oldShipID)

    def _RemoveItemsFromHolds(self):
        self.RemoveAllItemsFromHold(const.flagCargo)
        self.RemoveAllItemsFromHold(const.flagFighterBay)
        for eachHold in const.fighterTubeFlags:
            self.RemoveAllItemsFromHold(eachHold)

    def FitItemToLocation(self, locationID, itemID, flagID):
        if self._IsLocationIDInvalidForFitting(locationID):
            return
        wasItemLoaded = self.IsItemIdInDogmaItems(itemID)
        if not self.IsItemIdInDogmaItems(locationID):
            self.LoadItem(locationID)
            if not wasItemLoaded:
                self.LogInfo('Neither location not item loaded, returning early', locationID, itemID)
                return
        if not self.IsItemIdInDogmaItems(itemID):
            self.LoadItem(itemID)
            return
        locationDogmaItem = self.SafeGetDogmaItem(locationID)
        if locationDogmaItem is None:
            self.LogInfo('FitItemToLocation::Fitted to None item', itemID, locationID, flagID)
            return
        dogmaItem = self.GetDogmaItem(itemID)
        if getattr(dogmaItem, 'IsValidFittingLocation', None) and not dogmaItem.IsValidFittingLocation(locationDogmaItem):
            return
        dogmaItem.SetLocation(locationID, locationDogmaItem, flagID)
        if flagID in invConst.fittingFlags or itemID == self.shipID or flagID == invConst.flagHiddenModifers:
            startedEffects = self.StartPassiveEffects(itemID, dogmaItem.typeID)
        if self.IsCharge(dogmaItem):
            module = self.GetModuleFromShipFlag(flagID)
            if module:
                typeEffectInfo = sm.GetService('ghostFittingSvc').GetDefaultAndOverheatEffect(module.typeID)
                defaultEffectID = typeEffectInfo.defaultEffect.effectID
                self.TryRestartBurstEffects(defaultEffectID, module.typeID)
        if flagID != FAKE_FLAGID:
            sm.GetService('ghostFittingSvc').SendOnStatsUpdatedEvent()

    def UnfitItemFromShip(self, itemID):
        self.selectedDronesTracker.UnregisterDroneFromActive(itemID)
        item = self.SafeGetDogmaItem(itemID)
        if not item:
            return
        if not self.IsCharge(item):
            chargeItem = self.GetChargeFromShipFlag(item.flagID)
            if chargeItem:
                self.UnfitItemFromShip(chargeItem.itemID)
        self.UnfitItemFromLocation(self.shipID, itemID)
        self.UnloadItem(itemID)

    def GetQuantityFromCache(self, locationID, flagID):
        return 1

    def GetInstance(self, item):
        instanceRow = [item.itemID]
        for attributeID in self.GetAttributesByIndex().itervalues():
            v = getattr(item, dogma_data.get_attribute_name(attributeID), 0)
            instanceRow.append(v)

        return instanceRow

    def OnlineModule(self, itemKey):
        self.ChangeModuleStatus(itemKey, const.effectOnline)

    def ActivateModule(self, itemKey, moduleTypeID, flagID):
        if self.IsShipCloaked() and flagID not in const.rigSlotFlags:
            raise UserError('DeniedActivateCloaked')
        typeEffectInfo = sm.GetService('ghostFittingSvc').GetDefaultAndOverheatEffect(moduleTypeID)
        defaultEffectID = typeEffectInfo.defaultEffect.effectID
        self.ChangeModuleStatus(itemKey, defaultEffectID)
        self.TryStartPassiveEffects(itemKey, moduleTypeID, flagID)

    def TryStartPassiveEffects(self, itemID, moduleTypeID, flagID):
        if not IsRigSlot(flagID):
            return
        self.StartPassiveEffects(itemID, moduleTypeID)

    def ChangeModuleOverheatStatus(self, itemKey, moduleTypeID, flagID, start = True):
        typeEffectInfo = sm.GetService('ghostFittingSvc').GetDefaultAndOverheatEffect(moduleTypeID)
        if typeEffectInfo.overloadEffect:
            if start:
                self.ChangeModuleStatus(itemKey, typeEffectInfo.overloadEffect.effectID)
            else:
                self.StopEffectAndRestartBursts(typeEffectInfo.overloadEffect.effectID, itemKey)
            if typeEffectInfo.defaultEffect:
                self.StopEffectAndRestartBursts(typeEffectInfo.defaultEffect.effectID, itemKey)
                self.ActivateModule(itemKey, moduleTypeID, flagID)

    def OfflineSimulatedModule(self, itemKey, moduleTypeID, flagID):
        self.OfflineModule(itemKey)
        self.TryStopPassiveEffects(itemKey, moduleTypeID, flagID)
        self.DeactivateSimulatedModule(itemKey, moduleTypeID)

    def DeactivateSimulatedModule(self, itemKey, moduleTypeID):
        typeEffectInfo = sm.GetService('ghostFittingSvc').GetDefaultAndOverheatEffect(moduleTypeID)
        if typeEffectInfo.defaultEffect:
            self.StopEffectAndRestartBursts(typeEffectInfo.defaultEffect.effectID, itemKey)
        if typeEffectInfo.overloadEffect:
            self.StopEffectAndRestartBursts(typeEffectInfo.overloadEffect.effectID, itemKey)

    def StopEffectAndRestartBursts(self, effectID, itemKey, forced = False):
        self.StopEffect(effectID, itemKey, forced=forced)
        self.TryRestartBurstEffects(effectID, itemKey)

    def TryStopPassiveEffects(self, itemID, itemTypeID, flagID):
        if not IsRigSlot(flagID):
            return
        dogmaItem = self.SafeGetDogmaItem(itemID)
        if dogmaItem is None:
            return
        self.StopPassiveEffects(dogmaItem, itemID, itemTypeID)

    def GetItem(self, itemID):
        if itemID != session.charid:
            return self.dogmaItems.get(itemID)
        item = self.godma.GetItem(itemID)
        return item

    def GetCharacter(self, itemID, flush = False):
        return self.GetItem(itemID)

    def ShouldStartChanceBasedEffect(self, *args, **kwargs):
        return False

    def StartSystemEffect(self):
        pass

    def AddTargetEx(self, *args, **kwargs):
        return 1

    def ChangeModuleStatus(self, itemKey, effectID = None):
        dogmaItem = self.GetDogmaItem(itemKey)
        envInfo = dogmaItem.GetEnvironmentInfo()
        env = Environment(itemID=envInfo.itemID, charID=envInfo.charID, shipID=self.shipID, targetID=envInfo.targetID, otherID=envInfo.otherID, effectID=effectID, dogmaLM=weakref.proxy(self), expressionID=None, structureID=envInfo.structureID)
        self.StartEffect(effectID, itemKey, env, checksOnly=None)

    def CheckSkillRequirementsForType(self, typeID, *args):
        return self.GetMissingSkills(typeID)

    @telemetry.ZONE_METHOD
    def GetMissingSkills(self, typeID, skillSvc = None):
        if skillSvc is None:
            skillSvc = sm.GetService('skills')
        return super(FittingDogmaLocation, self).GetMissingSkills(typeID, skillSvc.GetSkills())

    def SetQuantity(self, itemKey, quantity):
        shipID, flagID, typeID = itemKey
        if self.IsItemLoaded(shipID):
            return self.SetAttributeValue(itemKey, const.attributeQuantity, quantity)

    def GetTurretAndMissileDps(self, shipID):
        return GetTurretMissileAndAoeDps(shipID, self)

    def GetAlphaStrike(self):
        return GetAlphaStrike(self)

    def GetOptimalDroneDamage(self, shipID, activeDrones):
        return GetOptimalDroneDamage(shipID, self, activeDrones)

    def GetOptimalDroneDamage2(self, shipID, activeDrones):
        return self.GetOptimalDroneDamage(shipID, activeDrones)

    def IsModuleIncludedInCalculation(self, module):
        dogmaItem = self.GetDogmaItem(module.itemID)
        return dogmaItem.IsActive()

    def GetDragData(self, itemID):
        return GetFittingItemDragData(itemID, self)

    def GetClassForItem(self, item):
        categoryID = item.categoryID
        if item.flagID in (const.flagCargo,) and categoryID in (const.categoryShip, const.categoryStructure):
            return BaseDogmaItem
        if categoryID == const.categoryShip:
            return GhostShipDogmaItem
        if item.categoryID == const.categoryStructure:
            return GhostStructureDogmaItem
        if IsStructureFittable(categoryID):
            return GhostStructureModuleDogmaItem
        if IsShipFittable(categoryID):
            return GhostModuleDogmaItem
        if item.categoryID == const.categoryDrone:
            return GhostDroneDogmaItem
        if item.categoryID == const.categoryFighter:
            return GhostFighterDogmaItem
        return BaseDogmaLocation.GetClassForItem(self, item)

    def GetShip(self):
        return self.GetShipItem()

    def GetShipItem(self):
        return self.SafeGetDogmaItem(self.shipID)

    def GetFittedItemsToShip(self):
        shipItem = self.GetShipItem()
        if shipItem:
            return shipItem.GetFittedItems()
        else:
            return {}

    def GetModuleFromShipFlag(self, flagID):
        return self.GetItemFromShipFlag(flagID, getCharge=False)

    def GetChargeFromShipFlag(self, flagID):
        return self.GetItemFromShipFlag(flagID, getCharge=True)

    def GetItemFromShipFlag(self, flagID, getCharge):
        fittedItems = self.GetFittedItemsToShip()
        for eachItem in fittedItems.itervalues():
            try:
                if eachItem.flagID != flagID:
                    continue
                if getCharge and self.IsCharge(eachItem) or not getCharge and not self.IsCharge(eachItem):
                    return eachItem
            except ReferenceError as e:
                self.LogWarn(e)

    def IsCharge(self, fittedItem):
        if isinstance(fittedItem.itemID, tuple):
            return True
        if fittedItem.categoryID == const.categoryCharge:
            return True
        return False

    def GetChargeNonDB(self, shipID, flagID):
        for itemID, fittedItem in self.GetFittedItemsToShip().iteritems():
            if isinstance(itemID, tuple):
                continue
            if fittedItem.flagID != flagID:
                continue
            if fittedItem.categoryID == const.categoryCharge:
                return fittedItem

    def GetSensorStrengthAttribute(self, shipID):
        return GetSensorStrengthAttribute(self, shipID)

    @WrappedMethod
    def MakeShipActive(self, shipID, oldShipID):
        myCharID = session.charid
        self.LoadItem(myCharID)
        shipDogmaItem = self.GetDogmaItem(shipID)
        shipDogmaItem.OnItemLoaded()
        uthread.Lock(self, 'makeShipActive')
        try:
            while not session.IsItSafe():
                self.LogInfo('MakeShipActive - session is mutating. Sleeping for 250ms')
                blue.pyos.synchro.SleepSim(250)

            if shipID is None:
                log.LogTraceback('Unexpectedly got shipID = None')
                return
            scatterValueBefore = self.scatterAttributeChanges
            self.SetScatterOnOrOff(scatterOn=False)
            try:
                self.ApplyBrainEffects(shipID, myCharID)
            finally:
                self.shipIDBeingDisembarked = None
                self.SetScatterOnOrOff(scatterOn=scatterValueBefore)

        finally:
            uthread.UnLock(self, 'makeShipActive')

    def RemoveAllItemsFromHold(self, flagID):
        holdItems = self.GetHoldItems(flagID)
        for eachItemID in holdItems:
            self.UnloadItem(eachItemID)

    def GetCapacity(self, shipID, attributeID, flagID):
        keyVal = KeyVal(capacity=0, used=0)
        if flagID == const.flagDroneBay:
            keyVal.capacity = self.GetAttributeValue(shipID, const.attributeDroneCapacity)
            used = 0
            shipDogmaItem = self.GetDogmaItem(shipID)
            for droneID in shipDogmaItem.drones:
                used += self.GetAttributeValue(droneID, const.attributeVolume)

            keyVal.used = used
        elif flagID == const.flagCargo:
            shipItem = self.SafeGetDogmaItem(shipID)
            if not shipItem:
                return keyVal
            if shipItem.categoryID == const.categoryStructure:
                keyVal.capacity = MAX_CARGO
            else:
                keyVal.capacity = self.GetAttributeValue(shipID, const.attributeCapacity)
            used = 0
            for eachItemID, eachItem in self.GetHoldItems(const.flagCargo).iteritems():
                qty = getattr(eachItem, 'stacksize', 1)
                used += qty * self.GetAttributeValue(eachItemID, const.attributeVolume)

            keyVal.used = used
        elif flagID == const.flagFighterBay:
            keyVal.capacity = self.GetAttributeValue(shipID, const.attributeFighterCapacity)
            used = 0
            fightersInBay = self.GetHoldItems(const.flagFighterBay)
            for eachItemID, eachItem in fightersInBay.iteritems():
                used += eachItem.stacksize * self.GetAttributeValue(eachItemID, const.attributeVolume)

            keyVal.used = used
        elif IsFighterTubeFlag(flagID):
            keyVal.capacity = self.GetAttributeValue(shipID, const.attributeFighterCapacity)
            used = 0
            fightersInTube = self.GetHoldItems(flagID)
            for eachItemID, eachItem in fightersInTube.iteritems():
                used += eachItem.stacksize * self.GetAttributeValue(eachItemID, const.attributeVolume)

            keyVal.used = used
        return keyVal

    def CapacitorSimulator(self, shipID):
        return CapacitorSimulator(self, shipID)

    def _IsLocationIDInvalidForFitting(self, locationID):
        if locationID == self.shipIDBeingDisembarked:
            return True
        isLocationIDValidForFitting = locationID not in (self.GetCurrentShipID(), session.charid)
        return isLocationIDValidForFitting

    def OnAttributeChanged(self, attributeID, itemKey, value = None, oldValue = None):
        value = BaseDogmaLocation.OnAttributeChanged(self, attributeID, itemKey, value=value, oldValue=oldValue)
        self.RefreshEffectsOnShip(attributeID, itemKey)
        if self.scatterAttributeChanges:
            sm.ScatterEvent('OnDogmaAttributeChanged', self.shipID, itemKey, attributeID, value)

    def GetQuantity(self, itemID):
        return getattr(self.GetItem(itemID), 'stacksize', 1)

    def GetAccurateAttributeValue(self, itemID, attributeID, *args):
        return self.GetAttributeValue(itemID, attributeID)

    def DecreaseItemAttribute(self, itemKey, attributeID, itemKey2, attributeID2, limit = None, scaleFactor = 1):
        pass

    def AddLocationRequiredSkillModifierWithSource(self, operation, toLocationID, skillID, toAttribID, fromAttrib):
        if toLocationID is None:
            return
        BaseDogmaLocation.AddLocationRequiredSkillModifierWithSource(self, operation, toLocationID, skillID, toAttribID, fromAttrib)

    def IncreaseItemAttribute(self, itemKey, attributeID, itemKey2, attributeID2, limitAttributeID = None, scaleFactor = 1):
        value = scaleFactor * self.GetAttributeValue(itemKey2, attributeID2)
        if limitAttributeID:
            dogmaItem = self.dogmaItems.get(itemKey)
            value, _ = LimitAttributeOnItem(dogmaItem, blue.os.GetSimTime() / const.SEC, limitAttributeID, value)
        new, old = self.IncreaseItemAttributeEx(itemKey, attributeID, value, alsoReturnOldValue=True)
        if attributeID in (const.attributeShieldCharge, const.attributeCapacitorCharge) and new > old:
            actingItem = self.dogmaItems.get(itemKey2)
            if actingItem is None:
                self.broker.LogWarn('No actingItem in IncreaseItemAttribute', itemKey, attributeID, itemKey2, attributeID2)
        return new

    def IncreaseItemAttributeEx(self, itemKey, attributeID, value, silently = 0, alsoReturnOldValue = False):
        dogmaItem = self.GetDogmaItem(itemKey)
        if not dogmaItem.CanAttributeBeModified():
            if alsoReturnOldValue:
                return (0, 0)
            return 0
        attrib = dogmaItem.attributes[attributeID]
        oldValue = attrib.GetValue()
        attrib.SetBaseValue(oldValue + value)
        newValue = attrib.GetValue()
        if alsoReturnOldValue:
            return (newValue, oldValue)
        return newValue

    def DecreaseItemAttributeEx(self, itemKey, attributeID, reduction, silently = 0, alsoReturnOldValue = False):
        dogmaItem = self.dogmaItems.get(itemKey, None)
        if dogmaItem is None or not dogmaItem.CanAttributeBeModified():
            if alsoReturnOldValue:
                return (0, 0)
            return 0
        oldValue = dogmaItem.attributes[attributeID].GetValue()
        if oldValue - reduction < 0:
            newValue = 0
        else:
            newValue = oldValue - reduction
        dogmaItem.attributes[attributeID].SetBaseValue(newValue)
        if alsoReturnOldValue:
            return (newValue, oldValue)
        return newValue

    def IsInWeaponBank(self, *args):
        return False

    def WaitForShip(self, *args):
        pass

    def CheckItemsMissingInAddModifier(self, toItemID, fromAttrib):
        if not fromAttrib:
            raise RuntimeError('Item missing from AddModifier')

    def GetSecurityClass(self):
        return securityClassZeroSec

    def StartEffect_PreChecks(self, effect, dogmaItem, environment, byUser):
        BaseDogmaLocation.StartEffect_PreChecks(self, effect, dogmaItem, environment, byUser)
        if effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget) and dogmaItem.IsOnline():
            self._CheckIfTooManyModulesInGroupAreActive(effect, dogmaItem, environment)
            if self.GetAttributeValue(dogmaItem.itemID, const.attributeActivationBlocked) != 0:
                raise UserError('ModuleIsBlocked', {'moduleName': (const.UE_TYPEID, dogmaItem.typeID)})

    def _CheckIfTooManyModulesInGroupAreActive(self, effect, dogmaItem, environment):
        shipCategoryID = environment.shipCategoryID
        shipID = environment.shipID
        itemID = dogmaItem.itemID
        itemGroupID = dogmaItem.groupID
        if shipCategoryID != const.categoryShip:
            return
        if not self.IsShipLoaded(shipID):
            return
        maxGroupActive = self.GetAttributeValue(itemID, const.attributeMaxGroupActive)
        if itemGroupID == self.GetAttributeValue(shipID, const.attributeMaxShipGroupActiveID):
            maxGroupActive = max(self.GetAttributeValue(shipID, const.attributeMaxShipGroupActive), maxGroupActive)
        if maxGroupActive > 0:
            itemTypeID = dogmaItem.typeID
            shipDogmaItem = self.GetDogmaItem(shipID)
            modules = shipDogmaItem.GetFittedItems().itervalues()
            total = len([ item for item in modules if item.groupID == itemGroupID and item.IsActive() ])
            if total >= maxGroupActive:
                raise UserError('EffectCrowdedOut', {'module': itemTypeID,
                 'count': total})

    def SetDroneActivityState(self, droneID, setActive, qty = 1):
        return self.selectedDronesTracker.SetDroneActivityState(self, droneID, setActive, qty=qty)

    def RegisterDroneAsActive(self, droneID, qty = 1, raiseError = True):
        return self.selectedDronesTracker.RegisterDroneAsActive(self, droneID, qty=qty, raiseError=raiseError)

    def UnregisterDroneFromActive(self, droneID, qty = 1):
        return self.selectedDronesTracker.UnregisterDroneFromActive(droneID, qty=qty)

    def GetActiveDrones(self):
        return self.selectedDronesTracker.GetSelectedDrones()

    @telemetry.ZONE_METHOD
    def GetSubSystemInFlag(self, shipID, flagID):
        dogmaItem = self.GetModuleFromShipFlag(flagID)
        return dogmaItem

    def GetActivityState(self, itemID):
        dogmaItem = self.SafeGetDogmaItem(itemID)
        if dogmaItem:
            return GetTextForCurrentStateForDogmaItem(dogmaItem)
        return (None, None, None)

    def GetHoldItems(self, flagID):
        cargoItems = {}
        for eachItemID, eachItem in self.dogmaItems.iteritems():
            if eachItem.flagID == flagID:
                cargoItems[eachItemID] = eachItem

        return cargoItems

    def GetFightersInTubeInfo(self, flagID):
        fightersInHold = self.GetHoldItems(flagID)
        if len(fightersInHold) > 1:
            self.LogError('More than 1 fighter in tube, flagID = ', flagID)
        for eachItem in fightersInHold.itervalues():
            squadronSize = eachItem.squadronSize
            fighterTypeID = eachItem.typeID
            fighterID = eachItem.itemID
            return KeyVal(itemID=fighterID, typeID=fighterTypeID, squadronSize=squadronSize, fighters=eachItem)

    def SetScatterOnOrOff(self, scatterOn = True):
        self.scatterAttributeChanges = scatterOn

    def GetMaxActiveDrones(self):
        return max(5, self.GetAttributeValue(session.charid, const.attributeMaxActiveDrones))

    def RefreshEffectsOnShip(self, attributeID, itemKey, *args):
        self._TryRefreshOtherModuleEffectsOnChanges(attributeID, itemKey)
        if itemKey != self.shipID:
            return
        effectIDsToRefresh = self.effectsNeedRefreshDict.get(attributeID, [])
        if not effectIDsToRefresh:
            return
        effectInfoForRefresh = self.GetItemsAndEffectsToUpdate(effectIDsToRefresh, [])
        for effectClass, environment, eachItemKey in effectInfoForRefresh:
            effectClass.RefreshEffect(self, environment, eachItemKey, self.shipID)

    def _TryRefreshOtherModuleEffectsOnChanges(self, attributeID, itemKey):
        if attributeID in const.dbuffAttributeValueMappings:
            pass
        elif itemKey != self.shipID and attributeID in SPEED_ATTRIBUTES_REQUIRING_MODULE_UPDATE:
            pass
        else:
            return
        effectInfoForRefresh = self.GetItemsAndEffectsToUpdate(SPEED_CHANGING_EFFECTS, [])
        for eachEffectToRefresh in effectInfoForRefresh:
            if eachEffectToRefresh not in self.effectRefreshInfo:
                self.effectRefreshInfo.append(eachEffectToRefresh)

        self.__RefreshEffect()

    @threadutils.throttled(0.05)
    def __RefreshEffect(self):
        while self.effectRefreshInfo:
            effectInfo = self.effectRefreshInfo.pop(0)
            effectClass, environment, eachItemKey = effectInfo
            if environment.shipID != self.shipID:
                continue
            effectClass.RefreshEffect(self, environment, eachItemKey, self.shipID)

    def GetItemsAndEffectsToUpdate(self, effectIDsToRefresh, excludedItems):
        effectInfoForRefresh = []
        for eachDogmaItem in self.GetFittedItemsToShip().itervalues():
            if eachDogmaItem.itemID in excludedItems:
                continue
            for eachEffectID, eachEffect in eachDogmaItem.activeEffects.iteritems():
                if eachEffectID not in effectIDsToRefresh:
                    continue
                environment = eachEffect[const.ACT_IDX_ENV]
                effectClass = self.effectCompiler.effects.get(eachEffectID)
                if effectClass is None:
                    continue
                effectInfoForRefresh.append((effectClass, environment, eachDogmaItem.itemID))

        return effectInfoForRefresh

    def GetActivatedEffectsOnShip(self):
        activatedEffects = []
        for itemID, dogmaItem in self.GetFittedItemsToShip().iteritems():
            try:
                for effectID, activationInfo in dogmaItem.activeEffects.iteritems():
                    effectCategory = self.dogmaStaticMgr.effects[effectID].effectCategory
                    if effectID != const.effectOnline and effectCategory in self.manualEffectCategories:
                        activatedEffects.append((effectID,
                         itemID,
                         activationInfo,
                         dogmaItem.typeID))

            except ReferenceError:
                pass

        return activatedEffects

    def DeactivateActivatedEffectsOfShip(self, excludeEffectKey = None):
        for effectID, itemID, activationInfo, typeID in self.GetActivatedEffectsOnShip():
            if excludeEffectKey == (effectID, itemID):
                continue
            try:
                self.StopEffectAndRestartBursts(effectID, itemID, forced=True)
            except Exception as e:
                pass

        sm.GetService('ghostFittingSvc').SendFittingSlotsChangedEvent()
        return 1

    def DeactivateBlockedActivatedEffectsOfShip(self):
        for effectID, itemID, activationInfo, typeID in self.GetActivatedEffectsOnShip():
            if not self.GetAttributeValue(itemID, const.attributeActivationBlocked):
                continue
            try:
                self.StopEffectAndRestartBursts(effectID, itemID, forced=True)
            except Exception as e:
                pass

        sm.GetService('ghostFittingSvc').SendFittingSlotsChangedEvent()
        return 1

    def TryRestartBurstEffects(self, effectID, itemID):
        if effectID not in BURST_EFFECTS:
            return
        self.dbuffRegistry.RemoveBuffsFromItem(self.shipID)
        effectInfoForRefresh = self.GetItemsAndEffectsToUpdate(BURST_EFFECTS, [itemID])
        for effectClass, environment, eachItemKey in effectInfoForRefresh:
            effectClass.Start(environment, self, eachItemKey, environment.shipID, environment.charID, environment.otherID, environment.targetID)

        sm.GetService('ghostFittingSvc').SendOnStatsUpdatedEvent()

    def IsShipCloaked(self):
        cloakingDeviceList = [ x for x in self.GetFittedItemsToShip().itervalues() if x.groupID == const.groupCloakingDevice ]
        return any((x for x in cloakingDeviceList if x.IsActive()))

    def GetShipItemForFighter(self, itemID):
        currentShipID = self.GetCurrentShipID()
        if currentShipID:
            return self.SafeGetDogmaItem(currentShipID)

    def GetFightersForTube(self, eachTubeFlagID):
        fighterInfo = self.GetFightersInTubeInfo(eachTubeFlagID)
        if fighterInfo:
            return fighterInfo.fighters

    def GetFighterNumByTypeIDsInTubes(self):
        return GetFighterNumByTypeIDsInTubes(self)

    def GetCharacterSecurityStatus(self, charID):
        return sm.GetService('crimewatchSvc').GetMySecurityStatus()

    def GetAttributesForItem(self, itemID, typeID):
        if itemID and dynamicitemattributes.IsDynamicType(typeID):
            realItemID = GetOriganlItemIDFromItemKey(itemID)
            return sm.GetService('dynamicItemSvc').GetDynamicItemAttributes(realItemID)
        return BaseDogmaLocation.GetAttributesForItem(self, itemID, typeID)

    def GetAttributesForRealItemID(self, itemID, typeID):
        if itemID and dynamicitemattributes.IsDynamicType(typeID):
            return sm.GetService('dynamicItemSvc').GetDynamicItemAttributes(itemID)
        return BaseDogmaLocation.GetAttributesForItem(self, itemID, typeID)

    def OnActivationBlockedChanged(self, attributeID, itemID, newValue, oldValue = None):
        if not newValue:
            return
        dogmaItem = self.dogmaItems[itemID]
        for effectID in dogmaItem.activeEffects.keys():
            if effectID in self.onlineEffects:
                continue
            effect = self.dogmaStaticMgr.effects[effectID]
            if effect.effectCategory not in [const.dgmEffActivation, const.dgmEffTarget]:
                continue
            self.StopEffect(effectID, itemID, forced=True)

        sm.GetService('ghostFittingSvc').SendFittingSlotsChangedEvent()

    def ShouldMessageItemEvent(self, itemID, ownerID = None, locationID = None):
        dogmaItem = self.dogmaItems.get(itemID, None)
        if dogmaItem is None:
            return False
        if ownerID is None:
            ownerID = dogmaItem.ownerID
        if self.IsIgnoringOwnerEvents(ownerID):
            return False
        if locationID is None:
            locationID = dogmaItem.locationID
        if locationID in self.loadingItems and itemID in self.loadingItems:
            return False
        if locationID in self.unloadingItems and itemID in self.unloadingItems:
            return False
        return True
