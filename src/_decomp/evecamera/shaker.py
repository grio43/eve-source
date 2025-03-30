#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evecamera\shaker.py
import blue
import geo2
import trinity
DEFAULT_NOISE_SCALE = 0
DEFAULT_NOISE_DAMP = 1.1

class ShakeBehavior(object):

    def __init__(self, key = None):
        self.key = key
        self.noiseCurve = None
        self.scaleCurve = None
        self.dampCurve = None
        self.noiseScale = DEFAULT_NOISE_SCALE
        self.noiseDamp = DEFAULT_NOISE_DAMP


class ShakeController(object):

    def __init__(self, camera):
        self._currentBehavior = ShakeBehavior()
        self._camera = camera
        self._isEnabled = True

    def _Apply(self, behavior):
        self._camera.ResetCurveStartTime()
        self._camera.noiseCurve = behavior.noiseCurve
        self._camera.noiseScaleCurve = behavior.scaleCurve
        self._camera.noiseScale = behavior.noiseScale
        self._camera.noiseDampCurve = behavior.dampCurve
        self._camera.noiseDamp = behavior.noiseDamp

    def Enable(self, enabled):
        self._isEnabled = enabled
        if self._isEnabled:
            self._camera.noise = True
        else:
            self.ClearCurrentShake()
            self._camera.noise = False

    def DoCameraShake(self, shakeObj):
        if not self._isEnabled:
            return
        self._Apply(shakeObj)
        self._currentBehavior = shakeObj

    def EndCameraShake(self, key = None):
        if not self._isEnabled:
            return
        if self._currentBehavior.key == key:
            self.ClearCurrentShake()

    def ClearCurrentShake(self):
        if not self._isEnabled:
            return
        self._currentBehavior = ShakeBehavior()
        self._Apply(self._currentBehavior)
