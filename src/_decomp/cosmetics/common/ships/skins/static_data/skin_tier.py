#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\static_data\skin_tier.py
import shipgroup
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import ship_skin_design_tier_thresholdsLoader
except ImportError:
    ship_skin_design_tier_thresholdsLoader = None

class _ShipSkinTierThresholdsDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/ship_skin_design_tier_thresholds.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/ship_skin_design_tier_thresholds.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/ship_skin_design_tier_thresholds.fsdbinary'
    __loader__ = ship_skin_design_tier_thresholdsLoader


def get_tier_thresholds_data():
    return _ShipSkinTierThresholdsDataLoader.GetData()


class ShipSkinTierThresholdsSet(object):

    def __init__(self, info_group_id, thresholds_per_tier_level):
        self._info_group_id = info_group_id
        self._thresholds = []
        self._build_thresholds_list(thresholds_per_tier_level)

    def _build_thresholds_list(self, thresholds_per_tier_level):
        max_tier = max(thresholds_per_tier_level.keys()) + 1
        self._thresholds.append(0)
        for tier_level in range(1, max_tier):
            if tier_level not in thresholds_per_tier_level:
                raise Exception('The list of SKIN tier thresholds for info group id %s is missing a value for tier %s' % (self._info_group_id, tier_level))
            self._thresholds.append(thresholds_per_tier_level[tier_level])

        previous = -1
        for x in self._thresholds:
            if x <= previous:
                raise Exception('The list of SKIN tier thresholds for info group id %s is not strictly ascending' % self._info_group_id)
            previous = x

    def get_tier_level(self, points_value):
        if points_value > self._thresholds[-1]:
            return self.get_max_tier()
        if self.get_max_tier() <= 1 or points_value <= self._thresholds[1]:
            return 1
        for tier_level in range(2, len(self._thresholds)):
            if self._thresholds[tier_level - 1] < points_value <= self._thresholds[tier_level]:
                return tier_level

    def get_max_tier(self):
        return len(self._thresholds)

    def get_threshold_for_tier(self, tier_level):
        if tier_level < 0:
            tier_level = 0
        if tier_level >= self.get_max_tier():
            return None
        return self._thresholds[tier_level]


class ShipSkinTierTable(object):

    def __init__(self):
        self._tier_thresholds_sets = None

    @property
    def tier_thresholds_sets(self):
        if self._tier_thresholds_sets is None:
            self._load_thresholds()
        return self._tier_thresholds_sets

    def _load_thresholds(self):
        self._tier_thresholds_sets = {}
        fsd_data = get_tier_thresholds_data()
        for info_group_id, thresholds in fsd_data.iteritems():
            self._tier_thresholds_sets[info_group_id] = ShipSkinTierThresholdsSet(info_group_id, thresholds)

    def get_thresholds_for_ship_type(self, ship_type_id):
        ship_group_id = shipgroup.get_ship_group_id(ship_type_id)
        if ship_group_id is None:
            return
        return self.tier_thresholds_sets.get(ship_group_id, None)

    def get_tier_level_for_design(self, skin_design):
        return self.get_tier_level(skin_design.ship_type_id, skin_design.compute_current_points_value())

    def get_tier_level(self, ship_type_id, points_value):
        thresholds_set = self.get_thresholds_for_ship_type(ship_type_id)
        if thresholds_set is None:
            return 1
        return thresholds_set.get_tier_level(points_value)
