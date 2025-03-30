#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\miners\tackler.py
from behaviors.actions import WaitAction
from behaviors.behaviortree import BehaviorTree
from behaviors.composites import PrioritySelector
from behaviors.const.behaviorroles import ROLE_TACKLER
from behaviors.const.blackboardchannels import MY_COMBAT_TARGET
from behaviors.trees.combat import CreateTargetSwitchingBehavior, TARGET_SWITCH_TIMER, CreateEntityCombatBehavior
from behaviors.trees.regroup import CreateReGroupBehavior
from behaviors.trees.reinforcements import CreateReinforceLocationBehavior
from behaviors.trees.role import CreateRegisterEntityRole
from behaviors.trees.unspawn import CreateUnspawnBehavior
from brennivin.itertoolsext import Bundle

def CreateTacklerBehaviorTree():
    root = PrioritySelector(Bundle(name='Tackler Tree'))
    root.AddSubTask(CreateRegisterEntityRole(ROLE_TACKLER))
    root.AddSubTask(CreateTargetSwitchingBehavior(targetAddress=MY_COMBAT_TARGET, targetSwitchTimerAddress=TARGET_SWITCH_TIMER))
    root.AddSubTask(CreateEntityCombatBehavior(targetAddress=MY_COMBAT_TARGET))
    root.AddSubTask(CreateUnspawnBehavior())
    root.AddSubTask(CreateReinforceLocationBehavior())
    root.AddSubTask(CreateReGroupBehavior())
    root.AddSubTask(WaitAction(Bundle(name='Do nothing')))
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(root)
    return behaviorTree
