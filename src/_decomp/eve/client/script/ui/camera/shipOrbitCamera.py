#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\shipOrbitCamera.py
import math
import destiny
import gametime
import uthread2
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from eve.client.script.parklife import states
from eve.client.script.ui.camera.cameraUtil import GetDurationByDistance, GetBallPosition, GetBall, GetBallMaxZoom, Vector3Chaser, VectorLerper, IsAutoTrackingEnabled, CheckShowModelTurrets, GetSpeedDirection, GetInitialLookAtDistance, IsDynamicCameraMovementEnabled
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
import evecamera
import blue
import geo2
import evetypes
import uthread
import evegraphics.settings as gfxsettings
import inventorycommon.const as invconst
from eve.client.script.ui.camera.util.cameraSpeedOffsetter import CameraSpeedOffsetter
from evegraphics.explosions.spaceObjectExplosionManager import SpaceObjectExplosionManager
from carbonui.uicore import uicore
from destructionEffect import destructionType as destructionEffectType
TRACK_RESET_SPEED = 60.0
TRACK_DEFAULT_SPEED = 30.0

class ShipOrbitCamera(BaseSpaceCamera):
    __notifyevents__ = BaseSpaceCamera.__notifyevents__[:] + ['OnBallparkSetState',
     'OnStateChange',
     'OnDungeonCameraInterest',
     'OnBallAdded']
    cameraID = evecamera.CAM_SHIPORBIT
    isBobbingCamera = True
    minFov = 0.8
    maxFov = 1.2
    minZoom = 800000
    name = 'ShipOrbitCamera'

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.lookAtBall = None
        self.trackBall = None
        self.trackPendingItemIDSpeedDuration = None
        self.orbitFreezeProp = 0.0
        self._zoomPropCache = None
        self._eyeOffsetChaser = Vector3Chaser()
        self._trackOffsetChaser = Vector3Chaser()
        self.trackLerper = VectorLerper(duration=1.5)
        self.speedOffsetter = CameraSpeedOffsetter()
        self.isManualFovEnabled = False
        self._trackSpeedMultiplier = 1.0
        self._trackSpeed = TRACK_DEFAULT_SPEED
        self._handleTargetKilledThread = None
        self.speedDir = None

    def OnActivated(self, itemID = None, lastCamera = None, **kwargs):
        BaseSpaceCamera.OnActivated(self, **kwargs)
        self.speedOffsetter.OnActivated()
        self.RegisterActivated()
        if lastCamera and lastCamera.cameraID in (evecamera.CAM_TACTICAL,
         evecamera.CAM_SHIPPOV,
         evecamera.CAM_JUMP,
         evecamera.CAM_UNDOCK,
         evecamera.CAM_ENTERSPACE,
         evecamera.CAM_EXPLOSION):
            itemID = itemID or getattr(lastCamera, 'lastLookAtID', None) or self.ego
            self._SetLookAtBall(itemID)
            atPos1 = self.GetTrackPosition(self.lookAtBall)
            eyePos1 = geo2.Vec3Add(atPos1, geo2.Vec3Scale(lastCamera.GetLookAtDirection(), self.GetInitialZoomDist(lastCamera)))
            if lastCamera.cameraID in (evecamera.CAM_TACTICAL,
             evecamera.CAM_JUMP,
             evecamera.CAM_UNDOCK,
             evecamera.CAM_ENTERSPACE,
             evecamera.CAM_EXPLOSION):
                if hasattr(lastCamera, 'transitionDelay'):
                    duration = lastCamera.transitionDelay
                else:
                    duration = GetDurationByDistance(lastCamera.eyePosition, eyePos1, 0.4, 0.6)
                self.Transit(lastCamera.atPosition, lastCamera.eyePosition, atPos1, eyePos1, duration=duration, smoothing=0.0)
                currFov = self.fov
                self.fov = lastCamera.fov
                if not IsDynamicCameraMovementEnabled():
                    self.SetFovTarget(currFov)
            else:
                self.SetAtPosition(atPos1)
                self.SetEyePosition(eyePos1)
        elif itemID:
            self._SetLookAtBall(itemID)
        elif not self.lookAtBall:
            self._SetLookAtBall(self.ego)

    def RegisterActivated(self):
        settings.char.ui.Set('spaceCameraID', evecamera.CAM_SHIPORBIT)

    def GetInitialZoomDist(self, lastCamera):
        if lastCamera.cameraID == evecamera.CAM_ENTERSPACE:
            dist = lastCamera.GetZoomDistance()
        elif self._zoomPropCache is not None:
            dist = self.GetZoomDistanceByZoomProportion(self._zoomPropCache)
        else:
            dist = self.GetLookAtDistance()
        return dist

    def StopHandleTargetKilledThread(self):
        if self._handleTargetKilledThread:
            self._handleTargetKilledThread.kill()
        self._handleTargetKilledThread = None

    def GetLookAtItemID(self):
        return self.GetItemID()

    def LookAt(self, itemID, forceUpdate = False, objRadius = None):
        lookAtBall = self._TrySetLookAtBall(itemID, forceUpdate, objRadius)
        if lookAtBall:
            radius = self.GetLookAtDistance(objRadius)
            self._LookAtAnimate(itemID, radius)
        self.StopHandleTargetKilledThread()

    def _TrySetLookAtBall(self, itemID, forceUpdate = False, objRadius = None):
        if not self.IsLookAtAllowed(itemID):
            return
        self.Track(None, speed=TRACK_RESET_SPEED)
        self.DisableManualFov()
        isAlreadyLookingAt = self.lookAtBall and self.lookAtBall.id == itemID
        if not forceUpdate and isAlreadyLookingAt and not objRadius:
            if itemID != self.ego:
                self._SetLookAtBall(self.ego)
                return self.lookAtBall
            else:
                return
        self._ScatterLookAtEvent(itemID)
        if self.CheckObjectTooFar(itemID):
            self.Track(itemID)
            return
        self._SetLookAtBall(itemID)
        return self.lookAtBall

    def _ScatterLookAtEvent(self, itemID):
        sm.ScatterEvent('OnCameraLookAt', itemID == self.ego, itemID)

    def IsLookAtAllowed(self, itemID):
        if not self.IsManualControlEnabled():
            return False
        if self.IsBallWarping(itemID) and itemID != self.ego:
            return False
        return True

    def LookAtMaintainDistance(self, itemID):
        lookAtBall = self._TrySetLookAtBall(itemID)
        if lookAtBall:
            radius = self.GetZoomDistance()
            self._LookAtAnimate(itemID, radius)

    def IsBallWarping(self, itemID):
        trackBall = GetBall(itemID)
        return trackBall is None or trackBall.mode == destiny.DSTBALL_WARP

    def DisableManualFov(self):
        self.isManualFovEnabled = False

    def _SetLookAtBall(self, itemID):
        self.lookAtBall = GetBall(itemID)
        if self.lookAtBall:
            sm.StartService('stateSvc').SetState(self.lookAtBall.id, states.lookingAt, True)
            CheckShowModelTurrets(self.lookAtBall)
        self.Track(None, speed=TRACK_RESET_SPEED)
        if not self.lookAtBall:
            self.ResetAnchorPos()
            return
        self.UpdateMaxZoom()
        self.ConstructAnchorBall()
        if isinstance(self.lookAtBall, SpaceObject):
            self.lookAtBall.RegisterForModelLoad(self.OnLookAtItemModelLoaded)

    def UpdateMaxZoom(self):
        ball = self.lookAtBall
        nearClip = self.nearClip
        if ball is not None and nearClip is not None:
            self.SetMaxZoom(GetBallMaxZoom(ball, nearClip))

    def _LookAtAnimate(self, itemID, radius):
        atPos1 = GetBallPosition(self.lookAtBall)
        eyePos1 = self._GetNewLookAtEyePos(atPos1, itemID, radius)
        duration = GetDurationByDistance(self.eyePosition, eyePos1, 0.5, 1.5)
        self.speedOffsetter.Reset()
        self.TransitTo(atPos1, eyePos1, duration=duration, smoothing=0.0)

    def _GetNewLookAtEyePos(self, atPos1, itemID, radius):
        typeID = self.lookAtBall.typeID
        if typeID and evetypes.GetGroupID(typeID) == invconst.groupBillboard:
            direction = self._GetBillboardLookAtDirection()
            radius = self.lookAtBall.radius * 5
        else:
            direction = self.GetLookAtDirection()
        eyePos1 = geo2.Vec3Add(atPos1, geo2.Vec3Scale(direction, radius))
        return eyePos1

    def _GetBillboardLookAtDirection(self):
        direction = GetSpeedDirection(self.lookAtBall)
        if geo2.Vec3Dot(self.GetLookAtDirection(), direction) < 0:
            direction = geo2.Vec3Scale(direction, -1)
        return direction

    def GetLookAtDistance(self, objRadius = None):
        return GetInitialLookAtDistance(self.maxZoom, self.minZoom, objRadius)

    def _UpdateAtOffset(self):
        if not self.lookAtBall:
            self._trackOffsetChaser.ResetValue()
            return
        atOffset = None
        self.speedDir = GetSpeedDirection(self.lookAtBall)
        self._UpdateTrackOffset()
        trackOffset = self._trackOffsetChaser.GetValue()
        self.speedOffsetter._Update(self.lookAtBall, self.maxZoom, self.IsTracking())
        speedOffset = self.speedOffsetter.GetSpeedOffset()
        self._AddToAtOffset(geo2.Vec3Add(trackOffset, speedOffset))

    def _UpdateTrackOffset(self):
        if self.IsTracking() and IsDynamicCameraMovementEnabled():
            trackOffset = self._GetTrackAtOffset()
            self._trackOffsetChaser.SetTargetValue(trackOffset, self._trackSpeed * self._trackSpeedMultiplier)
        else:
            self._trackOffsetChaser.ResetValue(TRACK_RESET_SPEED * self._trackSpeedMultiplier)

    def _GetTrackAtOffset(self):
        trackOffset = geo2.Vec3Subtract(self.GetTrackPosition(self.trackBall), self._atPosition)
        length = geo2.Vec3Length(trackOffset)
        maxLen = 250000
        if length > maxLen:
            trackOffset = geo2.Vec3Scale(trackOffset, maxLen / length)
        return trackOffset

    def _GetTrackEyeOffset(self):
        offsetProp = 1.0 - self.GetZoomProportion() ** self.kZoomPower
        offsetDir = self._GetTrackEyeOffsetDirection()
        offsetAmount = offsetProp * self.maxZoom
        offset = geo2.Vec3Scale(offsetDir, offsetAmount)
        return offset

    def _GetTrackEyeOffsetDirection(self):
        pitch = math.pi - self.GetPitch()
        rotMat = geo2.MatrixRotationAxis(self.GetZAxis(), -pitch)
        return geo2.Vec3Transform(self.GetYAxis(), rotMat)

    def _UpdateEyeOffset(self):
        if self.IsChasing():
            offset = (0, 0.5 * self.maxZoom, 0)
            eyeOffset = self.GetChaseEyeOffset()
            offset = geo2.Vec3Subtract(offset, eyeOffset)
            self._eyeOffsetChaser.SetTargetValue(offset, 1.0)
        elif self.IsTracking() and IsDynamicCameraMovementEnabled():
            offset = self._GetTrackEyeOffset()
            self._eyeOffsetChaser.SetTargetValue(offset, self._trackSpeed * self._trackSpeedMultiplier)
        else:
            self._eyeOffsetChaser.ResetValue(self._trackSpeed * self._trackSpeedMultiplier)
        self._AddToEyeOffset(self._eyeOffsetChaser.GetValue())

    def Update(self):
        self._UpdateAnchorPosition()
        BaseSpaceCamera.Update(self)
        if not self.lookAtBall or not self.ego:
            return
        zoomProp = self.GetZoomProportion()
        self._UpdateAtOffset()
        self._UpdateEyeOffset()
        newAtPos = self.GetTrackPosition(self.lookAtBall)
        atDiff = geo2.Vec3Subtract(newAtPos, self._atPosition)
        self.SetAtPosition(newAtPos)
        if self.IsChasing():
            self.SetEyePosition(self.trackLerper.GetValue(self._eyePosition, self.GetChaseEyePosition()))
        elif self.IsTracking():
            self.SetEyePosition(self.trackLerper.GetValue(self._eyePosition, self.GetTrackingEyePosition()))
        else:
            prop = self._GetEyePosDriftProporition()
            eyeOffset = geo2.Vec3Scale(atDiff, prop)
            self.SetEyePosition(geo2.Vec3Add(self._eyePosition, eyeOffset))
        if not self.IsInTransit():
            if self.GetItemID() == self.ego or self.IsTracking() or self.IsChasing():
                self.SetZoom(zoomProp)
            self.EnforceMinZoom()
        if not self.isManualFovEnabled and IsDynamicCameraMovementEnabled():
            self.SetFovTarget(self.GetDynamicFov())

    def _UpdateAnchorPosition(self):
        if self.lookAtBall and self.lookAtBall.mode == destiny.DSTBALL_WARP:
            self.ResetAnchorPos()
        elif not self._anchorBall or geo2.Vec3Length(GetBallPosition(self._anchorBall)) > evecamera.LOOKATRANGE_MAX_NEW:
            self.ConstructAnchorBall()

    def GetTrackingEyePosition(self):
        trackPos = self.GetTrackPosition(self.trackBall)
        direction = geo2.Vec3Subtract(self._atPosition, trackPos)
        direction = geo2.Vec3Normalize(direction)
        offset = geo2.Vec3Scale(direction, self.GetZoomDistance())
        return geo2.Vec3Add(self._atPosition, offset)

    def GetChaseEyePosition(self):
        offset = geo2.Vec3Scale(self.speedDir, -self.GetZoomDistance())
        return geo2.Vec3Add(self._atPosition, offset)

    def IsTracking(self):
        return self.trackBall is not None and self.trackBall != self.lookAtBall

    def GetChaseEyeOffset(self):
        offsetAmount = geo2.Vec3Length(self.speedOffsetter.GetSpeedOffset())
        eyeOffset = geo2.Vec3Scale(self.speedDir, offsetAmount)
        return eyeOffset

    def Track(self, itemID = None, speed = TRACK_DEFAULT_SPEED, duration = 1.5, **kwargs):
        self.trackPendingItemIDSpeedDuration = None
        if self.trackBall and self.trackBall.id == itemID:
            return
        if not self.trackBall and itemID is None:
            return
        self.StopUpdateThreads()
        if itemID and self.trackBall is None:
            self._TrackZoomOutIfTooClose()
        self.trackBall = GetBall(itemID)
        self._trackSpeed = speed
        self._RampUpTrackSpeed(duration)
        self.trackLerper.Reset(duration)
        self.StopHandleTargetKilledThread()
        sm.ScatterEvent('OnCameraTrack', itemID)

    def _TrackZoomOutIfTooClose(self):
        if self.GetZoomProportion() < 0.45:
            self.SetZoomTarget(0.45)

    def _RampUpTrackSpeed(self, duration = 1.5):
        self._trackSpeedMultiplier = 0.0
        uicore.animations.MorphScalar(self, '_trackSpeedMultiplier', 0.0, 1.0, duration=duration)

    def _GetEyePosDriftProporition(self):
        if not IsDynamicCameraMovementEnabled():
            return 1.0
        elif self.GetItemID() == self.ego:
            return 0.999
        else:
            zoomProp = self.GetZoomProportion()
            prop = 0.7 * (1.0 - zoomProp)
            prop = max(0.5, prop)
            if prop < 1.0:
                prop += self.orbitFreezeProp * (1.0 - prop)
            prop = min(prop, 1.0)
            return prop

    def IsChasing(self):
        return self.lookAtBall == self.trackBall and self.speedDir and geo2.Vec3Length(self.speedDir) > 0.0

    def GetTrackItemID(self):
        if self.IsTracking():
            return self.trackBall.id

    def ResetCamera(self, *args):
        self.LookAt(self.ego, forceUpdate=True)

    def ResetCameraPosition(self):
        BaseSpaceCamera.ResetCameraPosition(self)
        self._SetLookAtBall(self.ego)

    def Orbit(self, dx = 0, dy = 0):
        if self.IsTransitioningToOrFromTracking() and IsDynamicCameraMovementEnabled():
            return
        BaseSpaceCamera.Orbit(self, dx, dy)
        if self.IsTracking() or self.IsChasing():
            self.Track(None, speed=TRACK_RESET_SPEED)

    def IsTransitioningToOrFromTracking(self):
        return self._trackSpeedMultiplier < 0.4

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        self._zoomPropCache = self.GetZoomProportion()
        self.lookAtBall = None
        self._trackOffsetChaser.ResetValue()
        self.speedOffsetter.Reset()
        self.ResetAnchorPos()
        self.DisableManualFov()
        self._trackSpeed = 1.0
        self._trackSpeedMultiplier = 1.0
        self.ResetRotate()
        self.StopHandleTargetKilledThread()

    def GetItemID(self):
        if self.lookAtBall:
            return self.lookAtBall.id

    def ClearCameraParent(self):
        self._SetLookAtBall(self.ego)

    def OnBallRemoved(self, ball):
        if ball == self.lookAtBall:
            if not self.isActive or ball.id == self.ego:
                self._SetLookAtBall(None)
            elif ball.id != self.ego and destructionEffectType.isExplosionOrOverride(ball.destructionEffectId):
                if gfxsettings.Get(gfxsettings.UI_EXPLOSION_EFFECTS_ENABLED) and IsDynamicCameraMovementEnabled():
                    sm.GetService('sceneManager').SetPrimaryCamera(evecamera.CAM_EXPLOSION, itemID=ball.id)
                else:
                    self.LookAt(self.ego)
            else:
                self.LookAt(self.ego)
        if ball == self.trackBall:
            SpaceObjectExplosionManager.GetExplosionTimesWhenAvailable(ball.id, lambda t1, t2: self.StartHandleTargetKilledThread(ball.id, t1, t2))

    def StartHandleTargetKilledThread(self, ballID, globalExplosionStart, wreckSwitchTime):
        self._handleTargetKilledThread = uthread.new(self._HandleTargetKilled, ballID, globalExplosionStart, wreckSwitchTime)

    def _HandleTargetKilled(self, ballID, globalExplosionStart, wreckSwitchTime):
        blue.synchro.SleepUntilSim(wreckSwitchTime + 5 * gametime.SEC)
        self.Track(None, speed=TRACK_RESET_SPEED)

    def OnBallparkSetState(self):
        if self.isActive:
            self._SetLookAtBall(self.ego)
        else:
            self._SetLookAtBall(None)

    def OnCurrentShipWarping(self):
        if self.GetLookAtItemID() is not None and self.GetLookAtItemID() != self.ego:
            self.LookAt(self.ego)

    def OnMouseDown(self, button):
        if self.IsTracking() or self.IsChasing():
            return
        if button == 0:
            uicore.animations.MorphScalar(self, 'orbitFreezeProp', self.orbitFreezeProp, 1.0, duration=0.5, timeOffset=0.0)

    def OnMouseUp(self, button):
        if button == 0:
            uicore.animations.MorphScalar(self, 'orbitFreezeProp', self.orbitFreezeProp, 0.0, duration=2.0, timeOffset=0.0)

    def FovZoom(self, dz):
        self.minFov = 0.3
        self.maxFov = 1.3
        BaseSpaceCamera.FovZoom(self, dz)
        self.isManualFovEnabled = True

    def OnStateChange(self, itemID, flag, flagState, *args):
        if flagState and flag == states.selected and IsAutoTrackingEnabled():
            if not uicore.cmd.IsSomeCombatCommandLoaded():
                self.Track(itemID)

    def OnDungeonCameraInterest(self, itemID, speed, duration):
        if not (self.isActive and IsDynamicCameraMovementEnabled()):
            return
        ball = GetBall(itemID)
        if ball:
            self.Track(itemID, speed, duration)
        else:
            self.trackPendingItemIDSpeedDuration = (itemID, speed, duration)

    def OnBallAdded(self, slimItem):
        if self.trackPendingItemIDSpeedDuration and slimItem.itemID == self.trackPendingItemIDSpeedDuration[0]:
            self.Track(*self.trackPendingItemIDSpeedDuration)

    def GetZoomToPoint(self):
        offset = BaseSpaceCamera.GetZoomToPoint(self)
        speedOffset = self.speedOffsetter.GetSpeedOffset()
        if speedOffset:
            offset = geo2.Vec3AddD(offset, speedOffset)
        return offset

    def OnLookAtItemModelLoaded(self):
        self.UpdateMaxZoom()
        if self.GetZoomDistance() < self.maxZoom:
            self.SetZoom(0.0)
