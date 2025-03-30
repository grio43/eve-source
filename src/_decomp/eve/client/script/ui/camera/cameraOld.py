#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\cameraOld.py
from eve.client.script.ui.camera.spaceCamera import SpaceCamera

class CameraOld(SpaceCamera):

    def UpdateCameraBobbing(self, *args):
        self.idleMove = 0
