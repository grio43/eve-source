#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\modularHangarCameraController.py
import evecamera
import math
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
from eve.client.script.ui.camera.cameraUtil import CheckInvertZoom, GetPowerOfWithSign
import carbonui.const as uiconst
from carbonui.uicore import uicore
TRINITY_PICKABLE_HANGARVIEO_BUFFER_ID = 100

class ModularHangarCameraController(BaseCameraController):
    cameraID = evecamera.CAM_MODULARHANGAR
    enablePickTransparent = True

    def __init__(self):
        BaseCameraController.__init__(self)
        self.isRotating = False
        self.isTraveling = False

    def OnMouseMove(self, *args):
        camera = self.GetCamera()
        kOrbit = evecamera.ORBIT_MOVE_DIST
        if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
            kZoom = 0.005
            self._Zoom(-self.GetMouseDY(), kZoom)
            if math.fabs(self.GetMouseDX()) > 1:
                if self.IsCameraRotated():
                    camera.Rotate(0.01 * self.GetMouseDX(), 0.0)
                else:
                    camera.Orbit(0.01 * self.GetMouseDX(), 0.0)
        elif uicore.uilib.leftbtn:
            if self.isRotating:
                kRotate = 0.005 * camera.fov
                camera.Rotate(kRotate * self.GetMouseDX(), kRotate * self.GetMouseDY())
                if not camera.GetIsChangingShip():
                    camera.ResetRotate()
                    camera.ResetFOV()
                    camera.SetRotating(False)
                    self.isRotating = False
            else:
                camera.Orbit(kOrbit * self.GetMouseDX(), kOrbit * self.GetMouseDY())
        elif uicore.uilib.rightbtn and self.isRotating:
            kRotate = 0.005 * camera.fov
            camera.Rotate(kRotate * self.GetMouseDX(), kRotate * self.GetMouseDY())

    def OnMouseWheel(self, *args):
        k = 0.0005
        self._Zoom(uicore.uilib.dz, k)

    def GetAreaName(self, areaID):
        if areaID == TRINITY_PICKABLE_HANGARVIEO_BUFFER_ID:
            return 'billboard'
        else:
            return BaseCameraController.GetAreaName(self, areaID)

    def _Zoom(self, dz, k):
        camera = self.GetCamera()
        dz = CheckInvertZoom(dz)
        dz = GetPowerOfWithSign(dz)
        if uicore.uilib.Key(uiconst.VK_MENU) or self.IsCameraRotated():
            camera.FovZoom(k * dz)
        else:
            camera.Zoom(k * dz)

    def OnGlobalRightMouseUp(self, obj, eventID, (vkey, flag)):
        if vkey != 1:
            return True
        camera = self.GetCamera()
        camera.ResetRotate()
        camera.ResetFOV()
        camera.SetRotating(False)
        self.isRotating = False

    def OnMouseDown(self, button, *args):
        ret = BaseCameraController.OnMouseDown(self, button, *args)
        camera = self.GetCamera()
        if camera.GetIsChangingShip():
            self.isRotating = True
            camera.SetRotating(True)
        if button == 1:
            self.isRotating = True
            camera = self.GetCamera()
            camera.SetRotating(True)
            uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalRightMouseUp)
        return ret

    def OnMouseUp(self, button, *args):
        BaseCameraController.OnMouseUp(self, button, *args)
        camera = self.GetCamera()
        if self.isRotating and camera.GetIsChangingShip():
            camera.ResetRotate()
            camera.ResetFOV()
            camera.SetRotating(False)
            self.isRotating = False

    def IsCameraRotated(self):
        return uicore.uilib.rightbtn and self.GetCamera().IsRotated()
