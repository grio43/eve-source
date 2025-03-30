#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\static_data\slot.py
from cosmetics.common.ships.skins.static_data import slot_name
from cosmetics.common.ships.skins.static_data.component import ComponentsDataLoader
from cosmetics.common.ships.skins.static_data.component_category import get_category_from_fsd, ComponentCategory
from cosmetics.common.ships.skins.static_data.slot_category import get_slot_category_from_fsd, SlotCategory
from cosmetics.common.ships.skins.static_data.slot_name import SlotID
from localization import GetByMessageID
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import ship_cosmetic_slotsLoader
except ImportError:
    ship_cosmetic_slotsLoader = None

class SlotsDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/ship_cosmetic_slots.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/ship_cosmetic_slots.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/ship_cosmetic_slots.fsdbinary'
    __loader__ = ship_cosmetic_slotsLoader
    _slot_data_by_id = None

    @classmethod
    def get_slots_by_id(cls):
        return cls.GetData()

    @classmethod
    def get_slot_data(cls, slot_id):
        cls._check_init_slot_definitions()
        return cls._slot_data_by_id[slot_id]

    @classmethod
    def _check_init_slot_definitions(cls):
        if cls._slot_data_by_id:
            return
        cls._slot_data_by_id = {}
        for slot_id, slot_data in SlotsDataLoader.GetData().items():
            cls._slot_data_by_id[slot_id] = Slot.build_from_fsd(slot_id, slot_data)

    @classmethod
    def ReloadDataFromDisk(cls):
        super(SlotsDataLoader, cls).ReloadDataFromDisk()
        cls._slot_data_by_id = None

    @classmethod
    def get_allowed_component(cls, slot_id):
        slot_data = cls.get_slot_data(slot_id)
        allowed_components = ComponentsDataLoader.get_components_data(category_filter=slot_data.allowed_component_categories, slot_internal_name_filter=slot_data.unique_id)
        return allowed_components


class Slot(object):

    def __init__(self, unique_id, category, name_id, description_id, allowed_component_categories):
        self._unique_id = unique_id
        self._internal_name = slot_name.INTERNAL_NAME_BY_SLOT_ID[unique_id]
        self._category = category
        self._name_id = name_id
        self._description_id = description_id
        self._allowed_component_categories = allowed_component_categories

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def internal_name(self):
        return self._internal_name

    @property
    def category(self):
        return self._category

    @property
    def name(self):
        return GetByMessageID(self._name_id)

    @property
    def description(self):
        return GetByMessageID(self._description_id)

    @property
    def allowed_component_categories(self):
        return self._allowed_component_categories

    @staticmethod
    def build_from_fsd(slot_id, fsd_data):
        name_id = fsd_data.name
        description_id = fsd_data.description
        category = get_slot_category_from_fsd(fsd_data.category)
        allowed_component_categories = [ get_category_from_fsd(x) for x in fsd_data.allowed_design_component_categories ]
        return Slot(slot_id, category, name_id, description_id, allowed_component_categories)
