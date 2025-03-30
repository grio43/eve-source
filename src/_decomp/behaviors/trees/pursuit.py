#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\pursuit.py
from behaviors import composites
from behaviors.actions.ballparks import WarpToNewLocation
from behaviors.actions.blackboards import BlackboardSetMessageAsNoneAction
from behaviors.actions.combattargets import FindTarget
from behaviors.actions.timer import BlockWhileTimeout
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.conditions.blackboards import BlackboardValueUpdatedRecentlyCondition, IsBlackboardValueNotNone
from behaviors.conditions.randomized import CachedRandomChanceCondition
from behaviors.const.blackboardchannels import WARP_SCRAMBLED_ADDRESS
from behaviors.trees.combat import GROUP_PRIMARY_TARGET, COMBAT_TARGETS_SET
from behaviors.trees.regroup import CreateGetBallPositionAfterWarpBehavior
from brennivin.itertoolsext import Bundle
PURSUIT_DELAY_TIMER_ADDRESS = (ScopeTypes.Item, 'PURSUIT_DELAY_TIMER')
PURSUIT_TARGET_ADDRESS = (ScopeTypes.Item, 'PURSUIT_TARGET')
PURSUIT_LOCATION_ADDRESS = (ScopeTypes.EntityGroup, 'PURSUIT_LOCATION')
PURSUIT_CHANCE_ADDRESS = (ScopeTypes.EntityGroup, 'PURSUIT_CHANCE')

def CreatePursuitBehavior():
    return composites.Sequence(Bundle(name='Enemy Pursuit root')).AddSubTask(composites.PrioritySelector(Bundle(name='do we have a usable location?')).AddSubTask(composites.Sequence().AddSubTask(BlackboardValueUpdatedRecentlyCondition(Bundle(address=PURSUIT_LOCATION_ADDRESS, timeInSeconds=10))).AddSubTask(IsBlackboardValueNotNone(Bundle(valueAddress=PURSUIT_LOCATION_ADDRESS)))).AddSubTask(composites.Sequence(Bundle(name='pick a location if appropriate?')).AddSubTask(BlackboardValueUpdatedRecentlyCondition(Bundle(address=GROUP_PRIMARY_TARGET, timeInSeconds=10))).AddSubTask(CachedRandomChanceCondition(Bundle(chance=0.5, randomValueAddress=PURSUIT_CHANCE_ADDRESS, cacheTimeInSeconds=10))).AddSubTask(BlackboardSetMessageAsNoneAction(Bundle(messageAddress=PURSUIT_TARGET_ADDRESS))).AddSubTask(FindTarget(Bundle(name='Find A Pursuit Target', selectedTargetAddress=PURSUIT_TARGET_ADDRESS, potentialTargetListAddress=COMBAT_TARGETS_SET, includedCategories=[], targetEvaluationFunction='threat', onlyCheckLocalBubble=False, primaryTargetIdAddress=COMBAT_TARGETS_SET))).AddSubTask(CreateGetBallPositionAfterWarpBehavior(ballIdAddress=PURSUIT_TARGET_ADDRESS, locationAddress=PURSUIT_LOCATION_ADDRESS)))).AddSubTask(BlockWhileTimeout(Bundle(timerAddress=PURSUIT_DELAY_TIMER_ADDRESS, timeoutSeconds=4.0))).AddSubTask(WarpToNewLocation(Bundle(locationMessage=PURSUIT_LOCATION_ADDRESS, warpScrambledAddress=WARP_SCRAMBLED_ADDRESS))).AddSubTask(BlockWhileTimeout(Bundle(timerAddress=PURSUIT_DELAY_TIMER_ADDRESS, timeoutSeconds=15.0)))
