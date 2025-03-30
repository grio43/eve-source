#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\solarSystemMapCamera.py
import math
import evecamera
from carbonui.uianimations import animations
from eve.client.script.ui.camera.mapCamera import MapCamera
from eve.client.script.ui.shared.mapView import mapViewConst

class SolarSystemMapCamera(MapCamera):
    cameraID = evecamera.CAM_SOLARSYSTEMMAP
    maxZoom = mapViewConst.MIN_CAMERA_DISTANCE
    minZoom = mapViewConst.MAX_CAMERA_DISTANCE
    kMaxPitch = math.pi - 0.05
    default_eyePosition = (0, 10000, -50)

    def __init__(self):
        MapCamera.__init__(self)
        self.atPositionMethod = None
        self.centerOffsetPanels = 0.0

    def SetCenterOffsetPanels(self, value):
        self.centerOffsetPanels = value

    def GetCenterOffset(self):
        offset = self.centerOffsetPanels
        baseOffset = MapCamera.GetCenterOffset(self)
        if baseOffset:
            offset += baseOffset
        return offset

    def TransitTo(self, atPosition = None, eyePosition = None, duration = 1.0, smoothing = 0.1, numPoints = 1000, timeOffset = 0.0):
        animations.MorphVector3(self, 'eyePosition', self.eyePosition, eyePosition, duration=duration, timeOffset=timeOffset)
        animations.MorphVector3(self, 'atPosition', self.atPosition, atPosition, duration=duration, timeOffset=timeOffset)
