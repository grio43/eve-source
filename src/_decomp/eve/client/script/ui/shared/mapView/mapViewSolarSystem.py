#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\mapViewSolarSystem.py
import logging
import carbonui.const as uiconst
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import evecamera
import geo2
import localization
import trinity
import uthread
from brennivin.itertoolsext import Bundle
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.fill import Fill
from carbonui.window.segment.underlay import WindowSegmentUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import IsUnder
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.control.themeColored import FillThemeColored, FrameThemeColored
from eve.client.script.ui.inflight.probeScannerWindow import ProbeScannerWindow
from eve.client.script.ui.inflight.scannerFiles.directionalScanUtil import SetScanModeTarget, IsDscanConeShown
from eve.client.script.ui.inflight.scannerFiles.directionalScannerPalette import DirectionalScannerPalette
from eve.client.script.ui.inflight.scannerFiles.directionalScannerWindow import DirectionalScanner
from eve.client.script.ui.inflight.scannerFiles.probeScannerPalette import ProbeScannerPalette
from eve.client.script.ui.inflight.scannerFiles.scanHologramHandler import ScanHologramHandler
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import SetProbeScanPanelWindowed, SetDirectionalScanPanelWindowed, IsSolarSystemMapFullscreen, IsShortuctExecutionAllowed, SetProbeScanEmbeddedPanelOpen, SetProbeScanEmbeddedPanelClosed, IsProbeScanEmbeddedPanelOpen, SetDirectionalScanEmbeddedPanelClosed, IsDirectionalScanEmbeddedPanelOpen, SetDirectionalScanEmbeddedPanelOpen
from eve.client.script.ui.shared.mapView.mapViewBookmarkHandler import MapViewBookmarkHandler
from eve.client.script.ui.shared.mapView.mapViewConst import MARKERID_MYPOS, MARKERID_MYHOME, VIEWMODE_MARKERS_SETTINGS, SETTING_PREFIX, MIN_CAMERA_DISTANCE_SOLARSYSTEMVIEW, MAX_CAMERA_DISTANCE_SOLARSYSTEMVIEW
from eve.client.script.ui.shared.mapView.mapViewScannerNavigationStandalone import MapViewScannerNavigation
from eve.client.script.ui.shared.mapView.mapViewSceneContainer import MapViewSceneContainer
from eve.client.script.ui.shared.mapView.mapViewUtil import SolarSystemPosToMapPos, ScaleSolarSystemValue, GetTranslationFromParentWithRadius, UpdateDebugOutput, TryGetPosFromItemID
from eve.client.script.ui.shared.mapView.markers.mapMarkerMyHome import MarkerMyHome
from eve.client.script.ui.shared.mapView.markers.mapMarkersHandler import MapViewMarkersHandler
from eve.client.script.ui.shared.mapView.markers.markerMyLocationSolarSystem import MarkerMyLocationSolarSystem
from eve.client.script.ui.shared.mapView.systemMapHandler import SystemMapHandler, SolarSystemInfoBox
from eve.common.script.sys.idCheckers import IsSolarSystem, IsStation, IsKnownSpaceSystem
from evegraphics import effects
from eveservices.menu import GetMenuService
from localization import GetByLabel
from menu import MenuList
from probescanning.tooltips.DScanHelpTooltip import DScanHelpTooltip
from probescanning.tooltips.ProbeScanHelpTooltip import ProbeScanHelpTooltip
log = logging.getLogger(__name__)
SUNBASE = 7.5
LINE_EFFECT = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Lines3DStarMapNew.fx'
PARTICLE_EFFECT = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Particles/StarmapNew.fx'
PARTICLE_SPRITE_TEXTURE = 'res:/Texture/Particle/mapStarNew5.dds'
PARTICLE_SPRITE_HEAT_TEXTURE = 'res:/Texture/Particle/mapStarNewHeat.dds'
DISTANCE_RANGE = 'distanceRange'
NEUTRAL_COLOR = (0.25,
 0.25,
 0.25,
 1.0)
HEX_TILE_SIZE = 60

class MapViewSolarSystem(Container):
    __notifyevents__ = ['OnUIScalingChange',
     'OnAutopilotUpdated',
     'OnDestinationSet',
     'OnSessionChanged',
     'OnBallparkSetState',
     'DoBallClear',
     'DoBallsAdded',
     'OnDirectionalScanComplete',
     'OnDirectionalScannerClosed',
     'OnDirectionalScannerOpened',
     'OnDirectionalScannerDocked',
     'OnDirectionalScannerUndocked',
     'OnDscanEntryMouseEnter',
     'OnDscanEntryMouseExit',
     'OnProbeScannerClosed',
     'OnProbeScannerDocked',
     'OnProbeScannerUndocked']
    curveSet = None
    systemMap = None
    mapRoot = None
    infoBox = None
    markersHandler = None
    bookmarkHandler = None
    layoutHandler = None
    markersAlwaysVisible = set()
    inFocus = False
    currentSolarsystem = None
    hilightID = None
    mapViewID = None
    sceneBlendMode = None
    showSolarSystemNebula = True
    showStarfield = False
    showDebugInfo = False
    showInfobox = False
    cameraID = evecamera.CAM_SOLARSYSTEMMAP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.mapViewID = attributes.mapViewID
        self.innerPadding = attributes.Get('innerPadding', 0)
        self.mapSvc = sm.GetService('map')
        self.autoFocusEnabled = settings.char.ui.Get('%s_autoFocusEnabled_%s' % (SETTING_PREFIX, self.mapViewID), True)
        self.mainCont = Container(name='mainCont', parent=self)
        self.infoLayer = Container(parent=self, clipChildren=True, name='infoLayer', padding=self.innerPadding)
        if attributes.showCloseButton:
            ButtonIcon(parent=self.infoLayer, hint=localization.GetByLabel('UI/Generic/Close'), texturePath='res:/UI/Texture/classes/DockPanel/closeButton.png', func=attributes.closeFunction or self.Close, align=uiconst.TOPRIGHT)
        self.showInfobox = attributes.Get('showInfobox', self.showInfobox)
        if self.showInfobox:
            self.infoBox = SolarSystemInfoBox(parent=self.infoLayer, align=uiconst.TOPLEFT, left=32, top=32)
        navigationClass = attributes.Get('navigationClass', MapViewScannerNavigation)
        navigationPadding = attributes.Get('navigationPadding', (0, 32, 0, 0))
        self.mapNavigation = navigationClass(parent=self, align=uiconst.TOALL, state=uiconst.UI_NORMAL, mapView=self, padding=navigationPadding)
        self.ConstructScene(attributes)
        self.ConstructViewButtonCont()

    def ConstructViewButtonCont(self):
        self.viewButtonCont = ContainerAutoSize(name='viewButtonCont', parent=Container(parent=self.mainCont), align=uiconst.CENTERBOTTOM, top=12)
        btn = ButtonIcon(parent=self.viewButtonCont, align=uiconst.TOPLEFT, iconSize=50, pos=(45, 0, 46, 46), texturePath='res:/UI/Texture/Classes/MapView/sideView.png', func=self.OnSideViewButton)
        btn.LoadTooltipPanel = self.LoadSideViewBtnTooltipPanel
        btn = ButtonIcon(parent=self.viewButtonCont, align=uiconst.TOPLEFT, iconSize=50, pos=(0, 0, 46, 46), texturePath='res:/UI/Texture/Classes/MapView/topView.png', func=self.OnTopViewButton)
        btn.LoadTooltipPanel = self.LoadTopViewBtnTooltipPanel

    def OnTopViewButton(self):
        self.mapNavigation.cameraController.SetTopView()

    def OnSideViewButton(self):
        self.mapNavigation.cameraController.SetSideView()

    def LoadSideViewBtnTooltipPanel(self, tooltipPanel, *args):
        self._LoadBtnTooltipPanel(tooltipPanel, 'UI/Inflight/Scanner/ViewFromSide')

    def LoadTopViewBtnTooltipPanel(self, tooltipPanel, *args):
        self._LoadBtnTooltipPanel(tooltipPanel, 'UI/Inflight/Scanner/ViewFromTop')

    def _LoadBtnTooltipPanel(self, tooltipPanel, txt):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=GetByLabel(txt), colSpan=tooltipPanel.columns, bold=True)
        tooltipPanel.AddLabelShortcut(GetByLabel('UI/Inflight/Scanner/ToggleView'), GetByLabel('UI/Inflight/Scanner/DoubleClickScene'), bold=False)

    def CheckExecuteFilterShortcut(self, vkey):
        if IsShortuctExecutionAllowed(self) and not IsSolarSystemMapFullscreen():
            dScanHasFocus = IsDirectionalScanEmbeddedPanelOpen() and IsUnder(uicore.registry.GetFocus(), self.directionalScannerPalette)
            if IsProbeScanEmbeddedPanelOpen() and not dScanHasFocus:
                return self.probeScannerPalette.ToggleFilterShortcut(vkey)
            if IsDirectionalScanEmbeddedPanelOpen():
                return self.directionalScannerPalette.ToggleFitlerShortcut(vkey)
        return False

    def ConstructScene(self, attributes):
        sceneContainer = MapViewSceneContainer(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=self.innerPadding, cameraID=self.cameraID)
        sceneContainer.Startup()
        self.sceneContainer = sceneContainer
        self.sceneContainer.display = False
        scene = trinity.EveSpaceScene()
        self.showSolarSystemNebula = attributes.Get('showSolarSystemNebula', self.showSolarSystemNebula)
        if self.showSolarSystemNebula:
            scene.backgroundRenderingEnabled = True
        self.showStarfield = attributes.Get('showStarfield', self.showStarfield)
        if self.showStarfield:
            scene.starfield = trinity.Load('res:/dx9/scene/starfield/spritestars.red')
            scene.backgroundRenderingEnabled = True
        self.mapRoot = trinity.EveRootTransform()
        self.mapRoot.name = 'mapRoot'
        scene.objects.append(self.mapRoot)
        self.sceneBlendMode = attributes.Get('sceneBlendMode', self.sceneBlendMode)
        self.sceneContainer.scene = scene
        self.sceneContainer.DisplaySpaceScene(blendMode=self.sceneBlendMode)
        if self.destroyed:
            return
        self.markersHandler = MapViewMarkersHandler(self, self.sceneContainer.bracketCurveSet, self.infoLayer, eventHandler=self.mapNavigation, stackMarkers=attributes.Get('stackMarkers', True))
        self.bookmarkHandler = MapViewBookmarkHandler(self)
        self.showDebugInfo = attributes.Get('showDebugInfo', self.showDebugInfo)
        if self.showDebugInfo:
            self.debugOutput = EveLabelSmall(parent=self, align=uiconst.BOTTOMLEFT, left=6, top=6, idx=0)
            self.debugOutputTimer = AutoTimer(5, self.UpdateDebugOutput)
        self.camera.fov = 0.7
        self.camera.maxZoom = MIN_CAMERA_DISTANCE_SOLARSYSTEMVIEW
        self.camera.minZoom = MAX_CAMERA_DISTANCE_SOLARSYSTEMVIEW
        self.camera.nearClip = 0.1
        self.camera.farClip = 50000.0
        self.camera.SetUpdateCallback(self.OnCameraUpdate)
        uthread.new(uicore.registry.SetFocus, self)
        self.ConstructScanPanels()
        self.scanHologramHandler = ScanHologramHandler(scene=self.sceneContainer.scene, camera=self.camera)
        sm.RegisterNotify(self)

    def ConstructScanPanels(self):
        self.horizontalDragCont = DragResizeCont(name='HorizontalDragContainer', parent=self.mainCont, idx=0, align=uiconst.TORIGHT, minSize=362, defaultSize=362, maxSize=600, onResizeCallback=self.OnHorizontalDragContResize, settingsID='solarSystemViewHorizontal', state=uiconst.UI_HIDDEN)
        self.panelsCont = DragResizeCont(name='PanelsContainer', parent=self.horizontalDragCont.mainCont, align=uiconst.TOTOP_PROP, minSize=0.32, defaultSize=0.5, maxSize=1.0, padding=(0, 26, 0, 0), settingsID='solarSystemViewVertical')
        self.secondPanelContainer = Container(name='secondPanelContainer', parent=self.horizontalDragCont.mainCont, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        self.secondPanelMainCont = Container(parent=self.secondPanelContainer, padding=4)
        FillThemeColored(bgParent=self.panelsCont.mainCont, colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=0.6)
        FillThemeColored(bgParent=self.secondPanelContainer, colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=0.6)
        FillThemeColored(bgParent=self.horizontalDragCont, colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=0.2)
        self.firstPanelMainCont = Container(name='firstPanelMainCont', parent=self.panelsCont.mainCont, padding=4)
        self.horizontalDragCont.mainCont.padding = 4
        self.panelsCont.OnMouseWheel = lambda *args: None
        self.directionalScannerPalette = None
        self.probeScannerPalette = None
        self.UpdateScanPanels()

    def UpdateScanPanels(self):
        if IsSolarSystemMapFullscreen():
            self.horizontalDragCont.padding = (0, 0, 18, 55)
        else:
            self.horizontalDragCont.padding = 0
        if not IsProbeScanEmbeddedPanelOpen() and not IsDirectionalScanEmbeddedPanelOpen():
            self.horizontalDragCont.Hide()
        elif not session.solarsystemid:
            self.horizontalDragCont.Hide()
        else:
            self.horizontalDragCont.Show()
            self._UpdateScanPanelsEmbedded()
        self.OnHorizontalDragContResize()

    def _UpdateScanPanelsEmbedded(self):
        parent = self.firstPanelMainCont
        if IsProbeScanEmbeddedPanelOpen() or IsDirectionalScanEmbeddedPanelOpen():
            if IsProbeScanEmbeddedPanelOpen():
                if self.probeScannerPalette:
                    self.probeScannerHeader.SetParent(parent)
                    self.probeScannerPalette.SetParent(parent)
                else:
                    self.ConstructScannerPalette(parent)
                parent = self.secondPanelMainCont
            if IsDirectionalScanEmbeddedPanelOpen():
                if self.directionalScannerPalette:
                    self.directionalScannerHeader.SetParent(parent)
                    self.directionalScannerPalette.SetParent(parent)
                else:
                    self.ConstructDirectionalScannerPalette(parent)
        if IsProbeScanEmbeddedPanelOpen() and IsDirectionalScanEmbeddedPanelOpen():
            self.panelsCont.SetMaxSize(0.8)
            self.secondPanelContainer.SetState(uiconst.UI_NORMAL)
        else:
            self.panelsCont.SetMaxSize(1.0)
            self.secondPanelContainer.SetState(uiconst.UI_HIDDEN)

    def OpenDirectionalScanPanelEmbedded(self):
        if IsDirectionalScanEmbeddedPanelOpen():
            return
        if self.currentSolarsystem:
            self.currentSolarsystem.EnableDirectionalScanHandler()
        SetDirectionalScanEmbeddedPanelOpen()
        self.UpdateScanPanels()

    def OpenProbeScanPanelEmbedded(self):
        if self.currentSolarsystem:
            self.currentSolarsystem.EnableProbeHandlerStandalone()
        SetProbeScanEmbeddedPanelOpen()
        self.UpdateScanPanels()

    def OnDirectionalScannerDocked(self):
        self.OpenDirectionalScanPanelEmbedded()

    def OnDirectionalScannerUndocked(self):
        SetDirectionalScanEmbeddedPanelClosed()

    def OnProbeScannerUndocked(self):
        SetProbeScanEmbeddedPanelClosed()

    def OnProbeScannerDocked(self):
        self.OpenProbeScanPanelEmbedded()

    def OnDockModeChanged(self, isFullScreen = False):
        self.horizontalDragCont.Close()
        self.mapNavigation.OnDockModeChanged()
        self.ConstructScanPanels()
        if isFullScreen:
            self.camera.EnableCenterOffset()
        else:
            self.camera.DisableCenterOffset()

    def ConstructDirectionalScannerPalette(self, parent):
        DirectionalScanner.CloseIfOpen()
        self.directionalScannerHeader = ScannerPaletteHeader(parent=parent, align=uiconst.TOTOP, text=GetByLabel('UI/Inflight/Scanner/DirectionalScanner'), floatCallback=self.SetDirectionalScannerWindowed, helpTooltip=DScanHelpTooltip, closeCallback=self.CloseDirectionalScannerPalette)
        self.directionalScannerPalette = DirectionalScannerPalette(parent=parent, padTop=2, scanOnOpen=False, state=uiconst.UI_NORMAL, uniqueUiName=pConst.UNIQUE_NAME_DIRECTIONAL_SCANNER)

    def CloseDirectionalScanWindow(self):
        dScanWindow = DirectionalScanner.GetIfOpen()
        if dScanWindow:
            dScanWindow.CloseByUser()

    def ConstructScannerPalette(self, parent):
        ProbeScannerWindow.CloseIfOpen()
        self.probeScannerHeader = ScannerPaletteHeader(parent=parent, align=uiconst.TOTOP, text=GetByLabel('UI/Inflight/Scanner/ProbeScanner'), floatCallback=self.SetProbeScannerWindowed, helpTooltip=ProbeScanHelpTooltip, closeCallback=self.CloseProbeScannerPalette)
        self.probeScannerPalette = ProbeScannerPalette(name='ProbeScannerPalette', parent=parent, align=uiconst.TOALL, state=uiconst.UI_NORMAL, padTop=2, uniqueUiName=pConst.UNIQUE_NAME_PROBE_SCANNER)

    def CloseProbeScannerWindow(self):
        probeScanWindow = ProbeScannerWindow.GetIfOpen()
        if probeScanWindow:
            probeScanWindow.CloseByUser()

    def CloseDirectionalScannerPalette(self):
        if self.currentSolarsystem:
            self.currentSolarsystem.StopDirectionalScanHandler()
        SetDirectionalScanEmbeddedPanelClosed()
        self.directionalScannerPalette.Close()
        self.directionalScannerHeader.Close()
        self.directionalScannerPalette = None
        self.UpdateScanPanels()

    def CloseProbeScannerPalette(self):
        if self.currentSolarsystem:
            self.currentSolarsystem.StopProbeHandler()
        SetProbeScanEmbeddedPanelClosed()
        self.probeScannerPalette.Close()
        self.probeScannerHeader.Close()
        self.probeScannerPalette = None
        self.UpdateScanPanels()

    def ToggleDirectionalScanner(self, wasMinimized = False):
        if IsDirectionalScanEmbeddedPanelOpen():
            if not wasMinimized:
                self.CloseDirectionalScannerPalette()
        else:
            self.OpenDirectionalScanPanelEmbedded()

    def ToggleProbeScanner(self, wasMinimized = False):
        if IsProbeScanEmbeddedPanelOpen():
            if not wasMinimized:
                self.CloseProbeScannerPalette()
        else:
            self.OpenProbeScanPanelEmbedded()

    def SetDirectionalScannerWindowed(self):
        self.CloseDirectionalScannerPalette()
        SetDirectionalScanPanelWindowed()
        DirectionalScanner.Open()
        self.UpdateScanPanels()

    def SetProbeScannerWindowed(self):
        self.CloseProbeScannerPalette()
        SetProbeScanPanelWindowed()
        ProbeScannerWindow.Open()
        self.UpdateScanPanels()

    def OnHorizontalDragContResize(self, *args):
        if not hasattr(self, 'horizontalDragCont'):
            return
        if self.horizontalDragCont.display:
            w, _ = self.GetAbsoluteSize()
            offset = self.horizontalDragCont.width / float(w)
        else:
            offset = 0.0
        self.camera.SetCenterOffsetPanels(offset)

    def _OnSizeChange_NoBlock(self, *args):
        self.OnHorizontalDragContResize()

    def Close(self, *args, **kwds):
        sm.UnregisterNotify(self)
        if hasattr(self, 'mapRoot') and self.mapRoot is not None:
            del self.mapRoot.children[:]
        self.mapRoot = None
        if self.currentSolarsystem:
            self.currentSolarsystem.RemoveFromScene()
        self.currentSolarsystem = None
        if self.camera:
            self.camera.OnDeactivated()
            sm.GetService('sceneManager').UnregisterCamera(self.camera.cameraID)
        self.camera = None
        if self.markersHandler:
            self.markersHandler.StopHandler()
        self.markersHandler = None
        if self.bookmarkHandler:
            self.bookmarkHandler.StopHandler()
        self.bookmarkHandler = None
        self.mapNavigation = None
        self.debugOutputTimer = None
        Container.Close(self)

    def UpdateDebugOutput(self):
        if self.destroyed:
            return
        UpdateDebugOutput(self.debugOutput, camera=self.camera, mapView=self)

    def SetFocusState(self, focusState):
        self.inFocus = focusState

    def OnMarkerHovered(self, itemID):
        hilightID = itemID
        if self.hilightID != hilightID:
            self.hilightID = hilightID
            if hilightID:
                self.markersHandler.HilightMarkers([hilightID])
            else:
                self.markersHandler.HilightMarkers([])

    def OnMapViewSettingChanged(self, settingKey, *args, **kwds):
        if settingKey == VIEWMODE_MARKERS_SETTINGS:
            if self.currentSolarsystem:
                self.currentSolarsystem.LoadMarkers(showChanges=True)

    def FocusSelf(self, *args, **kwds):
        self.EnableAutoFocus()
        self.SetActiveItemID(self.GetEgoMarkerID())

    def EnableAutoFocus(self):
        settings.char.ui.Set('%s_autoFocusEnabled_%s' % (SETTING_PREFIX, self.mapViewID), True)
        self.autoFocusEnabled = True

    def DisableAutoFocus(self):
        settings.char.ui.Set('%s_autoFocusEnabled_%s' % (SETTING_PREFIX, self.mapViewID), False)
        self.autoFocusEnabled = False

    @apply
    def solarSystemTransform():

        def fget(self):
            if self.currentSolarsystem:
                return self.currentSolarsystem.systemMapTransform

        return property(**locals())

    @apply
    def solarSystemSunID():

        def fget(self):
            if self.currentSolarsystem:
                return self.currentSolarsystem.sunID

        return property(**locals())

    @apply
    def camera():

        def fget(self):
            if getattr(self, 'sceneContainer', None):
                return self.sceneContainer.camera

        def fset(self, value):
            pass

        return property(**locals())

    @apply
    def scene():

        def fget(self):
            return self.sceneContainer.scene

        return property(**locals())

    @apply
    def solarSystemID():

        def fget(self):
            if self.currentSolarsystem:
                return self.currentSolarsystem.solarsystemID

        def fset(self, value):
            pass

        return property(**locals())

    def LogError(self, *args, **kwds):
        log.error('MAPVIEW ' + repr(args))

    def LogInfo(self, *args, **kwds):
        log.info('MAPVIEW ' + repr(args))

    def LogWarn(self, *args, **kwds):
        log.warning('MAPVIEW ' + repr(args))

    def OnUIScalingChange(self, *args):
        self.markersHandler.ReloadAll()

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
        if self.destroyed:
            return
        solarsystemID = homeStationRow.solarSystemID
        if solarsystemID != self.currentSolarsystem.solarsystemID:
            return
        if IsStation(homeStationID):
            stationInfo = sm.GetService('ui').GetStationStaticInfo(homeStationID)
            pos = (stationInfo.x, stationInfo.y, stationInfo.z)
        else:
            stationInfo = Bundle(stationID=homeStationID, stationTypeID=homeStationRow.stationTypeID)
            pos = TryGetPosFromItemID(homeStationID, solarsystemID)
        localPosition = SolarSystemPosToMapPos(pos)
        markerObject = self.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerMyHome, stationInfo=stationInfo, solarSystemID=solarsystemID, mapPositionLocal=localPosition, mapPositionSolarSystem=(0, 0, 0))
        self.markersAlwaysVisible.add(markerID)

    def RemoveMyLocation(self):
        markerID = self.GetEgoMarkerID()
        self.markersHandler.RemoveMarker(markerID, fadeOut=False)

    def ShowMyLocation(self):
        if self.destroyed:
            return
        if self.mapRoot is None:
            return
        self.RemoveMyLocation()
        markerID = self.GetEgoMarkerID()
        try:
            self.markersAlwaysVisible.remove(markerID)
        except:
            pass

        if self.solarSystemID == session.solarsystemid2:
            if session.stationid:
                stationInfo = sm.GetService('ui').GetStationStaticInfo(session.stationid)
                if self.destroyed:
                    return
                localPosition = SolarSystemPosToMapPos((stationInfo.x, stationInfo.y, stationInfo.z))
                trackObjectID = None
            elif session.structureid:
                structureInfo = self.mapSvc.GetMapDataForStructure(session.solarsystemid2, session.structureid)
                localPosition = SolarSystemPosToMapPos((structureInfo.x, structureInfo.y, structureInfo.z))
                trackObjectID = None
            else:
                localPosition = (0, 0, 0)
                trackObjectID = session.shipid or session.stationid
            self.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerMyLocationSolarSystem, trackObjectID=trackObjectID, solarSystemID=session.solarsystemid2, mapPositionLocal=localPosition, mapPositionSolarSystem=(0, 0, 0))
            self.markersAlwaysVisible.add(markerID)
            if self.autoFocusEnabled:
                self.FocusSelf()

    def GetEgoMarkerID(self):
        return (MARKERID_MYPOS, session.charid)

    def OnCameraUpdate(self):
        camera = self.camera
        if camera is None or self.destroyed:
            return
        if self.currentSolarsystem:
            self.currentSolarsystem.OnCameraUpdate()
        cameraDistance = camera.GetZoomDistanceForMap()
        if self.markersHandler:
            self.markersHandler.RegisterCameraTranslationFromParent(cameraDistance)

    def SetCameraPointOfInterestSolarSystemPosition(self, solarSystemID, position):
        if solarSystemID != self.solarSystemID:
            return
        self.DisableAutoFocus()
        self.camera.LookAtPoint(SolarSystemPosToMapPos(position))

    def SetActiveItemID(self, itemID, *args, **kwds):
        markerObject = self.markersHandler.GetMarkerByID(itemID)
        if markerObject:
            self.SetSelectedMarker(markerObject)

    def SetSelectedMarker(self, markerObject, *args, **kwds):
        PlaySound('msg_newscan_explore_click_play')
        SetScanModeTarget()
        self.camera.LookAtMarker(markerObject)

    def LookAtEgoMarker(self, duration = None):
        pos = self.GetEgoPosition()
        if pos:
            self.camera.LookAtPoint(pos, duration)

    def GetEgoPosition(self):
        markerObject = self.markersHandler.GetMarkerByID(self.GetEgoMarkerID())
        if markerObject:
            return markerObject.GetDisplayPosition()

    def LoadSolarSystemDetails(self, solarSystemID):
        current = getattr(self, 'currentSolarsystem', None)
        if current:
            resetSolarsystemID = current.solarsystemID
        else:
            resetSolarsystemID = None
        if resetSolarsystemID != solarSystemID:
            if current:
                current.Close()
            self.currentSolarsystem = None
            self.currentSolarsystem = SystemMapHandler(self, solarSystemID, position=(0, 0, 0))
            self.currentSolarsystem.LoadSolarSystemMap()
            self.currentSolarsystem.EnableProbeHandlerStandalone()
            if self.destroyed:
                return
            self.currentSolarsystem.LoadMarkers()
            if self.destroyed:
                return
            scaling = ScaleSolarSystemValue(1.0)
            self.currentSolarsystem.systemMapTransform.scaling = (scaling, scaling, scaling)
            if not IsKnownSpaceSystem(solarSystemID) and self.scene.starfield:
                self.scene.starfield.numStars = 0
            uthread.new(self.ShowMyHomeStation)
            uthread.new(self.ShowMyLocation)
            if self.infoBox:
                self.infoBox.LoadSolarSystemID(solarSystemID)

    def FrameSolarSystem(self):
        radius = ScaleSolarSystemValue(self.currentSolarsystem.solarSystemRadius)
        cameraDistanceFromInterest = GetTranslationFromParentWithRadius(radius, self.camera)
        if not self.autoFocusEnabled:
            self.SetCameraPointOfInterestSolarSystemPosition(session.solarsystemid2, (0, 0, 0))
        if cameraDistanceFromInterest:
            self.camera.SetZoomDistance(1.3 * cameraDistanceFromInterest)
        self.sceneContainer.display = True

    def GetPickObjects(self, *args, **kwds):
        return None

    def OnAutopilotUpdated(self):
        pass

    def OnDestinationSet(self, *args, **kwds):
        self.ShowMyLocation()

    def OnBallparkSetState(self, *args):
        if self.currentSolarsystem:
            self.currentSolarsystem.LoadMarkers()
            self.ShowMyHomeStation()

    def OnSessionChanged(self, isRemote, session, change):
        if self.destroyed:
            return
        if self.currentSolarsystem:
            if 'locationid' in change and not IsSolarSystem(change['locationid'][1]):
                self.currentSolarsystem.StopDirectionalScanHandler()
                self.currentSolarsystem.StopProbeHandler()
                self.currentSolarsystem.HideRangeIndicator()
                self.currentSolarsystem.LoadMarkers()
                self.ShowMyHomeStation()
                uthread.new(self.ShowMyLocation)
        if not session.solarsystemid:
            self.UpdateScanPanels()

    def DoBallClear(self, solitem):
        self.RemoveMyLocation()

    def DoBallsAdded(self, balls_slimItems, *args, **kw):
        for ball, slimItem in balls_slimItems:
            if ball.id == session.shipid:
                uthread.new(self.ShowMyLocation)
                break

    def UpdateViewPort(self):
        if self.sceneContainer:
            self.sceneContainer.UpdateViewPort()

    def OnDirectionalScanComplete(self, angle, range, direction, results):
        egoPos = self.GetEgoPosition()
        if IsDscanConeShown() and egoPos and not self.destroyed:
            self.scanHologramHandler.RenderHolograms(results, egoPos, direction)

    def OnDscanEntryMouseEnter(self, typeID):
        if IsDscanConeShown():
            egoPos = self.GetEgoPosition()
            if egoPos:
                camera = sm.GetService('sceneManager').GetActivePrimaryCamera()
                direction = geo2.Vec3Scale(camera.GetLookAtDirection(), -1)
                self.scanHologramHandler.RenderHologram(typeID, egoPos, direction)

    def OnDscanEntryMouseExit(self):
        self.scanHologramHandler.HideHologram()

    def OnDirectionalScannerOpened(self):
        if self.currentSolarsystem:
            self.currentSolarsystem.EnableDirectionalScanHandler()

    def OnDirectionalScannerClosed(self):
        SetDirectionalScanEmbeddedPanelClosed()
        if self.currentSolarsystem:
            self.currentSolarsystem.StopDirectionalScanHandler()

    def OnProbeScannerClosed(self):
        SetProbeScanEmbeddedPanelClosed()


class ScannerPaletteHeader(Container):
    name = 'ScannerPaletteHeader'
    default_height = 26

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        text = attributes.text
        floatCallback = attributes.floatCallback
        helpTooltip = attributes.helpTooltip
        self.closeCallback = attributes.closeCallback
        WindowSegmentUnderlay(bgParent=self)
        headerLabel = eveLabel.EveLabelMedium(parent=self, align=uiconst.CENTERLEFT, text=text, left=5)
        MoreInfoIcon(name='helpIcon', parent=self, align=uiconst.CENTERLEFT, left=headerLabel.width + 10).tooltipPanelClassInfo = helpTooltip()
        ButtonIcon(name='openInWindow', parent=self, iconSize=16, pos=(24, 0, 16, 16), texturePath='res:/UI/Texture/classes/DockPanel/floatButton.png', align=uiconst.CENTERRIGHT, func=floatCallback, hint=localization.GetByLabel('UI/Inflight/Scanner/OpenInWindow'))
        ButtonIcon(name='closePanel', parent=self, pos=(4, 0, 16, 16), texturePath='res:/UI/Texture/classes/DockPanel/closeButton.png', align=uiconst.CENTERRIGHT, func=self.close)

    def close(self):
        super(ScannerPaletteHeader, self).Close()
        self.closeCallback()
