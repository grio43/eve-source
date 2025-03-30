#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\fuel\client\data_types.py
import gametime
from const import HOUR

class Fuel(object):
    _type_id = 0
    _amount_at_last_updated = 0
    _burned_per_hour = 0
    _last_updated_time = None

    @property
    def type_id(self):
        return self._type_id

    @property
    def burned_per_hour(self):
        return self._burned_per_hour

    @property
    def amount_now(self):
        return self.get_amount_at(gametime.GetWallclockTime())

    def __init__(self, type_id, amount, burned_per_hour, last_updated):
        self._type_id = type_id
        self._amount_at_last_updated = amount
        self._burned_per_hour = burned_per_hour
        self._last_updated_time = last_updated

    def __eq__(self, other):
        if not isinstance(other, Fuel):
            return NotImplemented
        return self._type_id == other._type_id and self._amount_at_last_updated == other._amount_at_last_updated and self._burned_per_hour == other._burned_per_hour and self._last_updated_time == other._last_updated_time

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self._type_id,
         self._amount_at_last_updated,
         self._burned_per_hour,
         self._last_updated_time))

    def take_copy(self):
        return Fuel(self._type_id, self._amount_at_last_updated, self._burned_per_hour, self._last_updated_time)

    def get_amount_at(self, time):
        if not self._last_updated_time:
            return self._amount_at_last_updated
        elapsed_hours = float(time - self._last_updated_time) / HOUR
        burned = int(elapsed_hours * self._burned_per_hour)
        return max(self._amount_at_last_updated - burned, 0)

    def get_time_when_empty(self):
        if not self._last_updated_time:
            return None
        if self._burned_per_hour == 0:
            return None
        hours_remaining = self._amount_at_last_updated / float(self._burned_per_hour)
        return self._last_updated_time + int(hours_remaining * HOUR)
