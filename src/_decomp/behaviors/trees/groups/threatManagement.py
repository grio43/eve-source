#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\groups\threatManagement.py
from behaviors.actions.combat import OwnerListFilterAction
from behaviors.composites import Sequence
from behaviors.monitors.ballparks import MonitorProximitySensorsForGroupMembers, TargetsWithOwnerEnteredBubbleMonitor
from behaviors.monitors.ballparks import MonitorInvulnerabilityCanceledInGroupBubbles
from behaviors.monitors.combat import MonitorAssistanceToGroupTargets
from behaviors.trees.combat import COMBAT_TARGETS_SET
from brennivin.itertoolsext import Bundle
from inventorycommon.const import categoryShip, categoryDrone, groupCapsule, categoryFighter

def CreateThreatManagementBehavior(friendlyOwnerIds = None, hostileOwnerIds = None, isAutomaticallyAggressive = False):
    root = Sequence(Bundle(name='threat management'))
    if friendlyOwnerIds:
        root.AddSubTask(OwnerListFilterAction(Bundle(name='Clear out friendly targets', ownerIdSet=friendlyOwnerIds, itemIdSetAddress=COMBAT_TARGETS_SET)))
    if hostileOwnerIds:
        root.AddSubTask(TargetsWithOwnerEnteredBubbleMonitor(Bundle(name='Watch out for enemy owners arriving', targetSetAddress=COMBAT_TARGETS_SET, ownerIds=hostileOwnerIds)))
    root.AddSubTask(MonitorAssistanceToGroupTargets(Bundle(name='Watch out for neutrals assisting known enemies', combatTargetsAddress=COMBAT_TARGETS_SET)))
    root.AddSubTask(MonitorProximitySensorsForGroupMembers(Bundle(name='Watch out for hostiles entering protected airspace', objectListAddress=COMBAT_TARGETS_SET, includedCategories=[categoryShip, categoryDrone, categoryFighter], excludedGroups=[groupCapsule], validOwnerIds=None if isAutomaticallyAggressive else hostileOwnerIds, invalidOwnerIds=friendlyOwnerIds if isAutomaticallyAggressive else None)))
    root.AddSubTask(MonitorInvulnerabilityCanceledInGroupBubbles(Bundle(targetIdListAddress=COMBAT_TARGETS_SET)))
    return root
