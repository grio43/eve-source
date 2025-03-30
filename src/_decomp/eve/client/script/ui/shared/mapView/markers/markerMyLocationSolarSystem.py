#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\markerMyLocationSolarSystem.py
from eve.client.script.ui.inflight.scannerFiles.directionalScanUtil import GetActiveScanMode, SCANMODE_CAMERA
from eve.client.script.ui.shared.mapView.markers.mapMarkerMyLocation import MarkerMyLocation

class MarkerMyLocationSolarSystem(MarkerMyLocation):

    def OnMapMarkerUpdated(self, projectBracket):
        self.displayStateOverride = GetActiveScanMode() != SCANMODE_CAMERA
        MarkerMyLocation.OnMapMarkerUpdated(self, projectBracket)

    def CheckConstructCircles(self):
        pass
