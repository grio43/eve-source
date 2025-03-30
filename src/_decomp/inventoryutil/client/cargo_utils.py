#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\inventoryutil\client\cargo_utils.py
from eve.client.script.environment.invControllers import ShipCargo
from inventorycommon.const import CARGO_CAPACITY_NUDGE_AMOUNT

def get_cargo_volume_available():
    cargo_hold_controller = ShipCargo()
    cargo_capacity = cargo_hold_controller.GetCapacity()
    available = cargo_capacity.capacity - cargo_capacity.used
    available += CARGO_CAPACITY_NUDGE_AMOUNT
    return available
