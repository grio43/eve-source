#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\incursions\roamingdriftertree.py
from behaviors import composites
from behaviors.actions import WaitAction
from behaviors.actions.combatnavigation import DEFAULT_COMBAT_ORBIT_RANGE, DEFAULT_COMBAT_ATTACK_RANGE
from behaviors.behaviortree import BehaviorTree
from behaviors.trees.combat import CreateTargetSwitchingBehavior, CreateEntityCombatBehavior
from behaviors.trees.drifters.superweapon import CreateSuperWeaponBehavior
from behaviors.trees.incursions.const import ROAMING_SITE_GROUP_IDS
from behaviors.trees.regroup import CreateReGroupBehavior
from behaviors.trees.explore import CreateExplorationBehavior
from brennivin.itertoolsext import Bundle
COMBAT_ORBIT_VELOCITY = 1500

def CreateRoamingDrifterBehaviorTree():
    root = composites.PrioritySelector(Bundle(name='Roaming Drifter Root'))
    root.AddSubTask(CreateSuperWeaponBehavior())
    root.AddSubTask(CreateTargetSwitchingBehavior())
    root.AddSubTask(CreateEntityCombatBehavior(orbitVelocity=COMBAT_ORBIT_VELOCITY, orbitRange=DEFAULT_COMBAT_ORBIT_RANGE, attackRange=DEFAULT_COMBAT_ATTACK_RANGE))
    root.AddSubTask(CreateReGroupBehavior())
    root.AddSubTask(CreateExplorationBehavior(groupsOfInterest=ROAMING_SITE_GROUP_IDS, explorationIntervalSeconds=570))
    root.AddSubTask(WaitAction(Bundle(name='Do nothing')))
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(root)
    return behaviorTree
