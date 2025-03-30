#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\inventory.py
import eve.common.script.sys.eveCfg as eveCfg
import eve.client.script.ui.services.menuSvcExtras.invItemFunctions as inventory_functions
from .base import Action

class JettisonTrashItem(Action):
    atom_id = 336

    def __init__(self, inventory_item = None, **kwargs):
        super(JettisonTrashItem, self).__init__(**kwargs)
        self.inventory_item = inventory_item

    def start(self, **kwargs):
        super(JettisonTrashItem, self).start(**kwargs)
        if not self.inventory_item:
            return
        if eveCfg.InShipInSpace():
            inventory_functions.Jettison([self.inventory_item], showPrompt=False)
        else:
            inventory_functions.TrashInvItems([self.inventory_item], sm.GetService('invCache'), showPrompt=False)


class AddItemRestriction(Action):
    atom_id = 449

    def __init__(self, type_id = None, typelist_id = None, **kwargs):
        super(AddItemRestriction, self).__init__(**kwargs)
        self.type_id = type_id
        self.typelist_id = typelist_id

    def _get_restrictions_tracker(self):
        from inventoryrestrictions.client.tracker import InventoryRestrictionsTracker
        return InventoryRestrictionsTracker()

    def start(self, **kwargs):
        super(AddItemRestriction, self).start(**kwargs)
        if self.type_id and self.typelist_id:
            self._get_restrictions_tracker().add_client_restriction_on_type(int(self.type_id), int(self.typelist_id))

    def stop(self):
        super(AddItemRestriction, self).stop()
        if self.type_id and self.typelist_id:
            self._get_restrictions_tracker().remove_client_restriction_on_type(int(self.type_id), int(self.typelist_id))

    @classmethod
    def get_subtitle(cls, type_id = None, typelist_id = None, **kwargs):
        if type_id and typelist_id:
            return u'{}: {}'.format(type_id, typelist_id)
        return ''


class RemoveItemRestriction(Action):
    atom_id = 450

    def __init__(self, type_id = None, typelist_id = None, **kwargs):
        super(RemoveItemRestriction, self).__init__(**kwargs)
        self.type_id = type_id
        self.typelist_id = typelist_id

    def _get_restrictions_tracker(self):
        from inventoryrestrictions.client.tracker import InventoryRestrictionsTracker
        return InventoryRestrictionsTracker()

    def start(self, **kwargs):
        super(RemoveItemRestriction, self).start(**kwargs)
        tracker = self._get_restrictions_tracker()
        if self.type_id and self.typelist_id:
            tracker.remove_client_restriction_on_type(int(self.type_id), int(self.typelist_id))
        else:
            tracker.remove_all_client_restrictions()

    @classmethod
    def get_subtitle(cls, type_id = None, typelist_id = None, **kwargs):
        if type_id and typelist_id:
            return u'{}: {}'.format(type_id, typelist_id)
        return ''


class ScatterInventoryItemsMoved(Action):
    atom_id = 489

    def start(self, **kwargs):
        super(ScatterInventoryItemsMoved, self).start(**kwargs)
        self._simulate_move_from_cargo_to_item_hangar()

    def _simulate_move_from_cargo_to_item_hangar(self):
        from carbon.common.lib.const import ixLocationID, ixFlag
        from inventorycommon.const import flagCargo
        change = {ixLocationID: session.shipid,
         ixFlag: flagCargo}
        items = [ItemMock(character_id=session.charid, location_id=session.stationid)]
        sm.ScatterEvent('OnMultipleItemChange', items, change)


class ItemMock(object):

    def __init__(self, character_id, location_id):
        from inventorycommon.const import flagHangar, typeVeldspar, groupVeldspar, categoryAsteroid
        self.itemID = 1000000212149L
        self.typeID = typeVeldspar
        self.ownerID = character_id
        self.locationID = location_id
        self.flagID = flagHangar
        self.quantity = 1
        self.groupID = groupVeldspar
        self.categoryID = categoryAsteroid
        self.customInfo = ''
        self.stacksize = 1
        self.singleton = 0
