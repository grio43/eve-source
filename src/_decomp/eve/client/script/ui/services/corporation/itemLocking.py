#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\corporation\itemLocking.py
from carbon.common.script.sys.service import Service
from eve.common.lib import appConst as const
from eve.common.script.sys.idCheckers import IsCorporation
from locks import TempLock

class ItemLocking(Service):
    __servicename__ = 'ItemLocking'
    __displayname__ = 'Client side Item Locking Service'
    __guid__ = 'svc.lockedItems'
    __notifyevents__ = ['OnLockedItemChange']

    def __init__(self):
        Service.__init__(self)
        self.lockedItemsByLocationID = {}
        self.locationsWithLockedItems = None
        self.remoteSvc = None

    def Run(self, *args):
        Service.Run(self, args)
        self.remoteSvc = sm.RemoteSvc('itemLocking')

    def GetLockedItemsByLocation(self, locationID):
        with TempLock('GetLockedItemsByLocation_%s' % locationID):
            if locationID not in self.lockedItemsByLocationID:
                self.lockedItemsByLocationID[locationID] = self.remoteSvc.GetItemsByLocation(locationID)
        return self.lockedItemsByLocationID[locationID]

    def GetLockedItemLocations(self):
        with TempLock('GetLockedItemLocations'):
            if self.locationsWithLockedItems is None:
                self.locationsWithLockedItems = self.remoteSvc.GetLockedItemLocations()
        return self.locationsWithLockedItems

    def IsItemLocked(self, item):
        if not IsCorporation(item.ownerID):
            return False
        if item.flagID == const.flagCorpDeliveries and item.locationID in (session.structureid, session.stationid) and not self._CanTakeFromDeliveries():
            return True
        for office in sm.GetService('officeManager').GetMyCorporationsOffices():
            if office.officeID == item.locationID:
                if item.itemID in self.GetLockedItemsByLocation(office.stationID):
                    return True

        return self.IsItemIDLocked(item.itemID)

    def IsItemIDLocked(self, itemID):
        stationID = session.stationid or session.structureid
        if stationID is not None:
            return itemID in self.GetLockedItemsByLocation(stationID)
        return False

    @staticmethod
    def _CanTakeFromDeliveries():
        return session.corprole & (const.corpRoleAccountant | const.corpRoleTrader)

    def OnLockedItemChange(self, itemID, ownerID, locationID, isLocked):
        try:
            del self.lockedItemsByLocationID[locationID]
        except KeyError:
            pass

        if self.locationsWithLockedItems is not None:
            if isLocked:
                self.locationsWithLockedItems.add(locationID)
            elif len(self.GetLockedItemsByLocation(locationID)) == 0:
                self.locationsWithLockedItems.discard(locationID)
        sm.ScatterEvent('OnLockedItemChangeUI', itemID, ownerID, locationID)
