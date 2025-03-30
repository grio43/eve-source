#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\corpseharvesting.py
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.composites import Sequence, PrioritySelector
from brennivin.itertoolsext import Bundle
from behaviors.actions.ballparks import SelectItemByTypes, ApproachObject, EntityLootItem
from behaviors.conditions.blackboards import IsBlackboardValueNotNone
from behaviors.actions.blackboards import BlackboardSetMessageAsNoneAction
from behaviors.monitors.ballparks import TargetLeavingParkMonitor
from behaviors.decorators.timers import CooldownTimer
from behaviors.actions.timer import SucceedAfterTimeoutAction
from inventorycommon.const import typeCorpse, typeCorpseFemale
CORPSE_TYPES = [typeCorpse, typeCorpseFemale]
CORPSE_ITEM_ADDRESS = (ScopeTypes.Item, 'CORPSE_ITEM')
CORPSE_SCAN_COOLDOWN = (ScopeTypes.EntityGroup, 'CORPSE_SCAN_COOLDOWN')
CORPSE_SCAN_COOLDOWN_SEC = 300

def CreateCorpseHarvestingBehavior():
    return PrioritySelector(Bundle(name='Corpse Harvesting')).AddSubTask(Sequence(Bundle(name='Harvest Corpse If Valid Target')).AddSubTask(IsBlackboardValueNotNone(Bundle(name='Has Corpse Target', valueAddress=CORPSE_ITEM_ADDRESS))).AddSubTask(TargetLeavingParkMonitor(Bundle(targetAddress=CORPSE_ITEM_ADDRESS, clearValue=True))).AddSubTask(ApproachObject(Bundle(name='Approach Corpse', itemIdAddress=CORPSE_ITEM_ADDRESS, notifyRange=500, approachRange=0, blocking=True))).AddSubTask(EntityLootItem(Bundle(name='Pick Up Corpse For Loot', itemIdAddress=CORPSE_ITEM_ADDRESS))).AddSubTask(BlackboardSetMessageAsNoneAction(Bundle(name='Reset Corpse Target', messageAddress=CORPSE_ITEM_ADDRESS))).AddSubTask(SucceedAfterTimeoutAction(Bundle(name='Waiting On Object To Leave Park', timeoutSeconds=5))).AddSubTask(SelectItemByTypes(Bundle(name='Find Corpse In Bubble', typeIds=CORPSE_TYPES, selectedItemAddress=CORPSE_ITEM_ADDRESS)))).AddSubTask(CooldownTimer(Bundle(name='Corpse Harvest Cooldown Timer', timeoutSeconds=CORPSE_SCAN_COOLDOWN_SEC, timerAddress=CORPSE_SCAN_COOLDOWN)).AddSubTask(SelectItemByTypes(Bundle(name='Find Corpse In Bubble', typeIds=CORPSE_TYPES, selectedItemAddress=CORPSE_ITEM_ADDRESS))))
