#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\util\cameraBobbingOffsetter.py
import math
import blue
import geo2
from carbonui.uianimations import animations
BOBBING_SPEED = 0.5
VOMIT_THRESHOLD = 3100

class CameraBobbingOffsetter:

    def __init__(self):
        self.angle = 0.0
        self.rampValue = 0.0

    def UpdateOffset(self, atPosition, eyePosition):
        t = blue.os.fps
        self.angle += 1.0 / t * BOBBING_SPEED
        if self.angle > 2 * math.pi:
            self.angle %= 2 * math.pi
        distance = min(VOMIT_THRESHOLD, geo2.Vec3Distance(atPosition, eyePosition))
        idleYaw = distance * math.cos(self.angle) / 400.0 * self.rampValue
        idlePitch = 1.2 * idleYaw * math.sin(self.angle) * self.rampValue
        bobbingOffset = (idleYaw, idlePitch, 0)
        return bobbingOffset

    def OnActivated(self):
        animations.MorphScalar(self, 'rampValue', 0.0, 1.0, duration=2.0)
