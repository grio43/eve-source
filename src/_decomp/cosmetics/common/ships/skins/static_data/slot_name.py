#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\static_data\slot_name.py
from itertoolsext.Enum import Enum
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import ship_cosmetic_slot_namesLoader
except ImportError:
    ship_cosmetic_slot_namesLoader = None

class _SlotNamesDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/ship_cosmetic_slot_names.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/ship_cosmetic_slot_names.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/ship_cosmetic_slot_names.fsdbinary'
    __loader__ = ship_cosmetic_slot_namesLoader


def get_slot_names_data():
    return _SlotNamesDataLoader.GetData()


@Enum

class SlotID(object):
    PRIMARY_NANOCOATING = 1
    SECONDARY_NANOCOATING = 2
    TERTIARY_NANOCOATING = 3
    TECH_AREA = 4
    PATTERN = 5
    PATTERN_MATERIAL = 6
    SECONDARY_PATTERN = 7
    SECONDARY_PATTERN_MATERIAL = 8


PATTERN_SLOT_IDS = [SlotID.PATTERN, SlotID.SECONDARY_PATTERN]
PATTERN_MATERIAL_SLOT_IDS = [SlotID.PATTERN_MATERIAL, SlotID.SECONDARY_PATTERN_MATERIAL]
PATTERN_RELATED_SLOT_IDS = [SlotID.PATTERN,
 SlotID.PATTERN_MATERIAL,
 SlotID.SECONDARY_PATTERN,
 SlotID.SECONDARY_PATTERN_MATERIAL]
PATTERN_SLOT_ID_BY_PATTERN_MATERIAL_ID = {SlotID.PATTERN_MATERIAL: SlotID.PATTERN,
 SlotID.SECONDARY_PATTERN_MATERIAL: SlotID.SECONDARY_PATTERN}
PATTERN_MATERIAL_SLOT_ID_BY_PATTERN_ID = {value:key for key, value in PATTERN_SLOT_ID_BY_PATTERN_MATERIAL_ID.items()}
INTERNAL_NAME_BY_SLOT_ID = {SlotID.PRIMARY_NANOCOATING: 'primary_nanocoating',
 SlotID.SECONDARY_NANOCOATING: 'secondary_nanocoating',
 SlotID.TERTIARY_NANOCOATING: 'tertiary_nanocoating',
 SlotID.TECH_AREA: 'tech_area',
 SlotID.PATTERN: 'pattern',
 SlotID.PATTERN_MATERIAL: 'pattern_material',
 SlotID.SECONDARY_PATTERN: 'secondary_pattern',
 SlotID.SECONDARY_PATTERN_MATERIAL: 'secondary_pattern_material'}
