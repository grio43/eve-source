#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\invCache.py
import copy
import sys
import traceback
from functools import wraps
import blue
import dogma.data
import evetypes
import localization
import log
import stackless
import telemetry
import uthread
from caching.memoize import Memoize
from carbon.common.script.net.moniker import Moniker
from carbon.common.script.sys.crowset import CRowset
from carbon.common.script.sys.row import Row
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_ADMIN
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from eve.client.script.ui.inflight.shipHud import ActiveShipController
from eve.client.script.ui.util import utilWindows
from eve.common.lib import appConst as const
from eve.common.script.net import eveMoniker
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.util import inventoryFlagsCommon
from eveexceptions import UserError
from inventorycommon.const import flagFrigateEscapeBay
from inventorycommon.util import GetItemVolume, IsFittingFlag, IsFittable
from inventoryrestrictions import can_be_unfitted, ItemCannotBeUnfitted
from resourcewars.common.const import RW_CORPORATIONS
CAPACITY_ATTRIBUTES = (const.attributeCapacity,
 const.attributeDroneCapacity,
 const.attributeShipMaintenanceBayCapacity,
 const.attributeFleetHangarCapacity)
SPECIAL_CONTAINER_IDS = [const.containerWallet,
 const.containerStationCharacters,
 const.containerGlobal,
 const.containerSolarSystem,
 const.containerRecycler,
 const.containerCharacter]
PRIVATE_SHIP_FLAGS = [const.flagCargo]
PRIVATE_STRUCTURE_FLAGS = [const.flagHangar]
PRIVATE_STATION_FLAGS = [const.flagHangar, const.flagShipHangar]
PRIVATE_STATION_CONTAINERS = [const.containerHangar]

class UnavailableInventoryLocation(Exception):

    def __init__(self, locationName):
        super(UnavailableInventoryLocation, self).__init__(self)
        self.message = 'Failed to retrieve items; character is not located in a %s' % locationName

    def __str__(self):
        return self.message


def RaiseIfInventoryLocationUnavailable(sessionCheck, locationName):

    def RaiseIfInventoryLocationUnavailableDecorator(f):

        @wraps(f)
        def wrapped(*args, **kwargs):
            if not sessionCheck():
                raise UnavailableInventoryLocation(locationName)
            try:
                return f(*args, **kwargs)
            except Exception:
                raise UnavailableInventoryLocation(locationName)

        return wrapped

    return RaiseIfInventoryLocationUnavailableDecorator


class invCache(Service):
    __guid__ = 'svc.invCache'
    __exportedcalls__ = {'GetInventory': [],
     'GetInventoryFromId': [],
     'GetInventoryMgr': [],
     'GetItemHeader': [],
     'IsItemLocked': [],
     'TryLockItem': [],
     'UnlockItem': [],
     'GetStationIDOfItem': [],
     'IsInventoryPrimedAndListed': [],
     'InvalidateLocationCache': [],
     'AcceptPossibleRemovalTax': []}
    __dependencies__ = []
    __notifyevents__ = ['ProcessSessionChange',
     'OnSessionChanged',
     'OnItemsChanged',
     'OnItemChange',
     'OnCapacityChange',
     'OnPasswordChanged',
     'DoBallRemove',
     'OnDogmaAttributeChanged',
     'ProcessActiveShipChanged',
     'DoBallsRemove',
     'OnSessionReset',
     'OnInvalidateCacheForLocations']

    def __init__(self):
        super(invCache, self).__init__()
        self.Initialize()

    def Initialize(self):
        self.__invmgr = None
        self.__invlocID = 0
        self.__stationinvmgr = None
        self.__stationID = 0
        self.__itemhdr = None
        self.inventories = {}
        self.containerGlobal = None
        self.lockedItems = {}
        self.lockedItemsSemaphore = uthread.Semaphore()
        self.trace = 0
        self.locks = {}

    def Run(self, ms = None):
        sm.FavourMe(self.OnItemChange)
        sm.FavourMe(self.ProcessSessionChange)
        sm.FavourMe(self.OnCapacityChange)
        self.LogInfo('invCache lock tracing:', ['OFF', 'ON'][self.trace])

    def Stop(self, memStream = None):
        self.InvalidateCache()

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return
        if self.inventories.has_key((ball.id, None)):
            del self.inventories[ball.id, None]

    def ProcessSessionChange(self, isRemote, session, change):
        try:
            if not session.charid:
                return self.InvalidateCache()
            if 'corprole' in change and session.stationid:
                self.LogInfo('ProcessSessionChange corprole in station')
                office = sm.GetService('officeManager').GetCorpOfficeAtLocation()
                if office is not None:
                    key = (office.officeID, None)
                    if key in self.inventories:
                        self.LogInfo('Removing inventory for corp hangar')
                        del self.inventories[key]
            if 'shipid' in change and session.solarsystemid is not None:
                key = (change['shipid'][0], None)
                if key in self.inventories:
                    del self.inventories[key]
                return
            if not self._ShouldInvalidateCache(change):
                return
            self.InvalidateCache()
        finally:
            sm.services['godma'].ProcessSessionChange(isRemote, session, change)

    def _ShouldInvalidateCache(self, change):
        return 'stationid' in change or 'structureid' in change or 'solarsystemid' in change

    def OnSessionChanged(self, isRemote, sess, change):
        if ROLE_ADMIN & eve.session.role == ROLE_ADMIN:
            self.trace = 1
        else:
            self.trace = 0
        if 'corprole' in change and (session.stationid or session.structureid):
            self.LogInfo('OnSessionChanged corprole in station')
            self.InvalidateCorpCache()

    def OnSessionReset(self):
        self.InvalidateCache()
        self.Initialize()

    def OnPasswordChanged(self, which, containerItem):
        self.RemoveInventoryContainer(containerItem)

    def __getattr__(self, key):
        if key == 'inventorymgr':
            while eve.session.IsMutating() and not eve.session.IsChanging():
                self.LogInfo('Sleeping while waiting for a session change or mutation to complete')
                blue.pyos.synchro.SleepSim(250)

            if self.__invmgr is None or self.__invlocID != eve.session.locationid:
                self.__invlocID = eve.session.locationid
                self.__invmgr = eveMoniker.GetInventoryMgr()
            return self.__invmgr
        if key == 'stationInventoryMgr':
            while session.IsMutating() and not session.IsChanging():
                self.LogInfo('Sleeping while waiting for a session change or mutation to complete')
                blue.pyos.synchro.SleepSim(250)

            if self.__stationinvmgr is None or self.__stationID != session.stationid:
                if session.stationid is None:
                    raise RuntimeError('CharacterNotAtStation')
                self.__stationID = session.stationid
                self.__stationinvmgr = eveMoniker.GetStationInventoryMgr(session.stationid)
            return self.__stationinvmgr
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        raise AttributeError, key

    def OnItemsChanged(self, items, change, location):
        self.LogInfo('server says do change ', change, ' for ', len(items), ' items:', items)
        self.ValidateLocationCacheForItems(items)
        for i, item in enumerate(items):
            sm.ScatterEvent('OnItemChange', item, change, location)
            blue.pyos.BeNice()

        sm.ScatterEvent('OnMultipleItemChange', items, change)

    def OnItemChange(self, item, change, location):
        if const.ixQuantity in change:
            log.LogTraceback('invCache processing a ixQuantity change')
            if change[const.ixQuantity] < 0 or item.quantity < 0:
                raise RuntimeError('OnItemChange in invCache: negative qty', item, change)
        try:
            lockKey = item.itemID
            uthread.Lock(self, lockKey)
            try:
                self.LockedItemChange(item, change)
                oldItem = blue.DBRow(item)
                for k, v in change.iteritems():
                    if k in (const.ixStackSize, const.ixSingleton):
                        k = const.ixQuantity
                    oldItem[k] = v

                keyIs, keyWas = (None, None)
                if session.stationid:
                    if item.locationID == session.stationid:
                        if item.ownerID == eve.session.charid or item.ownerID == eve.session.corpid:
                            keyIs = (const.containerHangar, None)
                        if item.flagID == const.flagCorpDeliveries:
                            keyIs = (const.containerCorpMarket, item.ownerID)
                        elif keyIs is None:
                            keyIs = (const.containerHangar, item.ownerID)
                    if oldItem.locationID == session.stationid:
                        if oldItem.ownerID == eve.session.charid or oldItem.ownerID == eve.session.corpid:
                            keyWas = (const.containerHangar, None)
                        if oldItem.flagID == const.flagCorpDeliveries:
                            keyWas = (const.containerCorpMarket, oldItem.ownerID)
                        elif keyWas is None:
                            keyWas = (const.containerHangar, oldItem.ownerID)
                if keyIs is None:
                    keyIs = (item.locationID, None)
                if keyWas is None:
                    keyWas = (oldItem.locationID, None)
                if keyWas and self.inventories.has_key(keyWas):
                    inv = self.inventories[keyWas]
                    inv.OnItemChange(item, change, location)
                if keyIs != keyWas or const.ixFlag in change:
                    if keyIs and self.inventories.has_key(keyIs):
                        inv = self.inventories[keyIs]
                        inv.OnItemChange(item, change, location)
                if idCheckers.IsJunkLocation(item.locationID) or const.ixOwnerID in change or (const.ixQuantity in change or const.ixStackSize in change) and item.stacksize == 0:
                    if idCheckers.IsJunkLocation(item.locationID):
                        self.LogInfo('REMOVING:', item.itemID, 'item is in junk location')
                    elif const.ixOwnerID in change:
                        self.LogInfo('REMOVING:', item.itemID, ' ownership changed')
                    elif const.ixStackSize in change and item.stacksize == 0:
                        self.LogInfo('REMOVING:', item.itemID, ' new stacksize is 0')
                    if const.ixLocationID in change:
                        if self.containerGlobal:
                            self.containerGlobal.TrashItem(change[const.ixLocationID], item.itemID, item.locationID)
                if self.inventories.has_key((item.itemID, None)):
                    if oldItem.ownerID == eve.session.charid != item.ownerID:
                        del self.inventories[item.itemID, None]
                    else:
                        self.inventories[item.itemID, None].item = item
            finally:
                sm.services['godma'].OnItemChange(item, change, location)
                sm.services['inv'].OnItemChange(item, change, location)
                sm.ScatterEvent('OnItemChanged', item, change, location)

        finally:
            uthread.UnLock(self, lockKey)

    def LockedItemChange(self, item, change):
        self.UnlockItem(item.itemID)

    def TryLockItem(self, itemID, userErrorName = '', userErrorDict = {}, raiseIfLocked = 0):
        try:
            self.lockedItemsSemaphore.acquire()
            self.LogInfo('TryLockItem', itemID)
            bIsLocked, xlockTime, xuserErrorName, xuserErrorDict, co_name, co_filename, co_lineno, thread = self.IsItemLocked_NoLock(itemID)
            if bIsLocked:
                lockTime, userErrorName, userErrorDict = xlockTime, xuserErrorName, xuserErrorDict
            else:
                co_name = None
                co_filname = None
                co_lineno = None
                if self.trace:
                    frames = traceback.extract_stack(limit=2)
                    frame = frames[1]
                    if frame[0].endswith('service.py'):
                        frame = frames[0]
                    co_name = frame[2]
                    co_filname = frame[0]
                    co_lineno = frame[1]
                    self.LogInfo('TryLockItem called by ', co_name, ' ', co_filename, '(', co_lineno, ')')
                now = blue.os.GetWallclockTime()
                self.lockedItems[itemID] = (now,
                 userErrorName,
                 userErrorDict,
                 co_name,
                 co_filname,
                 co_lineno,
                 stackless.getcurrent())
                self.LogInfo('Locked Item', itemID)
                sm.ScatterEvent('OnItemLocked', itemID)
                return 1
        finally:
            self.lockedItemsSemaphore.release()

        if bIsLocked and raiseIfLocked:
            self.RaiseLockError(itemID, lockTime, userErrorName, userErrorDict, co_name, co_filename, co_lineno)
        return bIsLocked

    def RaiseLockError(self, itemID, lockTime, userErrorName, userErrorDict, co_name, co_filename, co_lineno):
        if len(userErrorName) == 0:
            userErrorName = 'ItemIsLocked'
            userErrorDict = {'reason': localization.GetByLabel('UI/Generic/NoReasonWasSpecified'),
             'lockTime': FmtDate(lockTime)}
        if userErrorDict == type({}):
            userErrorDict['lockTime'] = lockTime
        if not self.trace:
            raise UserError(userErrorName, userErrorDict)
        message = cfg.GetMessage(userErrorName, userErrorDict)
        msgDict = {}
        if co_name is None:
            co_name = localization.GetByLabel('UI/Generic/Unknown')
        if co_filename is None:
            co_filename = localization.GetByLabel('UI/Generic/Unknown')
        if co_lineno is None:
            co_lineno = localization.GetByLabel('UI/Generic/Unknown')
        msgDict['title'] = message.title
        msgDict['text'] = message.text
        msgDict['itemID'] = itemID
        msgDict['co_name'] = co_name
        msgDict['co_filename'] = co_filename
        msgDict['co_lineno'] = co_lineno
        msgDict['lockTime'] = lockTime
        raise UserError('AdminReportItemLocked', msgDict)

    def UnlockItem(self, itemID):
        try:
            self.lockedItemsSemaphore.acquire()
            self.UnlockItem_NoLock(itemID)
        finally:
            self.lockedItemsSemaphore.release()

    def UnlockItem_NoLock(self, itemID):
        self.LogInfo('UnlockItem_NoLock', itemID)
        if self.lockedItems.has_key(itemID):
            del self.lockedItems[itemID]
            self.LogInfo('Unlocked Item:', itemID)
            sm.ScatterEvent('OnItemUnlocked', itemID)
        else:
            self.LogInfo('UnlockItem_NoLock irrelevant item:', itemID)

    def IsItemLocked(self, itemID, raiseIfLocked = 0):
        try:
            self.lockedItemsSemaphore.acquire()
            bIsLocked, lockTime, userErrorName, userErrorDict, co_name, co_filename, co_lineno, thread = self.IsItemLocked_NoLock(itemID)
        finally:
            self.lockedItemsSemaphore.release()

        if bIsLocked and raiseIfLocked:
            self.RaiseLockError(itemID, lockTime, userErrorName, userErrorDict, co_name, co_filename, co_lineno)
        return bIsLocked

    def IsItemLocked_NoLock(self, itemID):
        if not self.lockedItems.has_key(itemID):
            return (0,
             0,
             '',
             {},
             None,
             None,
             None,
             None)
        lockTime, userErrorName, userErrorDict, co_name, co_filename, co_lineno, thread = self.lockedItems[itemID]
        return (1,
         lockTime,
         userErrorName,
         userErrorDict,
         co_name,
         co_filename,
         co_lineno,
         thread)

    def RemoveInventoryContainer(self, containerItem):
        self.LogInfo('Removing', evetypes.GetName(containerItem.typeID), 'container', containerItem.itemID, 'from cache as ownership has changed.')
        if not self.inventories.has_key((containerItem.itemID, None)):
            self.LogInfo('RemoveInventoryContainer container not found in inventories')
            return
        for itemID, item in self.inventories[containerItem.itemID, None].cachedItems.iteritems():
            if cfg.IsContainer(item):
                self.RemoveInventoryContainer(item)

        del self.inventories[containerItem.itemID, None]

    def GetInventoryMgr(self):
        return self.inventorymgr

    def GetItemHeader(self, force = 0):
        if self.__itemhdr is None or force:
            self.__itemhdr = sm.RemoteSvc('invbroker').GetItemDescriptor()
            self.LogInfo('invCache got remote itemhdr', self.__itemhdr)
        return self.__itemhdr

    def ValidateItemCanBeOpened(self, item):
        if not cfg.IsCargoContainer(item):
            return True
        if self.__invmgr:
            return self.__invmgr.ValidateItemCanBeOpened(item)
        return True

    def ValidateItemListCanBeOpened(self, items):
        cargoContainerItems = []
        for item in items:
            if cfg.IsCargoContainer(item):
                cargoContainerItems.append(item)

        if cargoContainerItems and self.__invmgr:
            return self.__invmgr.ValidateItemListCanBeOpened(cargoContainerItems)
        return []

    def GetItemsInCurrentShip(self, inventoryFlags):
        items = set()
        inventory = self.GetInventoryFromId(session.shipid)
        for inventoryFlag in inventoryFlags:
            for item in inventory.List(inventoryFlag):
                items.add(item.itemID)

        return items

    def _GetShipsInHangarInventory(self, inventory):
        items = set()
        for item in inventory.List(const.flagHangar):
            if idCheckers.IsShip(item.categoryID):
                items.add(item.itemID)

        return items

    def _GetItemsInHangarInventory(self, inventory):
        items = set()
        for item in inventory.List(const.flagHangar):
            if not idCheckers.IsShip(item.categoryID):
                items.add(item.itemID)

        return items

    @RaiseIfInventoryLocationUnavailable(sessionCheck=lambda : bool(session.shipid), locationName='ship')
    def GetItemsInCurrentShipCargo(self):
        inventoryFlags = [const.flagCargo]
        return self.GetItemsInCurrentShip(inventoryFlags)

    @RaiseIfInventoryLocationUnavailable(sessionCheck=lambda : bool(session.stationid), locationName='station')
    def GetItemsInCurrentStationShipHangar(self):
        inventory = self.GetInventory(const.containerHangar)
        return self._GetShipsInHangarInventory(inventory)

    @RaiseIfInventoryLocationUnavailable(sessionCheck=lambda : bool(session.stationid), locationName='station')
    def GetItemsInCurrentStationItemHangar(self):
        inventory = self.GetInventory(const.containerHangar)
        return self._GetItemsInHangarInventory(inventory)

    @RaiseIfInventoryLocationUnavailable(sessionCheck=lambda : bool(session.structureid), locationName='structure')
    def GetItemsInCurrentStructureShipHangar(self):
        inventory = self.GetInventoryFromId(session.structureid)
        return self._GetShipsInHangarInventory(inventory)

    @RaiseIfInventoryLocationUnavailable(sessionCheck=lambda : bool(session.structureid), locationName='structure')
    def GetItemsInCurrentStructureItemHangar(self):
        inventory = self.GetInventoryFromId(session.structureid)
        return self._GetItemsInHangarInventory(inventory)

    def GetInventory(self, containerid, param1 = None):
        if containerid in (const.containerHangar, const.containerCorpMarket) and session.structureid:
            containerid = const.containerStructure
            key = (session.structureid, None)
        else:
            key = (containerid, param1)
        if containerid in (const.containerHangar, const.containerCorpMarket):
            if self.__stationID != 0 and self.__stationID != session.stationid:
                self.InvalidateCache()
            inventoryMgr = self.stationInventoryMgr
            sessionCheckParams = {'stationid': self.__stationID}
        else:
            if self.__invlocID != eve.session.locationid:
                self.InvalidateCache()
            inventoryMgr = self.inventorymgr
            sessionCheckParams = {'locationid': self.__invlocID}
        if containerid in SPECIAL_CONTAINER_IDS:
            if containerid == const.containerGlobal:
                if self.containerGlobal is None:
                    inv = Moniker('charMgr', (session.charid, containerid))
                    self.containerGlobal = inv5MinCacheContainer(inv)
                return self.containerGlobal
            inv = self.inventorymgr.GetInventory(containerid, param1)
            inv.SetSessionCheck({'locationid': self.__invlocID})
            return inv
        if not self.inventories.has_key(key):
            inv = inventoryMgr.GetInventory(containerid, param1)
            inv.SetSessionCheck(sessionCheckParams)
            self.inventories[key] = invCacheContainer(inv, key, self)
        return self.inventories[key]

    def GetInventoryFromId(self, itemid, passive = 0, locationID = None):
        if itemid is None:
            log.LogTraceback('Thou shalt not send None in as itemid to GetInventoryFromId')
            raise IndexError
        if locationID is None:
            locationID = session.locationid
        if locationID == session.locationid:
            if locationID != self.__invlocID:
                self.InvalidateCache()
            inventoryMgr = self.inventorymgr
            sessionCheckParams = {'locationid': self.__invlocID}
        elif locationID == session.structureid:
            if session.solarsystemid != self.__invlocID:
                self.InvalidateCache()
            inventoryMgr = self.inventorymgr
            sessionCheckParams = {'locationid': self.__invlocID,
             'structureid': session.structureid}
        elif locationID == session.stationid:
            if locationID != self.__stationID:
                self.InvalidateCache()
            inventoryMgr = self.stationInventoryMgr
            sessionCheckParams = {'stationid': self.__stationID}
        key = (itemid, None)
        if key in self.inventories:
            return self.inventories[key]
        inv = inventoryMgr.GetInventoryFromId(itemid, passive)
        inv.SetSessionCheck(sessionCheckParams)
        self.inventories[key] = invCacheContainer(inv, key, self)
        return self.inventories[key]

    def IsInventoryPrimedAndListed(self, itemid):
        key = (itemid, None)
        inv = self.inventories.get(key, None)
        if inv is not None and inv.listed:
            return True
        return False

    def InvalidateCache(self):
        self.__invmgr = None
        self.__stationinvmgr = None
        self.containerGlobal = None
        for containerGuard in self.inventories.itervalues():
            containerGuard.moniker = None

        self.inventories = {}
        self.lockedItems = {}
        lockKeys = self.locks.keys()
        for lockKey in lockKeys:
            uthread.UnLock(self, lockKey)

        self.locks = {}

    def ValidateLocationCacheForItems(self, items):
        invalidItemIDs = self.ValidateItemListCanBeOpened(items)
        for itemID in invalidItemIDs:
            self.InvalidateLocationCache(itemID)

    def InvalidateLocationCache(self, itemID):
        key = itemID if isinstance(itemID, tuple) else (itemID, None)
        try:
            self.inventories[key].moniker = None
            del self.inventories[key]
            self.LogInfo('Invalidated location cache for ', key)
        except KeyError:
            pass

    def InvalidateCorpCache(self):
        keysToInvalidate = self.GetOfficeKeys() | self.GetCorpKeys()
        for key in keysToInvalidate:
            if key in self.inventories:
                del self.inventories[key]

        if keysToInvalidate:
            self.LogInfo('Removed inventory for corp hangar')

    def OnInvalidateCacheForLocations(self, locationIDs):
        for locID in locationIDs:
            self.InvalidateLocationCache(locID)

    def GetOfficeKeys(self):
        officeItemsKeys = set()
        office = sm.GetService('officeManager').GetCorpOfficeAtLocation()
        if office is None:
            return officeItemsKeys
        officeKey = (office.officeID, None)
        officeItemsKeys.add(officeKey)
        for key in self.inventories.keys():
            item = getattr(self.inventories[key], 'item', None)
            if item:
                locationID = getattr(item, 'locationID', None)
                if locationID and locationID == office.officeID:
                    officeItemsKeys.add(key)

        return officeItemsKeys

    def GetCorpKeys(self):
        corpItemsKeys = set()
        for key in self.inventories.keys():
            item = getattr(self.inventories[key], 'item', None)
            if item:
                ownerID = getattr(item, 'ownerID', None)
                if ownerID and ownerID == session.corpid:
                    corpItemsKeys.add(key)

        return corpItemsKeys

    def OnCapacityChange(self, moduleID):
        key = (moduleID, None)
        if self.inventories.has_key(key):
            self.inventories[key].capacityByFlag = {}
            self.inventories[key].capacityByLocation = None

    def GetStationIDOfItem(self, item):
        stationID = self.GetStationIDandOfficeIDOfItem(item)[0]
        if stationID:
            return stationID
        if item.flagID in const.flagCorpSAGs:
            if idCheckers.IsStation(item.locationID) or idCheckers.IsSolarSystem(item.locationID):
                return None
            if item.locationID in (session.locationid, session.structureid):
                return item.locationID
            invCache = sm.GetService('invCache')
            if self.IsInventoryPrimedAndListed(item.locationID):
                locationItem = invCache.GetInventoryFromId(item.locationID).GetItem()
                while locationItem and locationItem.itemID not in (session.stationid, session.structureid) and locationItem.locationID > const.minStation:
                    if locationItem.typeID == const.typeAssetSafetyWrap:
                        return locationItem.locationID
                    locationItem = invCache.GetInventoryFromId(locationItem.locationID).GetItem()

    def GetStationIDandOfficeIDOfItem(self, item):
        if idCheckers.IsStation(item.locationID) or item.locationID == session.structureid:
            return (item.locationID, None)
        if item.flagID in const.flagCorpSAGs:
            for office in sm.GetService('officeManager').GetMyCorporationsOffices():
                if item.locationID == office.officeID:
                    return (office.stationID, office.officeID)

        if sm.GetService('structureDirectory').GetStructureInfo(item.locationID):
            return (item.locationID, item.locationID)
        return (None, None)

    def FetchItem(self, itemID, fromLocationID):
        if idCheckers.IsStation(fromLocationID):
            inv = self.inventories.get((const.containerHangar, None), None)
        else:
            inv = self.inventories.get((fromLocationID, None), None)
        if inv is None:
            self.LogInfo('invCache::FetchItem - Could not find inventory', itemID, fromLocationID)
            return
        return inv.cachedItems.get(itemID, None)

    def GetParentItemFromItemID(self, itemID):
        for invCacheCont in self.inventories.values():
            if itemID in invCacheCont.cachedItems:
                return invCacheCont.cachedItems[itemID]

    def OnDogmaAttributeChanged(self, shipID, itemID, attributeID, value):
        if attributeID in CAPACITY_ATTRIBUTES:
            sm.ScatterEvent('OnCapacityChange', itemID)

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        if shipID:
            sm.ScatterEvent('OnCapacityChange', shipID)
        key = (oldShipID, None)
        if key in self.inventories:
            del self.inventories[key]

    def AcceptPossibleRemovalTax(self, items):
        if not items:
            return True
        assetWrapItem = None
        containerID = items[0].locationID
        parentLocationItem = self.GetParentItemFromItemID(containerID)
        while parentLocationItem is not None and assetWrapItem is None:
            if parentLocationItem.typeID == const.typeAssetSafetyWrap:
                assetWrapItem = parentLocationItem
            parentLocationItem = self.GetParentItemFromItemID(parentLocationItem.locationID)

        if assetWrapItem is None:
            return True
        assetInv = self.GetInventoryFromId(assetWrapItem.itemID)
        iskToPay = assetInv.GetPriceForItems([ item.itemID for item in items ])
        if iskToPay == 0:
            return True
        response = eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/Common/Confirm'),
         'question': localization.GetByLabel('UI/Inventory/AssetSafetyRecoveryConfirmation', tax=iskToPay)}, uiconst.YESNO)
        if response == uiconst.ID_YES:
            return True
        return False

    def StripFitting(self, itemID):
        inventory = self.GetInventoryFromId(itemID)
        fittedItems = ActiveShipController().GetModules()
        fittedTypes = {item.typeID for item in fittedItems}
        typesThatCannotBeUnfitted = {typeID for typeID in fittedTypes if not can_be_unfitted(typeID)}
        if typesThatCannotBeUnfitted:
            raise ItemCannotBeUnfitted(typesThatCannotBeUnfitted)
        ret = inventory.StripFitting()
        sm.ScatterEvent('OnFittingStripped', itemID)
        return ret


class inv5MinCacheContainer():
    __update_on_reload__ = 1

    def __init__(self, moniker):
        self.moniker = moniker
        self.listed = None
        self.cachedItems = {}
        self.listTime = None
        self.listedAll = None
        self.cachedItemsAll = {}
        self.cachedStationItems = {}
        self.cachedStations = (0, [])
        self.crits = {}
        self.deleteCacheThread = None

    def __EnterCriticalSection(self, k, v = None):
        if (k, v) not in self.crits:
            self.crits[k, v] = uthread.CriticalSection((k, v))
        self.crits[k, v].acquire()

    def __LeaveCriticalSection(self, k, v = None):
        self.crits[k, v].release()
        if (k, v) in self.crits and self.crits[k, v].IsCool():
            del self.crits[k, v]

    def __str__(self):
        try:
            return 'Global inventory for %s:%d' % (cfg.eveowners.Get(eve.session.charid).name, eve.session.charid)
        except StandardError:
            sys.exc_clear()
            return 'inventory.Global instance - failed to __str__ self'

    def ListStations(self):
        self.__EnterCriticalSection('ListStations')
        try:
            now = blue.os.GetWallclockTime()
            if self.cachedStations[0] + const.MIN * 5 < now:
                self.cachedStations = (now, self.moniker.ListStations())
            return self.cachedStations[1]
        finally:
            self.__LeaveCriticalSection('ListStations')

    def ListStationItems(self, stationID):
        try:
            self.__EnterCriticalSection('ListStationItems', stationID)
            now = blue.os.GetWallclockTime()
            if self.cachedStationItems.has_key(stationID):
                if self.cachedStationItems[stationID][0] + const.MIN * 5 < now:
                    del self.cachedStationItems[stationID]
            if not self.cachedStationItems.has_key(stationID):
                self.cachedStationItems[stationID] = (now, self.moniker.ListStationItems(stationID))
            return self.cachedStationItems[stationID][1]
        finally:
            self.__LeaveCriticalSection('ListStationItems', stationID)

    def InvalidateStationItemsCache(self, stationID):
        if self.cachedStationItems.has_key(stationID):
            del self.cachedStationItems[stationID]

    def List(self):
        now = blue.os.GetWallclockTime()
        if self.listed is not None:
            if self.listTime + const.MIN * 5 < now:
                self.listed = None
                self.cachedItems = {}
        if self.listed is None:
            self.listTime = now
            if self.moniker is None:
                return []
            realItems = self.moniker.List()
            for realItem in realItems:
                self.cachedItems[realItem.itemID] = realItem

            self.listed = 1
        return self.cachedItems.values()

    def ListIncludingContainers(self):
        if self.listedAll:
            return self.cachedItemsAll.values()
        realItems = self.moniker.ListIncludingContainers()
        for realItem in realItems:
            self.cachedItemsAll[realItem.itemID] = realItem

        self.deleteCacheThread = uthread.new(self._DeleteCachedItemsAll)
        self.deleteCacheThread.context = 'DeleteCahcedItemsAll'
        self.listedAll = 1
        return self.cachedItemsAll.values()

    def GetAssetWorth(self):
        self.moniker.Bind()
        return self.moniker.GetAssetWorth()

    def _DeleteCachedItemsAll(self):
        blue.pyos.synchro.Sleep(const.MIN * 5 / 10000)
        self.listedAll = 0
        self.cachedItemsAll = {}

    def TrashItem(self, stationID, itemID, locationID):
        if self.cachedStationItems.has_key(stationID):
            for item in self.cachedStationItems[stationID][1]:
                if item.itemID == itemID:
                    item.locationID = locationID
                    break


class invCacheContainer():
    __update_on_reload__ = 1

    def __init__(self, moniker, key, broker):
        self.broker = broker
        self.key = key
        self.moniker = PasswordHandlerObjectWrapper(moniker)
        self.cachedItems = {}
        self.listed = set()
        self._itemID = None
        self._typeID = None
        self._item = None
        self.capacityByFlag = {}
        self.capacityByLocation = None
        containerIDs = (const.containerHangar,
         const.containerWallet,
         const.containerStationCharacters,
         const.containerGlobal,
         const.containerSolarSystem,
         const.containerRecycler,
         const.containerCharacter,
         const.containerCorpMarket)
        if key[0] not in containerIDs:
            self._itemID = key[0]

    @property
    def itemID(self):
        if self._itemID is None:
            try:
                self._SetItemData()
            except AttributeError as error:
                raise RuntimeError, error, sys.exc_info()[2]

        return self._itemID

    @property
    def typeID(self):
        if self._typeID is None:
            try:
                self._SetItemData()
            except AttributeError as error:
                raise RuntimeError, error, sys.exc_info()[2]

        return self._typeID

    @property
    def item(self):
        if self._item is None:
            try:
                self._SetItemData()
            except AttributeError as error:
                raise RuntimeError, error, sys.exc_info()[2]

        return self._item

    def _SetItemData(self):
        if None in (self._itemID, self._typeID, self._item):
            session.WaitUntilSafe()
            if self._item is None:
                self._item = self.moniker.GetSelfInvItem()
                self._itemID = self._item.itemID
                self._typeID = self._item.typeID

    def __str__(self):
        try:
            return 'invCacheContainer %d for %s' % (self.itemID, self.key)
        except StandardError:
            sys.exc_clear()
            return 'invCacheContainer instance - failed to __str__ self'

    def LogInfo(self, *k, **v):
        self.broker.LogInfo('invCacheContainer', self.key, ':', *k, **v)

    def LogWarn(self, *k, **v):
        self.broker.LogWarn('invCacheContainer', self.key, ':', *k, **v)

    def LogError(self, *k, **v):
        self.broker.LogError('invCacheContainer', self.key, ':', *k, **v)

    def Add(self, itemID, sourceID, **kw):
        activeShipID = eveCfg.GetActiveShip()
        if itemID == activeShipID:
            raise UserError('CanNotPlaceActiveShipInAnotherHangar')
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if self.itemID == activeShipID:
            flagID = kw.get('flag', None)
            if flagID is not None and IsFittingFlag(flagID) or flagID == const.flagAutoFit:
                dogmaLocation.CheckCanFit(self.itemID, itemID, flagID, sourceID)
        if 'qty' in kw and kw['qty'] == 0:
            self.LogError('Trying to add a stack with 0 quantity to a container. Fix your code.')
            return
        if sm.GetService('lockedItems').IsItemIDLocked(itemID):
            raise UserError('CrpItemIsLocked')
        if itemID == self.itemID:
            raise UserError('CannotPlaceItemInsideItself')
        self.broker.TryLockItem(itemID, 'lockAddItemToContainer', {'containerType': self.typeID}, 1)
        try:
            if type(itemID) is tuple:
                return dogmaLocation.UnloadAmmoToContainer(activeShipID, itemID, self.itemID, kw.get('qty'))
            return self.moniker.Add(itemID, sourceID, **kw)
        finally:
            self.broker.UnlockItem(itemID)

    def MultiAdd(self, itemIDs, sourceID, **kw):
        activeShipID = eveCfg.GetActiveShip()
        if activeShipID in itemIDs:
            raise UserError('CanNotPlaceActiveShipInAnotherHangar')
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if self.itemID == activeShipID:
            flagID = kw.get('flag', None)
            if flagID is not None and IsFittingFlag(flagID) or flagID == const.flagAutoFit:
                for itemID in itemIDs:
                    dogmaLocation.CheckCanFit(self.itemID, itemID, flagID, sourceID)

        lockedItems = set()
        charges = set()
        for itemID in itemIDs:
            if self.itemID is not None and itemID == self.itemID:
                continue
            if sm.GetService('lockedItems').IsItemIDLocked(itemID):
                continue
            if not self.broker.IsItemLocked(itemID):
                if self.broker.TryLockItem(itemID):
                    lockedItems.add(itemID)
                    if type(itemID) is tuple:
                        charges.add(itemID)
                        dogmaLocation.UnloadAmmoToContainer(activeShipID, itemID, self.itemID)

        if not len(lockedItems):
            return
        try:
            nonCharges = lockedItems - charges
            if len(nonCharges) > 0:
                self.moniker.MultiAdd(list(nonCharges), sourceID, **kw)
        finally:
            for itemID in lockedItems:
                self.broker.UnlockItem(itemID)

        return True

    def StackAll(self, *args, **kw):
        if idCheckers.IsFakeItem(self.itemID):
            self.LogInfo("StackAll called on a fake location. Why bother.. I won't do it")
            return
        itemIDsToLock = []
        types = set()
        hasSomethingToStack = False
        for each in self.List(*args, **kw):
            if self.itemID is not None and each.itemID == self.itemID:
                continue
            if each.quantity < 0:
                continue
            if sm.GetService('lockedItems').IsItemLocked(each):
                continue
            if not hasSomethingToStack:
                if each.quantity != const.maxInt:
                    if each.typeID in types:
                        hasSomethingToStack = True
                    types.add(each.typeID)
            if not self.broker.IsItemLocked(each.itemID):
                if self.broker.TryLockItem(each.itemID):
                    itemIDsToLock.append(each.itemID)

        if not len(itemIDsToLock):
            return
        try:
            if hasSomethingToStack:
                return self.moniker.StackAll(*args, **kw)
        finally:
            for itemID in itemIDsToLock:
                self.broker.UnlockItem(itemID)

    def MultiMerge(self, ops, sourceContainerID):
        itemIDsToLock = []
        for i, (sourceid, destid, qty) in enumerate(ops):
            if self.itemID is not None and sourceid == self.itemID:
                continue
            if sm.GetService('lockedItems').IsItemIDLocked(sourceid):
                continue
            if not self.broker.IsItemLocked(sourceid):
                if self.broker.TryLockItem(sourceid):
                    itemIDsToLock.append(sourceid)

        if not len(itemIDsToLock):
            return
        try:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            activeShipID = eveCfg.GetActiveShip()
            for sourceid, destid, qty in copy.copy(ops):
                if type(sourceid) is tuple:
                    dogmaLocation.UnloadAmmoToContainer(activeShipID, sourceid, destid, qty)
                    ops.remove((sourceid, destid, qty))

            self.LogInfo('MultiMerge - merging ops = ', len(ops))
            if len(ops) > 0:
                self.moniker.MultiMerge(ops, sourceContainerID)
        finally:
            for itemID in itemIDsToLock:
                self.broker.UnlockItem(itemID)

    def List(self, *args, **kw):
        flag = None
        if args is not None and len(args):
            flag = args[0]
        elif kw is not None and 'flag' in kw:
            flag = kw['flag']
        if flag not in self.listed:
            realItems = self.moniker.List(flag=flag)
            for realItem in realItems:
                self.cachedItems[realItem.itemID] = realItem
                self.listed.add(realItem.flagID)

            godmaSM = sm.GetService('godma').GetStateManager()
            if godmaSM.IsLocationLoaded(self.itemID):
                godmaItem = godmaSM.GetItem(self.itemID)
                if godmaItem is not None:
                    for subloc in godmaItem.sublocations:
                        self.cachedItems[subloc.itemID] = subloc.invItem

            self.listed.add(flag)
            self.LogInfo('We now have listed', self.listed, 'in', self.key)
        res = CRowset(self.broker.GetItemHeader(), [])
        for itemID in self.cachedItems.iterkeys():
            item = self.cachedItems[itemID]
            if flag is not None:
                if item.flagID != flag:
                    continue
            if 'typeID' in kw and item.typeID != kw['typeID']:
                continue
            if len(item) != len(res.header):
                self.LogError('Invalid Item', item)
                continue
            res.append(item)

        return res

    def ListByFlags(self, flagIDs, **kw):
        res = CRowset(self.broker.GetItemHeader(), [])
        if not flagIDs:
            return res
        uncachedFlags = [ flagID for flagID in flagIDs if flagID not in self.listed ]
        if uncachedFlags:
            uncachedRealItems = self.moniker.ListByFlags(flags=uncachedFlags)
            for realItem in uncachedRealItems:
                self.cachedItems[realItem.itemID] = realItem
                self.listed.add(realItem.flagID)

            godmaSM = sm.GetService('godma').GetStateManager()
            if godmaSM.IsLocationLoaded(self.itemID):
                godmaItem = godmaSM.GetItem(self.itemID)
                if godmaItem is not None:
                    for subloc in godmaItem.sublocations:
                        self.cachedItems[subloc.itemID] = subloc.invItem

            for flagID in uncachedFlags:
                self.listed.add(flagID)

            self.LogInfo('We now have listed', self.listed, 'in', self.key)
        for itemID in self.cachedItems.iterkeys():
            item = self.cachedItems[itemID]
            if item.flagID not in flagIDs:
                continue
            if 'typeID' in kw and item.typeID != kw['typeID']:
                continue
            if len(item) != len(res.header):
                self.LogError('Invalid Item', item)
                continue
            res.append(item)

        return res

    def ListHangar(self):
        return self.List(const.flagHangar)

    def ListCargo(self):
        return self.List(const.flagCargo)

    def ListDroneBay(self):
        return self.List(const.flagDroneBay)

    def ListHardware(self):
        return [ i for i in self.List() if const.flagSlotFirst <= i.flagID <= const.flagSlotLast ]

    def ListHardwareModules(self):
        return [ i for i in self.List() if IsFittable(i.categoryID) and IsFittingFlag(i.flagID) ]

    @staticmethod
    def IsFlagCapacityLocationWide(item):
        if item.groupID in (const.groupCorporateHangarArray, const.groupAssemblyArray, const.groupMobileLaboratory):
            return True
        return False

    def GetCapacity(self, flag = None):
        if self.item.groupID in (const.groupStation,) or self.item.typeID in (const.typeOffice,):
            capacity = Row(['capacity', 'used'], [9000000000000000.0, 0.0])
            return capacity
        if flag == flagFrigateEscapeBay:
            return self.GetFrigateEscapeBayCapacity(flag)
        if flag is None:
            flags = {i.flagID for i in self.List() if i.flagID is not None}
            if flags:
                capacity = Row(['capacity', 'used'], [0, 0.0])
                for flag in flags:
                    cap = self.GetCapacity(flag)
                    if capacity.capacity == 0:
                        capacity.capacity = cap.capacity
                    capacity.used += cap.used

                return capacity
        flag = flag or const.flagNone
        itemID = self.itemID
        if itemID is not None:
            godmaItem = sm.GetService('godma').GetItem(itemID)
            if godmaItem is not None and godmaItem.statemanager.invByID.has_key(godmaItem.itemID):
                if godmaItem.statemanager.invByID[godmaItem.itemID] != self:
                    self.LogWarn('FIXUP: godma is using an old thrown away invCacheContainer')
                    godmaItem.statemanager.invByID[godmaItem.itemID] = self
                capacity = godmaItem.GetCapacity(flag)
                return capacity
        capacityAttributeID = None
        if flag == const.flagDroneBay:
            capacityAttributeID = const.attributeDroneCapacity
        elif flag in inventoryFlagsCommon.inventoryFlagData and flag != const.flagCargo:
            capacityAttributeID = inventoryFlagsCommon.inventoryFlagData[flag]['attribute']
        elif self.item.categoryID == const.categoryShip:
            if flag == const.flagShipHangar:
                capacityAttributeID = const.attributeShipMaintenanceBayCapacity
            elif flag == const.flagFleetHangar:
                capacityAttributeID = const.attributeFleetHangarCapacity
        elif flag == const.flagSecondaryStorage:
            capacityAttributeID = const.attributeCapacitySecondary
        elif self.item.groupID == const.groupSilo:
            capacityAttributeID = const.attributeCapacity
        typeID = self.typeID
        dogmaIM = sm.GetService('clientDogmaIM')
        if capacityAttributeID is not None:
            actualCapacity = dogmaIM.GetCapacityForItem(itemID, capacityAttributeID)
            if actualCapacity is None:
                attribs = [ x for x in dogma.data.get_type_attributes(typeID) if x.attributeID == capacityAttributeID ]
                if self.item.groupID == const.groupSilo and self.item.categoryID == const.categoryStarbase:
                    actualCapacity = self.GetSiloCapacityByItemID(itemID)
                if actualCapacity is None and len(attribs):
                    actualCapacity = attribs[0].value
                if actualCapacity is None:
                    actualCapacity = dogma.data.get_attribute_default_value(capacityAttributeID)
        else:
            actualCapacity = None
            if flag == const.flagCargo:
                actualCapacity = dogmaIM.GetCapacityForItem(itemID, const.attributeCapacity)
            if actualCapacity is None:
                actualCapacity = evetypes.GetCapacity(typeID)
        used = 0.0
        isCustomsOffice = evetypes.GetGroupID(typeID) == const.groupPlanetaryCustomsOffices
        for each in self.List(flag):
            if isCustomsOffice and flag == const.flagHangar and each.ownerID != session.charid:
                continue
            if each.flagID == flag:
                used = used + GetItemVolume(each)

        if typeID == const.typePlasticWrap:
            actualCapacity = used
        if self.item.groupID == const.groupNpcIndustrialCommand and self.item.ownerID in RW_CORPORATIONS:
            haulerCapacity = sm.GetService('rwService').get_hauler_capacity(itemID)
            if haulerCapacity is not None:
                actualCapacity = haulerCapacity
        capacity = Row(['capacity', 'used'], [actualCapacity, used])
        self.capacityByLocation = capacity
        return capacity

    def GetFrigateEscapeBayCapacity(self, flag):
        used = 0.0
        for each in self.List(flag):
            used = used + GetItemVolume(each)

        if used:
            used = 1.0
        capacity = Row(['capacity', 'used'], [1.0, used])
        return capacity

    @Memoize(1)
    def GetSiloCapacityByItemID(self, itemID):
        return Moniker('posMgr', eve.session.solarsystemid).GetSiloCapacityByItemID(itemID)

    def GetItem(self, force = False):
        if force is True:
            self._itemID = self._typeID = self._item = None
        return self.item

    def OnItemChange(self, item, change, location):
        self._ProcessItemChange(item, change)
        sm.ScatterEvent('OnItemChangeProcessed', item, change)

    def _ProcessItemChange(self, item, change):
        oldItem = blue.DBRow(item)
        for k, v in change.iteritems():
            if k in (const.ixStackSize, const.ixSingleton):
                k = const.ixQuantity
            oldItem[k] = v

        location = self.key[0]
        owner = self.key[1]
        shouldCache = False
        if item.flagID in self.listed or item.ownerID == session.charid:
            shouldCache = True
        elif item.locationID == session.shipid:
            shouldCache = True
        elif item.ownerID == session.corpid:
            role = 0
            if item.flagID in const.corpHangarQueryRolesByFlag:
                role = const.corpHangarQueryRolesByFlag[item.flagID]
            elif self.item.groupID in const.containerGroupIDs:
                try:
                    myItem = self.broker.GetInventoryFromId(item.locationID).GetItem()
                    role = const.corpHangarQueryRolesByFlag[myItem.flagID]
                except KeyError:
                    pass

            if session.corprole & role:
                shouldCache = True
        if location == const.containerHangar:
            if owner is not None and owner not in [item.ownerID, oldItem.ownerID]:
                return
            if not session.stationid:
                return
            if location == const.containerHangar and owner is not None and item.ownerID == owner and const.ixOwnerID in change:
                self.cachedItems[item.itemID] = item
                return
            if item.locationID != session.stationid or item.stacksize == 0 or item.ownerID != eve.session.charid:
                if self.capacityByFlag.has_key(oldItem.flagID):
                    del self.capacityByFlag[oldItem.flagID]
                elif self.item and self.IsFlagCapacityLocationWide(self.item):
                    self.capacityByLocation = None
                if self.cachedItems.has_key(item.itemID):
                    del self.cachedItems[item.itemID]
                return
            if item.ownerID == eve.session.charid:
                if self.capacityByFlag.has_key(oldItem.flagID):
                    del self.capacityByFlag[oldItem.flagID]
                elif self.item and self.IsFlagCapacityLocationWide(self.item):
                    self.capacityByLocation = None
                self.cachedItems[item.itemID] = item
        elif location == const.containerCorpMarket:
            if owner is not None and owner not in [item.ownerID, oldItem.ownerID]:
                return
            if not session.stationid:
                return
            if item.locationID != session.stationid or item.stacksize == 0 or item.ownerID != eve.session.corpid:
                if self.capacityByFlag.has_key(oldItem.flagID):
                    del self.capacityByFlag[oldItem.flagID]
                elif self.item and self.IsFlagCapacityLocationWide(self.item):
                    self.capacityByLocation = None
                if self.cachedItems.has_key(item.itemID):
                    del self.cachedItems[item.itemID]
                return
            if item.ownerID == eve.session.corpid:
                if self.capacityByFlag.has_key(oldItem.flagID):
                    del self.capacityByFlag[oldItem.flagID]
                elif self.item and self.IsFlagCapacityLocationWide(self.item):
                    self.capacityByLocation = None
                if oldItem.locationID != session.stationid and item.locationID == session.stationid:
                    if self.cachedItems.has_key(item.itemID):
                        del self.cachedItems[item.itemID]
                    self.cachedItems[item.itemID] = item
                else:
                    if self.cachedItems.has_key(item.itemID):
                        del self.cachedItems[item.itemID]
                    self.cachedItems[item.itemID] = item
        elif item.locationID != location or item.stacksize == 0:
            if self.cachedItems.has_key(item.itemID):
                del self.cachedItems[item.itemID]
            if self.capacityByFlag.has_key(oldItem.flagID):
                del self.capacityByFlag[oldItem.flagID]
            elif self.item and self.IsFlagCapacityLocationWide(self.item):
                self.capacityByLocation = None
        elif oldItem.locationID != location and item.locationID == location:
            if self.cachedItems.has_key(item.itemID):
                del self.cachedItems[item.itemID]
            if shouldCache:
                self.cachedItems[item.itemID] = item
            if self.capacityByFlag.has_key(item.flagID):
                del self.capacityByFlag[item.flagID]
            elif self.item and self.IsFlagCapacityLocationWide(self.item):
                self.capacityByLocation = None
        else:
            if self.cachedItems.has_key(item.itemID):
                del self.cachedItems[item.itemID]
            if shouldCache:
                self.cachedItems[item.itemID] = item
            if self.capacityByFlag.has_key(item.flagID):
                del self.capacityByFlag[item.flagID]
            elif self.item and self.IsFlagCapacityLocationWide(self.item):
                self.capacityByLocation = None
            if change.has_key(const.ixFlag):
                if self.capacityByFlag.has_key(oldItem.flagID):
                    del self.capacityByFlag[oldItem.flagID]
                elif self.item and self.IsFlagCapacityLocationWide(self.item):
                    self.capacityByLocation = None

    def __getattr__(self, method):
        if method in self.__dict__:
            return self.__dict__[method]
        if method.startswith('__'):
            raise AttributeError(method)
        if not hasattr(self.moniker, method):
            raise AttributeError(method)
        return FastInvCallWrapper(self.moniker, method)


class PasswordHandlerCallWrapper():

    def __init__(self, object, method):
        self.__method__ = method
        self.__callable__ = object

    def __call__(self, *args, **keywords):
        try:
            return apply(getattr(self.__callable__, self.__method__), args, keywords)
        except UserError as what:
            if what.args[0] == 'PasswordProtectedCacheInvalid':
                invCache = sm.GetService('invCache')
                invCache.InvalidateLocationCache(args[1])
                raise UserError('SCGeneralPasswordRequired')
            else:
                if what.args[0] in ('SCGeneralPasswordRequired', 'SCConfigPasswordRequired') and self.__method__ != 'SetPassword':
                    if what.args[0] == 'SCGeneralPasswordRequired':
                        which = const.SCCPasswordTypeGeneral
                        caption = localization.GetByLabel('UI/Inventory/ItemActions/AccessPasswordRequiredCaption')
                        label = localization.GetByLabel('UI/Inventory/ItemActions/PleaseEnterAccessPassword')
                    else:
                        which = const.SCCPasswordTypeConfig
                        caption = localization.GetByLabel('UI/Inventory/ItemActions/ConfigurationPasswordRequiredCaption')
                        label = localization.GetByLabel('UI/Inventory/ItemActions/PleaseEnterConfigurationPassword')
                    passw = utilWindows.NamePopup(caption=caption, label=label, setvalue='', maxLength=16, passwordChar='*')
                    if passw is None:
                        raise
                    sys.exc_clear()
                    self.__callable__.EnterPassword(which, passw)
                    return self.__call__(*args, **keywords)
                raise
        finally:
            self.__dict__.clear()


class PasswordHandlerObjectWrapper():

    def __init__(self, object):
        self.__object = object

    def __getattr__(self, attributeName):
        if attributeName.startswith('__'):
            raise AttributeError(attributeName)
        if not hasattr(self.__object, attributeName):
            raise AttributeError(attributeName)
        return PasswordHandlerCallWrapper(self.__object, attributeName)


class FastInvCallWrapper():

    def __init__(self, object, method):
        self.__method__ = method
        self.__callable__ = object

    def __call__(self, *args, **keywords):
        try:
            return apply(getattr(self.__callable__, self.__method__), args, keywords)
        finally:
            self.__dict__.clear()
