#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\static_data\slot_category.py
from itertoolsext.Enum import Enum
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import ship_cosmetic_slot_categoriesLoader
except ImportError:
    ship_cosmetic_slot_categoriesLoader = None

class _SlotCategoriesDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/ship_cosmetic_slot_categories.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/ship_cosmetic_slot_categories.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/ship_cosmetic_slot_categories.fsdbinary'
    __loader__ = ship_cosmetic_slot_categoriesLoader


def get_slot_categories_data():
    return _SlotCategoriesDataLoader.GetData()


@Enum

class SlotCategory(object):
    MATERIAL = 1
    PATTERN = 2
    PATTERN_MATERIAL = 3


def get_slot_category_from_fsd(fsd_slot_category_id):
    if fsd_slot_category_id == 1:
        return SlotCategory.MATERIAL
    elif fsd_slot_category_id == 2:
        return SlotCategory.PATTERN
    elif fsd_slot_category_id == 3:
        return SlotCategory.PATTERN_MATERIAL
    else:
        return None
