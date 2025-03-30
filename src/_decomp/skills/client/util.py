#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\client\util.py
import collections
from carbon.common.script.sys.serviceManager import ServiceManager

def get_skill_service():
    return ServiceManager.Instance().GetService('skills')


def get_skill_queue_service():
    return ServiceManager.Instance().GetService('skillqueue')


def buy_and_train_skills(skills):
    skills_to_train = get_skills_to_train(skills)
    if buy_missing_skills(skills_to_train.keys()):
        skill_queue_service = get_skill_queue_service()
        skill_queue_service.AddSkillsToQueue(skills_to_train.items())


def buy_missing_skills(skill_type_ids):
    missing_skill_type_ids = filter(_is_skill_missing, skill_type_ids)
    if missing_skill_type_ids:
        skill_service = get_skill_service()
        bought_skills = skill_service.PurchaseSkills(missing_skill_type_ids)
        if not bought_skills:
            return False
        skill_service.WaitUntilSkillsAreAvailable(missing_skill_type_ids)
    return True


def get_skills_to_train(skills):
    result = collections.OrderedDict()
    skill_service = get_skill_service()
    for skill_type_id, level in skills.iteritems():
        if _is_skill_trained_or_training(skill_type_id, level):
            continue
        requirements = skill_service.GetSkillsMissingToUseItemRecursive(skill_type_id)
        for required_skill_type_id, required_level in requirements.iteritems():
            if _is_skill_trained_or_training(required_skill_type_id, required_level):
                continue
            result[required_skill_type_id] = max(result.get(required_skill_type_id, 0), required_level)

        result[skill_type_id] = max(result.get(skill_type_id, 0), level)

    return result


def _is_skill_missing(skill_type_id):
    skill_service = get_skill_service()
    skill = skill_service.GetSkillIncludingLapsed(skill_type_id)
    return skill is None or skill.trainedSkillLevel is None


def _is_skill_trained_or_training(skill_type_id, level):
    skill_service = get_skill_service()
    skill_level = skill_service.MySkillLevelIncludingQueued(skill_type_id)
    return skill_level >= level
