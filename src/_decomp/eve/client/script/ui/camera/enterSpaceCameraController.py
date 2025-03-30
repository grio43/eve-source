#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\enterSpaceCameraController.py
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
import evecamera
from carbonui.uicore import uicore

class EnterSpaceCameraController(BaseCameraController):
    cameraID = evecamera.CAM_ENTERSPACE

    def OnMouseUp(self, *args):
        self.SwitchToPrimaryCamera()

    def OnMouseMove(self, *args):
        if uicore.uilib.leftbtn:
            self.SwitchToPrimaryCamera()

    def OnMouseWheel(self, *args):
        self.SwitchToPrimaryCamera()

    def SwitchToPrimaryCamera(self):
        self.GetCamera().SwitchToPrimaryCamera()
