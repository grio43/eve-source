#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\debugCameraController.py
import math
from eve.client.script.ui.camera.cameraUtil import GetZoomDz, GetPanVectorForZoomToCursor, CheckInvertZoom
import evecamera
import carbonui.const as uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.camera.tacticalCameraController import TacticalCameraController

class DebugCameraController(TacticalCameraController):
    cameraID = evecamera.CAM_DEBUG

    def __init__(self, *args, **kwargs):
        super(DebugCameraController, self).__init__(*args, **kwargs)
        cam = self.GetCamera()
        if cam:
            cam.Detach()
