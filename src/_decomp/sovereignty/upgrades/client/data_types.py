#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\upgrades\client\data_types.py
import sovereignty.upgrades.const as upgrades_const

class UpgradeStaticData(object):
    type_id = None
    power = None
    workforce = None
    fuel_type_id = None
    consumption_per_hour = None
    startup_cost = None
    mutually_exclusive_group = None

    def __init__(self, type_id, power, workforce, fuel_type_id, consumption_per_hour, startup_cost, mutually_exclusive_group):
        self.type_id = type_id
        self.power = power
        self.workforce = workforce
        self.fuel_type_id = fuel_type_id
        self.consumption_per_hour = consumption_per_hour
        self.startup_cost = startup_cost
        self.mutually_exclusive_group = mutually_exclusive_group

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.type_id == other.type_id and self.power == other.power and self.workforce == other.workforce and self.fuel_type_id == other.fuel_type_id and self.consumption_per_hour == other.consumption_per_hour and self.startup_cost == other.startup_cost and self.mutually_exclusive_group == other.mutually_exclusive_group

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<UpgradeStaticData %s>' % self.__dict__


class InstalledUpgradeData(object):
    _upgrade_type_id = None
    _power_state = None
    _upgrade_id_key = None

    def __init__(self, upgrade_type_id, power_state, upgrade_id_key):
        self._upgrade_type_id = upgrade_type_id
        self._power_state = power_state
        self._upgrade_id_key = upgrade_id_key

    @property
    def upgrade_type_id(self):
        return self._upgrade_type_id

    @property
    def online_state(self):
        raise DeprecationWarning("'online_state' has been removed - try 'power_state' or one of the 'is_power_[X]' properties instead")

    @property
    def power_state(self):
        return self._power_state

    @property
    def is_power_offline(self):
        return self._power_state == upgrades_const.POWER_STATE_OFFLINE

    @property
    def is_power_online(self):
        return self._power_state == upgrades_const.POWER_STATE_ONLINE

    @property
    def is_power_low(self):
        return self._power_state == upgrades_const.POWER_STATE_LOW

    @property
    def is_power_pending(self):
        return self._power_state == upgrades_const.POWER_STATE_PENDING

    @property
    def upgrade_id_key(self):
        return self._upgrade_id_key

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self._upgrade_type_id == other._upgrade_type_id and self._power_state == other._power_state and self._upgrade_id_key == other._upgrade_id_key

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<InstalledUpgradeData %s>' % self.__dict__

    def take_copy(self):
        return InstalledUpgradeData(self.upgrade_type_id, self.power_state, self.upgrade_id_key)
