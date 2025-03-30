#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\explore.py
from behaviors.actions.ballparks import FindPointToExplore
from behaviors.conditions.ballparks import IsCoordinateInSameBubbleCondition
from behaviors.monitors.timers import StartTimerBlocks
from behaviors.monitors.blackboards import BlackboardMessageMonitor
from behaviors.trees.travel import CreateWarpToNewLocationBehavior, WARP_TO_LOCATION_GROUP
from behaviors import composites
from behaviors.blackboards.scopes import ScopeTypes
from brennivin.itertoolsext import Bundle
RESET_TIMER = (ScopeTypes.EntityGroup, 'EXPLORATION_RESET_TIMER')

def CreateExplorationBehavior(groupsOfInterest = None, dungeonsOfInterest = None, dungeonArchetypesOfInterest = None, explorationIntervalSeconds = 1800):
    groupsOfInterest = groupsOfInterest or []
    dungeonsOfInterest = dungeonsOfInterest or []
    dungeonArchetypesOfInterest = dungeonArchetypesOfInterest or []
    root = composites.PrioritySelector(Bundle(name='Exploration'))

    def CreateShouldExplore():
        node = composites.Sequence(Bundle(name='Should Change Location'))

        def CreateFindNewExplorationPoint():
            return FindPointToExplore(Bundle(name='Find Point To Explore', locationMessage=WARP_TO_LOCATION_GROUP, groupsOfInterest=groupsOfInterest, dungeonsOfInterest=dungeonsOfInterest, dungeonArchetypesOfInterest=dungeonArchetypesOfInterest, pickSpecificChance=0.3, shouldConsiderUnspawnedDungeons=False))

        node.AddSubTask(BlackboardMessageMonitor(Bundle(name='Reset On Timer Change', messageAddress=RESET_TIMER)))
        node.AddSubTask(StartTimerBlocks(Bundle(name='Exploration Reset Timer', timeoutSeconds=explorationIntervalSeconds, timerAddress=RESET_TIMER)))
        node.AddSubTask(CreateFindNewExplorationPoint())
        node.AddSubTask(IsCoordinateInSameBubbleCondition(Bundle(name='Force Fail So We Warp', coordinateAddress=WARP_TO_LOCATION_GROUP)))
        return node

    root.AddSubTask(CreateShouldExplore())
    root.AddSubTask(CreateWarpToNewLocationBehavior())
    return root
