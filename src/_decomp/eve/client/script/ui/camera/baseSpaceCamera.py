#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\baseSpaceCamera.py
import audio2
import blue
import evetypes
from carbon.common.script.util.mathCommon import GetAngleBetweenTwoVectors, IsWithinFrustum
from eve.client.script.parklife import states
from eve.client.script.ui.camera.baseCamera import Camera
from eve.client.script.ui.camera.cameraUtil import IsBobbingEnabled, GetCameraMaxLookAtRange, GetBallPosition, GetBall, IsAutoTrackingEnabled, FOV_MIN, FOV_MAX
from eve.client.script.ui.camera.util.cameraBobbingOffsetter import CameraBobbingOffsetter
from eve.common.lib import appConst
from evecamera.animation import AnimationController
from evecamera.shaker import ShakeController
from evecamera.utils import CreateBehaviorFromMagnitudeAndPosition, PanCameraAccelerated
import evegraphics.settings as gfxsettings
import geo2
import logging
import math
import random
import uthread
log = logging.getLogger(__name__)
MAX_NOISE = 160.0

class BaseSpaceCamera(Camera):
    isBobbingCamera = False
    name = 'BaseSpaceCamera'
    minZoom = 700000
    __notifyevents__ = Camera.__notifyevents__[:] + ['OnSpecialFX',
     'DoBallsRemove',
     'DoBallRemove',
     'DoClientSideBallRemove']

    def __init__(self):
        Camera.__init__(self)
        self.noiseCurve = None
        self.noiseScaleCurve = None
        self.noiseScale = 0.0
        self.noiseDampCurve = None
        self.noiseDamp = 1.1
        self._noiseX = 0.0
        self._noiseY = 0.0
        self._noiseOffset = None
        self._anchorBall = None
        self._anchorOffset = None
        self.trackTarget = None
        self.cachedCameraTranslation = None
        self.shakeController = ShakeController(self)
        self.animationController = AnimationController(self)
        self.isManualControlEnabled = True
        self.audioListener = None
        self._startTime = 0L
        if self.isBobbingCamera:
            self.bobbingOfsetter = CameraBobbingOffsetter()
        else:
            self.bobbingOfsetter = None

    @property
    def ego(self):
        return session.structureid or session.shipid

    def ShakeCamera(self, magnitude, position, key = None):
        behavior = CreateBehaviorFromMagnitudeAndPosition(magnitude, position, self)
        if behavior is None:
            return
        behavior.key = key
        self.shakeController.DoCameraShake(behavior)

    def StopShaking(self):
        self.shakeController.ClearCurrentShake()

    def Update(self):
        Camera.Update(self)
        if self.IsNoiseEnabled():
            self._UpdateCameraNoiseOffset()
        if self.bobbingOfsetter:
            self._UpdateBobbingOffset()
        self.UpdateAnchorOffset()

    def IsNoiseEnabled(self):
        try:
            return gfxsettings.Get(gfxsettings.UI_CAMERA_SHAKE_ENABLED)
        except gfxsettings.UninitializedSettingsGroupError:
            return False

    def ResetCurveStartTime(self):
        self._startTime = blue.os.GetSimTime()

    def _UpdateCameraNoiseOffset(self):
        if self._startTime == 0:
            self._startTime = blue.os.GetSimTime()
        localTime = blue.os.TimeAsDouble(blue.os.GetSimTime() - self._startTime)
        if self.noiseScaleCurve:
            self.noiseScale = self.noiseScaleCurve.UpdateScalar(localTime)
        if self.noiseScale == 0:
            return
        if self.noiseDampCurve:
            self.noiseDamp = self.noiseDampCurve.UpdateScalar(localTime)
        dT = 1.0 / blue.os.fps
        ran = random.random() - 0.5
        self._noiseX = (self._noiseX + self.noiseDamp * ran) / (1.0 + self.noiseDamp * dT)
        self._noiseX = max(-MAX_NOISE, min(self._noiseX, MAX_NOISE))
        ran = random.random() - 0.5
        self._noiseY = (self._noiseY + self.noiseDamp * ran) / (1.0 + self.noiseDamp * dT)
        self._noiseY = max(-MAX_NOISE, min(self._noiseY, MAX_NOISE))
        noiseScale = self.GetZoomDistance() / 100.0 * self.noiseScale
        direction = self.GetLookAtDirection()
        vecX = geo2.Vec3Cross(direction, self._upDirection)
        vecY = geo2.Vec3Cross(direction, vecX)
        vecX = geo2.Vec3Scale(vecX, self._noiseX * noiseScale)
        vecY = geo2.Vec3Scale(vecY, self._noiseY * noiseScale)
        noiseOffset = geo2.Vec3Add(vecX, vecY)
        self._AddToAtOffset(noiseOffset)

    def ClearCameraParent(self):
        self.LookAt(self.ego)
        self.ResetAnchorPos()

    def Track(self, itemID, **kwargs):
        pass

    def OnAutoTrackingChanged(self):
        if not self.isActive:
            return
        if IsAutoTrackingEnabled():
            itemID = sm.GetService('stateSvc').GetExclState(states.selected)
            self.Track(itemID)
        else:
            self.Track(None)

    def GetCameraParent(self):
        return self.trackTarget

    def DisableManualControl(self):
        self.StopUpdateThreads()
        self.isManualControlEnabled = False

    def EnableManualControl(self):
        self.isManualControlEnabled = True

    def IsManualControlEnabled(self):
        return self.isManualControlEnabled and not self.IsInTransit()

    def Pan(self, *args):
        if self.IsManualControlEnabled():
            Camera.Pan(self, *args)

    def Zoom(self, dz):
        if self.IsManualControlEnabled():
            Camera.Zoom(self, dz)

    def Orbit(self, *args):
        if self.IsManualControlEnabled():
            Camera.Orbit(self, *args)

    def GetTrackPosition(self, ball):
        if not ball:
            ret = (0, 0, 0)
        elif not ball.ballpark:
            ret = self._atPosition
            self.ResetCamera()
        else:
            ret = GetBallPosition(ball)
        if self._anchorOffset:
            ret = geo2.Vec3Subtract(ret, self._anchorOffset)
        return ret

    def _UpdateBobbingOffset(self):
        if not IsBobbingEnabled():
            return
        offset = self.bobbingOfsetter.UpdateOffset(self.atPosition, self.eyePosition)
        self._AddToEyeAndAtOffset(offset)

    def CheckObjectTooFar(self, itemID):
        ball = GetBall(itemID)
        if not ball:
            return False
        if getattr(ball, 'typeID', None) and self._IsBallTypeDisallowedForLookAt(ball.typeID):
            return True
        ballPos = GetBallPosition(ball)
        return geo2.Vec3Length(ballPos) > GetCameraMaxLookAtRange()

    def _IsBallTypeDisallowedForLookAt(self, typeID):
        return evetypes.GetGroupID(typeID) in (appConst.groupPlanet, appConst.groupMoon)

    def ConstructAnchorBall(self):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp or not bp.ego:
            return
        pos = bp.GetCurrentEgoPos()
        self._anchorBall = bp.AddClientSideBall(pos)

    def ResetAnchorPos(self):
        if self._anchorOffset:
            self.eyePosition = geo2.Vec3Add(self.eyePosition, self._anchorOffset)
            self.atPosition = geo2.Vec3Add(self.atPosition, self._anchorOffset)
        self._anchorBall = None
        self._anchorOffset = None

    def UpdateAnchorOffset(self):
        if self._anchorBall:
            self._anchorOffset = GetBallPosition(self._anchorBall)
            self._AddToEyeAndAtOffset(self._anchorOffset)
        else:
            self._anchorOffset = None

    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, timeFromStart = 0, graphicInfo = None):
        if guid == 'effects.Warping':
            if shipID in (self.ego, self.GetLookAtItemID()):
                self.OnCurrentShipWarping()

    def GetLookAtItemID(self):
        return self.ego

    def GetItemID(self):
        return self.GetLookAtItemID()

    def OnCurrentShipWarping(self):
        pass

    def OnActivated(self, **kwargs):
        Camera.OnActivated(self, **kwargs)
        uthread.new(self.AudioUpdateThread)
        settings.char.Subscribe('ui', 'orbitCameraAutoTracking', self.OnAutoTrackingChanged)
        if self.bobbingOfsetter:
            self.bobbingOfsetter.OnActivated()

    def OnDeactivated(self):
        super(BaseSpaceCamera, self).OnDeactivated()
        settings.char.Unsubscribe('ui', 'orbitCameraAutoTracking', self.OnAutoTrackingChanged)

    def AudioUpdateThread(self):
        self.audioListener = audio2.GetListener()
        while self.isActive:
            self.audioListener.SetPosition(self.GetLookAtDirection(), self.upDirection, self.eyePosition)
            blue.synchro.Yield()

        self.audioListener = None

    def TranslateFromParentAccelerated(self, begin, end, durationSec, accelerationPower = 2.0):
        self.animationController.Schedule(PanCameraAccelerated(begin, end, durationSec, accelerationPower))

    def IsLocked(self):
        return False

    def DoClientSideBallRemove(self, ball):
        self.DoBallRemove(ball)
        if ball == self._anchorBall:
            self.ResetAnchorPos()

    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, _, _ in pythonBalls:
            self.DoBallRemove(ball)

    def DoBallRemove(self, ball, *args, **kwargs):
        self.OnBallRemoved(ball)

    def OnBallRemoved(self, ball):
        pass

    def GetDynamicFovByDistance(self, dist):
        prop = max(0.0, min(dist / self.minZoom, 1.0))
        return FOV_MIN + prop ** 0.35 * (FOV_MAX - FOV_MIN)

    def GetDynamicFov(self):
        if self._atTransitOffset:
            atPos = geo2.Vec3Subtract(self.atPosition, self._atTransitOffset)
        else:
            atPos = self.atPosition
        dist = geo2.Vec3Distance(self.eyePosition, atPos)
        return self.GetDynamicFovByDistance(dist)

    def ResetFOV(self):
        self.SetFovTarget(self.default_fov)

    def GetItemPosition(self, itemID):
        itemBall = GetBall(itemID)
        if not itemBall:
            raise RuntimeError('Failed to find position for item %s. Item is not in the current ballpark.' % itemID)
        return GetBallPosition(itemBall)

    def GetLookAtItemDirection(self, itemID):
        itemPosition = self.GetItemPosition(itemID)
        eyePosition = geo2.Vec3AddD(self._eyePosition, self._eyeOffset) if self._eyeOffset else self._eyePosition
        return geo2.Vec3Direction(eyePosition, itemPosition)

    def IsWithinViewAngle(self, itemID, angleInDegrees):
        try:
            cameraLookAtDirection = self.GetLookAtDirectionWithOffset()
            itemLookAtDirection = self.GetLookAtItemDirection(itemID)
            angleFromCameraToItem = GetAngleBetweenTwoVectors(cameraLookAtDirection, itemLookAtDirection)
            angleToCheck = math.radians(angleInDegrees)
            return angleFromCameraToItem <= angleToCheck
        except Exception as exc:
            log.exception('Error when checking if item %s is in %s degree view angle: %s', itemID, angleInDegrees, exc)
            return False

    def IsWithinViewFrustum(self, itemID):
        try:
            itemPosition = self.GetItemPosition(itemID)
            return IsWithinFrustum(itemPosition, self.viewMatrix.transform, self.projectionMatrix.transform)
        except Exception as exc:
            log.exception('Error when checking whether item is within view frustum: %s', exc)
            return False

    def GetLookAtPointDirection(self, pointLocation):
        eyePosition = geo2.Vec3AddD(self._eyePosition, self._eyeOffset) if self._eyeOffset else self._eyePosition
        return geo2.Vec3Direction(eyePosition, pointLocation)

    def IsPointWithinViewAngle(self, pointLocation, angleInDegrees):
        try:
            cameraLookAtDirection = self.GetLookAtDirectionWithOffset()
            itemLookAtDirection = self.GetLookAtPointDirection(pointLocation)
            angleFromCameraToPoint = GetAngleBetweenTwoVectors(cameraLookAtDirection, itemLookAtDirection)
            angleToCheck = math.radians(angleInDegrees)
            return angleFromCameraToPoint <= angleToCheck
        except Exception as exc:
            log.exception('Error when checking if point %s is in %s degree view angle: %s', pointLocation, angleInDegrees, exc)
            return False
