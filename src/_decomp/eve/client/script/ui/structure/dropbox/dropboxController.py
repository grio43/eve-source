#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\dropbox\dropboxController.py
from signals import Signal
from eve.common.script.sys.idCheckers import IsDockableStructure
from eveexceptions.const import UE_TYPEIDL
from structures.types import GetAllowedFuelTypeIDs

class DropBoxController(object):
    __notifyevents__ = ['OnItemChange']

    def __init__(self, structureID, shipID):
        self.structureID = structureID
        self.forShipID = shipID
        self.on_items_added = Signal(signalName='on_items_added')
        self.on_items_removed = Signal(signalName='on_items_removed')
        self.on_items_updated = Signal(signalName='on_items_updated')
        self.typeID = sm.GetService('structureDirectory').GetStructureInfo(self.structureID).typeID
        self._SetItemFilter()
        self.itemsToBeTransferred = {}
        sm.RegisterNotify(self)

    def _SetItemFilter(self):
        if self.IsDockableStructure():
            self.itemFilter = lambda x: True
        else:
            allowedTypes = GetAllowedFuelTypeIDs(self.typeID)
            self.itemFilter = lambda x: x.typeID in allowedTypes

    def IsDockableStructure(self):
        return IsDockableStructure(self.typeID)

    def GetNumToBeTransferred(self):
        return len(self.itemsToBeTransferred)

    def IsItemAllowed(self, item):
        return self.itemFilter(item)

    def AddManyItems(self, items):
        if self.forShipID != session.shipid:
            raise RuntimeError("Try to add items to controller you shouldn't have")
        invalidItemIDs = set()
        invalidTypeIDs = set()
        for each in items:
            if each.locationID != self.forShipID:
                invalidItemIDs.add(each.itemID)
            elif each.flagID not in const.cargoHoldsValidForDeliveryService:
                invalidItemIDs.add(each.itemID)
            elif not self.IsItemAllowed(each):
                invalidItemIDs.add(each.itemID)
            if each.itemID in invalidItemIDs:
                invalidTypeIDs.add(each.typeID)
                continue
            self.itemsToBeTransferred[each.itemID] = each

        self.on_items_added({x.itemID for x in items} - invalidItemIDs)
        if invalidItemIDs:
            eve.Message('FailedToAddToDropbox', {'itemList': (UE_TYPEIDL, list(invalidTypeIDs))})

    def GetItem(self, itemID):
        return self.itemsToBeTransferred.get(itemID)

    def GetItems(self):
        return self.itemsToBeTransferred.values()

    def ResetItems(self):
        itemIDs = self.itemsToBeTransferred.keys()
        self.itemsToBeTransferred.clear()
        self.on_items_removed(itemIDs)

    def RemoveItems(self, itemIDs):
        for each in itemIDs:
            self.itemsToBeTransferred.pop(each, None)

        self.on_items_removed(itemIDs)

    def OnItemChange(self, item, change, location):
        itemIDsUpdated = set()
        toRemove = set()
        if item.itemID in self.itemsToBeTransferred:
            if self._ShouldItemBeForcefullyRemoved(item):
                toRemove.add(item.itemID)
            else:
                myItem = self.itemsToBeTransferred[item.itemID]
                if myItem.stacksize != item.stacksize or myItem.quantity != item.quantity:
                    self.itemsToBeTransferred[item.itemID] = item
                    itemIDsUpdated.add(item.itemID)
        if toRemove:
            self.RemoveItems(toRemove)
        self.on_items_updated(itemIDsUpdated)

    def _ShouldItemBeForcefullyRemoved(self, item):
        if item.stacksize == 0 and item.quantity == 0:
            return True
        if item.locationID != self.forShipID:
            return True
        if item.flagID not in const.cargoHoldsValidForDeliveryService:
            return True
        return False

    def GetStructureID(self):
        return self.structureID

    def TransferItems(self):
        allItems = self.itemsToBeTransferred.copy()
        self.ResetItems()
        movedItemIDs = sm.RemoteSvc('structureCargoDelivery').DropOffItems(allItems.keys(), session.shipid, self.structureID)
        itemRecsMoved = [ x for x in allItems.itervalues() if x.itemID in movedItemIDs ]
        if movedItemIDs:
            structureName = cfg.evelocations.Get(self.structureID).name
            if self.IsDockableStructure():
                msg = 'ItemsTransferredtoHangar'
            else:
                msg = 'ItemsTransferredtoFuelBay'
            eve.Message(msg, {'numItems': len(movedItemIDs),
             'structureName': structureName}, modal=False)
        return itemRecsMoved
