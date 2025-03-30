#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\logistics.py
from behaviors.const.behaviorroles import ROLE_LOGISTIC
from behaviors.utility.dogmatic import self_has_effect, get_remote_repair_impedance
from behaviors.utility.roles import get_role_for_member, get_group_commander
from ccpProfile import TimedFunction
from dogma.attributes import health
from dogma.const import effectNpcBehaviorRemoteArmorRepairer, effectNpcBehaviorRemoteShieldBooster
LOGISTICS_PRIORITY_COMMANDER = 0.5
LOGISTICS_PRIORITY_LOGISTIC = 0.4
LOGISTICS_PRIORITY_MEMBER_WITH_ROLE = 0.2
LOGISTICS_PRIORITY_MEMBER_WITHOUT_ROLE = 0.1
LOGISTICS_PRIORITY_NON_MEMBER = 0.0

@TimedFunction('behaviors::utility::logistics::get_base_logistics_priority')
def get_base_logistics_priority(task, item_id):
    if task.IsMember(item_id):
        commander_id = get_group_commander(task)
        if item_id == commander_id:
            return LOGISTICS_PRIORITY_COMMANDER
        role = get_role_for_member(task, item_id)
        if role == ROLE_LOGISTIC:
            return LOGISTICS_PRIORITY_LOGISTIC
        elif role is not None:
            return LOGISTICS_PRIORITY_MEMBER_WITH_ROLE
        else:
            return LOGISTICS_PRIORITY_MEMBER_WITHOUT_ROLE
    return LOGISTICS_PRIORITY_NON_MEMBER


def get_damage_state_function(task):
    if self_has_effect(task, effectNpcBehaviorRemoteArmorRepairer):
        return health.GetCurrentArmorRatio
    if self_has_effect(task, effectNpcBehaviorRemoteShieldBooster):
        return health.GetCurrentShieldRatio


def get_remote_repair_effect_id(task):
    if self_has_effect(task, effectNpcBehaviorRemoteArmorRepairer):
        return effectNpcBehaviorRemoteArmorRepairer
    if self_has_effect(task, effectNpcBehaviorRemoteShieldBooster):
        return effectNpcBehaviorRemoteShieldBooster


def get_damage_state_function_by_effect_id(effect_id):
    if effect_id == effectNpcBehaviorRemoteArmorRepairer:
        return health.GetCurrentArmorRatio
    if effect_id == effectNpcBehaviorRemoteShieldBooster:
        return health.GetCurrentShieldRatio


@TimedFunction('behaviors::utility::logistics::get_damage_state_modifier')
def get_damage_state_modifier(task, item_id, get_damage_state):
    return 1.0 - get_damage_state(task.context.dogmaLM, item_id)


@TimedFunction('behaviors::utility::logistics::get_logistics_priority')
def get_logistics_priority(task, item_id, get_damage_state):
    base_priority = get_base_logistics_priority(task, item_id)
    damage_modifier = get_damage_state_modifier(task, item_id, get_damage_state)
    remote_repair_impedance = get_remote_repair_impedance(task, item_id)
    priority = (base_priority + damage_modifier) * remote_repair_impedance
    return priority
