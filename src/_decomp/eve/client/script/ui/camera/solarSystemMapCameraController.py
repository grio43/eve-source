#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\solarSystemMapCameraController.py
import math
import evecamera
from carbonui.uianimations import animations
from eve.client.script.ui.camera.cameraUtil import CheckInvertZoom
from eve.client.script.ui.camera.mapCameraController import MapCameraController
from eve.client.script.ui.inflight.scannerFiles.directionalScanUtil import SetScanModeTarget, IsDscanShortcutPressed
from carbonui.uicore import uicore

class SolarSystemMapCameraController(MapCameraController):
    cameraID = evecamera.CAM_SOLARSYSTEMMAP
    kPan = 2.0

    def SetTopView(self):
        camera = self.GetCamera()
        camera.StopUpdateThreads()
        duration = max(0.1, math.fabs(camera.pitch - camera.kMinPitch) * 0.2)
        animations.MorphScalar(camera, 'pitch', camera.pitch, camera.kMinPitch, duration=duration)

    def SetSideView(self):
        camera = self.GetCamera()
        camera.StopUpdateThreads()
        duration = max(0.1, math.fabs(camera.pitch - math.pi / 2) * 0.2)
        animations.MorphScalar(camera, 'pitch', camera.pitch, math.pi / 2, duration=duration)

    def ToggleCameraView(self):
        camera = self.GetCamera()
        if camera.pitch < math.pi / 4:
            self.SetSideView()
        else:
            self.SetTopView()

    def OnMouseMove(self, *args):
        if uicore.uilib.leftbtn and not uicore.uilib.rightbtn and IsDscanShortcutPressed():
            self.OrbitPrimarySpaceCamera()
        else:
            camera = self.GetCamera()
            if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
                camera.Zoom(-CheckInvertZoom(uicore.uilib.dy) * 0.005)
            elif uicore.uilib.leftbtn:
                k = 0.01
                camera.Orbit(k * self.GetMouseDX(), k * self.GetMouseDY())
            elif uicore.uilib.rightbtn:
                self.Pan(camera)
            if uicore.uilib.rightbtn and not uicore.uilib.leftbtn:
                SetScanModeTarget()

    def OrbitPrimarySpaceCamera(self):
        camera = sm.GetService('sceneManager').GetActivePrimaryCamera()
        k = 0.005
        camera.Orbit(k * self.GetMouseDX(), k * self.GetMouseDY())

    def OnMouseWheel(self, *args):
        MapCameraController.OnMouseWheel(self, *args)
