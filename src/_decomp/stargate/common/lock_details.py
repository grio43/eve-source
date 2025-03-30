#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\stargate\common\lock_details.py


class LockDetails(object):

    def __init__(self, solar_system_id, gate_id, expiry_time):
        self.solar_system_id = solar_system_id
        self.gate_id = gate_id
        self.expiry_time = expiry_time

    def __eq__(self, other):
        return self.solar_system_id == other.solar_system_id and self.gate_id == other.gate_id and self.expiry_time == other.expiry_time

    def __ne__(self, other):
        return not self.__eq__(other)
