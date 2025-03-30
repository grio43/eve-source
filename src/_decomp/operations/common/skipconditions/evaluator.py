#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\skipconditions\evaluator.py
from operations.common.skipconditions.items import *
from operations.common.skipconditions.navigation import *
from operations.common.skipconditions.ship import ConditionTargetsLocked
from operations.common.skipconditions.skills import *
from operations.common.skipconditions.ui import *
import logging
logger = logging.getLogger(__name__)
STRING_TO_CONDITION_OBJECT = {'skillPointsTotal': ConditionSkillPointsTotal(),
 'skillPointsFree': ConditionFreeSkillPoints(),
 'skillLevel': ConditionSkillLevel(),
 'skillTraining': ConditionSkillInQueue(),
 'windowOpen': ConditionWindowOpenWithExactName(),
 'windowOpenWithNameLike': ConditionWindowOpenWithNameLike(),
 'inSpace': ConditionInSpace(),
 'inStation': ConditionInStation(),
 'inStructure': ConditionInStructure(),
 'shipBoarded': ConditionShipBoarded(),
 'moduleTypeActive': ConditionModuleTypeActive(),
 'moduleGroupActive': ConditionModuleGroupActive(),
 'itemOwned': ConditionItemOwned(),
 'inCareerAgentStation': ConditionIsInCareerAgentStation(),
 'inCareerAgentSystem': ConditionIsInCareerAgentSystem(),
 'moduleCharged': ConditionModuleCharged(),
 'inRwSite': ConditionIsInRwSite(),
 'survivorsOwned': ConditionSurvivorOwned(),
 'agencyCardSelected': ConditionAgencyCardSelected(),
 'inProximity': ConditionInProximity(),
 'destinationSetToCareerAgent': ConditionDestinationSetToCareerAgent(),
 'itemInCargo': ConditionItemInCargo(),
 'itemInHangar': ConditionItemInHangar(),
 'itemFitted': ConditionItemFitted(),
 'freeTurretSlots': ConditionFreeTurretSlots(),
 'targetsLocked': ConditionTargetsLocked(),
 'agencyContentGroupOpened': ConditionAgencyContentGroupOpened()}

def _evaluate_condition(character_id, condition):
    condition_type = condition.skipCondition
    condition_object = STRING_TO_CONDITION_OBJECT.get(condition_type, None)
    if condition_object is None:
        logger.error('Condition "{condition_string}" does not have a corresponding condition object'.format(condition_string=condition_type))
        return
    return condition_object.Evaluate(character_id, condition)


def _evaluate_conditions(character_id, condition_list):
    for cond in condition_list:
        if _evaluate_condition(character_id, cond):
            return True

    return False


def evaluate_server_skip_conditions_for_task(character_id, operation_cache, task_id):
    task = operation_cache.get_task_by_id(task_id)
    return _evaluate_conditions(character_id, task.serverSkipConditions)


def evaluate_client_skip_conditions_for_task(character_id, operation_cache, task_id):
    task = operation_cache.get_task_by_id(task_id)
    return _evaluate_conditions(character_id, task.clientSkipConditions)


def has_client_skip_conditions(operation_cache, task_id):
    return bool(operation_cache.get_task_by_id(task_id).clientSkipConditions)
