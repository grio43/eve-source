#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\util.py
from caching.memoize import Memoize
from cluster import SERVICE_CHARACTER
from eve.common.lib.appConst import CHARNODE_MOD
from eve.common.script.sys.idCheckers import IsCharacter
from eveprefs import boot
from operations.common.const import CategoryState, OperationState, TaskState, OPERATION_CATEGORY_TUTORIAL_AIR_NPE, OPERATION_CATEGORY_TUTORIAL_BNNPE_COMBAT, BNNPE_CATEGORIES

def is_category_locked(node_state):
    return node_state in (CategoryState.LOCKED,)


def is_category_active(node_state):
    return node_state in (CategoryState.ACTIVE,)


def is_category_skipped(node_state):
    return node_state in (CategoryState.SKIPPED_BY_PLAYER,
     CategoryState.SKIPPED_BY_INCEPTION,
     CategoryState.SKIPPED_BY_ACHIEVEMENTS,
     CategoryState.SKIPPED_BY_AGE,
     CategoryState.SKIPPED_BY_BNNPE_TERMINATION)


def is_category_complete(node_state):
    return node_state in (CategoryState.COMPLETE,)


def is_category_finished(node_state):
    return is_category_complete(node_state) or is_category_skipped(node_state)


def is_operation_locked(node_state):
    return node_state == OperationState.LOCKED


def is_operation_active(node_state):
    return node_state in (OperationState.ACTIVE, OperationState.AVAILABLE, OperationState.REACTIVATED)


def is_operation_finished(node_state):
    return node_state == OperationState.COMPLETE


def is_task_locked(node_state):
    return node_state == TaskState.LOCKED


def is_task_blocked(node_state):
    return node_state == TaskState.BLOCKED


def is_task_active(node_state):
    return node_state == TaskState.ACTIVE


def is_task_completable(node_state):
    return node_state in (TaskState.ACTIVE, TaskState.BLOCKED)


def is_task_finished(node_state):
    return node_state in (TaskState.COMPLETE, TaskState.SKIPPED)


def get_service(service, character_id):
    if boot.role == 'server':
        machoNet = sm.GetService('machoNet')
        node_id = machoNet.GetNodeFromAddress(SERVICE_CHARACTER, character_id % CHARNODE_MOD)
        return machoNet.session.ConnectToRemoteService(service, nodeID=node_id)
    if boot.role == 'client':
        return sm.RemoteSvc(service)


def is_character_eligible_for_operation(character_id):
    if character_id is None or not IsCharacter(character_id):
        return False
    return is_npe_enabled_for_character(character_id)


@Memoize
def is_npe_enabled_for_character(character_id):
    if character_id is None or not IsCharacter(character_id):
        return False
    operations_manager = get_service('operationsManager', character_id)
    if operations_manager:
        return operations_manager.can_character_play_the_tutorial(character_id)
    return False


def is_operation_restricted_to_newbie_systems(operation_id, operation_cache):
    return operation_cache.is_operation_in_category(get_tutorial_category_id(), operation_id)


def are_operation_prerequisites_met(category_id, operation_id, operations_cache, has_operation_ever_been_completed):
    operation = operations_cache.get_operation_by_id(operation_id)
    required_operation_id = operation.operationPrerequisites
    if required_operation_id is None:
        return True
    return has_operation_ever_been_completed(category_id, required_operation_id)


def get_tutorial_category_id():
    return OPERATION_CATEGORY_TUTORIAL_AIR_NPE


def get_bnnpe_category_ids():
    return BNNPE_CATEGORIES
