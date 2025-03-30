#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\pirate\shadow_of_the_serpent_trees.py
from behaviors import composites
from behaviors.actions import WaitAction
from behaviors.actions.combatnavigation import DEFAULT_COMBAT_ORBIT_RANGE, DEFAULT_COMBAT_ATTACK_RANGE
from behaviors.behaviortree import BehaviorTree
from behaviors.composites import Sequence
from behaviors.decorators.modifiers import ForceSuccess
from behaviors.monitors.blackboards import BlackboardMessageMonitor
from behaviors.monitors.groups import GroupMembershipMonitor
from behaviors.monitors.navigation import GroupMemberWarpModeChangedMonitor
from behaviors.trees.combat import CreateTargetSwitchingBehavior, CreateEntityCombatBehavior, COMBAT_TARGETS_SET
from behaviors.trees.groups.combat import CreateManageTargetCombatSetBehavior
from behaviors.trees.groups.threatManagement import CreateThreatManagementBehavior
from behaviors.trees.patrol import CreatePatrolBehavior, CreateIdleFallback
from behaviors.trees.regroup import CreateReGroupBehavior
from behaviors.trees.explore import CreateExplorationBehavior
from behaviors.trees.reinforcements import CreateRequestReinforcements
from behaviors.trees.tanking import CreateTankingBehavior
from brennivin.itertoolsext import Bundle
from inventorycommon.const import groupStargate, groupAsteroidBelt
PRUNE_TIMEOUT_SECONDS = 120
COMBAT_ORBIT_VELOCITY = 300

def CreateRoamingShadowOfTheSerpentTree():
    root = composites.PrioritySelector(Bundle(name='Shadow of the Serpent behavior'))
    root.AddSubTask(CreateTargetSwitchingBehavior())
    root.AddSubTask(CreateTankingBehavior())
    root.AddSubTask(CreateEntityCombatBehavior(orbitVelocity=COMBAT_ORBIT_VELOCITY, orbitRange=DEFAULT_COMBAT_ORBIT_RANGE, attackRange=DEFAULT_COMBAT_ATTACK_RANGE))
    root.AddSubTask(CreateReGroupBehavior())
    root.AddSubTask(CreateExplorationBehavior(groupsOfInterest=[groupStargate, groupAsteroidBelt], explorationIntervalSeconds=810))
    root.AddSubTask(CreatePatrolBehavior(patrolDistance=100000, orbitRange=10000, patrolInterval=90.0))
    root.AddSubTask(CreateIdleFallback())
    root.AddSubTask(WaitAction(Bundle(name='Do nothing')))
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(root)
    return behaviorTree


def CreateShadowOfTheSerpentGroupBehavior():
    root = Sequence(Bundle(name='Shadow of the Serpent group behavior'))
    root.AddSubTask(GroupMembershipMonitor(Bundle(name='Monitor changes in membership')))
    root.AddSubTask(GroupMemberWarpModeChangedMonitor(Bundle(name='Tracking movement that can result in bubbles changing.')))
    root.AddSubTask(BlackboardMessageMonitor(Bundle(messageAddress=COMBAT_TARGETS_SET)))
    root.AddSubTask(ForceSuccess().AddSubTask(CreateRequestReinforcements()))
    root.AddSubTask(CreateThreatManagementBehavior(friendlyOwnerIds=None, hostileOwnerIds=None, isAutomaticallyAggressive=True))
    root.AddSubTask(CreateManageTargetCombatSetBehavior(PRUNE_TIMEOUT_SECONDS))
    root.AddSubTask(WaitAction(Bundle(name='Wait for some action')))
    return root


def CreateShadowOfTheSerpentisGroupTree():
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(CreateShadowOfTheSerpentGroupBehavior())
    return behaviorTree
