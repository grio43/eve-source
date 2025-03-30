#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\jumpCamera.py
import blue
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
import evecamera
import geo2

class JumpCamera(BaseSpaceCamera):
    name = 'JumpCamera'
    cameraID = evecamera.CAM_JUMP
    default_fov = 1.0

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.bp = None
        self.oldCameraZoom = 0
        self.egoPos = None

    def OnActivated(self, lastCamera = None, itemID = None, **kwargs):
        BaseSpaceCamera.OnActivated(self, **kwargs)
        self.bp = sm.GetService('michelle').GetBallpark()
        if lastCamera and lastCamera.cameraID in evecamera.INSPACE_CAMERAS:
            lastAtPos = lastCamera.atPosition
            if lastCamera.cameraID == evecamera.CAM_TACTICAL:
                lastAtPos = lastCamera.GetAtPositionClosestToShip()
            self.SetAtPosition(lastAtPos)
            self.SetEyePosition(lastCamera.eyePosition)
            self.oldCameraZoom = super(JumpCamera, self).GetZoom()
            self.fov = lastCamera.fov
        self.SetFovTarget(self.default_fov)
        self.egoPos = self.bp.GetCurrentEgoPos()

    def GetZoom(self):
        return self.oldCameraZoom

    @property
    def transitionDelay(self):
        if sm.GetService('subway').Enabled():
            return 0.7 / blue.os.simDilation
        else:
            return 0.1

    def GetItemID(self):
        return self.ego

    def IsLocked(self):
        return True

    def Track(self, itemID, **kwargs):
        pass

    def LookAt(self, itemID, radius = None, **kwargs):
        if kwargs.get('force', False):
            super(BaseSpaceCamera, self).LookAt(itemID, radius, **kwargs)

    def OnBallRemoved(self, ball):
        if ball.id == self.ego:
            self.bp = None

    def Update(self):
        BaseSpaceCamera.Update(self)
        if self.bp:
            newPos = self.bp.GetCurrentEgoPos()
            diff = geo2.Vec3SubtractD(newPos, self.egoPos)
            self.egoPos = newPos
            self.atPosition = geo2.Vec3SubtractD(self._atPosition, diff)
            self.eyePosition = geo2.Vec3SubtractD(self._eyePosition, diff)
