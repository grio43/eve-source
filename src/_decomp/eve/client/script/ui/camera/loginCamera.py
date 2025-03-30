#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\loginCamera.py
from eve.client.script.ui.camera.baseCamera import Camera
import evecamera

class LoginCamera(Camera):
    name = 'LoginCamera'
    cameraID = evecamera.CAM_LOGIN
    default_fov = 0.8
    default_eyePosition = (0.0, 0.0, 22.0)
