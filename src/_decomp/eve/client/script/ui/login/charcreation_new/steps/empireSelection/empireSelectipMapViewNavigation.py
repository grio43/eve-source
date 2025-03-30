#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\empireSelection\empireSelectipMapViewNavigation.py
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectionMapCameraController import EmpireSelectionMapCameraController
from eve.client.script.ui.shared.mapView.mapViewNavigation import MapViewNavigation

class EmpireSelectionMapViewNavigation(MapViewNavigation):

    def GetMenu(self):
        pass

    def OnDblClick(self, *args):
        pass

    def ConstructCameraController(self):
        self.cameraController = EmpireSelectionMapCameraController(self.mapView.mapViewID, self.mapView.cameraID)
