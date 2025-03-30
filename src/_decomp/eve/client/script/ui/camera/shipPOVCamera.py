#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\shipPOVCamera.py
import math
import blue
from eve.client.script.parklife import states
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
from eve.client.script.ui.camera.cameraUtil import GetBallPosition
from eve.client.script.ui.inflight.povCameraInSceneContainer import PovCameraInSceneContainer
import evecamera
import geo2
import uthread
from carbonui.uicore import uicore
from evecamera.locationalcamera import get_orbit_camera_by_solar_system
ROTANGLE = (math.pi - 1.0) / 2.0

class ShipPOVCamera(BaseSpaceCamera):
    name = 'ShipPOVCamera'
    cameraID = evecamera.CAM_SHIPPOV
    minZoom = 100000
    default_fov = 1.0
    __notifyevents__ = BaseSpaceCamera.__notifyevents__ + ['OnLoadScene']

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.lastLookAtID = None
        self.trackBall = None
        self.inSceneContainer = None

    def Update(self):
        BaseSpaceCamera.Update(self)
        if not session.solarsystemid:
            return
        if not self.trackBall:
            self.UpdateTrackBall()
        if self.trackBall and getattr(self.trackBall, 'model', None) and hasattr(self.trackBall.model.rotationCurve, 'value'):
            self.UpdateUpDirection()
            self.UpdateAtEyePositions()
            self.UpdateInSceneContainer()
        if self.trackBall and self.trackBall.id != self.ego:
            camera = get_orbit_camera_by_solar_system(session.solarsystemid2)
            uthread.new(sm.GetService('sceneManager').SetPrimaryCamera, camera)

    def UpdateAtEyePositions(self):
        lookDir = self.GetLookDirection()
        ballPos = GetBallPosition(self.trackBall)
        if self.trackBall.model:
            radius = self.trackBall.model.GetBoundingSphereRadius()
        else:
            radius = self.trackBall.radius * 1.2
        self.SetEyePosition(geo2.Vec3Add(ballPos, geo2.Vec3Scale(lookDir, -radius)))
        self.SetAtPosition(geo2.Vec3Add(ballPos, geo2.Vec3Scale(lookDir, -2 * radius)))

    def GetTrackPosition(self):
        trackPos = self.trackBall.GetVectorAt(blue.os.GetSimTime())
        return (trackPos.x, trackPos.y, trackPos.z)

    def GetLookDirection(self):
        lookDir = geo2.QuaternionTransformVector(self.trackBall.model.rotationCurve.value, (0.0, 0.0, -1.0))
        lookDir = geo2.Vec3Normalize(lookDir)
        return lookDir

    def UpdateUpDirection(self):
        model = self.trackBall.model
        upDirection = geo2.QuaternionTransformVector(model.rotationCurve.value, (0.0, 1.0, 0.0))
        self.upDirection = geo2.Vec3Normalize(upDirection)

    def UpdateInSceneContainer(self):
        if not self.inSceneContainer:
            return
        if not sm.GetService('ui').IsUiVisible():
            self.inSceneContainer.transform.display = False
            return
        self.inSceneContainer.transform.display = True
        self.UpdateInSceneContainerPosition()
        lookAtDir = self.GetLookAtDirection()
        pitch = math.acos(geo2.Vec3Dot(lookAtDir, (0, -1, 0)))
        rightDir = geo2.Vec3Cross(self.GetUpDirection(), lookAtDir)
        roll = math.acos(geo2.Vec3Dot(rightDir, (0, 1, 0)))
        self.inSceneContainer.Update(pitch, roll)

    def UpdateInSceneContainerPosition(self):
        translation = geo2.Vec3Add(self.eyePosition, geo2.Vec3Scale(self.GetLookAtDirection(), -10))
        self.inSceneContainer.transform.translation = translation
        x = 10000.0 / uicore.desktop.width * self.fov ** 0.85
        self.inSceneContainer.transform.scaling = (x, x, 1.0)

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        if self.trackBall:
            self.trackBall = None
        if self.inSceneContainer:
            self.inSceneContainer.Close()
        self.ResetRotate()

    def OnActivated(self, lastCamera = None, **kwargs):
        BaseSpaceCamera.OnActivated(self, lastCamera=lastCamera, **kwargs)
        sm.StartService('stateSvc').SetState(self.ego, states.lookingAt, True)
        settings.char.ui.Set('spaceCameraID', evecamera.CAM_SHIPPOV)
        self.UpdateTrackBall()
        if lastCamera is not None and lastCamera.cameraID == evecamera.CAM_JUMP:
            self.Transit(lastCamera.atPosition, lastCamera.eyePosition, (0, 0, -1), (0, 0, 0), duration=lastCamera.transitionDelay)
        uthread.new(self.ConstructInSceneContainer)

    def UpdateTrackBall(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp:
            self.trackBall = bp.GetBall(self.ego)

    def ConstructInSceneContainer(self):
        while self.isActive:
            scene = sm.GetService('sceneManager').GetRegisteredScene('default')
            if scene:
                container = uicore.uilib.FindRootObject('PovCameraBracket')
                if container:
                    self.inSceneContainer = container
                else:
                    self.inSceneContainer = PovCameraInSceneContainer(scene=scene, name='PovCameraBracket', width=500, height=500, clearBackground=True, backgroundColor=(0, 0, 0, 0), faceCamera=True, renderJob=uicore.uilib.GetRenderJob())
                break
            blue.synchro.Yield()

    def LookAt(self, itemID, *args, **kwargs):
        if itemID == self.ego:
            return
        if not self.CheckObjectTooFar(itemID):
            camera = get_orbit_camera_by_solar_system(session.solarsystemid2)
            sm.GetService('sceneManager').SetPrimaryCamera(camera, itemID=itemID)

    def ResetCamera(self, *args):
        pass

    def Track(self, itemID, **kwargs):
        pass

    def _ClampRotateX(self, x):
        return max(-ROTANGLE, min(x, ROTANGLE))

    def _ClampRotateY(self, y):
        return max(-ROTANGLE, min(y, ROTANGLE))

    def OnLoadScene(self, *args):
        if self.inSceneContainer:
            self.inSceneContainer.Close()
        self.ConstructInSceneContainer()
