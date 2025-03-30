#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\mapCamera.py
import math
import evecamera
from eve.client.script.ui.camera.baseCamera import Camera
from eve.client.script.ui.camera.cameraUtil import GetDurationByDistance
import geo2
from eve.client.script.ui.shared.mapView import mapViewConst
from logmodule import LogException

class MapCamera(Camera):
    cameraID = evecamera.CAM_MAP
    maxZoom = mapViewConst.MIN_CAMERA_DISTANCE
    minZoom = mapViewConst.MAX_CAMERA_DISTANCE
    default_eyePosition = (0, 10000, -50)
    kOrbitSpeed = 10.0
    kOrbitStopAngle = 0.001
    kZoomStopDist = 0.001
    kPanStopDist = 0.01
    kMaxPitch = math.pi / 2
    kMinPitch = 0.01

    def __init__(self):
        Camera.__init__(self)
        self.viewport = None
        self._aspectRatio = 1.0
        self.callback = None
        self.sceneCursor = (0, 0, 0)
        self._isAttached = True
        self._centerOffsetEnabled = False

    def Update(self):
        Camera.Update(self)
        if self.callback:
            try:
                self.callback()
            except Exception as e:
                LogException(e)

        self._EnforceMaximumDistance()

    def _EnforceMaximumDistance(self):
        dist = geo2.Vec3Length(self.eyePosition)
        maxDist = 2 * self.minZoom
        if dist > maxDist:
            direction = geo2.Vec3Normalize(self.eyePosition)
            newEye = geo2.Vec3Scale(direction, maxDist)
            diff = geo2.Vec3Subtract(self.eyePosition, newEye)
            self.SetEyePosition(newEye)
            self.SetAtPosition(geo2.Vec3Subtract(self._atPosition, diff))

    def UpdateViewportSize(self, width, height):
        self._aspectRatio = float(width) / height

    def GetAspectRatio(self):
        return self._aspectRatio

    def GetViewport(self):
        return self.viewport

    def SetViewport(self, viewport):
        self.viewport = viewport

    def SetUpdateCallback(self, callback):
        self.callback = callback

    def LookAtMarker(self, markerObject, duration = None, animate = True, zoomDistance = None):
        atPos = markerObject.GetDisplayPosition()
        if atPos:
            self.LookAtPoint(atPos, duration, animate, zoomDistance)

    def LookAtPoint(self, atPos, duration = None, animate = True, zoomDistance = None):
        self.StopUpdateThreads()
        if not self.IsAttached():
            self._ResetAtPosition(atPos)
        eyePos = self.GetLookAtEyePosition(atPos, zoomDistance)
        if animate:
            if not duration:
                duration = GetDurationByDistance(self.atPosition, atPos, 0.3, 0.6, 500)
            self.TransitTo(atPos, eyePos, duration=duration)
        else:
            self.atPosition = atPos
            self.eyePosition = eyePos
        self._isAttached = True

    def GetLookAtEyePosition(self, atPos, zoomDistance):
        if zoomDistance:
            diff = geo2.Vec3Scale(geo2.Vec3Normalize(self.GetLookAtDirection()), zoomDistance)
            return geo2.Vec3Add(atPos, diff)
        else:
            diff = geo2.Vec3Subtract(atPos, self.atPosition)
            return geo2.Vec3Add(self.eyePosition, diff)

    def _ResetAtPosition(self, atPos):
        distance = -geo2.Vec3Distance(self.eyePosition, atPos)
        lookVec = geo2.Vec3Scale(self.GetLookAtDirection(), distance)
        self.SetAtPosition(geo2.Vec3Add(self._eyePosition, lookVec))

    def Pan(self, dx = 0, dy = 0, dz = 0):
        if self.IsAttached():
            self._SetDetached()
        k = self.GetPanSpeed()
        Camera.Pan(self, k * dx, k * dy, k * dz)

    def PanAxis(self, axis, amount):
        k = self.GetPanSpeed()
        Camera.PanAxis(self, axis, k * amount)
        if self.IsAttached():
            self._SetDetached()

    def _SetDetached(self):
        self.StopUpdateThreads()
        self._isAttached = False
        self.sceneCursor = self.GetAtPosition()

    def GetZoomDistanceForMap(self):
        if self.IsAttached():
            return self.GetZoomDistance()
        else:
            return self.GetDistanceToCursor()

    def GetDistanceToCursor(self):
        return geo2.Vec3Distance(self.eyePosition, self.sceneCursor)

    def GetPanSpeed(self):
        return 0.0001 + 0.001 * self.GetDistanceToCursor() ** 0.9

    def IsAttached(self):
        return self._isAttached

    def EnableCenterOffset(self):
        self._centerOffsetEnabled = True

    def DisableCenterOffset(self):
        self._centerOffsetEnabled = False

    def GetCenterOffset(self):
        if self._centerOffsetEnabled:
            return self.centerOffset
        else:
            return 0.0

    def Zoom(self, dz):
        if self.IsInTransit():
            return
        Camera.Zoom(self, dz)

    def PanImmediate(self, dx, dy, dz):
        k = self.GetPanSpeed()
        pan = geo2.Add(geo2.Add(geo2.Scale(self.GetXAxis(), dx * k), geo2.Scale(self.GetYAxis(), dy * k)), geo2.Scale(self.GetZAxis(), dz * k))
        self.eyePosition = geo2.Add(self._eyePosition, pan)
        self.atPosition = geo2.Add(self._atPosition, pan)

    def OrbitImmediate(self, yaw, pitch):
        self.pitch = self.pitch + pitch
        self.yaw = self.yaw + yaw
        self.StopOrbitUpdate()
