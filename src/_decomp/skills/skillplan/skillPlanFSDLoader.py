#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\skillPlanFSDLoader.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import skillPlansLoader
except ImportError:
    skillPlansLoader = None

class SkillPlanLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/skillPlans.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/skillPlans.fsdbinary'
    __loader__ = skillPlansLoader


def get_skill_plans():
    return SkillPlanLoader.GetData()


def iter_skill_plans():
    for skill_plan_id, skill_plan in get_skill_plans().iteritems():
        yield (skill_plan_id, skill_plan)


def get_skill_plan_name(skill_plan_id):
    skill_plan = get_skill_plans().get(skill_plan_id, None)
    if skill_plan:
        return skill_plan.name


def get_skill_plan_faction(skill_plan_id):
    skill_plan = get_skill_plans().get(skill_plan_id, None)
    if skill_plan:
        return skill_plan.factionID


def get_skill_plan_career_path(skill_plan_id):
    skill_plan = get_skill_plans().get(skill_plan_id, None)
    if skill_plan:
        return skill_plan.careerPathID


def get_skill_plan_division(skill_plan_id):
    skill_plan = get_skill_plans().get(skill_plan_id, None)
    if skill_plan:
        return skill_plan.npcCorporationDivision


def get_skill_plan_by_parameters(faction_id = None, career_path_id = None, division_id = None):
    for skill_plan_id, skill_plan in iter_skill_plans():
        if faction_id is not None and skill_plan.factionID != faction_id:
            continue
        if career_path_id is not None and skill_plan.careerPathID != career_path_id:
            continue
        if division_id is not None and skill_plan.npcCorporationDivision != division_id:
            continue
        return skill_plan_id
