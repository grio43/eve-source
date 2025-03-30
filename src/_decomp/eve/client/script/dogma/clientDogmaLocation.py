#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\dogma\clientDogmaLocation.py
import itertools
import sys
import utillib
import weakref
from collections import defaultdict
import blue
import dogma.data
import evetypes
import localization
import log
import telemetry
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.logUtil import LogNotice
from carbonui import uiconst
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from carbonui.util.various_unsorted import SortListOfTuples
from dogma.ammoloadingUtils import IsChargeCompatibleWithLauncher, GetModuleCapacityForAmmoType
from dogma.attributes.format import GetFormatAndValue
from dogma.dogmaWrappers import WrappedMethod
from dogma.effects.environment import Environment
from eve.client.script.dogma.clientDogmaUtilFunc import WasLaunchingDrone, WasLaunchingFighter
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
from eve.common.script.dogma.baseDogmaLocation import BaseDogmaLocation
from eve.common.script.net import eveMoniker
from eve.common.script.sys import eveCfg
from eve.common.script.sys.eveCfg import IsControllingStructure
from eveexceptions import UserError
from inventorycommon.util import IsFittingFlag, IsFittingModule, IsFighterTubeFlag, IsShipFittingFlag
from itertoolsext import first
from menu import MenuLabel
from shipfitting.droneUtil import GetOptimalDroneDamage
from shipfitting.fittingDogmaLocationUtil import GetDamageFromItem, GetChanceToHit
GROUPALL_THROTTLE_TIMER = 2 * const.SEC

class DogmaLocation(BaseDogmaLocation):
    __notifyevents__ = ['OnModuleAttributeChanges',
     'OnWeaponBanksChanged',
     'OnWeaponGroupDestroyed',
     'OnServerBrainUpdated',
     'OnHeatAdded',
     'OnHeatRemoved',
     'OnDroneControlLost',
     'OnDroneStateChange2',
     'OnFighterRemovedFromControllerClient']

    def __init__(self, broker, charBrain = None):
        super(DogmaLocation, self).__init__(broker)
        self.instanceCache = {}
        self.scatterAttributeChanges = True
        self.dogmaStaticMgr = sm.GetService('clientDogmaStaticSvc')
        self.remoteDogmaLM = None
        self.godma = sm.GetService('godma')
        self.stateMgr = self.godma.GetStateManager()
        self.skillSvc = sm.GetService('skills')
        self.fakeInstanceRow = None
        self.items = {}
        self.nextItemID = 0
        self.effectCompiler = sm.GetService('clientEffectCompiler')
        self.brain = None
        if charBrain:
            initialBrain = (-1,) + charBrain[1:]
            self.SetBrainData(session.charid, initialBrain)
        self.lastGroupAllRequest = None
        self.lastUngroupAllRequest = None
        self.shipIDBeingDisembarked = None
        self.shipIDBeingEmbarked = None
        self.locationName = 'ClientDogmaLocation'
        sm.RegisterNotify(self)

    def SetBrainData(self, charID, brain):
        self.brain = brain

    def GetBrainData(self, charID):
        return self.brain

    def HasBrainData(self, charID):
        return self.brain is not None

    def GetCurrentShipID(self):
        return self.shipsByPilotID.get(session.charid, None)

    def GetActiveShipID(self, characterID = None):
        return session.shipid

    def CheckApplyBrainEffects(self, shipID):
        return shipID in self.dogmaItems

    def GetMatchingAmmo(self, shipID, itemID):
        ammoInfoByTypeID = defaultdict(lambda : utillib.KeyVal(singletons=[], nonSingletons=[]))
        dogmaItem = self.dogmaItems[itemID]
        for item in self.broker.invCache.GetInventoryFromId(shipID).List(const.flagCargo):
            if self.GetMissingSkills(item.typeID):
                continue
            if IsChargeCompatibleWithLauncher(item.typeID, dogmaItem.typeID, self.dogmaStaticMgr):
                if item.singleton:
                    ammoInfoByTypeID[item.typeID].singletons.append(item)
                else:
                    ammoInfoByTypeID[item.typeID].nonSingletons.append(item)

        return ammoInfoByTypeID

    def AddToMenuFromAmmoInfo(self, itemID, chargeTypeID, ammoInfo, minimumAmmoNeeded, labels, numDamageTypes = None):
        menu = []
        menuClass = None
        if numDamageTypes >= 2:
            from eve.client.script.ui.control.eveMenu import AmmoMenuEntryView2
            menuClass = AmmoMenuEntryView2
        elif numDamageTypes == 1:
            from eve.client.script.ui.control.eveMenu import AmmoMenuEntryView
            menuClass = AmmoMenuEntryView
        if sum((item.stacksize for item in ammoInfo.singletons)) >= minimumAmmoNeeded:
            text = MenuLabel(labels[0], {'typeID': chargeTypeID})
            menu.append((text,
             self.LoadChargesToModule,
             (itemID, ammoInfo.singletons, ammoInfo.singletons[0].locationID),
             None,
             menuClass,
             None,
             chargeTypeID))
        noOfNonSingletons = sum((item.stacksize for item in ammoInfo.nonSingletons))
        if noOfNonSingletons >= minimumAmmoNeeded:
            text = MenuLabel(labels[1], {'typeID': chargeTypeID,
             'sumqty': noOfNonSingletons})
            menu.append((text,
             self.LoadChargesToModule,
             (itemID, ammoInfo.nonSingletons, ammoInfo.nonSingletons[0].locationID),
             None,
             menuClass,
             None,
             chargeTypeID))
        return menu

    def GetAmmoMenu(self, shipID, itemID, existingCharge, roomForReload):
        usedChargeType = self.godma.GetStateManager().GetAmmoTypeForModule(itemID)
        ammoInfoByTypeID = self.GetMatchingAmmo(shipID, itemID)
        sortedCharges = self.GetSortedCharges(itemID, ammoInfoByTypeID.keys(), existingCharge)
        numDamageTypes = self._FindNumDamageTypes(sortedCharges)
        try:
            minimumAmmoNeeded = len(self.GetModulesInBank(shipID, itemID))
        except TypeError:
            minimumAmmoNeeded = 1

        menu = []
        if usedChargeType in ammoInfoByTypeID and roomForReload:
            ammoInfo = ammoInfoByTypeID[usedChargeType]
            menuItems = self.AddToMenuFromAmmoInfo(itemID, usedChargeType, ammoInfo, minimumAmmoNeeded, ('UI/Inflight/ModuleRacks/ReloadUsed', 'UI/Inflight/ModuleRacks/Reload'), numDamageTypes)
            if menuItems:
                menu.extend(menuItems)
                menu.append((MenuLabel('UI/Inflight/ModuleRacks/ReloadAll'), uicore.cmd.GetCommandToExecute('CmdReloadAmmo')))
        if existingCharge and not self.godma.GetStateManager().IsModuleReloading(itemID):
            relevantOwner = session.charid
            label = 'UI/Inflight/ModuleRacks/UnloadToCargo'
            if IsControllingStructure() and shipID == session.structureid:
                label = 'UI/Inflight/ModuleRacks/UnloadToAmmoHold'
                relevantOwner = sm.GetService('structureDirectory').GetStructureInfo(shipID).ownerID
            shipItem = self.dogmaItems[shipID]
            flagID = const.flagCargo
            if shipItem.groupID == const.groupFlagCruiser:
                flagID = const.flagSpecializedAmmoHold
                label = 'UI/Inflight/ModuleRacks/UnloadToAmmoHold'
            menu.append((MenuLabel(label), self.UnloadAmmoToContainer, (shipID, existingCharge, (shipID, relevantOwner, flagID))))
        otherChargeMenu = []
        for chargeTypeID in sortedCharges:
            ammoInfo = ammoInfoByTypeID[chargeTypeID]
            if chargeTypeID == usedChargeType:
                continue
            otherChargeMenu.extend(self.AddToMenuFromAmmoInfo(itemID, chargeTypeID, ammoInfo, minimumAmmoNeeded, ('UI/Inflight/ModuleRacks/AmmoTypeAndStatus', 'UI/Inflight/ModuleRacks/AmmoTypeAndQuantity'), numDamageTypes))

        menu.extend(otherChargeMenu)
        return menu

    def GetSortedCharges(self, moduleID, ammoTypeIDs, existingCharge):
        typeIDsWithRangeInfo = []
        rest = []
        weaponRangeForModule = self.GetAccurateAttributeValue(moduleID, const.attributeMaxRange)
        weaponFalloffForModule = self.GetAccurateAttributeValue(moduleID, const.attributeFalloff)
        if weaponRangeForModule and existingCharge:
            existingRangeMultiplier = self.GetAccurateAttributeValue(existingCharge.itemID, const.attributeWeaponRangeMultiplier)
            if existingRangeMultiplier:
                weaponRangeForModule = weaponRangeForModule / existingRangeMultiplier
            existingFalloffMultiplier = self.GetAccurateAttributeValue(existingCharge.itemID, const.attributeFallofMultiplier)
            if existingFalloffMultiplier:
                weaponFalloffForModule = weaponFalloffForModule / existingFalloffMultiplier
        for eachTypeID in ammoTypeIDs:
            rangeForCharge = None
            rangeMultiplier = self.dogmaStaticMgr.GetTypeAttribute(eachTypeID, const.attributeWeaponRangeMultiplier)
            if rangeMultiplier:
                falloffBonus = self.dogmaStaticMgr.GetTypeAttribute(eachTypeID, const.attributeFallofMultiplier, 1.0)
                rangeWithFalloff = falloffBonus * weaponFalloffForModule + rangeMultiplier * weaponRangeForModule
                rangeForCharge = rangeWithFalloff
            else:
                flightTime = self.dogmaStaticMgr.GetTypeAttribute(eachTypeID, const.attributeExplosionDelay)
                if flightTime:
                    velocity = self.dogmaStaticMgr.GetTypeAttribute(eachTypeID, const.attributeMaxVelocity)
                    rangeForCharge = flightTime * velocity / 1000.0
            if rangeForCharge:
                sortKey = (-rangeForCharge, evetypes.GetName(eachTypeID))
                typeIDsWithRangeInfo.append((sortKey, eachTypeID))
            else:
                rest.append(eachTypeID)

        sortedCharges = SortListOfTuples(typeIDsWithRangeInfo)
        rest = localization.util.Sort(rest, key=lambda x: evetypes.GetName(x))
        return sortedCharges + rest

    def _FindNumDamageTypes(self, sortedCharges):
        numDamageTypes = 0
        for eachTypeID in sortedCharges:
            numDamageTypes = 0
            for attrID in const.damageTypeAttributes:
                value = self.dogmaStaticMgr.GetTypeAttribute(eachTypeID, attrID)
                if value:
                    numDamageTypes += 1
                if numDamageTypes >= 2:
                    return numDamageTypes

        return numDamageTypes

    @WrappedMethod
    @telemetry.ZONE_METHOD
    def MakeShipActive(self, shipID, shipState = None):
        uthread.pool('MakeShipActive', self._MakeShipActive, shipID, shipState)

    @WrappedMethod
    @telemetry.ZONE_METHOD
    def _MakeShipActive(self, shipID, shipState):
        if shipID is None:
            log.LogTraceback('Unexpectedly got shipID = None')
            return
        if shipID == self.locationID:
            log.LogTraceback('ClientDogmaLocation is attempting to activate itself as a characters shipID!')
            return
        uthread.Lock(self, 'makeShipActive')
        try:
            self.shipIDBeingDisembarked = self.GetCurrentShipID()
            self.shipIDBeingEmbarked = shipID
            if self.GetCurrentShipID() == shipID:
                self.shipIDBeingEmbarked = self.shipIDBeingDisembarked = None
                return
            while not session.IsItSafe():
                self.LogInfo('MakeShipActive - session is mutating. Sleeping for 250ms')
                blue.pyos.synchro.SleepSim(250)

            self.UpdateRemoteDogmaLocation()
            oldShipID = self.GetCurrentShipID()
            if shipState is None:
                sessionMgr = sm.GetService('sessionMgr')
                shipState = sessionMgr.PerformSelectiveSessionChange('board', 'board', False, self.remoteShipMgr.Board, shipID, session.shipid)
            self.instanceCache, self.instanceFlagQuantityCache, self.wbData, heatStates = shipState
            if oldShipID and oldShipID in self.dogmaItems:
                self.RemoveBrainEffects(oldShipID, session.charid, 'clientDogmaLocation._MakeShipActive')
            self.scatterAttributeChanges = False
            try:
                LogNotice('_MakeShipActive: Calling LoadItem on new shipID=', shipID)
                if oldShipID is not None:
                    LogNotice('_MakeShipActive: Unfitting oldShipID=', oldShipID)
                    self.UnfitItemFromLocation(oldShipID, session.charid)
                if shipID is not None:
                    LogNotice('_MakeShipActive: Calling OnCharacterEmbarkation')
                    if not oldShipID:
                        self.LoadItem(session.charid)
                        self.SetWeaponBanks(shipID, self.wbData)
                    else:
                        if oldShipID and oldShipID in self.dogmaItems:
                            LogNotice('_MakeShipActive: Unloading oldShipID=', oldShipID)
                            self.UninstallPilotFromShipAndItems(oldShipID)
                            self.UnloadItem(oldShipID)
                        self.OnCharacterEmbarkation(session.charid, shipID, switching=oldShipID is not None)
                        LogNotice('_MakeShipActive: Calling SetWeaponBanks')
                        self.SetWeaponBanks(shipID, self.wbData)
                        self.LoadItemsInLocation(shipID)
                        sm.ChainEvent('ProcessActiveShipChanged', shipID, oldShipID)
            finally:
                self.scatterAttributeChanges = True

            self.ClearInstanceCache()
        finally:
            self.shipIDBeingDisembarked = None
            self.shipIDBeingEmbarked = None
            uthread.UnLock(self, 'makeShipActive')

        LogNotice('_MakeShipActive: DONE')

    def WaitForShip(self):
        startTime = blue.os.GetWallclockTime()
        while self.IsSwitchingShips() and blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTime()) < 2000:
            blue.pyos.synchro.Sleep(100)

    def IsSwitchingShips(self):
        return self.shipIDBeingDisembarked is not None

    def ClearInstanceCache(self):
        self.instanceCache = {}
        self.instanceFlagQuantityCache = {}
        self.wbData = None

    @telemetry.ZONE_METHOD
    def UpdateRemoteDogmaLocation(self):
        if session.stationid is not None:
            self.remoteDogmaLM = eveMoniker.GetStationDogmaLocation()
            self.remoteShipMgr = eveMoniker.GetStationShipAccess()
            self.locationGroup = const.groupStation
            self.locationID = session.stationid
        else:
            self.remoteDogmaLM = eveMoniker.CharGetDogmaLocation()
            self.remoteShipMgr = eveMoniker.GetShipAccess()
            self.locationGroup = const.groupSolarSystem
            self.locationID = session.solarsystemid

    @telemetry.ZONE_METHOD
    def OnModuleAttributeChanges(self, changes):
        changes.sort(key=lambda change: change[4])
        for change in changes:
            try:
                eventName, ownerID, itemID, attributeID, time, newValue, oldValue, _ = change
                if attributeID == const.attributeQuantity:
                    if isinstance(itemID, tuple) and not self.IsItemLoaded(itemID[0]):
                        self.LogWarn("got an module attribute change and the item wasn't loaded", itemID)
                        continue
                    if newValue == 0:
                        self.SetAttributeValue(itemID, const.attributeQuantity, newValue)
                        self.UnfitAndUnloadItem(itemID[0], itemID)
                    else:
                        if itemID != self.GetSubLocation(itemID[0], itemID[1]):
                            self.FitItemToLocation(itemID[0], itemID, itemID[1])
                        self.dogmaItems[itemID].attributes[attributeID].SetBaseValue(newValue)
                elif attributeID == const.attributeIsOnline:
                    if not self.IsItemLoaded(itemID):
                        continue
                    if newValue == self.GetAttributeValue(itemID, const.attributeIsOnline):
                        continue
                    if newValue == 0:
                        self.StopEffect(const.effectOnline, itemID)
                    else:
                        self.Activate(itemID, const.effectOnline)
                elif self.IsItemLoaded(itemID) and attributeID in self.dogmaStaticMgr.damageStateAttributes:
                    dogmaItem = self.dogmaItems[itemID]
                    dogmaItem.attributes[attributeID].SetBaseValue(newValue)
                    sm.ScatterEvent('OnDamageStateChanged', itemID, attributeID, newValue, oldValue)
                elif self.IsItemLoaded(itemID) and attributeID in const.heatAttributes:
                    dogmaItem = self.dogmaItems[itemID]
                    dogmaItem.attributes[attributeID].SetBaseValue(newValue)
            except Exception as e:
                log.LogException('OnModuleAttributeChanges::Unexpected exception')
                sys.exc_clear()

    def LoadItem(self, itemKey, **kwargs):
        if itemKey == session.locationid:
            return itemKey
        super(DogmaLocation, self).LoadItem(itemKey, **kwargs)

    @telemetry.ZONE_METHOD
    def FitItemToLocation(self, locationID, itemID, flagID):
        if self._IsLocationIDInvalidForFitting(locationID):
            return
        super(DogmaLocation, self).FitItemToLocation(locationID, itemID, flagID)

    @telemetry.ZONE_METHOD
    def UnfitItemFromLocation(self, locationID, itemID, flushEffects = False):
        super(DogmaLocation, self).UnfitItemFromLocation(locationID, itemID, flushEffects)
        self.ScheduleCheckPowerCpuRequirementForOnlineModules(locationID)

    @telemetry.ZONE_METHOD
    def GetChargeNonDB(self, shipID, flagID):
        for itemID, fittedItem in self.dogmaItems[shipID].GetFittedItems().iteritems():
            if isinstance(itemID, tuple):
                continue
            if fittedItem.flagID != flagID:
                continue
            if fittedItem.categoryID == const.categoryCharge:
                return fittedItem

    @telemetry.ZONE_METHOD
    def GetSubSystemInFlag(self, shipID, flagID):
        fittedItems = self.GetFittedItemsToShip()
        itemsByFlagID = {x.flagID:x for x in fittedItems.itervalues()}
        return itemsByFlagID.get(flagID)

    @telemetry.ZONE_METHOD
    def GetItem(self, itemID):
        session.WaitUntilSafe()
        if itemID == self.GetCurrentShipID() or itemID == self.shipIDBeingEmbarked:
            return self.broker.invCache.GetInventoryFromId(itemID, locationID=session.stationid).GetItem()
        try:
            return self.items[itemID]
        except KeyError:
            sys.exc_clear()

        return self.godma.GetItem(itemID)

    @telemetry.ZONE_METHOD
    def GetCharacter(self, itemID, flush):
        return self.GetItem(itemID)

    @telemetry.ZONE_METHOD
    def Activate(self, itemID, effectID):
        dogmaItem = self.dogmaItems[itemID]
        envInfo = dogmaItem.GetEnvironmentInfo()
        env = Environment(envInfo.itemID, envInfo.charID, envInfo.shipID, envInfo.targetID, envInfo.otherID, effectID, weakref.proxy(self), None, envInfo.structureID)
        env.dogmaLM = self
        self.StartEffect(effectID, itemID, env)

    @telemetry.ZONE_METHOD
    def PostStopEffectAction(self, effectID, dogmaItem, activationInfo, *args):
        super(DogmaLocation, self).PostStopEffectAction(effectID, dogmaItem, activationInfo, *args)
        if effectID == const.effectOnline:
            self.ScheduleCheckPowerCpuRequirementForOnlineModules(dogmaItem.locationID)

    @telemetry.ZONE_METHOD
    def GetInstance(self, item):
        try:
            return self.instanceCache[item.itemID]
        except KeyError:
            sys.exc_clear()

        instanceRow = [item.itemID]
        godmaItem = self.broker.godma.GetItem(item.itemID)
        for attributeID in self.GetAttributesByIndex().itervalues():
            instanceRow.append(getattr(godmaItem, self.dogmaStaticMgr.attributes[attributeID].name, 0))

        return instanceRow

    def GetAccurateAttributeValue(self, itemID, attributeID, *args):
        godmaItem = self.godma.GetItem(itemID)
        isDocked = bool(session.stationid or session.structureid)
        if isDocked or godmaItem is None:
            return self.GetAttributeValue(itemID, attributeID)
        else:
            return self.GetGodmaAttributeValue(itemID, attributeID)

    @telemetry.ZONE_METHOD
    def GetMissingSkills(self, typeID, skillSvc = None):
        if skillSvc is None:
            skillSvc = sm.GetService('skills')
        return super(DogmaLocation, self).GetMissingSkills(typeID, skillSvc.GetSkills())

    @telemetry.ZONE_METHOD
    def CheckSkillRequirementsForType(self, _, typeID, errorMsgName):
        missingSkills = self.GetMissingSkills(typeID)
        if len(missingSkills) > 0:
            nameList = []
            for skillTypeID, requiredSkillLevel in missingSkills.iteritems():
                nameList.append(localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndLevel', skill=skillTypeID, amount=requiredSkillLevel))

            raise UserError(errorMsgName, {'requiredSkills': localization.formatters.FormatGenericList(nameList),
             'item': typeID,
             'skillCount': len(nameList)})
        return missingSkills

    @telemetry.ZONE_METHOD
    def LoadItemsInLocation(self, itemID):
        if itemID in (session.charid, self.GetCurrentShipID(), self.shipIDBeingEmbarked):
            dogmaItem = self.dogmaItems[itemID]
            self.LogInfo('LoadItemsInLocation %s' % itemID)
            self.UpdateRemoteDogmaLocation()
            itemInv = self.broker.invCache.GetInventoryFromId(itemID, locationID=self.locationID)
            for item in sorted(itemInv.List(), key=lambda x: x.categoryID not in (const.categoryModule, const.categoryStructureModule)):
                try:
                    if dogmaItem.ValidFittingFlag(item.flagID):
                        self.items[item.itemID] = item
                        self.LoadItem(item.itemID, invItem=item)
                except Exception:
                    if item.itemID in self.items:
                        del self.items[item.itemID]
                    log.LogException('LoadItemsInLocation %s, %s' % (itemID, evetypes.GetName(item.typeID)))
                    sys.exc_clear()

    def UnloadItem(self, itemKey, item = None):
        super(DogmaLocation, self).UnloadItem(itemKey, item)
        if itemKey in self.items:
            del self.items[itemKey]

    def UnfitAndUnloadItem(self, locationID, itemID):
        self.UnfitItemFromLocation(locationID, itemID)
        self.UnloadItem(itemID)

    def UnloadItemsInLocation(self, locationID):
        if locationID in (session.charid, self.GetCurrentShipID(), self.shipIDBeingEmbarked):
            self.LogInfo('UnloadItemsInLocation %s' % locationID)
            self.UpdateRemoteDogmaLocation()
            itemInv = self.broker.invCache.GetInventoryFromId(locationID, locationID=self.locationID)
            for item in itemInv.List():
                try:
                    self.UnfitItem(item.itemID)
                    self.UnloadItem(item.itemID, item)
                    if item.itemID in self.items:
                        del self.items[item.itemID]
                except:
                    if item.itemID not in self.items:
                        self.items[item.itemID] = item
                    log.LogException('UnloadItemsInLocation %s, %s' % (locationID, evetypes.GetName(item.typeID)))
                    sys.exc_clear()

    def GetSensorStrengthAttribute(self, shipID):
        maxAttributeID = None
        maxValue = None
        for attributeID in (const.attributeScanGravimetricStrength,
         const.attributeScanLadarStrength,
         const.attributeScanMagnetometricStrength,
         const.attributeScanRadarStrength):
            val = self.GetAttributeValue(shipID, attributeID)
            if val > maxValue:
                maxValue, maxAttributeID = val, attributeID

        return (maxAttributeID, maxValue)

    def UnfitItem(self, itemID):
        if itemID == session.charid:
            self.UnboardShip(session.charid)
        else:
            locationID = self.dogmaItems[itemID].locationID
            self.UnfitAndUnloadItem(locationID, itemID)
        if itemID in self.items:
            del self.items[itemID]
        if itemID in self.instanceCache:
            del self.instanceCache[itemID]

    def UnboardShip(self, charID):
        char = self.dogmaItems[charID]
        charItems = char.GetFittedItems()
        for implant in charItems.itervalues():
            for effectID in implant.activeEffects.keys():
                self.StopEffect(effectID, implant.itemID)

        oldShipID = self.GetCurrentShipID()
        self.UnfitItemFromLocation(self.GetCurrentShipID(), charID)

    def FitItem(self, item):
        if self._IsLocationIDInvalidForFitting(item.locationID):
            return
        self.items[item.itemID] = item
        self.LoadItem(item.itemID)
        self.FitItemToLocation(item.locationID, item.itemID, item.flagID)

    def GetChanceToHit(self, shipID, targetID):
        trackingSpeed, falloff, maxRange, optimalSig = GetChanceToHit(shipID, self)
        bp = self.broker.michelle.GetBallpark()
        ball = bp.slimItems.get(targetID)
        if ball:
            targetSig = bp.slimItems.get(targetID).signatureRadius
            return (bp._parent_GetAccuracy(shipID, targetID, maxRange, falloff, trackingSpeed, targetSig, optimalSig)[0], (trackingSpeed,
              maxRange,
              falloff,
              optimalSig))
        raise RuntimeError('target not found')

    def OnItemChange(self, item, change, location):
        wasFitted = item.itemID in self.dogmaItems
        isFitted = self.IsFitted(item)
        wasLaunchingDrones = False
        wasLaunchingFighters = False
        if wasFitted and not isFitted and not isinstance(item.itemID, tuple):
            if item.categoryID == const.categoryDrone:
                wasLaunchingDrones = self._WasLaunchingDrone(item, change)
                if not wasLaunchingDrones:
                    self.LogNotice('Unfitting item as a result from item change', item, change)
                    self.UnfitAndUnloadItem(self.GetCurrentShipID(), item.itemID)
            elif item.categoryID == const.categoryFighter:
                wasLaunchingFighters = self._WasLaunchingFighter(item, change)
                if not wasLaunchingFighters:
                    self.LogNotice('Unfitting item as a result from item change', item, change)
                    self.UnfitAndUnloadItem(self.GetCurrentShipID(), item.itemID)
            else:
                self.UnfitItem(item.itemID)
        if not wasFitted and isFitted and not isinstance(item.itemID, tuple):
            self.LogNotice('Fitting item as a result from item change', item, change)
            self.FitItem(item)
        if wasFitted and isFitted and const.ixFlag in change:
            self.dogmaItems[item.itemID].flagID = item.flagID
        if isFitted and const.ixStackSize in change:
            self.SetAttributeValue(item.itemID, const.attributeQuantity, item.stacksize)
        try:
            dogmaItem = self.dogmaItems[item.itemID]
        except KeyError:
            pass
        else:
            oldLocationID = item.locationID
            oldOwnerID = item.ownerID
            dogmaItem.invItem = item
            if const.ixOwnerID in change:
                dogmaItem.HandleOwnerChange(oldOwnerID)
            if const.ixLocationID in change:
                dogmaItem.HandleLocationChange(oldLocationID)
                if wasLaunchingDrones or wasLaunchingFighters:
                    shipItem = self.GetShip()
                    if shipItem and dogmaItem:
                        shipItem.subItems.add(dogmaItem)
            if isFitted and not wasFitted:
                self._OnlineModuleIfApplicable(item)

        if self.scatterAttributeChanges:
            sm.ScatterEvent('OnDogmaItemChange', item, change)
        self.items[item.itemID] = item

    def _WasLaunchingDrone(self, item, change):
        return WasLaunchingDrone(item, change, self.locationID)

    def _WasLaunchingFighter(self, item, change):
        return WasLaunchingFighter(item, change, self.locationID)

    def _OnlineModuleIfApplicable(self, item):
        if self.dogmaStaticMgr.TypeHasEffect(item.typeID, const.effectOnline):
            try:
                self.OnlineModule(item.itemID)
            except UserError as e:
                if e.msg != 'EffectAlreadyActive2':
                    uthread.pool('FitItem::RaiseUserError', eve.Message, *e.args)
            except Exception:
                log.LogException('Raised during OnlineModule')

    def IsFitted(self, item):
        if self._IsLocationIDInvalidForFitting(item.locationID):
            return False
        if not IsFittingFlag(item.flagID) and not self.IsValidDroneOrFighterLocation(item.flagID):
            return False
        if item[const.ixStackSize] <= 0:
            return False
        return True

    def IsValidDroneOrFighterLocation(self, flagID):
        if flagID == const.flagDroneBay or IsFighterTubeFlag(flagID):
            return True
        return False

    def _IsLocationIDInvalidForFitting(self, locationID):
        if locationID == self.shipIDBeingDisembarked:
            self.LogNotice('Ignoring location because the ship is being disembarked', locationID)
            return True
        isLocationIDValidForFitting = locationID not in (self.GetCurrentShipID(), session.charid, self.shipIDBeingEmbarked)
        return isLocationIDValidForFitting

    def OnAttributeChanged(self, attributeID, itemKey, value = None, oldValue = None):
        value = super(DogmaLocation, self).OnAttributeChanged(attributeID, itemKey, value=value, oldValue=oldValue)
        if self.scatterAttributeChanges:
            sm.ScatterEvent('OnDogmaAttributeChanged', self.GetCurrentShipID(), itemKey, attributeID, value)

    def GetShip(self):
        return self.dogmaItems[self.GetCurrentShipID()]

    def GetShipItem(self):
        return self.SafeGetDogmaItem(self.GetCurrentShipID())

    def TryFit(self, item, flagID):
        shipID = eveCfg.GetActiveShip()
        shipInv = self.broker.invCache.GetInventoryFromId(shipID, locationID=session.stationid)
        shipInv.Add(item.itemID, item.locationID, qty=1, flag=flagID)

    def GetQuantity(self, itemID):
        if isinstance(itemID, tuple):
            return self.GetAttributeValue(itemID, const.attributeQuantity)
        return self.GetItem(itemID).stacksize

    def GetCapacity(self, shipID, attributeID, flagID):
        ret = self.broker.invCache.GetInventoryFromId(self.GetCurrentShipID(), locationID=session.stationid).GetCapacity(flagID)
        if const.flagLoSlot0 <= flagID <= const.flagHiSlot7:
            shipDogmaItem = self.dogmaItems[shipID]
            subLocation = shipDogmaItem.subLocations.get(flagID, None)
            if subLocation is None:
                used = ret.used
            else:
                used = self.GetAttributeValue(subLocation, const.attributeQuantity) * evetypes.GetVolume(subLocation[2])
            moduleID = self.GetSlotOther(shipID, flagID)
            if moduleID is None:
                capacity = 0
            else:
                capacity = self.GetAttributeValue(moduleID, const.attributeCapacity)
            return utillib.KeyVal(capacity=capacity, used=used)
        return ret

    def OnlineModule(self, moduleID):
        self.Activate(moduleID, const.effectOnline)
        dogmaItem = self.dogmaItems[moduleID]
        try:
            self.remoteDogmaLM.SetModuleOnline(dogmaItem.locationID, moduleID)
        except UserError as e:
            if e.msg != 'EffectAlreadyActive2':
                self.StopEffect(const.effectOnline, moduleID)
                raise
        except Exception:
            self.StopEffect(const.effectOnline, moduleID)
            raise

    def OfflineModule(self, moduleID):
        dogmaItem = self.dogmaItems[moduleID]
        if dogmaItem.locationID not in (self.shipIDBeingDisembarked, self.shipIDBeingEmbarked):
            try:
                self.StopEffect(const.effectOnline, moduleID)
                self.remoteDogmaLM.TakeModuleOffline(dogmaItem.locationID, moduleID)
            except Exception:
                self.Activate(moduleID, const.effectOnline)
                raise

    def GetDragData(self, itemID):
        if itemID in self.items:
            return [uix.GetItemData(self.items[itemID], 'icons')]
        dogmaItem = self.dogmaItems[itemID]
        data = Bunch()
        data.__guid__ = 'listentry.InvItem'
        data.item = utillib.KeyVal(itemID=dogmaItem.itemID, typeID=dogmaItem.typeID, groupID=dogmaItem.groupID, categoryID=dogmaItem.categoryID, flagID=dogmaItem.flagID, ownerID=dogmaItem.ownerID, locationID=dogmaItem.locationID, stacksize=self.GetAttributeValue(itemID, const.attributeQuantity))
        data.rec = data.item
        data.itemID = itemID
        data.viewMode = 'icons'
        return [data]

    def GetDisplayAttributes(self, itemID, attributes):
        ret = {}
        dogmaItem = self.dogmaItems[itemID]
        for attributeID in itertools.chain(dogmaItem.attributes, attributes):
            if attributeID == const.attributeVolume:
                continue
            ret[attributeID] = self.GetAttributeValue(itemID, attributeID)

        return ret

    def GetCharacterSecurityStatus(self, charID):
        if charID != session.charid:
            return 0.0
        return sm.GetService('crimewatchSvc').GetMySecurityStatus()

    def LinkWeapons(self, shipID, toID, fromID, merge = True):
        if toID == fromID:
            return
        toItem = self.dogmaItems[toID]
        fromItem = self.dogmaItems[fromID]
        for item in (toItem, fromItem):
            if not item.IsOnline():
                raise UserError('CantLinkModuleNotOnline')

        if toItem.typeID != fromItem.typeID:
            self.LogInfo('LinkWeapons::Modules not of same type', toItem, fromItem)
            return
        if toItem.groupID not in const.dgmGroupableGroupIDs:
            self.LogInfo('group not groupable', toItem, fromItem)
            return
        if shipID is None or shipID != fromItem.locationID:
            log.LogTraceback('LinkWeapons::Modules not located in the same place')
        masterID = self.GetMasterModuleID(shipID, toID)
        if not masterID:
            masterID = toID
        slaveID = self.IsInWeaponBank(shipID, fromID)
        if slaveID:
            if merge:
                info = self.remoteDogmaLM.MergeModuleGroups(shipID, masterID, slaveID)
            else:
                info = self.remoteDogmaLM.PeelAndLink(shipID, masterID, slaveID)
        else:
            info = self.remoteDogmaLM.LinkWeapons(shipID, masterID, fromID)
        self.OnWeaponBanksChanged(shipID, info)

    def UngroupModule(self, shipID, moduleID):
        slaveID = self.remoteDogmaLM.UnlinkModule(shipID, moduleID)
        self.slaveModulesByMasterModule[shipID][moduleID].remove(slaveID)
        if not self.slaveModulesByMasterModule[shipID][moduleID]:
            del self.slaveModulesByMasterModule[shipID][moduleID]
        self.SetGroupNumbers(shipID)
        sm.ScatterEvent('OnRefreshModuleBanks')
        return slaveID

    def UnlinkAllWeapons(self, shipID):
        self.remoteDogmaLM.UnlinkAllModules(shipID)
        self.OnWeaponBanksChanged(shipID, {})
        self.lastUngroupAllRequest = blue.os.GetSimTime()

    def LinkAllWeapons(self, shipID):
        info = self.remoteDogmaLM.LinkAllWeapons(shipID)
        self.OnWeaponBanksChanged(shipID, info)
        self.lastGroupAllRequest = blue.os.GetSimTime()

    def GetGroupAllOpacity(self, attributeName):
        lastRequest = getattr(self, attributeName)
        if lastRequest is None:
            return 1.0
        timeDiff = blue.os.GetSimTime() - lastRequest
        waitTime = min(GROUPALL_THROTTLE_TIMER, GROUPALL_THROTTLE_TIMER - timeDiff)
        opacity = max(0, 1 - float(waitTime) / GROUPALL_THROTTLE_TIMER)
        return opacity

    def IsInWeaponBank(self, shipID, itemID):
        slaveModulesByMasterModule = self.slaveModulesByMasterModule.get(shipID, {})
        if itemID in slaveModulesByMasterModule:
            return itemID
        masterID = self.GetMasterModuleID(shipID, itemID)
        if masterID is not None:
            return masterID
        return False

    def GetGroupableTypes(self, shipID):
        groupableTypes = defaultdict(lambda : 0)
        try:
            dogmaItem = self.dogmaItems[shipID]
        except KeyError:
            self.LogInfo('GetGroupableTypes - called before I was ready', shipID)
        else:
            for fittedItem in dogmaItem.GetFittedItems().itervalues():
                if not const.flagHiSlot0 <= fittedItem.flagID <= const.flagHiSlot7:
                    continue
                if fittedItem.groupID not in const.dgmGroupableGroupIDs:
                    continue
                if not fittedItem.IsOnline():
                    continue
                groupableTypes[fittedItem.typeID] += 1

        return groupableTypes

    def CanGroupAll(self, shipID):
        groupableTypes = self.GetGroupableTypes(shipID)
        groups = {}
        dogmaItem = self.dogmaItems[shipID]
        for fittedItem in dogmaItem.GetFittedItems().itervalues():
            if fittedItem.groupID not in const.dgmGroupableGroupIDs:
                continue
            if not fittedItem.IsOnline():
                continue
            if not self.IsInWeaponBank(shipID, fittedItem.itemID) and groupableTypes[fittedItem.typeID] > 1:
                return True
            masterID = self.GetMasterModuleID(shipID, fittedItem.itemID)
            if masterID is None:
                masterID = fittedItem.itemID
            if fittedItem.typeID not in groups:
                groups[fittedItem.typeID] = masterID
            elif groups[fittedItem.typeID] != masterID:
                return True

        return False

    def DestroyWeaponBank(self, shipID, itemID):
        self.remoteDogmaLM.DestroyWeaponBank(shipID, itemID)
        self.OnWeaponGroupDestroyed(shipID, itemID)

    def SetWeaponBanks(self, shipID, data):
        super(DogmaLocation, self).SetWeaponBanks(shipID, data)
        self.SetGroupNumbers(shipID)

    def OnWeaponBanksChanged(self, shipID, info):
        self.SetWeaponBanks(shipID, info)
        sm.ScatterEvent('OnRefreshModuleBanks')

    def OnWeaponGroupDestroyed(self, shipID, itemID):
        try:
            del self.slaveModulesByMasterModule[shipID][itemID]
        except KeyError:
            pass

        self.SetGroupNumbers(shipID)
        sm.ScatterEvent('OnRefreshModuleBanks')

    def SetGroupNumbers(self, shipID):
        allGroupsDict = settings.user.ui.Get('linkedWeapons_groupsDict', {})
        groupsDict = allGroupsDict.get(shipID, {})
        for masterID in groupsDict.keys():
            if masterID not in self.slaveModulesByMasterModule[shipID]:
                del groupsDict[masterID]

        for masterID in self.slaveModulesByMasterModule[shipID]:
            if masterID in groupsDict:
                continue
            for i in xrange(1, 9):
                if i not in groupsDict.values():
                    groupsDict[masterID] = i
                    break

        settings.user.ui.Set('linkedWeapons_groupsDict', allGroupsDict)

    def GetModulesInBank(self, shipID, itemID):
        slaveModulesByMasterModule = self.slaveModulesByMasterModule.get(shipID, {})
        masterID = self.GetMasterModuleID(shipID, itemID)
        if masterID is None and itemID in slaveModulesByMasterModule:
            masterID = itemID
        elif masterID is None:
            return
        moduleIDs = self.GetSlaveModules(masterID, shipID)
        moduleIDs.add(masterID)
        return list(moduleIDs)

    def GetAllSlaveModulesByMasterModule(self, shipID):
        slaveModulesByMasterModule = self.slaveModulesByMasterModule.get(shipID, {})
        return slaveModulesByMasterModule

    def GetMasterModuleForFlag(self, shipID, flagID):
        moduleID = self.GetSlotOther(shipID, flagID)
        if moduleID is None:
            raise RuntimeError('GetMasterModuleForFlag, no module in the flag')
        masterID = self.GetMasterModuleID(shipID, moduleID)
        if masterID is not None:
            return masterID
        return moduleID

    def GetSubLocationsInBank(self, shipID, itemID):
        ret = []
        try:
            flagID = self.dogmaItems[itemID].flagID
        except KeyError:
            return []

        moduleID = self.GetSlotOther(shipID, flagID)
        if moduleID is None:
            return []
        moduleIDs = self.GetModulesInBank(shipID, moduleID)
        if not moduleIDs:
            return []
        shipDogmaItem = self.dogmaItems[shipID]
        for moduleID in moduleIDs:
            moduleDogmaItem = self.dogmaItems[moduleID]
            chargeID = shipDogmaItem.subLocations.get(moduleDogmaItem.flagID, None)
            if chargeID is not None:
                ret.append(chargeID)

        return ret

    def GetCrystalsInBank(self, shipID, itemID):
        flagID = self.dogmaItems[itemID].flagID
        moduleID = self.GetSlotOther(shipID, flagID)
        if moduleID is None:
            return []
        moduleIDs = self.GetModulesInBank(shipID, moduleID)
        if not moduleIDs:
            return []
        crystals = []
        for moduleID in moduleIDs:
            moduleDogmaItem = self.dogmaItems[moduleID]
            crystal = self.GetChargeNonDB(shipID, moduleDogmaItem.flagID)
            if crystal is not None:
                crystals.append(crystal.itemID)

        return crystals

    def LoadAmmoTypeToModule(self, moduleID, chargeTypeID):
        shipID = self.dogmaItems[moduleID].locationID
        shipInv = self.broker.invCache.GetInventoryFromId(shipID)
        chargeItems = [ ammoStack for ammoStack in shipInv.List(const.flagCargo) if ammoStack.typeID == chargeTypeID and not IsFittingFlag(ammoStack.flagID) ]
        self.LoadChargesToModule(moduleID, chargeItems, shipID)

    def LoadChargesToModule(self, moduleID, chargeItems, chargeLocationID):
        if not chargeItems:
            raise UserError('CannotLoadNotEnoughCharges')
        if not isinstance(chargeItems, (list, tuple)):
            chargeItems = [chargeItems]
        self.CheckSkillRequirementsForType(None, chargeItems[0].typeID, 'FittingHasSkillPrerequisites')
        moduleLocationID = self.dogmaItems[moduleID].locationID
        if self.IsModuleSlave(moduleID, moduleLocationID):
            moduleID = self.GetMasterModuleID(moduleLocationID, moduleID)
        PlaySound(uiconst.SOUND_ADD_OR_USE)
        self.remoteDogmaLM.LoadAmmo(moduleLocationID, moduleID, [ i.itemID for i in chargeItems ], chargeLocationID)

    def LoadAmmoToModules(self, shipID, moduleIDs, chargeItemIDs, ammoLocationID):
        PlaySound(uiconst.SOUND_ADD_OR_USE)
        self.remoteDogmaLM.LoadAmmo(shipID, moduleIDs, chargeItemIDs, ammoLocationID)

    def DropLoadChargeToModule(self, itemID, chargeTypeID, chargeItems):
        chargeLocationID = chargeItems[0].locationID
        chargeItems = filter(lambda i: i.locationID == chargeLocationID and i.typeID == chargeTypeID, chargeItems)
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            maxQty = sum((i.stacksize for i in chargeItems))
            if maxQty == 0:
                msg = localization.GetByLabel('UI/Common/NoMoreUnits')
            else:
                msg = localization.GetByLabel('UI/Common/SetQuantity')
            ret = uix.QtyPopup(int(maxQty), 0, int(maxQty), msg)
            if ret is None:
                return
            qty = ret['qty']
            if qty <= 0:
                return
            containerInventory = self.broker.invCache.GetInventoryFromId(chargeLocationID)
            sortedCharges = sorted(chargeItems, key=lambda i: i.stacksize)
            chargeSum = 0
            chargeItems = []
            for chargeItem in sortedCharges:
                if chargeSum + chargeItem.stacksize < qty:
                    chargeItems.append(chargeItem)
                    chargeSum += chargeItem.stacksize
                elif chargeSum < qty:
                    newStackID = containerInventory.Add(chargeItem.itemID, chargeLocationID, qty=qty - chargeSum, flag=chargeItem.flagID)
                    chargeItems.append(utillib.KeyVal(itemID=newStackID, typeID=chargeItem.typeID))
                    break

        self.LoadChargesToModule(itemID, chargeItems, chargeLocationID)

    def LoadChargeToAllModules(self, invItem):
        chargeTypeID = invItem.typeID
        self.CheckSkillRequirementsForType(None, chargeTypeID, 'FittingHasSkillPrerequisites')
        availableRounds = invItem.stacksize
        fittedItems = self.GetFittedItemsToShip().values()
        suitableModules = []
        loadingModules = set()
        stateManager = self.godma.GetStateManager()
        for module in fittedItems:
            if not IsShipFittingFlag(module.flagID):
                continue
            if not IsChargeCompatibleWithLauncher(chargeTypeID, module.typeID, self.dogmaStaticMgr):
                continue
            if self.IsInWeaponBank(module.locationID, module.itemID) and self.IsModuleSlave(module.itemID, module.locationID):
                continue
            if stateManager.IsModuleReloading(module.itemID):
                continue
            neededRounds = GetModuleCapacityForAmmoType(module.typeID, chargeTypeID, self.dogmaStaticMgr)
            subLocation = self.GetSubLocation(session.shipid, module.flagID)
            hasCharges = subLocation is not None
            sameChargeType = False
            if hasCharges and subLocation[2] == chargeTypeID:
                sameChargeType = True
                neededRounds -= self.GetQuantity(subLocation)
            if neededRounds <= 0:
                continue
            suitableModules.append((not module.IsOnline(),
             hasCharges,
             not sameChargeType,
             neededRounds,
             module.itemID))

        suitableModules.sort()
        for suitableModule in suitableModules:
            _, _, _, neededRounds, moduleItemID = suitableModule
            loadingModules.add(moduleItemID)
            availableRounds -= neededRounds
            if availableRounds <= 0:
                break

        if loadingModules:
            self.LoadAmmoToModules(session.shipid, loadingModules, [invItem.itemID], invItem.locationID)
        else:
            uicore.Message('NoSuitableModules')

    def UnloadModuleToContainer(self, shipID, itemID, containerArgs, flag = None):
        masterModuleID = None
        if self.IsInWeaponBank(shipID, itemID):
            ret = eve.Message('ClearGroupModule', {}, uiconst.YESNO, suppress=uiconst.ID_YES)
            if ret != uiconst.ID_YES:
                return
            masterModuleID = itemID
            if self.IsModuleSlave(itemID, shipID):
                masterModuleID = self.GetMasterModuleID(shipID, itemID)
            self.DestroyWeaponBank(shipID, masterModuleID)
        containerInv = self.broker.invCache.GetInventoryFromId(*containerArgs)
        containerItem = containerInv.GetItem()
        if containerItem.groupID == const.groupAuditLogSecureContainer and flag is None:
            flag = settings.user.ui.Get('defaultContainerLock_%s' % containerItem.itemID, None)
            ownerID = session.charid
            if containerItem.ownerID == session.corpid:
                ownerID = session.corpid
            self.remoteDogmaLM.UnloadAmmo(shipID, masterModuleID or itemID, (containerItem.itemID, ownerID, flag))
        else:
            self.remoteDogmaLM.UnloadAmmo(shipID, masterModuleID or itemID, containerItem.itemID)
        item = self.GetItem(itemID)
        if containerArgs[0] == shipID:
            containerInv.Add(itemID, item.locationID, qty=None, flag=flag)
        elif flag is not None:
            containerInv.Add(itemID, item.locationID, qty=None, flag=flag)
        else:
            containerInv.Add(itemID, item.locationID)

    def UnloadAmmoToContainer(self, shipID, ammoItem, destination, quantity = None):
        moduleID = masterID = None
        if self.IsItemSubLocation(ammoItem):
            ship, sourceFlagID, _ = ammoItem
            if shipID != ship:
                ammoItem = sm.StartService('godma').GetStateManager().GetItem(ammoItem)
            ammoID = ammoItem
        else:
            sourceFlagID = ammoItem.flagID
            ammoID = ammoItem.itemID
        try:
            moduleID = first(sm.GetService('invCache').GetInventoryFromId(shipID).List(flag=sourceFlagID), lambda i: i.itemID != ammoID).itemID
        except (StopIteration, TypeError):
            if self.IsItemSubLocation(ammoItem.itemID):
                shipID, sourceFlagID, _ = ammoItem.itemID
                ammoID = ammoItem.itemID
                moduleID = shipID

        if self.IsModuleSlave(moduleID, shipID):
            masterID = moduleID = self.GetMasterModuleID(shipID, moduleID)
        try:
            return self.remoteDogmaLM.UnloadAmmo(shipID, moduleID, destination, quantity)
        except UserError as e:
            if e.msg == 'NotEnoughCargoSpace' and masterID is not None:
                eve.Message('NotEnoughCargoSpaceToUnloadBank')
                return
            raise

    def UnloadAmmoFromModules(self, shipID, moduleIDs, destination):
        if not isinstance(moduleIDs, (list, set, tuple)):
            moduleIDs = [moduleIDs]
        self.remoteDogmaLM.UnloadAmmo(shipID, moduleIDs, destination)

    def CheckCanFit(self, locationID, itemID, flagID, fromLocationID):
        item = self.broker.invCache.FetchItem(itemID, fromLocationID)
        if item is None:
            self.LogInfo('ClientDogmaLocation::CheckCanFit - unable to fetch item', locationID, itemID, flagID, fromLocationID)
            return
        self.CheckCanFitByShipAndType(locationID, item.typeID)

    def CheckCanFitByShipAndType(self, locationID, typeID):
        maxGroupFitted = self.dogmaStaticMgr.GetTypeAttribute(typeID, const.attributeMaxGroupFitted)
        groupID = evetypes.GetGroupID(typeID)
        if maxGroupFitted is not None:
            modulesByGroup = self.GetModuleListByShipGroup(locationID, groupID)
            if len(modulesByGroup) >= maxGroupFitted:
                shipItem = self.dogmaItems[locationID]
                raise UserError('CantFitTooManyByGroup', {'ship': shipItem.typeID,
                 'module': typeID,
                 'groupName': evetypes.GetGroupNameByGroup(groupID),
                 'noOfModules': int(maxGroupFitted),
                 'noOfModulesFitted': len(modulesByGroup)})
        maxTypeFitted = self.dogmaStaticMgr.GetTypeAttribute(typeID, const.attributeMaxTypeFitted)
        if maxTypeFitted is not None:
            modulesByType = self.GetModuleListByShipType(locationID, typeID)
            if len(modulesByType) >= maxTypeFitted:
                shipItem = self.dogmaItems[locationID]
                raise UserError('CantFitTooManyByType', {'ship': shipItem.typeID,
                 'module': typeID,
                 'noOfModules': int(maxTypeFitted),
                 'noOfModulesFitted': len(modulesByType)})

    def GetOnlineModules(self, shipID):
        return {module.flagID:moduleID for moduleID, module in self.dogmaItems[shipID].GetFittedItems().iteritems() if module.IsOnline()}

    def AreAllFittedModulesOnline(self, shipID):
        for module in self.dogmaItems[shipID].GetFittedItems().values():
            if IsFittingModule(module.categoryID) and IsFittingFlag(module.flagID) and not module.IsOnline():
                return False

        return True

    def ShouldStartChanceBasedEffect(self, effectID, itemID, chanceAttributeID):
        dogmaItem = self.dogmaItems[itemID]
        if dogmaItem.groupID == const.groupBooster:
            godmaItem = self.godma.GetItem(itemID)
            if godmaItem is None:
                return False
            effectName = dogma.data.get_effect_name(effectID)
            godmaEffect = godmaItem.effects.get(effectName, None)
            if godmaEffect is None:
                return False
            if godmaEffect.isActive:
                return True
        return False

    def GetDogmaItemWithWait(self, itemID):
        startTime = blue.os.GetWallclockTime()
        while blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTime()) < 2000:
            if itemID in self.dogmaItems:
                return self.dogmaItems[itemID]
            self.LogInfo('GetDogmaItemWithWait::Item not ready, sleeping for 100ms')
            blue.pyos.synchro.Sleep(100)

        self.LogError('Failed to get dogmaItem in time', itemID)

    def GetModifierString(self, itemID, attributeID):
        dogmaItem = self.dogmaItems[itemID]
        modifiers = self.GetModifiersOnAttribute(itemID, attributeID, dogmaItem.locationID, dogmaItem.groupID, dogmaItem.ownerID, dogmaItem.typeID)
        baseValue = self.dogmaStaticMgr.GetTypeAttribute2(dogmaItem.typeID, attributeID)
        ret = 'Base Value: %s\n' % GetFormatAndValue(dogma.data.get_attribute(attributeID), baseValue)
        if modifiers:
            ret += 'modified by\n'
            for op, modifyingItemID, modifyingAttributeID in modifiers:
                value = self.GetAttributeValue(modifyingItemID, modifyingAttributeID)
                if op in (const.dgmAssPostMul,
                 const.dgmAssPreMul,
                 const.dgmAssPostDiv,
                 const.dgmAssPreDiv) and value == 1.0:
                    continue
                elif op in (const.dgmAssPostPercent, const.dgmAssModAdd, const.dgmAssModAdd) and value == 0.0:
                    continue
                modifyingItem = self.dogmaItems[modifyingItemID]
                modifyingAttribute = dogma.data.get_attribute(modifyingAttributeID)
                value = GetFormatAndValue(modifyingAttribute, value)
                ret += '  %s: %s\n' % (evetypes.GetName(modifyingItem.typeID), value)

        return ret

    def GatherDroneInfo(self, shipDogmaItem):
        dronesByTypeID = {}
        for droneID in shipDogmaItem.GetDronesInBay():
            damage = GetDamageFromItem(self, droneID)
            if damage == 0:
                continue
            damageMultiplier = self.GetAttributeValue(droneID, const.attributeDamageMultiplier)
            if damageMultiplier == 0:
                continue
            duration = self.GetAttributeValue(droneID, const.attributeRateOfFire)
            droneDps = damage * damageMultiplier / duration
            droneBandwidth = self.GetAttributeValue(droneID, const.attributeDroneBandwidthUsed)
            droneDogmaItem = self.dogmaItems[droneID]
            droneItem = self.GetItem(droneID)
            if droneItem is None:
                continue
            if droneDogmaItem.typeID not in dronesByTypeID:
                dronesByTypeID[droneItem.typeID] = [droneBandwidth, droneDps, droneItem.stacksize]
            else:
                dronesByTypeID[droneItem.typeID][-1] += droneItem.stacksize

        drones = defaultdict(list)
        for typeID, (bw, dps, qty) in dronesByTypeID.iteritems():
            bw = int(bw)
            drones[bw].append((typeID,
             bw,
             qty,
             dps))

        for l in drones.itervalues():
            l.sort(key=lambda vals: vals[-1], reverse=True)

        return drones

    def SimpleGetDroneDamageOutput(self, drones, bwLeft, dronesLeft):
        dronesUsed = {}
        totalDps = 0
        for bw in sorted(drones.keys(), reverse=True):
            if bw > bwLeft:
                continue
            for typeID, bwNeeded, qty, dps in drones[bw]:
                noOfDrones = min(int(bwLeft) / int(bwNeeded), qty, dronesLeft)
                if noOfDrones == 0:
                    break
                dronesUsed[typeID] = noOfDrones
                totalDps += dps * noOfDrones
                dronesLeft -= noOfDrones
                bwLeft -= noOfDrones * bwNeeded

        return (totalDps, dronesUsed)

    def GetOptimalDroneDamage(self, shipID, *args):
        shipDogmaItem = self.dogmaItems[shipID]
        drones = self.GatherDroneInfo(shipDogmaItem)
        self.LogInfo('Gathered drone info and found', len(drones), 'types of drones')
        bandwidth = self.GetAttributeValue(shipID, const.attributeDroneBandwidth)
        if session.solarsystemid:
            maxDrones = self.godma.GetItem(session.charid).maxActiveDrones
        else:
            maxDrones = self.GetAttributeValue(shipDogmaItem.ownerID, const.attributeMaxActiveDrones)
        self.startedKnapsack = blue.os.GetWallclockTime()
        dps, drones = self.SimpleGetDroneDamageOutput(drones, bandwidth, maxDrones)
        return (dps * 1000, drones)

    def GetOptimalDroneDamage2(self, shipID, activeDrones):
        return GetOptimalDroneDamage(shipID, self, activeDrones)

    def IsModuleIncludedInCalculation(self, module):
        return module.IsOnline()

    def GetGodmaAttributeValue(self, itemID, attributeID):
        attributeName = self.dogmaStaticMgr.attributes[attributeID].name
        return self.godma.GetStateManager().GetAttribute(itemID, attributeName)

    def GetModulesLackingSkills(self):
        ret = []
        for moduleID, module in self.dogmaItems[self.GetCurrentShipID()].GetFittedItems().iteritems():
            if IsFittingModule(module.categoryID) and IsFittingFlag(module.flagID) and not const.flagRigSlot0 <= module.flagID <= const.flagRigSlot7:
                if self.GetMissingSkills(module.typeID):
                    ret.append(moduleID)

        return ret

    def OnServerBrainUpdated(self, brainData):
        if self.brain and self.brain[0] >= brainData[0]:
            LogNotice('OnServerBrainUpdated received for brain version %s, but we already have version %s. Update cancelled!' % (brainData[0], self.brain[0]))
            return
        self.LogNotice('OnServerBrainUpdated received for character %s, brain version %s' % (session.charid, brainData[0]))
        shipID = self.shipsByPilotID.get(session.charid, None)
        if shipID is None:
            self.LogInfo('OnServerBrainUpdated:ClientDogmaLocation has not embarked character to anything. Nothing to do.')
            self.ProcessBrainData(session.charid, brainData)
            return
        with self.brainUpdate.Event(shipID):
            self.RemoveBrainEffects(shipID, session.charid, 'clientDogmaLocation.OnServerBrainUpdated')
            self.ProcessBrainData(session.charid, brainData)
            self.ApplyBrainEffects(shipID, session.charid, 'clientDogmaLocation.OnServerBrainUpdated')

    def GetModifiedTypeAttribute(self, typeID, attributeID):
        return self.dogmaStaticMgr.GetTypeAttribute(typeID, attributeID)

    def GetCurrentShipHeatStates(self):
        shipID = self.GetCurrentShipID()
        shipHeatStates = {}
        if shipID:
            shipHeatStates = self.dogmaItems[shipID].GetHeatValues()
        return shipHeatStates

    def OnHeatAdded(self, heatID, moduleID):
        shipItem = self.dogmaItems[self.GetCurrentShipID()]
        moduleItem = self.dogmaItems[moduleID]
        sourceAttribute = moduleItem.attributes[const.attributeHeatAbsorbtionRateModifier]
        heatAttribute = shipItem.attributes[heatID]
        sourceAttribute.AddOutgoingModifier(const.dgmAssModAdd, heatAttribute.incomingHeat)
        heatAttribute.AddIncomingModifier(const.dgmAssModAdd, sourceAttribute)

    def OnHeatRemoved(self, heatID, moduleID):
        shipItem = self.dogmaItems[self.GetCurrentShipID()]
        moduleItem = self.dogmaItems[moduleID]
        sourceAttribute = moduleItem.attributes[const.attributeHeatAbsorbtionRateModifier]
        heatAttribute = shipItem.attributes[heatID]
        sourceAttribute.RemoveOutgoingModifier(const.dgmAssModAdd, heatAttribute.incomingHeat)
        heatAttribute.RemoveIncomingModifier(const.dgmAssModAdd, sourceAttribute)

    def GetSecurityClass(self):
        return sm.GetService('map').GetSecurityClass(session.solarsystemid2)

    def GetActiveDrones(self):
        shipItem = self.GetShip()
        drones = shipItem.GetDrones()
        activeDrones = {}
        for droneID, droneDogmaItem in drones.iteritems():
            if droneDogmaItem.locationID == session.solarsystemid2:
                activeDrones[droneID] = 1

        if not activeDrones:
            activeDrones = self._FindDronesInBayForActive(drones)
        return activeDrones

    def _FindDronesInBayForActive(self, drones):
        _, droneTypesToUSse = self.GetOptimalDroneDamage(self.GetCurrentShipID())
        myDronesByTypeID = defaultdict(list)
        for x in drones.itervalues():
            myDronesByTypeID[x.typeID].append(x)

        activeDrones = {}
        for droneTypeID, qtyNeeded in droneTypesToUSse.iteritems():
            currentQty = 0
            for eachDrone in myDronesByTypeID.get(droneTypeID, []):
                droneItem = self.GetItem(eachDrone.itemID)
                qtyFromDrone = min(qtyNeeded - currentQty, droneItem.stacksize)
                activeDrones[eachDrone.itemID] = qtyFromDrone
                currentQty += qtyFromDrone
                if currentQty >= qtyNeeded:
                    break

        return activeDrones

    def OnDroneControlLost(self, droneID):
        unloaded = self.UnloadDroneOrFighterOnDeath(droneID)
        if unloaded:
            sm.ScatterEvent('OnDogmaDronesChanged')

    def OnDroneStateChange2(self, droneID, oldState, newState):
        if newState == -1:
            return
        if droneID in self.dogmaItems:
            return
        slimItem = sm.GetService('michelle').GetItem(droneID)
        currentShipID = self.GetCurrentShipID()
        if slimItem and slimItem.ownerID in (session.charid, currentShipID):
            typeID = slimItem.typeID
            item = blue.DBRow(self.godma.itemrd, [slimItem.itemID,
             typeID,
             slimItem.ownerID,
             currentShipID,
             const.flagDroneBay,
             1,
             evetypes.GetGroupID(typeID),
             evetypes.GetCategoryID(typeID),
             1])
            self.FitItem(item)
        sm.ScatterEvent('OnDogmaDronesChanged')

    def GetFittedItemsToShip(self):
        shipItem = self.GetShip()
        if shipItem:
            return shipItem.GetFittedItems()
        else:
            return {}

    def GetActivityState(self, itemID):
        return (None, None, None)

    def GetHoldItems(self, flagID):
        shipInv = self.broker.invCache.GetInventoryFromId(self.GetCurrentShipID())
        itemsInFlag = shipInv.List(flagID)
        cargoItems = {}
        for eachItem in itemsInFlag:
            if eachItem.flagID == flagID:
                cargoItems[eachItem.itemID] = eachItem

        return cargoItems

    def GetMaxActiveDrones(self):
        return self.GetAttributeValue(session.charid, const.attributeMaxActiveDrones)

    def GetShipItemForFighter(self, itemID):
        currentShipID = self.GetCurrentShipID()
        if currentShipID:
            return self.SafeGetDogmaItem(currentShipID)

    def OnFighterRemovedFromControllerClient(self, fighterID):
        self.UnloadDroneOrFighterOnDeath(fighterID)

    def UnloadDroneOrFighterOnDeath(self, entityID):
        dogmaItem = self.SafeGetDogmaItem(entityID)
        if not dogmaItem:
            return False
        if dogmaItem.locationID != self.GetCurrentShipID():
            self.UnfitAndUnloadItem(self.GetCurrentShipID(), entityID)
            return True
        return False

    def GetFightersForTube(self, eachTubeFlagID):
        from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
        shipFighterState = GetShipFighterState()
        return shipFighterState.GetFightersForTubeID(eachTubeFlagID)

    def Overload(self, itemID, effectID):
        if not self.__IsEffectActive(itemID, effectID):
            self.Activate(itemID, effectID)

    def OverloadRack(self, moduleIDs):
        for mID in moduleIDs:
            effectID = self.__GetOverloadEffect(mID)
            if effectID:
                self.Overload(mID, effectID)

    def StopOverloading(self, itemID, effectID):
        self.StopEffect(effectID, itemID)

    def StopOverloadingRack(self, moduleIDs):
        for mID in moduleIDs:
            effectID = self.__GetOverloadEffect(mID)
            if effectID:
                self.StopOverloading(mID, effectID)

    def __IsEffectActive(self, moduleID, effectID):
        module = self.SafeGetDogmaItem(moduleID)
        if module:
            if effectID in module.activeEffects:
                return True
        return False

    def __GetOverloadEffect(self, moduleID):
        module = self.SafeGetDogmaItem(moduleID)
        if not module:
            return
        for effectInfo in self.dogmaStaticMgr.TypeGetEffects(module.typeID).itervalues():
            effectID = effectInfo.effectID
            effect = self.dogmaStaticMgr.effects[effectID]
            if effect.effectCategory == const.dgmEffOverload:
                return effectID

    def IsFullyCorrupted(self):
        try:
            if sm.GetService('corruptionSuppressionSvc').IsCurrentSystemFullyCorrupted():
                return True
        except StandardError:
            log.LogTraceback('Failed to get IsFullyCorrupted on client')

        return False
