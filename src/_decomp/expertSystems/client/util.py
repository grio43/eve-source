#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\util.py
import functools
import urlparse
import evetypes
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.uicore import uicore
from eveexceptions import UserError
from journey.tracker import get_journey_id
import localization.util
from logmodule import LogException
from expertSystems import get_expert_system
from expertSystems.client.service import ExpertSystemService
from expertSystems.client.eventlogging.eventLoggers import event_logger
from skills.client.util import get_skill_service, buy_and_train_skills

def get_active_expert_systems_unlocking_type(type_id):
    skill_service = get_skill_service()
    expert_system_service = ExpertSystemService.instance()
    relevant_expert_systems = []
    for expert_system_id in expert_system_service.GetMyExpertSystems():
        expert_system = get_expert_system(expert_system_id)
        required_skills = skill_service.GetRequiredSkills(type_id)
        for skill_id, required_level in required_skills.iteritems():
            trained_level = skill_service.GetMyLevel(skill_id)
            provided_level = expert_system.skills.get(skill_id, 0)
            if required_level > provided_level or trained_level >= provided_level:
                break
        else:
            relevant_expert_systems.append(expert_system_id)

    return relevant_expert_systems


def is_unlocked_with_expert_system(type_id):
    return get_skill_service().IsUnlockedWithExpertSystem(type_id)


def expert_system_benefits_player(type_id):
    skill_service = get_skill_service()
    expert_system = get_expert_system(type_id)
    for skill_type_id in expert_system.skills:
        skill = skill_service.GetSkill(skill_type_id)
        if not skill or skill.trainedSkillLevel < expert_system.skills[skill_type_id]:
            return True

    return False


def browse_expert_systems(expert_system_type_id = None):
    try:
        sm = ServiceManager.Instance()
        typeIds = [expert_system_type_id] if expert_system_type_id else None
        sm.GetService('vgsService').OpenStore(categoryTag='expert system', typeIds=typeIds)
    except Exception:
        LogException('Failed to open new eden store to view expert system')
        raise UserError('FailedToOpenExpertSystemsInStore')

    event_logger.log_store_button_clicked()


def get_active_expert_systems_providing_skill(skill_type_id):
    return [ expert_system_type_id for expert_system_type_id in ExpertSystemService.instance().GetMyExpertSystems() if does_expert_system_provide_skill(expert_system_type_id, skill_type_id) ]


def does_expert_system_provide_skill(expert_system_type_id, skill_type_id):
    return any((granted_skill_type_id == skill_type_id for granted_skill_type_id in get_expert_system(expert_system_type_id).skills))


def get_sorted_expert_system_provided_skills(expert_system_type_id):
    expert_system = get_expert_system(expert_system_type_id)
    skill_service = get_skill_service()
    skills = []
    for skill_type_id, level in expert_system.skills.iteritems():
        skill = skill_service.GetSkill(skill_type_id)
        if skill is None or not skill.trainedSkillLevel:
            order = 0
        elif skill.trainedSkillLevel < level:
            order = 1
        else:
            order = 2
        name = get_localized_sort_key(evetypes.GetName(skill_type_id))
        skills.append(((order, name), skill_type_id))

    return [ skill_type_id for _, skill_type_id in sorted(skills, key=lambda x: x[0]) ]


def get_localized_sort_key(text):
    localized_cmp = localization.util.GetSortFunc(localization.util.GetLanguageID())
    localized_key = functools.cmp_to_key(localized_cmp)
    return localized_key(text)


def sorted_by_name(expert_systems):
    return sorted(expert_systems, key=lambda expert_system: get_localized_sort_key(expert_system.name))


def train_expert_system_skills(expert_system_type_id):
    skills = get_expert_system(expert_system_type_id).skills
    buy_and_train_skills(skills)
