#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\ballparks.py
import logging
import math
from random import choice, random, randint
import geo2
import evetypes
import gametime
import uthread2
from ballpark.const import DESTINY_MODE_WARP
from ballpark.locationgenerator import GetRandomDeepSpaceLocation, GetRandomPlacementNearRandomPlanet
from ballpark.messenger.const import MESSAGE_ON_BALL_MODE_CHANGED
from ballpark.warpDisruptionBalls import GetWarpBubbleItemIdsWithinRangeOfBall
from behaviors import status
from behaviors.behaviortree import UnrecoverableBehaviorError
from behaviors.blackboards import scopes
from behaviors.const.combat import COMBAT_ORBIT_MWD_DISTANCE_FACTOR_SHORT_DISTANCE, COMBAT_ORBIT_MWD_DISTANCE_THRESHOLD
from behaviors.const.combat import COMBAT_ORBIT_MWD_DISTANCE_MAXIMUM, COMBAT_ORBIT_COMMANDER_VELOCITY_FACTOR
from behaviors.const.combat import COMBAT_ORBIT_MWD_DISTANCE_MINIMUM, COMBAT_ORBIT_MWD_DISTANCE_FACTOR_LONG_DISTANCE
from behaviors.entity import NPCWarpError, NpcWarpScrambledError, NpcWarpBubbledError, NpcWarpPathBubbledError
from behaviors.exceptions import BehaviorAuthoringException
from behaviors.tasks import Task, BlockingTask
from behaviors.utility.ballparks import check_ball_released, get_balls_in_bubble, get_ball, is_ball_in_range
from behaviors.utility.ballparks import get_ball_position, is_ball_in_park, get_ball_warp_to_position
from behaviors.utility.ballparks import get_id_and_types_in_bubble_by_typelist
from behaviors.utility.ballparks import get_slim_item
from behaviors.utility.dogmatic import get_type_attribute_value
from behaviors.utility.inventory import get_inventory_item
from behaviors.utility.roles import is_commander, has_combat_role
from brennivin.itertoolsext import Bundle
from carbon.common.lib.const import SEC
from carbon.common.script.util import mathCommon
from carbon.common.script.util.mathCommon import RandomVector
from ccpProfile import TimedFunction
from dogma.const import attributeEntityCruiseSpeed, attributeMaxVelocity
from dogma.const import attributeWarpSpeedMultiplier
from eve.common.lib.appConst import AU
from eve.common.script.sys.idCheckers import IsEvePlayerCharacter
from eveexceptions import UserError
from eveuniverse.security import SecurityClassFromLevel, securityClassZeroSec
from inventorycommon.const import categoryCharge, groupStargate, groupStation
from spacecomponents.common.componentConst import NPC_WARP_BEACON, STORE_SLIM_ITEM_FIELD_IN_ITEM_SETTINGS
from spacecomponents.common.helper import HasStoreSlimItemFieldInItemSettingsComponent
from spacecomponents.server.components.storeslimitemfieldinitemsettings import StoreSlimItemFieldInItemSettings
logger = logging.getLogger(__name__)
ADDITIONAL_EXPLORATION_GROUPS = (scopes.ScopeTypes.EntityGroup, 'ADDITIONAL_EXPLORATION_GROUPS')
ADDITIONAL_EXPLORATION_ACTION = (scopes.ScopeTypes.EntityGroup, 'ADDITIONAL_EXPLORATION_ACTION')
ALIGN_START_TIME = (scopes.ScopeTypes.Item, 'ALIGN_START_TIME')
ALIGN_DIRECTION_NORMAL = (scopes.ScopeTypes.Item, 'ALIGN_DIRECTION_NORMAL')
UNSAFE_EXPLORATION_GROUPS = [groupStargate, groupStation]

class WarpToNewLocation(BlockingTask):

    @TimedFunction('behaviors::actions::ballparks::WarpToNewLocation::OnEnter')
    def OnEnter(self):
        super(WarpToNewLocation, self).OnEnter()
        self.SetStatusToFailed()
        coordinate = self.GetDestinationCoordinate()
        jitterRadius = self.GetJitterRadius()
        warpAtRange = self.GetWarpinDistance()
        warpSpeed = self.GetWarpSpeed()
        if coordinate:
            try:
                logger.debug('Behavior entity=%s is starting warp', self.context.myItemId)
                self.context.myBall.NPCWarpTo(coordinate, jitterRadius=jitterRadius, warpAtRange=warpAtRange, warpSpeed=warpSpeed)
                self.SubscribeItem(self.context.myItemId, MESSAGE_ON_BALL_MODE_CHANGED, self.DestinyModeChange)
                self.SendBlackboardValue(self.attributes.warpScrambledAddress, False)
                self.SetStatusToBlocked()
            except NpcWarpBubbledError:
                logger.debug('Behavior entity=%s is warp bubbled and cant warp anywhere', self.context.myItemId)
                self.SendBlackboardValue(self.attributes.warpScrambledAddress, True)
                self.context.myBall.NPCEndWarp()
            except NpcWarpScrambledError:
                logger.debug('Behavior entity=%s is warp scrambled and cant warp anywhere', self.context.myItemId)
                self.SendBlackboardValue(self.attributes.warpScrambledAddress, True)
                self.context.myBall.NPCEndWarp()
            except NpcWarpPathBubbledError:
                logger.debug('Behavior entity=%s path is warp bubbled', self.context.myItemId)
                self.context.myBall.NPCEndWarp()
            except NPCWarpError as e:
                logger.debug('Unable to warp: %s', e)
                try:
                    self.context.myBall.NPCEndWarp()
                except (UserError, NPCWarpError):
                    raise UnrecoverableBehaviorError('Unable to end after a failed warp.  Entity is probably dead.')

    def GetWarpSpeed(self):
        warpSpeed = self.context.ballpark.dogmaLM.GetAttributeValue(self.context.myItemId, attributeWarpSpeedMultiplier)
        if not warpSpeed or warpSpeed < 0.01:
            return 6.0
        return warpSpeed

    def GetDestinationCoordinate(self):
        return self.GetLastBlackboardValue(self.attributes.locationMessage)

    def DestinyModeChange(self, oldMode, newMode):
        if oldMode == DESTINY_MODE_WARP and self.context.ballpark is not None:
            self.UnsubscribeItem(self.context.myItemId, MESSAGE_ON_BALL_MODE_CHANGED, self.DestinyModeChange)
            self.SetStatusToSuccess()
            logger.debug('Behavior entity=%s is exiting warp', self.context.myItemId)

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeItem(self.context.myItemId, MESSAGE_ON_BALL_MODE_CHANGED, self.DestinyModeChange)
            self.SetStatusToInvalid()

    def GetJitterRadius(self):
        if hasattr(self.attributes, 'jitterRadius') and self.attributes.jitterRadius is not None:
            return self.attributes.jitterRadius
        else:
            return 20000

    def GetWarpinDistance(self):
        if self.HasAttribute('warpAtDistanceAddress'):
            valueFromAddress = self.GetLastBlackboardValue(self.attributes.warpAtDistanceAddress)
            if valueFromAddress is None:
                logger.debug('Behavior entity=%s has a warp distance address, but the value is None. Defaulting to 0.0', self.context.myItemId)
            else:
                return valueFromAddress
        return 0.0


class WarpToItem(WarpToNewLocation):

    def GetDestinationCoordinate(self):
        item_id = self.GetLastBlackboardValue(self.attributes.warpToItemIdAddress)
        if item_id is None:
            return
        if not is_ball_in_park(self, item_id):
            return
        coordinate = self.context.ballpark.GetWarpDestinationPoint(self.context.myItemId, item_id)
        return coordinate


class SelectCoordinateNearLocationAction(Task):

    @TimedFunction('behaviors::actions::ballparks::SelectCoordinateNearLocationAction::OnEnter')
    def OnEnter(self):
        locationID = self.GetLastBlackboardValue(self.attributes.locationAddress)
        referenceCoordinates = self.GetReferenceCoordinates(locationID)
        selectedCoordinates = self.ComputeRandomCoordinate(referenceCoordinates)
        self.SendBlackboardValue(self.attributes.coordinateAddress, selectedCoordinates)
        self.status = status.TaskSuccessStatus

    def GetReferenceCoordinates(self, locationID):
        if locationID is None:
            loc = (self.context.myBall.x, self.context.myBall.y, self.context.myBall.z)
        else:
            loc = self.GetLocation(locationID)
        return loc

    def ComputeRandomCoordinate(self, locationCoordinates):
        offset = mathCommon.RandomVector(self.attributes.maxDistance, self.attributes.maxDistance - self.attributes.minDistance)
        selectedCoordinates = geo2.Vec3AddD(locationCoordinates, offset)
        return selectedCoordinates

    def GetLocation(self, locationID):
        loc = cfg.evelocations.Get(locationID)
        return (loc.x, loc.y, loc.z)


class SelectCoordinateNearCoordinateAction(Task):

    @TimedFunction('behaviors::actions::ballparks::SelectCoordinateNearCoordinateAction::OnEnter')
    def OnEnter(self):
        sourcePoint = self._GetSourceCoordinates()
        selectedCoordinates = self.ComputeRandomCoordinate(sourcePoint or self.context.myBall.GetPosition())
        self.SendBlackboardValue(self.attributes.destinationCoordinateAddress, selectedCoordinates)
        self.status = status.TaskSuccessStatus

    def _GetSourceCoordinates(self):
        return self.GetLastBlackboardValue(self.attributes.sourceCoordinateAddress)

    def ComputeRandomCoordinate(self, locationCoordinates):
        offset = mathCommon.RandomVector(self.attributes.maxDistance, self.attributes.maxDistance - self.attributes.minDistance)
        selectedCoordinates = geo2.Vec3AddD(locationCoordinates, offset)
        return selectedCoordinates


class SelectCoordinateNearBall(SelectCoordinateNearCoordinateAction):

    def _GetSourceCoordinates(self):
        ball_id = self.GetLastBlackboardValue(self.attributes.targetBallAddress)
        ball = get_ball(self, ball_id)
        return (ball.x, ball.y, ball.z)


class ApproachCoordinatesAction(Task):

    @TimedFunction('behaviors::actions::ballparks::ApproachCoordinatesAction::OnEnter')
    def OnEnter(self):
        coordinate = self.GetLastBlackboardValue(self.attributes.coordinateAddress)
        if coordinate is None:
            self.status = status.TaskFailureStatus
            return
        if self.attributes.blocking:
            self.context.myBall.GotoPoint(coordinate, notificationRange=self.attributes.notifyRange, callback=(self.OnApproachNotify, ()))
            self.status = status.TaskSuspendedStatus
        else:
            self.context.myBall.GotoPoint(coordinate)
            self.status = status.TaskSuccessStatus

    def OnApproachNotify(self, entered, *args):
        logger.debug('OnApproachNotify(%s)', (entered, self.behaviorTree, self.context))
        self.context.myBall.StopMovementEvents()
        if self.status is not status.TaskInvalidStatus:
            self.status = status.TaskSuccessStatus
            self.status.OnUpdated(self)


def clampBetween(value, low, high):
    return max(min(value, high), low)


class AlignToCoordinatesAction(Task):

    @TimedFunction('behaviors::actions::ballparks::AlignToCoordinatesAction::OnEnter')
    def OnEnter(self):
        self.SendBlackboardValue(ALIGN_START_TIME, gametime.GetSimTime())
        self._MakeSureTargetPointIsFarAway()
        self.SetStatusToRunning()

    def _MakeSureTargetPointIsFarAway(self):
        minDist = 30000
        coordinate = self.GetLastBlackboardValue(self.attributes.coordinateAddress)
        myPos = self.context.myBall.GetPosition()
        direction = geo2.Vec3SubtractD(coordinate, myPos)
        if geo2.Vec3LengthSqD(direction) < minDist * minDist:
            normalizedDirection = geo2.Vec3NormalizeD(direction)
            scaledDirection = geo2.Vec3ScaleD(normalizedDirection, minDist)
            coordinate = geo2.Vec3AddD(myPos, scaledDirection)
            self.SendBlackboardValue(self.attributes.coordinateAddress, coordinate)

    def _HasTimedOut(self):
        timeOutSec = getattr(self.attributes, 'timeoutSeconds', 60.0)
        startTime = self.GetLastBlackboardValue(ALIGN_START_TIME)
        current_time = gametime.GetSimTime()
        return current_time - startTime > timeOutSec * SEC

    def _HasSuccessfullyAligned(self, alignDirectionNormal):
        acceptableDeviation = getattr(self.attributes, 'acceptableAngleDeviationDegrees', 1.0)
        fighterDirectionNormal = geo2.Vec3NormalizeD((self.context.myBall.vx, self.context.myBall.vy, self.context.myBall.vz))
        dotProduct = geo2.Vec3DotD(alignDirectionNormal, fighterDirectionNormal)
        dotProduct = clampBetween(dotProduct, -1.0, 1.0)
        angle = math.acos(dotProduct)
        return math.degrees(angle) < acceptableDeviation

    def _StopMovement(self):
        self.context.myBall.StopMovement()

    def _UpdateGotoPointAndReturnNormalizedDirection(self):
        coordinate = self.GetLastBlackboardValue(self.attributes.coordinateAddress)
        if coordinate is None:
            self.SetStatusToFailed()
            return
        myPos = self.context.myBall.GetPosition()
        direction = geo2.Vec3SubtractD(coordinate, myPos)
        normalizedDirection = geo2.Vec3NormalizeD(direction)
        gotoDistance = 5000.0
        gotoVector = geo2.Vec3ScaleD(normalizedDirection, gotoDistance)
        gotoPoint = geo2.Vec3AddD(myPos, gotoVector)
        self.context.myBall.GotoPoint(gotoPoint)
        return normalizedDirection

    def Update(self):
        normalizedDirection = self._UpdateGotoPointAndReturnNormalizedDirection()
        if self._HasSuccessfullyAligned(normalizedDirection):
            self.SetStatusToSuccess()
            self._StopMovement()
        elif self._HasTimedOut():
            self.SetStatusToFailed()
            self._StopMovement()

    def CleanUp(self):
        if not self.IsRunning():
            self.SetStatusToInvalid()


class ApproachObject(Task):

    @TimedFunction('behaviors::actions::ballparks::ApproachObject::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        itemId = self.GetLastBlackboardValue(self.attributes.itemIdAddress)
        if itemId is None:
            return
        if not self.context.ballpark.HasBall(itemId):
            return
        approachRange = self._GetApproachRange()
        if self.attributes.blocking:
            notifyRange = max(self.attributes.notifyRange, approachRange)
            self.context.myBall.ApproachObject(itemId, notificationRange=notifyRange, approachRange=approachRange, callback=(self.OnApproachNotify, ()))
            self.SetStatusToSuspended()
        else:
            self.context.myBall.ApproachObject(itemId, approachRange=approachRange)
            self.SetStatusToSuccess()

    def _GetApproachRange(self):
        if getattr(self.attributes, 'approachRangeAddress', None):
            return self.GetLastBlackboardValue(self.attributes.approachRangeAddress)
        return self.attributes.approachRange

    def OnApproachNotify(self, entered, *args):
        logger.debug('OnApproachNotify(%s)', (entered, self.behaviorTree, self.context))
        self.context.myBall.StopMovementEvents()
        if not self.IsInvalid():
            self.SetStatusToSuccess()
            self.status.OnUpdated(self)


class OrbitAtDistanceAction(Task):

    def OrbitNonBlocking(self, orbitTargetId, orbitRange):
        self.context.myBall.OrbitObject(orbitTargetId, approachRange=orbitRange)
        self.status = status.TaskSuccessStatus

    @TimedFunction('behaviors::actions::ballparks::OrbitAtDistanceAction::OnEnter')
    def OnEnter(self):
        check_ball_released(self.context.myBall, raises=UnrecoverableBehaviorError)
        orbitTargetId = self.GetLastBlackboardValue(self.attributes.orbitTargetAddress)
        if orbitTargetId is None:
            self.SetStatusToFailed()
            return
        if not self.context.ballpark.HasBall(orbitTargetId):
            self.SetStatusToFailed()
            return
        try:
            orbitRange = self._GetOrbitRange()
            if self.attributes.blocking:
                self.OrbitBlocking(orbitTargetId, orbitRange)
            else:
                self.OrbitNonBlocking(orbitTargetId, orbitRange)
            self._set_velocity_fraction()
        except UserError:
            self.SetStatusToFailed()

    def _GetOrbitRange(self):
        if getattr(self.attributes, 'orbitRangeAddress', None):
            return self.GetLastBlackboardValue(self.attributes.orbitRangeAddress)
        if getattr(self.attributes, 'orbitRange', None):
            return self.attributes.orbitRange
        raise BehaviorAuthoringException('BehaviorID: %s has no orbit range defined for task: %s', self.behaviorTree.GetBehaviorId(), type(self).__name__)

    def OrbitBlocking(self, orbitTargetId, orbitRange):
        if getattr(self.attributes, 'blockUntilRangeAddress', None):
            blockUntilRange = self.GetLastBlackboardValue(self.attributes.blockUntilRangeAddress)
        else:
            blockUntilRange = self.attributes.blockUntilRange or 1000.0
        self.context.myBall.OrbitObject(orbitTargetId, approachRange=orbitRange, notificationRange=blockUntilRange, callback=(self.OnInOrbitNotify, ()))
        self.status = status.TaskSuspendedStatus

    def OnInOrbitNotify(self, entered, *args):
        logger.debug('OnInOrbitNotify(%s)', (entered, self.behaviorTree, self.context))
        self.context.myBall.StopMovementEvents()
        if not self.IsInvalid():
            self.SetStatusToSuccess()
            self.status.OnUpdated(self)

    def _set_velocity_fraction(self):
        if self.HasAttribute('velocityFraction'):
            self.context.ballpark.SetSpeedFraction(self.context.myItemId, self.attributes.velocityFraction)

    def CleanUp(self):
        if not self.IsInvalid() and self.HasAttribute('velocityFraction'):
            self.context.ballpark.SetSpeedFraction(self.context.myItemId, 1.0)
        self.SetStatusToInvalid()


class FullStopAction(Task):

    @TimedFunction('behaviors::actions::ballparks::FullStopAction::OnEnter')
    def OnEnter(self):
        self.context.myBall.StopMovement()
        self.status = status.TaskSuccessStatus


class SelectTargetToAnalyzeAction(Task):

    @TimedFunction('behaviors::actions::ballparks::SelectTargetToAnalyzeAction::OnEnter')
    def OnEnter(self):
        logger.debug('SelectTargetToAnalyzeAction starting')
        ballsInBubble = self.context.ballpark.bubbles.get(self.context.myBall.newBubbleId)
        self.status = status.TaskFailureStatus
        if not ballsInBubble:
            logger.error('No bubbles to pick from')
            return
        targetCandidates = self.GetTargetCandidates(ballsInBubble)
        logger.debug('Target Candidates for Analysis: %s' % targetCandidates)
        targetId = self.FindSuitableTarget(targetCandidates)
        if targetId is not None:
            self.SendBlackboardValue(self.attributes.selectedTargetAddress, targetId)
            self.status = status.TaskSuccessStatus
        else:
            logger.debug('no suitable target found')

    def GetTargetCandidates(self, ballsInBubble):
        targetCandidates = []
        for ballId in ballsInBubble.keys():
            if ballId <= 0:
                continue
            if self.context.myItemId == ballId:
                continue
            targetCandidates.append(ballId)

        return targetCandidates

    def FindSuitableTarget(self, targetCandidates):
        targetId = None
        maxDistance = self.attributes.maxDistance
        GetSurfaceDist = self.context.ballpark.GetSurfaceDist
        getSlim = self.context.ballpark.slims.get
        ignoredCategories = self.attributes.ignoredCategories
        ignoredGroups = self.attributes.ignoredGroups
        ignoredTypes = self.attributes.ignoredTypes
        shouldIgnoreMobileTargets = self.attributes.shouldIgnoreMobileTargets
        while targetId is None and targetCandidates:
            index = randint(0, len(targetCandidates) - 1)
            ballId = targetCandidates.pop(index)
            slimItem = getSlim(ballId)
            if slimItem is None:
                continue
            if slimItem.categoryID in ignoredCategories:
                continue
            if slimItem.groupID in ignoredGroups:
                continue
            if slimItem.typeID in ignoredTypes:
                continue
            ball = self.context.ballpark.GetBall(ballId)
            if ball.isCloaked:
                continue
            if shouldIgnoreMobileTargets and ball.isFree:
                continue
            distance = GetSurfaceDist(self.context.myItemId, ballId)
            if distance and distance <= maxDistance:
                targetId = ballId

        return targetId


class GetBallWarpToLocation(Task):

    @TimedFunction('behaviors::actions::ballparks::GetBallWarpToLocation::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        ballId = self.GetLastBlackboardValue(self.attributes.ballIdAddress)
        if ballId is None:
            return
        try:
            self.context.ballpark.CheckBall(self.context.myItemId)
        except (UserError, RuntimeError):
            raise UnrecoverableBehaviorError('Entity no longer in ballpark. Probably dead.')

        position = get_ball_warp_to_position(self, ballId)
        self.SendBlackboardValue(self.attributes.locationAddress, position)
        self.SetStatusToSuccess()


class GetItemIdByTypeId(Task):

    @TimedFunction('behaviors::actions::ballparks::GetItemIdByTypeId::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        if not self.attributes.typeIds:
            return
        itemId = self.GetItemIdFromBallpark(self.context.myBall.id, self.attributes.typeIds)
        if itemId:
            self.SendBlackboardValue(self.attributes.itemIdAddress, itemId)
            self.SetStatusToSuccess()

    def GetItemIdFromBallpark(self, myBallId, typeIds):
        itemId = None
        getSlim = self.context.ballpark.slims.get
        itemsInBubble = self.context.ballpark.GetItemsInBubble(None, itemID=myBallId)
        while itemId is None and itemsInBubble:
            index = randint(0, len(itemsInBubble) - 1)
            ballId = itemsInBubble.pop(index)
            slimItem = getSlim(ballId)
            if slimItem is None:
                continue
            if slimItem.typeID not in typeIds:
                continue
            itemId = ballId

        return itemId


class GetItemIdByTypeIdsFromBlackboard(GetItemIdByTypeId):

    @TimedFunction('behaviors::actions::ballparks::GetItemIdByTypeId::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        if self.attributes.typeIdsAddress is None:
            return
        typeIds = self.GetLastBlackboardValue(self.attributes.typeIdsAddress)
        if not typeIds:
            return
        itemId = self.GetItemIdFromBallpark(self.context.myBall.id, typeIds)
        if itemId:
            self.SendBlackboardValue(self.attributes.itemIdAddress, itemId)
            self.SetStatusToSuccess()


class GetRandomDeepSpacePosition(Task):

    @TimedFunction('behaviors::actions::ballparks::GetRandomDeepSpacePosition::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        location = GetRandomDeepSpaceLocation(self.context.ballpark.solarsystemID, minPlacementDistance=500)
        if location:
            self.SendBlackboardValue(self.attributes.locationAddress, location)
            self.SetStatusToSuccess()


class GetRandomPositionNearRandomPlanet(Task):

    @TimedFunction('behaviors::actions::ballparks::GetRandomPositionNearRandomPlanet::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        location = GetRandomPlacementNearRandomPlanet(self.context.ballpark.solarsystemID, self.attributes.minDistanceAU * AU, self.attributes.maxDistanceAU * AU)
        if location:
            self.SendBlackboardValue(self.attributes.locationAddress, location)
            self.SetStatusToSuccess()


class TransferToLocation(Task):

    @TimedFunction('behaviors::actions::ballparks::TransferToLocation::OnEnter')
    def OnEnter(self):
        self.status = status.TaskFailureStatus
        location = self.GetLastBlackboardValue(self.attributes.locationAddress)
        if location:
            self.context.ballpark.ChangeBallPosition(self.context.myBall.id, *location)
            self.status = status.TaskSuccessStatus


class GetObjectSpaceLocation(Task):

    @TimedFunction('behaviors::actions::ballparks::GetObjectSpaceLocation::OnEnter')
    def OnEnter(self):
        itemId = self.GetLastBlackboardValue(self.attributes.itemIdAddress)
        if not itemId:
            self.status = status.TaskFailureStatus
            return
        location = self.context.ballpark.GetBallPosition(itemId)
        self.SendBlackboardValue(self.attributes.locationAddress, location)
        self.status = status.TaskSuccessStatus


class MakeSelfInvulnerable(Task):

    @TimedFunction('behaviors::actions::ballparks::MakeSelfInvulnerable::OnEnter')
    def OnEnter(self):
        self.context.ballpark.MakeInvulnerablePermanently(self.context.myBall.id, self.attributes.reason)
        self.status = status.TaskSuccessStatus


class CancelInvulnerabilityForSelf(Task):

    @TimedFunction('behaviors::actions::ballparks::CancelInvulnerabilityForSelf::OnEnter')
    def OnEnter(self):
        self.context.ballpark.CancelCurrentInvulnerability(self.context.myBall.id, self.attributes.reason)
        self.status = status.TaskSuccessStatus


class Cloak(Task):

    @TimedFunction('behaviors::actions::ballparks::Cloak::OnEnter')
    def OnEnter(self):
        self.context.ballpark.CloakShip(self.context.myItemId)
        self.status = status.TaskSuccessStatus


class Uncloak(Task):

    @TimedFunction('behaviors::actions::ballparks::Uncloak::OnEnter')
    def OnEnter(self):
        self.context.ballpark.UncloakShip(self.context.myItemId)
        self.status = status.TaskSuccessStatus


class SelectItemByTypes(Task):

    @TimedFunction('behaviors::actions::ballparks::SelectItemByTypes::OnEnter')
    def OnEnter(self):
        ballpark = self.context.ballpark
        bubbleId = self.context.myBall.newBubbleId
        ballIdsInBubble = ballpark.bubbles.get(bubbleId)
        self.status = status.TaskFailureStatus
        if ballIdsInBubble:
            selectedItem = self.FindItemByType(ballIdsInBubble, ballpark.slims)
            if selectedItem is not None:
                self.SendBlackboardValue(self.attributes.selectedItemAddress, selectedItem)
                self.status = status.TaskSuccessStatus

    def FindItemByType(self, ballIdsInBubble, slims):
        for ballId in ballIdsInBubble:
            slim = slims.get(ballId)
            if slim and slim.typeID in self.attributes.typeIds:
                return ballId


class SelectItemByGroups(Task):

    @TimedFunction('behaviors::actions::ballparks::SelectItemByTypes::OnEnter')
    def OnEnter(self):
        ballpark = self.context.ballpark
        bubbleId = self.context.myBall.newBubbleId
        ballIdsInBubble = ballpark.bubbles.get(bubbleId)
        self.status = status.TaskFailureStatus
        if ballIdsInBubble:
            selectedItem = self.FindItemByGroup(ballIdsInBubble, ballpark.slims)
            if selectedItem is not None:
                self.SendBlackboardValue(self.attributes.selectedItemAddress, selectedItem)
                self.status = status.TaskSuccessStatus

    def FindItemByGroup(self, ballIdsInBubble, slims):
        for ballId in ballIdsInBubble:
            slim = slims.get(ballId)
            if slim and slim.groupID in self.attributes.groupIds:
                return ballId


class StoreSunToBlackboardValue(Task):

    @TimedFunction('behaviors::actions::ballparks::SelectItemByTypes::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        sunID = self.context.ballpark.sunID
        if sunID:
            self.SendBlackboardValue(self.attributes.targetAddress, sunID)
            self.status = status.TaskSuccessStatus
            self.SetStatusToSuccess()


class BallNotInParkError(Exception):
    pass


class SelectClosestPointOnObject(Task):

    @TimedFunction('behaviors::actions::ballparks::SelectClosestPointOnObject::OnEnter')
    def OnEnter(self):
        objectId = self.GetLastBlackboardValue(self.attributes.objectIdAddress)
        try:
            closestSphere = self.GetClosestSphere(objectId)
            closestPoint = self.GetClosestSurfacePoint(closestSphere)
            self.SendBlackboardValue(self.attributes.closestPointAddress, closestPoint)
            self.status = status.TaskSuccessStatus
        except KeyError:
            self.status = status.TaskFailureStatus

    def GetClosestSphere(self, objectId):
        ball = self.context.ballpark.balls[objectId]
        pos = (ball.x, ball.y, ball.z)
        myPos = (self.context.myBall.x, self.context.myBall.y, self.context.myBall.z)
        if len(ball.miniBalls) == 0:
            return Bundle(pos=(ball.x, ball.y, ball.z), radius=ball.radius)

        def GetDistance(m):
            miniPos = (m.x, m.y, m.z)
            return geo2.Vec3DistanceD(myPos, geo2.Vec3AddD(pos, miniPos))

        miniBall = sorted(ball.miniBalls, key=GetDistance)[0]
        return Bundle(pos=geo2.Vec3AddD(pos, (miniBall.x, miniBall.y, miniBall.z)), radius=miniBall.radius)

    def GetClosestSurfacePoint(self, otherSphere):
        myPos = (self.context.myBall.x, self.context.myBall.y, self.context.myBall.z)
        vecToOther = geo2.Vec3SubtractD(otherSphere.pos, myPos)
        distanceToOther = geo2.Vec3LengthD(vecToOther)
        vecToPoint = geo2.Vec3ScaleD(vecToOther, 1.0 - otherSphere.radius / distanceToOther)
        return geo2.Vec3AddD(myPos, vecToPoint)


class GetBallsInBubbleByOwnerIds(Task):

    @TimedFunction('behaviors::actions::ballparks::GetBallsInBubbleByOwnerIds::OnEnter')
    def OnEnter(self):
        ballIds = self.GetBallsInBubbleForOwnerIds()
        self.UpdateObjectList(ballIds)
        self.status = status.TaskSuccessStatus

    def GetBallsInBubbleForOwnerIds(self):
        shipBallsInBubble = self.context.ballpark.GetShipsInSameBubble(self.context.myItemId)
        ownerIds = self.GetLastBlackboardValue(self.attributes.ownerListAddress)
        ballIds = set()
        for shipBallId in shipBallsInBubble:
            slim = self.context.ballpark.slims.get(shipBallId)
            if slim.ownerID in ownerIds:
                ballIds.add(shipBallId)

        return ballIds

    def UpdateObjectList(self, ballIds):
        if not ballIds:
            return
        existingBallIds = self.GetExistingBallIds()
        if ballIds.issubset(existingBallIds):
            return
        existingBallIds.update(ballIds)
        self.SendBlackboardValue(self.attributes.objectListAddress, existingBallIds)

    def GetExistingBallIds(self):
        return self.GetLastBlackboardValue(self.attributes.objectListAddress) or set()


class EntityLootItem(Task):

    @TimedFunction('behaviors::actions::ballparks::EntityLootItem::OnEnter')
    def OnEnter(self):
        itemId = self.GetItemForCollecting()
        if itemId:
            item = self.context.ballpark.inventory2.GetItem(itemId)
            self.context.ballpark.RemoveItemFromPark(item)
            self.AddObjectToLoot(item)
            self.status = status.TaskSuccessStatus
        else:
            self.status = status.TaskFailureStatus

    def GetItemForCollecting(self):
        return self.GetLastBlackboardValue(self.attributes.itemIdAddress)

    def AddObjectToLoot(self, item):
        logger.debug('Entity: %s looting typeId: %s & itemId: %s from park.' % (self.context.myBall.id, item.typeID, item.itemID))
        self.context.myBall.AddTypeAndAmountToAdditionalLoot(item.typeID)

    def SetChannel(self, context):
        self.channel = scopes.GetChannelFromAddress(context, self.attributes.itemIdAddress)


class StoreSlimItemFieldInItemSettingsAction(Task):

    @TimedFunction('behaviors::actions::ballparks::StoreSlimItemFieldInItemSettingsAction::OnEnter')
    def OnEnter(self):
        targetId = self.GetLastBlackboardValue(self.attributes.targetAddress)
        if targetId is None:
            logger.info('StoreSlimItemFieldInItemSettingsAction::Failed to get targetID from blackboard')
            self.SetStatusToFailed()
            return
        targetSlimItem = self.context.ballpark.slims.get(targetId, None)
        if targetSlimItem is None:
            logger.info('StoreSlimItemFieldInItemSettingsAction::Ball not in park')
            self.SetStatusToFailed()
            return
        if not HasStoreSlimItemFieldInItemSettingsComponent(targetSlimItem.typeID):
            logger.error('StoreSlimItemFieldInItemSettingsAction::Trying to set persistent pose for type %s which does not have the persistent pose spacecomponent attached.', targetSlimItem.typeID)
            self.SetStatusToFailed()
            return
        slimItemFieldName = self.GetLastBlackboardValue(self.attributes.slimItemFieldName)
        if slimItemFieldName is None:
            logger.info('StoreSlimItemFieldInItemSettingsAction::Failed to get slim item field name from blackboard')
            self.SetStatusToFailed()
            return
        if slimItemFieldName not in StoreSlimItemFieldInItemSettings.GetPersistentSlimItemAttributesForType(targetSlimItem.typeID):
            logger.info("StoreSlimItemFieldInItemSettingsAction::Can't modify field '%s' as it is not listed as one of the persistent fields on the space component.", slimItemFieldName)
            self.SetStatusToFailed()
            return
        slimItemFieldValue = self.GetLastBlackboardValue(self.attributes.slimItemFieldValue)
        if slimItemFieldValue is None:
            logger.info('StoreSlimItemFieldInItemSettingsAction::Failed to get slim item field value from blackboard')
            self.SetStatusToFailed()
            return
        persistentPoseComponent = self.context.ballpark.componentRegistry.GetComponentForItem(targetId, STORE_SLIM_ITEM_FIELD_IN_ITEM_SETTINGS)
        persistentPoseComponent.SaveSlimItemSetting(self.context.ballpark, slimItemFieldName, slimItemFieldValue)
        self.SetStatusToSuccess()


class StoreBlackboardToSlimItemAttribute(Task):

    @TimedFunction('behaviors::actions::ballparks::StoreBlackboardToSlimItemAttribute::OnEnter')
    def OnEnter(self):
        targetId = self.GetLastBlackboardValue(self.attributes.targetAddress)
        message = self.GetLastBlackboardValue(self.attributes.messageAddress)
        self.context.ballpark.UpdateSlimItemField(targetId, self.attributes.attributeName, message)
        self.SetStatusToSuccess()


class StoreSlimItemAttributeToBlackboard(Task):

    @TimedFunction('behaviors::actions::ballparks::StoreSlimItemAttributeToBlackboard::OnEnter')
    def OnEnter(self):
        targetId = self.GetLastBlackboardValue(self.attributes.targetAddress)
        slimItem = self.context.ballpark.slims.get(targetId)
        attributeValue = getattr(slimItem, self.attributes.attributeName, None)
        self.SendBlackboardValue(self.attributes.messageAddress, attributeValue)
        self.SetStatusToSuccess()


class FindPointToEscapeWarpTo(Task):

    @TimedFunction('behaviors::actions::ballparks::FindPointToEscapeWarpTo::OnEnter')
    def OnEnter(self):
        location = self.SelectLocation()
        if location:
            self.SendBlackboardValue(self.attributes.locationMessage, location)
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def SelectLocation(self):
        return GetRandomPlacementNearRandomPlanet(self.context.ballpark.solarsystemID, 1000, 10000)


class FindPointToExplore(Task):

    @TimedFunction('behaviors::actions::ballparks::FindPointToExplore::OnEnter')
    def OnEnter(self):
        location = self.SelectLocation()
        if location:
            self.SendBlackboardValue(self.attributes.locationMessage, location)
            self.status = status.TaskSuccessStatus
        else:
            self.status = status.TaskFailureStatus

    def SelectLocation(self):
        generalList = self.GetGeneralList()
        specificList = self._GetSpecificDungeonEntryPointsOfInterest()
        if len(specificList) > 0 and (len(generalList) == 0 or random() < self.attributes.pickSpecificChance):
            result = self._GetPointToExplore(specificList)
        else:
            result = self._GetPointToExplore(generalList)
        return result

    def GetGeneralList(self):
        distributionOverwrite = self.GetLastBlackboardValue(ADDITIONAL_EXPLORATION_ACTION)
        if distributionOverwrite:
            return self._GetExplorationBallsFromDistribution()
        behavioralList = self._GetBallsOfInterestFromGlobals(self.attributes.groupsOfInterest)
        distributionList = self._GetExplorationBallsFromDistribution()
        warpBeaconsInSystem = self._GetWarpBeaconsInSystem()
        dungeonArchetypeList = self._GetDungeonArchetypeEntryPointsOfInterest()
        return list(set(behavioralList + distributionList + warpBeaconsInSystem + dungeonArchetypeList))

    def _GetPointToExplore(self, warpObjectList):
        if len(warpObjectList) > 0:
            hasNoValidLocation = True
            count = 0
            objectToWarpToo = None
            while hasNoValidLocation and count < 10:
                objectToWarpToo = choice(warpObjectList)
                hasNoValidLocation = self.context.ballpark.InSameBubble(objectToWarpToo.id, self.context.myBall.id)
                count += 1

            if objectToWarpToo:
                position = self.context.ballpark.GetWarpDestinationPoint(self.context.myBall.id, objectToWarpToo.id)
                return position
            else:
                return
        else:
            return

    def _GetExplorationBallsFromDistribution(self):
        additionalExplorationGroupIDs = self.GetLastBlackboardValue(ADDITIONAL_EXPLORATION_GROUPS)
        return self._GetBallsOfInterestFromGlobals(additionalExplorationGroupIDs)

    def _GetBallsOfInterestFromGlobals(self, groups):
        groups = groups or []
        categories = self._get_categories_of_interest()
        if not groups and not categories:
            return []
        safe_balls_of_interest = []
        for ballID, ball in self._get_all_global_balls():
            item = get_inventory_item(self, ballID)
            if self._is_ball_of_interest(item, groups, categories) and self._is_safe_to_visit(item):
                safe_balls_of_interest.append(ball)

        return safe_balls_of_interest

    def _GetWarpBeaconsInSystem(self):
        warpBeacons = self.context.ballpark.componentRegistry.GetInstancesWithComponentClass(NPC_WARP_BEACON)
        warpBeaconBalls = []
        for warpBeacon in warpBeacons:
            warpBeaconBalls.append(self.context.ballpark.GetBall(warpBeacon.itemID))

        return warpBeaconBalls

    def _GetDungeonArchetypeEntryPointsOfInterest(self):
        archetypes_of_interest = self._get_archetypes_of_interest()
        if archetypes_of_interest:
            if self.attributes.shouldConsiderUnspawnedDungeons:
                return self.context.keeper.GetInstalledDungeonEntryObjectsOfArchetype(self.context.solarSystemId, archetypes_of_interest)
            else:
                return self.context.keeper.GetDungeonEntryObjectsOfArchetype(self.context.solarSystemId, archetypes_of_interest)
        return []

    def _GetSpecificDungeonEntryPointsOfInterest(self):
        dungeons_interest = self._get_dungeons_of_interest()
        if dungeons_interest:
            if self.attributes.shouldConsiderUnspawnedDungeons:
                return self.context.keeper.GetInstalledDungeonEntryObjectsOfDungeonID(self.context.solarSystemId, dungeons_interest)
            else:
                return self.context.keeper.GetDungeonEntryObjectsOfDungeonID(self.context.solarSystemId, dungeons_interest)
        return []

    def _get_categories_of_interest(self):
        if self.HasAttribute('categoriesOfInterest'):
            return self.attributes.categoriesOfInterest
        return []

    def _get_archetypes_of_interest(self):
        if self.HasAttribute('dungeonArchetypesOfInterest'):
            return self.attributes.dungeonArchetypesOfInterest
        return []

    def _get_dungeons_of_interest(self):
        if self.HasAttribute('dungeonsOfInterest'):
            return self.attributes.dungeonsOfInterest
        return []

    def _get_all_global_balls(self):
        return self.context.ballpark.globals.iteritems()

    def _is_ball_of_interest(self, item, groups, categories):
        return item.groupID in groups or item.categoryID in categories

    def _is_safe_to_visit(self, item):
        if not self._should_avoid_unsafe_locations_in_empire_space():
            return True
        if item.groupID not in UNSAFE_EXPLORATION_GROUPS:
            return True
        if IsEvePlayerCharacter(item.ownerID):
            return True
        return SecurityClassFromLevel(self.context.ballpark.security) == securityClassZeroSec

    def _should_avoid_unsafe_locations_in_empire_space(self):
        if not self.HasAttribute('avoidUnsafeLocationsInEmpireSpace'):
            return False
        return self.attributes.avoidUnsafeLocationsInEmpireSpace


class GetBallGotoPointAction(Task):

    @TimedFunction('behaviors::actions::ballparks::GetBallGotoPointAction::OnEnter')
    def OnEnter(self):
        ballId = self.GetLastBlackboardValue(self.attributes.ballIdAddress)
        ball = self.context.ballpark.GetBall(ballId)
        gotoPoint = (ball.gotoX, ball.gotoY, ball.gotoZ)
        self.SendBlackboardValue(self.attributes.gotoPointAddress, gotoPoint)
        self.SetStatusToSuccess()


class ManageMicroWarpDriveToTarget(Task):

    def __init__(self, attributes):
        super(ManageMicroWarpDriveToTarget, self).__init__(attributes)
        self.microWarpDriveThread = None
        self.isActive = False

    @TimedFunction('behaviors::actions::ballparks::ManageMicroWarpDriveToTarget::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        self.targetId = self.GetLastBlackboardValue(self.attributes.targetAddress)
        if self.targetId is None or not self._IsTargetInSameBubble():
            return
        if self.microWarpDriveThread is None:
            self.microWarpDriveThread = uthread2.start_tasklet(self._ManageMicroWarpDrive)
        self.SetStatusToSuccess()

    def _IsTargetInSameBubble(self):
        return self.context.ballpark.InSameBubble(self.context.myItemId, self.targetId)

    def _ManageMicroWarpDrive(self):
        while not self.IsInvalid() and self._AreBallsStillThere():
            shouldMicroWarpDrive = self._ShouldMicroWarpDrive()
            if self.isActive != shouldMicroWarpDrive:
                self._SetMovementSpeed(shouldMicroWarpDrive)
            uthread2.SleepSim(self.attributes.microWarpDriveDuration / 1000)

        self.microWarpDriveThread = None

    def _AreBallsStillThere(self):
        if not self.context.ballpark.HasBall(self.targetId):
            return False
        if not self.context.ballpark.HasBall(self.context.myItemId):
            return False
        if self.context.ballpark.IsCloaked(self.targetId):
            return False
        return True

    def _ShouldMicroWarpDrive(self):
        if not self._IsOutsideMicroWarpDriveDistance():
            return False
        return random() < self.attributes.microWarpDriveChance

    def _IsOutsideMicroWarpDriveDistance(self):
        distance = self.context.ballpark.DistanceBetween(self.context.myItemId, self.targetId)
        microWarpdriveDistance = self._GetMicroWarpDriveDistance()
        return distance >= microWarpdriveDistance

    def _GetMicroWarpDriveDistance(self):
        orbitDistance = self.GetLastBlackboardValue(self.attributes.orbitRangeAddress)
        if orbitDistance < COMBAT_ORBIT_MWD_DISTANCE_THRESHOLD:
            microWarpdriveDistance = orbitDistance * COMBAT_ORBIT_MWD_DISTANCE_FACTOR_SHORT_DISTANCE
            return max(microWarpdriveDistance, COMBAT_ORBIT_MWD_DISTANCE_MINIMUM)
        else:
            microWarpdriveDistance = orbitDistance * COMBAT_ORBIT_MWD_DISTANCE_FACTOR_LONG_DISTANCE
            return min(microWarpdriveDistance, COMBAT_ORBIT_MWD_DISTANCE_MAXIMUM)

    def _SetMovementSpeed(self, shouldMicroWarpDrive):
        if shouldMicroWarpDrive:
            self.context.myBall.SetMovementSpeed(cruise=False)
        else:
            self.context.myBall.SetMovementSpeed(cruise=True)
        self.isActive = shouldMicroWarpDrive

    def CleanUp(self):
        if not self.IsInvalid():
            self.isActive = False
            self._SetMovementSpeed(False)
            self.SetStatusToInvalid()


class ManageMicroWarpDriveToCoordinates(ManageMicroWarpDriveToTarget):

    @TimedFunction('behaviors::actions::ballparks::ManageMicroWarpDriveToCoordinates::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        self.coordinates = self.GetLastBlackboardValue(self.attributes.coordinateAddress)
        if self.coordinates is None or not self._IsTargetInSameBubble():
            return
        if self.microWarpDriveThread is None:
            self.microWarpDriveThread = uthread2.start_tasklet(self._ManageMicroWarpDrive)
        self.SetStatusToSuccess()

    def _IsTargetInSameBubble(self):
        myBubbleId = self.context.myBall.newBubbleId
        bubbleIdAtCoordinates = self.context.ballpark.GetBubbleAtCoordinates(*self.coordinates)
        return myBubbleId == bubbleIdAtCoordinates

    def _AreBallsStillThere(self):
        return self.context.ballpark.HasBall(self.context.myItemId)

    def _IsOutsideMicroWarpDriveDistance(self):
        ballPosition = (self.context.myBall.x, self.context.myBall.y, self.context.myBall.z)
        distance = geo2.Vec3DistanceD(ballPosition, self.coordinates)
        microWarpdriveDistance = self._GetMicroWarpDriveDistance()
        return distance >= microWarpdriveDistance


class ModifyOrbitVelocity(Task):

    @TimedFunction('behaviors::actions::ballparks::ModifyOrbitVelocity::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        self.orbitVelocity = self.attributes.orbitVelocity
        customVelocity = self._GetCustomOrbitVelocity()
        if not customVelocity:
            entityVelocity = self.context.myBall.GetEntityVelocity()
            entityVelocity.set_custom_orbit_velocity(customVelocity)
        self.SetStatusToSuccess()

    def _GetCustomOrbitVelocity(self):
        if is_commander(self, self.context.myItemId):
            slowestVelocityOfGroup = self._GetSlowestOrbitVelocityOfGroup()
            if slowestVelocityOfGroup:
                return slowestVelocityOfGroup * COMBAT_ORBIT_COMMANDER_VELOCITY_FACTOR
            raise BehaviorAuthoringException('Behavior %d received None or 0 as slowest combat velocity' % self.behaviorTree.GetBehaviorId())
        return self.attributes.orbitVelocity

    def _GetSlowestOrbitVelocityOfGroup(self):
        slowestVelocityForGroup = None
        group = self.context.entityLocation.GetGroupManager().GetGroup(self.context.myEntityGroupId)
        for entityId in group.GetGroupMembers():
            entityItem = self.context.ballpark.inventory2.GetItem(entityId)
            if not has_combat_role(self, entityItem.itemID):
                continue
            entityTypeVelocity = self._GetOrbitVelocityForType(entityItem)
            if entityTypeVelocity and (slowestVelocityForGroup is None or entityTypeVelocity < slowestVelocityForGroup):
                slowestVelocityForGroup = entityTypeVelocity

        return slowestVelocityForGroup

    def _GetOrbitVelocityForType(self, entityItem):
        entityTypeCruiseSpeed = get_type_attribute_value(self, entityItem.typeID, attributeEntityCruiseSpeed)
        entityTypeMaxVelocity = get_type_attribute_value(self, entityItem.typeID, attributeMaxVelocity)
        return entityTypeCruiseSpeed or entityTypeMaxVelocity

    def CleanUp(self):
        if not self.IsInvalid():
            if self.orbitVelocity is not None:
                entityVelocity = self.context.myBall.GetEntityVelocity()
                entityVelocity.remove_custom_orbit_velocity()
            self.SetStatusToInvalid()


class SelectClosestItemAndTypeByEveTypeList(Task):

    @TimedFunction('behaviors::actions::ballparks::SelectClosestItemAndTypeByEveTypeList::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        logger.debug('SelectClosestItemAndTypeByEveTypeList starting')
        if self.HasValidTarget():
            self.SetStatusToSuccess()
            return
        closestItemId, closestTypeId = self.GetClosestItemAndTypeOfInterest()
        if closestItemId is not None:
            self._update_blackboards(closestItemId, closestTypeId)
            self.SetStatusToSuccess()
        else:
            logger.debug('no suitable target found')

    def GetClosestItemAndTypeOfInterest(self):
        ballsOfInterest = get_id_and_types_in_bubble_by_typelist(self.context.ballpark, self.context.myBall.newBubbleId, self.attributes.eveTypeListId)
        closestItemId = None
        closestTypeId = None
        closestDistance = 0
        for ballId, typeId in ballsOfInterest:
            distanceToBall = self.GetDistanceToBall(ballId)
            if not closestItemId or distanceToBall < closestDistance:
                closestItemId = ballId
                closestTypeId = typeId
                closestDistance = distanceToBall

        return (closestItemId, closestTypeId)

    def GetDistanceToBall(self, ballId):
        return self.context.ballpark.DistanceBetween(self.context.myBall.id, ballId)

    def HasValidTarget(self):
        targetId = self.GetLastBlackboardValue(self.attributes.selectedTargetAddress)
        if not targetId or not self.context.ballpark.HasBall(targetId):
            return False
        targetBall = self.context.ballpark.GetBall(targetId)
        return targetBall.newBubbleId == self.context.myBall.newBubbleId

    def _update_blackboards(self, closestItemId, closestTypeId):
        self.SendBlackboardValue(self.attributes.selectedTargetAddress, closestItemId)
        self.SendBlackboardValue(self.attributes.selectedTypeAddress, closestTypeId)


class SelectClosestItemByEveTypeList(SelectClosestItemAndTypeByEveTypeList):

    def _update_blackboards(self, closestItemId, _):
        self.SendBlackboardValue(self.attributes.selectedTargetAddress, closestItemId)


class GetBallLocation(Task):

    @TimedFunction('behaviors::actions::ballparks::GetBallLocation::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        targetBallId = self.GetLastBlackboardValue(self.attributes.ballIdAddress)
        if targetBallId and is_ball_in_park(self, targetBallId):
            targetBall = get_ball(self, targetBallId)
            targetCoordinates = (targetBall.x, targetBall.y, targetBall.z)
            self.SendBlackboardValue(self.attributes.coordinateAddress, targetCoordinates)
            self.SetStatusToSuccess()


class PostOwnPosition(Task):

    @TimedFunction('behaviors::actions::ballparks::PostOwnPosition::OnEnter')
    def OnEnter(self):
        position = (self.context.myBall.x, self.context.myBall.y, self.context.myBall.z)
        self.SendBlackboardValue(self.attributes.coordinateAddress, position)
        self.SetStatusToSuccess()


class GotoPosition(Task):

    @TimedFunction('behaviors::actions::ballparks::GotoPosition::OnEnter')
    def OnEnter(self):
        position = self.GetLastBlackboardValue(self.attributes.coordinateAddress)
        self.context.ballpark.GotoPoint(self.context.myItemId, *position)
        self.SetStatusToSuccess()


class GetItemIdsInBubbleWithinRange(Task):

    @TimedFunction('behaviors::actions::ballparks::GetItemIdsInBubbleWithinRange::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        center_ball_id = self._get_center_ball_id()
        if center_ball_id is None:
            self.SetStatusToFailed()
            return
        center_ball = get_ball(self, center_ball_id)
        balls_in_bubble = get_balls_in_bubble(self, center_ball.newBubbleId)
        balls_of_interest = self._get_balls_of_interest(center_ball_id, balls_in_bubble)
        self.SendBlackboardValue(self.attributes.ballsWithinRangeAddress, balls_of_interest)

    def _get_center_ball_id(self):
        if self.HasAttribute('centerBallAddress'):
            return self.GetLastBlackboardValue(self.attributes.centerBallAddress)
        return self.context.myItemId

    def _get_balls_of_interest(self, center_ball_id, balls_in_bubble):
        balls_of_interest = []
        for ball_id in balls_in_bubble.keys():
            slim_item = get_slim_item(self, ball_id)
            if not slim_item:
                continue
            if any((filter_function(slim_item) for filter_function in self._get_filter_functions())):
                if self._is_ball_within_range(center_ball_id, ball_id):
                    balls_of_interest.append(ball_id)

        return balls_of_interest

    def _get_filter_functions(self):
        return [self._is_ball_of_category_interest, self._is_ball_of_group_interest]

    def _is_ball_of_category_interest(self, slim_item):
        categories_of_interest = getattr(self.attributes, 'categoriesOfInterest', [])
        return slim_item.categoryID in categories_of_interest

    def _is_ball_of_group_interest(self, slim_item):
        groups_of_interest = getattr(self.attributes, 'groupsOfInterest', [])
        return slim_item.groupID in groups_of_interest

    def _is_ball_within_range(self, center_ball_id, target_ball_id):
        if self.HasAttribute('maxDistanceAddress'):
            max_distance = self.GetLastBlackboardValue(self.attributes.maxDistanceAddress)
        elif self.HasAttribute('maxDistance'):
            max_distance = self.attributes.maxDistance
        else:
            raise BehaviorAuthoringException('Behavior Task: GetItemIdsInBubbleWithinRange is missing maxDistance for behavior=%s', self.behaviorTree.GetBehaviorId())
        return is_ball_in_range(self, center_ball_id, target_ball_id, max_distance)


class GetWarpBubbleItemIdsBlockingMeFromWarp(Task):

    @TimedFunction('behaviors::actions::ballparks::GetWarpBubbleItemIdsBlockingMeFromWarp::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        ship_ids = self._get_warp_bubble_owner_ship_ids()
        logger.debug('Behavior: GetWarpBubbleItemIdsBlockingMeFromWarp found targets=%s', ship_ids)
        self.SendBlackboardValue(self.attributes.itemIdSetAddress, ship_ids)

    def _get_warp_bubble_owner_ship_ids(self):
        warp_disrupt_probe_ids, warp_disrupt_ship_ids = self._get_blocking_warp_bubble_item_ids()
        warp_disrupt_ship_ids.extend(self._get_targets_for_warp_disrupt_probes(warp_disrupt_probe_ids))
        return warp_disrupt_ship_ids

    def _get_blocking_warp_bubble_item_ids(self):
        return GetWarpBubbleItemIdsWithinRangeOfBall(self.context.ballpark, self.context.myBall.id)

    def _get_targets_for_warp_disrupt_probes(self, warp_disrupt_probe_ids):
        target_ids_of_interest = []
        for probe_id in warp_disrupt_probe_ids:
            source_id = self._get_targetable_source_for_probe(probe_id)
            if source_id is not None:
                target_ids_of_interest.append(source_id)

        return target_ids_of_interest

    def _get_targetable_source_for_probe(self, probe_id):
        probe_category_id = get_inventory_item(self, probe_id).categoryID
        if probe_category_id != categoryCharge:
            return probe_id
        return get_slim_item(self, probe_id).sourceShipID


class SelectCoordinatesFromDirectionIntoDistance(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        coordinates = self._get_coordinates()
        self.SendBlackboardValue(self.attributes.coordinatesAddress, coordinates)

    def _get_coordinates(self):
        direction = self._get_direction()
        coordinates = self._get_coordinates_based_on_direction_into_distance(direction)
        return coordinates

    def _get_direction(self):
        direction = self.GetLastBlackboardValue(self.attributes.directionAddress)
        return geo2.Vec3NormalizeD(direction)

    def _get_coordinates_based_on_direction_into_distance(self, direction):
        my_ball = get_ball(self, self.context.myItemId)
        coordinates = geo2.Vec3ScaleD(direction, self.attributes.distance)
        return [my_ball.x + coordinates[0], my_ball.y + coordinates[1], my_ball.z + coordinates[2]]


class GetCoordinatesReducedByDistance(Task):

    def OnEnter(self):
        self.SetStatusToFailed()
        coordinates = self.GetLastBlackboardValue(self.attributes.sourceCoordinateAddress)
        my_position = get_ball_position(self, self.context.myItemId)
        if self.HasAttribute('distanceAddress'):
            distance = self.GetLastBlackboardValue(self.attributes.distanceAddress)
            if distance:
                direction = geo2.Vec3DirectionD(my_position, coordinates)
                coordinates = geo2.Vec3AddD(coordinates, geo2.Vec3ScaleD(direction, distance))
        self.SendBlackboardValue(self.attributes.destinationCoordinateAddress, coordinates)
        self.SetStatusToSuccess()


class FlyIntoRandomDirection(Task):

    def OnEnter(self):
        self.context.ballpark.GotoDirection(self.context.myItemId, *RandomVector())
        self.context.ballpark.SetSpeedFraction(self.context.myItemId, self.attributes.velocityFraction)
        self.SetStatusToSuspended()

    def CleanUp(self):
        if not self.IsInvalid():
            self.context.ballpark.SetSpeedFraction(self.context.myItemId, 1.0)
        self.SetStatusToInvalid()


class FindSpecificItemLocation(Task):

    def OnEnter(self):
        location = self.select_location()
        if location:
            self.SendBlackboardValue(self.attributes.locationMessageAddress, location)
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def select_location(self):
        specific_slims = self._get_slims_by_typelist()
        if len(specific_slims) > 0:
            chosen_slim_item = choice(specific_slims)
            self.SendBlackboardValue(self.attributes.chosenItemOfInterestAddress, chosen_slim_item)
            coordinates = self.context.ballpark.GetWarpDestinationPoint(self.context.myItemId, chosen_slim_item)
            return coordinates
        else:
            return None

    def _get_slims_by_typelist(self):
        slims_list = []
        if self.attributes.specificInterestTypelist is not None:
            type_ids = evetypes.GetTypeIDsByListID(self.attributes.specificInterestTypelist)
            for slim_item in self.context.ballpark.slims.itervalues():
                if slim_item.typeID in type_ids:
                    slims_list.append(slim_item.itemID)

        self.SendBlackboardValue(self.attributes.itemsOfInterestAddress, slims_list)
        return slims_list


class SelectAllItemIdsInBubbleByTypeList(Task):

    @TimedFunction('behaviors::actions::ballparks::SelectAllItemIdInBubbleByEveTypeList::OnEnter')
    def OnEnter(self):
        balls_of_interest = get_id_and_types_in_bubble_by_typelist(self.context.ballpark, self.context.myBall.newBubbleId, self.attributes.typeListId)
        item_ids = [ item_id for item_id, type_id in balls_of_interest ]
        self.SendBlackboardValue(self.attributes.selectedTargetsAddress, item_ids)
        self.SetStatusToSuccess()


class CountItemsInBubbleByTypeList(Task):

    @TimedFunction('behaviors::actions::ballparks::SelectAllItemIdInBubbleByEveTypeList::OnEnter')
    def OnEnter(self):
        balls_of_interest = get_id_and_types_in_bubble_by_typelist(self.context.ballpark, self.context.myBall.newBubbleId, self.attributes.typeListId)
        self.SendBlackboardValue(self.attributes.itemCountAddress, len(balls_of_interest))
        self.SetStatusToSuccess()


class TransferItemToLocation(Task):

    @TimedFunction('behaviors::actions::ballparks::TransferItemToLocation::OnEnter')
    def OnEnter(self):
        self.status = status.TaskFailureStatus
        item_id = self.GetLastBlackboardValue(self.attributes.itemIdAddress)
        location = self.GetLastBlackboardValue(self.attributes.locationAddress)
        if location and item_id:
            self.context.ballpark.ChangeBallPosition(item_id, *location)
            self.status = status.TaskSuccessStatus
