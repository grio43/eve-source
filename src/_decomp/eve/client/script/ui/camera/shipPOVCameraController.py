#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\shipPOVCameraController.py
from eve.client.script.ui.camera.cameraUtil import SetShipDirection, GetZoomDz
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
import carbonui.const as uiconst
import evecamera
from carbonui.uicore import uicore
FOV_LEVELS = [1.0, 0.625, 0.25]

class ShipPOVCameraController(BaseCameraController):
    cameraID = evecamera.CAM_SHIPPOV

    def __init__(self):
        BaseCameraController.__init__(self)
        self.fovLevel = 0
        self.dzAccumulated = 0
        self.GetCamera().fov = FOV_LEVELS[self.fovLevel]

    def OnMouseMove(self, *args):
        if uicore.uilib.leftbtn:
            k = 0.002 * self.GetCamera().fov
            self.GetCamera().Rotate(k * self.GetMouseDX(), k * self.GetMouseDY())

    def OnMouseWheel(self, *args):
        camera = self.GetCamera()
        dz = GetZoomDz()
        self.dzAccumulated += dz
        if self.dzAccumulated < -120:
            dz = -1
            self.dzAccumulated = 0
        elif self.dzAccumulated > 120:
            dz = 1
            self.dzAccumulated = 0
        else:
            return
        if dz < 0:
            if self.fovLevel == len(FOV_LEVELS) - 1:
                return
            self._ChangeFov(1)
        elif self.fovLevel > 0:
            self._ChangeFov(-1)

    def _ChangeFov(self, fovLevelDiff):
        self.fovLevel += fovLevelDiff
        sm.GetService('audio').SendUIEvent('ship_interior_cam_zoom_play')
        fov = FOV_LEVELS[self.fovLevel]
        camera = self.GetCamera()
        uicore.animations.MorphScalar(camera, 'fov', camera.fov, fov, duration=0.35, curveType=uiconst.ANIM_OVERSHOT)

    def OnDblClick(self, *args):
        if uicore.uilib.rightbtn or uicore.uilib.mouseTravel > 6:
            return
        SetShipDirection(self.GetCamera())

    def OnMouseDown(self, button, *args):
        ret = BaseCameraController.OnMouseDown(self, button, *args)
        if button == 0:
            uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalRightMouseUp)
        return ret

    def OnGlobalRightMouseUp(self, obj, eventID, (vkey, flag)):
        if vkey != 0:
            return True
        self.GetCamera().ResetRotate()
