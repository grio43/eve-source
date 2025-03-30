#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\fittingSvc.py
import sys
from collections import defaultdict, Counter
import blue
import dogma.data
import evetypes
import inventorycommon
import inventorycommon.const as invConst
import localization
import log
import uthread
import utillib
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING
from carbon.common.script.util.format import FmtAmt
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.linkUtil import GetShowInfoLink
from eve.client.script.ui.control.entries.fitting import FittingModuleEntry
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.fitting.fittingUtil import GetFighterNumByTypeIDsInTubes, GetFightersInTubes
from eve.client.script.ui.shared.fittingScreen.fittingSearchUtil import SearchFittingHelper
from eve.client.script.ui.shared.fittingMgmtWindow import FittingMgmt, ViewFitting
from eve.client.script.ui.shared.fittingScreen.missingItemsPopup import OpenBuyAllBox
from eve.common.lib.appConst import COMMUNITY_FITTING_CORP
from eve.common.script.sys import eveCfg
from eve.common.script.sys.eveCfg import GetActiveShip, InShipInSpace
from eveexceptions import UserError
from evetypes import TYPE_LIST_FILAMENTS, TYPE_LIST_OTHER_CARGO_HOLD_TYPES
from globalConfig.getFunctions import AreCommunityFittingsEnabled
from shipfitting import Fitting, INVALID_FITTING_ID
from inventorycommon.util import IsShipFittingFlag, IsShipFittable, IsSubsystemFlagVisible, IsFighterTubeFlag, IsModularShip
from carbonui import uiconst
from carbonui.util.various_unsorted import SortListOfTuples, GetClipboardData
from shipfitting.fittingStuff import IsThereRigMismatch
from shipfitting.importFittingUtil import FindShipAndFittingName, ImportFittingUtil
from shipfitting.exportFittingUtil import GetFittingEFTString
from textImporting import IsUsingDefaultLanguage
from utillib import KeyVal
from carbonui.uicore import uicore
from eve.common.lib import appConst as const
CARGO_MARKER = '_'

class fittingSvc(Service):
    __guid__ = 'svc.fittingSvc'
    __exportedcalls__ = {'GetFittingDictForActiveShip': [],
     'IsTypeFittedInActiveShip': []}
    __startupdependencies__ = ['settings', 'invCache']
    __notifyevents__ = ['OnSkillsChanged',
     'OnFittingAdded',
     'OnFittingDeleted',
     'OnManyFittingsDeleted',
     'OnFittingsUpdated',
     'OnGlobalConfigChanged',
     'OnCommunityFittingsUpdated',
     'OnSessionReset']

    def __init__(self):
        Service.__init__(self)
        self.Initialize()
        self.InitSearchFittingHelper()

    def Initialize(self):
        self.fittings = {}
        self.hasSkillByFittingID = {}
        self.importFittingUtil = None
        self.inSimulation = False
        self.busyFitting = False

    def Run(self, ms = None):
        self.state = SERVICE_RUNNING
        self.fittings = {}

    def OnSessionReset(self):
        self.Initialize()
        self.searchFittingHelper.ResetAllVariables()

    def InitSearchFittingHelper(self):
        self.searchFittingHelper = SearchFittingHelper(cfg)
        uthread.new(self.searchFittingHelper.BuildNameDict)

    def GetFittingMgr(self, ownerID):
        if ownerID == session.charid:
            return sm.RemoteSvc('charFittingMgr')
        if ownerID == session.corpid:
            return sm.RemoteSvc('corpFittingMgr')
        if session.allianceid and ownerID == session.allianceid:
            return sm.RemoteSvc('allianceFittingMgr')
        raise RuntimeError("Can't find the fitting manager you're asking me to get. ownerID:", ownerID)

    def HasLegacyClientFittings(self):
        if len(settings.char.generic.Get('fittings', {})) > 0:
            return True
        return False

    def GetLegacyClientFittings(self):
        return settings.char.generic.Get('fittings', {})

    def DeleteLegacyClientFittings(self):
        settings.char.generic.Set('fittings', None)

    def GetFighterTypesInTubes(self):
        dogmaLocation = self.GetCurrentDogmaLocation()
        return {typeID for typeID in GetFighterNumByTypeIDsInTubes(dogmaLocation).iterkeys()}

    def GetFittingDictForCurrentFittingWindowShip(self, putModuleAmmoInCargo = True):
        if self.IsShipSimulated():
            return self.GetFittingDictForSimulatedShip(putModuleAmmoInCargo=putModuleAmmoInCargo)
        else:
            return self.GetFittingDictForActiveShip(putModuleAmmoInCargo=putModuleAmmoInCargo)

    def GetFittingDictForActiveShip(self, putModuleAmmoInCargo = True):
        shipID = eveCfg.GetActiveShip()
        shipInv = self.invCache.GetInventoryFromId(shipID, locationID=session.stationid)
        visibleFittedItems = {i for i in shipInv.List() if inventorycommon.ItemIsVisible(i)}
        if InShipInSpace():
            try:
                drones = sm.GetService('clientDogmaIM').GetDogmaLocation().GetShip().GetDrones()
                godma = sm.GetService('godma')
                droneInvItems = filter(None, {godma.GetItem(x.itemID) for x in drones.itervalues() if x.locationID != shipID})
                droneDbRows = {blue.DBRow(x.dbrow) for x in droneInvItems}
                for eachDrone in droneDbRows:
                    eachDrone.flagID = const.flagDroneBay

                visibleFittedItems.update(droneDbRows)
            except StandardError as e:
                log.LogException('issue when getting drones for a fit')

        fitData = self.CreateFittingData(visibleFittedItems, putModuleAmmoInCargo=putModuleAmmoInCargo)
        return (shipInv.GetItem().typeID, fitData, visibleFittedItems)

    def IsTypeFittedInActiveShip(self, typeID):
        _shipType, fitData, _ = self.GetFittingDictForActiveShip()
        for fitTypeID, _fitFlag, _fitQuantity in fitData:
            if fitTypeID == typeID:
                return True

        return False

    def FittingDictForRemoteShip(self, shipID, putModuleAmmoInCargo, dockableLocationID, solarSystemID):
        inventoryMgr = sm.GetService('invCache').GetInventoryMgr()
        visibleFittedItems = inventoryMgr.GetContainerContents(shipID, dockableLocationID, solarSystemID)
        return self.GetFittingDictFromItems(visibleFittedItems, putModuleAmmoInCargo)

    def GetFittingDictFromItems(self, visibleFittedItems, putModuleAmmoInCargo):
        fittingData = self.CreateFittingData(visibleFittedItems, putModuleAmmoInCargo=putModuleAmmoInCargo)
        oringalItemIDByFlagAndTypeID = {(x.typeID, x.flagID):x.itemID for x in visibleFittedItems}
        for eachItem in visibleFittedItems:
            if IsFighterTubeFlag(eachItem.flagID):
                fittingData.append((eachItem.typeID, eachItem.flagID, eachItem.stacksize))

        return (fittingData, oringalItemIDByFlagAndTypeID)

    def GetFittingDictForSimulatedShip(self, putModuleAmmoInCargo = True):
        dogmaLocation = sm.GetService('clientDogmaIM').GetFittingDogmaLocation()
        shipID = dogmaLocation.GetCurrentShipID()
        shipItem = dogmaLocation.GetDogmaItem(shipID)
        fittedItems = shipItem.GetFittedItems()
        visibleFittedItems = (i for i in fittedItems.values() if inventorycommon.ItemIsVisible(i))
        cargoItems = dogmaLocation.GetHoldItems(const.flagCargo)
        fightersInTubes = GetFightersInTubes(dogmaLocation)
        fighterBayItems = dogmaLocation.GetHoldItems(const.flagFighterBay)
        items = list(visibleFittedItems)
        items += shipItem.GetDrones().values()
        items += cargoItems.values()
        items += fightersInTubes
        items += fighterBayItems.values()
        fitData = self.CreateFittingData(items, putModuleAmmoInCargo=putModuleAmmoInCargo)
        return (shipItem.typeID, fitData, items)

    def CreateFittingData(self, items, putModuleAmmoInCargo = True):
        fitData = []
        dronesByType = defaultdict(int)
        chargesByType = defaultdict(int)
        iceByType = defaultdict(int)
        fightersByType = defaultdict(int)
        implantsByType = defaultdict(int)
        modulesInCargo = defaultdict(int)
        filamentsByType = defaultdict(int)
        otherByType = defaultdict(int)
        for item in items:
            typeID = item.typeID
            flagID = item.flagID
            if IsShipFittingFlag(flagID) and IsShipFittable(item.categoryID):
                fitData.append((int(typeID), int(flagID), 1))
            elif item.categoryID == const.categoryDrone and flagID == const.flagDroneBay:
                dronesByType[typeID] += getattr(item, 'stacksize', 1)
            elif item.categoryID == const.categoryFighter and flagID == const.flagFighterBay:
                fightersByType[typeID] += getattr(item, 'stacksize', 1)
            elif item.categoryID == const.categoryFighter and IsFighterTubeFlag(flagID):
                fightersByType[typeID] += getattr(item, 'stacksize', 1)
            elif item.categoryID == const.categoryCharge and flagID == const.flagCargo:
                chargesByType[typeID] += getattr(item, 'stacksize', 1)
            elif item.categoryID == const.categoryImplant and flagID == const.flagCargo:
                implantsByType[typeID] += getattr(item, 'stacksize', 1)
            elif item.categoryID in (const.categoryModule, const.categorySubSystem) and flagID == const.flagCargo:
                modulesInCargo[typeID] += getattr(item, 'stacksize', 1)
            elif hasattr(item, 'groupID') and item.groupID == const.groupIceProduct and flagID == const.flagCargo:
                iceByType[typeID] += getattr(item, 'stacksize', 1)
            elif putModuleAmmoInCargo and item.categoryID == const.categoryCharge and flagID in const.moduleSlotFlags:
                chargesByType[typeID] += getattr(item, 'stacksize', 1)
            elif typeID in evetypes.GetTypeIDsByListID(TYPE_LIST_FILAMENTS):
                filamentsByType[typeID] += getattr(item, 'stacksize', 1)
            elif typeID in evetypes.GetTypeIDsByListID(TYPE_LIST_OTHER_CARGO_HOLD_TYPES):
                otherByType[typeID] += getattr(item, 'stacksize', 1)

        fitData += self.GetDataToAddToFitData(const.flagDroneBay, dronesByType)
        fitData += self.GetDataToAddToFitData(const.flagFighterBay, fightersByType)
        fitData += self.GetDataToAddToFitData(const.flagCargo, chargesByType)
        fitData += self.GetDataToAddToFitData(const.flagCargo, iceByType)
        fitData += self.GetDataToAddToFitData(const.flagCargo, implantsByType)
        fitData += self.GetDataToAddToFitData(const.flagCargo, modulesInCargo)
        fitData += self.GetDataToAddToFitData(const.flagCargo, filamentsByType)
        fitData += self.GetDataToAddToFitData(const.flagCargo, otherByType)
        return fitData

    def GetLoadedChargeTypes(self, items):
        chargesToLoad = []
        for item in items:
            typeID = item.typeID
            flagID = item.flagID
            if item.categoryID == const.categoryCharge and flagID != const.flagCargo:
                chargesToLoad.append((typeID, flagID))

        return chargesToLoad

    def GetDataToAddToFitData(self, flag, qtyByTypeID):
        data = []
        for typeID, quantity in qtyByTypeID.iteritems():
            data.append((int(typeID), int(flag), int(quantity)))

        return data

    def DisplayFittingFromItems(self, shipTypeID, items):
        fitting = self.GetFittingFromItems(shipTypeID, items)
        self.DisplayFitting(fitting)

    def GetFittingFromItems(self, shipTypeID, items):
        newItems = []
        for item in items:
            if not hasattr(item, 'flagID'):
                item.flagID = item.flag
            if not hasattr(item, 'stacksize'):
                item.stacksize = item.qtyDropped + item.qtyDestroyed
            item.categoryID = evetypes.GetCategoryID(item.typeID)
            newItems.append(item)

        fitData = self.CreateFittingData(newItems)
        fitting = utillib.KeyVal()
        fitting.shipTypeID = shipTypeID
        fitting.name = evetypes.GetName(shipTypeID)
        fitting.ownerID = None
        fitting.fittingID = None
        fitting.description = ''
        fitting.fitData = fitData
        return fitting

    def PersistFitting(self, ownerID, name, description, fit = None):
        if name is None or name.strip() == '':
            raise UserError('FittingNeedsToHaveAName')
        name = name.strip()
        fitting = utillib.KeyVal()
        fitting.name = name[:const.maxLengthFittingName]
        fitting.description = description[:const.maxLengthFittingDescription]
        self.PrimeFittings(ownerID)
        if ownerID == session.corpid:
            maxFittings = const.maxCorpFittings
        else:
            maxFittings = const.maxCharFittings
        if len(self.fittings[ownerID]) >= maxFittings:
            owner = cfg.eveowners.Get(ownerID).ownerName
            raise UserError('OwnerMaxFittings', {'owner': owner,
             'maxFittings': maxFittings})
        if fit is None:
            fitting.shipTypeID, fitting.fitData, _ = self.GetFittingDictForActiveShip()
        else:
            fitting.shipTypeID, fitting.fitData = fit
        self.VerifyFitting(fitting)
        fitting.ownerID = ownerID
        existingFitting = self._GetFittingWithName(fitting.shipTypeID, ownerID, name)
        if existingFitting:
            if ownerID == session.corpid:
                question = 'UpdateFitCorp'
            else:
                question = 'UpdateFitPersonal'
            ret = eve.Message(question, {'fittingName': name}, uiconst.YESNO, suppress=uiconst.ID_YES)
            if ret != uiconst.ID_YES:
                return
            if not fitting.description:
                fitting.description = existingFitting.description
        fittingMgr = self.GetFittingMgr(ownerID)
        if existingFitting:
            fittingID = fittingMgr.UpdateFitting(ownerID, fitting, fittingID=existingFitting.fittingID)
        else:
            fittingID = fittingMgr.SaveFitting(ownerID, fitting)
        if fittingID > 0:
            if existingFitting:
                fitting.fittingID = fittingID
                fitting.savedDate = blue.os.GetWallclockTime()
                if ownerID in self.fittings:
                    self.fittings[ownerID][fittingID] = fitting
            self.UpdateFittingWindow()
            sm.ScatterEvent('OnFittingsUpdated', fitting)
        return fittingID

    def _GetFittingWithName(self, shipTypeID, ownerID, name):
        fittingsForOwner = self.GetFittings(ownerID)
        for eachFitID, eachFit in fittingsForOwner.iteritems():
            if eachFit.shipTypeID == shipTypeID and eachFit.name == name:
                return eachFit

    def PersistManyFittings(self, ownerID, fittings):
        if ownerID == session.corpid:
            maxFittings = const.maxCorpFittings
        else:
            maxFittings = const.maxCharFittings
        self.PrimeFittings(ownerID)
        if len(self.fittings[ownerID]) + len(fittings) > maxFittings:
            owner = cfg.eveowners.Get(ownerID).ownerName
            raise UserError('OwnerMaxFittings', {'owner': owner,
             'maxFittings': maxFittings})
        fittingsToSave = {}
        tmpFittingID = INVALID_FITTING_ID
        for fitt in fittings:
            if fitt.name is None or fitt.name.strip() == '':
                raise UserError('FittingNeedsToHaveAName')
            fitting = utillib.KeyVal()
            fitting.fittingID = tmpFittingID
            fitting.name = fitt.name.strip()[:const.maxLengthFittingName]
            fitting.description = fitt.description[:const.maxLengthFittingDescription]
            fitting.shipTypeID = fitt.shipTypeID
            fitting.fitData = fitt.fitData
            self.VerifyFitting(fitting)
            fitting.ownerID = ownerID
            fittingsToSave[tmpFittingID] = fitting
            tmpFittingID -= 1

        newFittingIDs = self.GetFittingMgr(ownerID).SaveManyFittings(ownerID, fittingsToSave)
        for row in newFittingIDs:
            self.fittings[ownerID][row.realFittingID] = fittingsToSave[row.tempFittingID]
            self.fittings[ownerID][row.realFittingID].fittingID = row.realFittingID

        self.UpdateFittingWindow()
        return fitting

    def VerifyFitting(self, fitting):
        if fitting.name.find('@@') != INVALID_FITTING_ID or fitting.description.find('@@') != INVALID_FITTING_ID:
            raise UserError('InvalidFittingInvalidCharacter')
        if fitting.shipTypeID is None:
            raise UserError('InvalidFittingDataTypeID', {'typeName': fitting.shipTypeID})
        shipTypeName = evetypes.GetNameOrNone(fitting.shipTypeID)
        if shipTypeName is None:
            raise UserError('InvalidFittingDataTypeID', {'typeName': fitting.shipTypeID})
        if evetypes.GetCategoryID(fitting.shipTypeID) not in (const.categoryShip, const.categoryStructure):
            raise UserError('InvalidFittingDataShipNotShip', {'typeName': shipTypeName})
        if len(fitting.fitData) == 0:
            raise UserError('ParseFittingFittingDataEmpty')
        for typeID, flag, qty in fitting.fitData:
            if not evetypes.Exists(typeID):
                raise UserError('InvalidFittingDataTypeID', {'typeID': typeID})
            try:
                int(flag)
            except TypeError:
                raise UserError('InvalidFittingDataInvalidFlag', {'type': typeID})

            if not (IsShipFittingFlag(flag) or flag in (const.flagDroneBay, const.flagCargo, const.flagFighterBay)):
                raise UserError('InvalidFittingDataInvalidFlag', {'type': typeID})
            try:
                int(qty)
            except TypeError:
                raise UserError('InvalidFittingDataInvalidQuantity', {'type': typeID})

            if qty == 0:
                raise UserError('InvalidFittingDataInvalidQuantity', {'type': typeID})

        return True

    def GetAllFittingsForCharacter(self):
        ret = uthread.parallel([(self.GetFittings, (session.charid,)),
         (self.GetFittings, (session.corpid,)),
         (self.GetCommunityFittings, ()),
         (self.GetAllianceFittings, ())])
        return ret

    def GetCommunityFittings(self):
        if not AreCommunityFittingsEnabled(sm.GetService('machoNet')):
            return {}
        try:
            if COMMUNITY_FITTING_CORP not in self.fittings:
                corpFittingMgr = sm.RemoteSvc('corpFittingMgr')
                communityFittings = corpFittingMgr.GetCommunityFittings()
                self.fittings[COMMUNITY_FITTING_CORP] = communityFittings
            return self.fittings[COMMUNITY_FITTING_CORP]
        except StandardError as e:
            self.LogException(e)
            return {}

    def GetAllianceFittings(self):
        if session.allianceid:
            return self.GetFittings(session.allianceid)
        return {}

    def GetFittings(self, ownerID):
        self.PrimeFittings(ownerID)
        return self.fittings[ownerID]

    def GetFittingsForType(self, ownerID, typeID):
        allFittings = self.GetFittings(ownerID)
        return [ fitting for fitting in allFittings.items() if fitting[1]['shipTypeID'] == typeID ]

    def PrimeFittings(self, ownerID):
        if ownerID not in self.fittings:
            self.fittings[ownerID] = self.GetFittingMgr(ownerID).GetFittings(ownerID)

    def DeleteFitting(self, ownerID, fittingID):
        self.LogInfo('deleting fitting', fittingID, 'from owner', ownerID)
        self.GetFittingMgr(ownerID).DeleteFitting(ownerID, fittingID)
        if ownerID in self.fittings and fittingID in self.fittings[ownerID]:
            del self.fittings[ownerID][fittingID]
        self.UpdateFittingWindow()

    def DeleteManyFittings(self, fittingsByOwnerID):
        calls = []
        ownerIDs = fittingsByOwnerID.keys()
        totalFittings = 0
        for eachOwnerID in ownerIDs:
            fittingIDs = fittingsByOwnerID.get(eachOwnerID, [])
            totalFittings += len(fittingIDs)
            calls.append((self.GetFittingMgr(eachOwnerID).DeleteManyFittings, (eachOwnerID, fittingIDs)))

        ret = uthread.parallel(calls)
        fittingsDeleted = 0
        for x in ret:
            fittingsDeleted += len(x)

        if len(ownerIDs) > 1:
            ownerText = self.GetDeletedFittingsText(ownerIDs, fittingsByOwnerID, ret)
        else:
            ownerText = ''
        eve.Message('DeletedManyFittings', {'numFittings': fittingsDeleted,
         'ownerText': ownerText})

    def GetDeletedFittingsText(self, ownerIDs, fittingsByOwnerID, deletedFittings):
        textList = []
        for i, ownerID in enumerate(ownerIDs):
            if not ownerID:
                continue
            fittingIDs = fittingsByOwnerID.get(ownerID, [])
            if fittingIDs:
                numDeleted = len(deletedFittings[i])
                numAttempted = len(fittingIDs)
                msgName = 'UI/Fitting/FittingWindow/OwnerAndDeletedFittingNum'
                if numDeleted != numAttempted:
                    msgName = 'UI/Fitting/FittingWindow/OwnerAndDeletedFittingNumWithAttempted'
                ownerName = cfg.eveowners.Get(ownerID).name
                text = localization.GetByLabel(msgName, numFittings=numDeleted, ownerName=ownerName, numAttempted=len(fittingIDs))
                text = u'  \u2022 ' + text
                textList.append(text)

        return '<br>'.join(textList)

    def LoadFittingFromFittingIDAndGetBuyOptionOnFailure(self, ownerID, fittingID):
        fitting = self.fittings.get(ownerID, {}).get(fittingID, None)
        return self.LoadFittingFromFittingListAndGetBuyOptionOnFailure(fitting)

    def LoadFittingFromFittingListAndGetBuyOptionOnFailure(self, fitting):
        failedToLoad = self.LoadFitting(fitting, getFailedDict=True)
        failedToLoadCounter = Counter({x[0]:x[1] for x in failedToLoad})
        if failedToLoadCounter:
            OpenBuyAllBox(failedToLoadCounter, fitting)
        else:
            sm.GetService('ghostFittingSvc').TryExitSimulation()

    def LoadFittingFromFittingID(self, ownerID, fittingID, getFailedDict = False):
        fitting = self.fittings.get(ownerID, {}).get(fittingID, None)
        return self.LoadFitting(fitting, getFailedDict=getFailedDict)

    def CheckBusyFittingAndRaiseIfNeeded(self):
        if self.busyFitting:
            sm.GetService('loading').ProgressWnd('', '', 1, 1)
            raise UserError('CustomInfo', {'info': localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/BusyFittingWarning')})

    def DoFitManyShips(self, shipTypeID, fitInfo, cargoItemsByType, fitRigs, fittingName, maxAvailableFitting, itemContainerID = None):
        shipAccess = sm.StartService('gameui').GetShipAccess()
        try:
            failedInfo = None
            self.busyFitting = True
            sm.GetService('inv').ChangeTreeUpdatingState(isUpdateEnabled=False)
            failedInfo = shipAccess.FitShips(shipTypeID=shipTypeID, fitInfo=fitInfo, itemLocationID=session.stationid or session.structureid, cargoItemsByType=cargoItemsByType, fitRigs=fitRigs, name=fittingName, numToFit=maxAvailableFitting, itemContainerID=itemContainerID)
        finally:
            self.busyFitting = False
            sm.GetService('inv').ChangeTreeUpdatingState(isUpdateEnabled=True)
            if failedInfo:
                failedToLoad, failedShipID = failedInfo
                if failedShipID:
                    self._RenameShip(failedShipID)
                if failedToLoad:
                    self.ShowFailedToLoadMsg(failedToLoad)

    def _RenameShip(self, failedShipID):
        badFitName = localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/BadFitFittingFailed')
        self.invCache.GetInventoryMgr().SetLabel(failedShipID, badFitName)

    def GetMaxAvailabeAndMissingForFullFit(self, fitRigs, itemTypes, numToFit, qtyByTypeID, rigTypeIDs):
        missingForFullFit = {}
        maxRoundsForEachTypeID = {}
        for itemTypID, qtyNeeded in itemTypes.iteritems():
            if not fitRigs and itemTypID in rigTypeIDs:
                continue
            qtyInHangar = qtyByTypeID.get(itemTypID, 0)
            rounds = int(qtyInHangar / qtyNeeded)
            maxRoundsForEachTypeID[itemTypID] = rounds
            if rounds < numToFit:
                missingForFullFit[itemTypID] = qtyNeeded * numToFit - qtyInHangar

        maxAvailableFitting = min(maxRoundsForEachTypeID.values()) if maxRoundsForEachTypeID else None
        return (maxAvailableFitting, missingForFullFit)

    def GetMaxAvailable(self, fitRigs, itemTypes, qtyByTypeID, rigTypeIDs):
        maxRoundsForEachTypeID = {}
        for itemTypID, qtyNeeded in itemTypes.iteritems():
            if not fitRigs and itemTypID in rigTypeIDs:
                continue
            qtyInHangar = qtyByTypeID.get(itemTypID, 0)
            rounds = int(qtyInHangar / qtyNeeded)
            maxRoundsForEachTypeID[itemTypID] = rounds

    def LoadFitting(self, fitting, getFailedDict = False):
        self.CheckBusyFittingAndRaiseIfNeeded()
        self._CheckValidFittingLocation(fitting)
        shipInv = self.invCache.GetInventoryFromId(eveCfg.GetActiveShip())
        shipTypeID = shipInv.GetItem().typeID
        if shipTypeID != fitting.shipTypeID:
            raise UserError('ShipTypeInFittingNotSameAsShip')
        fittingObj = Fitting(fitting.fitData, shipInv)
        rigsByFlags = fittingObj.GetRigsByFlag()
        fitRigs = False
        cargoItemsByType = defaultdict(int)
        if bool(rigsByFlags):
            fittedRigsByFlagID = self.GetFittedRigsByFlagID()
            rigMismatch = IsThereRigMismatch(fittedRigsByFlagID, rigsByFlags)
            sameRigsInSameSlots = rigsByFlags == fittedRigsByFlagID
            if rigMismatch and not IsModularShip(shipTypeID):
                eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Fitting/ShipHasRigsAlready')})
            elif IsModularShip(shipTypeID) or sameRigsInSameSlots:
                fitRigs = True
            elif eve.Message('FitRigs', {}, uiconst.YESNO) == uiconst.ID_YES:
                fitRigs = True
            else:
                for flagID, typeID in fittingObj.GetModulesByFlag().iteritems():
                    if flagID in const.rigSlotFlags:
                        cargoItemsByType[typeID] += 1

        cargoItemsByType = dict(cargoItemsByType)
        itemTypes = fittingObj.GetQuantityByType()
        itemsToFit = defaultdict(set)
        for item in self.invCache.GetInventory(const.containerHangar).List(const.flagHangar):
            if item.typeID in itemTypes:
                qtyNeeded = itemTypes[item.typeID]
                if qtyNeeded == 0:
                    continue
                quantityToTake = min(item.stacksize, qtyNeeded)
                itemsToFit[item.typeID].add(item.itemID)
                itemTypes[item.typeID] -= quantityToTake

        numSubsystems = fittingObj.GetFittingSubSystemNumber()
        if numSubsystems:
            alreadyFitted = {x.typeID for x in shipInv.List() if IsSubsystemFlagVisible(x.flagID)}
            if numSubsystems != invConst.numVisibleSubsystems:
                raise UserError('CantUnfitSubSystems')
            clientDogmaStaticSvc = sm.GetService('clientDogmaStaticSvc')
            for flag, module in fittingObj.GetModulesByFlag().iteritems():
                if not IsSubsystemFlagVisible(flag):
                    continue
                if module in alreadyFitted:
                    continue
                moduleFitsShipType = int(clientDogmaStaticSvc.GetTypeAttribute(module, const.attributeFitsToShipType))
                if shipTypeID != moduleFitsShipType:
                    raise UserError('CannotFitSubSystemNotShip', {'subSystemName': (const.UE_TYPEID, module),
                     'validShipName': (const.UE_TYPEID, moduleFitsShipType),
                     'shipName': (const.UE_TYPEID, shipTypeID)})
                if module in itemTypes and itemTypes[module] > 0:
                    raise UserError('CantUnfitSubSystems')

        self.CheckBusyFittingAndRaiseIfNeeded()
        self.busyFitting = True
        try:
            fittingObjKeyVal = fittingObj.GetKeyValForApplyingFit()
            failedToLoad = shipInv.FitFitting(eveCfg.GetActiveShip(), shipTypeID, itemsToFit, session.stationid or session.structureid, fittingObjKeyVal, cargoItemsByType, fitRigs)
        finally:
            self.busyFitting = False

        if settings.user.ui.Get('useFittingNameForShips', 0):
            fittingName = StripTags(fitting.get('name'))
            fittingName = fittingName[:20]
            self.invCache.GetInventoryMgr().SetLabel(eveCfg.GetActiveShip(), fittingName)
        if getFailedDict:
            return failedToLoad
        self.ShowFailedToLoadMsg(failedToLoad)

    def ShowFailedToLoadMsg(self, failedToLoad):
        textList = []
        for typeID, qty in failedToLoad:
            if qty > 0:
                typeName = evetypes.GetName(typeID)
                link = GetShowInfoLink(typeID, typeName)
                textList.append((typeName.lower(), '%sx %s' % (qty, link)))

        if textList:
            textList = SortListOfTuples(textList)
            text = '<br>'.join(textList)
            text = localization.GetByLabel('UI/Fitting/MissingItems', types=text)
            eve.Message('CustomInfo', {'info': text}, modal=False)

    def _CheckValidFittingLocation(self, fitting):
        if session.stationid is None and session.structureid is None:
            raise UserError('CannotLoadFittingInSpace')
        if fitting is None:
            raise UserError('FittingDoesNotExist')

    def GetQtyInLocationByTypeIDs(self, itemTypes, onlyGetNonSingletons = False, locationID = None):
        if locationID is None:
            containerLocation = self.invCache.GetInventory(const.containerHangar)
            itemList = containerLocation.List(const.flagHangar)
        else:
            containerLocation = self.invCache.GetInventoryFromId(locationID)
            itemList = containerLocation.List()
        qtyByTypeID = defaultdict(int)
        for item in itemList:
            if item.typeID in itemTypes:
                if onlyGetNonSingletons and item.quantity < 0:
                    continue
                qtyByTypeID[item.typeID] += item.stacksize

        return qtyByTypeID

    def FindPersonalContainers(self):
        hangar = self.invCache.GetInventory(const.containerHangar)
        personalContainers = set()
        validContainers = (invConst.groupAuditLogSecureContainer,
         invConst.groupSecureCargoContainer,
         invConst.groupCargoContainer,
         invConst.groupFreightContainer)
        for item in hangar.List(const.flagHangar):
            if item.groupID in validContainers and item.ownerID == session.charid and item.singleton:
                personalContainers.add(item)

        return personalContainers

    def GetTypesToFit(self, fitting, shipInv):
        fittingObj = Fitting(fitting.fitData, shipInv)
        return (fittingObj.GetChargesByType(),
         fittingObj.GetDronesByType(),
         fittingObj.GetFigthersByType(),
         fittingObj.GetIceByType(),
         fittingObj.GetQuantityByType(),
         fittingObj.GetModulesByFlag(),
         fittingObj.GetRigsByFlag(),
         fittingObj.GetFittingSubSystemNumber())

    def GetFittedRigsByFlagID(self):
        rigsFittedByFlagID = {}
        shipInv = self.invCache.GetInventoryFromId(eveCfg.GetActiveShip(), locationID=session.stationid)
        for item in shipInv.List():
            if const.flagRigSlot0 <= item.flagID <= const.flagRigSlot7:
                rigsFittedByFlagID[item.flagID] = item.typeID

        return rigsFittedByFlagID

    def UpdateFittingWindow(self):
        wnd = FittingMgmt.GetIfOpen()
        if wnd is not None:
            wnd.DrawFittings()

    def ChangeNameAndDescription(self, fittingID, ownerID, name, description):
        if name is None or name.strip() == '':
            raise UserError('FittingNeedsToHaveAName')
        name = name.strip()
        fittings = self.GetFittings(ownerID)
        if fittingID in fittings:
            fitting = fittings[fittingID]
            if name != fitting.name or description != fitting.description:
                if name.find('@@') != INVALID_FITTING_ID or description.find('@@') != INVALID_FITTING_ID:
                    raise UserError('InvalidFittingInvalidCharacter')
                self.GetFittingMgr(ownerID).UpdateNameAndDescription(fittingID, ownerID, name, description)
                self.fittings[ownerID][fittingID].name = name
                self.fittings[ownerID][fittingID].description = description
        self.UpdateFittingWindow()

    def GetFitting(self, ownerID, fittingID):
        self.PrimeFittings(ownerID)
        if fittingID in self.fittings[ownerID]:
            return self.fittings[ownerID][fittingID]

    def CheckFittingExist(self, ownerID, shipTypeID, fitData):
        fittings = self.GetFittings(ownerID)
        fittingExists = False
        for fitting in fittings.itervalues():
            if fitting.shipTypeID != shipTypeID:
                continue
            if fitting.fitData != fitData:
                continue
            fittingExists = True

        return fittingExists

    def DisplayFittingFromString(self, fittingString, name = None):
        fitting, truncated = self.GetFittingFromString(fittingString, name)
        if fitting == INVALID_FITTING_ID:
            raise UserError('FittingInvalidForViewing')
        self.DisplayFitting(fitting, truncated=truncated)

    def DisplayFitting(self, fitting, truncated = False):
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            fittingsList = fitting.fitData[:]
            fittingsList.sort()
            newFittingStr = '%s' % fittingsList
            windowID = 'ViewFitting_%s' % newFittingStr
        else:
            windowID = 'ViewFitting'
        wnd = ViewFitting.GetIfOpen(windowID=windowID)
        if wnd:
            wnd.ReloadWnd(windowID=windowID, fitting=fitting, truncated=truncated)
            wnd.Maximize()
        else:
            ViewFitting.Open(windowID=windowID, fitting=fitting, truncated=truncated)

    def GetStringForFitting(self, fitting):
        typesDict = defaultdict(int)
        drones = {}
        fighters = {}
        charges = {}
        ice = {}
        implants = {}
        modules = {}
        filaments = {}
        otherCargoItems = {}
        for typeID, flag, qty in fitting.fitData:
            categoryID = evetypes.GetCategoryID(typeID)
            groupID = evetypes.GetGroupID(typeID)
            if IsShipFittable(categoryID):
                if flag == const.flagCargo:
                    modules[typeID] = qty
                else:
                    typesDict[typeID] += 1
            elif categoryID == const.categoryDrone:
                drones[typeID] = qty
            elif categoryID == const.categoryFighter:
                fighters[typeID] = qty
            elif categoryID == const.categoryCharge:
                charges[typeID] = qty
            elif categoryID == const.categoryImplant:
                implants[typeID] = qty
            elif groupID == const.groupIceProduct:
                ice[typeID] = qty
            elif typeID in evetypes.GetTypeIDsByListID(TYPE_LIST_FILAMENTS):
                filaments[typeID] = qty
            elif typeID in evetypes.GetTypeIDsByListID(TYPE_LIST_OTHER_CARGO_HOLD_TYPES):
                otherCargoItems[typeID] = qty

        retList = []
        subString = str(fitting.shipTypeID)
        retList.append(subString)
        for eachDict in [typesDict,
         drones,
         fighters,
         charges,
         ice,
         implants,
         filaments,
         otherCargoItems]:
            for typeID, qty in eachDict.iteritems():
                subString = '%s;%s' % (typeID, qty)
                retList.append(subString)

        for typeID, qty in modules.iteritems():
            subString = '%s%s;%s' % (typeID, CARGO_MARKER, qty)
            retList.append(subString)

        ret = ':'.join(retList)
        ret += '::'
        return ret

    def GetFittingFromString(self, fittingString, name = None):
        effectSlots = {const.effectHiPower: const.flagHiSlot0,
         const.effectMedPower: const.flagMedSlot0,
         const.effectLoPower: const.flagLoSlot0,
         const.effectRigSlot: const.flagRigSlot0,
         const.effectSubSystem: const.flagSubSystemSlot0,
         const.effectServiceSlot: const.flagServiceSlot0}
        truncated = False
        if not fittingString.endswith('::'):
            truncated = True
            fittingString = fittingString[:fittingString.rfind(':')]
        data = fittingString.split(':')
        fitting = utillib.KeyVal()
        fitData = []
        for line in data:
            typeInfo = line.split(';')
            if line == '':
                continue
            if len(typeInfo) == 1:
                try:
                    fitting.shipTypeID = int(typeInfo[0])
                except ValueError:
                    return (INVALID_FITTING_ID, truncated)

                continue
            typeID, qty = typeInfo
            inCargo = False
            if typeID.endswith(CARGO_MARKER):
                typeID = typeID[:-1]
                inCargo = True
            try:
                typeID, qty = int(typeID), int(qty)
            except ValueError:
                continue

            powerEffectID = sm.GetService('godma').GetPowerEffectForType(typeID)
            if powerEffectID is not None and not inCargo:
                startSlot = effectSlots[powerEffectID]
                for flag in xrange(startSlot, startSlot + qty):
                    fitData.append((typeID, flag, 1))

                effectSlots[powerEffectID] = flag + 1
            else:
                categoryID = evetypes.GetCategoryID(typeID)
                groupID = evetypes.GetGroupID(typeID)
                if categoryID == const.categoryDrone:
                    fitData.append((typeID, const.flagDroneBay, qty))
                if categoryID == const.categoryFighter:
                    fitData.append((typeID, const.flagFighterBay, qty))
                elif categoryID in (const.categoryCharge,
                 const.categoryImplant,
                 const.categoryModule,
                 const.categorySubSystem):
                    fitData.append((typeID, const.flagCargo, qty))
                elif groupID == const.groupIceProduct:
                    fitData.append((typeID, const.flagCargo, qty))
                elif typeID in evetypes.GetTypeIDsByListID(TYPE_LIST_FILAMENTS):
                    fitData.append((typeID, const.flagCargo, qty))
                elif typeID in evetypes.GetTypeIDsByListID(TYPE_LIST_OTHER_CARGO_HOLD_TYPES):
                    fitData.append((typeID, const.flagCargo, qty))
                else:
                    continue

        shipName = name or evetypes.GetName(fitting.shipTypeID)
        fitting.name = shipName
        fitting.ownerID = None
        fitting.fittingID = None
        fitting.description = ''
        fitting.fitData = fitData
        return (fitting, truncated)

    def GetFittingInfoScrollList(self, fitting):
        scrollListData = self.GetFittingInfoForScrollList(fitting)
        scrollList = []
        for d in scrollListData:
            if isinstance(d, KeyVal):
                entry = GetFromClass(FittingModuleEntry, d)
                scrollList.append(entry)
            else:
                scrollList.append(d)

        return scrollList

    def GetFittingInfoForScrollList(self, fitting):
        scrollListData = []
        typesByRack = self.GetTypesByRack(fitting)
        for key, effectID in [('hiSlots', const.effectHiPower),
         ('medSlots', const.effectMedPower),
         ('lowSlots', const.effectLoPower),
         ('rigSlots', const.effectRigSlot),
         ('subSystems', const.effectSubSystem),
         ('serviceSlots', const.effectServiceSlot)]:
            slots = typesByRack[key]
            if len(slots) < 1:
                continue
            label = dogma.data.get_effect_display_name(effectID)
            scrollListData.append(GetFromClass(Header, {'label': label}))
            dataForEffect = []
            for typeID, qty in slots.iteritems():
                data = self._GetDataForFittingEntry(typeID, qty)
                data.singleton = 1
                data.effectID = effectID
                dataForEffect.append((evetypes.GetGroupID(typeID), data))

            dataForEffect = SortListOfTuples(dataForEffect)
            scrollListData.extend(dataForEffect)

        for qtyByTypeIdDict, headerLabelPath, isValidGroup in ((typesByRack['charges'], 'UI/Generic/Charges', True),
         (typesByRack['ice'], 'UI/Inflight/MoonMining/Processes/Fuel', True),
         (typesByRack['drones'], 'UI/Drones/Drones', True),
         (typesByRack['fighters'], 'UI/Common/Fighters', True),
         (typesByRack['implants'], 'UI/Fitting/FittingWindow/ImplantsAndBoosters', True),
         (typesByRack['modules'], 'UI/Fitting/FittingWindow/FittingManagement/Modules', True),
         (typesByRack['filaments'], 'UI/Fitting/FittingWindow/FittingManagement/Filaments', True),
         (typesByRack['otherInCargo'], 'UI/Fitting/FittingWindow/FittingManagement/OtherItemsInCargo', True),
         (typesByRack['other'], 'UI/Fitting/FittingWindow/FittingManagement/OtherItems', False)):
            if len(qtyByTypeIdDict) > 0:
                scrollListData.append(GetFromClass(Header, {'label': localization.GetByLabel(headerLabelPath)}))
                scrollListData += self._GetFittingEntryDataForGroup(qtyByTypeIdDict, isValidGroup)

        return scrollListData

    def _GetFittingEntryDataForGroup(self, qtyByTypeIdDict, isValidGroup):
        dataList = []
        for typeID, qty in qtyByTypeIdDict.iteritems():
            data = self._GetDataForFittingEntry(typeID, qty, isValidGroup)
            dataList.append(data)

        return dataList

    def _GetDataForFittingEntry(self, typeID, qty, isValidGroup = True):
        isObsolete = bool(sm.GetService('clientDogmaStaticSvc').GetTypeAttribute(typeID, const.attributeModuleIsObsolete))
        data = utillib.KeyVal(typeID=typeID, showinfo=1, getIcon=True, label=unicode(FmtAmt(qty)) + 'x ' + evetypes.GetName(typeID), isValidGroup=isValidGroup, isObsolete=isObsolete)
        return data

    def GetTypesByRack(self, fitting):
        ret = {'hiSlots': defaultdict(int),
         'medSlots': defaultdict(int),
         'lowSlots': defaultdict(int),
         'rigSlots': defaultdict(int),
         'subSystems': defaultdict(int),
         'serviceSlots': defaultdict(int),
         'charges': {},
         'drones': {},
         'ice': {},
         'fighters': {},
         'implants': {},
         'modules': {},
         'filaments': {},
         'otherInCargo': {},
         'other': {}}
        for typeID, flag, qty in fitting.fitData:
            if evetypes.GetCategoryID(typeID) == const.categoryCharge:
                ret['charges'][typeID] = qty
            elif evetypes.GetCategoryID(typeID) == const.categoryImplant:
                ret['implants'][typeID] = qty
            elif evetypes.GetGroupID(typeID) == const.groupIceProduct:
                ret['ice'][typeID] = qty
            elif flag in const.hiSlotFlags:
                ret['hiSlots'][typeID] += 1
            elif flag in const.medSlotFlags:
                ret['medSlots'][typeID] += 1
            elif flag in const.loSlotFlags:
                ret['lowSlots'][typeID] += 1
            elif flag in const.rigSlotFlags:
                ret['rigSlots'][typeID] += 1
            elif const.flagServiceSlot0 <= flag <= const.flagServiceSlot7:
                ret['serviceSlots'][typeID] += 1
            elif IsSubsystemFlagVisible(flag):
                ret['subSystems'][typeID] += 1
            elif flag == const.flagDroneBay:
                ret['drones'][typeID] = qty
            elif flag == const.flagFighterBay:
                ret['fighters'][typeID] = qty
            elif evetypes.GetCategoryID(typeID) in (const.categoryModule, const.categorySubSystem) and flag == const.flagCargo:
                ret['modules'][typeID] = qty
            elif typeID in evetypes.GetTypeIDsByListID(TYPE_LIST_FILAMENTS):
                ret['filaments'][typeID] = qty
            elif typeID in evetypes.GetTypeIDsByListID(TYPE_LIST_OTHER_CARGO_HOLD_TYPES):
                ret['otherInCargo'][typeID] = qty
            else:
                ret['other'][typeID] = qty

        return ret

    def HasSkillForFit(self, fitting):
        fittingID = fitting.fittingID
        try:
            return self.hasSkillByFittingID[fittingID]
        except KeyError:
            self.LogInfo('HasSkillForFit::Cache miss', fittingID)
            sys.exc_clear()

        hasSkill = self.hasSkillByFittingID[fittingID] = self.CheckSkillRequirementsForFit(fitting)
        return hasSkill

    def CheckSkillRequirementsForFit(self, fitting):
        godma = sm.GetService('godma')
        if not godma.CheckSkillRequirementsForType(fitting.shipTypeID):
            return False
        for typeID, flag, qty in fitting.fitData:
            if flag in inventorycommon.const.rigSlotFlags:
                continue
            if not godma.CheckSkillRequirementsForType(typeID):
                return False

        return True

    def GetAllFittings(self):
        ret = {}
        charFittings = self.GetFittings(session.charid)
        corpFittings = self.GetFittings(session.corpid)
        for fittingID in charFittings:
            ret[fittingID] = charFittings[fittingID]

        for fittingID in corpFittings:
            ret[fittingID] = corpFittings[fittingID]

        if session.allianceid:
            allianceFittings = self.GetFittings(session.allianceid)
            for fittingID, fitting in allianceFittings.iteritems():
                ret[fittingID] = fitting

        return ret

    def OnSkillsChanged(self, *args):
        self.hasSkillByFittingID = {}

    def OnFittingAdded(self, ownerID, fitID):
        if ownerID in self.fittings:
            deleteFits = False
            if isinstance(fitID, (int, long)):
                if fitID not in self.fittings[ownerID]:
                    deleteFits = True
            elif isinstance(fitID, list):
                if any((x in self.fittings[ownerID] for x in fitID)):
                    deleteFits = True
            else:
                raise RuntimeError("fitID should always be an int, long, or list. It wasn't. fitID = {} and type(fitID) = {}".format(fitID, type(fitID)))
            if deleteFits is True:
                del self.fittings[ownerID]
                self.UpdateFittingWindow()
                sm.ScatterEvent('OnFittingsUpdated')

    def OnFittingDeleted(self, ownerID, fitID):
        if ownerID in self.fittings:
            removed = self._OnFittingDeleted(ownerID, fitID)
            if removed:
                self.UpdateFittingWindow()
                sm.ScatterEvent('OnFittingsUpdated')

    def _OnFittingDeleted(self, ownerID, fitID):
        if fitID in self.fittings[ownerID]:
            del self.fittings[ownerID][fitID]
            return True
        return False

    def OnManyFittingsDeleted(self, ownerID, fitIDs):
        if ownerID not in self.fittings:
            return
        numRemoved = 0
        for fitID in fitIDs:
            removed = self._OnFittingDeleted(ownerID, fitID)
            numRemoved += removed

        if numRemoved:
            self.UpdateFittingWindow()
            sm.ScatterEvent('OnFittingsUpdated')

    def OnFittingsUpdated(self, fitting = None):
        if not self.IsShipSimulated() or fitting is None:
            return
        shipTypeID, fittingDataInWnd, allItems = self.GetFittingDictForSimulatedShip(putModuleAmmoInCargo=True)
        if fitting.shipTypeID != shipTypeID:
            return
        savedData = sorted(fitting.fitData)
        currentData = sorted(fittingDataInWnd)
        if savedData == currentData:
            sm.GetService('ghostFittingSvc').ResetSimulationChangedFlag()

    def ImportFittingFromClipboard(self, *args):
        try:
            textInField = GetClipboardData()
            shipName, fitName = FindShipAndFittingName(textInField)
            importFittingUtil = self.GetImportFittingUtil()
            shipTypeID = importFittingUtil.GetTypeIDFromName(shipName.lower())
            if not shipTypeID:
                eve.Message('ImportingErrorFromClipboard')
                return
            itemLines, errorLines = importFittingUtil.GetAllItems(textInField)
            fitData = importFittingUtil.CreateFittingData(itemLines, shipTypeID)
            if not fitData:
                eve.Message('ImportingErrorFromClipboard')
                return
            fittingData = utillib.KeyVal(shipTypeID=shipTypeID, fitData=fitData, fittingID=None, description='', name=fitName, ownerID=0)
            self.DisplayFitting(fittingData)
            if errorLines:
                errorText = '<br>'.join(errorLines)
                text = '<b>%s</b><br>%s' % (localization.GetByLabel('UI/SkillQueue/CouldNotReadLines'), errorText)
                eve.Message('CustomInfo', {'info': text})
        except Exception as e:
            log.LogWarn('Failed to import fitting from clipboard, e = ', e)
            eve.Message('ImportingErrorFromClipboard')

    def GetImportFittingUtil(self):
        if self.importFittingUtil is None:
            self.importFittingUtil = ImportFittingUtil(dogma.data.get_all_type_effects(), sm.GetService('clientDogmaStaticSvc'), IsUsingDefaultLanguage(session))
        return self.importFittingUtil

    def ExportFittingToClipboard(self, fitting, isLocalized = False):
        fittingString = GetFittingEFTString(fitting, isLocalized=isLocalized)
        blue.pyos.SetClipboardData(fittingString)

    def SaveFitting(self, *args):
        return self.DoSaveFitting()

    def DoSaveFitting(self, name = None):
        fitting = self.GetFittingForCurrentInWnd()
        if name:
            fitting.name = name
        windowID = 'Save_ViewFitting_%s' % fitting.shipTypeID
        wnd = ViewFitting.GetIfOpen(windowID=windowID)
        if wnd and not wnd.destroyed:
            wnd.ReloadWnd(windowID, fitting, truncated=None)
            wnd.Maximize()
        else:
            ViewFitting.Open(windowID=windowID, fitting=fitting, truncated=None)

    def GetFittingForCurrentInWnd(self, putModuleAmmoInCargo = True):
        fitting = KeyVal()
        fitting.shipTypeID, fitting.fitData, _ = self.GetFittingDictForCurrentFittingWindowShip(putModuleAmmoInCargo=putModuleAmmoInCargo)
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        desc = ''
        if self.inSimulation:
            ownerID = ghostFittingSvc.lastLoadedFitInfo[0]
            fittingID = ghostFittingSvc.lastLoadedFitInfo[1]
            if ownerID and fittingID:
                originalFit = self.GetFitting(ownerID, fittingID)
                if originalFit:
                    desc = originalFit['description']
        fitting.fittingID = None
        fitting.description = desc
        if self.inSimulation:
            shipName = ghostFittingSvc.GetShipName()
        else:
            shipName = cfg.evelocations.Get(GetActiveShip()).locationName
        fitting.name = shipName
        fitting.ownerID = 0
        return fitting

    def GetShipIDForFittingWindow(self):
        if self.IsShipSimulated():
            fittingDL = self.GetCurrentDogmaLocation()
            return fittingDL.GetCurrentShipID()
        return eveCfg.GetActiveShip()

    def GetCurrentDogmaLocation(self):
        if self.IsShipSimulated():
            return sm.GetService('clientDogmaIM').GetFittingDogmaLocation()
        else:
            return sm.GetService('clientDogmaIM').GetDogmaLocation()

    def IsShipSimulated(self):
        return self.inSimulation

    def SetSimulationState(self, simulationOn = False):
        ghostFittingController = sm.GetService('ghostFittingSvc').GetGhostFittingController()
        if ghostFittingController:
            ghostFittingController.SetSimulationState(simulationOn)
        self.inSimulation = simulationOn

    def RemoveAndLoadChargesFromSimulatedShip(self, clientDL, actualShipItemID, simulatedChargeTypesAndQtyByFlagID):
        actualShipInv = sm.GetService('invCache').GetInventoryFromId(actualShipItemID)
        visibleFittedItems = [ i for i in actualShipInv.List() if inventorycommon.ItemIsVisible(i) ]
        actualShip_chargeTypesAndQtyByFlagID = self.GetChargesAndQtyByFlag(visibleFittedItems)
        if actualShip_chargeTypesAndQtyByFlagID == simulatedChargeTypesAndQtyByFlagID:
            return {}
        moduleIDs = {i.itemID for i in visibleFittedItems if i.flagID in inventorycommon.const.moduleSlotFlags and i.categoryID != const.categoryCharge}
        moduleIDs = {i for i in moduleIDs if not clientDL.IsModuleSlave(i, actualShipItemID)}
        clientDL.UnloadAmmoFromModules(actualShipItemID, moduleIDs, (session.structureid or session.stationid, session.charid, const.flagHangar))
        blue.pyos.synchro.Yield()
        return self.FitSimulatedCharges(clientDL, simulatedChargeTypesAndQtyByFlagID)

    def FitSimulatedCharges(self, clientDL, simulated_chargeTypesAndQtyByFlagID):
        fitted = clientDL.GetShip().GetFittedItems()
        fittedByFlagID = {x.flagID:x for x in fitted.itervalues() if x.categoryID != const.categoryCharge}
        hangar = sm.GetService('invCache').GetInventory(const.containerHangar)
        invItemsByTypeIDs = defaultdict(list)
        for x in hangar.List(const.flagHangar):
            invItemsByTypeIDs[x.typeID].append(x)

        ammoFailedToLoad = defaultdict(int)
        for flagID, chargeInfo in simulated_chargeTypesAndQtyByFlagID.iteritems():
            chargeTypeID, qty = chargeInfo
            moduleItem = fittedByFlagID.get(flagID, None)
            if not moduleItem:
                continue
            invItemsForType = invItemsByTypeIDs.get(chargeTypeID, None)
            if not invItemsForType:
                ammoFailedToLoad[chargeTypeID] += qty
                continue
            try:
                moduleID = moduleItem.itemID
                if moduleID < invConst.flagSlotLast:
                    log.LogTraceback('FitSimulatedCharges: ModuleID invalid')
                clientDL.LoadChargesToModule(moduleID, invItemsForType, invItemsForType[0].locationID)
            except UserError as e:
                if e.msg == 'CannotLoadNotEnoughCharges':
                    ammoFailedToLoad[chargeTypeID] += qty
                else:
                    raise

        return ammoFailedToLoad

    def GetChargesAndQtyByFlag(self, fittedItems):
        chargeTypesAndQtyByFlagID = defaultdict(int)
        for item in fittedItems:
            flagID = item.flagID
            if item.categoryID == const.categoryCharge and flagID in const.moduleSlotFlags:
                stacksize = getattr(item, 'stacksize', 1)
                chargeTypesAndQtyByFlagID[flagID] = (item.typeID, stacksize)

        return chargeTypesAndQtyByFlagID

    def OnGlobalConfigChanged(self, configVals):
        if not AreCommunityFittingsEnabled(sm.GetService('machoNet')):
            self.ClearCommunityFittingCache()

    def OnCommunityFittingsUpdated(self):
        self.ClearCommunityFittingCache()

    def ClearCommunityFittingCache(self):
        if COMMUNITY_FITTING_CORP in self.fittings:
            self.fittings.pop(COMMUNITY_FITTING_CORP)
            sm.StartService('objectCaching').InvalidateCachedMethodCall('corpFittingMgr', 'GetCommunityFittings')
