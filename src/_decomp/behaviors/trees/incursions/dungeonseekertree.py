#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\incursions\dungeonseekertree.py
from behaviors import composites
from behaviors.actions import WaitAction
from behaviors.actions.combatnavigation import DEFAULT_COMBAT_ORBIT_RANGE, DEFAULT_COMBAT_ATTACK_RANGE
from behaviors.behaviortree import BehaviorTree
from behaviors.trees.combat import CreateTargetSwitchingBehavior, CreateEntityCombatBehavior
from behaviors.trees.guardobject import CreateGuardObjectBehavior
from brennivin.itertoolsext import Bundle
COMBAT_ORBIT_VELOCITY = 600

def CreateDungeonSeekerBehaviorTree():
    root = composites.PrioritySelector(Bundle(name='Dungeon Seeker Root'))
    root.AddSubTask(CreateTargetSwitchingBehavior())
    root.AddSubTask(CreateEntityCombatBehavior(orbitVelocity=COMBAT_ORBIT_VELOCITY, orbitRange=DEFAULT_COMBAT_ORBIT_RANGE, attackRange=DEFAULT_COMBAT_ATTACK_RANGE))
    root.AddSubTask(CreateGuardObjectBehavior())
    root.AddSubTask(WaitAction(Bundle(name='Do nothing')))
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(root)
    return behaviorTree
