#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\static_data\component.py
from evetypes import TypeNotFoundException
import chroma
import logging
import sys
import evetypes
from itertoolsext.Enum import Enum
from cosmetics.common.ships.skins.static_data.ntc import ntc
from cosmetics.common.ships.skins.static_data.component_finish import get_finish_from_fsd
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from cosmetics.common.ships.skins.static_data.component_point_value import ComponentPointValuesTable
from inventorycommon.const import groupShipSkinDesignComponents
from localization import GetByMessageID
from fsdBuiltData.common.base import BuiltDataLoader
from cosmetics.common.ships.skins.static_data.component_category import get_category_from_fsd, ComponentCategory
from cosmetics.common.ships.skins.static_data.component_rarity import get_rarity_from_fsd, ComponentRarityLevel
from cosmetics.common.ships.skins.static_data.slot_name import SlotID
COMPONENT_ITEM_INFINITE_USES_GRANTED = -1
try:
    import ship_skin_design_componentsLoader
except ImportError:
    ship_skin_design_componentsLoader = None

try:
    import ship_skin_design_components_post_processLoader
except ImportError:
    ship_skin_design_components_post_processLoader = None

log = logging.getLogger(__name__)

class ComponentsPostProcessDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/ship_skin_design_components_post_process.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/ship_skin_design_components_post_process.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/ship_skin_design_components_post_process.fsdbinary'
    __loader__ = ship_skin_design_components_post_processLoader

    @classmethod
    def get_hex_color_by_id(cls, component_id):
        components_post_process_data = cls.GetData()
        if not components_post_process_data:
            log.error('GetData() returned None in ComponentsPostProcessDataLoader.get_hex_color_by_id')
            return
        component_color_hex = components_post_process_data.get(component_id, None)
        if component_color_hex is None:
            log.error('component id %s not found in ComponentsPostProcessDataLoader' % component_id)
        return component_color_hex


class ComponentsDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/ship_skin_design_components.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/ship_skin_design_components.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/ship_skin_design_components.fsdbinary'
    __loader__ = ship_skin_design_componentsLoader
    _components_by_id = None
    _is_initialized = False

    @classmethod
    def ReloadDataFromDisk(cls):
        cls._components_by_id = None
        cls._is_initialized = False

    @classmethod
    def get_component_data(cls, component_id):
        cls._check_init_components_by_id()
        return cls._components_by_id.get(component_id, None)

    @classmethod
    def get_components_data(cls, category_filter = None, slot_internal_name_filter = None):
        cls._check_init_components_by_id()
        result = {}
        for component_id, component_data in cls._components_by_id.items():
            if (category_filter is None or component_data.category in category_filter) and (slot_internal_name_filter is None or slot_internal_name_filter not in component_data.disallowed_slot_ids):
                result[component_id] = component_data

        return result

    @classmethod
    def load_components_data(cls):
        cls._check_init_components_by_id()

    @classmethod
    def _check_init_components_by_id(cls):
        if cls._is_initialized:
            return
        log.info('SKIN COMPONENT LICENSES MANAGEMENT - Start loading component data')
        cls._components_by_id = {}
        components_data = ComponentsDataLoader.GetData()
        if not components_data:
            log.info('SKIN COMPONENT LICENSES MANAGEMENT - Component data unavailable, will try again later')
            return
        for component_id, component_data in components_data.items():
            cls._components_by_id[component_id] = ComponentData.build_from_fsd(component_id, component_data, ComponentPointValuesTable())

        cls._is_initialized = True
        log.info('SKIN COMPONENT LICENSES MANAGEMENT - Finished loading component data')

    @classmethod
    def ReloadDataFromDisk(cls):
        super(ComponentsDataLoader, cls).ReloadDataFromDisk()
        cls._components_by_id = None

    @classmethod
    def get_component_for_component_type(cls, component_type_id):
        try:
            group_id = evetypes.GetGroupID(component_type_id)
        except TypeNotFoundException:
            return None

        if group_id != groupShipSkinDesignComponents:
            log.warning('type id %s must be of group %s to be matched to a ship skin component' % (component_type_id, groupShipSkinDesignComponents))
        components = cls.get_components_data()
        for component_id, component_data in components.items():
            item_data = component_data.component_item_data_by_type_id.get(component_type_id)
            if item_data:
                return component_data

        log.warning('could not match type id %s to any component id' % component_type_id)

    @classmethod
    def get_component_item_for_component_type(cls, component_type_id):
        component_data = cls.get_component_for_component_type(component_type_id)
        if component_data:
            item_data = component_data.component_item_data_by_type_id.get(component_type_id)
            return item_data


class ComponentData(object):

    def __init__(self, component_id, internal_name, name_id, description_id, origin_event_id, category, rarity, finish, resource_file_path, icon_file_path, disallowed_slot_ids, associated_type_ids, sequence_binder_type_id, sequence_binder_required_amount, points_value, projection_type_uv, published):
        self._color_shade_sort_index = sys.maxint
        log.info('ComponentData init  - component_id: {component_id} name_id: {name_id} icon_file_path: {icon_file_path}'.format(component_id=component_id, name_id=name_id, icon_file_path=icon_file_path))
        component_color_hex = ComponentsPostProcessDataLoader.get_hex_color_by_id(component_id)
        if component_color_hex is None:
            log.warning('None returned by get_hex_color_by_id for component_id: {component_id} name_id: {name_id} icon_file_path: {icon_file_path} ComponentData init  - resource_file_path: {resource_file_path}'.format(component_id=component_id, name_id=name_id, resource_file_path=resource_file_path, icon_file_path=icon_file_path))
        else:
            color_shade_name = ntc.shade_name_from_hex(component_color_hex)
            color_order_list = ['Red',
             'Orange',
             'Yellow',
             'Green',
             'Blue',
             'Violet',
             'Brown',
             'Black',
             'Grey',
             'White']
            self._color_shade_sort_index = color_order_list.index(color_shade_name)
            apply_secondary_hue_sort = True
            if apply_secondary_hue_sort:
                hue, s, l = chroma.hex_to_hsl(component_color_hex)
                self._color_shade_sort_index *= 1000
                self._color_shade_sort_index += int(float(hue) * 360.0)
            log.info('color_shade_name: {color_shade_name} color_shade_sort_index: {color_shade_sort_index} ComponentData init - component_id: {component_id} name_id: {name_id} resource_file_path: {resource_file_path}'.format(component_id=component_id, name_id=name_id, resource_file_path=resource_file_path, color_shade_name=color_shade_name, color_shade_sort_index=self._color_shade_sort_index))
        self._component_id = component_id
        self._internal_name = internal_name
        self._name_id = name_id
        self._description_id = description_id
        self._origin_event_id = origin_event_id
        self._category = category
        self._rarity = rarity
        self._finish = finish
        self._resource_file_path = resource_file_path
        self._icon_file_path = icon_file_path
        self._disallowed_slot_ids = disallowed_slot_ids
        self._component_item_data_by_type_id = associated_type_ids
        self._sequence_binder_type_id = sequence_binder_type_id
        self._sequence_binder_required_amount = sequence_binder_required_amount
        self._points_value = points_value
        self._projection_type_uv = projection_type_uv
        self._published = published

    @property
    def color_shade_sort_index(self):
        return self._color_shade_sort_index

    @property
    def component_id(self):
        return self._component_id

    @property
    def internal_name(self):
        return self._internal_name

    @property
    def name(self):
        return GetByMessageID(self._name_id)

    @property
    def description(self):
        return GetByMessageID(self._description_id)

    @property
    def origin_event_name(self):
        if self._origin_event_id:
            return GetByMessageID(self._origin_event_id)

    @property
    def category(self):
        return self._category

    @property
    def rarity(self):
        return self._rarity

    @property
    def finish(self):
        return self._finish

    @property
    def resource_file_path(self):
        return self._resource_file_path

    @property
    def icon_file_path(self):
        return self._icon_file_path

    @property
    def disallowed_slot_ids(self):
        return self._disallowed_slot_ids

    @property
    def projection_type_uv(self):
        return self._projection_type_uv

    @property
    def component_item_data_by_type_id(self):
        return self._component_item_data_by_type_id

    @property
    def sequence_binder_type_id(self):
        return self._sequence_binder_type_id

    @property
    def sequence_binder_required_amount(self):
        return self._sequence_binder_required_amount

    @property
    def published(self):
        return self._published

    @property
    def points_value(self):
        return self._points_value

    def get_license_type(self, type_id):
        component_item = self.component_item_data_by_type_id.get(type_id, None)
        if component_item:
            return component_item.license_type

    def get_item_type(self, license_type):
        for type_id, component_item in self.component_item_data_by_type_id.items():
            if component_item.license_type == license_type:
                return type_id

    @staticmethod
    def build_from_fsd(component_id, fsd_data, points_value_table):
        internal_name = fsd_data.internal_name
        name_id = fsd_data.name
        description_id = fsd_data.description
        origin_event_id = fsd_data.origin_event
        category = get_category_from_fsd(fsd_data.category)
        rarity = get_rarity_from_fsd(fsd_data.rarity)
        finish = get_finish_from_fsd(fsd_data.finish)
        resource_file_path = fsd_data.resource_file
        icon_file_path = fsd_data.icon_file
        disallowed_slot_ids = [ x for x in fsd_data.disallowed_slots ]
        associated_type_ids = {x.type_id:ComponentItemData(component_id, category, x.type_id, x.license_uses_granted) for x in fsd_data.associated_type_ids}
        sequence_binder_type_id = fsd_data.sequence_binder.item_type_id
        sequence_binder_required_amount = fsd_data.sequence_binder.count
        points_value = points_value_table.get_point_value(category, rarity)
        projection_type_uv = [projection_type_from_fsd(fsd_data.projection_type_u), projection_type_from_fsd(fsd_data.projection_type_v)]
        published = fsd_data.published
        return ComponentData(component_id, internal_name, name_id, description_id, origin_event_id, category, rarity, finish, resource_file_path, icon_file_path, disallowed_slot_ids, associated_type_ids, sequence_binder_type_id, sequence_binder_required_amount, points_value, projection_type_uv, published)


class ComponentItemData(object):

    def __init__(self, component_id, category, type_id, license_uses_granted):
        self._component_id = component_id
        self._category = category
        self._type_id = type_id
        self._license_uses_granted = license_uses_granted if license_uses_granted > 0 else COMPONENT_ITEM_INFINITE_USES_GRANTED

    @property
    def component_id(self):
        return self._component_id

    @property
    def category(self):
        return self._category

    @property
    def type_id(self):
        return self._type_id

    @property
    def license_uses_granted(self):
        return self._license_uses_granted

    @property
    def license_type(self):
        if self._license_uses_granted == COMPONENT_ITEM_INFINITE_USES_GRANTED:
            return ComponentLicenseType.UNLIMITED
        else:
            return ComponentLicenseType.LIMITED


@Enum

class PatternProjectionType(object):
    CLAMP = 0
    REPEAT = 1
    BORDER = 2


_PROJECTION_TYPE_FSD_MAPPING = {'Clamp': PatternProjectionType.CLAMP,
 'Repeat': PatternProjectionType.REPEAT,
 'Border': PatternProjectionType.BORDER}
_PROJECTION_TYPE_TO_FSD_MAPPING = {PatternProjectionType.CLAMP: 'Clamp',
 PatternProjectionType.REPEAT: 'Repeat',
 PatternProjectionType.BORDER: 'Border'}

def projection_type_from_fsd(fsd_value):
    return _PROJECTION_TYPE_FSD_MAPPING.get(fsd_value, None)


def projection_type_to_fsd(value):
    return _PROJECTION_TYPE_TO_FSD_MAPPING.get(value, None)
