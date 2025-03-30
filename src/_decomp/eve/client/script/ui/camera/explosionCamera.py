#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\explosionCamera.py
import random
import math
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
from eve.client.script.ui.camera.cameraUtil import GetBall, GetBallPosition
from eve.client.script.ui.view.viewStateConst import ViewState
import evecamera
import blue
import geo2
from evegraphics.explosions.spaceObjectExplosionManager import SpaceObjectExplosionManager
from carbonui.uicore import uicore
BOUNDING_SPHERE_MULTIPLICATION = 20

def MiddlePoint(endPos, startPos):
    return geo2.Vec3Scale(geo2.Vec3Direction(endPos, startPos), geo2.Vec3Distance(startPos, endPos) * 0.5)


class ExplosionCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_EXPLOSION
    name = 'ExplosionCamera'

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.msUntilGlobal = 0.0
        self.interest = None
        self.startTime = 0
        self.isRunning = False
        self.animateCamera = False
        self.endTime = 0
        self.p0, self.p1, self.p2, self.p3, self.p4 = (None, None, None, None, None)

    def ResetCamera(self):
        self.p0, self.p1, self.p2, self.p3, self.p4 = (None, None, None, None, None)
        self.startTime = 0
        self.isRunning = False
        self.animateCamera = False
        self.endTime = 0.0
        self.msUntilGlobal = 0.0

    def OnActivated(self, lastCamera = None, itemID = None, **kwargs):
        BaseSpaceCamera.OnActivated(self, **kwargs)
        if lastCamera and lastCamera.cameraID in evecamera.INSPACE_CAMERAS:
            self.SetAtPosition(lastCamera.atPosition)
            self.SetEyePosition(lastCamera.eyePosition)
            self.interest = itemID
            self.fov = lastCamera.fov
        self.SetFovTarget(self.default_fov)
        SpaceObjectExplosionManager.GetExplosionTimesWhenAvailable(itemID, self.SetTimes)

    def SetTimes(self, globalExplosionStart, wreckSwitchTime):
        self.startTime = blue.os.GetSimTime()
        self.msUntilGlobal = float(blue.os.TimeDiffInMs(self.startTime, long(globalExplosionStart))) * 1.2
        self.CalculatePoints()
        if self.animateCamera:
            velocity = geo2.Vec3Distance(self.p0, self.p2) / max(self.msUntilGlobal, 100)
            self.endTime = self.msUntilGlobal + min(geo2.Vec3Distance(self.p2, self.p3) / velocity, 5000)
        self.isRunning = True

    def Update(self):
        if not self.isRunning:
            BaseSpaceCamera.Update(self)
            return
        egoBall = GetBall(self.ego)
        if egoBall is None:
            self.isRunning = False
            return
        if not self.animateCamera:
            egoPos = GetBallPosition(egoBall)
            self.Transit(self.atPosition, self.eyePosition, egoPos, self.eyePosition, 3.0, callback=self.SwitchToPrimaryCamera)
            self.isRunning = False
        else:
            interestBall = GetBall(self.interest)
            if interestBall is None:
                self.isRunning = True
                return
            t = float(blue.os.TimeDiffInMs(self.startTime, blue.os.GetSimTime()))
            self.atPosition = GetBallPosition(interestBall)
            if t < self.msUntilGlobal:
                self.eyePosition = self.GetSplinePosition(t / self.msUntilGlobal, self.p0, self.p1, self.p2)
            elif t < self.endTime:
                frac = (t - self.msUntilGlobal) / (self.endTime - self.msUntilGlobal)
                self.eyePosition = self.GetPosBetweenTwoPoints(frac, self.p2, self.p3)
            else:
                egoPos = GetBallPosition(egoBall)
                self.Transit(self.atPosition, self.p3, egoPos, self.p3, 5.0, callback=self.SwitchToPrimaryCamera)
                self.isRunning = False
        BaseSpaceCamera.Update(self)

    def GetPosBetweenTwoPoints(self, frac, p0, p1):
        invFrac = 1 - frac
        p0Influence = geo2.Vec3Scale(p0, invFrac)
        p1Influence = geo2.Vec3Scale(p1, frac)
        newPoint = geo2.Vec3Add(p0Influence, p1Influence)
        return newPoint

    def GetSplinePosition(self, frac, p0, p1, p2):
        invFrac = 1 - frac
        p0Influence = geo2.Vec3Scale(p0, invFrac * invFrac)
        p1Influence = geo2.Vec3Scale(p1, 2.0 * frac * invFrac)
        p2Influence = geo2.Vec3Scale(p2, frac * frac)
        newPoint = geo2.Vec3Add(p0Influence, geo2.Vec3Add(p1Influence, p2Influence))
        return newPoint

    def CalculatePoints(self):
        startBall = GetBall(self.interest)
        startPos = GetBallPosition(startBall)
        egoBall = GetBall(self.ego)
        endPos = GetBallPosition(egoBall)
        offset = geo2.Vec3Subtract(endPos, startPos)
        if self.GetDistanceFromLookAt() > geo2.Vec3Length(offset):
            self.animateCamera = False
            return
        self.animateCamera = True
        distanceFromLookAt = self.GetDistanceFromLookAt()
        self.p0 = self.eyePosition
        self.p3 = self._GetNewLookAtEyePosWithPositionInView(endPos, max(distanceFromLookAt, egoBall.radius * 5.0), startPos)
        shipBasedBounds = startBall.radius * BOUNDING_SPHERE_MULTIPLICATION
        if geo2.Vec3DistanceSq(endPos, startPos) < geo2.Vec3DistanceSq(endPos, self.p0):
            if distanceFromLookAt < shipBasedBounds:
                self.SetupOrbitTrackInsideOfBounds(distanceFromLookAt, shipBasedBounds)
            else:
                self.SetupOrbitTrackOutsideOfBounds(distanceFromLookAt)
        elif distanceFromLookAt < shipBasedBounds:
            self.SetupTranslationTrackInsideOfBounds(distanceFromLookAt, shipBasedBounds)
        else:
            self.SetupTranslationTrackOutsideOfBounds()

    def SetupOrbitTrackInsideOfBounds(self, distanceFromLookAt, bounds):
        perpendicularDirection = self.FindPerpendicularDirection(self.eyePosition, self.atPosition, self.p3)
        self.p1 = geo2.Vec3Add(self.atPosition, geo2.Vec3Scale(perpendicularDirection, distanceFromLookAt))
        lengthToBounds = bounds * bounds - distanceFromLookAt * distanceFromLookAt
        lengthFromP1ToP3 = geo2.Vec3DistanceSq(self.p1, self.p3)
        if lengthToBounds > lengthFromP1ToP3:
            self.p2 = self.p3
        else:
            p1ToP3 = geo2.Vec3Direction(self.p3, self.p1)
            self.p2 = geo2.Vec3Add(self.p1, geo2.Vec3Scale(p1ToP3, math.sqrt(lengthToBounds)))

    def SetupTranslationTrackInsideOfBounds(self, distanceFromLookAt, bounds):
        perpendicularDirection = self.FindPerpendicularDirection(self.eyePosition, self.atPosition, self.p3)
        perpendicularPos = geo2.Vec3Add(self.atPosition, geo2.Vec3Scale(perpendicularDirection, distanceFromLookAt))
        lengthToBounds = bounds * bounds - distanceFromLookAt * distanceFromLookAt
        lengthFromP1ToP3 = geo2.Vec3DistanceSq(perpendicularPos, self.p3)
        if lengthToBounds > lengthFromP1ToP3:
            self.p2 = self.p3
        else:
            p1ToP3 = geo2.Vec3Direction(self.p3, perpendicularPos)
            self.p2 = geo2.Vec3Add(self.atPosition, geo2.Vec3Scale(p1ToP3, math.sqrt(lengthToBounds)))
        self.p1 = geo2.Vec3Add(self.p0, MiddlePoint(self.p2, self.p0))

    def SetupOrbitTrackOutsideOfBounds(self, distanceFromLookAt):
        perpendicularDirection = self.FindPerpendicularDirection(self.eyePosition, self.atPosition, self.p3)
        self.p2 = geo2.Vec3Add(self.atPosition, geo2.Vec3Scale(perpendicularDirection, distanceFromLookAt))
        self.p1 = geo2.Vec3Add(self.p0, MiddlePoint(self.p2, self.p0))

    def SetupTranslationTrackOutsideOfBounds(self):
        self.p1 = self.GetPosBetweenTwoPoints(0.1, self.p0, self.p3)
        self.p2 = self.GetPosBetweenTwoPoints(0.2, self.p0, self.p3)

    def FindPerpendicularDirection(self, eyePosition, atPosition, point):
        eyeToAt = geo2.Vec3Subtract(atPosition, eyePosition)
        eyeToPoint = geo2.Vec3Subtract(point, eyePosition)
        scale = geo2.Vec3Dot(eyeToPoint, eyeToAt) / geo2.Vec3Dot(eyeToAt, eyeToAt)
        closestPointOnLine = geo2.Vec3Add(eyePosition, geo2.Vec3Scale(eyeToAt, scale))
        direction = geo2.Vec3Direction(point, closestPointOnLine)
        return direction

    def SwitchToPrimaryCamera(self):
        spaceCamera = sm.GetService('viewState').GetView(ViewState.Space).ActivatePrimaryCamera()
        if self.animateCamera:
            spaceCamera.eyePosition = self.eyePosition
            spaceCamera.atPosition = self.atPosition
        self.ResetCamera()
        return spaceCamera

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        uicore.animations.StopAllAnimations(self)

    def Track(self, itemID, **kwargs):
        cam = self.SwitchToPrimaryCamera()
        if cam:
            cam.Track(itemID)

    def LookAt(self, itemID, **kwargs):
        cam = self.SwitchToPrimaryCamera()
        if cam:
            cam.LookAt(itemID, **kwargs)

    def LookAtMaintainDistance(self, itemID):
        pass

    def _GetNewLookAtEyePosWithPositionInView(self, atPos1, radius, interestPosition):
        vectorDiff = geo2.Vec3Subtract(atPos1, interestPosition)
        fov = self.fov - self.fovOffset
        angleToRotate = -fov * 0.65
        randomness = 0.5 * random.random()
        invRandomness = 0.5 - randomness
        rotation = geo2.MatrixMultiply(geo2.MatrixRotationX(angleToRotate * randomness), geo2.MatrixRotationY(angleToRotate * invRandomness))
        newEyeDir = geo2.Vec3Normalize(vectorDiff)
        newEyeDir = geo2.Vec3Transform(newEyeDir, rotation)
        return geo2.Vec3Add(geo2.Vec3Scale(newEyeDir, radius), atPos1)
