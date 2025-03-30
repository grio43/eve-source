#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\static_data\component_category.py
from itertoolsext.Enum import Enum
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import ship_skin_design_component_categoriesLoader
except ImportError:
    ship_skin_design_component_categoriesLoader = None

class _ComponentCategoriesDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/ship_skin_design_component_categories.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/ship_skin_design_component_categories.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/ship_skin_design_component_categories.fsdbinary'
    __loader__ = ship_skin_design_component_categoriesLoader


def get_component_categories_data():
    return _ComponentCategoriesDataLoader.GetData()


@Enum

class ComponentCategory(object):
    MATERIAL = 1
    PATTERN = 2
    METALLIC = 3


def get_category_from_fsd(fsd_category_id):
    if fsd_category_id == 1:
        return ComponentCategory.MATERIAL
    elif fsd_category_id == 2:
        return ComponentCategory.PATTERN
    elif fsd_category_id == 3:
        return ComponentCategory.METALLIC
    else:
        return None
