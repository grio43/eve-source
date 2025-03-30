#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\debugCamera.py
from eve.client.script.ui.camera.tacticalCamera import TacticalCamera
import evecamera

class DebugCamera(TacticalCamera):
    name = 'DebugCamera'
    cameraID = evecamera.CAM_DEBUG
    minFov = 0.01
    maxFov = 1.0
    default_fov = 1.0

    def LookAt(self, itemID, *args, **kwargs):
        TacticalCamera.LookAt(self, itemID, *args, **kwargs)
        self.SetFovTarget(self.default_fov)
