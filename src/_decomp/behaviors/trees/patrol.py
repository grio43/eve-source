#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\patrol.py
from behaviors import composites
from behaviors.actions import WaitAction
from behaviors.actions.ballparks import SelectTargetToAnalyzeAction, OrbitAtDistanceAction
from behaviors.actions.ballparks import FullStopAction, SelectCoordinateNearCoordinateAction
from behaviors.actions.ballparks import ApproachCoordinatesAction
from behaviors.actions.blackboards import BlackboardSendMyItemIdMessageAction
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.conditions.ballparks import IsBallPresentInMyBubbleCondition, IsBallWithInDistanceCondition, IsCoordinateInSameBubbleCondition
from behaviors.conditions.blackboards import BlackboardMessageAndMyItemIdEqualCondition
from behaviors.monitors.ballparks import BubbleChangedMonitor
from behaviors.monitors.blackboards import BlackboardMessageMonitorBlocking, BlackboardMessageMonitor
from behaviors.monitors.timers import StartTimerBlocks
from brennivin.itertoolsext import Bundle
from inventorycommon import const as invConst
WARP_TO_LOCATION_GROUP = (ScopeTypes.EntityGroup, 'WARP_TO_LOCATION_GROUP')
PATROL_OBJECT_TIMER = (ScopeTypes.EntityGroup, 'PATROL_OBJECT_TIMER')
PATROL_OBJECT_ID = (ScopeTypes.EntityGroup, 'PATROL_OBJECT_ID')
PATROL_CONSIDER_LIST = (ScopeTypes.EntityGroup, 'PATROL_CONSIDER_LIST')
IGNORED_CATEGORIES = {invConst.categoryDrone, invConst.categoryShip}
IGNORED_GROUPS = {invConst.groupDeadspaceSleeperAwakenedDefender,
 invConst.groupDeadspaceSleeperSleeplessPatroller,
 invConst.groupDeadspaceSleeperSleeplessSentinel,
 invConst.groupDeadspaceSleeperSleeplessDefender,
 invConst.groupDeadspaceSleeperAwakenedPatroller,
 invConst.groupDeadspaceSleeperAwakenedSentinel,
 invConst.groupDeadspaceSleeperAwakenedDefender,
 invConst.groupDeadspaceSleeperEmergentPatroller,
 invConst.groupDeadspaceSleeperEmergentSentinel,
 invConst.groupDeadspaceSleeperEmergentDefender,
 invConst.groupRoamingSleepersCruiser,
 invConst.groupDrifterBattleship,
 invConst.groupStation,
 invConst.groupCloud,
 invConst.groupHarvestableCloud,
 invConst.groupPlanetaryCloud,
 invConst.groupTemporaryCloud,
 invConst.groupWarpDisruptionProbe,
 invConst.groupBeacon,
 invConst.groupInvisibleBeacon}
TYPE_UNIDENTIFIED_WH = 34494
IGNORED_TYPES = {TYPE_UNIDENTIFIED_WH}
IDLE_ANCHOR = (ScopeTypes.EntityGroup, 'IDLE_ANCHOR')
IDLE_GOTO_POINT = (ScopeTypes.EntityGroup, 'IDLE_GOTO_POINT')

def CreateIdlePatrolBehavior():
    root = composites.PrioritySelector(Bundle(name='Idle'))
    root.AddSubTask(CreatePatrolBehavior())
    root.AddSubTask(CreateIdleFallback())
    return root


def HaveAValidTarget(targetAddress = None, maxDistance = None):
    isValidTargetRoot = composites.Sequence(Bundle(name='Has Valid Target?'))
    isValidTargetRoot.AddSubTask(BlackboardMessageMonitorBlocking(Bundle(messageAddress=targetAddress)))
    isValidTargetRoot.AddSubTask(IsBallPresentInMyBubbleCondition(Bundle(ballIdAddress=targetAddress)))
    isValidTargetRoot.AddSubTask(IsBallWithInDistanceCondition(Bundle(ballIdAddress=targetAddress, maxDistance=maxDistance)))
    return isValidTargetRoot


def CreatePatrolBehavior(patrolDistance = 100000, orbitRange = 10000, patrolInterval = 90.0):
    root = composites.Sequence(Bundle(name='Patrol Area'))
    root.AddSubTask(BubbleChangedMonitor(Bundle()))

    def SelectTargetAction(scanDistance):
        return SelectTargetToAnalyzeAction(Bundle(selectedTargetAddress=PATROL_OBJECT_ID, maxDistance=scanDistance, ignoredCategories=IGNORED_CATEGORIES, ignoredGroups=IGNORED_GROUPS, ignoredTypes=IGNORED_TYPES, shouldIgnoreMobileTargets=True))

    def SelectTargetToAnalyze(scanDistance):
        node = composites.Sequence(Bundle(name='Select Patrol Target'))
        node.AddSubTask(StartTimerBlocks(Bundle(timeoutSeconds=patrolInterval, timerAddress=PATROL_OBJECT_TIMER)))
        node.AddSubTask(SelectTargetAction(scanDistance))
        return node

    def PickObjectToPatrol():
        pickObjectRoot = composites.PrioritySelector(Bundle(name='Pick Object to Patrol'))
        pickObjectRoot.AddSubTask(SelectTargetToAnalyze(patrolDistance))
        pickObjectRoot.AddSubTask(HaveAValidTarget(targetAddress=PATROL_OBJECT_ID, maxDistance=patrolDistance))
        pickObjectRoot.AddSubTask(SelectTargetAction(patrolDistance))
        return pickObjectRoot

    root.AddSubTask(PickObjectToPatrol())
    root.AddSubTask(BlackboardMessageMonitor(Bundle(messageAddress=PATROL_OBJECT_TIMER)))
    root.AddSubTask(BlackboardMessageMonitor(Bundle(messageAddress=PATROL_OBJECT_ID)))
    root.AddSubTask(OrbitAtDistanceAction(Bundle(orbitTargetAddress=PATROL_OBJECT_ID, orbitRange=orbitRange, blocking=True, blockUntilRange=orbitRange * 1.5)))
    root.AddSubTask(WaitAction(Bundle(name='Patrolling object')))
    return root


def CreateIdleFallback():
    root = composites.Sequence(Bundle(name='Idle Fallback'))

    def CreateSelectPointBehavior():
        selectPointRoot = composites.PrioritySelector(Bundle(name='Select Observation Point'))

        def CreateValidPointBehavior():
            isValidPointRoot = composites.Sequence()
            isValidPointRoot.AddSubTask(BlackboardMessageMonitorBlocking(Bundle(messageAddress=IDLE_GOTO_POINT)))
            isValidPointRoot.AddSubTask(IsCoordinateInSameBubbleCondition(Bundle(coordinateAddress=IDLE_GOTO_POINT)))
            return isValidPointRoot

        selectPointRoot.AddSubTask(CreateValidPointBehavior())
        selectPointRoot.AddSubTask(SelectCoordinateNearCoordinateAction(Bundle(sourceCoordinateAddress=WARP_TO_LOCATION_GROUP, destinationCoordinateAddress=IDLE_GOTO_POINT, minDistance=10000.0, maxDistance=20000.0)))
        return selectPointRoot

    root.AddSubTask(CreateSelectPointBehavior())
    root.AddSubTask(ApproachCoordinatesAction(Bundle(coordinateAddress=IDLE_GOTO_POINT, notifyRange=1000.0, blocking=True)))

    def PickAnchor():
        pickAnchorRoot = composites.PrioritySelector(Bundle(name='Pick Anchor'))
        pickAnchorRoot.AddSubTask(HaveAValidTarget(targetAddress=IDLE_ANCHOR, maxDistance=40000))
        pickAnchorRoot.AddSubTask(BlackboardSendMyItemIdMessageAction(Bundle(messageAddress=IDLE_ANCHOR)))
        return pickAnchorRoot

    root.AddSubTask(PickAnchor())

    def AnchorOrOrbit():
        anchorOrOrbitRoot = composites.PrioritySelector(Bundle(name='Anchor or Orbit'))

        def Anchor():
            anchorRoot = composites.Sequence(Bundle(name='Anchor'))
            anchorRoot.AddSubTask(BlackboardMessageAndMyItemIdEqualCondition(Bundle(name='Am I Anchor?', messageAddress=IDLE_ANCHOR)))
            anchorRoot.AddSubTask(FullStopAction(Bundle()))
            anchorRoot.AddSubTask(WaitAction(Bundle()))
            return anchorRoot

        anchorOrOrbitRoot.AddSubTask(Anchor())

        def OrbitByDefault():
            orbitRoot = composites.Sequence(Bundle(name='Orbit By Default'))
            orbitRoot.AddSubTask(OrbitAtDistanceAction(Bundle(orbitTargetAddress=IDLE_ANCHOR, orbitRange=3000.0, blocking=False, blockUntilRange=None)))
            orbitRoot.AddSubTask(WaitAction(Bundle()))
            return orbitRoot

        anchorOrOrbitRoot.AddSubTask(OrbitByDefault())
        return anchorOrOrbitRoot

    root.AddSubTask(AnchorOrOrbit())
    return root
