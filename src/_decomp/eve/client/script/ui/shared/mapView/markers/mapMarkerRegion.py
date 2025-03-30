#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerRegion.py
from carbonui.primitives.base import ScaleDpi
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Label import MarkerLabelBase

class MarkerLabelRegion(MarkerLabelBase):
    fontColor = (1.0, 1.0, 1.0, 0.85)
    distanceFadeAlphaNearFar = (mapViewConst.MAX_MARKER_DISTANCE * 0.015, mapViewConst.MAX_MARKER_DISTANCE * 2)
    fontSize = 10
    letterSpace = 3

    def __init__(self, *args, **kwds):
        MarkerLabelBase.__init__(self, *args, **kwds)
        self.typeID = const.typeRegion
        self.itemID = self.markerID

    def GetLabelText(self):
        return cfg.evelocations.Get(self.markerID).name.upper()

    def GetDragText(self):
        return cfg.evelocations.Get(self.markerID).name

    def Load(self):
        MarkerLabelBase.Load(self)
        self.projectBracket.offsetY = -ScaleDpi(self.markerContainer.height + 20)

    def UpdateActiveAndHilightState(self):
        if self.hilightState or self.activeState:
            self.projectBracket.maxDispRange = 1e+32
        elif self.distanceFadeAlphaNearFar:
            self.projectBracket.maxDispRange = self.distanceFadeAlphaNearFar[1]

    def GetMarkerOpacity(self, bracketCameraDistance, cameraZoomDistance):
        if self.IsActive() or self.IsHilighted():
            return mapViewConst.OPACITY_MARKER_SELECTED
        return MarkerLabelBase.GetMarkerOpacity(self, bracketCameraDistance, cameraZoomDistance)
