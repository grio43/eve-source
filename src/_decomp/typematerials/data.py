#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\typematerials\data.py
from dogma.identity import get_safe_dogma_identity
import evetypes
from fsdBuiltData.common.base import BuiltDataLoader
from collections import namedtuple
from inventorycommon import const
try:
    import typeMaterialsLoader
except ImportError:
    typeMaterialsLoader = None

NONE_TYPES = (const.typeCredits, const.typeBookmark, const.typeBiomass)
NONE_GROUPS = (const.groupRookieship, const.groupMineral)
NONE_CATEGORIES = (const.categoryBlueprint, const.categoryReaction)
ReprocessingOptions = namedtuple('ReprocessingOptions', ['typeID', 'isRecyclable', 'isRefinable'])

class TypeMaterials(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/typeMaterials.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/typeMaterials.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/typeMaterials.fsdbinary'
    __loader__ = typeMaterialsLoader


def _get_all():
    return TypeMaterials.GetData()


def _get_by_id(type_id):
    type_id = get_safe_dogma_identity(type_id)
    return _get_all().get(type_id, None)


def get_type_materials_by_id(type_id):
    type_materials = _get_by_id(type_id)
    if type_materials:
        return type_materials.materials
    return []


def get_types_with_no_materials():
    all_type_ids = evetypes.GetAllTypeIDs()
    type_material_ids = [ i for i in _get_all().iterkeys() ]
    return [ typeID for typeID in all_type_ids if typeID not in type_material_ids ]


def type_has_materials(type_id):
    return len(get_type_materials_by_id(type_id)) > 0


def is_reprocessable_type(type_id):
    return type_has_materials(type_id) and not is_decompressible_gas_type(type_id)


def is_decompressible_gas_type(type_id):
    return type_has_materials(type_id) and evetypes.GetGroupID(type_id) == const.groupCompressedGas


def get_reprocessing_options(type_id):
    group_id = evetypes.GetGroupID(type_id)
    category_id = evetypes.GetCategoryID(type_id)
    can_recycle = False
    can_refine = False
    if type_id not in NONE_TYPES and group_id not in NONE_GROUPS and category_id not in NONE_CATEGORIES:
        if is_reprocessable_type(type_id):
            if category_id == const.categoryAsteroid or group_id == const.groupHarvestableCloud:
                can_refine = True
            else:
                can_recycle = True
    return ReprocessingOptions(type_id, can_recycle, can_refine)
