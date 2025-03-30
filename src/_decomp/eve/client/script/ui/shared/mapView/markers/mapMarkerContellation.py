#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerContellation.py
from carbonui import uiconst
from carbonui.primitives.base import ReverseScaleDpi, ScaleDpi
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase import MarkerUniverseBased
import inventorycommon.const as invConst
from eve.common.script.util.eveFormat import FmtSystemSecStatus

class MarkerLabelConstellation(MarkerUniverseBased):
    distanceFadeAlphaNearFar = (mapViewConst.MAX_MARKER_DISTANCE * 0.07, mapViewConst.MAX_MARKER_DISTANCE * 0.3)

    def __init__(self, *args, **kwds):
        MarkerUniverseBased.__init__(self, *args, **kwds)
        self.typeID = invConst.typeConstellation
        self.itemID = self.markerID
        self.label = None

    def Load(self):
        MarkerUniverseBased.Load(self)
        self.projectBracket.offsetY = -ScaleDpi(self.markerContainer.height + 8)
        self.label = Label(parent=self.markerContainer, align=uiconst.CENTER, opacity=0.95)
        Frame(bgParent=self.markerContainer, opacity=0.3)
        Fill(bgParent=self.markerContainer, color=(0, 0, 0, 0.5))
        self.UpdateLabelText()

    def UpdateLabelText(self):
        if not self.label or not self.markerContainer:
            return
        self.label.SetText(self.GetLabelText())
        width, height = self.label.GetAbsoluteSize()
        self.markerContainer.pos = (0,
         0,
         ReverseScaleDpi(width + 6),
         ReverseScaleDpi(height))

    def UpdateActiveAndHilightState(self):
        if self.hilightState or self.activeState:
            self.projectBracket.maxDispRange = 1e+32
        elif self.distanceFadeAlphaNearFar:
            self.projectBracket.maxDispRange = self.distanceFadeAlphaNearFar[1]
        self.UpdateLabelText()

    def GetMarkerOpacity(self, bracketCameraDistance, cameraZoomDistance):
        if self.IsSelected() or self.IsHilighted():
            return mapViewConst.OPACITY_MARKER_SELECTED
        if self.IsActive():
            if self.markerHandler.IsRegionSelected():
                nearFadeDist, farFadeDist = self._distanceFadeAlphaNearFar
                return self.GetMarkerBaseOpacity(bracketCameraDistance, None, farFadeDist)
            nearFadeDist, farFadeDist = self._distanceFadeAlphaNearFar
            baseOpacity = self.GetMarkerBaseOpacity(bracketCameraDistance, nearFadeDist, farFadeDist)
            if baseOpacity:
                nearFactor = self.GetNearFadeFactor(bracketCameraDistance, cameraZoomDistance)
                return baseOpacity * nearFactor

    def _HideRenderObject(self):
        self.DestroyRenderObject()

    def GetLabelText(self):
        constName = cfg.evelocations.Get(self.markerID).name
        if self.IsSelected():
            return constName
        else:
            constData = mapViewData.GetKnownConstellation(self.markerID)
            security = sum([ sm.GetService('map').GetSystemSecurityValue(solarsystemID) for solarsystemID in constData.solarSystemIDs ]) / len(constData.solarSystemIDs)
            security, color = FmtSystemSecStatus(security, getColor=True)
            return '%s <color=%s>%s</color>' % (constName, Color.RGBtoHex(color[0], color[1], color[2]), security)

    def GetDragText(self):
        return cfg.evelocations.Get(self.markerID).name
