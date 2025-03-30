#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\miniMapCamera.py
import math
import evecamera
from carbonui.uianimations import animations
from eve.client.script.ui.camera.mapCamera import MapCamera

class MiniMapCamera(MapCamera):
    cameraID = evecamera.CAM_MINIMAP
    minZoom = 80000
    maxZoom = 5.0
    animationSpeed = 0.5

    def __init__(self):
        MapCamera.__init__(self)
        self.pitch = 0.3 * math.pi
        self._centerOffsetPanels = 0
        self._verticalOffsetPanels = 0

    @property
    def verticalOffsetPanels(self):
        return self._verticalOffsetPanels

    @verticalOffsetPanels.setter
    def verticalOffsetPanels(self, value):
        self._verticalOffsetPanels = value

    @property
    def centerOffsetPanels(self):
        return self._centerOffsetPanels

    @centerOffsetPanels.setter
    def centerOffsetPanels(self, value):
        self._centerOffsetPanels = value

    def SetCenterOffsetPanels(self, value):
        animations.MorphScalar(obj=self, attrName='centerOffsetPanels', startVal=self.centerOffsetPanels, endVal=value, duration=self.animationSpeed, callback=lambda : setattr(self, 'centerOffsetPanels', value))

    def SetVerticalOffsetPanels(self, value):
        animations.MorphScalar(obj=self, attrName='verticalOffsetPanels', startVal=self.verticalOffsetPanels, endVal=value, duration=self.animationSpeed, callback=lambda : setattr(self, 'verticalOffsetPanels', value))

    def GetCenterOffset(self):
        offset = self.centerOffsetPanels
        baseOffset = MapCamera.GetCenterOffset(self)
        if baseOffset:
            offset += baseOffset
        return offset

    def GetVerticalOffset(self):
        offset = self.verticalOffsetPanels
        baseOffset = MapCamera.GetVerticalOffset(self)
        if baseOffset:
            offset += baseOffset
        return offset
