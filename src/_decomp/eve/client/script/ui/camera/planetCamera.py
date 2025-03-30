#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\planetCamera.py
import math
import geo2
from carbonui.uianimations import animations
from eve.client.script.ui.camera.baseCamera import Camera
import evecamera
OFFSET = 0.05
K_FOVOFFSET = 0.25
K_YOFFSET = 500
K_LOOKATDIROFFSET = 850
K_ORBITTO_PITCHOFFSET = 0.12
K_ZOOMDIFF_ANIMDURATION = 1.4
ANIM_DURATION = 0.5

class PlanetCamera(Camera):
    cameraID = evecamera.CAM_PLANET
    maxZoom = 1100.0
    minZoom = 4000.0
    kMinPitch = 0.1
    kMaxPitch = math.pi - kMinPitch
    kZoomSpeed = 5.0
    name = 'PlanetCamera'

    def __init__(self):
        Camera.__init__(self)
        self.callback = None

    def SetCallback(self, callback):
        self.callback = callback

    def Update(self):
        atOffset = self._GetAtOffset()
        lookAtOffset = atOffset
        self._AddToAtOffset(lookAtOffset)
        self.fovOffset = K_FOVOFFSET * (1.0 - self.zoomLinear)
        if self.callback:
            self.callback()
        Camera.Update(self)

    def _GetAtOffset(self):
        eaquatorDistProp = self.GetEquatorDistanceProp()
        zoom = self.GetZoomProportionLinear()
        zoomProp = (1.0 - zoom) ** 7
        offsetDir = geo2.Vec3Normalize((-self._eyePosition[0], eaquatorDistProp * K_YOFFSET, -self._eyePosition[2]))
        offsetAmount = K_LOOKATDIROFFSET * eaquatorDistProp * zoomProp
        offsetDir = geo2.Vec3Scale(offsetDir, math.fabs(offsetAmount))
        return offsetDir

    def GetEquatorDistanceProp(self):
        equatorDistProp = self.GetEquatorDistancePropLinear(self.pitch)
        equatorDistProp = math.copysign(math.fabs(equatorDistProp) ** 0.35, equatorDistProp)
        return equatorDistProp

    def GetOrbitPoint(self):
        return (0, 0, 0)

    def GetZoomToPoint(self):
        return (0, 0, 0)

    def GetLookAtDirectionWithOffset(self):
        return self.GetLookAtDirection()

    def OrbitToSurfacePoint(self, surfacePoint, newZoom = None, initStartPos = False):
        self.StopUpdateThreads()
        yaw = self._GetYaw(surfacePoint)
        pitch = self._GetPitch(surfacePoint)
        if initStartPos:
            yaw0, pitch0 = self._InitStartPosition(yaw, pitch)
            self.yaw = yaw0
            self.pitch = pitch0
            self.zoomLinear = newZoom * 1.5
            duration = 1.2
        else:
            yaw0, pitch0, zoomLinear0 = self.yaw, self.pitch, self.zoomLinear
            duration = self.GetAnimDuration(yaw, pitch, newZoom)
        animations.MorphScalar(self, 'yaw', yaw0, yaw, duration=duration)
        animations.MorphScalar(self, 'pitch', pitch0, pitch, duration=duration)
        animations.MorphScalar(self, 'zoomLinear', self.zoomLinear, newZoom, duration=duration)

    def Orbit(self, dx = 0, dy = 0):
        Camera.Orbit(self, dx, dy)
        self.StopAnimations()

    def Zoom(self, dz):
        Camera.Zoom(self, dz)
        self.StopAnimations()

    def _InitStartPosition(self, yaw, pitch):
        yaw += OFFSET
        if self.pitch > math.pi / 2:
            pitch -= OFFSET
        else:
            pitch += OFFSET
        return (yaw, pitch)

    def _GetPitch(self, surfacePoint):
        pitch = surfacePoint.phi
        equatorDistProp = self.GetEquatorDistancePropLinear(pitch)
        pitch += K_ORBITTO_PITCHOFFSET * equatorDistProp
        pitch = max(self.kMinPitch, min(pitch, self.kMaxPitch))
        return pitch

    def GetEquatorDistancePropLinear(self, pitch):
        return 1.0 - pitch / (math.pi / 2)

    def _GetYaw(self, surfacePoint):
        yaw = -surfacePoint.theta - math.pi / 2.0
        if math.fabs(self.yaw - yaw) > math.pi:
            if self.yaw > yaw:
                yaw += 2 * math.pi
            else:
                yaw -= 2 * math.pi
        return yaw

    def GetAnimDuration(self, yaw, pitch, zoom):
        yawDiff = math.fabs(self.yaw - yaw) * (1.0 - self.GetEquatorDistancePropLinear(pitch))
        pitchDiff = math.fabs(self.pitch - pitch)
        zoomDiff = K_ZOOMDIFF_ANIMDURATION * math.fabs(self.zoomLinear - zoom)
        diff = max(yawDiff, pitchDiff, zoomDiff)
        return ANIM_DURATION * (1.2 + diff)
