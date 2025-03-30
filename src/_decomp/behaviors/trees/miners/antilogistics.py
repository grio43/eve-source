#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\miners\antilogistics.py
from behaviors.actions import WaitAction
from behaviors.behaviortree import BehaviorTree
from behaviors.composites import PrioritySelector
from behaviors.const.behaviorroles import ROLE_ANTI_LOGISTIC
from behaviors.const.blackboardchannels import MY_COMBAT_TARGET
from behaviors.const.combat import FITTED_MODULE_GROUP_TARGET_EVALUATOR
from behaviors.trees.combat import CreateTargetSwitchingBehavior, CreateEntityCombatBehavior, TARGET_SWITCH_TIMER
from behaviors.trees.regroup import CreateReGroupBehavior
from behaviors.trees.reinforcements import CreateReinforceLocationBehavior
from behaviors.trees.role import CreateRegisterEntityRole
from behaviors.trees.unspawn import CreateUnspawnBehavior
from brennivin.itertoolsext import Bundle
from inventorycommon.const import groupEnergyTransferArray, groupFueledRemoteShieldBooster, groupRemoteHullRepairer
from inventorycommon.const import groupFueledRemoteArmorRepairer, groupArmorRepairProjector, groupShieldTransporter
ANTI_LOGISTICS_PREFERRED_MODULE_GROUPS = [groupShieldTransporter,
 groupArmorRepairProjector,
 groupFueledRemoteArmorRepairer,
 groupFueledRemoteShieldBooster,
 groupRemoteHullRepairer,
 groupEnergyTransferArray]

def CreateAntiLogisticsBehaviorTree():
    root = PrioritySelector(Bundle(name='Anti-Logistics Tree'))
    root.AddSubTask(CreateRegisterEntityRole(ROLE_ANTI_LOGISTIC))
    root.AddSubTask(CreateTargetSwitchingBehavior(targetAddress=MY_COMBAT_TARGET, targetSwitchTimerAddress=TARGET_SWITCH_TIMER, targetEvaluationFunction=FITTED_MODULE_GROUP_TARGET_EVALUATOR, preferredModuleGroups=ANTI_LOGISTICS_PREFERRED_MODULE_GROUPS))
    root.AddSubTask(CreateEntityCombatBehavior(targetAddress=MY_COMBAT_TARGET, targetEvaluationFunction=FITTED_MODULE_GROUP_TARGET_EVALUATOR, preferredModuleGroups=ANTI_LOGISTICS_PREFERRED_MODULE_GROUPS))
    root.AddSubTask(CreateUnspawnBehavior())
    root.AddSubTask(CreateReinforceLocationBehavior())
    root.AddSubTask(CreateReGroupBehavior())
    root.AddSubTask(WaitAction(Bundle(name='Do nothing')))
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(root)
    return behaviorTree
