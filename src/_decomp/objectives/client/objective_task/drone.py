#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\drone.py
import uthread2
import evetypes
from eve.common.script.sys.eveCfg import InShipInSpace
from eve.common.lib import appConst
from eve.client.script.ui.shared.inventory.invWindow import Inventory
from inventorycommon.const import INVENTORY_ID_SHIP_DRONE_BAY
from objectives.client.objective_task.base import ObjectiveTask

class LoadDroneTask(ObjectiveTask):
    objective_task_content_id = None
    __notifyevents__ = ['OnItemChanged',
     'ProcessActiveShipChanged',
     'OnDroneStateChange2',
     'OnDroneControlLost']

    def ProcessActiveShipChanged(self, *args, **kwargs):
        self.update()

    def OnItemChanged(self, item, change, location):
        if appConst.ixFlag not in change:
            return
        if item.flagID == appConst.flagDroneBay:
            if self._validate_drone(item.typeID):
                self.completed = True
        elif change[appConst.ixFlag] == appConst.flagDroneBay:
            self.update()

    def OnDroneStateChange2(self, *args, **kwargs):
        self.update()

    def OnDroneControlLost(self, *args, **kwargs):
        self.update()

    @uthread2.debounce(0.5)
    def _update(self):
        self.completed = self._validate()

    def _validate(self):
        in_drone_bay = self._validate_drones(self._get_in_drone_bay())
        if in_drone_bay:
            return True
        in_space = self._validate_drones(self._get_in_space())
        if in_space:
            return True
        return False

    def _get_in_drone_bay(self):
        drones = sm.GetService('invCache').GetInventoryFromId(session.shipid).ListDroneBay()
        return drones

    def _get_in_space(self):
        if not InShipInSpace():
            return []
        drones = sm.GetService('michelle').GetDrones() or {}
        return drones.values()

    def _validate_drones(self, drones):
        for drone in drones:
            if self._validate_drone(drone.typeID):
                return True

        return False

    def _validate_drone(self, type_id):
        return True

    def double_click(self):
        Inventory.OpenOrShow(invID=(INVENTORY_ID_SHIP_DRONE_BAY, session.shipid))


class LoadCombatDroneTask(LoadDroneTask):
    objective_task_content_id = 28

    def _validate_drone(self, type_id):
        return evetypes.GetGroupID(type_id) == appConst.groupCombatDrone
