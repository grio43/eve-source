#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\harvesting.py
from behaviors.actions.ballparks import SelectItemByTypes, SelectClosestPointOnObject, ApproachCoordinatesAction, FullStopAction
from behaviors.actions.effects import PlayOneShotStretchEffectAction
from behaviors.actions.timer import SucceedAfterTimeoutAction
from behaviors.behaviortree import BehaviorTree
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.composites import Sequence, PrioritySelector
from behaviors.conditions.ballparks import IsCoordinateWithinDistance
from brennivin.itertoolsext import Bundle
SELECTED_HARVEST_TARGET = (ScopeTypes.EntityGroup, 'SELECTED_HARVEST_TARGET')
SELECTED_HARVEST_LOCATION = (ScopeTypes.Item, 'SELECTED_HARVEST_LOCATION')
HARVESTABLE_STRUCTURE_SET = [34573,
 34717,
 34761,
 34762,
 34763,
 34764,
 34765]
DECONSTRUCTION_EFFECT = 'effects.DeconstructionBeam'
HARVEST_EFFECT = 'effects.HarvestingBeam'
DECONSTRUCTION_DURATION_MS = 10000.0
HARVEST_DURATION_MS = 10000.0
EFFECT_DELAY_SEC = 5.0

def CreateHarvestOutpostBehaviorTree():
    root = CreateHarvestOutpostBehavior()
    tree = BehaviorTree()
    tree.StartRootTask(root)
    return tree


def CreateHarvestOutpostBehavior():
    return Sequence(Bundle(name='Harvest Mechanical Parts')).AddSubTask(SelectItemByTypes(Bundle(typeIds=HARVESTABLE_STRUCTURE_SET, selectedItemAddress=SELECTED_HARVEST_TARGET))).AddSubTask(SelectClosestPointOnObject(Bundle(objectIdAddress=SELECTED_HARVEST_TARGET, closestPointAddress=SELECTED_HARVEST_LOCATION))).AddSubTask(PrioritySelector().AddSubTask(IsCoordinateWithinDistance(Bundle(coordinateAddress=SELECTED_HARVEST_LOCATION, maxDistance=8000.0))).AddSubTask(ApproachCoordinatesAction(Bundle(coordinateAddress=SELECTED_HARVEST_LOCATION, notifyRange=5000.0, blocking=True)))).AddSubTask(Sequence().AddSubTask(FullStopAction()).AddSubTask(PlayOneShotStretchEffectAction(Bundle(effectDuration=DECONSTRUCTION_DURATION_MS, effectName=DECONSTRUCTION_EFFECT, effectTargetAddress=SELECTED_HARVEST_TARGET))).AddSubTask(SucceedAfterTimeoutAction(Bundle(timeoutSeconds=EFFECT_DELAY_SEC + DECONSTRUCTION_DURATION_MS / 1000.0))).AddSubTask(PlayOneShotStretchEffectAction(Bundle(effectDuration=HARVEST_DURATION_MS, effectName=HARVEST_EFFECT, effectTargetAddress=SELECTED_HARVEST_TARGET))).AddSubTask(SucceedAfterTimeoutAction(Bundle(timeoutSeconds=EFFECT_DELAY_SEC + HARVEST_DURATION_MS / 1000.0))))
