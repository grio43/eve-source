#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\drifters\driftertree.py
from behaviors import composites
from behaviors.actions.combatnavigation import DEFAULT_COMBAT_ORBIT_RANGE, DEFAULT_COMBAT_ATTACK_RANGE
from behaviors.behaviortree import BehaviorTree
from behaviors.trees.combat import CreateCombatBehavior, CreateTargetSwitchingBehavior, CreateFriendlyTargetFilterBehavior
from behaviors.trees.drifters.drifter_aggression import CreateDrifterEntosisAggressionBehavior
from behaviors.trees.explore import CreateExplorationBehavior
from behaviors.trees.drifters.idle import CreateIdleBehavior
from behaviors.trees.harvesting import CreateHarvestOutpostBehavior
from behaviors.trees.incursions.const import DRIFTER_OWNERS
from behaviors.trees.pursuit import CreatePursuitBehavior
from behaviors.trees.regroup import CreateReGroupBehavior
from behaviors.trees.reinforcements import CreateRequestReinforcements
from behaviors.trees.drifters.superweapon import CreateSuperWeaponBehavior
from behaviors.trees.drifters.disappear import CreateDisappearBehavior
from behaviors.trees.corpseharvesting import CreateCorpseHarvestingBehavior
from behaviors.trees.corpsedisposal import CreateCorpseDisposalBehavior
from brennivin.itertoolsext import Bundle
LANDMARK_ARCHETYPE = 2
DUNGEON_WORMHOLE = 5643
UNIDENTIFIED_STRUCTURE = 5610
COMBAT_ORBIT_VELOCITY = 1500

def CreateDrifterBehaviorTree():
    root = composites.PrioritySelector(Bundle(name='Drifter Root'))
    root.AddSubTask(CreateRequestReinforcements())
    root.AddSubTask(CreateSuperWeaponBehavior())
    root.AddSubTask(CreateTargetSwitchingBehavior())
    root.AddSubTask(CreateDrifterEntosisAggressionBehavior())
    root.AddSubTask(CreateFriendlyTargetFilterBehavior(DRIFTER_OWNERS))
    root.AddSubTask(CreateCombatBehavior(orbitVelocity=COMBAT_ORBIT_VELOCITY, orbitRange=DEFAULT_COMBAT_ORBIT_RANGE, attackRange=DEFAULT_COMBAT_ATTACK_RANGE))
    root.AddSubTask(CreateReGroupBehavior())
    root.AddSubTask(CreatePursuitBehavior())
    root.AddSubTask(CreateCorpseHarvestingBehavior())
    root.AddSubTask(CreateCorpseDisposalBehavior())
    root.AddSubTask(CreateExplorationBehavior(dungeonArchetypesOfInterest=[LANDMARK_ARCHETYPE], dungeonsOfInterest=[DUNGEON_WORMHOLE, UNIDENTIFIED_STRUCTURE]))
    root.AddSubTask(CreateDisappearBehavior())
    root.AddSubTask(CreateHarvestOutpostBehavior())
    root.AddSubTask(CreateIdleBehavior())
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(root)
    return behaviorTree


def CreateHiveSystemDrifterBehaviorTree():
    root = composites.PrioritySelector(Bundle(name='Drifter Root'))
    root.AddSubTask(CreateRequestReinforcements())
    root.AddSubTask(CreateSuperWeaponBehavior())
    root.AddSubTask(CreateTargetSwitchingBehavior())
    root.AddSubTask(CreateFriendlyTargetFilterBehavior(DRIFTER_OWNERS))
    root.AddSubTask(CreateCombatBehavior(orbitVelocity=COMBAT_ORBIT_VELOCITY, orbitRange=DEFAULT_COMBAT_ORBIT_RANGE, attackRange=DEFAULT_COMBAT_ATTACK_RANGE))
    root.AddSubTask(CreateReGroupBehavior())
    root.AddSubTask(CreateCorpseHarvestingBehavior())
    root.AddSubTask(CreateExplorationBehavior(dungeonArchetypesOfInterest=[LANDMARK_ARCHETYPE], dungeonsOfInterest=[DUNGEON_WORMHOLE, UNIDENTIFIED_STRUCTURE]))
    root.AddSubTask(CreateIdleBehavior())
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(root)
    return behaviorTree
