#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\sequencing_util.py
from cosmetics.common.ships.skins.static_data import sequencing_const

def get_maximum_runs_per_job(get_skill_level_method):
    total = sequencing_const.max_runs_default
    for type_id, values in sequencing_const.max_runs_added_by_skill_and_level.iteritems():
        skill_level = get_skill_level_method(type_id)
        if skill_level:
            for i in range(1, skill_level + 1):
                total += values[i]

    return total


def get_maximum_concurrent_sequencing_jobs(get_skill_level_method):
    total = sequencing_const.max_concurrent_jobs_default
    for type_id, values in sequencing_const.max_concurrent_jobs_added_by_skill_and_level.iteritems():
        skill_level = get_skill_level_method(type_id)
        if skill_level:
            for i in range(1, skill_level + 1):
                total += values[i]

    return total


def get_sequencing_duration_bonus(get_skill_level_method):
    bonus = 0.0
    for type_id in sequencing_const.sequencing_time_bonus_skills:
        skill_level = get_skill_level_method(type_id)
        if skill_level:
            for i in range(1, skill_level + 1):
                bonus += sequencing_const.sequencing_time_bonus_by_skill_and_level[type_id][i]

    return bonus


def get_sequencing_duration_bonus_percentage(get_skill_level_method):
    return int(get_sequencing_duration_bonus(get_skill_level_method) * 100.0)


def build_component_licenses_per_type_dict(licenses):
    licenses_dict = {}
    for license in licenses:
        if license is not None:
            if license.component_id not in licenses_dict:
                licenses_dict[license.component_id] = {}
            licenses_dict[license.component_id][license.license_type] = license

    return licenses_dict
