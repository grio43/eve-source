#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\capitalHangarCameraController.py
import evecamera
import math
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
from eve.client.script.ui.camera.cameraUtil import CheckInvertZoom, GetPowerOfWithSign
import carbonui.const as uiconst
from carbonui.uicore import uicore

class CapitalHangarCameraController(BaseCameraController):
    cameraID = evecamera.CAM_CAPITALHANGAR

    def OnMouseMove(self, *args):
        camera = self.GetCamera()
        kOrbit = evecamera.ORBIT_MOVE_DIST
        if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
            kZoom = 0.005
            self._Zoom(-uicore.uilib.dy, kZoom)
            if math.fabs(uicore.uilib.dx) > 1:
                camera.Orbit(0.01 * self.GetMouseDX(), 0.0)
        elif uicore.uilib.leftbtn:
            camera.Orbit(kOrbit * self.GetMouseDX(), kOrbit * uicore.uilib.dy)

    def OnMouseWheel(self, *args):
        k = 0.0005
        self._Zoom(uicore.uilib.dz, k)

    def _Zoom(self, dz, k):
        camera = self.GetCamera()
        dz = CheckInvertZoom(dz)
        dz = GetPowerOfWithSign(dz)
        camera.Zoom(k * dz)

    def OnGlobalRightMouseUp(self, obj, eventID, (vkey, flag)):
        if vkey != 1:
            return True
        self.GetCamera().ResetRotate()

    def OnMouseDown(self, button, *args):
        ret = BaseCameraController.OnMouseDown(self, button, *args)
        if button == 1:
            uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalRightMouseUp)
        return ret
