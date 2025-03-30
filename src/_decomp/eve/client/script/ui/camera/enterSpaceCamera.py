#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\enterSpaceCamera.py
import math
import blue
import geo2
import evecamera
import uthread
from ballparkCommon import parkhelpers
from carbonui.uicore import uicore
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
from eve.client.script.ui.camera.cameraUtil import GetBall, GetBallPosition, GetBallMaxZoom, GetBallRadius, GetBallWaitForModel, IsDynamicCameraMovementEnabled, GetSpeedDirection, GetInitialLookAtDistance
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.script.sys.idCheckers import IsVoidSpaceSystem
duration = 15.0

class EnterSpaceCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_ENTERSPACE
    name = 'EnterSpaceCamera'
    __notifyevents__ = BaseSpaceCamera.__notifyevents__ + ['OnCurrSessionSpaceEnteredFirstTime']

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.animEntryThread = None

    def Update(self):
        BaseSpaceCamera.Update(self)
        if IsDynamicCameraMovementEnabled():
            self.SetFovTarget(self.GetDynamicFov())
        ball = GetBall(self.ego)
        if ball:
            self.SetAtPosition(GetBallPosition(ball))

    def StartAnimation(self):
        self.animEntryThread = uthread.new(self._OnActivated)

    def _OnActivated(self):
        if not (sm.RemoteSvc('achievementTrackerMgr').HasEverWarped() or IsVoidSpaceSystem(session.solarsystemid)):
            self.AnimEnterFirstTimeEverInSpace()
        else:
            self.AnimEnter()
        uthread.new(self.SwitchToPrimaryCamera)

    def AnimEnter(self):
        ball = GetBallWaitForModel(self.ego)
        self.SetEyePosition(geo2.Vec3Scale(GetSpeedDirection(ball), 2 * GetBallRadius(ball)))
        self.SetMaxZoom(GetBallMaxZoom(ball, self.nearClip))
        uicore.animations.MorphScalar(self, 'yaw', self.yaw, self.yaw + math.pi / 20, duration=duration)
        uicore.animations.MorphScalar(self, 'pitch', self.pitch, self.pitch + math.pi / 40, duration=duration)
        dist = GetInitialLookAtDistance(self.maxZoom, self.minZoom)
        zoom0 = self.GetZoomProportionByZoomDistance(5 * dist)
        zoom1 = self.GetZoomProportionByZoomDistance(dist)
        uicore.animations.MorphScalar(self, 'zoom', zoom0, zoom1, duration=duration * 0.8)
        blue.synchro.SleepWallclock(duration * 1000)

    def AnimEnterFirstTimeEverInSpace(self):
        ball = GetBallWaitForModel(self.ego)
        radius = GetBallRadius(ball)
        self.SetMaxZoom(GetBallMaxZoom(ball, self.nearClip))
        eyePos0 = self._GetEyePos0(radius)
        eyePos1 = self._GetEyePos1(radius)
        uicore.animations.MorphVector3(self, '_eyePosition', eyePos0, eyePos1, duration=duration, sleep=True)

    def _GetEyePos0(self, radius):
        bp = sm.GetService('michelle').GetBallpark()
        direction = geo2.Vec3Normalize(bp.GetCurrentEgoPos())
        eyePos0 = geo2.Vec3Scale(direction, 5 * radius)
        eyePos0 = geo2.Vec3Add(eyePos0, (0, 0.5 * radius, 0))
        quat = geo2.QuaternionRotationAxis((0, 1, 0), 0.5)
        eyePos0 = geo2.QuaternionTransformVector(quat, eyePos0)
        return eyePos0

    def _GetEyePos1(self, radius):
        bp = sm.GetService('michelle').GetBallpark()
        shipPosition = bp.GetCurrentEgoPos()
        planet = parkhelpers.GetNearestPlanet(session.solarsystemid, shipPosition)
        planetPos = planet.position.data
        surfaceVector = geo2.Vec3Scale(geo2.Vec3Normalize(planetPos), planet.radius)
        axis = geo2.Vec3Cross(planetPos, shipPosition)
        quat = geo2.QuaternionRotationAxis((0, 1, 0), math.pi)
        surfaceVector = geo2.QuaternionTransformVector(quat, surfaceVector)
        surfacePoint = geo2.Vec3Subtract(planetPos, surfaceVector)
        surfacePoint = geo2.Vec3Subtract(surfacePoint, shipPosition)
        lookDir = geo2.Vec3Normalize(surfacePoint)
        eyePos = geo2.Vec3Scale(lookDir, -5 * radius)
        eyePos = geo2.Vec3Add(eyePos, (0, radius, 0))
        return eyePos

    def GetMinZoomProp(self):
        return self.maxZoom / self.minZoom

    def SwitchToPrimaryCamera(self):
        sm.GetService('viewState').GetView(ViewState.Space).ActivatePrimaryCamera()

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        uicore.animations.StopAllAnimations(self)
        if self.animEntryThread:
            self.animEntryThread.kill()
            self.animEntryThread = None

    def OnCurrSessionSpaceEnteredFirstTime(self):
        if self.isActive:
            self.StartAnimation()

    def Track(self, itemID, **kwargs):
        self.SwitchToPrimaryCamera()
