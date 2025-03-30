#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\mapCameraController.py
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
from eve.client.script.ui.camera.cameraUtil import GetZoomDz, CheckInvertZoom
from carbonui.uicore import uicore
from eve.client.script.ui.shared.mapView.mapViewSettings import IsAbstractModeActive
import geo2

class MapCameraController(BaseCameraController):
    kPan = 5.0

    def __init__(self, mapViewID = None, cameraID = None):
        self.cameraID = cameraID
        self.mapViewID = mapViewID
        BaseCameraController.__init__(self)

    def GetViewport(self):
        return self.GetCamera().GetViewport()

    def OnMouseWheel(self, *args):
        camera = self.GetCamera()
        if camera:
            dz = GetZoomDz()
            camera.Zoom(dz * 0.0005)

    def OnMouseMove(self, *args):
        camera = self.GetCamera()
        if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
            camera.Zoom(-CheckInvertZoom(uicore.uilib.dy) * 0.005)
        elif uicore.uilib.leftbtn:
            k = 0.01
            camera.Orbit(k * self.GetMouseDX(), k * self.GetMouseDY())
        elif uicore.uilib.rightbtn:
            if IsAbstractModeActive(self.mapViewID):
                self.PanAxis(camera)
            else:
                self.Pan(camera)

    def Pan(self, camera):
        k = self.kPan
        camera.Pan(-k * self.GetMouseDX(), k * self.GetMouseDY(), 0)

    def PanAxis(self, camera):
        k = self.kPan
        dx = k * self.GetMouseDX()
        dy = k * self.GetMouseDY()
        xAxis = camera.GetXAxis()
        yAxis = geo2.Vec3Cross(xAxis, camera.upDirection)
        camera.PanAxis(xAxis, -dx)
        camera.PanAxis(yAxis, -dy)
