#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerCelestial.py
from carbon.common.script.util.format import FmtDist
from eve.client.script.parklife import states
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
from eve.client.script.ui.shared.mapView.mapViewConst import VIEWMODE_MARKERS_OVERLAP_SORT_ORDER
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Icon import MarkerIconBase
from eve.client.script.ui.shared.mapView.markers.mapMarkerSpaceObjectRadialMenu import MapMarkerSpaceObjectRadialMenu
from eve.client.script.ui.util.uix import EditStationName, GetBallparkRecord
import evetypes
from eveservices.menu import GetMenuService

class MarkerSpaceObject(MarkerIconBase):
    distanceFadeAlphaNearFar = (0.0, mapViewConst.MAX_MARKER_DISTANCE * 0.1)
    backgroundTexturePath = None
    __notifyevents__ = ['OnStateChange']

    def __init__(self, *args, **kwds):
        sm.RegisterNotify(self)
        celestialData = kwds['celestialData']
        bracketIconPath = sm.GetService('bracket').GetBracketIcon(celestialData.typeID)
        if bracketIconPath:
            kwds['texturePath'] = bracketIconPath
        MarkerIconBase.__init__(self, *args, **kwds)
        self.projectBracket.offsetY = 0
        self.celestialData = celestialData
        self.typeID = self.celestialData.typeID
        self.itemID = self.celestialData.itemID

    def Close(self, *args):
        MarkerIconBase.Close(self, *args)
        sm.UnregisterNotify(self)

    def OnStateChange(self, itemID, flag, state, *args):
        if flag == states.mouseOver and itemID == self.itemID:
            self.SetHilightState(state)

    def GetMenu(self):
        return GetMenuService().CelestialMenu(self.celestialData.itemID, typeID=self.celestialData.typeID)

    def GetOverlapSortValue(self, reset = False):
        if self.overlapSortValue and not reset:
            return self.overlapSortValue
        displayText = (self.GetDisplayText() or '').lower()
        groupID = self.celestialData.groupID
        if groupID in VIEWMODE_MARKERS_OVERLAP_SORT_ORDER:
            idx = VIEWMODE_MARKERS_OVERLAP_SORT_ORDER.index(groupID)
            if self.isDscanHiliteShown:
                idx -= len(VIEWMODE_MARKERS_OVERLAP_SORT_ORDER)
            self.overlapSortValue = (self.markerID[0], idx, displayText)
        else:
            self.overlapSortValue = (self.markerID[0], len(VIEWMODE_MARKERS_OVERLAP_SORT_ORDER) + self.celestialData.groupID, displayText)
        return self.overlapSortValue

    def GetDisplayText(self):
        displayName = ''
        locationName = cfg.evelocations.Get(self.celestialData.itemID).name
        if locationName:
            displayName = locationName
            if evetypes.GetGroupID(self.typeID) == const.groupStation:
                displayName = EditStationName(displayName, usename=1)
        elif self.celestialData.typeID:
            displayName = evetypes.GetName(self.celestialData.typeID)
        return displayName

    def GetLabelText(self):
        displayName = self.GetDisplayText()
        distance = self.GetDistance()
        if distance is not None:
            displayName += ' ' + FmtDist(distance)
        return displayName

    def OnClick(self, *args):
        doDScan = self.CheckDirectionalScanItem()
        if not doDScan:
            sm.GetService('stateSvc').SetState(self.itemID, states.selected, 1)
            MarkerIconBase.OnClick(self, *args)

    def OnMouseDown(self, *args):
        if not GetBallparkRecord(self.itemID):
            return
        sm.GetService('radialmenu').TryExpandActionMenu(self.itemID, self.markerContainer, radialMenuClass=MapMarkerSpaceObjectRadialMenu, markerObject=self)

    def OnMouseEnter(self, *args):
        sm.GetService('stateSvc').SetState(self.itemID, states.mouseOver, 1)
        MarkerIconBase.OnMouseEnter(self, *args)

    def OnMouseExit(self, *args):
        sm.GetService('stateSvc').SetState(self.itemID, states.mouseOver, 0)
        MarkerIconBase.OnMouseExit(self, *args)
