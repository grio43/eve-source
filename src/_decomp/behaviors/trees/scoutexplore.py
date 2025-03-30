#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\scoutexplore.py
from behaviors.actions.ballparks import WarpToNewLocation, FindPointToExplore
from behaviors.conditions.ballparks import IsCoordinateInSameBubbleCondition
from behaviors.const.blackboardchannels import WARP_SCRAMBLED_ADDRESS
from behaviors.monitors.timers import StartTimerBlocks
from behaviors.monitors.blackboards import BlackboardMessageMonitor
from behaviors import composites
from behaviors.decorators import modifiers
from behaviors.blackboards.scopes import ScopeTypes
import inventorycommon.const as invconst
from brennivin.itertoolsext import Bundle
WARP_TO_LOCATION_GROUP = (ScopeTypes.EntityGroup, 'WARP_TO_LOCATION_GROUP')
RESET_TIMER = (ScopeTypes.EntityGroup, 'EXPLORATION_RESET_TIMER')
LANDMARK_ARCHETYPE = 2
AJS1 = 5460
UNIDENTIFIED_STRUCTURE = 5610
DUNGEON_WORMHOLE = 5643

def CreateExplorationBehavior():
    root = composites.PrioritySelector(Bundle(name='Exploration'))

    def CreateShouldExplore():
        node = composites.Sequence(Bundle(name='Should Change Location'))

        def CreateFindNewExplorationPoint():
            node = FindPointToExplore(Bundle(name='Find Point To Explore', locationMessage=WARP_TO_LOCATION_GROUP, groupsOfInterest=[invconst.groupStargate,
             invconst.groupStation,
             invconst.groupPlanetaryCustomsOffices,
             invconst.groupAsteroidBelt], dungeonsOfInterest=[AJS1, UNIDENTIFIED_STRUCTURE, DUNGEON_WORMHOLE], dungeonArchetypesOfInterest=[], pickSpecificChance=0.3, shouldConsiderUnspawnedDungeons=False))
            return node

        node.AddSubTask(BlackboardMessageMonitor(Bundle(name='Reset On Timer Change', messageAddress=RESET_TIMER)))
        node.AddSubTask(StartTimerBlocks(Bundle(name='Exploration Reset Timer', timeoutSeconds=360, timerAddress=RESET_TIMER)))
        node.AddSubTask(CreateFindNewExplorationPoint())
        node.AddSubTask(IsCoordinateInSameBubbleCondition(Bundle(name='Force Fail So We Warp', coordinateAddress=WARP_TO_LOCATION_GROUP)))
        return node

    def CreateWarpToNewLocationBehavior():
        node = composites.Sequence(Bundle(name='Warp To New Location'))

        def CreateIsLocationNotInSameBubble():
            node = modifiers.Not()
            node.AddSubTask(IsCoordinateInSameBubbleCondition(Bundle(coordinateAddress=WARP_TO_LOCATION_GROUP)))
            return node

        node.AddSubTask(BlackboardMessageMonitor(Bundle(name='Reset On Warp Location Message', messageAddress=WARP_TO_LOCATION_GROUP)))
        node.AddSubTask(CreateIsLocationNotInSameBubble())
        node.AddSubTask(WarpToNewLocation(Bundle(name='Do Warp', locationMessage=WARP_TO_LOCATION_GROUP, warpScrambledAddress=WARP_SCRAMBLED_ADDRESS)))
        return node

    root.AddSubTask(CreateShouldExplore())
    root.AddSubTask(CreateWarpToNewLocationBehavior())
    return root
