#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\tryFit.py
import evetypes
import log
import blue
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from eve.client.script.environment import invControllers as invCtrl
from eve.client.script.ui.shared.fitting.fittingUtil import RigFittingCheck
from eve.common.script.sys.idCheckers import IsStation, IsSolarSystem, flagCorpSAGs
from inventorycommon.const import flagFrigateEscapeBay
from inventorycommon.util import IsFittingModule, IsShipFittingFlag
from shipfitting.fittingStuff import GetSlotTypeForType
from utillib import KeyVal
from collections import defaultdict
from carbonui.uicore import uicore
from itertools import groupby
from dogma.ammoloadingUtils import GetModuleCapacityForAmmoType
FAKE_ITEM_GUID = ['listentry.GenericMarketItem',
 'listentry.Item',
 'uicls.GenericDraggableForTypeID',
 'listentry.QuickbarItem',
 'listentry.ContractItemSelect',
 'listentry.FittingModuleEntry',
 'listentry.KillItems']
FAKE_ITEM_LOCATION_GUID = ['xtriui.ListSurroundingsBtn']

class TryFitter(object):

    def __init__(self):
        self.ghostFittingSvc = sm.GetService('ghostFittingSvc')

    def TryFit(self, realInvItems, fakeInvItems, controller, shipID = None):
        if not shipID:
            shipID = session.shipid
            if not shipID:
                return
        invItems = realInvItems + fakeInvItems
        dogmaLocation = controller.GetDogmaLocation()
        charges, drones, fakeFighters, newInvItems = self.GetInvItemsToFit(invItems, controller)
        if len(newInvItems) == 1:
            invItem = invItems[0]
            if self.IsShipOrStructure(invItem):
                return GhostFitShip(invItem)
        if not controller.IsSimulated() and not realInvItems and fakeInvItems:
            self.ghostFittingSvc.LoadCurrentShip()
        if len(newInvItems) > 0:
            sourceID = getattr(newInvItems[0], 'locationID', None)
            self.FitModule(shipID, sourceID, newInvItems, controller)
        if drones:
            self.AddDrones(drones, shipID, controller)
        if fakeFighters:
            self.AddSimulatedFighters(fakeFighters, shipID, controller)
        if charges:
            self.TryFitCharges(dogmaLocation, shipID, controller, charges)

    def IsModuleSuitable(self, dogmaLocation, usedWith, module):
        if not IsShipFittingFlag(module.flagID):
            return False
        if module.typeID not in usedWith:
            return False
        if self.IsWeaponBankSlave(dogmaLocation, module):
            return False
        if self.IsCharge(module):
            return False
        return True

    def IsCharge(self, row):
        return row.categoryID == const.categoryCharge

    def IsWeaponBankSlave(self, dogmaLocation, row):
        return dogmaLocation.IsInWeaponBank(row.locationID, row.itemID) and dogmaLocation.IsModuleSlave(row.itemID, row.locationID)

    def IsShipOrStructure(self, invItem):
        categoryID = evetypes.GetCategoryID(invItem.typeID)
        if categoryID in (const.categoryShip, const.categoryStructure):
            return True

    def GetInvItemsToFit(self, invItems, controller):
        isSimulated = controller.IsSimulated()
        if isSimulated:
            useRigs = True
        else:
            useRigs = None
        charges = []
        drones = []
        fakeFighters = []
        newInvItems = []
        subSystemGroupIDs = set()
        for eachInvItem in invItems[:]:
            categoryID = evetypes.GetCategoryID(eachInvItem.typeID)
            if IsFittingModule(categoryID):
                slotEffect = GetSlotTypeForType(eachInvItem.typeID)
                if slotEffect == const.effectRigSlot:
                    if useRigs is None:
                        useRigs = RigFittingCheck(eachInvItem, controller.GetTypeID())
                    if useRigs:
                        newInvItems.append(eachInvItem)
                    continue
            if categoryID == const.categorySubSystem:
                if eachInvItem.groupID not in subSystemGroupIDs:
                    subSystemGroupIDs.add(eachInvItem.groupID)
                    newInvItems.append(eachInvItem)
                continue
            elif categoryID == const.categoryCharge:
                charges.append(eachInvItem)
                continue
            elif categoryID == const.categoryDrone:
                drones.append(eachInvItem)
                continue
            elif isSimulated and categoryID == const.categoryFighter:
                fakeFighters.append(eachInvItem)
                continue
            newInvItems.append(eachInvItem)

        return (charges,
         drones,
         fakeFighters,
         newInvItems)

    def FitModule(self, shipID, sourceID, invItems, controller):
        PlaySound(uiconst.SOUND_ADD_OR_USE)
        if controller.IsSimulated():
            sortedInvItems = sorted(invItems, key=lambda x: x.typeID)
            for each in sortedInvItems:
                self.ghostFittingSvc.TryFitModuleToOneSlot(each.typeID, feedbackTimeOut=True, originalItemID=getattr(each, 'itemID', None))

        else:
            itemIDs = [ invItem.itemID for invItem in invItems ]
            shipInv = sm.GetService('invCache').GetInventoryFromId(shipID, locationID=session.stationid)
            shipInv.moniker.MultiAdd(itemIDs, sourceID, flag=const.flagAutoFit)

    def TryFitCharges(self, dogmaLocation, shipID, controller, charges):
        if controller.IsSimulated():
            return self.TryFitGhostCharges(charges)
        loadResults = None
        infoSvc = sm.GetService('info')
        sortKey = lambda charge: charge.typeID
        loadedModules = set()
        for chargeTypeID, chargeItems in groupby(sorted(charges, key=sortKey), sortKey):
            usedWith = infoSvc.GetUsedWithTypeIDs(chargeTypeID)
            if usedWith is None:
                continue
            try:
                dogmaLocation.CheckSkillRequirementsForType(None, chargeTypeID, 'FittingHasSkillPrerequisites')
            except UserError as e:
                loadResults = e
                continue

            chargeItems = list(chargeItems)
            availableRounds = sum((c.stacksize for c in chargeItems))
            isCrystalOrScript = evetypes.GetGroupID(chargeTypeID) in cfg.GetCrystalGroups()
            fittedItems = dogmaLocation.GetFittedItemsToShip().values()
            fittedItems = sorted(fittedItems, key=lambda x: getattr(x, 'flagID', None))
            suitableModules = set()
            for moduleItem in fittedItems:
                if availableRounds <= 0:
                    break
                if moduleItem.itemID in loadedModules:
                    continue
                if not self.IsModuleSuitable(dogmaLocation, usedWith, moduleItem):
                    continue
                if isCrystalOrScript:
                    if len([ i for i in fittedItems if i.flagID == moduleItem.flagID if i.itemID != moduleItem.itemID ]):
                        continue
                    availableRounds -= 1
                else:
                    subLocation = dogmaLocation.GetSubLocation(shipID, moduleItem.flagID)
                    if subLocation is not None and subLocation[2] != chargeTypeID:
                        continue
                    neededRounds = GetModuleCapacityForAmmoType(moduleItem.typeID, chargeTypeID, dogmaLocation.dogmaStaticMgr)
                    if subLocation is not None:
                        neededRounds -= dogmaLocation.GetQuantity(subLocation)
                    if neededRounds <= 0:
                        continue
                    availableRounds -= neededRounds
                suitableModules.add(moduleItem.itemID)

            if len(suitableModules):
                try:
                    dogmaLocation.LoadAmmoToModules(shipID, suitableModules, [ c.itemID for c in chargeItems ], chargeItems[0].locationID)
                    loadResults = True
                    loadedModules.update(suitableModules)
                except StandardError as e:
                    loadResults = e

            blue.pyos.synchro.SleepSim(50)

        if isinstance(loadResults, UserError):
            raise loadResults
        elif not loadedModules:
            uicore.Message('NoSuitableModules')

    def TryFitGhostCharges(self, charges):
        chargeTypeIDs = {x.typeID for x in charges}
        self.ghostFittingSvc.TryFitFakeAmmoToAllModulesFitted(chargeTypeIDs)

    def AddDrones(self, drones, shipID, controller):
        if controller.IsSimulated():
            qtyByTypeAndItemID = defaultdict(int)
            for eachDrone in drones:
                qtyByTypeAndItemID[eachDrone.typeID, eachDrone.itemID] += 1

            self.ghostFittingSvc.TryFitDronesToDroneBay(qtyByTypeAndItemID)
        else:
            invCtrl.ShipDroneBay(shipID).AddItems(drones)

    def AddSimulatedFighters(self, fighters, shipID, controller):
        if not controller.IsSimulated():
            return
        qtyByTypeID = defaultdict(int)
        for eachFighter in fighters:
            qtyByTypeID[eachFighter.typeID] += getattr(eachFighter, 'stacksize', None) or 1

        self.ghostFittingSvc.TryFitFightersToTubeOrBay(qtyByTypeID)


def GhostFitShip(invItem):
    shipTypeID = invItem.typeID
    fitData = []
    oringalItemIDByFlagAndTypeID = {}
    itemID = getattr(invItem, 'itemID', None)
    if itemID:
        dockableLocationID, solarSystemID, ownerID = _GetOwnerAndLocationID(invItem)
        if (dockableLocationID or solarSystemID) and ownerID in (session.charid, session.corpid):
            try:
                fitData, oringalItemIDByFlagAndTypeID = sm.GetService('fittingSvc').FittingDictForRemoteShip(itemID, putModuleAmmoInCargo=True, dockableLocationID=dockableLocationID, solarSystemID=solarSystemID)
            except Exception as e:
                if isinstance(e, UserError) and e.msg == 'InventoryStopSpamming':
                    raise
                log.LogWarn('Tryfit - failed to get fitdata, e = ', e)

    fitting = KeyVal(shipTypeID=shipTypeID, fittingID=None, ownerID=None, fitData=fitData)
    sm.GetService('ghostFittingSvc').SimulateFitting(fitting, oringalItemIDByFlagAndTypeID)


def _GetOwnerAndLocationID(invItem):
    dockableLocationID = getattr(invItem, 'locationID', None)
    solarSystemID = None
    ownerID = getattr(invItem, 'ownerID', None)
    item = getattr(invItem, 'item', invItem)
    if ownerID is None and item:
        ownerID = getattr(item, 'ownerID', None)
    if dockableLocationID is None and item:
        dockableLocationID = getattr(item, 'locationID', None)
    if item and item.flagID in (const.flagCargo, const.flagShipHangar, flagFrigateEscapeBay):
        parentShipInfo = GetParentShipInfo(item)
        if parentShipInfo:
            dockableLocationID, solarSystemID = parentShipInfo
    elif ownerID == session.corpid and item and item.flagID in flagCorpSAGs:
        for office in sm.GetService('officeManager').GetMyCorporationsOffices():
            if office.officeID == dockableLocationID:
                dockableLocationID = office.stationID
                break

    return (dockableLocationID, solarSystemID, ownerID)


def GetParentShipInfo(item):
    parentShip = sm.GetService('invCache').GetInventoryFromId(item.locationID).GetItem()
    if not parentShip:
        return
    dockableLocationID = solarSystemID = None
    itemLocation = parentShip.locationID
    if IsStation(itemLocation):
        dockableLocationID = itemLocation
    elif IsSolarSystem(itemLocation):
        dockableLocationID = None
        solarSystemID = itemLocation
    elif sm.GetService('structureDirectory').GetStructureInfo(itemLocation) is not None:
        dockableLocationID = itemLocation
    return (dockableLocationID, solarSystemID)
