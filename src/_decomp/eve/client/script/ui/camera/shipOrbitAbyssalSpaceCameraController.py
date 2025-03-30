#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\shipOrbitAbyssalSpaceCameraController.py
from eve.client.script.ui.camera.shipOrbitCameraController import ShipOrbitCameraController
from evecamera import CAM_SHIPORBIT_ABYSSAL_SPACE

class ShipOrbitCameraAbyssalSpaceController(ShipOrbitCameraController):
    cameraID = CAM_SHIPORBIT_ABYSSAL_SPACE

    def __init__(self, *args, **kwargs):
        super(ShipOrbitCameraAbyssalSpaceController, self).__init__(*args, **kwargs)
