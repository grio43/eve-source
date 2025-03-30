#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\inventory.py
from eve.common.lib import appConst
import caching
import evetypes
from .base import Event

class InventoryOpened(Event):
    atom_id = 63
    __notifyevents__ = ['OnInventoryContainerShown']

    def OnInventoryContainerShown(self, inventory_container, previous_inventory_container):
        self.invoke(inventory_container=inventory_container[0], previous_inventory_container=previous_inventory_container[0])


class InventoryClosed(Event):
    atom_id = 64
    __notifyevents__ = ['OnInventoryClosed']

    def OnInventoryClosed(self, inventory_container):
        self.invoke(inventory_container=inventory_container[0])


class CrateOpened(Event):
    atom_id = 65
    __notifyevents__ = ['OnClientEvent_CrateOpen']

    def OnClientEvent_CrateOpen(self, type_id):
        self.invoke(type_id=type_id)


class InventoryItemsChanged(Event):
    atom_id = 69
    __notifyevents__ = ['OnMultipleItemChange']

    def OnMultipleItemChange(self, *args, **kwargs):
        self.invoke()


class InventoryItemsMoved(Event):
    atom_id = 66
    __notifyevents__ = ['OnMultipleItemChange']

    def OnMultipleItemChange(self, items, change):
        if appConst.ixFlag not in change:
            return
        self.invoke(flag_id=items[0].flagID, old_flag_id=change[appConst.ixFlag])


class InventoryItemsMovedToShip(InventoryItemsMoved):
    atom_id = 67

    def invoke(self, **kwargs):
        if kwargs['flag_id'] not in self.flags:
            return
        super(InventoryItemsMovedToShip, self).invoke(**kwargs)

    @caching.lazy_property
    def flags(self):
        return {appConst.flagCargo}.union(appConst.fittingFlags)


class InventoryItemsMovedToShipCargo(InventoryItemsMoved):
    atom_id = 68

    def invoke(self, **kwargs):
        if kwargs['flag_id'] != appConst.flagCargo:
            return
        super(InventoryItemsMovedToShipCargo, self).invoke(**kwargs)


class InventoryItemChanged(Event):
    atom_id = 70
    __notifyevents__ = ['OnItemChanged']

    def OnItemChanged(self, item, change, location):
        self.invoke(item_id=item.itemID, flag_id=item.flagID, old_flag_id=change.get(appConst.ixFlag, None), type_id=item.typeID, group_id=evetypes.GetGroupID(item.typeID))


class InventoryItemMovedToShipCargo(InventoryItemChanged):
    atom_id = 350

    def invoke(self, **kwargs):
        if kwargs['flag_id'] != appConst.flagCargo:
            return
        super(InventoryItemMovedToShipCargo, self).invoke(**kwargs)


class OpenCargoCommand(Event):
    atom_id = 351
    __notifyevents__ = ['OnOpenCargoExecuted']

    def OnOpenCargoExecuted(self, slim_item):
        self.invoke(item_id=slim_item.itemID, type_id=slim_item.typeID, group_id=slim_item.groupID)
