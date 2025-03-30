#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\shipOrbitRestrictedCamera.py
import evecamera
from eve.client.script.ui.camera import cameraUtil
from eve.client.script.ui.camera.shipOrbitCamera import ShipOrbitCamera
import logging
logger = logging.getLogger(__name__)

class RestrictedShipOrbitCamera(ShipOrbitCamera):
    cameraID = evecamera.CAM_SHIPORBIT_RESTRICTED
    name = 'ShipOrbitCamera'

    def __init__(self):
        self.isLocked = False
        self.isRotationEnabled = True
        self.ResetZoom()
        ShipOrbitCamera.__init__(self)

    def OnActivated(self, **kwargs):
        super(RestrictedShipOrbitCamera, self).OnActivated(**kwargs)

    def ResetZoom(self):
        self.lockedMinZoom = None
        self.lockedMaxZoom = None

    def IsMinZoomValid(self, minZoom, maxZoom):
        return not minZoom or not maxZoom or minZoom > maxZoom

    def CorrectMinZoom(self, minZoom, maxZoom):
        if self.IsMinZoomValid(minZoom, maxZoom):
            return minZoom
        return maxZoom + 1

    def SqueezeZoom(self, minZoom, maxZoom):
        self.lockedMaxZoom = maxZoom
        if self.lockedMaxZoom:
            self.SetMaxZoom(self.lockedMaxZoom)
        self.lockedMinZoom = self.CorrectMinZoom(minZoom, self.lockedMaxZoom)
        if self.lockedMinZoom:
            self.SetMinZoom(self.lockedMinZoom)

    def SqueezePitch(self, minPitch, maxPitch):
        self.kMinPitch = max(minPitch, self.kMinPitch)
        self.kMaxPitch = min(maxPitch, self.kMaxPitch)
        currentPitch = self.GetPitch()
        desiredPitch = self.ClampPitch(currentPitch)
        self.SetPitch(desiredPitch)

    def UpdateMaxZoom(self):
        ball = self.lookAtBall
        nearClip = self.nearClip
        ballMaxZoom = cameraUtil.GetBallMaxZoom(ball, nearClip)
        newMaxZoom = max(ballMaxZoom, self.lockedMaxZoom or 0.0)
        newMinZoom = self.CorrectMinZoom(self.lockedMinZoom, newMaxZoom)
        if newMinZoom:
            self.SetMinMaxZoom(newMinZoom, newMaxZoom)
        else:
            self.SetMaxZoom(newMaxZoom)

    def Lock(self, minZoom, maxZoom, minPitch, maxPitch, isRotationEnabled):
        self.isLocked = True
        if not isRotationEnabled:
            self.DisableRotation()
        self.SqueezeZoom(minZoom, maxZoom)
        self.SqueezePitch(minPitch, maxPitch)

    def Unlock(self):
        self.isLocked = False
        self.EnableRotation()
        self.ResetZoom()

    def IsLocked(self):
        return self.isLocked

    def EnableRotation(self):
        self.isRotationEnabled = True
        self.EnableManualControl()

    def DisableRotation(self):
        self.isRotationEnabled = False
        self.DisableManualControl()

    def Orbit(self, *args, **kwargs):
        if self.isRotationEnabled:
            super(RestrictedShipOrbitCamera, self).Orbit(*args, **kwargs)

    def Rotate(self, *args, **kwargs):
        if self.isRotationEnabled:
            super(RestrictedShipOrbitCamera, self).Rotate(*args, **kwargs)

    def Track(self, *args, **kwargs):
        if self.isRotationEnabled:
            super(RestrictedShipOrbitCamera, self).Track(*args, **kwargs)

    def RegisterActivated(self):
        settings.char.ui.Set('spaceCameraID', evecamera.CAM_SHIPORBIT_RESTRICTED)
