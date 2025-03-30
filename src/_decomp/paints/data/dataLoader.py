#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\paints\data\dataLoader.py
import trinity
from fsdBuiltData.common.base import BuiltDataLoader
from paints.data.const import ALL_PAINT_RARITIES, ALL_PAINT_FINISHES
try:
    import paintsLoader
except ImportError:
    paintsLoader = None

try:
    import hueCategoriesLoader
except ImportError:
    hueCategoriesLoader = None

class _PaintsDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/paints.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/paints.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/paints.fsdbinary'
    __loader__ = paintsLoader


class _HueCategoriesDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/hueCategories.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/hueCategories.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/hueCategories.fsdbinary'
    __loader__ = hueCategoriesLoader


def _get_paint(paint_id):
    paint_data = _PaintsDataLoader.GetData()
    try:
        return paint_data[paint_id]
    except KeyError:
        raise PaintDoesNotExistError(paint_id)


def get_paint_ids():
    return _PaintsDataLoader.GetData().keys()


def get_paint_ids_with_finish(finish_id):
    if finish_id not in ALL_PAINT_FINISHES:
        raise ValueError("Invalid finish ID '{0}'".format(finish_id))
    paint_ids = [ paint_id for paint_id, paint in _PaintsDataLoader.GetData().iteritems() if paint.finish == finish_id ]
    return paint_ids


def get_paint_ids_with_rarity(rarity_id):
    if rarity_id not in ALL_PAINT_RARITIES:
        raise ValueError("Invalid rarity ID '{0}'".format(rarity_id))
    paint_ids = [ paint_id for paint_id, paint in _PaintsDataLoader.GetData().iteritems() if paint.rarity == rarity_id ]
    return paint_ids


def get_paint_ids_with_hue_category(hue_category_id):
    _get_hue_category(hue_category_id)
    paint_ids = [ paint_id for paint_id, paint in _PaintsDataLoader.GetData().iteritems() if paint.hueCategory == hue_category_id ]
    return paint_ids


def get_paint_material_name(paint_id):
    return _get_paint(paint_id).materialName


def get_material_rgba(paint_id):
    material_name = get_paint_material_name(paint_id)
    material = trinity.Load('res:/dx9/model/SpaceObjectFactory/materials/{}.red'.format(material_name))
    return material.parameters[0].value


def get_paint_brand_name_id(paint_id):
    return _get_paint(paint_id).paintNameID


def get_paint_finish(paint_id):
    return _get_paint(paint_id).finish


def get_paint_rarity(paint_id):
    return _get_paint(paint_id).rarity


def get_paint_hue_category(paint_id):
    return _get_paint(paint_id).hueCategory


def _get_hue_category(hue_category_id):
    hue_category_data = _HueCategoriesDataLoader.GetData()
    try:
        return hue_category_data[hue_category_id]
    except KeyError:
        raise HueCategoryDoesNotExistError(hue_category_id)


def get_hue_category_ids():
    return _HueCategoriesDataLoader.GetData().keys()


def get_hue_category_message_id(hue_category_id):
    return _get_hue_category(hue_category_id).hueNameID


def get_hue_category_hue(hue_category_id):
    return _get_hue_category(hue_category_id).hue


class PaintDataError(StandardError):
    pass


class PaintDoesNotExistError(PaintDataError):

    def __init__(self, paint_id):
        self.paint_id = paint_id

    def __str__(self):
        return "Paint ID '{0}' does not exist".format(self.paint_id)


class HueCategoryDoesNotExistError(PaintDataError):

    def __init__(self, hue_category_id):
        self.hue_category_id = hue_category_id

    def __str__(self):
        return "Hue Category '{0}' does not exist".format(self.hue_category_id)
