#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\items\locationDogmaItem.py
from baseDogmaItem import BaseDogmaItem
from dogma.const import attributeMaxGroupOnline, effectOnline
from eveexceptions import UserError
from eveexceptions.const import UE_GROUPID, UE_TYPEID
from utillib import strx
import weakref
from dogma import dogmaLogging as log
import sys
import inventorycommon.const as invconst
from ccpProfile import TimedFunction

class LocationDogmaItem(BaseDogmaItem):

    @TimedFunction('LocationDogmaItem::__init__')
    def __init__(self, dogmaLocation, item, eveCfg, clientIDFunc):
        BaseDogmaItem.__init__(self, dogmaLocation, item, eveCfg, clientIDFunc)
        self.fittedItems = {}
        self.subLocations = {}

    def Unload(self):
        BaseDogmaItem.Unload(self)
        self.dogmaLocation.LogInfo('LocationDogmaItem unloading subLocations')
        for itemKey in self.subLocations.values():
            self.dogmaLocation.UnloadItem(itemKey)

        if self in self.subLocations:
            self.subLocations.remove(self)
        self.dogmaLocation.LogInfo('LocationDogmaItem unloading fittedItems')
        for itemKey in self.fittedItems.keys():
            self.dogmaLocation.UnloadItem(itemKey)

        if self.itemID in self.fittedItems:
            del self.fittedItems[self.itemID]
        if self.itemID in self.dogmaLocation.moduleListsByShipGroup:
            del self.dogmaLocation.moduleListsByShipGroup[self.itemID]
        if self.itemID in self.dogmaLocation.moduleListsByShipType:
            del self.dogmaLocation.moduleListsByShipType[self.itemID]

    def OnItemLoaded(self):
        self.dogmaLocation.LoadItemsInLocation(self.itemID)
        self.dogmaLocation.LoadSublocations(self.itemID)
        BaseDogmaItem.OnItemLoaded(self)

    def PostLoadAction(self):
        super(LocationDogmaItem, self).PostLoadAction()
        self.dogmaLocation.CheckPowerCpuRequirementForOnlineModules(self.itemID)
        self._EnforceMaxGroupOnline()

    def ValidFittingFlag(self, flagID):
        if invconst.flagLoSlot0 <= flagID <= invconst.flagHiSlot7:
            return True
        return False

    def SetSubLocation(self, itemKey):
        flagID = itemKey[1]
        if flagID in self.subLocations:
            log.LogTraceback('SetSubLocation used for subloc with flag %s' % strx(self.subLocations[flagID]))
        self.subLocations[flagID] = itemKey

    def RemoveSubLocation(self, itemKey):
        flagID = itemKey[1]
        subLocation = self.subLocations.get(flagID, None)
        if subLocation is not None:
            if subLocation != itemKey:
                log.LogTraceback('RemoveSubLocation used for subloc with occupied flag %s' % strx((itemKey, subLocation)))
            del self.subLocations[flagID]

    def RegisterFittedItem(self, dogmaItem, flagID):
        if self.ValidFittingFlag(flagID) or dogmaItem.itemID == self.itemID or flagID == invconst.flagPilot:
            self.fittedItems[dogmaItem.itemID] = weakref.proxy(dogmaItem)
            self.dogmaLocation.moduleListsByShipGroup[self.itemID][dogmaItem.groupID].add(dogmaItem.itemID)
            self.dogmaLocation.moduleListsByShipType[self.itemID][dogmaItem.typeID].add(dogmaItem.itemID)

    def UnregisterFittedItem(self, dogmaItem):
        groupID = dogmaItem.groupID
        typeID = dogmaItem.typeID
        itemID = dogmaItem.itemID
        try:
            self.dogmaLocation.moduleListsByShipGroup[self.itemID][groupID].remove(itemID)
        except KeyError:
            self.dogmaLocation.LogError("UnregisterFittedItem::Tried to remove item from mlsg but group wasn't there", strx(dogmaItem))
            sys.exc_clear()
        except IndexError:
            self.dogmaLocation.LogError("UnregisterFittedItem::Tried to remove item from mlsg but it wasn't there", strx(dogmaItem))
            sys.exc_clear()

        try:
            self.dogmaLocation.moduleListsByShipType[self.itemID][typeID].remove(itemID)
        except KeyError:
            self.dogmaLocation.LogError("UnregisterFittedItem::Tried to remove item from mlsg but type wasn't there", strx(dogmaItem))
            sys.exc_clear()
        except IndexError:
            self.dogmaLocation.LogError("UnregisterFittedItem::Tried to remove item from mlsg but it wasn't there", strx(dogmaItem))
            sys.exc_clear()

        try:
            del self.fittedItems[dogmaItem.itemID]
        except KeyError:
            self.dogmaLocation.LogError("UnregisterFittedItem::Tried to remove item from fittedItems but it wasn't there", strx(dogmaItem))

    def GetFittedItems(self):
        return self.fittedItems

    def GetPersistables(self):
        ret = BaseDogmaItem.GetPersistables(self)
        ret.update(self.fittedItems.keys())
        return ret

    def _FlushEffects(self):
        stackTraceCount = 0
        for fittedItem in self.fittedItems.itervalues():
            try:
                if fittedItem.itemID == self.itemID:
                    continue
                stackTraceCount += fittedItem.FlushEffects()
            except ReferenceError as e:
                self.dogmaLocation.LogWarn('Failed to _FlushEffects for a fitted dogmaitem that is no longer around - we should have cleaned this up')
                log.LogException(channel='svc.dogmaIM')
                sys.exc_clear()

        stackTraceCount += BaseDogmaItem._FlushEffects(self)
        return stackTraceCount

    def GetCharacterID(self):
        return self.GetPilot()

    def CheckCanOnlineItem(self, itemID):
        dogmaItem = self.dogmaLocation.GetItem(itemID)
        groupID = dogmaItem.groupID
        maxGroupOnline = self._GetLowestMaxGroupOnlineDict().get(groupID, None)
        if maxGroupOnline is not None:
            onlineModuleIDs = self._GetOnlineItemIDsInGroup(groupID)
            try:
                onlineModuleIDs.remove(itemID)
            except ValueError:
                pass

            if len(onlineModuleIDs) >= maxGroupOnline:
                raise UserError('CannotOnlineReachedMaxGroupOnline', {'type': (UE_TYPEID, dogmaItem.typeID),
                 'group': (UE_GROUPID, groupID),
                 'maxGroupOnline': maxGroupOnline})

    def EnforceMaxGroupOnlineForGroup(self, groupID):
        maxGroupOnline = self._GetLowestMaxGroupOnlineDict().get(groupID, None)
        if maxGroupOnline is not None:
            self._OfflineExcessModulesInGroup(groupID, maxGroupOnline)

    def _EnforceMaxGroupOnline(self):
        maxGroupOnlineByGroupID = self._GetLowestMaxGroupOnlineDict()
        for groupID, maxGroupOnline in maxGroupOnlineByGroupID.iteritems():
            self._OfflineExcessModulesInGroup(groupID, maxGroupOnline)

    def _GetLowestMaxGroupOnlineDict(self):
        maxGroupOnlineByGroupID = {}
        fittedItems = self.GetFittedItems()
        for moduleID, moduleDogmaItem in fittedItems.iteritems():
            if not self.dogmaLocation.TypeHasAttribute(moduleDogmaItem.typeID, attributeMaxGroupOnline):
                continue
            maxGroupOnline = int(self.dogmaLocation.GetAttributeValue(moduleID, attributeMaxGroupOnline))
            try:
                currentGroupMinimum = maxGroupOnlineByGroupID[moduleDogmaItem.groupID]
            except KeyError:
                maxGroupOnlineByGroupID[moduleDogmaItem.groupID] = maxGroupOnline
            else:
                maxGroupOnlineByGroupID[moduleDogmaItem.groupID] = min(maxGroupOnline, currentGroupMinimum)

        return maxGroupOnlineByGroupID

    def _OfflineExcessModulesInGroup(self, groupID, maxGroupOnline):
        onlineModuleIDs = self._GetOnlineItemIDsInGroup(groupID)
        if len(onlineModuleIDs) > maxGroupOnline:
            excessModuleIDs = onlineModuleIDs[maxGroupOnline:]
            for moduleID in excessModuleIDs:
                self.dogmaLocation.OfflineModule(moduleID)

    def _GetOnlineItemIDsInGroup(self, groupID):
        onlineItemIDs = []
        for itemID, dogmaItem in self.fittedItems.iteritems():
            if dogmaItem.groupID != groupID:
                continue
            if dogmaItem.IsOnline() and (itemID, effectOnline) not in self.dogmaLocation.deactivatingEffects:
                onlineItemIDs.append(itemID)

        return onlineItemIDs
