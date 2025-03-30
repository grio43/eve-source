#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\shipOrbitHazardCamera.py
import evecamera
from eve.client.script.ui.camera.shipOrbitCamera import ShipOrbitCamera

class ShipOrbitHazardSpaceCamera(ShipOrbitCamera):
    cameraID = evecamera.CAM_SHIPORBIT_HAZARD
    name = 'ShipOrbitCameraHazard'
    minZoom = 120000
    minFov = 0.9
    maxFov = 1.4

    def IsLocked(self):
        return True

    def RegisterActivated(self):
        settings.char.ui.Set('spaceCameraID', evecamera.CAM_SHIPORBIT_HAZARD)
