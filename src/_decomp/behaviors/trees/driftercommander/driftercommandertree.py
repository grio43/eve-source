#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\driftercommander\driftercommandertree.py
from behaviors import composites
from behaviors.actions.combatnavigation import DEFAULT_COMBAT_ORBIT_RANGE, DEFAULT_COMBAT_ATTACK_RANGE
from behaviors.behaviortree import BehaviorTree
from behaviors.trees.combat import CreateCombatBehavior, CreateTargetSwitchingBehavior
from behaviors.trees.guardobject import CreateGuardObjectBehavior
from behaviors.trees.drifters.superweapon import CreateSuperWeaponBehavior
from brennivin.itertoolsext import Bundle
COMBAT_ORBIT_VELOCITY = 1500

def CreateDrifterCommanderBehaviorTree():
    root = composites.PrioritySelector(Bundle(name='Drifter Root'))
    root.AddSubTask(CreateSuperWeaponBehavior())
    root.AddSubTask(CreateTargetSwitchingBehavior())
    root.AddSubTask(CreateCombatBehavior(orbitVelocity=COMBAT_ORBIT_VELOCITY, orbitRange=DEFAULT_COMBAT_ORBIT_RANGE, attackRange=DEFAULT_COMBAT_ATTACK_RANGE))
    root.AddSubTask(CreateGuardObjectBehavior())
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(root)
    return behaviorTree
