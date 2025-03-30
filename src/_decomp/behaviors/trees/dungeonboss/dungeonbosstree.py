#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\dungeonboss\dungeonbosstree.py
from behaviors import composites
from behaviors.actions import WaitAction
from behaviors.actions.ballparks import FindPointToExplore
from behaviors.actions.blackboards import BlackboardSetMessageToBooleanValueAction
from behaviors.actions.combatnavigation import DEFAULT_COMBAT_ATTACK_RANGE, DEFAULT_COMBAT_ORBIT_RANGE
from behaviors.actions.damage import SetArmorRatio
from behaviors.behaviortree import BehaviorTree
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.conditions.blackboards import IsBlackboardValueTrue
from behaviors.const.combat import SIZE_TARGET_EVALUATOR
from behaviors.decorators.timers import CooldownTimer
from behaviors.monitors.damage import ArmorDamageThresholdMonitor
from behaviors.trees.combat import CreateCombatBehavior, CreateTargetSwitchingBehavior
from behaviors.trees.explore import CreateExplorationBehavior
from behaviors.trees.guardobject import CreateGuardObjectBehavior, CreateGuardCurrentLocationBehavior
from behaviors.trees.travel import CreateWarpToNewLocationBehavior, WARP_TO_LOCATION_GROUP
from brennivin.itertoolsext import Bundle
from evedungeons.common.constants import ARCHETYPE_HIDDEN_WORMHOLE_DUNGEON
from inventorycommon.const import groupPlanet
ESCAPE_TIMER = (ScopeTypes.Item, 'ESCAPE_TIMER')
ESCAPE_TRIGGER_ADDRESS = (ScopeTypes.Item, 'ESCAPE_TRIGGER')
COMBAT_ORBIT_VELOCITY = 1500
BOSS_EXPLORATION_SITE_GROUP_IDS = [groupPlanet]
BOSS_EXPLORATION_TIME = 3600
BOSS_GUARD_RANGE = 500000
BOSS_GUARD_REPLACEMENT_RANGE = 100000
BOSS_ESCAPE_INTERVAL_SECONDS = 1200
BOSS_ESCAPE_ARMOR_RATIO = 0.2
BOSS_ESCAPE_EMERGENCY_ARMOR_RATIO_BUFFER = 0.05

def CreateFindNewEscapeLocation():
    return FindPointToExplore(Bundle(name='Find Point To Escape-warp to', locationMessage=WARP_TO_LOCATION_GROUP, groupsOfInterest=BOSS_EXPLORATION_SITE_GROUP_IDS, dungeonArchetypesOfInterest=[ARCHETYPE_HIDDEN_WORMHOLE_DUNGEON], dungeonsOfInterest=[], pickSpecificChance=0.0, shouldConsiderUnspawnedDungeons=False))


def CreateEscapeBehavior(escapeIntervalSeconds = BOSS_ESCAPE_INTERVAL_SECONDS, escapeArmorRatio = BOSS_ESCAPE_ARMOR_RATIO):
    root = composites.Sequence(Bundle(name='Escape'))
    root.AddSubTask(ArmorDamageThresholdMonitor(Bundle(armorRatioThreshold=escapeArmorRatio, thresholdReachedAddress=ESCAPE_TRIGGER_ADDRESS)))
    root.AddSubTask(IsBlackboardValueTrue(Bundle(valueAddress=ESCAPE_TRIGGER_ADDRESS)))
    root.AddSubTask(CooldownTimer(Bundle(timerAddress=ESCAPE_TIMER, timeoutSeconds=escapeIntervalSeconds)).AddSubTask(composites.Sequence().AddSubTask(CreateFindNewEscapeLocation()).AddSubTask(CreateWarpToNewLocationBehavior()).AddSubTask(SetArmorRatio(Bundle(name='Assign emergency armor value to prevent re-triggering', armorRatio=escapeArmorRatio + BOSS_ESCAPE_EMERGENCY_ARMOR_RATIO_BUFFER))).AddSubTask(BlackboardSetMessageToBooleanValueAction(Bundle(name='Reset trigger', messageAddress=ESCAPE_TRIGGER_ADDRESS, value=False)))))
    return root


def CreateDungeonBossBehaviorTree():
    root = composites.PrioritySelector(Bundle(name='Dungeon Boss Root'))
    root.AddSubTask(CreateGuardCurrentLocationBehavior(guardRange=BOSS_GUARD_RANGE, guardReplacementRange=BOSS_GUARD_REPLACEMENT_RANGE))
    root.AddSubTask(CreateEscapeBehavior(escapeIntervalSeconds=BOSS_ESCAPE_INTERVAL_SECONDS, escapeArmorRatio=BOSS_ESCAPE_ARMOR_RATIO))
    root.AddSubTask(CreateTargetSwitchingBehavior(targetEvaluationFunction=SIZE_TARGET_EVALUATOR))
    root.AddSubTask(CreateCombatBehavior(orbitVelocity=COMBAT_ORBIT_VELOCITY, orbitRange=DEFAULT_COMBAT_ORBIT_RANGE, attackRange=DEFAULT_COMBAT_ATTACK_RANGE))
    root.AddSubTask(CreateExplorationBehavior(groupsOfInterest=BOSS_EXPLORATION_SITE_GROUP_IDS, dungeonArchetypesOfInterest=[ARCHETYPE_HIDDEN_WORMHOLE_DUNGEON], explorationIntervalSeconds=BOSS_EXPLORATION_TIME))
    root.AddSubTask(CreateGuardObjectBehavior())
    root.AddSubTask(WaitAction(Bundle(name='Do nothing')))
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(root)
    return behaviorTree
