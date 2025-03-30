#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\corpStructureData.py
import evetypes
from cosmetics.common.structures.const import PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS
from structures import UPKEEP_STATE_FULL_POWER, UPKEEP_STATE_LOW_POWER, UPKEEP_STATE_ABANDONED

class CorpStructureData(object):

    def __init__(self, instance_id, type_id, upkeep_state, location_id, license_id = None):
        self.instance_id = instance_id
        self.type_id = type_id
        self.upkeep_state = upkeep_state
        self.location_id = location_id
        self.structure_name = cfg.evelocations.Get(instance_id).name
        self.location_name = cfg.evelocations.Get(location_id).name
        self.type_name = evetypes.GetName(type_id)
        self.price_per_duration = {}
        self.license_id = license_id

    def __eq__(self, other):
        return self.instance_id == other.instance_id

    def get_price_for_duration(self, duration):
        return self.price_per_duration.get(duration, None)

    def is_eligible_for_painting(self):
        return self.type_id in PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS

    def is_ready_for_painting(self):
        return self.upkeep_state == UPKEEP_STATE_FULL_POWER

    def is_low_power(self):
        return self.upkeep_state == UPKEEP_STATE_LOW_POWER

    def is_abandoned(self):
        return self.upkeep_state == UPKEEP_STATE_ABANDONED

    def is_eligible_for_application(self):
        return self.is_eligible_for_painting() and self.is_ready_for_painting()
