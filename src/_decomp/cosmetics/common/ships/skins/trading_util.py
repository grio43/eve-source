#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\trading_util.py
from cosmetics.common.ships.skins.static_data import trading_const

def get_maximum_concurrent_skin_listings(get_skill_level_method):
    total = trading_const.max_concurrent_listings_default
    for type_id, values in trading_const.max_concurrent_listings_added_by_skill_and_level.iteritems():
        skill_level = get_skill_level_method(type_id)
        if skill_level:
            for i in range(1, skill_level + 1):
                total += values[i]

    return total


def get_tax_reduction_percentage(get_skill_level_method):
    total = 0
    for type_id, values in trading_const.tax_rate_percent_reduction_per_level.iteritems():
        skill_level = get_skill_level_method(type_id)
        if skill_level:
            for i in range(1, skill_level + 1):
                total += values[i]

    return total
