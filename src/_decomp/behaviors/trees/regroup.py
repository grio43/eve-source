#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\regroup.py
from behaviors import composites
from behaviors.actions.ballparks import WarpToNewLocation, GetBallWarpToLocation, GetBallGotoPointAction
from behaviors.actions.entities import SelectGroupLeaderAction
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.conditions.ballparks import IsBallPresentInMyBubbleCondition, IsBallInWarpCondition
from behaviors.const.blackboardchannels import WARP_SCRAMBLED_ADDRESS
from behaviors.decorators.modifiers import Not
from brennivin.itertoolsext import Bundle
GROUP_LEADER_ADDRESS = (ScopeTypes.EntityGroup, 'GROUP_LEADER')
REGROUP_LOCATION_ADDRESS = (ScopeTypes.EntityGroup, 'REGROUP_LOCATION')

def CreateReGroupBehavior():
    return composites.Sequence(Bundle(name='ReGroup root')).AddSubTask(SelectGroupLeaderAction(Bundle(groupLeaderIdAddress=GROUP_LEADER_ADDRESS))).AddSubTask(Not().AddSubTask(IsBallPresentInMyBubbleCondition(Bundle(ballIdAddress=GROUP_LEADER_ADDRESS)))).AddSubTask(CreateGetBallPositionAfterWarpBehavior(ballIdAddress=GROUP_LEADER_ADDRESS, locationAddress=REGROUP_LOCATION_ADDRESS)).AddSubTask(WarpToNewLocation(Bundle(locationMessage=REGROUP_LOCATION_ADDRESS, warpScrambledAddress=WARP_SCRAMBLED_ADDRESS)))


def CreateGetBallPositionAfterWarpBehavior(ballIdAddress = None, locationAddress = None):
    return composites.PrioritySelector(Bundle(name='Get Position After Warp')).AddSubTask(composites.Sequence().AddSubTask(IsBallInWarpCondition(Bundle(ballIdAddress=ballIdAddress))).AddSubTask(GetBallGotoPointAction(Bundle(ballIdAddress=ballIdAddress, gotoPointAddress=locationAddress)))).AddSubTask(GetBallWarpToLocation(Bundle(ballIdAddress=ballIdAddress, locationAddress=locationAddress)))
