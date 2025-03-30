#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\mapViewWorld.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.mapView.colorModes.colorModeInfoBase import ColorModeInfoBase
from eve.client.script.ui.shared.mapView.mapCompass import MapCompass
from eve.client.script.ui.shared.mapView.mapView import MapView
from eve.client.script.ui.shared.mapView.selectedInfoCont import SelectedInfoCont

class MapViewWorld(MapView):

    def ApplyAttributes(self, attributes):
        super(MapViewWorld, self).ApplyAttributes(attributes)
        sm.ScatterEvent('OnClientEvent_OpenMap')

    def ConstructOverlayTools(self):
        self.overlayTools = Container(parent=self, name='overlayTools')
        self.colorModeInfoPanel = ColorModeInfoBase(parent=self.overlayTools, mapView=self)
        self.selectedInfoCont = SelectedInfoCont(parent=self.overlayTools, align=uiconst.CENTERTOP, setActiveCallback=self.OnSelectedInfoLocationClicked)
        self.mapCompass = MapCompass(parent=self.overlayTools, align=uiconst.BOTTOMRIGHT, pos=(0, 0, 65, 65), onClickCallback=self.OnMapCompassClicked)

    def UpdateColorModeInfoPanel(self, filter):
        self.colorModeInfoPanel.LoadColorModeInfo(filter)

    def SetActiveItemID(self, itemID, localID = None, zoomToItem = False, animate = True, *args, **kwds):
        MapView.SetActiveItemID(self, itemID, localID, zoomToItem, animate, *args, **kwds)
        self.selectedInfoCont.Update(self.activeSolarSystemID, self.activeConstellationID, self.activeRegionID)

    def OnWindowResize(self, width, height):
        if width > 600 or self.isFullScreen:
            self.selectedInfoCont.SetShouldShow(True)
        else:
            self.selectedInfoCont.SetShouldShow(False)
        self.selectedInfoCont.UpdateDisplayState()
        MapView.OnWindowResize(self, width, height)

    def OnCameraUpdate(self):
        MapView.OnCameraUpdate(self)
        if self.camera:
            self.mapCompass.Update(self.camera.yaw)
