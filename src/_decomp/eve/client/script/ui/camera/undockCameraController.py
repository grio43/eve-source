#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\undockCameraController.py
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
import evecamera
from carbonui.uicore import uicore

class UndockCameraController(BaseCameraController):
    cameraID = evecamera.CAM_UNDOCK

    def OnMouseUp(self, button, *args):
        if button == 0:
            self.SwitchToPrimaryCamera()

    def OnMouseMove(self, *args):
        if uicore.uilib.leftbtn:
            self.SwitchToPrimaryCamera()

    def OnMouseWheel(self, *args):
        self.SwitchToPrimaryCamera()

    def SwitchToPrimaryCamera(self):
        self.GetCamera().SwitchToPrimaryCamera()
