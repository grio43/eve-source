#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\mapViewNavigation.py
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from eve.client.script.ui.camera.mapCameraController import MapCameraController
from carbonui.uicore import uicore
from menu import MenuLabel
import evespacemouse
spaceMouseSupportEnabled = False

class MapViewNavigation(Container):
    default_cursor = uiconst.UICURSOR_DEFAULT
    lastPickInfo = None
    isTabStop = True
    pickInfo = None
    pickPosition = None
    cameraUpdateTimer = None
    rightMouseDownPosition = None

    def Close(self, *args):
        Container.Close(self, *args)
        self.mapView = None
        self.pickTimer = None
        self.cameraUpdateTimer = None
        evespacemouse.StopListening(self._OnSpaceMousePosition, None)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.mapView = attributes.mapView
        self.pickTimer = AutoTimer(20, self.CheckPick)
        self.mouseDownPick = None
        self.ConstructCameraController()
        if spaceMouseSupportEnabled:
            evespacemouse.StartListening(None, self._OnSpaceMousePosition, None, 100)

    def _OnSpaceMousePosition(self, dt, translation, rotation):
        mo = uicore.uilib.mouseOver
        parent = self.parent
        while mo != parent:
            if not mo.parent or mo is uicore.uilib.desktop:
                break
            mo = mo.parent

        if mo != parent:
            return
        spaceMouseScale = 1000.0 / 16.0
        camera = self.cameraController.GetCamera()
        if rotation[0] or rotation[1]:
            orbitScale = 0.012 * spaceMouseScale * dt
            camera.OrbitImmediate(rotation[1] * orbitScale, rotation[0] * orbitScale)
        if translation[0] or translation[1] or translation[2]:
            if camera.IsAttached():
                camera.Zoom(-translation[2] * 0.01 * spaceMouseScale * dt)
            else:
                panScale = 30 * spaceMouseScale * dt
                camera.PanImmediate(translation[0] * panScale, translation[1] * panScale, -translation[2] * panScale)
        raise evespacemouse.StopPropagation()

    def ConstructCameraController(self):
        self.cameraController = MapCameraController(self.mapView.mapViewID, self.mapView.cameraID)

    def CheckPick(self):
        if uicore.uilib.mouseOver is not self or uicore.uilib.leftbtn or uicore.uilib.rightbtn:
            return
        mx, my = uicore.uilib.x, uicore.uilib.y
        if self.pickPosition:
            dX = abs(mx - self.pickPosition[0])
            dY = abs(my - self.pickPosition[1])
            picked = self.pickPosition[-1]
            if dX == 0 and dY == 0:
                if not picked:
                    self.PickScene(mx, my)
                    self.pickPosition = (mx, my, True)
                return
        self.pickPosition = (mx, my, False)

    def PickScene(self, mouseX, mouseY):
        pickInfo = self.mapView.GetPickObjects(mouseX, mouseY, getMarkers=False)
        if pickInfo:
            self.mapView.OnMarkerHovered(pickInfo[0])
        else:
            self.mapView.OnMarkerHovered(None)

    def MapMarkerPickingOverride(self, *args, **kwds):
        return False

    def PickRegionID(self):
        return None

    def OnDblClick(self, *args):
        if self.destroyed:
            return
        pickInfo = self.GetPickInfo()
        if pickInfo:
            self.mapView.SetSelectedMarker(pickInfo[0][1])
        else:
            self.mapView.LookAtCurrentLocation()

    def ClickPickedObject(self):
        pickInfo = self.GetPickInfo()
        if pickInfo:
            self.mapView.SetSelectedMarker(pickInfo[0][1])

    def GetPickInfo(self):
        mouseX, mouseY = uicore.uilib.x, uicore.uilib.y
        if self.destroyed:
            return None
        pickInfo = self.mapView.GetPickObjects(mouseX, mouseY, getMarkers=True)
        return pickInfo

    def OnMouseWheel(self, *args):
        self.cameraController.OnMouseWheel()

    def OnMouseMove(self, *args):
        if not uicore.IsDragging():
            self.cameraController.OnMouseMove()

    def OnMouseDown(self, *args):
        self.cameraController.OnMouseDown(*args)
        self.mouseDownPick = self.GetPickInfo()
        self.mapView.infoLayer.state = uiconst.UI_DISABLED

    def OnClick(self, *args):
        pickInfo = self.GetPickInfo()
        if pickInfo and pickInfo == self.mouseDownPick:
            self.mapView.SetSelectedMarker(pickInfo[0][1])
        self.mouseDownPick = None

    def OnMouseUp(self, *args):
        self.mapView.infoLayer.state = uiconst.UI_PICKCHILDREN

    def GetMenuForObjectID(self, objectID):
        return self.mapView.GetItemMenu(objectID)

    def GetMenu(self):
        pickInfo = self.mapView.GetPickObjects(uicore.uilib.x, uicore.uilib.y)
        if pickInfo and len(pickInfo) == 1:
            return self.GetMenuForObjectID(pickInfo[0][0])
        locations = [(MenuLabel('UI/Map/Navigation/menuSolarSystem'), self.mapView.SetActiveItemID, (session.solarsystemid2,)), (MenuLabel('UI/Map/Navigation/menuConstellation'), self.mapView.SetActiveItemID, (session.constellationid,)), (MenuLabel('UI/Map/Navigation/menuRegion'), self.mapView.SetActiveItemID, (session.regionid,))]
        m = [(MenuLabel('UI/Map/Navigation/menuSelectCurrent'), locations)]
        mapSvc = sm.GetService('map')
        waypoints = sm.StartService('starmap').GetWaypoints()
        if len(waypoints):
            waypointList = []
            wpCount = 1
            for waypointID in waypoints:
                waypointItem = mapSvc.GetItem(waypointID)
                caption = MenuLabel('UI/Map/Navigation/menuWaypointEntry', {'itemName': waypointItem.itemName,
                 'wpCount': wpCount})
                waypointList += [(caption, self.mapView.SetActiveItemID, (waypointID,))]
                wpCount += 1

            m.append((MenuLabel('UI/Map/Navigation/menuSelectWaypoint'), waypointList))
            m.append(None)
            m.append((MenuLabel('UI/Map/Navigation/menuClearWaypoints'), sm.StartService('starmap').ClearWaypoints, (None,)))
        return m

    def OnDockModeChanged(self):
        pass
