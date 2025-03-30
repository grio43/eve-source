#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\groups\incursions.py
from behaviors.actions import WaitAction
from behaviors.behaviortree import BehaviorTree
from behaviors.composites import Sequence, PrioritySelector
from behaviors.conditions.blackboards import IsBlackboardValueNone
from behaviors.const.blackboardchannels import GUARD_OBJECT_ITEM_ID
from behaviors.decorators.modifiers import ForceSuccess
from behaviors.monitors.ballparks import MonitorSpecificProximitySensorForGroupMembers
from behaviors.monitors.blackboards import BlackboardMessageMonitor
from behaviors.monitors.groups import GroupMembershipMonitor
from behaviors.monitors.navigation import GroupMemberWarpModeChangedMonitor
from behaviors.trees.combat import COMBAT_TARGETS_SET
from behaviors.trees.groups.combat import CreateManageTargetCombatSetBehavior
from behaviors.trees.groups.threatManagement import CreateThreatManagementBehavior
from behaviors.trees.incursions.const import AMARR_NAVY_OWNERS, DRIFTER_OWNERS
from behaviors.trees.reinforcements import CreateRequestReinforcements
from brennivin.itertoolsext import Bundle
from inventorycommon.const import groupCapsule, categoryShip, categoryDrone, categoryEntity, categoryFighter
PRUNE_TIMEOUT_SECONDS = 120

def CreateIncursionGroupBehavior(friendlyOwnerIds = None, hostileOwnerIds = None, isAutomaticallyAggressive = False):
    root = Sequence(Bundle(name='root'))
    root.AddSubTask(GroupMembershipMonitor(Bundle(name='Monitor changes in membership')))
    root.AddSubTask(GroupMemberWarpModeChangedMonitor(Bundle(name='Tracking movement that can result in bubbles changing.')))
    root.AddSubTask(BlackboardMessageMonitor(Bundle(messageAddress=COMBAT_TARGETS_SET)))
    root.AddSubTask(ForceSuccess().AddSubTask(CreateRequestReinforcements()))
    root.AddSubTask(CreateThreatManagementBehavior(friendlyOwnerIds=friendlyOwnerIds, hostileOwnerIds=hostileOwnerIds, isAutomaticallyAggressive=isAutomaticallyAggressive))
    root.AddSubTask(CreateManageTargetCombatSetBehavior(PRUNE_TIMEOUT_SECONDS))
    root.AddSubTask(CreateGroupGuardBehavior(friendlyOwnerIds=friendlyOwnerIds, hostileOwnerIds=hostileOwnerIds, isAutomaticallyAggressive=isAutomaticallyAggressive))
    root.AddSubTask(WaitAction(Bundle(name='Wait for some action')))
    return root


def CreateGroupBehaviorTree(friendlyOwnerIds = None, hostileOwnerIds = None, isAutomaticallyAggressive = False):
    root = CreateIncursionGroupBehavior(friendlyOwnerIds=friendlyOwnerIds, hostileOwnerIds=hostileOwnerIds, isAutomaticallyAggressive=isAutomaticallyAggressive)
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(root)
    return behaviorTree


def CreateDrifterGroupBehaviorTree():
    return CreateGroupBehaviorTree(friendlyOwnerIds=DRIFTER_OWNERS, hostileOwnerIds=AMARR_NAVY_OWNERS, isAutomaticallyAggressive=True)


def CreateGroupGuardBehavior(friendlyOwnerIds = None, hostileOwnerIds = None, isAutomaticallyAggressive = False):
    root = PrioritySelector(Bundle(name='guard monitoring'))
    root.AddSubTask(IsBlackboardValueNone(Bundle(valueAddress=GUARD_OBJECT_ITEM_ID)))
    root.AddSubTask(MonitorSpecificProximitySensorForGroupMembers(Bundle(objectListAddress=COMBAT_TARGETS_SET, proximitySensorAddress=GUARD_OBJECT_ITEM_ID, includedCategories=[categoryShip,
     categoryDrone,
     categoryEntity,
     categoryFighter], excludedGroups=[groupCapsule], validOwnerIds=None if isAutomaticallyAggressive else hostileOwnerIds, invalidOwnerIds=friendlyOwnerIds if isAutomaticallyAggressive else None)))
    return root
