#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\util\cameraSpeedOffsetter.py
import math
import blue
import geo2
from carbonui.uianimations import animations
from eve.client.script.ui.camera.cameraUtil import IsDynamicCameraMovementEnabled, GetBallRadius, GetSpeedDirection, Vector3Chaser
K_OFFSET = 350.0

class CameraSpeedOffsetter:

    def __init__(self):
        self.speedDir = None
        self.offset = (0, 0, 0)
        self.vectorChaser = Vector3Chaser(speed=1.0)
        self.rampValue = 0.0

    def Reset(self):
        self.vectorChaser.ResetValue()

    def GetSpeedOffset(self):
        return self.vectorChaser.GetValue()

    def _Update(self, ball, maxZoom, isTracking):
        if IsDynamicCameraMovementEnabled() and not isTracking:
            speedProp = self._GetSpeedOffsetProportion(ball)
            maxOffset = min(0.95 * maxZoom - GetBallRadius(ball), GetBallRadius(ball))
            offsetAmount = maxOffset * speedProp * self.rampValue
            speedDir = GetSpeedDirection(ball)
            self.offset = geo2.Vec3Scale(speedDir, offsetAmount)
        else:
            self.offset = (0, 0, 0)
        self.vectorChaser.SetTargetValue(self.offset)

    def _GetSpeedOffsetProportion(self, ball):
        speed = self.GetLookAtBallSpeed(ball)
        velocity = geo2.Vec3Length(speed)
        if velocity <= 0.0:
            return 0.0
        else:
            return math.exp(-K_OFFSET / velocity)

    def GetLookAtBallSpeed(self, ball):
        vec = ball.GetVectorDotAt(blue.os.GetSimTime())
        vec = (vec.x, vec.y, vec.z)
        return vec

    def OnActivated(self):
        animations.MorphScalar(self, 'rampValue', 0.0, 1.0, duration=2.0)
        self.Reset()
