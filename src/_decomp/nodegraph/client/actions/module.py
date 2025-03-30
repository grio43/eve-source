#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\module.py
from inventorycommon.const import flagAutoFit, flagCargo, flagHangar, containerHangar
import eve.common.script.sys.eveCfg as eveCfg
import eve.common.script.sys.idCheckers as idCheckers
from carbonui.uicore import uicore
from .base import Action

class ActivateModule(Action):
    atom_id = 323

    def __init__(self, item_id = None, **kwargs):
        super(ActivateModule, self).__init__(**kwargs)
        self.item_id = item_id

    def start(self, **kwargs):
        super(ActivateModule, self).start(**kwargs)
        if self.item_id and uicore.layer.shipui.isopen:
            uicore.layer.shipui.ActivateModuleByItemID(self.item_id)


class DeactivateModule(Action):
    atom_id = 324

    def __init__(self, item_id = None, **kwargs):
        super(DeactivateModule, self).__init__(**kwargs)
        self.item_id = item_id

    def start(self, **kwargs):
        super(DeactivateModule, self).start(**kwargs)
        if self.item_id and uicore.layer.shipui.isopen:
            uicore.layer.shipui.DeactivateModuleByItemID(self.item_id)


class FitModule(Action):
    atom_id = 321

    def __init__(self, item_id = None, item_location_id = None, **kwargs):
        super(FitModule, self).__init__(**kwargs)
        self.item_id = item_id
        self.item_location_id = item_location_id

    def start(self, **kwargs):
        super(FitModule, self).start(**kwargs)
        if not self.item_id or not self.item_location_id:
            return
        if not eveCfg.IsDocked() or not eveCfg.InShip():
            return
        ship_inventory = sm.GetService('invCache').GetInventoryFromId(session.shipid, locationID=session.locationid)
        ship_inventory.moniker.MultiAdd([self.item_id], self.item_location_id, flag=flagAutoFit)


class UnfitModule(Action):
    atom_id = 322

    def __init__(self, item_id = None, **kwargs):
        super(UnfitModule, self).__init__(**kwargs)
        self.item_id = item_id

    def start(self, **kwargs):
        super(UnfitModule, self).start(**kwargs)
        if not self.item_id or not eveCfg.InShip():
            return
        if session.stationid or session.structureid:
            sm.GetService('invCache').GetInventory(containerHangar).Add(self.item_id, session.shipid, flag=flagHangar)
        else:
            ship_inventory = sm.GetService('invCache').GetInventoryFromId(session.shipid, locationID=session.locationid)
            ship_inventory.Add(self.item_id, session.shipid, qty=None, flag=flagCargo)


class LoadCharges(Action):
    atom_id = 325

    def __init__(self, inventory_item = None, module_item_id = None, **kwargs):
        super(LoadCharges, self).__init__(**kwargs)
        self.inventory_item = inventory_item
        self.module_item_id = module_item_id

    def start(self, **kwargs):
        super(LoadCharges, self).start(**kwargs)
        if not self.inventory_item or not eveCfg.InShip():
            return
        dogma_location = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if self.module_item_id:
            dogma_location.LoadAmmoToModules(session.shipid, [self.module_item_id], [self.inventory_item.itemID], self.inventory_item.locationID)
        else:
            dogma_location.LoadChargeToAllModules(self.inventory_item)


class UnloadCharges(Action):
    atom_id = 424

    def __init__(self, item_id = None, **kwargs):
        super(UnloadCharges, self).__init__(**kwargs)
        self.item_id = item_id

    def _get_fitted_items(self):
        dogma_location = sm.GetService('clientDogmaIM').GetDogmaLocation()
        return dogma_location.GetFittedItemsToShip()

    def _get_item(self):
        fitted_items = self._get_fitted_items()
        for item in fitted_items.itervalues():
            if item.itemID == self.item_id:
                return item

    def _unfit_charges_by_slot_flag(self, flag_id):
        from eve.client.script.ui.shared.fitting.fittingControllerUtil import GetFittingController
        ship_fitting_controller = GetFittingController(session.shipid)
        slot_fitting_controller = ship_fitting_controller.GetSlotController(flag_id)
        slot_fitting_controller.UnfitCharge()

    def start(self, **kwargs):
        super(UnloadCharges, self).start(**kwargs)
        if not self.item_id or not eveCfg.InShip():
            return
        item = self._get_item()
        if item:
            self._unfit_charges_by_slot_flag(item.flagID)


class OnlineModule(Action):
    atom_id = 390

    def __init__(self, item_id = None, **kwargs):
        super(OnlineModule, self).__init__(**kwargs)
        self.item_id = item_id

    def start(self, **kwargs):
        super(OnlineModule, self).start(**kwargs)
        if not self.item_id or not eveCfg.InShip():
            return
        dogma_location = sm.GetService('clientDogmaIM').GetDogmaLocation()
        dogma_location.OnlineModule(self.item_id)


class StripFitting(Action):
    atom_id = 332

    def __init__(self, ship_id = None, **kwargs):
        super(StripFitting, self).__init__(**kwargs)
        self.ship_id = ship_id

    def start(self, **kwargs):
        super(StripFitting, self).start(**kwargs)
        ship_id = self.ship_id or session.shipid
        if self._can_strip(ship_id):
            sm.GetService('invCache').StripFitting(ship_id)

    def _can_strip(self, ship_id):
        try:
            if not eveCfg.IsDocked():
                return False
            inventory = sm.GetService('invCache').GetInventory(containerHangar)
            ship = None
            for item in inventory.List(flagHangar):
                if item.itemID == ship_id:
                    ship = item
                    break

            if not ship:
                return False
            if not idCheckers.IsShip(ship.categoryID):
                return False
            if idCheckers.IsCapsule(ship.groupID):
                return False
        except:
            return False

        return True
