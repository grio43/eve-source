#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\mapView.py
import itertools
import logging
import geo2
import evecamera
import evemath
from brennivin.itertoolsext import Bundle
from carbonui.primitives.base import ScaleDpi
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.util import colorblind
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.filters import filtersByID
from eve.client.script.ui.shared.mapView.filters.colorInfoWrapperMapFilter import ColorInfoWrapperMapFilter
from eve.client.script.ui.shared.mapView.filters.mapFilterConst import PARTICLE_SPRITE_TEXTURE, PARTICLE_SPRITE_HEAT_TEXTURE
from eve.client.script.ui.shared.mapView.layout.mapLayoutHandler import MapViewLayoutHandler
from eve.client.script.ui.shared.mapView.mapViewBookmarkHandler import MapViewBookmarkHandler
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData
from eve.client.script.ui.shared.mapView.mapViewNavigation import MapViewNavigation
from eve.client.script.ui.shared.mapView.markers.mapMarkerEmanationLock import MarkerEmanationLock
from eve.client.script.ui.shared.mapView.markers.mapMarkerMyHome import MarkerMyHome
from eve.client.script.ui.shared.mapView.markers.mapMarkerMyLocation import MarkerMyLocation
from eve.client.script.ui.shared.mapView.markers.mapMarkerVulnerableSkyhook import MarkerVulnerableSkyhook
from eve.client.script.ui.shared.mapView.markers.mapMarkersHandler import MapViewMarkersHandler
from eve.client.script.ui.shared.mapView.mapViewUtil import SolarSystemPosToMapPos
from eve.client.script.ui.shared.mapView.mapViewSceneContainer import MapViewSceneContainer
from eve.client.script.ui.shared.mapView.mapViewSettings import GetMapViewSetting, SetMapViewSetting, IsAbstractModeActive
from eve.client.script.ui.shared.mapView import mapViewUtil
from eve.client.script.ui.shared.mapView.systemMapHandler import SystemMapHandler
from eve.common.lib import appConst
from eve.client.script.ui.shared.mapView.workforce import MapViewSovHubHandler
from eve.common.script.sys.idCheckers import IsStation, IsKnownSpaceSystem, IsKnownSpaceRegion, IsKnownSpaceConstellation
import blue
import trinity
import uthread
from menu import MenuList
from carbonui.primitives.container import Container
import eve.client.script.ui.shared.mapView.mapViewColorHandler as colorHandler
from eve.client.script.ui.shared.mapView.mapViewConst import JUMPBRIDGE_COLOR, JUMPBRIDGE_COLOR_NO_ACCESS, JUMPBRIDGE_TYPE, MARKERID_MYHOME, MARKERID_MYPOS, MARKERID_SOLARSYSTEM_CELESTIAL, MARKERID_EMANATION_LOCK_GATE, UNIVERSE_SCALE, VIEWMODE_COLOR_SETTINGS, VIEWMODE_FOCUS_SELF, VIEWMODE_LAYOUT_CONSTELLATIONS, VIEWMODE_LAYOUT_REGIONS, VIEWMODE_LAYOUT_SETTINGS, VIEWMODE_LAYOUT_SHOW_ABSTRACT_SETTINGS, VIEWMODE_LINES_ALL, VIEWMODE_LINES_NONE, VIEWMODE_LINES_SELECTION_REGION, VIEWMODE_LINES_SELECTION_REGION_NEIGHBOURS, VIEWMODE_LINES_SETTINGS, VIEWMODE_LINES_SHOW_ALLIANCE_SETTINGS, VIEWMODE_LINES_SHOW_JUMP_BRIDGES_MY, VIEWMODE_LINES_SHOW_JUMP_BRIDGES_SETTINGS, VIEWMODE_MARKERS_SETTINGS, MARKERID_VULNERABLE_SKYHOOK, MARKERS_OPTION_VULNERABLE_SKYHOOK, MARKERID_VULNERABLE_SKYHOOK_SOLARSYSTEM
import eve.client.script.ui.shared.maps.mapcommon as mapcommon
from eve.common.script.sys.idCheckers import IsSolarSystem, IsConstellation, IsRegion
import geo2
import carbonui.const as uiconst
from logmodule import LogException
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
from eve.common.lib import appConst as const
from sovereignty.resource.shared.planetary_resources_cache import DataUnavailableError
from stargate.client.gateLockController import GateLockController
from stargate.client import get_gate_lock_messenger
from localization import GetByLabel
from stargate.client.gate_signals import on_lock_removed, on_lock_added
OPACITY_LINES_HOVERED = 0.3
OPACITY_LINES_SELECTED = 1.0
ZOOM_DIST_REGION = 20000
ZOOM_DIST_CONSTELLATION = 10000
ZOOM_DIST_SYSTEM = 6000
TIME_BENICE = 100
log = logging.getLogger(__name__)
LINE_EFFECT = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Lines3DStarMapNew.fx'
PARTICLE_EFFECT = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Particles/StarmapNew.fx'
DISTANCE_RANGE = 'distanceRange'
HEX_TILE_SIZE = 60

class MapView(Container):
    __notifyevents__ = ['OnAvoidanceItemsChanged',
     'OnUIScalingChange',
     'OnAutopilotUpdated',
     'OnDestinationSet',
     'OnHomeStationChanged',
     'OnBallparkSetState',
     'OnSessionChanged',
     'DoBallClear',
     'DoBallsAdded',
     'OnStructuresVisibilityUpdated']
    mapRoot = None
    curveSet = None
    systemMap = None
    markersHandler = None
    bookmarkHandler = None
    sovHubHandler = None
    layoutHandler = None
    markersAlwaysVisible = set()
    markersLoaded = False
    dirtyLineIDs = set()
    inFocus = False
    isFullScreen = False
    currentSolarsystem = None
    hilightID = None
    jumpRouteHighlightID = None
    mapViewID = None
    jumpDriveTransform = None
    mapFilterID = None
    showDebugInfo = False
    cameraID = evecamera.CAM_MAP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.isFullScreen = attributes.isFullScreen
        self.mapViewID = attributes.mapViewID or self.mapViewID
        interestID = attributes.interestID or self._GetDefaultInterestID()
        zoomToItem = attributes.get('zoomToItem', True)
        mapFilterID = attributes.starColorMode or self.mapFilterID
        self.ResetVariables()
        self.mapSvc = sm.GetService('map')
        self.clientPathfinderService = sm.GetService('clientPathfinderService')
        self.mapGroupingMode = self.GetGroupingMode()
        self.layoutHandler = self.ConstructLayoutHandler()
        self.ConstructOverlayTools()
        self.ConstructMarkerLayers()
        self.ConstructMapNavigation()
        self.sceneContainer = MapViewSceneContainer(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, cameraID=self.cameraID)
        uicore.registry.SetFocus(self)
        if mapFilterID is not None:
            self._SetMapFilter(mapFilterID)
        self.constructSceneThread = uthread.new(self._ConstructScene, interestID, zoomToItem, mapFilterID)
        on_lock_added.connect(self._on_emanation_lock_changed)
        on_lock_removed.connect(self._on_emanation_lock_changed)

    def _ConstructScene(self, interestID, zoomToItem, mapFilterID):
        self.sceneContainer.Hide()
        loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER)
        self.sceneContainer.Startup()
        self.camera.SetUpdateCallback(self.OnCameraUpdate)
        self.ConstructStarDataTexture()
        self.ConstructMapScene()
        self.ConstructMapRoot()
        self.ConstructMarkersHandler()
        self.ConstructBookmarkHandler()
        self.ConstructSovHubHandler()
        self.CreateStarParticles()
        self.CreateJumpLineSet()
        self.CreateWorkforceTransportLineSet()
        self.LoadJumpLines()
        self.LoadAllJumpBridges()
        self.UpdateMapLayout()
        self.ReconstructMyLocationMarker()
        self.ReconstructEmanationLockMarker()
        self.ShowMyHomeStation()
        self._SetActiveItemID(interestID)
        self.CheckLoadAllMarkers()
        self.InitCameraFocus(zoomToItem, mapFilterID)
        self.constructSceneThread = None
        loadingWheel.Hide()
        self.sceneContainer.Show()

    def _GetDefaultInterestID(self):
        return session.solarsystemid2

    def UpdateCameraFocus(self, zoomToItem = True, animate = True):
        if not self.CheckUpdateCameraFocusByFilter(animate):
            self.FocusCameraOnActiveEntity(animate=animate, zoomToItem=zoomToItem)

    def InitCameraFocus(self, zoomToItem = True, mapFilterID = None):
        if not mapFilterID or not self.CheckUpdateCameraFocusByFilter(animate=False):
            self.FocusCameraOnActiveEntity(animate=False, zoomToItem=zoomToItem)

    def CheckUpdateCameraFocusByFilter(self, animate = True):
        solarSystemIDs = self.activeFilter.GetSystemsToZoomTo()
        if not solarSystemIDs:
            return False
        if len(solarSystemIDs) > 1:
            self.FocusCameraOnMultipleSystems(solarSystemIDs, animate=animate)
        elif solarSystemIDs:
            self.SetActiveItemID(solarSystemIDs[0])
        return True

    def FocusCameraOnMultipleSystems(self, solarSystemIDs, animate):
        nodes = self.layoutHandler.GetNodesBySolarSystemIDs(solarSystemIDs)
        points = [ node.position for node in nodes ]
        centerPoint = evemath.get_center_point(points)
        distance = evemath.get_farthest_distance_from_point(centerPoint, points)
        self.camera.LookAtPoint(centerPoint, animate=animate, zoomDistance=2 * distance)

    def ConstructMarkerLayers(self):
        self.infoLayer = Container(parent=self, clipChildren=True, name='infoLayer')

    def ConstructMapNavigation(self):
        self.mapNavigation = MapViewNavigation(parent=self, align=uiconst.TOALL, state=uiconst.UI_NORMAL, mapView=self)

    def OnMouseWheel(self, *args):
        self.mapNavigation.OnMouseWheel(*args)

    def ConstructOverlayTools(self):
        pass

    def OnMapCompassClicked(self):
        self.camera.StopUpdateThreads()
        animations.MorphScalar(self.camera, 'yaw', self.camera.yaw, 0.0, duration=0.6)

    def OnSelectedInfoLocationClicked(self, locationID):
        self.SetActiveItemID(locationID, zoomToItem=True)
        self.UpdateLines()

    def Close(self, *args, **kwds):
        if self.destroyed:
            return
        try:
            if self.constructSceneThread:
                self.constructSceneThread.kill()
                self.constructSceneThread = None
            sm.GetService('audio').SendUIEvent('map_stop_all')
            if self.currentSolarsystem:
                self.currentSolarsystem.RemoveFromScene()
            self.currentSolarsystem = None
            if self.camera:
                self.camera.OnDeactivated()
                sm.GetService('sceneManager').UnregisterCamera(self.camera.cameraID)
            if self.markersHandler:
                self.markersHandler.StopHandler()
            self.markersHandler = None
            if self.bookmarkHandler:
                self.bookmarkHandler.StopHandler()
            self.bookmarkHandler = None
            if self.layoutHandler:
                self.layoutHandler.StopHandler()
            self.layoutHandler = None
            self.mapNavigation = None
            self.ResetVariables()
        except:
            LogException()

        Container.Close(self, *args, **kwds)

    def UpdateDebugOutput(self):
        if self.destroyed:
            return
        mapViewUtil.UpdateDebugOutput(self.debugOutput, camera=self.camera, mapView=self)

    def SetFocusState(self, focusState):
        self.inFocus = focusState

    def ResetVariables(self):
        self.LogInfo('MapViewPanel Reset')
        self.destinationPath = [None]
        self.currentSolarsystem = None
        self.lineMode = None
        if self.mapRoot is not None:
            del self.mapRoot.children[:]
        self.mapRoot = None
        self.mapStars = None
        self.starParticles = None
        self.solarSystemJumpLineSet = None
        self.overlayContentFrame = None
        self.distanceRangeLines = None
        self.starColorByID = {}
        self.activeItemID = None
        self.activeLocalID = None
        self.activeSolarSystemID = None
        self.activeConstellationID = None
        self.activeRegionID = None
        self.isExpandingSolarSystem = False

    def OnDockModeChanged(self, isFullScreen):
        if self.destroyed:
            return
        self.isFullScreen = isFullScreen
        if isFullScreen:
            self.camera.EnableCenterOffset()
        else:
            self.camera.DisableCenterOffset()

    def OnMapViewSettingChanged(self, settingKey, settingValue, *args, **kwds):
        if settingKey == VIEWMODE_FOCUS_SELF:
            if not IsKnownSpaceSystem(session.solarsystemid2):
                mapViewUtil.OpenSolarSystemMap()
            else:
                self.LookAtCurrentLocation()
                self.UpdateLines()
        elif settingKey == VIEWMODE_MARKERS_SETTINGS:
            if self.currentSolarsystem:
                self.currentSolarsystem.LoadMarkers(showChanges=True)
            else:
                self.LoadBookmarkMarkers()
                self.LoadShowHubMarkers()
                self.LoadVulnerableSkyhooks()
        elif settingKey == VIEWMODE_COLOR_SETTINGS:
            self.UpdateMapViewColorMode()
        elif settingKey == VIEWMODE_LAYOUT_SETTINGS:
            self.mapGroupingMode = settingValue
            self.UpdateMapLayout()
        elif settingKey == VIEWMODE_LAYOUT_SHOW_ABSTRACT_SETTINGS:
            self.AnimFadeOutInfoLayer()
            self.UpdateMapLayout()
            self.AnimFadeInInfoLayer()
        else:
            self.UpdateMapLayout()

    def LookAtCurrentLocation(self):
        zoomToItem = self.camera.GetZoomDistance() > 50000
        self.SetActiveItemID(itemID=session.solarsystemid2, localID=(MARKERID_MYPOS, session.charid), zoomToItem=zoomToItem)

    def UpdateMapLayout(self):
        self.UpdateMapViewColorMode()
        if self.destroyed:
            return
        self.ReconstructMyLocationMarker()
        self.ReconstructEmanationLockMarker()
        self.RefreshActiveState()
        currentLineMode = self.GetLineMode()
        if currentLineMode != self.lineMode:
            self.UpdateLines(hint='OnMapViewSettingChanged')

    def IsAbstractModeActive(self):
        return IsAbstractModeActive(self.mapViewID)

    def GetGroupingMode(self):
        return GetMapViewSetting(VIEWMODE_LAYOUT_SETTINGS, self.mapViewID)

    def SetGroupingMode(self, groupingMode):
        if self.mapGroupingMode == groupingMode:
            return
        self.mapGroupingMode = groupingMode
        self.LoadStarLayout(self.activeItemID)

    def ConstructLayoutHandler(self):
        return MapViewLayoutHandler(self)

    def ConstructMapScene(self):
        self.sceneContainer.Startup()
        self.mapScene = trinity.EveSpaceScene()
        self.mapScene.backgroundRenderingEnabled = True
        self.ConstructStarfield()
        self.sceneContainer.scene = self.mapScene
        self.sceneContainer.DisplaySpaceScene()
        return self.mapScene

    def ConstructStarfield(self):
        self.mapScene.starfield = trinity.Load('res:/dx9/scene/starfield/spritestars.red')
        self.mapScene.starfield.maxDist = 300
        self.mapScene.starfield.minDist = 300

    def ConstructMapRoot(self):
        self.mapRoot = trinity.EveRootTransform()
        self.mapRoot.name = 'mapRoot'
        self.mapRoot.display = False
        self.mapScene.objects.append(self.mapRoot)

    def ConstructMarkersHandler(self):
        self.markersHandler = MapViewMarkersHandler(self, self.sceneContainer.bracketCurveSet, self.infoLayer, eventHandler=self.mapNavigation)

    def ConstructBookmarkHandler(self):
        self.bookmarkHandler = MapViewBookmarkHandler(self, loadUniverseBookmarks=True, solarSystemScaling=mapViewConst.SCALING_SOLARSYSTEMINWORLDMAP)

    def ConstructSovHubHandler(self):
        self.sovHubHandler = MapViewSovHubHandler(self)

    @apply
    def camera():

        def fget(self):
            if self.sceneContainer:
                return self.sceneContainer.camera

        return property(**locals())

    @apply
    def scene():

        def fget(self):
            return self.sceneContainer.scene

        return property(**locals())

    def LogError(self, *args, **kwds):
        log.error('MAPVIEW ' + repr(args))

    def LogInfo(self, *args, **kwds):
        log.info('MAPVIEW ' + repr(args))

    def LogWarn(self, *args, **kwds):
        log.warning('MAPVIEW ' + repr(args))

    def OnAvoidanceItemsChanged(self):
        colorMode, itemID = self.GetFilterIDAndItemID()
        if colorMode == mapcommon.STARMODE_AVOIDANCE:
            self.UpdateMapViewColorMode()

    def OnUIScalingChange(self, *args):
        self.markersHandler.ReloadAll()

    def OnWindowResize(self, width, height):
        self.UpdateViewPort()

    def GetPickObjects(self, mouseX, mouseY, getMarkers = True):
        if not self.markersHandler:
            return
        x, y = ScaleDpi(mouseX), ScaleDpi(mouseY)
        vx, vy = self.sceneContainer.viewport.x, self.sceneContainer.viewport.y
        lastDistance = None
        picked = []
        for markerID, marker in self.markersHandler.projectBrackets.iteritems():
            if not marker.projectBracket.isInFront or not marker.positionPickable:
                continue
            mx, my = marker.projectBracket.rawProjectedPosition
            if x - 7 < vx + mx < x + 8 and y - 7 < vy + my < y + 8:
                distance = marker.projectBracket.cameraDistance
                if distance < self.camera.farClip and (lastDistance is None or distance < lastDistance):
                    if getMarkers:
                        picked = [(markerID, marker)]
                    else:
                        picked = [markerID]
                    lastDistance = distance

        return picked

    def GetItemMenu(self, itemID):
        item = self.mapSvc.GetItem(itemID, retall=True)
        if not item:
            return MenuList()
        m = MenuList([None])
        m += GetMenuService().CelestialMenu(itemID, mapItem=item)
        return m.filter('UI/Commands/ShowLocationOnMap')

    def ShowMyHomeStation(self):
        if self.destroyed:
            return
        markerID = (MARKERID_MYHOME, session.charid)
        self.markersHandler.RemoveMarker(markerID)
        try:
            self.markersAlwaysVisible.remove(markerID)
        except:
            pass

        homeStationRow = sm.GetService('charactersheet').GetHomeStationRow()
        homeStationID = homeStationRow.stationID
        if not homeStationID or self.destroyed:
            return
        solarSystemID = homeStationRow.solarSystemID
        regionID = self.mapSvc.GetRegionForSolarSystem(solarSystemID)
        if not IsKnownSpaceRegion(regionID):
            return
        mapNode = self.layoutHandler.GetNodeBySolarSystemID(solarSystemID)
        solarSystemPosition = mapNode.position
        if IsStation(homeStationID):
            stationInfo = sm.GetService('ui').GetStationStaticInfo(homeStationID)
            pos = (stationInfo.x, stationInfo.y, stationInfo.z)
        else:
            stationInfo = Bundle(stationID=homeStationID, stationTypeID=homeStationRow.stationTypeID)
            pos = mapViewUtil.TryGetPosFromItemID(homeStationID, solarSystemID)
        localPosition = self.SolarSystemPosToMapPos(pos)
        self.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerMyHome, stationInfo=stationInfo, solarSystemID=solarSystemID, mapPositionLocal=localPosition, mapPositionSolarSystem=solarSystemPosition)
        self.markersAlwaysVisible.add(markerID)

    def SolarSystemPosToMapPos(self, pos):
        return geo2.Vec3Scale(mapViewUtil.SolarSystemPosToMapPos(pos), mapViewConst.SCALING_SOLARSYSTEMINWORLDMAP)

    def RemoveMyLocation(self):
        markerID = (MARKERID_MYPOS, session.charid)
        self.markersHandler.RemoveMarker(markerID, fadeOut=False)

    def LoadVulnerableSkyhooks(self):
        uthread.new(self._LoadVulnerableSkyhooks)

    def _LoadVulnerableSkyhooks(self):
        if self.destroyed:
            return
        if self.mapRoot is None:
            return
        self.markersHandler.RemoveMarkersByType(MARKERID_VULNERABLE_SKYHOOK_SOLARSYSTEM)
        skyhook_settings = GetMapViewSetting(VIEWMODE_MARKERS_SETTINGS, self.mapViewID)
        skyhooks_enabled = MARKERS_OPTION_VULNERABLE_SKYHOOK in skyhook_settings
        if not skyhooks_enabled:
            self.markersHandler.RemoveMarkersByType(MARKERID_VULNERABLE_SKYHOOK)
            return
        try:
            solar_systems = sm.GetService('sovereigntyResourceSvc').GetSolarSystemsWithTheftVulnerableSkyhooks()
        except DataUnavailableError:
            return

        if self.destroyed:
            return
        if self.mapRoot is None:
            return
        for solar_system_id in solar_systems:
            map_node = self.layoutHandler.GetNodeBySolarSystemID(solar_system_id)
            position = map_node.position
            marker_id = (MARKERID_VULNERABLE_SKYHOOK, solar_system_id)
            self.markersHandler.AddSolarSystemBasedMarker(marker_id, MarkerVulnerableSkyhook, solarSystemID=solar_system_id, mapPositionLocal=(0, 0, 0), mapPositionSolarSystem=position, distanceFadeAlphaNearFar=None)

    def _ConstructSolarSystemVulnerableSkyhooks(self, solar_system_id, solar_system_position):
        try:
            expiry_by_planet = sm.GetService('sovereigntyResourceSvc').GetPlanetIDsAndTheftVulnerabilityExpiry(solar_system_id)
            planets = expiry_by_planet.keys()
        except DataUnavailableError:
            return

        if len(planets) == 0:
            return
        marker_id = (MARKERID_VULNERABLE_SKYHOOK, solar_system_id)
        self.markersHandler.RemoveMarker(marker_id)
        for planet_id in planets:
            planet = cfg.mapSolarSystemContentCache.planets[planet_id]
            planet_position = (planet.position.x, planet.position.y, planet.position.z)
            planet_position = SolarSystemPosToMapPos(planet_position)
            planet_position = geo2.Vec3ScaleD(planet_position, mapViewConst.SCALING_SOLARSYSTEMINWORLDMAP)
            marker_id = (MARKERID_VULNERABLE_SKYHOOK_SOLARSYSTEM, solar_system_id)
            self.markersHandler.AddSolarSystemBasedMarker(marker_id, MarkerVulnerableSkyhook, solarSystemID=solar_system_id, mapPositionLocal=planet_position, mapPositionSolarSystem=solar_system_position, distanceFadeAlphaNearFar=None)

    def _on_emanation_lock_changed(self, lock_details):
        uthread.new(self.ReconstructEmanationLockMarker)

    def RemoveEmanationLockMarker(self):
        markerID = (MARKERID_EMANATION_LOCK_GATE, session.charid)
        self.markersHandler.RemoveMarker(markerID, fadeOut=False)

    def ReconstructEmanationLockMarker(self):
        if self.destroyed:
            return
        if self.mapRoot is None:
            return
        self.RemoveEmanationLockMarker()
        markerID = (MARKERID_EMANATION_LOCK_GATE, session.charid)
        self.markersAlwaysVisible.discard(markerID)
        gateLockController = GateLockController.get_instance(get_gate_lock_messenger(sm.GetService('publicGatewaySvc')))
        lockDetails = gateLockController.get_current_system_lock()
        if lockDetails is None or lockDetails.solar_system_id != session.solarsystemid2:
            return
        gateItemID = lockDetails.gate_id
        gateBall = sm.GetService('michelle').GetBall(gateItemID)
        if gateBall is None:
            return
        gateTypeID = gateBall.typeID
        pos = SolarSystemPosToMapPos((gateBall.x, gateBall.y, gateBall.z))
        pos = geo2.Vec3ScaleD(pos, mapViewConst.SCALING_SOLARSYSTEMINWORLDMAP)
        mapNode = self.layoutHandler.GetNodeBySolarSystemID(session.solarsystemid2)
        if mapNode is None:
            return
        solarSystemPos = mapNode.position
        marker = self.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerEmanationLock, solarSystemID=session.solarsystemid2, mapPositionLocal=pos, mapPositionSolarSystem=solarSystemPos, distanceFadeAlphaNearFar=None)
        marker.SetLabelTextFromItem(gateItemID, gateTypeID)
        self.markersAlwaysVisible.add(markerID)

    def ReconstructMyLocationMarker(self):
        if self.destroyed:
            return
        if self.mapRoot is None:
            return
        self.RemoveMyLocation()
        markerID = (MARKERID_MYPOS, session.charid)
        try:
            self.markersAlwaysVisible.remove(markerID)
        except:
            pass

        markerObject = None
        if IsKnownSpaceRegion(session.regionid):
            mapNode = self.layoutHandler.GetNodeBySolarSystemID(session.solarsystemid2)
            solarSystemPosition = mapNode.position
            if session.stationid or session.structureid:
                markerObject = self._ConstructMyLocationMarkerStation(markerID, solarSystemPosition)
            else:
                markerObject = self._ConstructMyLocationMarkerSpace(markerID, solarSystemPosition)
            self.markersAlwaysVisible.add(markerID)
        self.ShowJumpDriveRange(markerObject)

    def _ConstructMyLocationMarkerSpace(self, markerID, solarSystemPosition):
        bp = sm.GetService('michelle').GetBallpark()
        if bp and bp.ego and bp.ego in bp.balls and False:
            ego = bp.balls[bp.ego]
            localPosition = self.SolarSystemPosToMapPos((ego.x, ego.y, ego.z))
        else:
            localPosition = (0.0, 0.0, 0.0)
        if self.currentSolarsystem:
            trackObjectID = session.shipid or session.stationid
            scale = mapViewConst.SCALING_SOLARSYSTEMINWORLDMAP
        else:
            trackObjectID = None
            scale = None
        markerObject = self.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerMyLocation, trackObjectID=trackObjectID, trackObjectScale=scale, solarSystemID=session.solarsystemid2, mapPositionLocal=localPosition, mapPositionSolarSystem=solarSystemPosition)
        return markerObject

    def _ConstructMyLocationMarkerStation(self, markerID, solarSystemPosition):
        if session.stationid:
            stationInfo = sm.GetService('ui').GetStationStaticInfo(session.stationid)
            if self.destroyed:
                return
            pos = (stationInfo.x, stationInfo.y, stationInfo.z)
        else:
            structure = self.mapSvc.GetMapDataForStructure(session.solarsystemid2, session.structureid)
            if not structure:
                return
            pos = (structure.x, structure.y, structure.z)
        localPosition = self.SolarSystemPosToMapPos(pos)
        return self.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerMyLocation, solarSystemID=session.solarsystemid2, mapPositionLocal=localPosition, mapPositionSolarSystem=solarSystemPosition)

    def ShowJumpDriveRange(self, markerObject):
        self.RemoveJumpDriveRange()
        if not IsKnownSpaceRegion(session.regionid):
            return
        if markerObject is None:
            return
        if session.shipid is None:
            return
        dogmaLM = sm.GetService('clientDogmaIM').GetDogmaLocation()
        try:
            driveRange = dogmaLM.GetAttributeValue(session.shipid, const.attributeJumpDriveRange)
        except KeyError:
            log.warning('Unable to get driveRange for ship: %s' % session.shipid)
            return

        if driveRange is None or driveRange == 0:
            return
        scale = 2.0 * driveRange * appConst.LIGHTYEAR * UNIVERSE_SCALE
        sphere = trinity.Load('res:/dx9/model/UI/JumpRangeBubble.red')
        scaling = (scale, scale * self.GetYScaleFactor(), scale)
        sphere.scaling = scaling
        sphere.name = 'jumpDriveRange'
        self.mapRoot.children.append(sphere)
        markerObject.RegisterTrackingTransform(sphere)
        self.jumpDriveTransform = sphere

    def RemoveJumpDriveRange(self):
        if self.jumpDriveTransform:
            if self.jumpDriveTransform in self.mapRoot.children:
                self.mapRoot.children.remove(self.jumpDriveTransform)

    def LayoutChangeStarting(self, changedSolarSystems):
        pass

    def AnimFadeOutInfoLayer(self):
        uicore.animations.FadeTo(self.infoLayer, startVal=self.infoLayer.opacity, endVal=0.0, duration=0.1, sleep=True)

    def LayoutChanging(self, progress, changedSolarSystems):
        if self.currentSolarsystem and self.currentSolarsystem.solarsystemID in changedSolarSystems:
            mapNode = changedSolarSystems[self.currentSolarsystem.solarsystemID]
            newPosition = geo2.Vec3Lerp(mapNode.oldPosition, mapNode.position, progress)
            self.currentSolarsystem.SetPosition(newPosition)

    def LayoutChangeCompleted(self, changedSolarSystems):
        if self.destroyed:
            return
        self.starParticles.UpdateBoundingBox()
        self.mapStars.mesh.minBounds = self.starParticles.aabbMin
        self.mapStars.mesh.maxBounds = self.starParticles.aabbMax
        self.markersHandler.UpdateMarkerPositions(changedSolarSystems, self.GetYScaleFactor())
        self.RefreshLines()
        self.mapRoot.display = True

    def AnimFadeInInfoLayer(self):
        uicore.animations.FadeTo(self.infoLayer, startVal=self.infoLayer.opacity, endVal=1.0, duration=0.3, timeOffset=0.7)

    def SetMarkersFilter(self, showMarkers):
        if showMarkers:
            showMarkers += list(self.markersAlwaysVisible)
        self.markersHandler.SetDisplayStateOverrideFilter(showMarkers)

    def CreateStarParticles(self):
        self.mapStars = trinity.EveTransform()
        self.mapStars.name = 'mapStars'
        self.mapStars.sortValueMultiplier = 1000000.0
        self.starParticleTexture = trinity.TriTextureParameter()
        self.starParticleTexture.name = 'TexMap'
        self.starParticleTexture.resourcePath = PARTICLE_SPRITE_TEXTURE
        distanceRangeStars = trinity.Tr2Vector4Parameter()
        distanceRangeStars.name = DISTANCE_RANGE
        distanceRangeStars.value = (0, 1, 0, 0)
        self.distanceRangeStars = distanceRangeStars
        self.starParticles = trinity.Tr2RuntimeInstanceData()
        self.starParticles.SetElementLayout([(trinity.PARTICLE_ELEMENT_TYPE.POSITION, 0, 3),
         (trinity.PARTICLE_ELEMENT_TYPE.POSITION, 1, 3),
         (trinity.PARTICLE_ELEMENT_TYPE.CUSTOM, 0, 1),
         (trinity.PARTICLE_ELEMENT_TYPE.CUSTOM, 1, 4)])
        mesh = trinity.Tr2InstancedMesh()
        mesh.geometryResPath = 'res:/Graphics/Generic/UnitPlane/UnitPlane.gr2'
        mesh.instanceGeometryResource = self.starParticles
        self.mapStars.mesh = mesh
        area = trinity.Tr2MeshArea()
        area.effect = trinity.Tr2Effect()
        area.effect.effectFilePath = PARTICLE_EFFECT
        area.effect.resources.append(self.starParticleTexture)
        area.effect.resources.append(self.starDataTexture)
        area.effect.parameters.append(distanceRangeStars)
        mesh.transparentAreas.append(area)
        particleCounter = itertools.count()
        starParticleData = []
        initPos = (0.0, 0.0, 0.0)
        for systemID, system in self._GetKnownUniverseSolarSystems().iteritems():
            particleID = particleCounter.next()
            starParticleData.append((initPos,
             initPos,
             0.0,
             (0.0, 0.0, 0.0, 0.0)))
            self.layoutHandler.CreateSolarSystemNode(particleID, systemID, initPos, system)

        vs = trinity.GetVariableStore()
        vs.RegisterVariable('StarmapMorphValue', 0.0)
        self.starParticles.SetData(starParticleData)
        self.layoutHandler.RegisterStarParticles(self.starParticles)
        self.mapRoot.children.append(self.mapStars)

    def _GetKnownUniverseSolarSystems(self):
        return mapViewData.GetKnownUniverseSolarSystems()

    def _GetKnownUniverseConstellations(self):
        return mapViewData.GetKnownUniverseConstellations()

    def _GetKnownUniverseRegions(self):
        return mapViewData.GetKnownUniverseRegions()

    def ConstructStarDataTexture(self):
        heattex = trinity.TriTextureParameter()
        heattex.name = 'HeatTexture'
        heattex.resourcePath = PARTICLE_SPRITE_HEAT_TEXTURE
        self.starDataTexture = heattex

    def CreateJumpLineSet(self):
        self.solarSystemJumpLineSet = mapViewUtil.CreateLineSet()
        self.solarSystemJumpLineSet.lineEffect.effectFilePath = LINE_EFFECT
        self.solarSystemJumpLineSet.name = 'JumpLines'
        self.mapRoot.children.append(self.solarSystemJumpLineSet)
        if self.distanceRangeLines is None:
            distanceRangeLines = trinity.Tr2Vector4Parameter()
            distanceRangeLines.name = DISTANCE_RANGE
            distanceRangeLines.value = (0, 1, 0, 0)
            self.distanceRangeLines = distanceRangeLines
        self.solarSystemJumpLineSet.lineEffect.parameters.append(self.distanceRangeLines)
        self.layoutHandler.RegisterJumpLineSet(self.solarSystemJumpLineSet)

    def CreateWorkforceTransportLineSet(self):
        self.workforceTransportLineSet = mapViewUtil.CreateLineSet()
        self.workforceTransportLineSet.lineEffect.effectFilePath = LINE_EFFECT
        self.workforceTransportLineSet.name = 'WorkforceTransportLines'
        for tex2D in self.workforceTransportLineSet.lineEffect.resources:
            tex2D.resourcePath = 'res:/UI/Texture/classes/LineSet/lineSegment.dds'

        self.mapRoot.children.append(self.workforceTransportLineSet)
        self.workforceTransportLineSet.lineEffect.parameters.append(self.distanceRangeLines)
        self.layoutHandler.RegisterTransitLineSet(self.workforceTransportLineSet)

    def OnCameraUpdate(self):
        camera = self.camera
        if camera is None:
            return
        if not self.starParticles:
            return
        cameraDistance = self.camera.GetZoomDistanceForMap()
        self.UpdateAudioLoop(cameraDistance)
        aabbMin = self.starParticles.aabbMin
        aabbMax = self.starParticles.aabbMax
        bbSize = geo2.Vec3Add(geo2.Vec3Negate(aabbMin), aabbMax)
        maxLength = geo2.Vec3Length(bbSize)
        self.camera.nearClip = 0.1
        self.camera.farClip = cameraDistance + maxLength
        fadeOutFar = max(100.0, cameraDistance * 4)
        self.distanceRangeStars.value = (cameraDistance,
         fadeOutFar,
         0,
         0)
        if self.distanceRangeLines:
            self.distanceRangeLines.value = (cameraDistance,
             fadeOutFar * 100,
             0,
             0)
        if self.markersHandler:
            self.markersHandler.RegisterCameraTranslationFromParent(cameraDistance)
        if self.currentSolarsystem:
            self.currentSolarsystem.RegisterCameraTranslationFromParent(cameraDistance)
        self.CheckToggleExpandSolarSystem()

    def UpdateAudioLoop(self, cameraDistance):
        if cameraDistance < mapViewConst.AUDIO_SOLARSYSTEM_DISTANCE:
            if self.inFocus:
                self.ChangeAmbientAudioLoop('map_system_loop_play')
            else:
                self.ChangeAmbientAudioLoop('map_system_loop_window_play')
        elif cameraDistance < mapViewConst.AUDIO_CONSTELLATION_DISTANCE:
            if self.inFocus:
                self.ChangeAmbientAudioLoop('map_constellation_loop_play')
            else:
                self.ChangeAmbientAudioLoop('map_constellation_loop_window_play')
        elif self.inFocus:
            self.ChangeAmbientAudioLoop('map_region_loop_play')
        else:
            self.ChangeAmbientAudioLoop('map_region_loop_window_play')

    def CheckToggleExpandSolarSystem(self):
        if self.camera.GetZoomDistance() < 5000 * mapViewConst.SCALING_SOLARSYSTEMINWORLDMAP:
            self.ExpandSelectedSolarSystem(self.activeSolarSystemID)
        else:
            self.CloseCurrentSolarSystemIfAny()

    def ChangeAmbientAudioLoop(self, audioPath):
        if getattr(self, 'ambientAudioPath', None) != audioPath:
            self.ambientAudioPath = audioPath
            sm.GetService('audio').SendUIEvent('map_stop_all')
            sm.GetService('audio').SendUIEvent(audioPath)

    def GetStarData(self):
        return getattr(self, 'starData', {})

    def GetDistance(self, fromVector, toVector):
        return geo2.Vec3Length(geo2.Vec3Subtract(fromVector, toVector))

    def GetExtraMouseOverInfoForItemID(self, itemID):
        mapNode = self.layoutHandler.GetNodeBySolarSystemID(itemID)
        if mapNode:
            return self.activeFilter.GetSystemHint(itemID)

    def OnMarkerHovered(self, itemID = None):
        hilightID = itemID
        if self.hilightID != hilightID:
            self.hilightID = hilightID
            if hilightID:
                self.markersHandler.HilightMarkers([hilightID])
            else:
                self.markersHandler.HilightMarkers([])
            self.UpdateLines()
        elif not itemID and self.markersHandler and self.markersHandler.hilightMarkers:
            self.markersHandler.HilightMarkers([])
            self.UpdateLines()

    def SetCameraPointOfInterestSolarSystemPosition(self, solarSystemID, position):
        mapInfo = mapViewData.GetKnownSolarSystem(solarSystemID)
        if not mapInfo:
            return
        mapNode = self.layoutHandler.GetNodeBySolarSystemID(solarSystemID)
        self.camera.SetAtPosition(geo2.Vec3Add(mapNode.position, self.SolarSystemPosToMapPos(position)))

    def SetSelectedMarker(self, markerObject, **kwds):
        zoomToItem = self._GetZoomToItem(markerObject.markerID)
        if mapViewUtil.IsDynamicMarkerType(markerObject.markerID):
            self.SetActiveItemID(itemID=markerObject.solarSystemID, localID=markerObject.markerID, zoomToItem=zoomToItem, **kwds)
        else:
            self.SetActiveItemID(itemID=markerObject.markerID, zoomToItem=zoomToItem, **kwds)

    def _GetZoomToItem(self, itemID):
        if IsRegion(itemID):
            if self.camera.GetZoomDistance() > 2.0 * ZOOM_DIST_REGION:
                return True
        elif IsConstellation(itemID):
            if self.camera.GetZoomDistance() > 1.5 * ZOOM_DIST_CONSTELLATION:
                return True
        return False

    def RefreshActiveState(self, updateCamera = True):
        if self.activeItemID:
            self.SetActiveItemID(self.activeItemID, self.activeLocalID, updateCamera=updateCamera)

    def LoadStarLayout(self, itemID):
        keywords = {'yScaleFactor': self.GetYScaleFactor()}
        if self.mapGroupingMode == VIEWMODE_LAYOUT_REGIONS:
            if IsRegion(itemID):
                keywords['expandedItems'] = [itemID]
            elif IsConstellation(itemID):
                mapInfo = mapViewData.GetKnownConstellation(itemID)
                keywords['expandedItems'] = [mapInfo.regionID]
            if IsSolarSystem(itemID) and IsKnownSpaceSystem(itemID):
                mapInfo = mapViewData.GetKnownSolarSystem(itemID)
                keywords['expandedItems'] = [mapInfo.regionID]
        elif self.mapGroupingMode == VIEWMODE_LAYOUT_CONSTELLATIONS:
            if IsConstellation(itemID):
                keywords['expandedItems'] = [itemID]
            elif IsSolarSystem(itemID) and IsKnownSpaceSystem(itemID):
                mapInfo = mapViewData.GetKnownSolarSystem(itemID)
                keywords['expandedItems'] = [mapInfo.constellationID]
        self.layoutHandler.LoadLayout(self.mapGroupingMode, **keywords)

    def GetYScaleFactor(self):
        if self.IsAbstractModeActive():
            return 0.25
        return 1.0

    def SetActiveItemID(self, itemID, localID = None, zoomToItem = False, animate = True, updateCamera = True, *args, **kwds):
        self._SetActiveItemID(itemID, localID)
        if updateCamera:
            self.FocusCameraOnActiveEntity(animate=animate, zoomToItem=zoomToItem)
        self.UpdateLines('SetActiveItemID')

    def _SetActiveItemID(self, itemID, localID = None):
        itemID, localID = self._CheckMangleIDs(itemID, localID)
        self.LoadStarLayout(itemID)
        if self.inFocus:
            self.PlaySelectionSound(itemID)
        self.activeItemID = itemID
        self.activeLocalID = localID
        if self.IsInKnownSpace(itemID):
            if IsConstellation(itemID) or IsRegion(itemID):
                self.CloseCurrentSolarSystemIfAny()
            self._UpdateActiveSystemConstRegion(itemID)
            self._UpdateActiveMarkers(itemID)

    def IsInKnownSpace(self, itemID):
        return IsKnownSpaceSystem(itemID) or IsKnownSpaceConstellation(itemID) or IsKnownSpaceRegion(itemID)

    def _CheckMangleIDs(self, primaryItemID, localID):
        if localID == (MARKERID_MYPOS, session.charid):
            primaryItemID = session.solarsystemid2
            localID = localID
        elif IsStation(primaryItemID):
            stationData = cfg.stations.Get(primaryItemID)
            primaryItemID = stationData.solarSystemID
            localID = (MARKERID_SOLARSYSTEM_CELESTIAL, primaryItemID)
        return (primaryItemID, localID)

    def PlaySelectionSound(self, itemID):
        if IsSolarSystem(itemID):
            sm.GetService('audio').SendUIEvent('map_system_zoom_play')
        elif IsConstellation(itemID):
            sm.GetService('audio').SendUIEvent('map_constellation_zoom_play')
        elif IsRegion(itemID):
            sm.GetService('audio').SendUIEvent('map_region_zoom_play')

    def _GetCameraPointOfInterest(self, itemID):
        if IsSolarSystem(itemID):
            return self._GetCameraPointOfInterestSolarSystem(itemID)
        elif IsConstellation(itemID):
            return self._GetCameraPointOfInterestConstellation(itemID)
        elif IsRegion(itemID):
            return self._GetCameraPointOfInterestRegion(itemID)
        else:
            return (0.0, 0.0, 0.0)

    def _UpdateActiveMarkers(self, itemID):
        if IsSolarSystem(itemID):
            activeIDs, selectedIDs = self.GetActiveAndSelectedIdsSolarSystem(itemID)
        elif IsConstellation(itemID):
            activeIDs, selectedIDs = self.GetActiveAndSelectedIdsConstellation(itemID)
        elif IsRegion(itemID):
            activeIDs, selectedIDs = self.GetActiveAndSelectedIDsRegion(itemID)
        else:
            activeIDs = []
            selectedIDs = []
        activeIDs += self.GetAlwaysActiveSystemIDs()
        self.markersHandler.UpdateMarkerState(activeIDs, selectedIDs)

    def GetActiveAndSelectedIdsSolarSystem(self, itemID):
        solarSystemData = mapViewData.GetKnownSolarSystem(itemID)
        constellationData = mapViewData.GetKnownConstellation(solarSystemData.constellationID)
        regionData = mapViewData.GetKnownRegion(solarSystemData.regionID)
        activeIDs = solarSystemData.neighbours + constellationData.solarSystemIDs + regionData.constellationIDs + [solarSystemData.regionID]
        selectedIDs = [itemID, solarSystemData.constellationID]
        return (activeIDs, selectedIDs)

    def GetActiveAndSelectedIdsConstellation(self, itemID):
        constellationData = mapViewData.GetKnownConstellation(itemID)
        regionData = mapViewData.GetKnownRegion(constellationData.regionID)
        activeIDs = regionData.constellationIDs + constellationData.solarSystemIDs + [constellationData.regionID]
        selectedIDs = [itemID]
        return (activeIDs, selectedIDs)

    def GetActiveAndSelectedIDsRegion(self, itemID):
        regionData = mapViewData.GetKnownRegion(itemID)
        activeIDs = [itemID] + regionData.constellationIDs
        selectedIDs = [itemID]
        return (activeIDs, selectedIDs)

    def GetAlwaysActiveSystemIDs(self):
        solarSystemIDs = sm.GetService('starmap').GetDestinationPath()
        solarSystemIDs.append(session.solarsystemid2)
        return solarSystemIDs

    def _UpdateActiveSystemConstRegion(self, itemID):
        if IsSolarSystem(itemID):
            self._UpdateActiveItemSolarSystem(itemID)
        elif IsConstellation(itemID):
            self._UpdateActiveItemConstellation(itemID)
        elif IsRegion(itemID):
            self._UpdateActiveItemRegion(itemID)
        else:
            self._UpdateActiveItemUniverse()

    def _UpdateActiveItemSolarSystem(self, itemID):
        solarSystemData = mapViewData.GetKnownSolarSystem(itemID)
        self.activeSolarSystemID = itemID
        self.activeConstellationID = solarSystemData.constellationID
        self.activeRegionID = solarSystemData.regionID

    def _GetCameraPointOfInterestSolarSystem(self, itemID):
        try:
            return self.layoutHandler.GetNodeBySolarSystemID(itemID).position
        except AttributeError:
            return None

    def _UpdateActiveItemConstellation(self, itemID):
        mapData = mapViewData.GetKnownConstellation(itemID)
        self.activeSolarSystemID = None
        self.activeConstellationID = itemID
        self.activeRegionID = mapData.regionID

    def _GetCameraPointOfInterestConstellation(self, itemID):
        mapData = mapViewData.GetKnownConstellation(itemID)
        positions = [ self.layoutHandler.GetNodeBySolarSystemID(solarSystemID).position for solarSystemID in mapData.solarSystemIDs ]
        cameraPointOfInterest, radius = mapViewUtil.GetBoundingSphereRadiusCenter(positions, self.GetYScaleFactor())
        return cameraPointOfInterest

    def _GetCameraPointOfInterestRegion(self, itemID):
        mapData = mapViewData.GetKnownRegion(itemID)
        positions = [ self.layoutHandler.GetNodeBySolarSystemID(solarSystemID).position for solarSystemID in mapData.solarSystemIDs ]
        cameraPointOfInterest, radius = mapViewUtil.GetBoundingSphereRadiusCenter(positions, self.GetYScaleFactor())
        return cameraPointOfInterest

    def _UpdateActiveItemRegion(self, itemID):
        self.activeSolarSystemID = None
        self.activeConstellationID = None
        self.activeRegionID = itemID

    def _UpdateActiveItemUniverse(self):
        self.activeSolarSystemID = None
        self.activeConstellationID = None
        self.activeRegionID = None

    def CheckLoadAllMarkers(self):
        if not self.markersLoaded and not self.destroyed:
            self.markersLoaded = True
            self._LoadAllMarkers()
            if self.destroyed:
                return
            self.markersHandler.UpdateMarkers()

    def _LoadAllMarkers(self):
        self.LoadRegionMarkers()
        self.LoadConstellationMarkers()
        self.LoadBookmarkMarkers()
        self.LoadLandmarkMarkers()
        self.LoadSolarSystemMarkers()
        self.LoadShowHubMarkers()
        self.LoadVulnerableSkyhooks()

    def FocusCameraOnActiveEntity(self, animate = True, zoomToItem = False):
        markerObject = self.markersHandler.GetMarkerByID(self.activeLocalID)
        if not markerObject:
            markerObject = self.markersHandler.GetMarkerByID(self.activeItemID)
        zoomDistance = self.GetZoomDistanceByLocationType(self.activeItemID) if zoomToItem else None
        if markerObject:
            self.camera.LookAtMarker(markerObject, animate=animate, zoomDistance=zoomDistance)
        else:
            cameraPointOfInterest = self._GetCameraPointOfInterest(self.activeItemID)
            if cameraPointOfInterest:
                self.camera.LookAtPoint(cameraPointOfInterest, animate=animate, zoomDistance=zoomDistance)

    def GetZoomDistanceByLocationType(self, itemID):
        if IsRegion(itemID):
            zoomDistance = ZOOM_DIST_REGION
        elif IsConstellation(itemID):
            zoomDistance = ZOOM_DIST_CONSTELLATION
        else:
            zoomDistance = ZOOM_DIST_SYSTEM
        return zoomDistance

    def CloseCurrentSolarSystemIfAny(self):
        if not self.currentSolarsystem:
            return
        self.currentSolarsystem.Close()
        self.currentSolarsystem = None
        self.layoutHandler.SetExpandedSolarSystemID(None)
        self.ReconstructMyLocationMarker()
        self.ReconstructEmanationLockMarker()
        self.LoadBookmarkMarkers()
        self.LoadShowHubMarkers()
        self.LoadVulnerableSkyhooks()

    def ExpandSelectedSolarSystem(self, solarSystemID):
        if self.isExpandingSolarSystem:
            return
        self.isExpandingSolarSystem = True
        uthread.new(self._ExpandSelectedSolarSystem, solarSystemID)

    def _ExpandSelectedSolarSystem(self, solarSystemID):
        try:
            if self.currentSolarsystem:
                resetSolarsystemID = self.currentSolarsystem.solarsystemID
            else:
                resetSolarsystemID = None
            if resetSolarsystemID == solarSystemID:
                return
            self.layoutHandler.SetExpandedSolarSystemID(solarSystemID)
            if not self.currentSolarsystem and solarSystemID is None:
                return
            if self.currentSolarsystem:
                self.currentSolarsystem.Close()
            mapNode = self.layoutHandler.GetNodeBySolarSystemID(solarSystemID)
            if not mapNode:
                return
            solarSystemPosition = mapNode.position
            self.ConstructExpandedSolarsystem(solarSystemID, solarSystemPosition)
        finally:
            self.isExpandingSolarSystem = False

    def ConstructExpandedSolarsystem(self, solarSystemID, solarSystemPosition):
        self.currentSolarsystem = SystemMapHandler(self, solarSystemID, scaling=mapViewConst.SCALING_SOLARSYSTEMINWORLDMAP, position=solarSystemPosition, loadBookmarks=True)
        self.currentSolarsystem.LoadSolarSystemMap()
        if self.destroyed:
            return
        self.currentSolarsystem.LoadMarkers()
        if self.destroyed:
            return
        cameraParentTravel = self.GetDistance(self.camera.atPosition, solarSystemPosition)
        scaling = self.GetSolarSystemMapScaling()
        if cameraParentTravel:
            uicore.animations.MorphVector3(self.currentSolarsystem.systemMapTransform, 'scaling', (0.0, 0.0, 0.0), (scaling, scaling, scaling), duration=max(0.1, min(1500.0, cameraParentTravel) / 2000.0))
        else:
            self.currentSolarsystem.systemMapTransform.scaling = (scaling, scaling, scaling)
        self.ReconstructMyLocationMarker()
        self.ReconstructEmanationLockMarker()
        self._ConstructSolarSystemVulnerableSkyhooks(solarSystemID, solarSystemPosition)

    def GetSolarSystemMapScaling(self):
        return mapViewUtil.ScaleSolarSystemValue(mapViewConst.SCALING_SOLARSYSTEMINWORLDMAP)

    def LoadBookmarkMarkers(self):
        if not self.destroyed and self.bookmarkHandler:
            self.bookmarkHandler.LoadBookmarkMarkers()

    def LoadLandmarkMarkers(self):
        for landmarkID, landmark in self.mapSvc.GetLandmarks().iteritems():
            if self.destroyed or not self.markersHandler:
                return
            pos = mapViewUtil.ScaledPosToMapPos(geo2.Vec3Scale(landmark.position, UNIVERSE_SCALE))
            self.markersHandler.AddLandmarkMarker(-landmarkID, pos, landmarkData=landmark, yScaleFactor=self.GetYScaleFactor())

    def LoadRegionMarkers(self):
        self.LogInfo('LoadRegionMarkers')
        for regionID, regionItem in self._GetKnownUniverseRegions().iteritems():
            if not IsKnownSpaceRegion(regionID):
                continue
            if self.destroyed or not self.markersHandler:
                return
            position = regionItem.mapPosition
            self.markersHandler.AddRegionMarker(regionID, position, yScaleFactor=self.GetYScaleFactor())
            blue.pyos.BeNice(TIME_BENICE)

    def LoadConstellationMarkers(self):
        for constellationID, constellationItem in self._GetKnownUniverseConstellations().iteritems():
            if not IsKnownSpaceConstellation(constellationID):
                continue
            if self.destroyed or not self.markersHandler:
                return
            self.markersHandler.AddConstellationMarker(constellationID, constellationItem.mapPosition, yScaleFactor=self.GetYScaleFactor())
            blue.pyos.BeNice(TIME_BENICE)

    def LoadShowHubMarkers(self):
        if not self.destroyed and self.sovHubHandler:
            uthread.new(self.sovHubHandler.LoadShowHubMarkers)

    def CheckFlattenCorrdinate(self, position):
        if not self.IsAbstractModeActive():
            return position
        k = self.GetYScaleFactor()
        return (position[0], k * position[1], position[2])

    def LoadSolarSystemMarkers(self):
        solarSystemIDs = self._GetAllSolarSystemIDs()
        for solarSystemID in solarSystemIDs:
            if not IsKnownSpaceSystem(solarSystemID):
                continue
            if self.destroyed or not self.markersHandler:
                return
            mapNode = self.layoutHandler.GetNodeBySolarSystemID(solarSystemID)
            self.markersHandler.AddSolarSystemMarker(solarSystemID, mapNode.position)
            blue.pyos.BeNice(TIME_BENICE)

    def _GetAllSolarSystemIDs(self):
        solarSystemIDs = self._GetKnownUniverseSolarSystems()
        if not self.activeSolarSystemID:
            return solarSystemIDs
        solarSystemData = mapViewData.GetKnownSolarSystem(self.activeSolarSystemID)
        consteallationData = mapViewData.GetKnownConstellation(solarSystemData.constellationID)
        activeSolarSystemIDs = consteallationData.solarSystemIDs + solarSystemData.neighbours
        return sorted(solarSystemIDs, key=lambda ssid: ssid in activeSolarSystemIDs, reverse=True)

    def GetLineIDForJumpBetweenSystems(self, fromSystemID, toSystemID):
        mapNode = self.layoutHandler.GetNodeBySolarSystemID(fromSystemID)
        if mapNode:
            for lineData in mapNode.lineData:
                if lineData.fromSolarSystemID == toSystemID or lineData.toSolarSystemID == toSystemID:
                    return lineData.lineID

    def GetLineIDsForSolarSystemID(self, solarSystemID):
        mapNode = self.layoutHandler.GetNodeBySolarSystemID(solarSystemID)
        if mapNode:
            return [ lineData.lineID for lineData in mapNode.lineData ]
        return []

    def GetLineIDsForSolarSystemIDs(self, solarSystemIDs):
        result = []
        for solarSystemID in solarSystemIDs:
            result.extend(self.GetLineIDsForSolarSystemID(solarSystemID))

        return result

    def LoadJumpLines(self):
        self.allianceJumpLines = []
        self.jumpLineInfoByLineID = {}
        self.allJumpBridges = []
        self.myJumpBridges = []
        lineSet = self.solarSystemJumpLineSet
        defaultColor = (0, 0, 0, 0)
        defaultPos = (0, 0, 0)
        for lineData in mapViewData.IterateJumps():
            lineID = lineSet.AddStraightLine(defaultPos, defaultColor, defaultPos, defaultColor, mapViewConst.JUMPLINE_BASE_WIDTH)
            lineData.lineID = lineID
            self.jumpLineInfoByLineID[lineID] = lineData
            fromNode = self.layoutHandler.GetNodeBySolarSystemID(lineData.fromSolarSystemID)
            fromNode.AddLineData(lineData)
            toNode = self.layoutHandler.GetNodeBySolarSystemID(lineData.toSolarSystemID)
            toNode.AddLineData(lineData)

    def LoadAllJumpBridges(self):
        self.allJumpBridges = []
        self.myJumpBridges = []
        jumpBridgesGates, hasAccessTo, hasNoAccessTo = sm.GetService('map').GetJumpBridgesWithMyAccess()
        defaultPos = (0, 0, 0)
        newLineData = []
        for structureA, structureB in jumpBridgesGates:
            solarSystemA = structureA.solarSystemID
            solarSystemB = structureB.solarSystemID
            if not IsSolarSystem(solarSystemA) or not IsSolarSystem(solarSystemB):
                self.LogWarn("DrawAllianceJumpLines had entry that wasn't a solarsystem:", solarSystemA, solarSystemB)
                continue
            hasAccessToA = structureA.structureID in hasAccessTo
            hasAccessToB = structureB.structureID in hasAccessTo
            colorA = JUMPBRIDGE_COLOR if hasAccessToA else JUMPBRIDGE_COLOR_NO_ACCESS
            colorB = JUMPBRIDGE_COLOR if hasAccessToB else JUMPBRIDGE_COLOR_NO_ACCESS
            lineID = self.solarSystemJumpLineSet.AddCurvedLineCrt(defaultPos, colorA, defaultPos, colorB, defaultPos, 3)
            lineData = mapViewData.PrimeJumpData(solarSystemA, solarSystemB, JUMPBRIDGE_TYPE, colorA, colorB)
            lineData.lineID = lineID
            newLineData.append(lineData)
            self.allJumpBridges.append(lineID)
            if hasAccessToA or hasAccessToB:
                self.myJumpBridges.append(lineID)
            self.jumpLineInfoByLineID[lineID] = lineData
            fromNode = self.layoutHandler.GetNodeBySolarSystemID(solarSystemA)
            fromNode.AddLineData(lineData)
            toNode = self.layoutHandler.GetNodeBySolarSystemID(solarSystemB)
            toNode.AddLineData(lineData)

        worldUp = geo2.Vector(0.0, -1.0, 0.0)
        for eachLineData in newLineData:
            self.layoutHandler.UpdateLinePosition(eachLineData, {}, worldUp)

        if self.solarSystemJumpLineSet:
            self.solarSystemJumpLineSet.SubmitChanges()

    def RefreshLines(self):
        self.dirtyLineIDs = set()
        self._UpdateLines(hint='RefreshLines')

    def UpdateLines(self, hint = '', **kwds):
        uthread.new(self._UpdateLines, hint)

    def _UpdateLines(self, hint = '', **kwds):
        if self.destroyed:
            return
        self.LogInfo('MapView UpdateLines ' + hint)
        lineMode = self.GetLineMode()
        if lineMode != self.lineMode:
            self.dirtyLineIDs = set()
            self.lineMode = lineMode
        self.UpdateLineColorData()
        self.UpdateJumpLineColorData()
        self.solarSystemJumpLineSet.SubmitChanges()

    def UpdateJumpLineColorData(self):
        if self.jumpRouteHighlightID:
            self.UpdateAutopilotJumpRoute(0.2)
            self.UpdateHighlightJumpRoute()
        else:
            self.UpdateAutopilotJumpRoute()

    def _GetLineOpacityByLineID(self):
        opacityByLineID = {}
        lineMode = self.GetLineMode()
        if lineMode != VIEWMODE_LINES_NONE:
            if self.activeRegionID and lineMode in (VIEWMODE_LINES_SELECTION_REGION, VIEWMODE_LINES_SELECTION_REGION_NEIGHBOURS) and IsKnownSpaceRegion(self.activeRegionID):
                self._GetLineOpacitySelectedRegionAndNeighbours(self.activeRegionID, opacityByLineID, OPACITY_LINES_SELECTED)
            if self.hilightID:
                self._GetLineOpacityByLineIDforItemID(opacityByLineID, self.hilightID, OPACITY_LINES_HOVERED)
            selectedID = self.GetSelectedItemID()
            self._GetLineOpacityByLineIDforItemID(opacityByLineID, selectedID, OPACITY_LINES_SELECTED)
        self._GetLineOpacityAllianceJumps(opacityByLineID)
        self._GetLineOpacityJumpsBridges(opacityByLineID)
        return opacityByLineID

    def _GetLineOpacityByLineIDforItemID(self, opacityByLineID, itemID, baseOpacity):
        if IsSolarSystem(itemID) and IsKnownSpaceSystem(itemID):
            if self.activeConstellationID:
                self._GetLineOpacityConstellationSelected(opacityByLineID, self.activeConstellationID, baseOpacity)
        elif IsConstellation(itemID) and IsKnownSpaceConstellation(itemID):
            self._GetLineOpacityConstellationSelected(opacityByLineID, itemID, baseOpacity)
        elif IsRegion(itemID) and IsKnownSpaceRegion(itemID):
            self._GetLineOpacityRegionSelected(opacityByLineID, itemID, baseOpacity)

    def GetSelectedItemID(self):
        return self.activeSolarSystemID or self.activeConstellationID or self.activeRegionID

    def _GetLineOpacityAllianceJumps(self, opacityByLineID):
        showAllianceLines = GetMapViewSetting(VIEWMODE_LINES_SHOW_ALLIANCE_SETTINGS, self.mapViewID)
        for lineID in self.allianceJumpLines:
            opacityByLineID[lineID] = OPACITY_LINES_SELECTED if showAllianceLines else 0.0

    def _GetLineOpacityJumpsBridges(self, opacityByLineID):
        showJumpBridges = GetMapViewSetting(VIEWMODE_LINES_SHOW_JUMP_BRIDGES_SETTINGS, self.mapViewID)
        linesToShow = self.myJumpBridges if showJumpBridges == VIEWMODE_LINES_SHOW_JUMP_BRIDGES_MY else self.allJumpBridges
        for lineID in self.allJumpBridges:
            opacityByLineID[lineID] = OPACITY_LINES_SELECTED if lineID in linesToShow else 0.0

    def _GetLineOpacitySelectedRegionAndNeighbours(self, activeRegionID, opacityByLineID, baseOpacity):
        if self.GetGroupingMode() == mapViewConst.VIEWMODE_LAYOUT_CONSTELLATIONS:
            regionsToShow = self._GetKnownUniverseRegions().keys()
        else:
            regionsToShow = [activeRegionID]
        if self.GetLineMode() == VIEWMODE_LINES_SELECTION_REGION_NEIGHBOURS:
            regionsToShow = regionsToShow + mapViewData.GetKnownRegion(activeRegionID).neighbours
        solarSystemIDs = self.mapSvc.ExpandItems(regionsToShow)
        lineIDs = self.GetLineIDsForSolarSystemIDs(solarSystemIDs)
        for lineID in lineIDs:
            opacity = baseOpacity / 4
            if lineID in opacityByLineID:
                opacityByLineID[lineID] += opacity
            else:
                opacityByLineID[lineID] = opacity

    def _GetLineOpacityRegionSelected(self, opacityByLineID, hiliteID, baseOpacity):
        hiliteItem = mapViewData.GetKnownRegion(hiliteID)
        lineIDs = self.GetLineIDsForSolarSystemIDs(hiliteItem.solarSystemIDs)
        for lineID in lineIDs:
            opacity = baseOpacity / 4
            if lineID in opacityByLineID:
                opacityByLineID[lineID] += opacity
            else:
                opacityByLineID[lineID] = opacity

    def _GetLineOpacityConstellationSelected(self, opacityByLineID, hiliteID, baseOpacity):
        constellation = mapViewData.GetKnownConstellation(hiliteID)
        lineIDs = self.GetLineIDsForSolarSystemIDs(constellation.solarSystemIDs)
        for lineID in lineIDs:
            if lineID in opacityByLineID:
                opacityByLineID[lineID] += baseOpacity
            else:
                opacityByLineID[lineID] = baseOpacity

    def GetLineMode(self):
        return GetMapViewSetting(VIEWMODE_LINES_SETTINGS, self.mapViewID)

    def ChangeLineColor(self, lineSet, lineID, color, opacity = 1.0):
        if len(color) == 2:
            fromColor = self.ModulateAlpha(color[0], opacity)
            toColor = self.ModulateAlpha(color[1], opacity)
        else:
            fromColor = toColor = self.ModulateAlpha(color, opacity)
        fromColor = colorblind.CheckReplaceColor(fromColor)
        toColor = colorblind.CheckReplaceColor(toColor)
        lineSet.ChangeLineColor(lineID, fromColor, toColor)

    def ModulateAlpha(self, color, alphaModulate):
        if len(color) == 3:
            r, g, b = color
            return (r,
             g,
             b,
             alphaModulate)
        r, g, b, a = color
        return (r,
         g,
         b,
         a * alphaModulate)

    def UpdateLineColorData(self):
        lineAlphaByLineID = self._GetLineOpacityByLineID()
        newLineIDs = set(lineAlphaByLineID.keys())
        updateLinesIDs = self.GetLineIDsToUpdate(newLineIDs)
        opacityDefault = self.GetLineDefaultOpacity()
        for lineID in updateLinesIDs:
            self.UpdateLineColorAndWidth(lineID, opacityDefault, lineAlphaByLineID)

    def GetLineDefaultOpacity(self):
        if self.GetLineMode() == VIEWMODE_LINES_ALL:
            opacityDefault = 0.1
        else:
            opacityDefault = 0.0
        return opacityDefault

    def GetLineIDsToUpdate(self, newLineIDs):
        if not self.dirtyLineIDs:
            updateLinesIDs = self.jumpLineInfoByLineID.keys()
        else:
            updateLinesIDs = newLineIDs.union(self.dirtyLineIDs)
        self.dirtyLineIDs = newLineIDs
        return updateLinesIDs

    def UpdateLineColorAndWidth(self, lineID, opacityDefault, lineAlphaByLineID):
        lineData = self.jumpLineInfoByLineID[lineID]
        fromColor, toColor = self.GetLineColor(opacityDefault, lineAlphaByLineID, lineData, lineID)
        lineSet = self.solarSystemJumpLineSet
        lineSet.ChangeLineColor(lineID, fromColor, toColor)
        lineSet.ChangeLineWidth(lineID, mapViewConst.JUMPLINE_BASE_WIDTH)
        if lineData.jumpType == mapcommon.REGION_JUMP:
            lineLength = self.layoutHandler.GetDistanceBetweenSolarSystems(lineData.fromSolarSystemID, lineData.toSolarSystemID)
            lineSet.ChangeLineAnimation(lineID, (0, 0, 0, 1), 0.0, lineLength / mapViewConst.REGION_LINE_TICKSIZE)
            lineSet.ChangeLineWidth(lineID, mapViewConst.JUMPLINE_BASE_WIDTH * 1.6)
        elif lineData.jumpType == mapcommon.CONSTELLATION_JUMP:
            lineLength = self.layoutHandler.GetDistanceBetweenSolarSystems(lineData.fromSolarSystemID, lineData.toSolarSystemID)
            ticksize = lineLength / mapViewConst.CONSTELLATION_LINE_TICKSIZE
            lineSet.ChangeLineAnimation(lineID, (0, 0, 0, 1), 0.0, ticksize)
            lineSet.ChangeLineWidth(lineID, mapViewConst.JUMPLINE_BASE_WIDTH * 1.3)
        else:
            lineSet.ChangeLineAnimation(lineID, (0, 0, 0, 0), 0.0, 1.0)

    def GetLineColor(self, baseLineAlphaModulate, lineAlphaByLineID, lineData, lineID):
        lineOpacity = lineAlphaByLineID.get(lineID, baseLineAlphaModulate)
        if lineID in self.allianceJumpLines:
            fromColor = toColor = JUMPBRIDGE_COLOR
        else:
            if lineID in self.allJumpBridges:
                lineData = self.jumpLineInfoByLineID[lineID]
                fromColor = lineData.colorFrom or JUMPBRIDGE_COLOR
                toColor = lineData.colorTo or JUMPBRIDGE_COLOR
                return (fromColor[:3] + (lineOpacity,), toColor[:3] + (lineOpacity,))
            fromColor = self.activeFilter.GetLineColor(lineData.fromSolarSystemID)
            toColor = self.activeFilter.GetLineColor(lineData.toSolarSystemID)
        if lineData.jumpType == mapcommon.REGION_JUMP:
            fromColor = self._GetRegionJumpColor(fromColor)
            toColor = self._GetRegionJumpColor(toColor)
        fromColor = self.ModulateAlpha(fromColor, lineOpacity)
        toColor = self.ModulateAlpha(toColor, lineOpacity)
        return (fromColor, toColor)

    def _GetRegionJumpColor(self, color):
        color = Color(*color)
        if color.IsGrayscale():
            color = color.SetBrightness(0.9)
        else:
            color = color.SetSaturation(0.7)
        return color.GetRGBA()

    def GetSystemColorBasedOnSecRating(self, ssID, alpha = 2.0):
        c = sm.GetService('map').GetModifiedSystemColor(ssID)
        return (c[0],
         c[1],
         c[2],
         alpha)

    def UpdateHighlightJumpRoute(self, lineAlpha = 3.0):
        targetID = self.jumpRouteHighlightID
        if targetID in [session.solarsystemid2, session.constellationid, session.regionid]:
            return []
        solarSystemIDs = sm.GetService('starmap').ShortestGeneralPath(targetID)
        if not len(solarSystemIDs):
            return
        self._UpdatePathLineAppearance(solarSystemIDs=solarSystemIDs, lineAlpha=lineAlpha, animate=False)

    def UpdateAutopilotJumpRoute(self, lineAlpha = 2.0):
        solarSystemIDs = sm.GetService('starmap').GetDestinationPath()
        if solarSystemIDs and solarSystemIDs[0] != session.solarsystemid2:
            solarSystemIDs = [session.solarsystemid2] + solarSystemIDs
        self._UpdatePathLineAppearance(solarSystemIDs=solarSystemIDs, lineAlpha=lineAlpha, animate=True)

    def _UpdatePathLineAppearance(self, solarSystemIDs, lineAlpha, animate):
        for i in xrange(len(solarSystemIDs) - 1):
            fromID = solarSystemIDs[i]
            toID = solarSystemIDs[i + 1]
            lineID = self.GetLineIDForJumpBetweenSystems(fromID, toID)
            if not lineID:
                continue
            self.ApplyJumpLineColorAndWidth(lineAlpha, fromID, toID, lineID)
            lineLength = self.layoutHandler.GetDistanceBetweenSolarSystems(fromID, toID)
            if lineLength:
                if animate:
                    animationSpeed, segmentScale = self.GetJumpRouteAnimationSpeedAndScale(fromID, lineID, lineLength)
                else:
                    animationSpeed = segmentScale = 0
                self.solarSystemJumpLineSet.ChangeLineAnimation(lineID, (0, 0, 0, 0.75), animationSpeed, segmentScale)

    def GetJumpRouteAnimationSpeedAndScale(self, fromID, lineID, lineLength):
        jumpLineInfo = self.jumpLineInfoByLineID[lineID]
        animationDirection = -1 if fromID == jumpLineInfo.fromSolarSystemID else 1
        segmentScale = lineLength / mapViewConst.AUTOPILOT_LINE_TICKSIZE
        animationSpeed = mapViewConst.AUTOPILOT_LINE_ANIM_SPEED / segmentScale * animationDirection
        return (animationSpeed, segmentScale)

    def ApplyJumpLineColorAndWidth(self, lineAlpha, fromID, toID, lineID):
        jumpLineInfo = self.jumpLineInfoByLineID[lineID]
        self.dirtyLineIDs.add(lineID)
        if fromID == jumpLineInfo.fromSolarSystemID:
            fromColor = self.GetSystemColorBasedOnSecRating(fromID, alpha=lineAlpha)
            toColor = self.GetSystemColorBasedOnSecRating(toID, alpha=lineAlpha)
        else:
            fromColor = self.GetSystemColorBasedOnSecRating(toID, alpha=lineAlpha)
            toColor = self.GetSystemColorBasedOnSecRating(fromID, alpha=lineAlpha)
        fromColor = colorblind.CheckReplaceColor(fromColor)
        toColor = colorblind.CheckReplaceColor(toColor)
        self.solarSystemJumpLineSet.ChangeLineColor(lineID, fromColor, toColor)
        self.solarSystemJumpLineSet.ChangeLineWidth(lineID, mapViewConst.AUTOPILOT_LINE_WIDTH)

    def SetMapFilter(self, filterID):
        self._SetMapFilter(filterID)
        self.UpdateMapViewColorMode()
        self.CheckUpdateCameraFocusByFilter()

    def _SetMapFilter(self, filterID):
        if filterID in mapcommon.oldColorModeToNewColorMode:
            filterID = mapcommon.oldColorModeToNewColorMode[filterID]
        SetMapViewSetting(VIEWMODE_COLOR_SETTINGS, filterID, self.mapViewID)

    def UpdateMapViewColorMode(self):
        filter = self.GetActiveFilter()
        self.activeFilter = filter
        if self.destroyed:
            return
        self.UpdateColorModeInfoPanel(self.activeFilter)
        self.ApplyStarColors()
        self.RefreshLines()
        self.markersHandler.RefreshActiveAndHilightedMarkers()

    def GetActiveFilter(self):
        filterID, itemID = self.GetFilterIDAndItemID()
        filterCls = filtersByID.GetFilterByID(filterID)
        if filterCls:
            return filterCls(filterID, itemID)
        filterData = self.GetColorFormatFunction(filterID)
        if filterData is None:
            SetMapViewSetting(VIEWMODE_COLOR_SETTINGS, None, self.mapViewID)
            return self.GetActiveFilter()
        return ColorInfoWrapperMapFilter(filterID, itemID, filterData)

    def GetColorFormatFunction(self, colorMode):
        return colorHandler.GetMapFilterData(colorMode)

    def UpdateColorModeInfoPanel(self, filter):
        pass

    def GetFilterIDAndItemID(self):
        ret = GetMapViewSetting(VIEWMODE_COLOR_SETTINGS, self.mapViewID)
        if not isinstance(ret, tuple):
            return (ret, None)
        else:
            return ret

    def ApplyStarColors(self):
        self.starColorByID = {}
        self.starDataTexture.resourcePath = self.activeFilter.GetSpriteEffectPath()
        self.starParticleTexture.resourcePath = self.activeFilter.GetSpriteEffectPathNear()
        for particleID, mapNode in self.layoutHandler.GetNodesByParticleID().iteritems():
            solarSystemID = mapNode.solarSystemID
            starColor = self.activeFilter.GetStarColor(solarSystemID)
            self.starColorByID[solarSystemID] = starColor
            self.starParticles.SetItemElement(particleID, 3, starColor)
            starSize = self.activeFilter.GetStarSize(solarSystemID)
            self.starParticles.SetItemElement(particleID, 2, float(starSize))

        self.starParticles.UpdateData()
        self.mapStars.display = 1

    def GetLegend(self, name):
        return getattr(self, name + 'Legend', [])

    def OnAutopilotUpdated(self):
        self.UpdateLines(hint='OnAutopilotUpdated')
        self._UpdateActiveMarkers(self.GetSelectedItemID())

    def OnDestinationSet(self, *args, **kwds):
        self.UpdateLines(hint='OnDestinationSet')
        self._UpdateActiveMarkers(self.GetSelectedItemID())

    def OnHomeStationChanged(self, *args, **kwds):
        self.ShowMyHomeStation()

    def OnBallparkSetState(self, *args):
        if session.solarsystemid2:
            if self.currentSolarsystem:
                self.currentSolarsystem.LoadMarkers()
            self.layoutHandler.ClearCache()
            self.RefreshActiveState(updateCamera=False)

    def OnStructuresVisibilityUpdated(self):
        if session.solarsystemid2:
            if self.currentSolarsystem:
                self.currentSolarsystem.LoadMarkers()

    def OnSessionChanged(self, isRemote, session, change):
        if 'locationid' in change and not IsSolarSystem(change['locationid'][1]) or 'structureid' in change:
            uthread.new(self.ReconstructMyLocationMarker)
            uthread.new(self.ReconstructEmanationLockMarker)
        if 'solarsystemid' in change:
            lastSystem, newSystem = change['solarsystemid']
            if self.activeItemID == lastSystem:
                self.SetActiveItemID(newSystem, zoomToItem=True)
        if 'shipid' in change:
            uthread.new(self.ReconstructMyLocationMarker)
            uthread.new(self.ReconstructEmanationLockMarker)

    def DoBallClear(self, solitem):
        self.RemoveMyLocation()

    def DoBallsAdded(self, balls_slimItems, *args, **kw):
        for ball, slimItem in balls_slimItems:
            if ball.id == session.shipid:
                uthread.new(self.ReconstructMyLocationMarker)
                uthread.new(self.ReconstructEmanationLockMarker)
                break

    def UpdateViewPort(self):
        if self.sceneContainer:
            self.sceneContainer.UpdateViewPort()
