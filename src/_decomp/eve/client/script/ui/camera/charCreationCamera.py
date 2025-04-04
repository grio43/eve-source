#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\charCreationCamera.py
import math
import geo2
import blue
import mathext
import signals
import charactercreator.const as ccConst
from carbonui.camera.behaviors.cameraBehavior import CameraBehavior
from carbonui.camera.polarCamera import PolarCamera
from carbonui.util.various_unsorted import GetAttrs
CONTROL_NONE = 0
CONTROL_VERTICAL = 1
CONTROL_BOTH = 2

class CharCreationCamera(PolarCamera):

    def __init__(self, avatar, modeName = ccConst.CAMERA_MODE_DEFAULT):
        PolarCamera.__init__(self)
        self.cameraModeChanged = signals.Signal(signalName='cameraModeChanged')
        self.frontClip = 0.1
        self.backClip = 1000.0
        self.pitch = math.pi / 2
        self._transformDistance = None
        self._transformPOI = None
        self._rotateAvatar = None
        self._onFocusValue = False
        self.moveCallback = None
        self.updateFocus = True
        self.AddBehavior(CharCreationCameraHandler())
        self.focus = (0.0, 0.0, 0.0)
        self.xFactor = 0.0
        self.yFactor = 0.0
        self._currentMode = None
        self.ToggleMode(modeName, avatar)

    def ToggleMode(self, modeName, avatar = None, transformTime = None):
        self.avatar = avatar
        self.UpdateAvatarStats()
        self.updateFocus = True
        self.xTarget = 0.0
        self.yTarget = 0.0
        setup = {'controlStyle': CONTROL_NONE,
         'farDistance': 1000.0,
         'nearDistance': 1.0,
         'minRotation': None,
         'maxRotation': None,
         'fieldOfView': 0.9,
         'minPanX': -0.14,
         'maxPanX': 0.12,
         'minPanY': -0.12,
         'maxPanY': 0.12,
         'nearPan': 0.0,
         'nearFocusY': 0.0,
         'farFocusY': 0.0,
         'nearMinTilt': 0.0,
         'nearMaxTilt': math.pi,
         'farMinTilt': 0.0,
         'farMaxTilt': math.pi,
         'distance': 1.7,
         'poi': (0, 1.5, 0),
         'rotateAvatar': True}
        if modeName in (ccConst.CAMERA_MODE_FACE, ccConst.CAMERA_MODE_BODY):
            setup['controlStyle'] = CONTROL_VERTICAL
            setup['fieldOfView'] = 0.3
            setup['farDistance'] = 8.0
            setup['nearDistance'] = 0.9
            setup['minPanX'] = 0.0
            setup['maxPanX'] = 0.0
            setup['minPanY'] = -1.5
            setup['maxPanY'] = 0.1
            setup['nearPan'] = 0.0
            setup['nearFocusY'] = 0.0
            setup['farFocusY'] = -self.avatarEyeHeight / 2.0 + 0.1
            setup['nearMinTilt'] = math.pi * 0.4
            setup['nearMaxTilt'] = math.pi * 0.66
            setup['farMinTilt'] = math.pi * 0.5
            setup['farMaxTilt'] = math.pi * 0.5
            if modeName == ccConst.CAMERA_MODE_FACE:
                setup['distance'] = setup['nearDistance'] + 0.5
                setup['poi'] = (0, -setup['nearFocusY'], 0)
                setup['yFactor'] = setup['nearFocusY']
            else:
                setup['distance'] = setup['farDistance']
                setup['poi'] = (0, -setup['farFocusY'], 0)
                setup['yFactor'] = setup['farFocusY']
        elif modeName == ccConst.CAMERA_MODE_PORTRAIT:
            setup['controlStyle'] = CONTROL_BOTH
            setup['minRotation'] = 1.0
            setup['maxRotation'] = 2.5
            setup['fieldOfView'] = 0.3
            setup['farDistance'] = 2.5
            setup['nearDistance'] = 0.6
            setup['minPanX'] = -0.2
            setup['maxPanX'] = 0.2
            setup['minPanY'] = -0.15
            setup['maxPanY'] = 0.15
            setup['nearPan'] = 0.07
            setup['nearFocusY'] = 0.0
            setup['farFocusY'] = 0.0
            setup['nearMinTilt'] = math.pi * 0.33
            setup['nearMaxTilt'] = math.pi * 0.66
            setup['farMinTilt'] = math.pi * 0.33
            setup['farMaxTilt'] = math.pi * 0.66
            setup['distance'] = setup['nearDistance'] + 0.5
            setup['rotateAvatar'] = False
        self._transformDistance = None
        self._transformPOI = None
        if (self._rotateAvatar is None or self._rotateAvatar != setup['rotateAvatar']) and self.avatar:
            self.avatar.rotation = (0, 0, 0, 1)
            self.yaw = math.pi / 2
        self._rotateAvatar = setup['rotateAvatar']
        now = blue.os.GetWallclockTime()
        for k, v in setup.iteritems():
            if transformTime:
                if k == 'distance':
                    self._transformDistance = (now,
                     self.distance,
                     v,
                     transformTime)
                elif k == 'poi':
                    self._transformPOI = (now,
                     (0.0, -self.yFactor, 0.0),
                     v,
                     transformTime)
                    self._onFocusValue = True
                else:
                    setattr(self, k, v)
            else:
                setattr(self, k, v)

        self._ChangeMode(modeName)

    def _ChangeMode(self, newMode):
        previousMode = self._currentMode
        self._currentMode = newMode
        if previousMode != self._currentMode:
            self.cameraModeChanged(previousMode, self._currentMode)

    def UpdatePortraitInfo(self):
        self.UpdateAvatarStats()
        self.nearFocusY = self.avatarEyeHeight
        self.farFocusY = self.avatarEyeHeight

    def UpdateAvatar(self, avatar):
        self.avatar = avatar

    def GetBonePosition(self, boneName):
        if self.avatar is not None and self.avatar.animationUpdater is not None:
            joint = self.avatar.GetBoneIndex(boneName)
            if joint == 4294967295L:
                return (0.0, 0.0, 0.0)
            ret = self.avatar.GetBonePosition(joint)
            return ret
        return (0.0, 0.0, 0.0)

    def UpdateAvatarStats(self):
        if self.avatar is not None and self.avatar.animationUpdater is not None:
            blue.resMan.Wait()
            pos = self.GetBonePosition('fj_eyeballRight')
            self.avatarEyeHeight = pos[1]
        else:
            self.avatarEyeHeight = 0.0

    def PlacePortraitCamera(self, pos, poi):
        direction = geo2.Subtract(pos, poi)
        self.distance = geo2.Vec3Length(direction)
        direction = geo2.Vec3Normalize(direction)
        self.yaw = math.acos(direction[0])
        self.pitch = math.asin(direction[1]) + math.pi / 2.0
        right = self.GetBonePosition('fj_eyeballRight')
        left = self.GetBonePosition('fj_eyeballLeft')
        self.focus = geo2.Add(right, left)
        self.focus = geo2.Vector(*self.focus) * 0.5
        xFactor, yFactor = self.GetCorrectCameraXandYFactors(pos, poi)
        self.xFactor = xFactor
        self.yFactor = yFactor

    def GetCorrectCameraXandYFactors(self, position, poi):
        cameraZ = geo2.Vec3Normalize(geo2.Subtract(position, poi))
        cameraX = geo2.Vec3Cross(cameraZ, (0.0, 1.0, 0.0))
        cameraY = geo2.Vec3Cross(cameraZ, cameraX)
        cameraMatrix = ((cameraX[0],
          cameraY[0],
          cameraZ[0],
          0.0),
         (cameraX[1],
          cameraY[1],
          cameraZ[1],
          0.0),
         (cameraX[2],
          cameraY[2],
          cameraZ[2],
          0.0),
         (0.0, 0.0, 0.0, 1.0))
        offset = geo2.Subtract(self.focus, poi)
        res = geo2.Vec3Transform(offset, cameraMatrix)
        return (res[0], res[1])

    def Zoom(self, delta):
        newFov = self.fieldOfView + delta * 0.0005
        newFov = min(self.maxFov, max(self.minFov, newFov))
        self.fieldOfView = newFov
        self.xFactor = self.xTarget
        self.yFactor = self.yTarget

    def Dolly(self, delta):
        if self.controlStyle == CONTROL_NONE:
            return
        if self.controlStyle == CONTROL_BOTH:
            self.xFactor = self.xTarget
            self.yFactor = self.yTarget
        newDistance = min(self.farDistance, max(self.nearDistance, self.distance - self.distance * (delta * 0.0025)))
        self.distance = newDistance
        if self._currentMode == ccConst.CAMERA_MODE_FACE and newDistance > 0.75 * self.farDistance:
            self._ChangeMode(ccConst.CAMERA_MODE_BODY)
        elif self._currentMode == ccConst.CAMERA_MODE_BODY and newDistance < self.nearDistance + 0.5:
            self._ChangeMode(ccConst.CAMERA_MODE_FACE)
        if self._onFocusValue:
            portion = self.GetPortionFromDistance()
            self.yFactor = mathext.lerp(self.nearFocusY, self.farFocusY, portion)

    def GetPortionFromDistance(self):
        minmaxRange = self.farDistance - self.nearDistance
        portion = (self.distance - self.nearDistance) / minmaxRange
        return portion

    def GetPortionFromFieldOfView(self):
        minmaxRange = self.maxFov - self.minFov
        portion = (self.fieldOfView - self.minFov) / minmaxRange
        return portion

    def GetFocusYBasedOnDistance(self):
        portion = self.GetPortionFromDistance()
        focusRange = self.farFocusY - self.nearFocusY
        return self.nearFocusY + focusRange * portion

    def GetMinMaxPitchBasedOnDistance(self):
        portion = self.GetPortionFromDistance()
        minRange = self.farMinTilt - self.nearMinTilt
        maxRange = self.farMaxTilt - self.nearMaxTilt
        return (self.nearMinTilt + minRange * portion, self.nearMaxTilt + maxRange * portion)

    def Pan(self, dx, dy):
        if self.controlStyle == CONTROL_NONE:
            return
        self.xFactor -= dx * 0.0005
        self.yFactor += dy * 0.0005 * self.distance
        self.xTarget = self.xFactor
        self.yTarget = self.yFactor
        self._onFocusValue = False

    def GetPanLimitsBasedOnDistance(self):
        if self.controlStyle == CONTROL_VERTICAL:
            portion = 1.0
        else:
            portion = self.GetPortionFromDistance()
        return ((self.minPanX * portion - self.nearPan, self.maxPanX * portion + self.nearPan), (self.minPanY * portion - self.nearPan, self.maxPanY * portion + self.nearPan))

    def LimitPanning(self):
        xLimits, yLimits = self.GetPanLimitsBasedOnDistance()
        if self.controlStyle == CONTROL_BOTH:
            xAxis = geo2.Vector(self.viewMatrix.transform[0][0], self.viewMatrix.transform[1][0], self.viewMatrix.transform[2][0])
            yAxis = geo2.Vector(self.viewMatrix.transform[0][1], self.viewMatrix.transform[1][1], self.viewMatrix.transform[2][1])
        else:
            xAxis = geo2.Vector(1.0, 0.0, 0.0)
            yAxis = geo2.Vector(0.0, 1.0, 0.0)
        self.xFactor = min(xLimits[1], max(xLimits[0], self.xFactor))
        self.yFactor = min(yLimits[1], max(yLimits[0], self.yFactor))
        horizontal = xAxis * self.xFactor
        vertical = yAxis * self.yFactor
        offset = horizontal + vertical
        rotatedFocus = geo2.QuaternionTransformVector(self.avatar.rotation, self.focus)
        newPoi = rotatedFocus + offset
        self.SetPointOfInterest(newPoi)

    def AdjustYaw(self, delta):
        if self.controlStyle == CONTROL_NONE:
            return
        if self._rotateAvatar:
            delta = delta * 0.005
            yaw, pitch, roll = geo2.QuaternionRotationGetYawPitchRoll(self.avatar.rotation)
            yaw = yaw + delta
            if self.maxRotation is not None and self.minRotation is not None:
                if yaw < math.pi:
                    yaw = min(yaw, self.minRotation)
                else:
                    yaw = max(yaw, self.maxRotation)
            rotation = geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, roll)
            self.avatar.rotation = rotation
            charSvc = sm.GetService('character')
            if GetAttrs(charSvc, 'sculpting', 'highlightGhost', 'avatar'):
                charSvc.sculpting.highlightGhost.avatar.rotation = rotation
            if GetAttrs(charSvc, 'sculpting', 'bodyHighlightGhost', 'avatar'):
                charSvc.sculpting.bodyHighlightGhost.avatar.rotation = rotation
            self.Update()
        else:
            PolarCamera.AdjustYaw(self, delta * 0.005)

    def SetYaw(self, yaw, ignoreUpdate = True):
        if self.maxRotation is not None and self.minRotation is not None:
            yaw = max(self.minRotation, min(self.maxRotation, yaw))
        PolarCamera.SetYaw(self, yaw)

    def AdjustPitch(self, delta):
        if self.controlStyle == CONTROL_NONE:
            return
        self.minPitch, self.maxPitch = self.GetMinMaxPitchBasedOnDistance()
        PolarCamera.AdjustPitch(self, delta * 0.005)

    def Update(self):
        if self.updateFocus:
            right = self.GetBonePosition('fj_eyeballRight')
            left = self.GetBonePosition('fj_eyeballLeft')
            self.focus = geo2.Add(right, left)
            self.focus = geo2.Vector(*self.focus) * 0.5
        if self.moveCallback:
            self.moveCallback(self.viewMatrix)
        if self.controlStyle == CONTROL_VERTICAL:
            length = geo2.Vec2Length(geo2.Vector(self.focus[0], self.focus[2]))
            self.focus = (0.0, self.focus[1], length)
            self.updateFocus = False
        PolarCamera.Update(self)

    def SetMoveCallback(self, cb):
        self.moveCallback = cb


class CharCreationCameraHandler(CameraBehavior):

    def __init__(self):
        CameraBehavior.__init__(self)

    @staticmethod
    def GetName(self):
        return 'CharCreationCameraHandler'

    def ProcessCameraUpdate(self, camera, now, frameTime):
        if camera._transformDistance:
            startTime, startValue, toValue, duration = camera._transformDistance
            ndt = min(1.0, blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTime()) / duration)
            camera.distance = mathext.lerp(startValue, toValue, ndt)
            if ndt >= 1.0:
                camera._transformDistance = None
        if camera._transformPOI:
            startTime, startValue, toValue, duration = camera._transformPOI
            ndt = min(1.0, blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTime()) / duration)
            camera.yFactor = mathext.lerp(-startValue[1], -toValue[1], ndt)
            if ndt >= 1.0:
                camera._transformPOI = None
        if camera.controlStyle != CONTROL_NONE:
            camera.minPitch, camera.maxPitch = camera.GetMinMaxPitchBasedOnDistance()
            camera.pitch = min(camera.maxPitch, max(camera.minPitch, camera.pitch))
            camera.LimitPanning()
        camera.UpdateProjectionMatrix()
