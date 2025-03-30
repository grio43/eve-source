#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\scoutsidle.py
from behaviors import composites
from behaviors.actions import WaitAction
from behaviors.actions.ballparks import ApproachCoordinatesAction, SelectCoordinateNearCoordinateAction
from behaviors.actions.ballparks import OrbitAtDistanceAction, FullStopAction, SelectTargetToAnalyzeAction
from behaviors.actions.blackboards import BlackboardSendMyItemIdMessageAction
from behaviors.actions import effects
from behaviors.actions.timer import SucceedAfterTimeoutAction
from behaviors.behaviortree import BehaviorTree
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.conditions.ballparks import IsCoordinateInSameBubbleCondition, IsBallPresentInMyBubbleCondition, IsBallWithInDistanceCondition
from behaviors.conditions.blackboards import BlackboardMessageAndMyItemIdEqualCondition
from behaviors.monitors.ballparks import BubbleChangedMonitor
from behaviors.monitors.blackboards import BlackboardMessageMonitorBlocking
from behaviors.monitors.timers import StartTimerBlocks
from brennivin.itertoolsext import Bundle
from inventorycommon import const as invConst
WARP_TO_LOCATION_GROUP = (ScopeTypes.EntityGroup, 'WARP_TO_LOCATION_GROUP')
ANALYZE_OBJECT_TIMER = (ScopeTypes.Item, 'ANALYZE_OBJECT_TIMER')
ANALYZE_OBJECT_ID = (ScopeTypes.Item, 'ANALYZE_OBJECT_ID')
ANALYZE_CONSIDER_LIST = (ScopeTypes.Item, 'ANALYZE_CONSIDER_LIST')
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
SCANNER_STRETCH_EFFECT = 'effects.SleeperScannerStretch'
SCANNER_SHIP_EFFECT = 'effects.SleeperScannerShip'
SCANNER_EFFECT_DURATION_MSEC = 10000

def CreateIdleBehavior():
    root = composites.PrioritySelector(Bundle(name='Idle'))
    root.AddSubTask(CreateAnalyzeBehavior())
    root.AddSubTask(CreateIdleFallback())
    return root


def HaveAValidTarget(targetAddress = None, maxDistance = None):
    isValidTargetRoot = composites.Sequence(Bundle(name='Has Valid Target?'))
    isValidTargetRoot.AddSubTask(BlackboardMessageMonitorBlocking(Bundle(messageAddress=targetAddress)))
    isValidTargetRoot.AddSubTask(IsBallPresentInMyBubbleCondition(Bundle(ballIdAddress=targetAddress)))
    isValidTargetRoot.AddSubTask(IsBallWithInDistanceCondition(Bundle(ballIdAddress=targetAddress, maxDistance=maxDistance)))
    return isValidTargetRoot


def CreateAnalyzeBehavior():
    analyzeRoot = composites.Sequence(Bundle(name='Analyze Objects'))
    analyzeRoot.AddSubTask(BubbleChangedMonitor(Bundle()))

    def SelectTargetAction(scanDistance):
        return SelectTargetToAnalyzeAction(Bundle(selectedTargetAddress=ANALYZE_OBJECT_ID, maxDistance=scanDistance, ignoredCategories=[], ignoredGroups=IGNORED_GROUPS, ignoredTypes=IGNORED_TYPES, shouldIgnoreMobileTargets=False))

    def SelectTargetToAnalyze(scanDistance):
        node = composites.Sequence(Bundle(name='Select Analyze Target'))
        node.AddSubTask(StartTimerBlocks(Bundle(timeoutSeconds=30.0, timerAddress=ANALYZE_OBJECT_TIMER)))
        node.AddSubTask(SelectTargetAction(scanDistance))
        return node

    def PickObjectToAnalyze():
        pickObjectRoot = composites.PrioritySelector(Bundle(name='Pick Object'))
        scanDistance = 75000
        pickObjectRoot.AddSubTask(SelectTargetToAnalyze(scanDistance))
        pickObjectRoot.AddSubTask(HaveAValidTarget(targetAddress=ANALYZE_OBJECT_ID, maxDistance=scanDistance))
        pickObjectRoot.AddSubTask(SelectTargetAction(scanDistance))
        return pickObjectRoot

    analyzeRoot.AddSubTask(PickObjectToAnalyze())
    analyzeRoot.AddSubTask(OrbitAtDistanceAction(Bundle(orbitTargetAddress=ANALYZE_OBJECT_ID, orbitRange=4000.0, blocking=True, blockUntilRange=7000)))
    analyzeRoot.AddSubTask(effects.PlayOneShotStretchEffectAction(Bundle(effectDuration=SCANNER_EFFECT_DURATION_MSEC, effectName=SCANNER_STRETCH_EFFECT, effectTargetAddress=ANALYZE_OBJECT_ID)))
    analyzeRoot.AddSubTask(effects.PlayOneShotTargetedShipEffectAction(Bundle(effectDuration=SCANNER_EFFECT_DURATION_MSEC, effectName=SCANNER_SHIP_EFFECT, effectTargetAddress=ANALYZE_OBJECT_ID)))
    analyzeRoot.AddSubTask(SucceedAfterTimeoutAction(Bundle(timeoutSeconds=SCANNER_EFFECT_DURATION_MSEC / 1000.0)))
    return analyzeRoot


def CreateIdleFallback():
    fallbackRoot = composites.Sequence(Bundle(name='Idle Fallback'))

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

    fallbackRoot.AddSubTask(CreateSelectPointBehavior())
    fallbackRoot.AddSubTask(ApproachCoordinatesAction(Bundle(coordinateAddress=IDLE_GOTO_POINT, notifyRange=1000.0, blocking=True)))

    def PickAnchor():
        pickAnchorRoot = composites.PrioritySelector(Bundle(name='Pick Anchor'))
        pickAnchorRoot.AddSubTask(HaveAValidTarget(targetAddress=IDLE_ANCHOR, maxDistance=40000))
        pickAnchorRoot.AddSubTask(BlackboardSendMyItemIdMessageAction(Bundle(messageAddress=IDLE_ANCHOR)))
        return pickAnchorRoot

    fallbackRoot.AddSubTask(PickAnchor())

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

    fallbackRoot.AddSubTask(AnchorOrOrbit())
    return fallbackRoot


def CreateAnalyzeTree():
    tree = BehaviorTree()
    tree.StartRootTask(CreateAnalyzeBehavior())
    return tree
