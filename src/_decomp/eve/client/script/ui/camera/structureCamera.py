#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\structureCamera.py
from eve.client.script.ui.camera.shipOrbitCamera import ShipOrbitCamera
from evecamera import CAM_STRUCTURE

class StructureCamera(ShipOrbitCamera):
    cameraID = CAM_STRUCTURE
    name = 'StructureCamera'

    def RegisterActivated(self):
        pass
