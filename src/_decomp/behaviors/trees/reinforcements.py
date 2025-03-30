#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\reinforcements.py
from behaviors.actions.ballparks import WarpToNewLocation
from behaviors.behaviortree import BehaviorTree
from behaviors.composites import Sequence
from behaviors.conditions.ballparks import IsLocationWithinWarpDistance
from behaviors.conditions.blackboards import IsBlackboardValueNotNone, BlackboardValueUpdatedRecentlyCondition
from behaviors.const.blackboardchannels import LAST_REINFORCEMENT_REQUEST_COORDINATE_ADDRESS, WARP_SCRAMBLED_ADDRESS
from behaviors.decorators.modifiers import ForceFailure
from behaviors.monitors.reinforcements import AreReinforcementsAuthorizedMonitor, AreReinforcementAvailableMonitor
from behaviors.actions.reinforcements import CallInReinforcementsAction
from brennivin.itertoolsext import Bundle

def CreateRequestReinforcements():
    root = ForceFailure(Bundle(name='Reinforcements'))

    def CreateSequence():
        seq = Sequence(Bundle())
        seq.AddSubTask(AreReinforcementsAuthorizedMonitor(Bundle()))
        seq.AddSubTask(AreReinforcementAvailableMonitor(Bundle()))
        seq.AddSubTask(CallInReinforcementsAction(Bundle()))
        return seq

    root.AddSubTask(CreateSequence())
    return root


def CreateReinforcementTree():
    tree = BehaviorTree()
    tree.StartRootTask(CreateRequestReinforcements())
    return tree


def CreateReinforceLocationBehavior():
    seq = Sequence(Bundle(name='Reinforce Group'))
    seq.AddSubTask(IsBlackboardValueNotNone(Bundle(name='Do we have a location to reinforce?', valueAddress=LAST_REINFORCEMENT_REQUEST_COORDINATE_ADDRESS)))
    seq.AddSubTask(BlackboardValueUpdatedRecentlyCondition(Bundle(name='Posted in the last minute?', address=LAST_REINFORCEMENT_REQUEST_COORDINATE_ADDRESS, timeInSeconds=60)))
    seq.AddSubTask(IsLocationWithinWarpDistance(Bundle(name='Far enough to warp?', coordinateAddress=LAST_REINFORCEMENT_REQUEST_COORDINATE_ADDRESS)))
    seq.AddSubTask(WarpToNewLocation(Bundle(name='Warp drive active!', locationMessage=LAST_REINFORCEMENT_REQUEST_COORDINATE_ADDRESS, warpScrambledAddress=WARP_SCRAMBLED_ADDRESS)))
    return seq
