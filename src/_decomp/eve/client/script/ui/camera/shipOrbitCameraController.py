#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\shipOrbitCameraController.py
import math
import carbonui.const as uiconst
from eve.client.script.ui.camera.cameraUtil import SetShipDirection, GetZoomDz, CheckInvertZoom
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
from eve.client.script.ui.camera.cameraAchievementEventTracker import CameraAchievementEventTracker
import evecamera
from carbonui.uicore import uicore

class ShipOrbitCameraController(BaseCameraController):
    cameraID = evecamera.CAM_SHIPORBIT

    def __init__(self, *args, **kwargs):
        super(ShipOrbitCameraController, self).__init__(*args, **kwargs)
        self.cameraAchievementEventTracker = CameraAchievementEventTracker()

    def OnMouseMove(self, *args):
        camera = self.GetCamera()
        kOrbit = evecamera.ORBIT_MOVE_DIST
        if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
            kZoom = 0.005
            self._Zoom(-CheckInvertZoom(uicore.uilib.dy), kZoom)
            if math.fabs(uicore.uilib.dx) > 1:
                if not self.IsCameraRotated():
                    camera.Orbit(0.01 * self.GetMouseDX(), 0.0)
                    self.RecordOrbitForAchievements()
        elif uicore.uilib.leftbtn:
            camera.Orbit(kOrbit * self.GetMouseDX(), kOrbit * self.GetMouseDY())
            self.RecordOrbitForAchievements()
        elif uicore.uilib.rightbtn and not camera.IsTracking():
            kRotate = 0.005 * camera.fov
            camera.Rotate(kRotate * self.GetMouseDX(), kRotate * self.GetMouseDY())

    def OnMouseDown(self, button, *args):
        ret = BaseCameraController.OnMouseDown(self, button, *args)
        self.GetCamera().OnMouseDown(button)
        if button == 1:
            uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalRightMouseUp)
        return ret

    def OnMouseUp(self, button, *args):
        BaseCameraController.OnMouseUp(self, button, *args)
        camera = self.GetCamera()
        camera.OnMouseUp(button)
        self.cameraAchievementEventTracker.StopRecordingOrbitForAchievements()

    def OnGlobalRightMouseUp(self, obj, eventID, (vkey, flag)):
        if vkey != 1:
            return True
        self.ResetRotate()

    def OnDblClick(self, *args):
        if uicore.uilib.rightbtn or uicore.uilib.mouseTravel > 6:
            return
        SetShipDirection(self.GetCamera())

    def OnMouseWheel(self, *args):
        k = 0.0005
        dz = GetZoomDz()
        self._Zoom(dz, k)

    def _Zoom(self, dz, k):
        camera = self.GetCamera()
        self.RecordZoomForAchievements(dz)
        if uicore.uilib.Key(uiconst.VK_MENU) or self.IsCameraRotated():
            camera.FovZoom(k * dz)
        elif camera.lookAtBall:
            camera.Zoom(k * dz)
            self.ResetRotate()

    def ResetRotate(self):
        camera = self.GetCamera()
        camera.ResetRotate()
        camera.DisableManualFov()

    def IsCameraRotated(self):
        return uicore.uilib.rightbtn and self.GetCamera().IsRotated()

    def RecordOrbitForAchievements(self):
        camera = self.GetCamera()
        self.cameraAchievementEventTracker.RecordOrbitForAchievements(self, camera)

    def RecordZoomForAchievements(self, amount):
        self.cameraAchievementEventTracker.RecordZoomForAchievements(amount)
