#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\dogmatic.py
import uthread2
from behaviors.utility.inventory import get_type_id_by_item_id
from ccpProfile import TimedFunction
import logging
from behaviors.utility.ballparks import is_ball_in_range
from behaviors.utility.owner import get_owner_id
from carbon.common.lib.const import SECONDS_IN_MILLISECOND
from dogma.const import attributeDisallowAssistance, attributeRemoteRepairImpedance, attributeExplosionDelay
from dogma.const import effecttargetABCAttack
from dogma.const import attributeEntityMissileTypeID, attributeMissileEntityVelocityMultiplier, attributeMissileEntityFlightTimeMultiplier
from dogma.const import attributeMaxVelocity
from dogma.effects.restricted.util import get_effect_range_falloff_modifier_at_distance
from eveexceptions import UserError
logger = logging.getLogger(__name__)

def get_my_attribute_value(task, attribute_id):
    return get_attribute_value(task, task.context.myItemId, attribute_id)


@TimedFunction('behaviors::utility::dogmatic::get_attribute_value')
def get_attribute_value(task, item_id, attribute_id):
    return task.context.dogmaLM.GetAttributeValue(item_id, attribute_id)


def get_my_type_attribute_value(task, attribute_id):
    return get_type_attribute_value(task, task.context.mySlimItem.typeID, attribute_id)


@TimedFunction('behaviors::utility::dogmatic::get_type_attribute_value')
def get_type_attribute_value(task, type_id, attribute_id):
    return task.context.dogmaLM.dogmaStaticMgr.GetTypeAttribute2(type_id, attribute_id)


def type_has_effect(task, type_id, effect_id):
    return task.context.dogmaLM.dogmaStaticMgr.TypeHasEffect(type_id, effect_id)


def self_has_effect(task, effect_id):
    return type_has_effect(task, task.context.mySlimItem.typeID, effect_id)


def is_effect_active(task, item_id, effect_id):
    return task.context.dogmaLM.GetActiveEffectData(item_id, effect_id) is not None


def is_my_effect_active(task, effect_id):
    return is_effect_active(task, task.context.myItemId, effect_id)


@TimedFunction('behaviors::utility::dogmatic::is_my_effect_active_on_target')
def is_my_effect_active_on_target(task, effect_id, target_id):
    effect_environment = task.context.dogmaLM.GetActiveEffectEnvironment(task.context.myItemId, effect_id)
    if effect_environment is None:
        return False
    return effect_environment.targetID == target_id


def get_my_locked_targets(task):
    return task.context.dogmaLM.GetTargets(task.context.myItemId)


@TimedFunction('behaviors::utility::dogmatic::try_activate_effect')
def try_activate_effect(task, effect_id, repeats, target_id = None, context = None, module_id = None, cycles = 0, delay = 0):
    module_id = module_id or task.context.myItemId
    owner_id = get_owner_id(task)
    try:
        if cycles > 0:
            uthread2.start_tasklet(stop_effect, task, effect_id, module_id, cycles)
        if delay > 0:
            uthread2.sleep(delay)
        task.context.dogmaLM.ActivateWithContext(owner_id, module_id, effect_id, targetid=target_id, repeat=repeats, context=context)
        logger.debug('try_activate_effect: entity=%s started effect=%s on target=%s', module_id, effect_id, target_id)
    except UserError as e:
        logger.debug('try_activate_effect: entity=%s failed effect=%s due to UserError=%s', module_id, effect_id, e)
    except ReferenceError:
        logger.debug('try_activate_effect: entity=%s failed effect=%s due to ReferenceError, it most likely died while sleeping', module_id, effect_id)
    except RuntimeError as e:
        logger.exception('try_activate_effect: entity=%s failed effect=%s due to RuntimeError=%s', module_id, effect_id, e)


def stop_effect(task, effect_id, module_id, cycles):
    if effect_id is None:
        module_type_id = get_type_id_by_item_id(task, module_id)
        effect_id = task.context.dogmaLM.dogmaStaticMgr.GetDefaultEffect(module_type_id)
    if module_id is None:
        module_id = task.context.myItemId
    effect = task.context.dogmaLM.dogmaStaticMgr.GetEffect(effect_id)
    duration_attribute_id = effect.durationAttributeID
    single_cycle_duration = task.context.dogmaLM.GetAttributeValue(module_id, duration_attribute_id)
    seconds_until_stop = single_cycle_duration * cycles / 1000.0
    logger.debug('behavior::dogmatic::stop_effect: entity=%s shutting down module=%s with effect=%s after cycles=%s and duration=%s', task.context.myItemId, module_id, effect_id, cycles, seconds_until_stop)
    uthread2.SleepSim(seconds_until_stop)
    try:
        bool(task.context)
    except ReferenceError:
        return

    try:
        task.context.dogmaLM.StopEffect(effect_id, module_id, forceStopRepeating=True)
    except UserError:
        pass

    task.behaviorTree.RequestReset(requestedBy=task)
    logger.debug('behavior::dogmatic::stop_effect: entity=%s stopped using module=%s with effect=%s', task.context.myItemId, module_id, effect_id)


def _get_single_cycle_duration_for_module_or_effect(task, effect_id, module_id):
    effect = task.context.dogmaLM.dogmaStaticMgr.GetEffect(effect_id)
    duration_attribute_id = effect.durationAttributeID
    return task.context.dogmaLM.GetAttributeValue(module_id, duration_attribute_id)


def is_assistance_disallowed(task, item_id):
    return get_attribute_value(task, item_id, attributeDisallowAssistance) > 0


def get_remote_repair_impedance(task, item_id):
    return get_attribute_value(task, item_id, attributeRemoteRepairImpedance)


@TimedFunction('behaviors::utility::dogmatic::get_range_falloff_multiplier_at_distance')
def get_range_falloff_multiplier_at_distance(task, effect_id, distance):
    source_id = task.context.myItemId
    return get_effect_range_falloff_modifier_at_distance(task.context.dogmaLM, effect_id, source_id, distance)


def get_default_effect_id_for_type(task, type_id):
    return task.context.dogmaLM.dogmaStaticMgr.GetDefaultEffect(type_id)


def can_activate_effect_on_target(task, type_id, effect_id, target_id):
    if effect_id not in task.context.ballpark.dogmaLM.dogmaStaticMgr.effects:
        return False
    if not task.context.ballpark.dogmaLM.dogmaStaticMgr.TypeHasEffect(type_id, effect_id):
        return False
    effect = task.context.ballpark.dogmaLM.dogmaStaticMgr.effects[effect_id]
    if not effect.falloffAttributeID and effect.rangeAttributeID is not None and effect_id != effecttargetABCAttack:
        effect_range = get_my_attribute_value(task, effect.rangeAttributeID)
        return is_ball_in_range(task, task.context.myItemId, target_id, effect_range)
    return True


def get_entity_max_missile_range(task, type_id):
    missile_type_id = get_type_attribute_value(task, type_id, attributeEntityMissileTypeID)
    missile_base_velocity = get_type_attribute_value(task, missile_type_id, attributeMaxVelocity)
    missile_explosion_delay = get_type_attribute_value(task, missile_type_id, attributeExplosionDelay)
    velocity_multiplier = get_type_attribute_value(task, type_id, attributeMissileEntityVelocityMultiplier)
    flight_time_multiplier = get_type_attribute_value(task, type_id, attributeMissileEntityFlightTimeMultiplier)
    missile_velocity = missile_base_velocity * flight_time_multiplier
    flight_time = missile_explosion_delay * velocity_multiplier * SECONDS_IN_MILLISECOND
    return missile_velocity * flight_time


def get_dogma_lm(task):
    return task.context.dogmaLM


def is_module_fitted_from_group_id_set(task, item_id, group_id_set):
    fitted_module_group_ids = get_dogma_lm(task).GetFittedModulesGroupIdsForShip(item_id)
    return not group_id_set.isdisjoint(fitted_module_group_ids)


def try_stop_effect(task, effect_id, forced = False):
    try:
        task.context.dogmaLM.StopEffect(effect_id, task.context.myItemId, forced=forced)
        logger.debug('Behavior=%s stopped effect=%s', task.context.myItemId, effect_id)
    except UserError:
        pass


def remove_my_target(task, target_id):
    task.context.dogmaLM.RemoveTarget(task.context.myItemId, target_id)
