#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\groups\combat.py
from behaviors.actions.combattargets import PruneNpcsFromTargetSet
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.decorators.modifiers import ForceSuccess
from behaviors.decorators.timers import CooldownTimer
from behaviors.trees.combat import COMBAT_TARGETS_SET
from brennivin.itertoolsext import Bundle
PRUNE_TARGET_TIMER_ADDRESS = (ScopeTypes.EntityGroup, 'PRUNE_TARGET_TIMER')

def CreateManageTargetCombatSetBehavior(cooldownTimerSeconds):
    root = ForceSuccess()
    root.AddSubTask(CooldownTimer(Bundle(timerAddress=PRUNE_TARGET_TIMER_ADDRESS, timeoutSeconds=cooldownTimerSeconds)).AddSubTask(PruneNpcsFromTargetSet(Bundle(targetSetAddress=COMBAT_TARGETS_SET))))
    return root
