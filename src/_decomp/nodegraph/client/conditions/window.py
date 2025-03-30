#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\window.py
from carbonui.uicore import uicore
from carbonui.control.window import Window
from eve.client.script.ui.shared.inventory.invWindow import Inventory as InventoryWindow
import inventorycommon.const as inventoryConst
from .base import Condition

class WindowCondition(Condition):
    atom_id = None

    def __init__(self, window_id = None, **kwargs):
        super(WindowCondition, self).__init__(**kwargs)
        self.window_id = window_id

    @classmethod
    def get_subtitle(cls, window_id = None, **kwargs):
        return window_id


class IsWindowClosed(WindowCondition):
    atom_id = 35

    def validate(self, **kwargs):
        window = get_window(self.window_id)
        return not window or window.IsMinimized()


class IsWindowMinimized(WindowCondition):
    atom_id = 36

    def validate(self, **kwargs):
        window = get_window(self.window_id)
        return window and window.IsMinimized()


class IsWindowOpen(WindowCondition):
    atom_id = 37

    def validate(self, **kwargs):
        window = get_window(self.window_id)
        return window and not window.IsMinimized()


class IsWindowHovered(WindowCondition):
    atom_id = 349

    def validate(self, **kwargs):
        window = get_window(self.window_id)
        return window and window.IsHovered()


class InventoryOpen(Condition):
    atom_id = 127

    def __init__(self, inventory_container = None, window_instance_id = None, **kwargs):
        super(InventoryOpen, self).__init__(**kwargs)
        self.inventory_container = inventory_container
        self.window_instance_id = window_instance_id

    def validate(self, **kwargs):
        window_instance_id = self.window_instance_id
        window_id = self.inventory_container
        if window_id in inventoryConst.ALL_HOLDS:
            if window_instance_id in [session.shipid, None]:
                ship_cargo_window_id = 'ActiveShipCargo'
            else:
                ship_cargo_window_id = inventoryConst.INVENTORY_ID_SHIP_CARGO
            window = get_window(ship_cargo_window_id, window_instance_id)
            if window and window_id == window.currInvID[0]:
                return True
            if not window_instance_id:
                window_instance_id = session.shipid
        window = get_window(window_id, window_instance_id)
        if window and window_id == window.currInvID[0]:
            return True
        inventory_window_open = False
        for inventory_window_id in [inventoryConst.INVENTORY_ID_STATION, inventoryConst.INVENTORY_ID_SPACE, inventoryConst.INVENTORY_ID_STRUCTURE]:
            window = get_window(inventory_window_id)
            if not window or not window.currInvID:
                continue
            if window_id == window.currInvID[0]:
                return not window_instance_id or window_instance_id == window.currInvID[1]
            inventory_window_open = True

        return bool(not window_id and inventory_window_open)

    @classmethod
    def get_subtitle(cls, inventory_container = '', **kwargs):
        return inventory_container


def get_window(window_id, window_instance_id = None):
    return Window.GetIfOpen(window_id, window_instance_id)
