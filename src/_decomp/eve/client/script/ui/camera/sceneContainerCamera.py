#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\sceneContainerCamera.py
from eve.client.script.ui.camera.baseCamera import Camera
import geo2
import uthread
import blue

class SceneContainerCamera(Camera):
    kFovSpeed = 7.0

    def __init__(self):
        Camera.__init__(self)
        self._aspectRatio = 1.0
        self.innerBoundRadius = (0.0, 0.0, 0.0)
        self._advancedInspectionModeOn = False
        self._currentlyInspecting = False
        self.inspectionUpdateThread = None
        self._modelCenterOffset = (0.0, 0.0, 0.0)
        self._inspectionZoomLevel = 0.0

    def UpdateViewportSize(self, width, height):
        if height:
            self._aspectRatio = float(width) / height

    def GetAspectRatio(self):
        return self._aspectRatio

    def OnActivated(self, **kwargs):
        Camera.OnActivated(self, **kwargs)
        sm.GetService('sceneManager').RegisterForCameraUpdate(self)

    def OnDeactivated(self):
        Camera.OnActivated(self)
        sm.GetService('sceneManager').UnregisterForCameraUpdate(self)

    def SetAdvancedInspectionMode(self, isOn):
        self._advancedInspectionModeOn = isOn

    def GetAdvancedInspectionModeStatus(self):
        return self._advancedInspectionModeOn

    def SetCurrentInspectionStatus(self, isOn):
        if not self._currentlyInspecting and isOn:
            self._currentlyInspecting = isOn
            self.SetFovTarget(1.0)
            self._inspectionZoomLevel = 0.0
            if self.inspectionUpdateThread is None:
                self.inspectionUpdateThread = uthread.new(self.InspectionUpdateThread)
        elif self._currentlyInspecting and not isOn:
            self.ResetRotate()
            self._rotateOffset = (0.0, 0.0)
            self._currentlyInspecting = isOn
            self.SetFovTarget(1.2)

    def GetCurrentInspectionStatus(self):
        return self._currentlyInspecting

    def SetZoom(self, proportion):
        if not self._currentlyInspecting:
            direction = self.GetLookAtDirection()
            distance = self.GetZoomDistanceByZoomProportion(proportion)
            zoomVec = geo2.Vec3Scale(direction, distance)
            self.SetEyePosition(geo2.Vec3Add(self.GetZoomToPoint(), zoomVec))

    def Zoom(self, dz):
        if not self._currentlyInspecting:
            return super(SceneContainerCamera, self).Zoom(dz)
        self._inspectionZoomLevel += dz
        self._inspectionZoomLevel = min(1.0, max(0.0, self._inspectionZoomLevel))

    def SetInnerBoundRadius(self, innerRadius):
        maxSideLength = max(self.innerBoundRadius)
        padding = (0.1 * maxSideLength, 0.1 * maxSideLength, 0.1 * maxSideLength)
        self.innerBoundRadius = geo2.Vec3Add(innerRadius, padding)

    def SetModelCenter(self, modelCenter):
        self._modelCenterOffset = modelCenter
        self.SetAtPosition(self._modelCenterOffset)

    def GetLookAtDirection(self):
        if not self._currentlyInspecting:
            return super(SceneContainerCamera, self).GetLookAtDirection()
        return geo2.Vec3Direction(self._eyePosition, self._modelCenterOffset)

    def InspectionUpdateThread(self):
        try:
            maxSideLength = max(self.innerBoundRadius)
            directionScaler = (self.innerBoundRadius[0] / maxSideLength, self.innerBoundRadius[1] / maxSideLength, self.innerBoundRadius[2] / maxSideLength)
            offsetFactor = 1 - pow(min(directionScaler), 1.3)
            finalZoomLevel = 0.3
            followSpeed = 0.0
            while True:
                if not self._currentlyInspecting:
                    numBufferUpdatesRemaining = 60.0
                    followSpeed = 0.0
                    while numBufferUpdatesRemaining > 0.0:
                        if self._currentlyInspecting:
                            followSpeed = 0.0
                            break
                        direction = self.GetLookAtDirection()
                        distance = self.maxZoom + finalZoomLevel * (self.minZoom - self.maxZoom)
                        zoomVec = geo2.Vec3Scale(direction, distance)
                        targetEyePos = geo2.Vec3Add(self.GetZoomToPoint(), zoomVec)
                        self.SetAtPosition(geo2.Vec3Lerp(self.GetAtPosition(), self._modelCenterOffset, followSpeed))
                        self.SetEyePosition(geo2.Vec3Lerp(self.GetEyePosition(), targetEyePos, followSpeed))
                        followSpeed = min(1.0, followSpeed + 0.02)
                        numBufferUpdatesRemaining -= 1.0
                        blue.synchro.Yield()

                    if not self._currentlyInspecting:
                        break
                rotationQuaternion = self.GetRotationQuat()
                direction = geo2.QuaternionTransformVector(rotationQuaternion, (0.0, 0.0, 1.0))
                adjustedDirection = (direction[0] / directionScaler[0], direction[1] / directionScaler[1], direction[2] / directionScaler[2])
                ipScale = 1.0 + self._inspectionZoomLevel
                innerPoint = tuple((ele1 * ele2 * ipScale for ele1, ele2 in zip(adjustedDirection, self.innerBoundRadius)))
                offsetAtPosition = tuple((ele1 * ele2 * ele3 * offsetFactor for ele1, ele2, ele3 in zip(adjustedDirection, self.innerBoundRadius, directionScaler)))
                targetAtPosition = geo2.Vec3Add(self._modelCenterOffset, offsetAtPosition)
                targetEyePos = geo2.Vec3Add(self._modelCenterOffset, innerPoint)
                self.SetAtPosition(geo2.Vec3Lerp(self.GetAtPosition(), targetAtPosition, followSpeed))
                self.SetEyePosition(geo2.Vec3Lerp(self.GetEyePosition(), targetEyePos, followSpeed))
                followSpeed = min(1.0, followSpeed + 0.01)
                blue.synchro.Yield()

        finally:
            self.SetAtPosition(self._modelCenterOffset)
            self.SetZoomLinear(finalZoomLevel)
            self.inspectionUpdateThread = None
