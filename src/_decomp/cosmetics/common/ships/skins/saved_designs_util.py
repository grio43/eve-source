#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\saved_designs_util.py
from cosmetics.common.ships.skins.static_data import saved_designs_const

def get_maximum_saved_designs(get_skill_level_method):
    total = 0
    for type_id, values in saved_designs_const.max_saved_designs_added_by_skill_and_level.iteritems():
        skill_level = get_skill_level_method(type_id)
        if skill_level:
            for i in range(1, skill_level + 1):
                total += values[i]

    return total
