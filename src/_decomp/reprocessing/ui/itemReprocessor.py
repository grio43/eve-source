#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\reprocessing\ui\itemReprocessor.py
from eveexceptions import UserError
from collections import defaultdict
from inventorycommon.const import corpDivisionsByFlag

class ItemReprocessor(object):

    def __init__(self, reprocessingSvc, invCache, AskToContinue):
        self.reprocessingSvc = reprocessingSvc
        self.invCache = invCache
        self.AskToContinue = AskToContinue

    def Reprocess(self, items, activeShipID, outputLocationID, outputFlagID):
        itemsByLocationID = defaultdict(list)
        for item in items:
            self._CheckIsRefiningShip(activeShipID, item.itemID)
            itemsByLocationID[item.locationID].append(item)

        reprocessed = []
        for fromLocationID, items in itemsByLocationID.iteritems():
            itemIDs = self._LockItems(items)
            if not itemIDs:
                continue
            try:
                flagID = outputFlagID
                if (outputLocationID, outputFlagID) == (None, None):
                    sampleItem = items[0]
                    outputLocationID = sampleItem.locationID
                    ownerID = sampleItem.ownerID
                    flagID = sampleItem.flagID
                elif outputFlagID in corpDivisionsByFlag:
                    ownerID = session.corpid
                elif outputLocationID in (session.stationid, session.structureid):
                    ownerID = session.charid
                else:
                    ownerID = None
                reprocessed.extend(self._DoReprocess(itemIDs, ownerID, fromLocationID, outputLocationID, flagID))
            finally:
                self._UnlockItems(itemIDs)

        return reprocessed

    def _CheckIsRefiningShip(self, activeShipID, itemID):
        if itemID == activeShipID:
            raise UserError('CannotReprocessActive')

    def _IsInSameLocation(self, locationID, item):
        return locationID == item.locationID

    def _LockItems(self, items):
        itemIDs = []
        for item in items:
            self.invCache.TryLockItem(item.itemID, 'lockReprocessing', {'itemType': item.typeID}, 1)
            itemIDs.append(item.itemID)

        return itemIDs

    def _UnlockItems(self, itemIDs):
        for itemID in itemIDs:
            self.invCache.UnlockItem(itemID)

    def _DoReprocess(self, itemIDs, ownerID, fromLocation, outputLocationID, outputFlagID):
        return self.reprocessingSvc.GetReprocessingSvc().Reprocess(itemIDs, fromLocation, ownerID, outputLocationID, outputFlagID)
