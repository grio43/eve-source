#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\modularHangarCapitalCameraController.py
import evecamera
import math
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
from eve.client.script.ui.camera.cameraUtil import CheckInvertZoom, GetPowerOfWithSign
import carbonui.const as uiconst
from carbonui.uicore import uicore
TRINITY_PICKABLE_HANGARVIEO_BUFFER_ID = 100

class ModularHangarCapitalCameraController(BaseCameraController):
    cameraID = evecamera.CAM_MODULARHANGAR_CAPITAL
    enablePickTransparent = True

    def __init__(self):
        BaseCameraController.__init__(self)
        self.isRotating = False

    def OnMouseMove(self, *args):
        camera = self.GetCamera()
        kOrbit = evecamera.ORBIT_MOVE_DIST
        if uicore.uilib.leftbtn or uicore.uilib.rightbtn:
            camera.Orbit(kOrbit * self.GetMouseDX(), kOrbit * self.GetMouseDY())

    def OnMouseWheel(self, *args):
        pass

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

    def OnGlobalMouseUp(self, obj, eventID, (vkey, flag)):
        if vkey != 1 and vkey != 0:
            return True
        camera = self.GetCamera()
        camera.ResetRotate()
        camera.ResetFOV()
        self.isRotating = False

    def OnMouseDown(self, button, *args):
        ret = BaseCameraController.OnMouseDown(self, button, *args)
        self.isRotating = True
        uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp)
        return ret

    def IsCameraRotated(self):
        return self.isRotating
