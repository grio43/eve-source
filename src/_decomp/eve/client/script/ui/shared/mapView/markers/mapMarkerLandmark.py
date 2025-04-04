#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerLandmark.py
import evetypes
from menu import MenuLabel
from carbonui.primitives.base import ScaleDpi
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Label import MarkerLabelBase
from eve.client.script.ui.shared.maps.maputils import GetNameFromMapCache

class MarkerLabelLandmark(MarkerLabelBase):
    fontPath = 'res:/UI/Fonts/EveSansNeue-Italic.otf'
    letterSpace = 2
    distanceFadeAlphaNearFar = (mapViewConst.MAX_MARKER_DISTANCE * 0.05, mapViewConst.MAX_MARKER_DISTANCE * 0.1)

    def __init__(self, *args, **kwds):
        MarkerLabelBase.__init__(self, *args, **kwds)
        self.landmarkData = kwds['landmarkData']
        self.typeID = const.typeMapLandmark
        self.itemID = self.markerID

    def Load(self):
        MarkerLabelBase.Load(self)
        self.projectBracket.offsetY = -ScaleDpi(self.markerContainer.height + 20)

    def GetLabelText(self):
        return GetNameFromMapCache(self.landmarkData.landmarkNameID, 'landmark')

    def GetMenu(self):
        return [(MenuLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, (const.typeMapLandmark, self.markerID))]

    def OnClick(self, *args, **kwds):
        sm.GetService('info').ShowInfo(const.typeMapLandmark, self.markerID)
