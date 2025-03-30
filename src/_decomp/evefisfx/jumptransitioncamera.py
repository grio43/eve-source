#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evefisfx\jumptransitioncamera.py
import blue
import carbon.common.script.util.mathUtil as mathUtil
import evecamera
import evecamera.animation as camanim
import evecamera.utils as camutils
import geo2
import math
import trinity
import uthread2
import eve.client.script.parklife.states as states
from carbonui.uicore import uicore

class LookAnimation(object):
    __guid__ = 'effects.JumpTransitionLookAnimation'

    def __init__(self, camera, rotation, startFocusID = None, endFocusID = None, startTranslation = None, endTranslation = None):
        self.camera = camera
        self.rotation = rotation
        self.startBall = None
        self.endTranslationFromParent = endTranslation
        self.startTranslation = startTranslation
        self.startFocusID = startFocusID
        self.endFocusID = endFocusID

    def _GetFocusPosition(self):
        if self.startFocusID is None:
            return (0, 0, 0)
        park = sm.GetService('michelle').GetBallpark()
        if park is None:
            return (0, 0, 0)
        ball = park.GetBall(self.startFocusID)
        if ball is None:
            return (0, 0, 0)
        pos = ball.GetVectorAt(blue.os.GetSimTime())
        pos = (pos.x, pos.y, pos.z)
        model = ball.GetModel()
        if model and hasattr(model, 'locatorSets'):
            locatorSet = model.locatorSets.FindByName('jump_center')
            if locatorSet and len(locatorSet.locators) > 0:
                jumpCenterPosition = locatorSet.locators[0][0]
                posVector = geo2.QuaternionTransformVector(self.rotation, jumpCenterPosition)
                pos = geo2.Vec3Add(pos, posVector)
        return pos

    def Stop(self):
        pass

    def Start(self):
        uthread2.StartTasklet(self._DoCameraLookAnimation_Thread)

    def _DoCameraLookAnimation_Thread(self):
        if self.startTranslation:
            targetTranslation = self.startTranslation
        else:
            targetTranslation = self.camera.GetZoomDistance()
        direction = geo2.Vec3Scale(geo2.QuaternionTransformVector(self.rotation, (0, 0, 1)), -targetTranslation)
        atPosition = self._GetFocusPosition()
        eyePosition = geo2.Vec3Add(atPosition, direction)
        self.camera.TransitTo(atPosition, eyePosition, smoothing=0.0)

    def OnJumpDone(self):
        itemID = self.GetJumpEndLookAtID()
        if itemID is not None:
            sm.GetService('stateSvc').SetState(itemID, states.selected, 1)

    def GetJumpEndLookAtID(self):
        lookatID = self.endFocusID
        autoPilot = sm.GetService('autoPilot')
        starmapSvc = sm.GetService('starmap')
        destinationPath = starmapSvc.GetDestinationPath()
        if destinationPath is not None and len(destinationPath) > 0 and destinationPath[0] is not None:
            bp = sm.GetService('michelle').GetBallpark()
            if bp is not None:
                destID = autoPilot.GetGateOrStationID(bp, destinationPath[0])
                if destID is not None:
                    lookatID = destID
        return lookatID


class AbyssalLookAnimation(LookAnimation):
    __guid__ = 'effects.AbyssalLookAnimation'

    def __init__(self, camera, distance, effectRoot, startFocusID):
        self.camera = camera
        self.distance = distance
        self.effectRoot = effectRoot
        self.startFocusID = startFocusID
        self.endFocusID = None

    def Start(self):
        atPosition = self._GetFocusPosition()
        eyePos = self.camera.GetEyePosition()
        dir = geo2.Vec3Direction(atPosition, eyePos)
        eyePos = geo2.Vec3Add(geo2.Vec3Scale(dir, -self.distance), atPosition)
        dir = geo2.QuaternionRotationArc(dir, (0.0, 0.0, 1.0))
        self.effectRoot.rotation = geo2.QuaternionInverse(dir)
        self.camera.TransitTo(atPosition, eyePos, smoothing=0.0)

    def OnJumpDone(self):
        pass


class AbyssalGateLookAnimation(LookAnimation):
    __guid__ = 'effects.AbyssalGateLookAnimation'

    def __init__(self, camera, distance, rotation, gateID):
        self.camera = camera
        self.distance = distance
        self.rotation = rotation
        self.startFocusID = gateID
        self.endFocusID = None

    def Start(self):
        direction = geo2.Vec3Scale(geo2.QuaternionTransformVector(self.rotation, (0, 0, 1)), -self.distance)
        atPosition = self._GetFocusPosition()
        eyePosition = geo2.Vec3Add(atPosition, direction)
        self.camera.TransitTo(atPosition, eyePosition, smoothing=0.0)


class AnimateGatePan(camanim.BaseCameraAnimation):

    def __init__(self, initialTranslation, progressCurve):
        camanim.BaseCameraAnimation.__init__(self, camanim.PAN_ANIMATION, 0, evecamera.PRIORITY_HIGH, False)
        self.initialTranslation = initialTranslation
        self.progressCurve = progressCurve

    def Tick(self, camera, simTime, clockTime):
        t = blue.os.TimeDiffInMs(self.timeStart, simTime) / 1000.0
        progress = self.progressCurve.GetValueAt(t)
        camera.translationFromParent = mathUtil.Lerp(self.initialTranslation, 0, progress)

    def Stop(self):
        self.isDone = True


class AnimateGateLookAt(camanim.BaseCameraAnimation):

    def __init__(self, endPosFunction, translationOffset, progressCurve):
        camanim.BaseCameraAnimation.__init__(self, camanim.TRANSLATION_ANIMATION, 0, evecamera.PRIORITY_HIGH, False)
        self.startPos = (0.0, 0.0, 0.0)
        self.progressCurve = progressCurve
        self.started = False
        self.translationOffset = translationOffset
        self.endPosFunction = endPosFunction

    def _FirstTick(self, cameraParent, simTime):
        self.started = True
        if cameraParent.translationCurve is not None:
            self.startPos = cameraParent.translationCurve.GetVectorAt(simTime)
            self.startPos = (self.startPos.x, self.startPos.y, self.startPos.z)
            cameraParent.translationCurve = None
        else:
            self.startPos = cameraParent.translation

    def Tick(self, camera, simTime, clockTime):
        if self.isDone:
            return
        t = blue.os.TimeDiffInMs(self.timeStart, simTime) / 1000.0
        progress = self.progressCurve.GetValueAt(t)
        cameraParent = camera.GetCameraParent()
        if not self.started:
            self._FirstTick(cameraParent, simTime)
            self.started = True
        endPos = self.endPosFunction()
        endPos = geo2.Vec3Add(endPos, self.translationOffset)
        cameraParent.translation = geo2.Vec3Lerp(self.startPos, endPos, progress)

    def Stop(self):
        self.isDone = True


class OutFOV(camanim.BaseCameraAnimation):

    def __init__(self, duration):
        camanim.BaseCameraAnimation.__init__(self, camanim.FOV_ANIMATION, duration, evecamera.PRIORITY_HIGH, False)
        self.fovStart = 1
        self.fovEnd = 2.2
        self.animationStartsAt = 0.3

    def Start(self, camera, simTime, clockTime):
        camanim.BaseCameraAnimation.Start(self, camera, simTime, clockTime)
        self.fovStart = camera.fov

    def _Tick(self, progress, camera):
        progress = max(0, (progress - self.animationStartsAt) / (1 - self.animationStartsAt))
        camera.fov = mathUtil.Lerp(self.fovStart, self.fovEnd, 1.0 - math.pow(1.0 - progress, 2.0))

    def End(self, camera):
        camera.fov = self.fovEnd


class OutExtraTransl(camanim.BaseCameraAnimation):

    def __init__(self, duration, finalOffset):
        camanim.BaseCameraAnimation.__init__(self, camanim.EXTRA_TRANSLATION_ANIMATION, duration, evecamera.PRIORITY_HIGH, False)
        self.finalOffset = finalOffset

    def _Tick(self, progress, camera):
        transl = geo2.Vec3Lerp((0, 0, 0), self.finalOffset, math.pow(progress, 4.0))
        camera.SetEffectOffset(transl)

    def End(self, camera):
        camera.SetEffectOffset(self.finalOffset)


class InFOV(camanim.BaseCameraAnimation):

    def __init__(self, duration):
        camanim.BaseCameraAnimation.__init__(self, camanim.FOV_ANIMATION, duration, evecamera.PRIORITY_HIGH, False)
        self.fovStart = 2.2
        self.fovEnd = 1.0
        self.animationStartsAt = 0.3

    def Start(self, camera, simTime, clockTime):
        camanim.BaseCameraAnimation.Start(self, camera, simTime, clockTime)
        self.fovStart = camera.fov

    def _Tick(self, progress, camera):
        progress = math.pow(progress, 4.0)
        camera.fov = mathUtil.Lerp(self.fovStart, self.fovEnd, progress)

    def End(self, camera):
        camera.fov = self.fovEnd


class InExtraTransl(camanim.BaseCameraAnimation):

    def __init__(self, duration, offset):
        camanim.BaseCameraAnimation.__init__(self, camanim.EXTRA_TRANSLATION_ANIMATION, duration, evecamera.PRIORITY_HIGH, False)
        self.offset = offset

    def _Tick(self, progress, camera):
        offset = geo2.Vec3Lerp(self.offset, (0, 0, 0), math.pow(progress, 2.0))
        camera.SetEffectOffset(offset)

    def End(self, camera):
        offset = (0, 0, 0)
        camera.SetEffectOffset(offset)
