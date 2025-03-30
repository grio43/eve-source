#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\ghostFittingSvc.py
from carbon.common.script.sys.service import Service
from collections import defaultdict
from contextlib import contextmanager
import dynamicitemattributes
import evetypes
import inventorycommon
import itertoolsext
import shipmode
import threadutils
import uthread
import telemetry
from carbon.common.script.util.commonutils import StripTags
from eve.common.lib import appConst as const
from eve.common.lib.appConst import UE_LOC
from dogma.items.structureModuleDogmaItem import StructureModuleDogmaItem
from eve.client.script.ui.control.historyBar import HistoryController, UPDATE_CODE_SELECTED
from eve.client.script.ui.inflight import shipstance
from eve.client.script.ui.shared.fitting.fittingControllerUtil import GetFittingController
from eve.client.script.ui.shared.fitting.fittingUtil import GetTypeIDForController
from eve.client.script.ui.shared.fittingScreen import OFFLINE, ONLINE, ACTIVE, OVERHEATED, DEACTIVATING, DEHEATING, HEATING_FROM_OFFLINE, ACTIVE_FROM_OFFLINE
from eve.client.script.ui.shared.fittingScreen.browsers.browserUtil import AUTO_FITTED_SERVICES_BY_STRUCTURE_TYPE
from eve.client.script.ui.shared.fittingScreen.fittingSearchUtil import FAKE_FLAGID
from eve.client.script.ui.shared.fittingScreen.fittingSnapshot import FittingSnapshot
from eve.client.script.ui.shared.fittingScreen.fittingUtil import GetDefaultAndOverheatEffectForType, GetFlagIdToUse, IsCharge, GetOriginalItemID
from eve.client.script.ui.shared.fittingScreen.ghostFittingUtil import GhostFittingDataObject, DBLessGhostFittingDataObject
from dogma.items.chargeDogmaItem import ChargeDogmaItem
from dogma.items.moduleDogmaItem import ModuleDogmaItem
from eve.client.script.ui.shared.fittingScreen.itemPickerMenu import IsValidForHold, GetModifiedQtyDict, GetMaxQty, IsAllowedToAddAtAll, GetDronesInDamgeAmountOrder
from eve.client.script.ui.shared.fittingScreen.moduleStateUtil import GetCurrentStateForDogmaItemWithEffects
from eve.common.script.sys.eveCfg import GetActiveShip
from eveexceptions import UserError
from fighters import FIGHTER_CLASS_LIGHT, FIGHTER_CLASS_SUPPORT, FIGHTER_CLASS_HEAVY, FIGHTER_CLASS_STANDUP_LIGHT, FIGHTER_CLASS_STANDUP_SUPPORT, FIGHTER_CLASS_STANDUP_HEAVY, classNameMessageByFighterClass, shipTubeCountAttributeByFighterClass
from fighters import GetMaxSquadronSize
from fighters.client import GetFighterClass, GetSquadronTypes, GetFighterTubesForShipAndDogmaLocation
from inventorycommon.util import IsSubsystemFlag, IsFighterTubeFlag, IsModularShip
from localization import GetByLabel
from shipfitting.errorConst import WRONG_SLOT, SLOT_IN_USE, SLOT_NOT_PRESENT
from shipfitting.fittingDogmaLocationUtil import GetNumChargesFullyLoaded
from shipfitting.fittingStuff import GetErrorInfoDoesModuleTypeIDFit, IsRightSlotForType, CheckCanFitType, IsRigSlot, GetSlotListForTypeID
import inventorycommon.const as invConst
import blue
import log
from shipmode.inventory import InventoryGhost
from utillib import KeyVal
import carbonui.const as uiconst
from carbonui.uicore import uicore
from dogma import ammoloadingUtils
allModuleSlots = invConst.subsystemSlotFlags + invConst.loSlotFlags + invConst.medSlotFlags + invConst.hiSlotFlags + invConst.serviceSlotFlags
allSlots = invConst.rigSlotFlags + allModuleSlots
TYPEIDS_NOT_ACTIVE_BY_DEFAULT = evetypes.GetTypeIDsByGroups([const.groupCloakingDevice, const.groupMassEntanglers])
USERERRORS_TO_EAT = ('EffectAlreadyActive2',
 'NotEnoughCpu',
 'NotEnoughPower',
 'NoCharges',
 'EffectCrowdedOut',
 'CantCloakTooManyDevices',
 'DeniedActivateCloaked',
 'ModuleIsBlocked',
 'CannotOnlineReachedMaxGroupOnline')

class GhostFittingSvc(Service):
    __guid__ = 'svc.ghostFittingSvc'
    __exportedcalls__ = {}
    __startupdependencies__ = ['clientDogmaIM']
    __notifyevents__ = ['OnSessionReset', 'OnCharacterSessionChanged', 'ProcessSessionReset']

    @telemetry.ZONE_METHOD
    def __init__(self):
        super(GhostFittingSvc, self).__init__()
        self.effectsByType = {}
        self._ghostFittingController = None
        self.simulationChanged = False
        self.fittingName = ''
        self.failedDynamicTypesByFlagID = {}
        self.lastLoadedFitInfo = (None, None)
        self.clientDogmaLocation = None
        self._fittingDogmaLocation = None
        self.historyController = HistoryController(overwriteHistory=False)

    @property
    def ghostFittingController(self):
        return self._ghostFittingController

    @ghostFittingController.setter
    def ghostFittingController(self, value):
        self._ghostFittingController = value

    @property
    def fittingDogmaLocation(self):
        if self._fittingDogmaLocation is None:
            self._fittingDogmaLocation = self.clientDogmaIM.GetFittingDogmaLocation()
        return self._fittingDogmaLocation

    def _Reset(self):
        self.effectsByType = {}
        self.ghostFittingController = None
        self.simulationChanged = False
        self.fittingName = ''
        self.failedDynamicTypesByFlagID = {}
        self.lastLoadedFitInfo = (None, None)
        self.clientDogmaLocation = None
        self._fittingDogmaLocation = None

    def Run(self, ms = None):
        super(GhostFittingSvc, self).Run(ms)
        self.clientDogmaLocation = self.clientDogmaIM.GetDogmaLocation()

    def OnSessionReset(self):
        self._Reset()

    def OnCharacterSessionChanged(self, _oldCharacterID, newCharacterID):
        if newCharacterID is not None:
            self.clientDogmaLocation = self.clientDogmaIM.GetDogmaLocation()

    def ResetFittingDomaLocation(self, force = False):
        self._fittingDogmaLocation = self.clientDogmaIM.GetFittingDogmaLocation(force=force)

    def TryFitItemsToCargo(self, qtyByTypeIDs, allowModifyQty = True):
        self.TryFitItemsToHold(qtyByTypeIDs, const.flagCargo, allowModifyQty)

    def TryFitFightersToTubeOrBay(self, qtyByTypeIDs):
        for eachTypeID, qty in qtyByTypeIDs.iteritems():
            self.FitAFighterToTubeOrBay(eachTypeID, qty, sendUpdateEvent=False)

        self.SendFittingSlotsChangedEvent()

    def FitAFighterToTubeOrBay(self, fighterTypeID, qty, sendUpdateEvent = True):
        try:
            fighter = self.FitFighterToEmptyTube(fighterTypeID)
        except UserError as e:
            if e.msg == 'CannotLoadFighterTubeNoTubesAvailableForClass':
                fighter = None
            else:
                raise

        if not fighter:
            self.TryFitItemsToFighterBay({fighterTypeID: qty})
            fighter = self._GetCargoItemOfType(fighterTypeID, const.flagFighterBay)
        if sendUpdateEvent:
            self.SendFittingSlotsChangedEvent()
        return fighter

    def TryFitItemsToFighterBay(self, qtyByTypeIDs, allowModifyQty = True):
        self.TryFitItemsToHold(qtyByTypeIDs, const.flagFighterBay, allowModifyQty)

    def TryFitItemsToHold(self, qtyByTypeIDs, flagID, allowModifyQty = True):
        if allowModifyQty:
            qtyByTypeIDs = GetModifiedQtyDict(self.fittingDogmaLocation, qtyByTypeIDs, flagID)
        for eachTypeID, eachQty in qtyByTypeIDs.iteritems():
            typeVolume = evetypes.GetVolume(eachTypeID)
            if typeVolume <= 0:
                continue
            if not IsAllowedToAddAtAll(eachTypeID):
                continue
            self.FitAnItemToHold(eachTypeID, eachQty, flagID, sendUpdateEvent=False)

        self.SendOnStatsUpdatedEvent()

    def FitAnItemToHold(self, typeID, qty, flagID, sendUpdateEvent = False):
        dogmaItem = self._GetCargoItemOfType(typeID, flagID)
        if dogmaItem:
            qty = min(qty, GetMaxQty(self.fittingDogmaLocation, flagID, {typeID: qty}) or 0)
            if not qty:
                return dogmaItem
            dogmaItem.stacksize += qty
        else:
            dogmaItem = self.FitItemOrDroneToShip(typeID, flagID, qty=qty)
        if sendUpdateEvent:
            self.SendOnStatsUpdatedEvent()
        if dogmaItem and not IsValidForHold(typeID, flagID):
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/Fitting/FittingWindow/ItemAddedNotInFitting')})
        return dogmaItem

    def _GetCargoItemOfType(self, typeID, flagID):
        currentItems = self.fittingDogmaLocation.GetHoldItems(flagID)
        dogmaItem = itertoolsext.first_or_default((i for i in currentItems.itervalues() if i.typeID == typeID))
        return dogmaItem

    def ModifyHoldItemStackSize(self, typeID, wantedNum, flagID):
        dogmaItem = self._GetCargoItemOfType(typeID, flagID)
        if dogmaItem:
            maxExtra = GetMaxQty(self.fittingDogmaLocation, flagID, {typeID: wantedNum}) or 0
            qty = min(wantedNum, dogmaItem.stacksize + maxExtra)
            if qty == 0:
                return self.UnfitModule(dogmaItem.itemID)
            dogmaItem.stacksize = qty
            self.SendOnStatsUpdatedEvent()
        else:
            self.FitAnItemToHold(typeID, wantedNum, flagID, sendUpdateEvent=True)

    def TryFitDronesToDroneBay(self, qtyByTypeAndItemIDs, allowModifyQty = True, fittingSnapshot = None):
        if allowModifyQty:
            qtyByTypeAndItemIDs = GetModifiedQtyDict(self.fittingDogmaLocation, qtyByTypeAndItemIDs, const.flagDroneBay)
        dogmaItemIDsFitted = set()
        for (eachTypeID, eachItemID), eachQty in qtyByTypeAndItemIDs.iteritems():
            fitted = self.FitDronesToShip(eachTypeID, eachQty, raiseError=False, sendUpdateEvent=False, selectByDefault=False, itemID=eachItemID)
            dogmaItemIDsFitted.update(fitted)

        if fittingSnapshot:
            self.RegisterDronesByTypeID(dogmaItemIDsFitted, fittingSnapshot.registeredDroneTypes)
        else:
            self.RegisterTopDpsDrones(dogmaItemIDsFitted)
        self.SendOnStatsUpdatedEvent()

    def RegisterTopDpsDrones(self, dogmaItemIDsFitted):
        shipDogmaItem = self.fittingDogmaLocation.GetShip()
        if shipDogmaItem:
            dronesInDamageOrder = GetDronesInDamgeAmountOrder(self.fittingDogmaLocation, dogmaItemIDsFitted)
            for eachDroneID in dronesInDamageOrder:
                self.fittingDogmaLocation.RegisterDroneAsActive(eachDroneID, raiseError=False)

    def RegisterDronesByTypeID(self, allDrones, registeredDroneTypes):
        selectedDrones = defaultdict(int)
        selectedDrones.update(registeredDroneTypes)
        for droneID in allDrones:
            dogmaItem = self.fittingDogmaLocation.SafeGetDogmaItem(droneID)
            if dogmaItem.typeID in selectedDrones:
                selectedDrones[dogmaItem.typeID] -= 1
                if selectedDrones[dogmaItem.typeID] <= 0:
                    selectedDrones.pop(dogmaItem.typeID, None)
                self.fittingDogmaLocation.RegisterDroneAsActive(droneID, raiseError=False)
            if not selectedDrones:
                break

    def FitDronesToShip(self, droneTypeID, qty = 1, raiseError = True, sendUpdateEvent = True, selectByDefault = True, itemID = None):
        dogmaItemIDsFitted = set()
        for i in xrange(qty):
            dogmaItem = self.FitADroneToShip(droneTypeID, raiseError, selectByDefault=selectByDefault, itemID=itemID)
            if dogmaItem is None:
                break
            dogmaItemIDsFitted.add(dogmaItem.itemID)

        if sendUpdateEvent:
            self.SendOnStatsUpdatedEvent()
        return dogmaItemIDsFitted

    def FitADroneToShip(self, droneTypeID, raiseError = True, sendUpdateEvent = False, selectByDefault = True, itemID = None):
        shipDogmaItem = self.fittingDogmaLocation.GetShipItem()
        currentItems = shipDogmaItem.drones
        dogmaItem = self.FitItemOrDroneToShip(droneTypeID, const.flagDroneBay, itemID=itemID)
        if dogmaItem:
            if selectByDefault:
                self.fittingDogmaLocation.RegisterDroneAsActive(dogmaItem.itemID, raiseError=raiseError)
            if sendUpdateEvent:
                self.SendOnStatsUpdatedEvent()
        return dogmaItem

    def FitItemOrDroneToShip(self, typeID, flagID, qty = 1, itemID = None):
        shipID = self.fittingDogmaLocation.GetCurrentShipID()
        g = GhostFittingDataObject(shipID, flagID, typeID, originalItemID=itemID)
        capacityInfo = self.fittingDogmaLocation.GetCapacity(shipID, None, flagID)
        volume = evetypes.GetVolume(typeID)
        if capacityInfo.used + volume * qty > capacityInfo.capacity:
            return
        itemKey = g.GetItemKey()
        dogmaItem = self.GetLoadedItem(itemKey, item=g)
        dogmaItem.stacksize = qty
        return dogmaItem

    def FitFighterToEmptyTube(self, fighterTypeID):
        emptyTubeID = None
        for eachTubeID in const.fighterTubeFlags:
            inTube = self.fittingDogmaLocation.GetFightersForTube(eachTubeID)
            if not inTube:
                emptyTubeID = eachTubeID
                break

        if not emptyTubeID:
            return
        maxInSquadron = GetMaxSquadronSize(fighterTypeID)
        return self.FitFighterToTube(fighterTypeID, emptyTubeID, maxInSquadron)

    def FitFighterToTube(self, fighterTypeID, tubeFlagID, qty = 1):
        dogmaItem = self.fittingDogmaLocation.GetFightersForTube(tubeFlagID)
        if dogmaItem and dogmaItem.typeID != fighterTypeID:
            raise UserError('CannotLoadFighterTubeDifferentTypeAlreadyLoaded', {'loadedType': dogmaItem.typeID,
             'newType': fighterTypeID})
        qty = self.GetMaxExtraFighters(dogmaItem, fighterTypeID, qty)
        if dogmaItem:
            if qty < 1:
                eve.Message('CannotLoadFighterTubeSquadronIsFull', {'loadedType': dogmaItem.typeID})
                return dogmaItem
            dogmaItem.stacksize += qty
        else:
            if not self._CheckEmptyTubeCanAcceptFighter(fighterTypeID):
                fighterClass = GetFighterClass(self.fittingDogmaLocation, fighterTypeID)
                raise UserError('CannotLoadFighterTubeNoTubesAvailableForClass', {'newType': fighterTypeID,
                 'className': (UE_LOC, classNameMessageByFighterClass[fighterClass])})
            shipID = self.fittingDogmaLocation.GetCurrentShipID()
            g = GhostFittingDataObject(shipID, tubeFlagID, fighterTypeID)
            itemKey = g.GetItemKey()
            dogmaItem = self.GetLoadedItem(itemKey, item=g)
            dogmaItem.stacksize = qty
        if dogmaItem:
            self.SendFittingSlotsChangedEvent()
            self.SendOnStatsUpdatedEvent()
        return dogmaItem

    def GetMaxExtraFighters(self, dogmaItem, fighterTypeID, wantedNum):
        if dogmaItem:
            squadronSize = dogmaItem.stacksize
        else:
            squadronSize = 0
        from fighters import GetMaxSquadronSize
        maxSquadronSize = GetMaxSquadronSize(fighterTypeID)
        qty = min(wantedNum, maxSquadronSize - squadronSize)
        return qty

    def ModifyFighterStackSize(self, typeID, wantedNum, flagID):
        dogmaItem = self.fittingDogmaLocation.GetFightersForTube(flagID)
        if dogmaItem:
            squadronSize = dogmaItem.stacksize
            maxExtra = self.GetMaxExtraFighters(dogmaItem, typeID, squadronSize)
            qty = min(wantedNum, squadronSize + maxExtra)
            if wantedNum < 1:
                return self.UnfitModule(dogmaItem.itemID)
            dogmaItem.stacksize = qty
            self.SendOnStatsUpdatedEvent()
        else:
            self.FitFighterToTube(typeID, flagID, wantedNum)

    def _CheckEmptyTubeCanAcceptFighter(self, fighterTypeID):
        fighterClass = GetFighterClass(self.fittingDogmaLocation, fighterTypeID)
        heavy, support, light = GetSquadronTypes(self.fittingDogmaLocation.GetFighterNumByTypeIDsInTubes())
        totalFightersInTubes = heavy + support + light
        shipID = self.fittingDogmaLocation.shipID
        tubeCountAttributeID = shipTubeCountAttributeByFighterClass[fighterClass]
        totalAllowedFightersForClass = self.fittingDogmaLocation.GetAttributeValue(shipID, tubeCountAttributeID)
        numOfTubes = GetFighterTubesForShipAndDogmaLocation(shipID, self.fittingDogmaLocation)
        if not totalAllowedFightersForClass:
            return False
        if numOfTubes <= totalFightersInTubes:
            return False
        if fighterClass in (FIGHTER_CLASS_LIGHT, FIGHTER_CLASS_STANDUP_LIGHT):
            return light < totalAllowedFightersForClass
        if fighterClass in (FIGHTER_CLASS_SUPPORT, FIGHTER_CLASS_STANDUP_SUPPORT):
            return support < totalAllowedFightersForClass
        if fighterClass in (FIGHTER_CLASS_HEAVY, FIGHTER_CLASS_STANDUP_HEAVY):
            return heavy < totalAllowedFightersForClass
        return True

    def GetLoadedItem(self, itemKey, item, preview = False):
        if IsSubsystemFlag(item.flagID) and not preview:
            subSystem = self.fittingDogmaLocation.GetSubSystemInFlag(None, item.flagID)
            if subSystem:
                self.fittingDogmaLocation.UnfitItemFromShip(subSystem.itemID)
        self.fittingDogmaLocation.LoadItem(itemKey=itemKey, invItem=item)
        self.FlagSimulationChanged()
        return self.fittingDogmaLocation.SafeGetDogmaItem(itemKey)

    def FitModuleToShipAndChangeState(self, shipID, flagID, moduleTypeID, preview = False, originalItemID = None, ignoreSubsystemChange = False):
        dogmaItem, errorInfo = self.FitModuleToShip(shipID, flagID, moduleTypeID, preview, originalItemID=originalItemID)
        if not dogmaItem:
            return (None, errorInfo)
        itemKey = dogmaItem.itemID
        with self.EatCpuPowergridActiveUserErrors():
            self.PerformActionAndSetNewState(ONLINE, itemKey, moduleTypeID, flagID)
        with self.EatCpuPowergridActiveUserErrors():
            if moduleTypeID not in TYPEIDS_NOT_ACTIVE_BY_DEFAULT:
                self.PerformActionAndSetNewState(ACTIVE, itemKey, moduleTypeID, flagID)
        if IsSubsystemFlag(flagID):
            self.SendSubSystemsChangedEvent()
            if not preview and not ignoreSubsystemChange:
                self.SendSubSystemsReallyChanged()
        return (dogmaItem, None)

    def FitModuleToShip(self, shipID, flagID, moduleTypeID, preview = False, originalItemID = None):
        usedFlags = {x.flagID for x in self.fittingDogmaLocation.GetFittedItemsToShip().itervalues()}
        flagID = GetFlagIdToUse(self.fittingDogmaLocation.dogmaStaticMgr, moduleTypeID, flagID, usedFlags)
        canFitModuleInSlot, errorInfo = self.CanFitModuleInSlot(shipID, moduleTypeID, flagID, preview=preview, originalItemID=originalItemID)
        if not canFitModuleInSlot:
            return (None, errorInfo)
        originalItemID = GetOriginalItemID(originalItemID)
        g = GhostFittingDataObject(shipID, flagID, moduleTypeID, originalItemID=originalItemID)
        itemKey = g.GetItemKey()
        dogmaItem = self.GetLoadedItem(itemKey, g, preview)
        return (dogmaItem, None)

    def CanFitModuleInSlot(self, shipID, moduleTypeID, flagID, preview = False, originalItemID = None):
        errorInfo = GetErrorInfoDoesModuleTypeIDFit(self.fittingDogmaLocation, moduleTypeID, flagID, originalItemID)
        if errorInfo is not None:
            if not (IsSubsystemFlag(flagID) and errorInfo.errorKey == SLOT_NOT_PRESENT):
                return (False, errorInfo)
        if self.fittingDogmaLocation.GetSlotOther(shipID, flagID) and not IsSubsystemFlag(flagID):
            self.LogInfo('Couldn not fit a module to ship, something there ', shipID, flagID, moduleTypeID)
            return (False, KeyVal(errorKey=SLOT_IN_USE, extraInfo=None))
        if not IsRightSlotForType(self.fittingDogmaLocation.dogmaStaticMgr, moduleTypeID, flagID):
            self.LogInfo('Couldn not fit a module to ship, not right slot ', shipID, flagID, moduleTypeID)
            return (False, KeyVal(errorKey=WRONG_SLOT, extraInfo=None))
        CheckCanFitType(self.fittingDogmaLocation, moduleTypeID, shipID, originalItemID)
        return (True, errorInfo)

    def UnfitDrones(self, itemKeys, scatter = True):
        for eachItemKey in itemKeys:
            self.UnfitDrone(eachItemKey, scatter=False)

        if scatter:
            self.SendFittingSlotsChangedEvent()
            self.SendOnStatsUpdatedEvent()

    def UnfitDrone(self, itemKey, scatter = True):
        self.fittingDogmaLocation.UnregisterDroneFromActive(itemKey)
        self.UnfitModule(itemKey, scatter)

    def UnfitOneFighter(self, itemID):
        dogmaItem = self.fittingDogmaLocation.SafeGetDogmaItem(itemID)
        if not dogmaItem:
            return
        if dogmaItem.flagID == const.flagFighterBay:
            qty = dogmaItem.stacksize
            wantedNum = max(0, qty - 1)
            self.ModifyHoldItemStackSize(dogmaItem.typeID, wantedNum, const.flagFighterBay)
            self.SendFittingSlotsChangedEvent()
        else:
            self.UnfitModule(itemID)

    def UnfitModule(self, itemKey, scatter = True):
        fittingSvc = sm.GetService('fittingSvc')
        if not fittingSvc.IsShipSimulated():
            log.LogWarn('cant use ghost fitting to unfit non-simulated ship')
            return
        dogmaItem = self.fittingDogmaLocation.SafeGetDogmaItem(itemKey)
        flagID = None
        isPreview = False
        if dogmaItem:
            with self.EatCpuPowergridActiveUserErrors():
                flagID = dogmaItem.flagID
                self.PerformActionAndSetNewState(OFFLINE, dogmaItem.itemID, dogmaItem.typeID, flagID)
                isPreview = getattr(dogmaItem, 'isPreviewItem', False)
        self.fittingDogmaLocation.UnfitItemFromShip(itemKey)
        if scatter:
            self.SendFittingSlotsChangedEvent()
            self.SendOnStatsUpdatedEvent()
            if IsSubsystemFlag(flagID):
                self.SendSubSystemsChangedEvent()
                if not isPreview and not self.GetGhostFittingController().actuallyFittedSubsystemInfo:
                    self.SendSubSystemsReallyChanged()
        self.FlagSimulationChanged()
        return True

    def FitAmmoList(self, ammoInfo):
        for typeID, flagID in ammoInfo:
            self.FitAmmoToLocation(flagID, typeID)

    def FitAmmoToLocation(self, flagID, ammoTypeID):
        moduleItem = self.fittingDogmaLocation.GetModuleFromShipFlag(flagID)
        if not moduleItem:
            return None
        doesFit = ammoloadingUtils.IsChargeCompatibleWithLauncher(ammoTypeID, moduleItem.typeID, self.fittingDogmaLocation.dogmaStaticMgr)
        if not doesFit:
            return None
        oldAmmo = self.fittingDogmaLocation.GetChargeFromShipFlag(flagID)
        if oldAmmo:
            try:
                self.UnfitModule(oldAmmo.itemID, scatter=False)
            except Exception as e:
                print 'e = ', e

        shipID = self.fittingDogmaLocation.GetCurrentShipID()
        g = DBLessGhostFittingDataObject(shipID, flagID, ammoTypeID)
        chargeKey = g.GetItemKey()
        chargeItem = self.GetLoadedItem(chargeKey, g)
        GAV = self.fittingDogmaLocation.GetAccurateAttributeValue
        numCharges = GetNumChargesFullyLoaded(chargeKey, moduleItem.itemID, GAV)
        if numCharges < 1:
            self.UnfitModule(chargeKey, scatter=False)
            return None
        chargeItem.stacksize = numCharges
        return chargeItem

    def GetDefaultAndOverheatEffect(self, typeID):
        if typeID not in self.effectsByType:
            effectsForType = GetDefaultAndOverheatEffectForType(typeID)
            self.effectsByType[typeID] = effectsForType
        return self.effectsByType[typeID]

    def GetModuleStatus(self, itemKey, typeID, flagID):
        if IsSubsystemFlag(flagID):
            return ONLINE
        typeEffectInfo = self.GetDefaultAndOverheatEffect(typeID)
        currentState = self.GetCurrentState(itemKey, typeEffectInfo, flagID)
        return currentState

    def PerformActionAndSetNewState(self, newState, itemKey, typeID, flagID):
        typeEffectInfo = self.GetDefaultAndOverheatEffect(typeID)
        if newState == OVERHEATED and not typeEffectInfo.overloadEffect:
            newState = ACTIVE
        if newState == ACTIVE and not typeEffectInfo.defaultEffect:
            return
        if newState == ONLINE:
            self.fittingDogmaLocation.OnlineModule(itemKey)
        elif newState == ACTIVE:
            self.fittingDogmaLocation.ActivateModule(itemKey, typeID, flagID)
        elif newState == OVERHEATED:
            self.fittingDogmaLocation.ChangeModuleOverheatStatus(itemKey, typeID, flagID, start=True)
        elif newState == OFFLINE:
            self.fittingDogmaLocation.OfflineSimulatedModule(itemKey, typeID, flagID)
        elif newState == DEACTIVATING:
            self.fittingDogmaLocation.DeactivateSimulatedModule(itemKey, typeID)
        elif newState == DEHEATING:
            self.fittingDogmaLocation.ChangeModuleOverheatStatus(itemKey, typeID, flagID, start=False)
        elif newState == HEATING_FROM_OFFLINE:
            self.fittingDogmaLocation.OnlineModule(itemKey)
            self.fittingDogmaLocation.ChangeModuleOverheatStatus(itemKey, typeID, flagID, start=True)
        elif newState == ACTIVE_FROM_OFFLINE:
            self.fittingDogmaLocation.OnlineModule(itemKey)
            self.fittingDogmaLocation.ActivateModule(itemKey, typeID, flagID)
        else:
            log.LogWarn('something went wrong!')
            return

    def GetCurrentState(self, itemKey, typeEffectInfo, flagID):
        dogmaItem = self.fittingDogmaLocation.SafeGetDogmaItem(itemKey)
        if dogmaItem is None:
            return
        return GetCurrentStateForDogmaItemWithEffects(dogmaItem, typeEffectInfo, flagID)

    def GetNewState(self, currentState, typeEffectInfo, flagID):
        isRigSlot = IsRigSlot(flagID)
        newState = None
        isActivateable = bool(typeEffectInfo.defaultEffect and typeEffectInfo.isActivatable)
        isOverHeatable = bool(typeEffectInfo.overloadEffect)
        if currentState == ONLINE:
            if isActivateable:
                newState = ACTIVE
            else:
                newState = OFFLINE
        elif currentState == ACTIVE:
            if isOverHeatable:
                newState = OVERHEATED
            else:
                newState = OFFLINE
        elif currentState == OVERHEATED:
            newState = OFFLINE
        elif currentState == OFFLINE:
            if isRigSlot:
                newState = ACTIVE
            else:
                newState = ONLINE
        return newState

    def GetNewStateBackwards(self, currentState, typeEffectInfo, flagID):
        isRigSlot = IsRigSlot(flagID)
        isOverHeatable = bool(typeEffectInfo.overloadEffect)
        isActivateable = bool(typeEffectInfo.defaultEffect and typeEffectInfo.isActivatable)
        newState = None
        if currentState == ONLINE:
            newState = OFFLINE
        elif currentState == ACTIVE:
            newState = DEACTIVATING
        elif currentState == OVERHEATED:
            newState = DEHEATING
        elif currentState == OFFLINE:
            if isOverHeatable:
                newState = HEATING_FROM_OFFLINE
            elif isRigSlot or isActivateable:
                newState = ACTIVE_FROM_OFFLINE
            else:
                newState = ONLINE
        return newState

    def SwitchBetweenModes(self, itemKey, typeID, flagID):
        typeEffectInfo = self.GetDefaultAndOverheatEffect(typeID)
        currentState = self.GetCurrentState(itemKey, typeEffectInfo, flagID)
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            newState = self.GetNewStateBackwards(currentState, typeEffectInfo, flagID)
        else:
            newState = self.GetNewState(currentState, typeEffectInfo, flagID)
        if newState is not None:
            self.PerformActionAndSetNewState(newState, itemKey, typeID, flagID)
        else:
            log.LogWarn('newState was None')
        self.SendOnStatsUpdatedEvent()

    def OnlineAllModuleSlots(self):
        return self.OnlineAllInRack(allModuleSlots)

    def ActivateAllModuleSlots(self):
        return self.ActivateSlotList(allModuleSlots)

    def UnfitAllModules(self):
        self.UnfitAllModulesInRack(allSlots)

    def OnlineAllInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.OnlineSlotList(slotList)

    def ActivateAllHighSlots(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.ActivateSlotList(slotList)

    def OverheatAllInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.OverheatSlotList(slotList)

    def OfflineAllInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.OfflineSlotList(slotList)

    def UnfitAllAmmoInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.UnfitAllInSlotlist(slotList, unfitModules=False)

    def UnfitAllModulesInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.UnfitAllInSlotlist(slotList)

    def UnfitAllInSlotlist(self, slotList, unfitModules = True):
        for flagID in slotList:
            ghostAmmo = self.fittingDogmaLocation.GetChargeFromShipFlag(flagID)
            if ghostAmmo:
                self.UnfitModule(ghostAmmo.itemID)
            if unfitModules:
                ghostModule = self.fittingDogmaLocation.GetModuleFromShipFlag(flagID)
                if ghostModule:
                    self.PerformActionAndSetNewState(0, ghostModule.itemID, ghostModule.typeID, ghostModule.flagID)
                    self.UnfitModule(ghostModule.itemID)

    def OnlineSlotList(self, slotList):
        self.OfflineSlotList(slotList)
        self.PerformActionOnSlotList(ONLINE, slotList)

    def ActivateSlotList(self, slotList):
        self.OfflineSlotList(slotList)
        self.OnlineSlotList(slotList)
        self.PerformActionOnSlotList(ACTIVE, slotList)

    def OverheatSlotList(self, slotList):
        self.ActivateSlotList(slotList)
        self.PerformActionOnSlotList(OVERHEATED, slotList)

    def OfflineSlotList(self, slotList):
        self.PerformActionOnSlotList(OFFLINE, slotList)

    def OfflineAllModules(self):
        self.OfflineSlotList(invConst.hiSlotFlags)
        self.OfflineSlotList(invConst.medSlotFlags)
        self.OfflineSlotList(invConst.loSlotFlags)

    def PerformActionOnSlotList(self, action, slotList):
        for flagID in slotList:
            ghostItem = self.fittingDogmaLocation.GetModuleFromShipFlag(flagID)
            if ghostItem:
                if ghostItem.typeID in TYPEIDS_NOT_ACTIVE_BY_DEFAULT and action in (ACTIVE, OVERHEATED):
                    continue
                with self.EatCpuPowergridActiveUserErrors():
                    self.PerformActionAndSetNewState(action, ghostItem.itemID, ghostItem.typeID, flagID)

    @contextmanager
    def EatCpuPowergridActiveUserErrors(self):
        try:
            yield
        except UserError as e:
            if e.msg in USERERRORS_TO_EAT:
                self.LogInfo('UserError ingored when fitting= ' + e.msg + str(e.args))
            else:
                raise

    @contextmanager
    def PerformAndScatterUpdateEvent(self):
        try:
            yield
        finally:
            self.SendFittingSlotsChangedEvent()

    def TryExitSimulation(self, askQuestion = True):
        if sm.GetService('fittingSvc').IsShipSimulated():
            self.ToggleGhostFitting(askQuestion=askQuestion)

    def ToggleGhostFitting(self, askQuestion = True, *args):
        fittingSvc = sm.GetService('fittingSvc')
        isSimulated = fittingSvc.IsShipSimulated()
        if isSimulated:
            if askQuestion and not self.ShouldContinueAfterAskingAboutSwitchingShips(msg='ExitSimulationWarning'):
                return
            fittingSvc.SetSimulationState(False)
            shipID = GetActiveShip()
            newTypeID = GetTypeIDForController(shipID)
            self.ResetSimulationChangedFlag()
            self.SendOnSimulatedShipLoadedEvent(shipID, newTypeID)
            self.SendOnFeedbackTextChanged(None)
        else:
            self.LoadCurrentShip()

    def LoadCurrentShip(self):
        clientDL = self.clientDogmaIM.GetDogmaLocation()
        ship = clientDL.SafeGetDogmaItem(clientDL.GetActiveShipID(session.charid))
        if ship is None:
            return
        stanceID = shipstance.get_ship_stance(ship.itemID, ship.typeID)
        fitData = []
        chargeInfoToLoad = []
        originalItemIDByFlagAndTypeID = {}
        for module in ship.GetFittedItems().values():
            if isinstance(module, (ModuleDogmaItem, StructureModuleDogmaItem)):
                info = ItemInfo(module.itemID, module.typeID, module.flagID, 1)
                originalItemIDByFlagAndTypeID[module.typeID, module.flagID] = module.itemID
                fitData.append(info)
            elif isinstance(module, ChargeDogmaItem):
                info = (module.typeID, module.flagID)
                originalItemIDByFlagAndTypeID[module.typeID, module.flagID] = module.itemID
                chargeInfoToLoad.append(info)
            else:
                continue

        dynamicItemSvc = sm.GetService('dynamicItemSvc')
        for drone in ship.GetDrones().itervalues():
            itemId = None
            if dynamicItemSvc.IsDynamicItem(drone.typeID):
                itemId = drone.itemID
            info = ItemInfo(itemId, drone.typeID, const.flagDroneBay, drone.invItem.stacksize)
            fitData.append(info)

        shipInv = sm.GetService('invCache').GetInventoryFromId(session.shipid)
        visibleFittedItems = (i for i in shipInv.List() if inventorycommon.ItemIsVisible(i))
        for eachItem in visibleFittedItems:
            if eachItem.flagID in [const.flagCargo, const.flagFighterBay]:
                info = ItemInfo(eachItem.itemID, eachItem.typeID, eachItem.flagID, eachItem.stacksize)
                fitData.append(info)
            elif IsFighterTubeFlag(eachItem.flagID):
                squadronSize = eachItem.stacksize
                dogmaItem = clientDL.GetFightersForTube(eachItem.flagID)
                if dogmaItem:
                    squadronSize = dogmaItem.squadronSize
                info = ItemInfo(eachItem.itemID, eachItem.typeID, eachItem.flagID, squadronSize)
                fitData.append(info)

        blue.pyos.synchro.Yield()
        self.fittingName = cfg.evelocations.Get(session.shipid).name or StripTags(GetByLabel('UI/Fitting/FittingWindow/SimulatedShipName', typeID=ship.typeID))
        self._LoadSimulatedShipFromData(ship.typeID, fitData, oringalItemIDByFlagAndTypeID=originalItemIDByFlagAndTypeID)
        if stanceID:
            shipID = self.fittingDogmaLocation.GetCurrentShipID()
            if shipID:
                self.SetSimulatedStance(stanceID, shipID)
        self.FitAmmoList(chargeInfoToLoad)
        self.TriggerHistoryCorrection()
        self.ResetSimulationChangedFlag()

    def LoadCurrentShipExternal(self):
        self.OpenFittingWindowIfNeeded()
        self.LoadCurrentShip()

    def TriggerHistoryCorrection(self):
        self.historyController.TriggerHistoryCorrection(self.TakeSnapshot())

    def SimulateFitting(self, fitting, oringalItemIDByFlagAndTypeID = {}, chargesToLoad = None, *args):
        if getattr(fitting, 'isCurrentShip', False):
            return self.LoadCurrentShip()
        if evetypes.GetCategoryID(fitting.shipTypeID) not in (const.categoryShip, const.categoryStructure):
            return
        self.OpenFittingWindowIfNeeded()
        fittingID = getattr(fitting, 'fittingID', None)
        ownerID = getattr(fitting, 'ownerID', None)
        fitData = self._GetFitDataWithAutoFittedServiceModule(fitting.shipTypeID, fitting.fitData)
        self.LoadSimulatedFitting(fitting.shipTypeID, fittingID, ownerID, fitData, oringalItemIDByFlagAndTypeID=oringalItemIDByFlagAndTypeID)
        if chargesToLoad:
            self.FitAmmoList(chargesToLoad)
        self.fittingName = getattr(fitting, 'name', None) or StripTags(GetByLabel('UI/Fitting/FittingWindow/SimulatedShipName', typeID=fitting.shipTypeID))

    def _GetFitDataWithAutoFittedServiceModule(self, shipTypeID, fitData):
        if shipTypeID in AUTO_FITTED_SERVICES_BY_STRUCTURE_TYPE:
            serviceTypeID = AUTO_FITTED_SERVICES_BY_STRUCTURE_TYPE[shipTypeID]
            slotIsEmpty = invConst.flagServiceSlot0 not in {x.flagID for x in fitData}
            if slotIsEmpty and serviceTypeID not in {x.typeID for x in fitData}:
                fitData = fitData[:]
                fitData.append(ItemInfo(None, serviceTypeID, invConst.flagServiceSlot0, 1))
        return fitData

    def _GetItemInFlagQtyBytTypeID(self, allItems, holdFlagID):
        qtyByTypeID = defaultdict(int)
        for itemInfo in allItems:
            if itemInfo.flagID == holdFlagID:
                qtyByTypeID[itemInfo.typeID] += itemInfo.qty

        return qtyByTypeID

    def _GetItemInFlagQtyByTypeIDAndItemID(self, allItems, holdFlagID):
        qtyByTypeAndItemID = defaultdict(int)
        for itemInfo in allItems:
            if itemInfo.flagID == holdFlagID:
                qtyByTypeAndItemID[itemInfo.typeID, itemInfo.itemID] += itemInfo.qty

        return qtyByTypeAndItemID

    @telemetry.ZONE_METHOD
    def LoadSimulatedFitting(self, shipTypeID, fittingID, ownerID, fitData, oringalItemIDByFlagAndTypeID = {}):
        self._LoadSimulatedShipFromData(shipTypeID, fitData, oringalItemIDByFlagAndTypeID)
        self.lastLoadedFitInfo = (ownerID, fittingID)
        self.TriggerHistoryCorrection()

    def _UpdateFitData(self, fitData):
        if not fitData:
            return fitData
        ret = []
        for entry in fitData:
            if isinstance(entry, ItemInfo):
                ret.append(entry)
            else:
                typeID, flagID, qty = entry
                ret.append(ItemInfo(None, typeID, flagID, qty))

        return ret

    def _LoadSimulatedShipFromData(self, shipTypeID, fitData, oringalItemIDByFlagAndTypeID = {}, fittingSnapshot = None, askBeforeSwitching = True):
        fitData = self._UpdateFitData(fitData)
        self.failedDynamicTypesByFlagID.clear()
        if askBeforeSwitching and self.fittingDogmaLocation.GetCurrentShipID():
            if not self.ShouldContinueAfterAskingAboutSwitchingShips(msg='LoadSimulatedShip'):
                raise UserError('CustomNotify', {'notify': GetByLabel('UI/Fitting/FittingWindow/LoadngOfShipCancelled')})
        self.lastLoadedFitInfo = (None, None)
        self.fittingDogmaLocation.SetScatterOnOrOff(scatterOn=False)
        shipDogmaItem = self.LoadShip(shipTypeID)
        shipItemKey = shipDogmaItem.itemID
        sm.GetService('fittingSvc').SetSimulationState(True)
        self.SendOnSimulatedShipLoadedEvent(shipItemKey, shipTypeID)
        blue.pyos.synchro.Yield()
        fitData.sort(key=lambda x: x.flagID, reverse=True)
        rigsAndModulesInfo = [ m for m in fitData if m.flagID in allSlots ]
        for itemInfo in rigsAndModulesInfo:
            if not self.fittingDogmaLocation.SafeGetDogmaItem(shipItemKey):
                return
            newFlagID = self.fittingDogmaLocation.dogmaStaticMgr.GetTypeAttribute(itemInfo.typeID, const.attributeSubSystemSlot, None)
            if newFlagID:
                itemInfo.flagID = int(newFlagID)
            try:
                if itemInfo.itemID is None:
                    itemInfo.itemID = oringalItemIDByFlagAndTypeID.get((itemInfo.typeID, itemInfo.flagID), None)
                if dynamicitemattributes.IsDynamicType(itemInfo.typeID) and itemInfo.itemID is None:
                    self.failedDynamicTypesByFlagID[itemInfo.flagID] = itemInfo.typeID
                    continue
                self.FitModuleToShip(shipItemKey, itemInfo.flagID, itemInfo.typeID, originalItemID=itemInfo.itemID)
            finally:
                pass

        if fittingSnapshot:
            self._ActivateOnLoadingSnapshot(fittingSnapshot)
        else:
            self._ActivateOnLoading()
        self.RemoveInvalidDynamicDrones(fitData, fittingSnapshot)
        self.FitDrones(fitData, fittingSnapshot)
        self.FitFighters(fitData)
        self.AddItemsToCargo(fitData)
        self.fittingDogmaLocation.SetScatterOnOrOff(scatterOn=True)
        self.SendOnStatsUpdatedEvent()
        self.ResetSimulationChangedFlag()
        if IsModularShip(shipTypeID):
            self.SendSubSystemsChangedEvent()
        self.SendFittingSlotsChangedEvent()
        ghostifttingController = self.GetGhostFittingController()
        if not ghostifttingController:
            ghostifttingController = self.LoadGhostFittingController(shipItemKey)
        ghostifttingController.SetFailedModuleTypeIDs(self.failedDynamicTypesByFlagID)

    def _ActivateOnLoading(self):
        self.fittingDogmaLocation.SetScatterOnOrOff(scatterOn=False)
        self.ActivateSlotList(invConst.rigSlotFlags)
        self.OnlineAllModuleSlots()
        blue.pyos.synchro.Yield()
        self.fittingDogmaLocation.SetScatterOnOrOff(scatterOn=False)
        self.ActivateAllModuleSlots()

    def _ActivateOnLoadingSnapshot(self, snapshot):
        onlineModules = snapshot.GetOnlineModules()
        activeModules = snapshot.GetActiveModules()
        overheatedModules = snapshot.GetOverheatedModules()
        self.OfflineSlotList(snapshot.GetOfflineRigs())
        self.ActivateSlotList(snapshot.GetOnlineRigs())
        blue.pyos.synchro.Yield()
        if onlineModules:
            self.OnlineAllInRack(onlineModules)
        if activeModules:
            self.ActivateSlotList(activeModules)
        if overheatedModules:
            self.OverheatAllInRack(overheatedModules)
        self.SendFittingSlotsChangedEvent()

    def RemoveInvalidDynamicDrones(self, fitData, fittingSnapshot):
        dynamicItemSvc = sm.GetService('dynamicItemSvc')
        for item in fitData:
            if item.flagID == const.flagDroneBay and dynamicItemSvc.IsDynamicItem(item.typeID) and item.itemID is None:
                fitData.remove(item)

    @telemetry.ZONE_METHOD
    def FitDrones(self, fitData, fittingSnapshot = None):
        qtyByTypeAndItemID = self._GetItemInFlagQtyByTypeIDAndItemID(fitData, const.flagDroneBay)
        self.TryFitDronesToDroneBay(qtyByTypeAndItemID, False, fittingSnapshot)

    def FitFighters(self, fitData):
        qtyByTypeID = self._GetItemInFlagQtyBytTypeID(fitData, const.flagFighterBay)
        self.TryFitItemsToFighterBay(qtyByTypeID)
        for itemInfo in fitData:
            if IsFighterTubeFlag(itemInfo.flagID):
                self.FitFighterToTube(itemInfo.typeID, itemInfo.flagID, itemInfo.qty)

    def AddItemsToCargo(self, fitData):
        qtyByTypeID = self._GetItemInFlagQtyBytTypeID(fitData, const.flagCargo)
        self.TryFitItemsToCargo(qtyByTypeID, False)

    def TryLoadAmmo(self, fitData):
        uthread.new(self.TryLoadAmmo_thread, fitData)

    def TryLoadAmmo_thread(self, fitData):
        self.__WaitForInfoSvc()
        fittedItems = self.fittingDogmaLocation.GetFittedItemsToShip()
        flagsWithCharge = {x.flagID for x in fittedItems.values() if IsCharge(x.typeID)}
        modulesWithoutCharge = [ x for x in fittedItems.values() if x.flagID not in flagsWithCharge ]
        flagByModuleTypeIDs = defaultdict(set)
        for each in modulesWithoutCharge:
            flagByModuleTypeIDs[each.typeID].add(each.flagID)

        qtyByTypeID = self._GetItemInFlagQtyBytTypeID(fitData, const.flagCargo)
        typeAndQtyInCargo = qtyByTypeID.items()
        typeAndQtyInCargo.sort(key=lambda x: x[1], reverse=True)
        infoSvc = sm.GetService('info')
        chargeInfo = []
        for typeID, qty in typeAndQtyInCargo:
            if not IsCharge(typeID):
                continue
            if not flagByModuleTypeIDs:
                break
            usedWithTypeIDs = infoSvc.GetUsedWithTypeIDs(typeID)
            if not usedWithTypeIDs:
                continue
            usedWithTypeIDs = set(usedWithTypeIDs)
            inBoth = usedWithTypeIDs.intersection(flagByModuleTypeIDs)
            for eachModuleTypeID in inBoth:
                flagIDs = flagByModuleTypeIDs[eachModuleTypeID]
                for eachFlagID in flagIDs:
                    info = (typeID, eachFlagID)
                    chargeInfo.append(info)

                flagByModuleTypeIDs.pop(eachModuleTypeID)

        if chargeInfo:
            self.FitAmmoList(chargeInfo)
            self.SendOnStatsUpdatedEvent()
            self.SendFittingSlotsChangedEvent()
            self.ResetSimulationChangedFlag()

    def __WaitForInfoSvc(self):
        count = 0
        infoSvc = sm.GetService('info')
        while getattr(infoSvc, '_usedWithTypeIDs', None) is None or getattr(infoSvc, '_usedWithInitializing', False):
            if count > 30:
                break
            count += 1
            blue.pyos.synchro.SleepWallclock(100)

    def LoadShip(self, shipTypeID):
        shipDogmaItem = self.fittingDogmaLocation.LoadMyShip(shipTypeID)
        return shipDogmaItem

    def TryFitFakeAmmoToAllModulesFitted(self, ammoTypeIDs):
        if not sm.GetService('fittingSvc').IsShipSimulated():
            return
        fittedModules = self.fittingDogmaLocation.GetFittedItemsToShip().values()
        fittedModuleTypes = {x.typeID for x in fittedModules}
        for eachChargeTypeID in ammoTypeIDs:
            usedWith = sm.GetService('info').GetUsedWithTypeIDs(eachChargeTypeID)
            for eachModuleTypeID in usedWith:
                if eachModuleTypeID in fittedModuleTypes:
                    self.TryFitAmmoTypeToAll(eachModuleTypeID, eachChargeTypeID)
                    fittedModuleTypes.discard(eachModuleTypeID)
                if not fittedModuleTypes:
                    break

            if not fittedModuleTypes:
                break

    def TryFitAmmoTypeToAll(self, moduleTypeID, ammoTypeID):
        fittingSvc = sm.GetService('fittingSvc')
        if not fittingSvc.IsShipSimulated():
            return
        for flagID in const.hiSlotFlags + const.medSlotFlags + const.loSlotFlags:
            moduleItem = self.fittingDogmaLocation.GetModuleFromShipFlag(flagID)
            if moduleItem and moduleItem.typeID == moduleTypeID:
                self.FitAmmoToLocation(flagID, ammoTypeID)

        self.SendFittingSlotsChangedEvent()

    def TryFitModuleToOneSlot(self, moduleTypeID, preview = False, feedbackTimeOut = False, originalItemID = None):
        fittingSvc = sm.GetService('fittingSvc')
        shipID = self.fittingDogmaLocation.shipID
        if not fittingSvc.IsShipSimulated():
            return
        if evetypes.GetCategoryID(moduleTypeID) == const.categoryDrone:
            return self.FitADroneToShip(moduleTypeID, raiseError=False, sendUpdateEvent=True, itemID=originalItemID)
        if evetypes.GetCategoryID(moduleTypeID) == const.categoryFighter:
            return self.FitAFighterToTubeOrBay(moduleTypeID, qty=1)
        flagIDs = GetSlotListForTypeID(self.fittingDogmaLocation.dogmaStaticMgr, moduleTypeID)
        dogmaItemFitted = None
        errorInfo = None
        for flagID in flagIDs:
            oldGhostFittedItem = self.fittingDogmaLocation.GetModuleFromShipFlag(flagID)
            if oldGhostFittedItem and getattr(oldGhostFittedItem, 'isPreviewItem', None):
                self.UnfitModule(oldGhostFittedItem.itemID)
            dogmaItemFitted, errorInfo = self.FitModuleToShipAndChangeState(shipID, flagID, moduleTypeID, preview=preview, originalItemID=originalItemID)
            if dogmaItemFitted:
                break

        if dogmaItemFitted:
            self.SendFittingSlotsChangedEvent()
        self.SendOnFeedbackTextChanged(errorInfo, timeout=feedbackTimeOut)
        return dogmaItemFitted

    def ResetGhostFittingController(self):
        self.ghostFittingController = None

    def GetGhostFittingController(self):
        return self.ghostFittingController

    def LoadGhostFittingController(self, itemID):
        self.ghostFittingController = GetFittingController(itemID, ghost=True)
        return self.ghostFittingController

    @threadutils.throttled(0.5)
    def SendOnSimulatedShipLoadedEvent(self, shipItemKey, shipTypeID):
        ghostFittingController = self.GetGhostFittingController()
        if ghostFittingController:
            if ghostFittingController.IsControllerChanging(shipItemKey, shipTypeID, ghostFittingController.GetItemID(), ghostFittingController.GetTypeID()):
                ghostFittingController.on_controller_changing(shipItemKey)
                return
            ghostFittingController.OnSimulationStateChanged()
            uthread.new(ghostFittingController.OnSimulatedShipLoaded, shipItemKey, shipTypeID)

    @threadutils.throttled(0.5)
    def SendOnStatsUpdatedEvent(self):
        ghostFittingController = self.GetGhostFittingController()
        if ghostFittingController:
            ghostFittingController.UpdateStats()

    @threadutils.throttled(0.5)
    def SendFittingSlotsChangedEvent(self):
        ghostFittingController = self.GetGhostFittingController()
        if ghostFittingController:
            uthread.new(ghostFittingController.OnFittingSlotsChanged)

    @threadutils.throttled(0.5)
    def SendSubSystemsChangedEvent(self):
        ghostFittingController = self.GetGhostFittingController()
        if ghostFittingController:
            uthread.new(ghostFittingController.OnSubSystemsChanged)

    @threadutils.throttled(0.5)
    def SendSubSystemsReallyChanged(self):
        ghostFittingController = self.GetGhostFittingController()
        if ghostFittingController:
            uthread.new(ghostFittingController.OnSubSystemsReallyChanged)

    def SendOnFeedbackTextChanged(self, errorInfo, timeout = False):
        sm.ScatterEvent('OnFeedbackTextChanged', errorInfo, timeout)

    def LoadFakeItem(self, shipID, moduleTypeID):
        g = GhostFittingDataObject(shipID, flagID=FAKE_FLAGID, typeID=moduleTypeID)
        g.ownerID = None
        itemKey = g.GetItemKey()
        self.fittingDogmaLocation.LoadItem(itemKey=itemKey, invItem=g)
        dogmaItem = self.fittingDogmaLocation.SafeGetDogmaItem(itemKey)
        if not dogmaItem or dogmaItem.flagID != FAKE_FLAGID:
            return
        info = KeyVal(powerValue=self.fittingDogmaLocation.GetAttributeValue(itemKey, const.attributePower), cpuValue=self.fittingDogmaLocation.GetAttributeValue(itemKey, const.attributeCpu))
        self.fittingDogmaLocation.UnfitItemFromShip(itemKey)
        return info

    def IsSimulatingCurrentShipType(self):
        actualShip = self.clientDogmaLocation.GetShip()
        simulatedShip = self.fittingDogmaLocation.GetShip()
        return actualShip and simulatedShip and actualShip.typeID == simulatedShip.typeID

    def GetSimulatedShipStance(self, ship_id, type_id):
        inv = InventoryGhost(ship_id, invConst.flagHiddenModifers, self.fittingDogmaLocation, GhostFittingDataObject)
        currentStance = shipmode.get_current_ship_stance(type_id, inv.list_items())
        if currentStance is None:
            stancesByTypes = shipmode.data.get_stance_by_type(type_id).items()
            if not stancesByTypes:
                return
            stancesByTypes.sort(key=lambda x: x[1])
            inv.create_item(stancesByTypes[0][0])
        return shipmode.get_current_ship_stance(type_id, inv.list_items())

    def SetSimulatedStance(self, stance_id, ship_id):
        if not self.ghostFittingController:
            return
        inventory = InventoryGhost(ship_id, invConst.flagHiddenModifers, self.fittingDogmaLocation, GhostFittingDataObject)
        typeID = inventory.get_type_id(ship_id)
        notifier = StanceNotifier(self.ghostFittingController, ship_id)
        shipStance = shipmode.ShipStance(inventory, notifier, shipmode.data.get_modes_by_type(typeID))
        shipStance.set_stance(stance_id, 0)

    def ProcessSessionReset(self):
        self.simulationChanged = False

    def ShouldContinueAfterAskingAboutSwitchingShips(self, msg):
        if not self.simulationChanged:
            return True
        return self._ShouldContinueAfterAskingAboutSwitchingShips(msg)

    def _ShouldContinueAfterAskingAboutSwitchingShips(self, msg):
        dogmaItemKeys = set(self.fittingDogmaLocation.dogmaItems.keys())
        for itemID in (session.charid, self.fittingDogmaLocation.GetCurrentShipID()):
            dogmaItemKeys.discard(itemID)

        if not dogmaItemKeys:
            return True
        if eve.Message(msg, buttons=uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            return True
        return False

    def FlagSimulationChanged(self):
        if not self.simulationChanged:
            sm.ScatterEvent('OnSimulationChanged')
        self.simulationChanged = True

    def ResetSimulationChangedFlag(self):
        if self.simulationChanged:
            sm.ScatterEvent('OnSimulationChanged')
        self.simulationChanged = False

    def GetShipName(self):
        if sm.GetService('fittingSvc').IsShipSimulated():
            if self.simulationChanged:
                return '*' + self.fittingName
            return self.fittingName
        else:
            return cfg.evelocations.Get(session.shipid).name

    def SimulateCurrentShip(self):
        self.OpenFittingWindowIfNeeded()
        self.LoadCurrentShip()

    def OpenFittingWindowIfNeeded(self):
        from eve.client.script.ui.shared.fittingScreen.fittingWnd import FittingWindow
        wnd = FittingWindow.GetIfOpen()
        if wnd:
            wnd.Maximize()
        else:
            uicore.cmd.OpenFitting()

    def GetOriginalItemID(self, dogmaItemID):
        return dogmaItemID.split('_')[-1]

    def TakeSnapshot(self):
        dogmaLocation = sm.GetService('fittingSvc').GetCurrentDogmaLocation()
        ship = dogmaLocation.SafeGetDogmaItem(dogmaLocation.GetActiveShipID(session.charid))
        if ship is None:
            return
        dynamicItemSvc = sm.GetService('dynamicItemSvc')
        fitData = []
        chargeInfoToLoad = []
        oringalItemIDByFlagAndTypeID = {}
        currentStatusByFlagID = {}
        for module in ship.GetFittedItems().values():
            if isinstance(module, (ModuleDogmaItem, StructureModuleDogmaItem)):
                info = ItemInfo(module.itemID, module.typeID, module.flagID, 1)
                fitData.append(info)
                currentStatusByFlagID[module.flagID] = self.GetModuleStatus(module.itemID, module.typeID, module.flagID)
                oringalItemIDByFlagAndTypeID[module.typeID, module.flagID] = module.itemID
            elif isinstance(module, ChargeDogmaItem):
                info = (module.typeID, module.flagID)
                chargeInfoToLoad.append(info)
            else:
                continue

        activeDrones = dogmaLocation.GetActiveDrones()
        activeDronesByTypeID = defaultdict(int)
        for drone in ship.GetDrones().itervalues():
            info = ItemInfo(self.GetOriginalItemID(drone.itemID), drone.typeID, const.flagDroneBay, getattr(drone.invItem, 'stacksize', 1))
            fitData.append(info)
            if drone.itemID in activeDrones:
                activeDronesByTypeID[drone.typeID] += 1

        shipStanceID = self.GetSimulatedShipStance(ship.itemID, ship.typeID)
        flagsToInclude = [const.flagCargo, const.flagFighterBay] + const.fighterTubeFlags
        for eachFlagID in flagsToInclude:
            currentItems = self.fittingDogmaLocation.GetHoldItems(eachFlagID)
            for eachItem in currentItems.itervalues():
                info = ItemInfo(eachItem.itemID, eachItem.typeID, eachItem.flagID, eachItem.stacksize)
                fitData.append(info)

        return FittingSnapshot(ship.typeID, fitData, chargeInfoToLoad, oringalItemIDByFlagAndTypeID, activeDronesByTypeID, shipStanceID, currentStatusByFlagID=currentStatusByFlagID, shipName=self.GetShipName())

    def LoadSnapshot(self, snapshotData, updateCode):
        if snapshotData:
            if updateCode != UPDATE_CODE_SELECTED:
                return
            self._LoadSimulatedShipFromData(snapshotData.shipTypeID, snapshotData.fitData, oringalItemIDByFlagAndTypeID=snapshotData.oringalItemIDByFlagAndTypeID, fittingSnapshot=snapshotData, askBeforeSwitching=False)
            self.FitAmmoList(snapshotData.chargeInfoToLoad)
            if snapshotData.shipStanceID is not None:
                shipID = self.fittingDogmaLocation.GetCurrentShipID()
                if shipID:
                    self.SetSimulatedStance(snapshotData.shipStanceID, shipID)
            self.ResetSimulationChangedFlag()
            self.fittingName = snapshotData.shipName or StripTags(GetByLabel('UI/Fitting/FittingWindow/SimulatedShipName', typeID=snapshotData.shipTypeID))
            sm.ScatterEvent('OnSimulationChanged')

    def SaveSnapshot(self, *args):
        snapShotData = self.TakeSnapshot()
        if snapShotData:
            self.historyController.AddToHistory(snapShotData)

    def IsAllowedToLoadSnapshot(self, currentlySelectedInBar, toBeLoaded):
        if self.fittingDogmaLocation.GetCurrentShipID():
            snapShotData = self.TakeSnapshot()
            if currentlySelectedInBar == snapShotData:
                return True
            if not self._ShouldContinueAfterAskingAboutSwitchingShips(msg='LoadSimulatedShip'):
                eve.Message('CustomNotify', {'notify': GetByLabel('UI/Fitting/FittingWindow/LoadngOfShipCancelled')})
                return False
        return True

    def GetBitHintFromData(self, bitData):
        return bitData.shipName


class StanceNotifier(object):

    def __init__(self, controller, ship_id):
        self.ship_id = ship_id
        self.controller = controller

    def on_stance_changed(self, old_stance_id, new_stance_id):
        self.controller.OnStanceActive(self.ship_id, new_stance_id)
        sm.ScatterEvent('OnStanceActive', self.ship_id, new_stance_id)


class ItemInfo(object):

    def __init__(self, itemID, typeID, flagID, qty):
        self.itemID = itemID
        self.typeID = typeID
        self.flagID = flagID
        self.qty = qty

    def __repr__(self):
        return '<ItemInfo %s>, %s' % (self.__dict__, id(self))
