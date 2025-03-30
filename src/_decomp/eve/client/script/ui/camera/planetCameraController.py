#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\planetCameraController.py
import evecamera
from carbonui.uicore import uicore
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
from eve.client.script.ui.camera.cameraUtil import GetZoomDz, CheckInvertZoom
from evecamera import CAM_PLANET

class PlanetCameraController(BaseCameraController):
    cameraID = CAM_PLANET

    def OnMouseMove(self, *args):
        kOrbit = evecamera.ORBIT_MOVE_DIST
        if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
            self.camera.Zoom(-0.005 * CheckInvertZoom(self.GetMouseDY()))
        if uicore.uilib.leftbtn and not uicore.uilib.rightbtn:
            k = kOrbit * (0.05 + self.camera.GetZoomProportionLinear())
            self.camera.Orbit(k * self.GetMouseDX(), k * self.GetMouseDY())

    def OnMouseWheel(self, *args):
        dz = GetZoomDz()
        self.camera.Zoom(dz * 0.0005)

    def ZoomBy(self, dz):
        self.camera.Zoom(dz * 0.0005)

    def GetAreaName(self, areaID):
        return areaID
