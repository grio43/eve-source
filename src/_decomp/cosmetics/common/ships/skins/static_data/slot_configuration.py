#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\static_data\slot_configuration.py
import evetypes
from eve.common.lib import appConst
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import ship_cosmetic_slot_configurationsLoader
except ImportError:
    ship_cosmetic_slot_configurationsLoader = None

class SlotConfigurationsDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/ship_cosmetic_slot_configurations.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/ship_cosmetic_slot_configurations.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/ship_cosmetic_slot_configurations.fsdbinary'
    __loader__ = ship_cosmetic_slot_configurationsLoader
    _slot_configurations = None

    @classmethod
    def _check_init_slot_configurations(cls):
        if cls._slot_configurations:
            return
        configs = [ (SlotConfiguration.build_from_fsd(data), data.priority) for data in cls.GetData().values() ]
        cls._slot_configurations = [ a for a, b in sorted(configs, key=lambda x: x[1], reverse=False) ]

    @classmethod
    def get_for_ship(cls, type_id):
        cls._check_init_slot_configurations()
        for config in cls._slot_configurations:
            if config.is_ship_type_allowed(type_id):
                return config

    @classmethod
    def get_type_ids_with_empty_slot_configuration(cls):
        cls._check_init_slot_configurations()
        ship_list = []
        for config in cls._slot_configurations:
            if len(config.slots) == 0:
                ship_list.extend(config.allowed_ship_types)

        return ship_list

    @classmethod
    def ReloadDataFromDisk(cls):
        super(SlotConfigurationsDataLoader, cls).ReloadDataFromDisk()
        cls._slot_configurations = None


class SlotConfiguration(object):

    def __init__(self, slot_ids, allowed_ship_types, priority):
        self._slots = slot_ids
        self._allowed_ship_types = allowed_ship_types
        self._priority = priority

    def is_ship_type_allowed(self, ship_type_id):
        if self._allowed_ship_types is None or ship_type_id in self._allowed_ship_types:
            return True
        else:
            return False

    @property
    def slots(self):
        return self._slots

    @property
    def allowed_ship_types(self):
        return self._allowed_ship_types

    @staticmethod
    def build_from_fsd(fsd_data):
        slot_ids = fsd_data.config
        allowed_ship_types = None if fsd_data.allow_all_ships else fsd_data.ships
        priority = fsd_data.priority
        return SlotConfiguration(slot_ids, allowed_ship_types, priority)


def is_skinnable_ship(type_id):
    if evetypes.GetCategoryID(type_id) != appConst.categoryShip:
        return False
    if type_id in SlotConfigurationsDataLoader.get_type_ids_with_empty_slot_configuration():
        return False
    return True
