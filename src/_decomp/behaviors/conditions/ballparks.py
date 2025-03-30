#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\ballparks.py
import logging
import geo2
from ballpark.const import DESTINY_MODE_ORBIT
from ballpark.warpDisruptionBalls import GetWarpBubbleItemIdsWithinRangeOfCoordinate
from behaviors import status
from behaviors.tasks import Task
from behaviors.utility.ballparks import is_ball_cloaked, get_my_position, is_ball_in_park, get_ball
from ccpProfile import TimedFunction
from eve.common.lib.appConst import shipNotWarping, minWarpDistance
from eveexceptions import UserError
logger = logging.getLogger(__name__)

class IsCoordinateInSameBubbleCondition(Task):

    @TimedFunction('behaviors::conditions::ballparks::IsCoordinateInSameBubbleCondition::OnEnter')
    def OnEnter(self):
        coordinates = self.GetLastBlackboardValue(self.attributes.coordinateAddress)
        returnStatus = status.TaskFailureStatus
        if coordinates is not None:
            bubbleID = self.context.ballpark.GetBubbleAtCoordinates(*coordinates)
            if bubbleID == self.context.myBall.newBubbleId:
                returnStatus = status.TaskSuccessStatus
        self.status = returnStatus


class IsCoordinateWithinDistance(Task):

    @TimedFunction('behaviors::conditions::ballparks::IsCoordinateWithinDistance::OnEnter')
    def OnEnter(self):
        coordinates = self.GetLastBlackboardValue(self.attributes.coordinateAddress)
        self.SetStatusToFailed()
        if coordinates is not None:
            myBall = self.context.myBall
            myCoordinates = (myBall.x, myBall.y, myBall.z)
            vecToCoord = geo2.Vec3SubtractD(coordinates, myCoordinates)
            distance = geo2.Vec3Length(vecToCoord)
            self.SetStatusToSuccessIfTrueElseToFailed(distance <= self.GetMaxDistance())

    def GetMaxDistance(self):
        return self.attributes.maxDistance


class IsCoordinateWithinDistanceByAddress(IsCoordinateWithinDistance):

    def GetMaxDistance(self):
        maxDistance = self.GetLastBlackboardValue(self.attributes.maxDistanceAddress)
        if self.HasAttribute('fudgeDistanceAddress'):
            fudgeDistance = self.GetLastBlackboardValue(self.attributes.fudgeDistanceAddress)
            if fudgeDistance is not None:
                maxDistance += self.GetLastBlackboardValue(self.attributes.fudgeDistanceAddress)
        return maxDistance


class IsBallPresentInMyBubbleCondition(Task):

    def OnEnter(self):
        ballId = self.GetLastBlackboardValue(self.attributes.ballIdAddress)
        ball = self.context.ballpark.balls.get(ballId)
        if ball and ball.newBubbleId == self.context.myBall.newBubbleId:
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()


class IsBallPresentInBubbleByAddress(Task):

    def OnEnter(self):
        bubbleId = self.GetLastBlackboardValue(self.attributes.bubbleIdAddress)
        ballId = self.GetLastBlackboardValue(self.attributes.ballIdAddress)
        ball = self.context.ballpark.balls.get(ballId)
        if ball and ball.newBubbleId == bubbleId:
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()


class IsBallWithInDistanceCondition(Task):

    @TimedFunction('behaviors::conditions::ballparks::IsBallWithInDistanceCondition::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        ballId = self.GetLastBlackboardValue(self.attributes.ballIdAddress)
        source_ball_id = self._get_source_ball_id()
        distance = self.context.ballpark.GetSurfaceDist(source_ball_id, ballId)
        if distance <= self.attributes.maxDistance:
            self.SetStatusToSuccess()

    def _get_source_ball_id(self):
        return self.context.myItemId


class IsBallWithinDistanceOfBallCondition(IsBallWithInDistanceCondition):

    def _get_source_ball_id(self):
        return self.GetLastBlackboardValue(self.attributes.sourceBallIdAddress)


class AreItemsWithInDistanceCondition(Task):

    def OnEnter(self):
        self.SetStatusToFailed()
        itemId = self.GetLastBlackboardValue(self.attributes.itemIdAddress)
        otherItemIdAddress = getattr(self.attributes, 'otherItemIdAddress', None)
        if otherItemIdAddress is None:
            otherItemId = self.context.myItemId
        else:
            otherItemId = self.GetLastBlackboardValue(self.attributes.otherItemIdAddress)
        distance = self.context.ballpark.GetSurfaceDist(itemId, otherItemId)
        maxDistance = self.GetLastBlackboardValue(self.attributes.maxDistanceAddress)
        maxDistanceMultiplier = getattr(self.attributes, 'maxDistanceMultiplier', None) or 1.0
        maxDistance *= maxDistanceMultiplier
        if distance <= maxDistance:
            self.SetStatusToSuccess()


class IsOrbitingTargetCondition(Task):

    def IsOrbitingTarget(self, targetId):
        if targetId is None:
            return False
        if self.context.myBall.mode != DESTINY_MODE_ORBIT:
            return False
        if self.context.myBall.followId != targetId:
            return False
        return True

    @TimedFunction('behaviors::conditions::ballparks::IsOrbitingTargetCondition::OnEnter')
    def OnEnter(self):
        targetId = self.GetLastBlackboardValue(self.attributes.targetAddress)
        isOrbitingTarget = self.IsOrbitingTarget(targetId)
        if isOrbitingTarget:
            self.status = status.TaskSuccessStatus
        else:
            self.status = status.TaskFailureStatus


class IsBallCloakedCondition(Task):

    @TimedFunction('behaviors::conditions::ballparks::IsBallCloakedCondition::OnEnter')
    def OnEnter(self):
        ballId = self.GetLastBlackboardValue(self.attributes.ballIdAddress)
        isCloaked = is_ball_cloaked(self, ballId)
        if isCloaked:
            self.status = status.TaskSuccessStatus
        else:
            self.status = status.TaskFailureStatus


class IsBallInWarpCondition(Task):

    @TimedFunction('behaviors::conditions::ballparks::IsBallInWarpCondition::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        ballId = self.GetLastBlackboardValue(self.attributes.ballIdAddress)
        try:
            warpState = self.context.ballpark.IsWarping(ballId)
            if warpState != shipNotWarping:
                self.SetStatusToSuccess()
        except UserError:
            pass


class IsLocationWithinWarpDistance(Task):

    @TimedFunction('behaviors::conditions::ballparks::IsBallWithinWarpDistance::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        targetCoordinates = self.GetLastBlackboardValue(self.attributes.coordinateAddress)
        if targetCoordinates:
            myCoordinates = (self.context.myBall.x, self.context.myBall.y, self.context.myBall.z)
            distance = geo2.Vec3DistanceD(targetCoordinates, myCoordinates)
            if distance > minWarpDistance:
                self.SetStatusToSuccess()


class IsBallWithinWarpDistance(Task):

    @TimedFunction('behaviors::conditions::ballparks::IsBallWithinWarpDistance::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        target_ball_id = self.GetLastBlackboardValue(self.attributes.ballIdAddress)
        if not is_ball_in_park(self, target_ball_id):
            return
        distance = self.context.ballpark.GetSurfaceDist(target_ball_id, self.context.myBall.id)
        if distance > minWarpDistance:
            self.SetStatusToSuccess()


class HasValidBallTarget(Task):

    @TimedFunction('behaviors::conditions::ballparks::HasValidBallTarget::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        hasBall = self.context.ballpark.HasBall(self.GetLastBlackboardValue(self.attributes.ballIdAddress))
        if hasBall:
            self.SetStatusToSuccess()


class IsPathToCoordinatesClearOfBubbles(Task):

    @TimedFunction('behaviors::conditions::ballparks::IsPathToCoordinatesClearOfBubbles::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        coordinates = self._get_my_warp_to_coordinates()
        if coordinates is None:
            return
        if self._is_path_to_coordinates_clear(coordinates):
            self.SetStatusToSuccess()

    def _get_my_warp_to_coordinates(self):
        return self.GetLastBlackboardValue(self.attributes.coordinateAddress)

    def _is_path_to_coordinates_clear(self, coordinates):
        try:
            warp_disruptor_id, _ = self._get_closest_warp_disruptor_and_intersection_in_path(coordinates)
        except UserError:
            logger.debug('Behavior=%s for entity=%s warp path blocked by bubble that is too close to entity for warping there', self.behaviorTree.GetBehaviorId(), self.context.myItemId)
            return False

        if warp_disruptor_id is None:
            return True
        return self._is_warp_disruptor_at_end_coordinate(warp_disruptor_id, coordinates)

    def _get_closest_warp_disruptor_and_intersection_in_path(self, coordinates):
        return self.context.ballpark.GetClosestDisruptorAndIntersectionInWarpPath(get_my_position(self), coordinates)

    def _is_warp_disruptor_at_end_coordinate(self, warp_disruptor_id, coordinates):
        warp_disruption_probe_ids, warp_disruption_ship_ids = self._get_warp_bubble_ids_at_coordinates(coordinates)
        return warp_disruptor_id in warp_disruption_probe_ids or warp_disruptor_id in warp_disruption_ship_ids

    def _get_warp_bubble_ids_at_coordinates(self, coordinates):
        return GetWarpBubbleItemIdsWithinRangeOfCoordinate(self.context.ballpark, coordinates)
