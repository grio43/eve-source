#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\modularHangarCamera.py
import math
from eve.client.script.ui.camera.cameraUtil import GetInitialLookAtDistance
import evecamera
import uthread
import logging
import blue
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
from gametime import GetSecondsSinceSimTime, GetSimTime
import carbonui.const as uiconst
import geo2
from carbonui.uicore import uicore
import eve.client.script.ui.view.hangarBehaviours.modularHangarBehavioursConstants as hc
from uthread2 import call_after_simtime_delay
logger = logging.getLogger(__name__)

class ModularHangarCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_MODULARHANGAR
    isBobbingCamera = False
    name = 'ModularHangarCamera'
    kMaxPitch = math.pi / 2.0 + math.pi / 8.0
    minFov = 0.3
    maxFov = 1.0
    hangarMinZoom = 2050.0
    hangarMaxZoom = 10.0

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.log = logger
        self.model = None
        self.atPosition = (0.0, 0.0, 0.0)
        self.typeID = 0
        self.zoomFactor = 0.5
        self.fov = 1.0
        self.fpShipSpawnTime = 0
        self.hangarEntryTime = 0
        self.simplifiedDirection = (0.0, 0.0, 0.0)
        self.camSpeed = (0.0, 0.0, 0.0)
        self.distanceToFP = 0
        self.isRotating = 0
        self.changingShip = False
        self.flightValueMap = []
        self.targetPoint = (0.0, 0.0, 0.0)
        self.lastShipLocation = None
        self.transitionAnimationEndedTime = 0
        self.hallwayTime = 0.4
        self.currentShipSizeClass = 1
        self.phase2finished = True
        self.changingSkinsTime = 0

    def SetCurrentShipSizeClass(self, sizeClass):
        self.currentShipSizeClass = sizeClass

    def SetRotating(self, isTrue):
        self.isRotating = isTrue

    def SetFlightValueMap(self, exit1, hallway1, hallway2, exit2, dockPos):
        hallwayLength = min(0.9, geo2.Vec3Length(geo2.Vec3Subtract(hallway1, hallway2)) / 10000)
        self.hallwayTime = 0.1 + hallwayLength
        if self.hallwayTime > 0.4 or not hc.TRANSITION_MODIFY_BY_HALLWAYTIME:
            self.flightValueMap = [self.GetEyePosition(),
             exit1,
             hallway1,
             hallway2,
             exit2,
             dockPos]
        else:
            modifiedHallway1 = geo2.Vec3Lerp(exit1, hallway1, self.hallwayTime)
            modifiedHallway2 = geo2.Vec3Lerp(exit2, hallway2, self.hallwayTime)
            self.flightValueMap = [self.GetEyePosition(),
             exit1,
             modifiedHallway1,
             modifiedHallway2,
             exit2,
             dockPos]

    def SetIsChangingSkin(self):
        self.changingSkinsTime = GetSimTime()

    def SetShip(self, model, typeID, changingShip = True):
        uicore.animations.StopAllAnimations(self)
        self.lastShipLocation = self.atPosition
        self.model = model
        self.typeID = typeID
        if changingShip:
            self.fov = 1.0
            self.fpShipSpawnTime = GetSimTime()
        self.targetPoint = self.GetEyePosition()
        self.changingShip = changingShip or self.changingShip

    def SkipFlight(self):
        time = GetSimTime() - (hc.SHIP_SWAP_DURATION + hc.TRANSITION_PADDING)
        self.fpShipSpawnTime = time
        self.changingSkinsTime = 0.0
        self.phase2finished = True
        self.changingShip = False

    def PlaceShip(self, pos):
        self.atPosition = pos

    def AnimEnterHangar(self, model, startPos, endPos, duration = 5.0):
        self.hangarEntryTime = GetSimTime()
        self.model = model
        self.atPosition = self._CalculateFocalPoint(model)
        self.changingShip = False
        self.SetEyePosition(self.CalculateTargetPoint())
        self.yaw = 0
        self.pitch = 0

        def AllignCamera():
            modelRotation = model.rotationCurve.currentValue
            extraYaw = geo2.QuaternionRotationGetYawPitchRoll(modelRotation)[0]
            self.yaw = extraYaw + 0.5 - math.pi
            self.pitch = 1.2
            self.zoomFactor = 0.9

        call_after_simtime_delay(AllignCamera, 0.3)

    def _AnimEnterHangarFOV(self, duration):
        pass

    def _AnimEnterHangarZoom(self, duration, model):
        pass

    def _AnimSwitchShipsZoom(self, duration, model):
        pass

    def _AnimZoom(self, duration, zoom0, zoom1):
        pass

    def UpdateMinMaxZoom(self):
        pass

    def SetZoom(self, proportion):
        pass

    def ClearRefs(self):
        self.model = None

    def CalculateTargetPoint(self):
        biggestEllipsoidAxis = max(self.model.generatedShapeEllipsoidRadius)
        roundFactor = hc.SHIELD_ELLIPSOID_ROUNDING_FACTOR + (1 - pow(1 - self.zoomFactor, 2.0)) * (1 - hc.SHIELD_ELLIPSOID_ROUNDING_FACTOR)
        cameraBoundLength, innerPaddingValue, outerPaddingValue = self.GetSizeDependantZoomConstants()
        platformCameraBounds = (cameraBoundLength, cameraBoundLength, cameraBoundLength)
        innerPadding = (innerPaddingValue, innerPaddingValue, innerPaddingValue)
        outerPadding = (outerPaddingValue, outerPaddingValue, outerPaddingValue)
        fullyRoundedEllipsoid = (biggestEllipsoidAxis, biggestEllipsoidAxis, biggestEllipsoidAxis)
        innerBoundRadius = geo2.Vec3Lerp(self.model.generatedShapeEllipsoidRadius, fullyRoundedEllipsoid, roundFactor)
        innerBoundRadius = geo2.Vec3Add(innerBoundRadius, innerPadding)
        preferredOuterBoundRadius = geo2.Vec3Add(geo2.Vec3Scale(innerBoundRadius, hc.SHIELD_ELLIPSOID_ZOOM_MULTIPLIER), outerPadding)
        outerBoundRadius = tuple((min(ele1, ele2) for ele1, ele2 in zip(preferredOuterBoundRadius, platformCameraBounds)))
        direction = self.GetLookAtDirection()
        invertedDirection = geo2.QuaternionInverse(self.model.rotationCurve.currentValue)
        self.simplifiedDirection = geo2.QuaternionTransformVector(invertedDirection, direction)
        invertedSimplifiedDirection = geo2.Vec3Scale(self.simplifiedDirection, -1)
        innerPoint = tuple((ele1 * ele2 for ele1, ele2 in zip(invertedSimplifiedDirection, innerBoundRadius)))
        outerPoint = tuple((ele1 * ele2 for ele1, ele2 in zip(invertedSimplifiedDirection, outerBoundRadius)))
        self.distanceToFP = geo2.Vec3Length(geo2.Vec3Lerp(innerPoint, outerPoint, self.zoomFactor))
        zoomVec = geo2.Vec3Scale(direction, self.distanceToFP)
        targetPos = geo2.Vec3Add(self.GetZoomToPoint(), zoomVec)
        return targetPos

    def GetSizeDependantZoomConstants(self):
        biggestEllipsoidAxis = max(self.model.generatedShapeEllipsoidRadius)
        if self.currentShipSizeClass == 0:
            cbl = hc.SMALL_PLATFORM_CAMERA_BOUNDS + hc.SMALL_PLATFORM_BOUNDING_PADDING * biggestEllipsoidAxis
            innerBoundsPadding = hc.SMALL_PLATFORM_INNER_PADDING_BOUNDING_SPHERE_FACTOR * biggestEllipsoidAxis
            return (cbl, hc.SMALL_PLATFORM_INNER_PADDING, hc.SMALL_PLATFORM_OUTER_PADDING)
        elif self.currentShipSizeClass == 1:
            cbl = hc.SMALL_PLATFORM_CAMERA_BOUNDS + hc.SMALL_PLATFORM_BOUNDING_PADDING * biggestEllipsoidAxis
            innerBoundsPadding = hc.SMALL_PLATFORM_INNER_PADDING_BOUNDING_SPHERE_FACTOR * biggestEllipsoidAxis
            return (cbl, hc.SMALL_PLATFORM_INNER_PADDING + innerBoundsPadding, hc.SMALL_PLATFORM_OUTER_PADDING)
        elif self.currentShipSizeClass == 2:
            cbl = hc.MEDIUM_PLATFORM_CAMERA_BOUNDS + hc.MEDIUM_PLATFORM_BOUNDING_PADDING * biggestEllipsoidAxis
            return (cbl, hc.MEDIUM_PLATFORM_INNER_PADDING, hc.MEDIUM_PLATFORM_OUTER_PADDING)
        elif self.currentShipSizeClass == 3:
            self.log.error('capital ship misplaced in the regular hangar')
            cbl = hc.SMALL_PLATFORM_CAMERA_BOUNDS + hc.SMALL_PLATFORM_BOUNDING_PADDING * biggestEllipsoidAxis
            innerBoundsPadding = hc.SMALL_PLATFORM_INNER_PADDING_BOUNDING_SPHERE_FACTOR * biggestEllipsoidAxis
            return (cbl, hc.SMALL_PLATFORM_INNER_PADDING + innerBoundsPadding, hc.SMALL_PLATFORM_OUTER_PADDING)
        else:
            return None

    def EnforceMaxZoom(self):
        if self.changingShip:
            cameraSpeed = hc.CAMERA_FOLLOW_SPEED / 100.0
            lerpedTarget = geo2.Vec3Lerp(self.GetEyePosition(), self.targetPoint, cameraSpeed)
            self.SetEyePosition(lerpedTarget)
            return
        if self.changingSkinsTime != 0:
            cameraSpeed = hc.CAMERA_FOLLOW_SPEED / 100.0
            lerpedTarget = geo2.Vec3Lerp(self.GetEyePosition(), self.CalculateTargetPoint(), cameraSpeed)
            self.SetEyePosition(lerpedTarget)
            return
        targetPos = self.CalculateTargetPoint()
        elapsedDuration = GetSecondsSinceSimTime(self.transitionAnimationEndedTime)
        timeSinceHangarEntry = GetSecondsSinceSimTime(self.hangarEntryTime)
        if timeSinceHangarEntry > 5 and not self.phase2finished and elapsedDuration < hc.PHASE_2_DURATION:
            target = geo2.Vec3Add(self.GetEyePosition(), self.camSpeed)
            blendRamp = (hc.PHASE_1_TO_2_BLEND_DURATION - elapsedDuration) / hc.PHASE_1_TO_2_BLEND_DURATION
            self.camSpeed = geo2.Vec3Scale(self.camSpeed, 0.6 + 0.4 * blendRamp)
            phase2Progress = (hc.PHASE_2_DURATION - elapsedDuration) / hc.PHASE_2_DURATION
            lerpedTarget = geo2.Vec3Lerp(target, targetPos, 1.0 - phase2Progress)
            self.SetEyePosition(lerpedTarget)
            if geo2.Vec3DistanceSqD(lerpedTarget, targetPos) < 5.0:
                self.phase2finished = True
        else:
            self.SetEyePosition(geo2.Vec3Lerp(self.GetEyePosition(), targetPos, min(1.0, elapsedDuration)))

    def ClampPitch(self, pitch):
        if self.model is None:
            return pitch
        if self.model.translationCurve is None:
            return pitch
        extraPitch = 0
        try:
            if self.currentShipSizeClass < 2:
                thresholds = [hc.SMALL_PLATFORM_GAP_INNER_EDGE, hc.SMALL_PLATFORM_GAP_OUTER_EDGE, hc.SMALL_PLATFORM_OUTER_EDGE]
                extraAllowance = math.pi / 3.0
            else:
                thresholds = [hc.MEDIUM_PLATFORM_GAP_INNER_EDGE, hc.MEDIUM_PLATFORM_GAP_OUTER_EDGE, hc.MEDIUM_PLATFORM_OUTER_EDGE]
                extraAllowance = math.pi / 6.0
            lookingAtTheFront = pow(max(self.simplifiedDirection[2], 0.0), 2)
            frontOffset = self.model.translationCurve.curves[1].value[2]
            relativeCamPlacementFront = self.distanceToFP + frontOffset
            frontBoost = min(max(relativeCamPlacementFront * lookingAtTheFront - thresholds[0], 0.0) / thresholds[1], 1.0)
            lookingRight = -cmp(self.simplifiedDirection[0], 0)
            centerOffset = self.model.translationCurve.curves[1].value[0]
            relativeCamPlacement = (self.distanceToFP + lookingRight * centerOffset) * abs(self.simplifiedDirection[0])
            gapCenter = (thresholds[0] + thresholds[1]) / 2
            gapHalfWidth = abs(thresholds[1] - thresholds[0]) / 2
            closenessToGapCenter = max(gapHalfWidth - abs(relativeCamPlacement - gapCenter), 0.0) / gapHalfWidth
            closenessToGapCenter = closenessToGapCenter * min(2.0 * max(self.simplifiedDirection[2] + 0.8, 0.0), 1.0)
            distanceFromPlatformEdge = min(max((relativeCamPlacement - thresholds[2]) / (gapHalfWidth * 4), 0), 1.0)
            extraPitch = (closenessToGapCenter + distanceFromPlatformEdge + frontBoost) * extraAllowance
        except Exception as exc:
            logger.exception('ModularHangarCamera: Ship translationCurve not configured correctly')

        maxPitch = math.pi / 2.0 + extraPitch
        return max(self.kMinPitch, min(pitch, maxPitch))

    def GetShipOffset(self):
        if self.model is None:
            return (0.0, 0.0, 0.0)
        localBB = self.model.GetLocalBoundingBox()
        height = abs(localBB[0][0])
        width = abs(localBB[0][2])
        return (0.0, height, width)

    def _AnimEnterHangarYaw(self, duration):
        pass

    def _AnimEnterHangarPitch(self, duration):
        pass

    def AnimSwitchShips(self, model, startPos, endPos, duration = 5.0):
        pass

    def Orbit(self, *args):
        BaseSpaceCamera.Orbit(self, *args)
        uicore.animations.StopAnimation(self, 'yaw')
        uicore.animations.StopAnimation(self, 'pitch')

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        self.model = None

    def Update(self):
        BaseSpaceCamera.Update(self)
        if self.model and self.model.translationCurve:
            if self.changingShip:
                self._updateShipChangeLocations()
                self.EnforceMaxZoom()
            else:
                self._UpdateFocalPoint()
                self.EnforceMaxZoom()

    def GetIsChangingShip(self):
        if self.changingShip or not self.phase2finished:
            return True
        return False

    def _updateShipChangeLocations(self):
        remappedTimings = hc.TRANSITION_TIME_REMAP
        swapDuration = hc.SHIP_SWAP_DURATION
        phase1Padding = hc.TRANSITION_PADDING
        if hc.TRANSITION_MODIFY_BY_HALLWAYTIME:
            swapDuration = 0.7 * swapDuration + 0.3 * swapDuration * self.hallwayTime
            phase1Padding = 0.7 * phase1Padding + 0.3 * phase1Padding * self.hallwayTime
        elapsedDuration = GetSecondsSinceSimTime(self.fpShipSpawnTime)
        travelProgress = min(elapsedDuration / swapDuration, 1.0)

        def _EndShipSwapping():
            self.changingShip = False
            self.zoomFactor = hc.PHASE_2_END_ZOOM_LEVEL
            self.transitionAnimationEndedTime = GetSimTime()
            cameraSpeed = hc.CAMERA_FOLLOW_SPEED / 100.0
            lerpedTarget = geo2.Vec3Lerp(self.GetEyePosition(), self.targetPoint, cameraSpeed)
            self.camSpeed = geo2.Vec3Subtract(lerpedTarget, self.GetEyePosition())
            self.phase2finished = False

        def _Relevancy(startRelevancy, endRelevancy, boost = 1.0):
            if boost is 0.0:
                return 0.0
            spikeTime = endRelevancy - startRelevancy
            frontSpike = min(max(travelProgress - startRelevancy, 0.0) / spikeTime, 0.5)
            backSpike = min(max(travelProgress - (endRelevancy - spikeTime / 2.0), 0.0) / spikeTime, 0.5)
            return boost * pow(max(frontSpike - backSpike, 0.0), 1 + hc.PATH_BELL_CURVE_CONST / 100)

        points = [hc.PATH_ORIGINAL_POSITION_RELEVANCY,
         hc.PATH_FIRST_EXIT_RELEVANCY,
         hc.PATH_FIRST_HALLWAY_POINT_RELEVANCY,
         hc.PATH_END_HALLWAY_POINT_RELEVANCY,
         hc.PATH_END_EXIT_RELEVANCY,
         hc.PATH_END_DOCK_POINT_RELEVANCY]
        progressMap = []
        for point in points:
            progressMap.append(_Relevancy(point[0], point[1], point[2]))

        targetPoint = (0.0, 0.0, 0.0)
        for i, each in enumerate(self.flightValueMap):
            if progressMap[i] != 0:
                addition = geo2.Vec3Scale(each, progressMap[i])
                targetPoint = geo2.Vec3Add(targetPoint, addition)

        total = sum(progressMap)
        if total == 0:
            return
        self.targetPoint = geo2.Vec3Scale(targetPoint, 1 / total)
        if elapsedDuration > swapDuration:
            swapThreshold = pow(hc.PHASE_2_START_THRESHOLD * max(self.model.generatedShapeEllipsoidRadius), 2)
            if geo2.Vec3DistanceSqD(self.GetEyePosition(), self.targetPoint) < swapThreshold:
                _EndShipSwapping()
            elif elapsedDuration > swapDuration + phase1Padding:
                _EndShipSwapping()
        targetShipPos = self._CalculateFocalPoint(self.model)
        remappedTravelProgress = min(max(travelProgress - remappedTimings[0], 0.0) / (remappedTimings[1] - remappedTimings[0]), 1.0)
        if remappedTravelProgress < hc.FP_SWAP_TIMING:
            lerpValue = hc.FP_SWAP_VALUE * pow(1 / hc.FP_SWAP_TIMING * remappedTravelProgress, hc.FP_SWAP_SPEED)
        else:
            reductionValue = max(2 * hc.FP_SWAP_TIMING - remappedTravelProgress, 0.0)
            reduction = (1 - hc.FP_SWAP_VALUE) * pow(1 / hc.FP_SWAP_TIMING * reductionValue, hc.FP_SWAP_SPEED)
            lerpValue = 1 - reduction
        linearPointRelevancy = 1.0 - 0.2 * (0.5 - abs(0.5 - lerpValue))
        if lerpValue < 0.5:
            lerpValue = 2 * pow(lerpValue, 2.0)
        else:
            ajustedLerpValue = lerpValue - 0.5
            lerpValue = 0.5 + 2 * ajustedLerpValue * (1 - ajustedLerpValue)
        linearPoint = geo2.Vec3Lerp(self.lastShipLocation, targetShipPos, lerpValue)
        superFloor = geo2.Vec3Add(geo2.Vec3Lerp(self.lastShipLocation, targetShipPos, 0.5), (0.0, -(500.0 + 500 * self.hallwayTime), 0.0))
        FPtarget = geo2.Vec3Lerp(superFloor, linearPoint, linearPointRelevancy)
        self.atPosition = FPtarget

    def _UpdateFocalPoint(self):
        if self.changingSkinsTime != 0:
            totalDuration = 5.0
            elapsedTime = GetSecondsSinceSimTime(self.changingSkinsTime)
            lerpValue = 0.05 * (elapsedTime / totalDuration)
            self.atPosition = geo2.Vec3Lerp(self.atPosition, self._CalculateFocalPoint(self.model), lerpValue)
            timeSinceHangarEntry = GetSecondsSinceSimTime(self.hangarEntryTime)
            if elapsedTime > totalDuration or timeSinceHangarEntry < 5.0:
                self.changingSkinsTime = 0
        else:
            self.atPosition = self._CalculateFocalPoint(self.model)

    def _CalculateFocalPoint(self, model):
        if model is None or model.translationCurve is None:
            return (0.0, 0.0, 0.0)
        modelTranslation = model.translationCurve.currentValue
        centerOffset = model.generatedShapeEllipsoidCenter
        rotatedCenterOffset = geo2.QuaternionTransformVector(self.model.rotationCurve.currentValue, centerOffset)
        return geo2.Add(modelTranslation, rotatedCenterOffset)

    def SetMinMaxZoomDefaults(self, minZoom, maxZoom):
        pass

    def SetHangarAnimationParameters(self, yaw, pitch, zoom, fov):
        pass

    def Zoom(self, dz):
        if self.zoomTarget is None:
            self.zoomTarget = self.zoomFactor
        self.zoomTarget = max(min(1.0, self.zoomTarget + 0.5 * dz), 0.0)
        if not self.zoomUpdateThread:
            self.zoomUpdateThread = uthread.new(self.ZoomUpdateThread)

    def SetZoomTarget(self, proportion):
        pass

    def ZoomUpdateThread(self):
        try:
            while True:
                if self.zoomTarget is None:
                    break
                distLeft = self.zoomTarget - self.zoomFactor
                if not distLeft:
                    break
                zoomSpeed = self._GetZoomSpeed()
                moveProp = zoomSpeed / blue.os.fps
                if math.fabs(distLeft) < self.kZoomStopDist:
                    moveProp *= self.kZoomStopDist / math.fabs(distLeft)
                moveProp = min(moveProp, 1.0)
                self.zoomFactor += distLeft * moveProp
                self.SetZoom(self.zoomFactor)
                if moveProp == 1.0:
                    break
                self.SetPitch(self.GetPitch())
                blue.synchro.Yield()

        finally:
            self.zoomUpdateThread = None
            self.zoomTarget = None
