#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\sleeperscouts.py
from behaviors import composites
from behaviors.actions.combatnavigation import DEFAULT_COMBAT_ORBIT_RANGE, DEFAULT_COMBAT_ATTACK_RANGE
from behaviors.behaviortree import BehaviorTree
from behaviors.trees.harvesting import CreateHarvestOutpostBehavior
from behaviors.trees.incursions.const import DRIFTER_OWNERS
from behaviors.trees.pursuit import CreatePursuitBehavior
from behaviors.trees.regroup import CreateReGroupBehavior
from behaviors.trees.reinforcements import CreateRequestReinforcements
from behaviors.trees.scoutsidle import CreateIdleBehavior
from behaviors.trees.scoutexplore import CreateExplorationBehavior
from behaviors.trees.combat import CreateCombatBehavior, CreateFriendlyTargetFilterBehavior
from behaviors.trees.corpseharvesting import CreateCorpseHarvestingBehavior
from behaviors.trees.corpsedisposal import CreateCorpseDisposalBehavior
from brennivin.itertoolsext import Bundle
COMBAT_ORBIT_VELOCITY = 600

def CreateSleeperScoutBehaviorTree():
    root = composites.PrioritySelector(Bundle(name='Sleeper Scout Root'))
    root.AddSubTask(CreateRequestReinforcements())
    root.AddSubTask(CreateFriendlyTargetFilterBehavior(DRIFTER_OWNERS))
    root.AddSubTask(CreateCombatBehavior(orbitVelocity=COMBAT_ORBIT_VELOCITY, orbitRange=DEFAULT_COMBAT_ORBIT_RANGE, attackRange=DEFAULT_COMBAT_ATTACK_RANGE))
    root.AddSubTask(CreateReGroupBehavior())
    root.AddSubTask(CreatePursuitBehavior())
    root.AddSubTask(CreateCorpseHarvestingBehavior())
    root.AddSubTask(CreateCorpseDisposalBehavior())
    root.AddSubTask(CreateExplorationBehavior())
    root.AddSubTask(CreateHarvestOutpostBehavior())
    root.AddSubTask(CreateIdleBehavior())
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(root)
    return behaviorTree


def CreateHiveSystemSleeperScoutBehaviorTree():
    root = composites.PrioritySelector(Bundle(name='Sleeper Scout Root'))
    root.AddSubTask(CreateRequestReinforcements())
    root.AddSubTask(CreateFriendlyTargetFilterBehavior(DRIFTER_OWNERS))
    root.AddSubTask(CreateCombatBehavior(orbitVelocity=COMBAT_ORBIT_VELOCITY, orbitRange=DEFAULT_COMBAT_ORBIT_RANGE, attackRange=DEFAULT_COMBAT_ATTACK_RANGE))
    root.AddSubTask(CreateReGroupBehavior())
    root.AddSubTask(CreateCorpseHarvestingBehavior())
    root.AddSubTask(CreateExplorationBehavior())
    root.AddSubTask(CreateIdleBehavior())
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(root)
    return behaviorTree
