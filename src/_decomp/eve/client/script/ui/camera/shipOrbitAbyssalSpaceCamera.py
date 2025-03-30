#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\shipOrbitAbyssalSpaceCamera.py
import evecamera
from eve.client.script.ui.camera.shipOrbitCamera import ShipOrbitCamera

class ShipOrbitAbyssalSpaceCamera(ShipOrbitCamera):
    cameraID = evecamera.CAM_SHIPORBIT_ABYSSAL_SPACE
    name = 'ShipOrbitCameraAbyssalSpace'
    minZoom = 30000
    minFov = 1.0
    maxFov = 2.0

    def IsLocked(self):
        return True

    def RegisterActivated(self):
        settings.char.ui.Set('spaceCameraID', evecamera.CAM_SHIPORBIT_ABYSSAL_SPACE)
