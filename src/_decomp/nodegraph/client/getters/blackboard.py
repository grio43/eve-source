#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\blackboard.py
from eve.common.script.net.eveMoniker import GetEntityLocation
from .base import GetterAtom

class GetShipsWarping(GetterAtom):
    atom_id = 233

    def __init__(self, item_id = None, include_item_id = None):
        self.item_id = item_id
        self.include_item_id = self.get_atom_parameter_value('include_item_id', include_item_id)

    def get_values(self, **kwargs):
        entity_location = GetEntityLocation()
        fleet_members = entity_location.GetExtraFleetMembers(self.item_id) or set()
        if self.include_item_id:
            fleet_members.add(self.item_id)
        return {'item_ids': fleet_members}
