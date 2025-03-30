#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\travel.py
from behaviors.actions.ballparks import WarpToNewLocation, GetRandomDeepSpacePosition
from behaviors.actions.entities import UnspawnSelf
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.composites import Sequence
from behaviors.conditions.ballparks import IsLocationWithinWarpDistance
from behaviors.const.blackboardchannels import WARP_SCRAMBLED_ADDRESS
from behaviors.monitors.blackboards import BlackboardMessageMonitor
from brennivin.itertoolsext import Bundle
WARP_TO_LOCATION_GROUP = (ScopeTypes.EntityGroup, 'WARP_TO_LOCATION_GROUP')
WARP_TO_LOCATION_ENTITY = (ScopeTypes.Item, 'WARP_TO_LOCATION_ENTITY')

def CreateWarpToNewLocationBehavior(warpToAddress = WARP_TO_LOCATION_GROUP):
    node = Sequence(Bundle(name='Warp To New Location'))
    node.AddSubTask(BlackboardMessageMonitor(Bundle(name='Reset On Warp Location Message', messageAddress=warpToAddress)))
    node.AddSubTask(IsLocationWithinWarpDistance(Bundle(coordinateAddress=warpToAddress)))
    node.AddSubTask(WarpToNewLocation(Bundle(name='Do Warp', locationMessage=warpToAddress, warpScrambledAddress=WARP_SCRAMBLED_ADDRESS)))
    return node


def CreateWarpAndUnspawnBehavior(warpToAddress = WARP_TO_LOCATION_GROUP):
    return Sequence(Bundle(name='Warp to random location and unspawn')).AddSubTask(GetRandomDeepSpacePosition(Bundle(locationAddress=warpToAddress))).AddSubTask(CreateWarpToNewLocationBehavior(warpToAddress)).AddSubTask(UnspawnSelf())
