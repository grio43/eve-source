#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\camera\debugCamera.py
import geo2
import math
import blue
from carbonui.camera.polarCamera import PolarCamera
from eve.common.lib import appConst as const

class DebugCamera(PolarCamera):

    def __init__(self):
        self.updatingDebugCamera = True
        self.showNormalCamera = False
        self.translationVector = [0.0, 0.0, 0.0]
        normCam = self._GetNonDebugCamera()
        self.lastCamPos = normCam.GetPosition() if normCam else (0.0, 0.0, 0.0)
        self.debugRenderClient = sm.GetService('debugRenderClient')
        self.debugRenderClient.SetDebugRendering(True)
        PolarCamera.__init__(self)

    def IsUpdatingDebugCamera(self):
        return self.updatingDebugCamera

    def ToggleDebugCameraUpdate(self):
        self.updatingDebugCamera = not self.updatingDebugCamera

    def IsShowingNormalCamera(self):
        return self.showNormalCamera

    def SetShowNormalCamera(self, showCamera):
        self.showNormalCamera = showCamera
        self.lastCamPos = None
        self.debugRenderClient.ClearAllShapes()

    def AdjustDebugCamYaw(self, delta, maxRotate = None, ignoreUpdate = True):
        if self.IsUpdatingDebugCamera():
            PolarCamera.AdjustYaw(self, delta, maxRotate, ignoreUpdate)

    def AdjustDebugCamPitch(self, delta):
        if self.IsUpdatingDebugCamera():
            PolarCamera.AdjustPitch(self, delta)

    def IsControlEnabled(self):
        return not self.IsUpdatingDebugCamera()

    def GetTranslationVector(self):
        return self.translationVector

    def SetTranslationVector(self, translationVector):
        self.translationVector = translationVector

    def _GetNonDebugCamera(self):
        return None

    def Update(self):
        normalCamera = self._GetNonDebugCamera()
        if not self.IsUpdatingDebugCamera() and normalCamera:
            if normalCamera:
                normalCamera.Update()
        if self.IsShowingNormalCamera() and normalCamera:
            camPos = normalCamera.GetPosition()
            poi = normalCamera.GetPointOfInterest()
            vec = geo2.Vec3Subtract(poi, camPos)
            vec = geo2.Vec3Normalize(vec)
            vec = geo2.Vec3Scale(vec, 0.5)
            self.debugRenderClient.RenderCone(camPos, geo2.Vec3Add(camPos, vec), 0.25, 4278190335L, time=1)
            if self.lastCamPos is not None and camPos != self.lastCamPos:
                self.debugRenderClient.RenderRay(self.lastCamPos, camPos, 4278190335L, 4278255360L, time=1000, pulse=True)
            self.lastCamPos = camPos
        if self.translationVector != [0.0, 0.0, 0.0]:
            now = blue.os.GetWallclockTime()
            frameTime = float(now - self.lastUpdateTime) / const.SEC
            poi = PolarCamera.GetPointOfInterest(self)
            rotMatrix = geo2.MatrixRotationYawPitchRoll(math.pi / 2.0 - self.yaw, math.pi / 2.0 - self.pitch, 0.0)
            scaledVector = geo2.Vec3Scale(self.translationVector, frameTime)
            relativeVector = geo2.Vec3TransformCoord(scaledVector, rotMatrix)
            newPos = geo2.Vec3Add(poi, relativeVector)
            PolarCamera.SetPointOfInterest(self, newPos)
        PolarCamera.Update(self)

    def SetRotationWithYaw(self, yawValue):
        if not self.IsUpdatingDebugCamera():
            normalCamera = self._GetNonDebugCamera()
            if normalCamera:
                normalCamera.SetRotationWithYaw(yawValue)

    def AdjustZoomFactorByZoom(self, delta):
        if not self.IsUpdatingDebugCamera():
            normalCamera = self._GetNonDebugCamera()
            if normalCamera:
                normalCamera.AdjustZoomFactorByZoom(delta)

    def SetPointOfInterest(self, poi):
        if self.IsUpdatingDebugCamera():
            PolarCamera.SetPointOfInterest(self, poi)
        else:
            normalCamera = self._GetNonDebugCamera()
            if normalCamera:
                normalCamera.SetPointOfInterest(poi)

    def AdjustPitch(self, delta):
        if not self.IsUpdatingDebugCamera():
            normalCamera = self._GetNonDebugCamera()
            if normalCamera:
                normalCamera.AdjustPitch(delta)

    def SetPitch(self, value):
        if self.IsUpdatingDebugCamera():
            PolarCamera.SetPitch(self, value)
        else:
            normalCamera = self._GetNonDebugCamera()
            if normalCamera:
                normalCamera.SetPitch(value)

    def SetPosition(self, position):
        if self.IsUpdatingDebugCamera():
            PolarCamera.SetPosition(self, position)
        else:
            normalCamera = self._GetNonDebugCamera()
            if normalCamera:
                normalCamera.SetPosition(position)

    def SetYawPitchDist(self, yaw, pitch, dist):
        if self.IsUpdatingDebugCamera():
            PolarCamera.SetYawPitchDist(self, yaw, pitch, dist)
        else:
            normalCamera = self._GetNonDebugCamera()
            if normalCamera:
                normalCamera.SetYawPitchDist(yaw, pitch, dist)

    def SetYaw(self, value, ignoreUpdate = True):
        if self.IsUpdatingDebugCamera():
            PolarCamera.SetYaw(self, value, ignoreUpdate)
        else:
            normalCamera = self._GetNonDebugCamera()
            if normalCamera:
                normalCamera.SetYaw(value, ignoreUpdate)

    def AdjustYaw(self, delta, maxRotate = None, ignoreUpdate = True):
        if not self.IsUpdatingDebugCamera():
            normalCamera = self._GetNonDebugCamera()
            if normalCamera:
                normalCamera.AdjustYaw(delta, maxRotate, ignoreUpdate)

    def AdjustZoom(self, delta):
        if self.IsUpdatingDebugCamera():
            PolarCamera.AdjustZoom(self, delta)
        else:
            normalCamera = self._GetNonDebugCamera()
            if normalCamera:
                normalCamera.AdjustZoom(delta)

    def SetZoom(self, zoom):
        if self.IsUpdatingDebugCamera():
            PolarCamera.SetZoom(self, zoom)
        else:
            normalCamera = self._GetNonDebugCamera()
            if normalCamera:
                normalCamera.SetZoom(zoom)

    def SmoothMove(self, targetPosition, targetRotation, targetTilt, targetDist, durationMS, callbackOnEnd = None):
        if self.IsUpdatingDebugCamera():
            PolarCamera.SmoothMove(self, targetPosition, targetRotation, targetTilt, targetDist, durationMS, callbackOnEnd)
        else:
            normalCamera = self._GetNonDebugCamera()
            if normalCamera:
                normalCamera.SmoothMove(targetPosition, targetRotation, targetTilt, targetDist, durationMS, callbackOnEnd)

    def UpdateSmoothMove(self, *args):
        if self.IsUpdatingDebugCamera():
            PolarCamera.UpdateSmoothMove(self, *args)
        else:
            normalCamera = self._GetNonDebugCamera()
            if normalCamera:
                normalCamera.UpdateSmoothMove(*args)

    def GetPosition(self):
        normalCamera = self._GetNonDebugCamera()
        return normalCamera.GetPosition()

    def GetYaw(self):
        normalCamera = self._GetNonDebugCamera()
        return normalCamera.GetYaw()

    def GetPitch(self):
        normalCamera = self._GetNonDebugCamera()
        return normalCamera.GetPitch()

    def GetYawPitch(self):
        normalCamera = self._GetNonDebugCamera()
        return normalCamera.GetYawPitch()
