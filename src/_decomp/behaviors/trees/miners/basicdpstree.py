#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\miners\basicdpstree.py
from behaviors.actions import WaitAction
from behaviors.behaviortree import BehaviorTree
from behaviors.composites import PrioritySelector
from behaviors.const.behaviorroles import ROLE_DPS
from behaviors.trees.combat import CreateTargetSwitchingBehavior, CreateEntityCombatBehavior
from behaviors.trees.regroup import CreateReGroupBehavior
from behaviors.trees.reinforcements import CreateReinforceLocationBehavior
from behaviors.trees.role import CreateRegisterEntityRole
from behaviors.trees.unspawn import CreateUnspawnBehavior
from brennivin.itertoolsext import Bundle

def CreateBasicDpsBehaviorTree():
    root = PrioritySelector(Bundle(name='Basic Dps Tree'))
    root.AddSubTask(CreateRegisterEntityRole(ROLE_DPS))
    root.AddSubTask(CreateTargetSwitchingBehavior())
    root.AddSubTask(CreateEntityCombatBehavior())
    root.AddSubTask(CreateUnspawnBehavior())
    root.AddSubTask(CreateReinforceLocationBehavior())
    root.AddSubTask(CreateReGroupBehavior())
    root.AddSubTask(WaitAction(Bundle(name='Do nothing')))
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(root)
    return behaviorTree
