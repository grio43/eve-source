#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\static_data\component_point_value.py
from cosmetics.common.ships.skins.static_data.component_category import get_category_from_fsd
from cosmetics.common.ships.skins.static_data.component_rarity import get_rarity_from_fsd
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import ship_skin_design_component_point_valuesLoader
except ImportError:
    ship_skin_design_component_point_valuesLoader = None

class _ComponentPointValuesDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/ship_skin_design_component_point_values.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/ship_skin_design_component_point_values.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/ship_skin_design_component_point_values.fsdbinary'
    __loader__ = ship_skin_design_component_point_valuesLoader


def get_component_point_values_data():
    return _ComponentPointValuesDataLoader.GetData()


class ComponentPointValuesTable(object):

    def __init__(self):
        self._table = {}
        self._load_from_fsd(get_component_point_values_data())

    def _load_from_fsd(self, fsd_data):
        for component_category, values in fsd_data.iteritems():
            key = get_category_from_fsd(component_category)
            self._table[key] = {}
            for rarity, points in values.iteritems():
                self._table[key][get_rarity_from_fsd(rarity)] = points

    def get_point_value(self, component_category, component_rarity):
        if component_category in self._table:
            if component_rarity in self._table[component_category]:
                return self._table[component_category][component_rarity]
