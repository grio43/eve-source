#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\guardobject.py
from behaviors.actions import WaitAction
from behaviors.actions.blackboards import BlackboardSendMyItemIdMessageAction, BlackboardSetMessageToIntegerValueAction
from behaviors.actions.guard import PlaceProximitySensor
from behaviors.composites import Sequence, PrioritySelector
from behaviors.decorators.modifiers import ForceFailure
from brennivin.itertoolsext import Bundle
from behaviors.actions.ballparks import OrbitAtDistanceAction, WarpToNewLocation
from behaviors.monitors.ballparks import MonitorSpecificProximitySensor
from behaviors.const.blackboardchannels import GUARD_OBJECT_ITEM_ID, GUARD_OBJECT_POSITION, GUARD_OBJECT_ORBIT_RANGE
from behaviors.const.blackboardchannels import WARP_SCRAMBLED_ADDRESS
from behaviors.conditions.ballparks import IsBallPresentInMyBubbleCondition
from behaviors.trees.combat import COMBAT_TARGETS_SET
from inventorycommon.const import categoryShip, categoryDrone, groupCapsule, categoryFighter
from npcs.server.tags import DRIFTER_TAG
GUARD_OBJECT_DEFAULT_CATEGORIES = [categoryShip, categoryDrone, categoryFighter]

def CreateGuardObjectBehavior(validOwnerIds = (), includedCategories = GUARD_OBJECT_DEFAULT_CATEGORIES, invalidOwnerIds = None):
    return PrioritySelector(Bundle(name='Guard Object')).AddSubTask(Sequence(Bundle(name='Orbit Guard Object')).AddSubTask(IsBallPresentInMyBubbleCondition(Bundle(ballIdAddress=GUARD_OBJECT_ITEM_ID))).AddSubTask(OrbitAtDistanceAction(Bundle(orbitTargetAddress=GUARD_OBJECT_ITEM_ID, orbitRange=0, blocking=False, blockUntilRange=None, orbitRangeAddress=GUARD_OBJECT_ORBIT_RANGE))).AddSubTask(MonitorSpecificProximitySensor(Bundle(objectListAddress=COMBAT_TARGETS_SET, includedCategories=includedCategories, excludedGroups=[groupCapsule], proximitySensorAddress=GUARD_OBJECT_ITEM_ID, validOwnerIds=validOwnerIds, invalidOwnerIds=invalidOwnerIds))).AddSubTask(WaitAction(Bundle(name='Wait until disturbed')))).AddSubTask(WarpToNewLocation(Bundle(name='Warp to Guard Object', locationMessage=GUARD_OBJECT_POSITION, warpScrambledAddress=WARP_SCRAMBLED_ADDRESS)))


def CreateGuardObjectEntityBehavior():
    return PrioritySelector(Bundle(name='Guard Object')).AddSubTask(Sequence(Bundle(name='Orbit Guard Object')).AddSubTask(IsBallPresentInMyBubbleCondition(Bundle(ballIdAddress=GUARD_OBJECT_ITEM_ID))).AddSubTask(OrbitAtDistanceAction(Bundle(orbitTargetAddress=GUARD_OBJECT_ITEM_ID, orbitRange=0, blocking=False, blockUntilRange=None, orbitRangeAddress=GUARD_OBJECT_ORBIT_RANGE))).AddSubTask(WaitAction(Bundle(name='Wait until disturbed')))).AddSubTask(WarpToNewLocation(Bundle(name='Warp to Guard Object', locationMessage=GUARD_OBJECT_POSITION, warpScrambledAddress=WARP_SCRAMBLED_ADDRESS)))


def CreateGuardCurrentLocationBehavior(guardRange = 1000000, guardReplacementRange = 10000):
    return ForceFailure(Bundle(name='Guard the current location')).AddSubTask(Sequence().AddSubTask(BlackboardSendMyItemIdMessageAction(Bundle(messageAddress=GUARD_OBJECT_ITEM_ID))).AddSubTask(BlackboardSetMessageToIntegerValueAction(Bundle(messageAddress=GUARD_OBJECT_ORBIT_RANGE, value=guardRange))).AddSubTask(PlaceProximitySensor(Bundle(itemIdAddress=GUARD_OBJECT_ITEM_ID, rangeAddress=GUARD_OBJECT_ORBIT_RANGE, sensorReplacementRange=guardReplacementRange, tags={DRIFTER_TAG}))))
