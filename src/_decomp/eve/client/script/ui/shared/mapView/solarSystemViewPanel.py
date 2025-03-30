#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\solarSystemViewPanel.py
import carbonui.const as uiconst
import localization
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uicore import uicore
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.inflight.probeScannerWindow import ProbeScannerWindow
from eve.client.script.ui.inflight.scannerFiles.directionalScannerWindow import DirectionalScanner
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import IsProbeScanEmbeddedPanelOpen, IsDirectionalScanEmbeddedPanelOpen
from eve.client.script.ui.shared.mapView.dockPanel import DockablePanel
from eve.client.script.ui.shared.mapView.dockPanelConst import DOCKPANELID_SOLARSYSTEMMAP
from eve.client.script.ui.shared.mapView.mapViewConst import MAPVIEW_SOLARSYSTEM_ID
from eve.client.script.ui.shared.mapView.mapViewScannerNavigationStandalone import MapViewScannerNavigation
from eve.client.script.ui.shared.mapView.mapViewSolarSystem import MapViewSolarSystem
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.script.sys.idCheckers import IsSolarSystem
from eveuniverse.solar_systems import is_solarsystem_map_suppressed

class SolarSystemViewPanel(DockablePanel):
    __notifyevents__ = DockablePanel.__notifyevents__ + ['OnBallparkSetState',
     'OnTacticalOverlayChange',
     'OnSessionChanged',
     'OnSetCameraOffset',
     'OnHideUI',
     'OnShowUI',
     'OnProbeScannerOpened']
    default_captionLabelPath = None
    default_caption = None
    default_windowID = DOCKPANELID_SOLARSYSTEMMAP
    default_iconNum = 'res:/UI/Texture/classes/ProbeScanner/solarsystemMapButton.png'
    default_minSize = (600, 500)
    panelID = default_windowID
    mapView = None
    overlayTools = None
    mapViewID = MAPVIEW_SOLARSYSTEM_ID
    viewState = ViewState.SystemMapNew
    hasImmersiveAudioOverlay = True

    def ApplyAttributes(self, attributes):
        DockablePanel.ApplyAttributes(self, attributes)
        self.showRangeIndicator = sm.GetService('tactical').IsTacticalOverlayActive()
        self.mapView = MapViewSolarSystem(parent=self.GetMainArea(), showInfobox=False, navigationPadding=(0, 0, 0, 0), navigationClass=MapViewScannerNavigation, mapViewID=self.mapViewID, showSolarSystemNebula=True, showStarfield=False, showDebugInfo=False, sceneBlendMode=None, stackMarkers=True)
        sceneOptionsContainer = Container(parent=self.toolbarContainer, align=uiconst.CENTERLEFT, width=100, height=32, left=4, idx=0)
        from eve.client.script.ui.shared.mapView.controls.mapViewMarkersSettingButton import MapViewMarkersSettingButton
        self.markersSettingButton = MapViewMarkersSettingButton(parent=sceneOptionsContainer, callback=self.OnMarkersSettingChanged, mapViewID=self.mapViewID, align=uiconst.TOPLEFT, left=2, top=2)
        focusSelf = ButtonIcon(parent=sceneOptionsContainer, pos=(26, 2, 26, 26), iconSize=16, func=self.OnFocusSelf, hint=localization.GetByLabel('UI/Map/FocusCurrentLocation'), texturePath='res:/UI/Texture/classes/MapView/focusIcon.png', align=uiconst.TOPLEFT)
        focusSelf.tooltipPointer = uiconst.POINT_TOP_1
        Fill(bgParent=self.content, color=eveThemeColor.THEME_TINT, opacity=0.8)
        if not sm.GetService('ui').IsUiVisible():
            self.OnHideUI()
        uthread.new(self.LoadSolarSystem)
        self.UpdateScope()

    def UpdateScope(self):
        if session.solarsystemid2:
            self.scope = uiconst.SCOPE_INFLIGHT
        elif session.structureid:
            self.scope = uiconst.SCOPE_STATION
        else:
            self.scope = uiconst.SCOPE_STATION

    def OnShortcutKeyDown(self, modkey, vkey, flag):
        if uicore.registry.GetActive() == self:
            return self.mapView.CheckExecuteFilterShortcut(vkey)
        return False

    def Close(self, *args):
        DockablePanel.Close(self, *args)
        PlaySound('scanner_atmo_loop_stop')

    def ToggleDirectionalScanner(self):
        wasMinimized = False
        if self.IsMinimized():
            wasMinimized = True
            self.Maximize()
        self.mapView.ToggleDirectionalScanner(wasMinimized)
        uicore.registry.SetFocus(self)

    def ToggleProbeScanner(self):
        wasMinimized = False
        if self.IsMinimized():
            wasMinimized = True
            self.Maximize()
        self.mapView.ToggleProbeScanner(wasMinimized)
        uicore.registry.SetFocus(self)

    def OpenProbeScanner(self):
        if self.IsMinimized():
            self.Maximize()
        self.mapView.OpenProbeScanPanelEmbedded()
        uicore.registry.SetFocus(self)

    def OnShowUI(self):
        self.toolbarContainer.display = True

    def OnHideUI(self):
        if self.IsFullscreen():
            self.toolbarContainer.display = False

    def StartDirectionalScanHandler(self):
        if self.mapView and self.mapView.currentSolarsystem:
            self.mapView.currentSolarsystem.EnableDirectionalScanHandler()

    def StopDirectionalScanHandler(self):
        if self.mapView and self.mapView.currentSolarsystem:
            self.mapView.currentSolarsystem.StopDirectionalScanHandler()

    def GetDirectionalScanHandler(self):
        if self.mapView and self.mapView.currentSolarsystem:
            return self.mapView.currentSolarsystem.directionalScanHandler

    def StartProbeHandler(self):
        if self.mapView and self.mapView.currentSolarsystem:
            self.mapView.currentSolarsystem.EnableProbeHandlerStandalone()

    def StopProbeHandler(self):
        if self.mapView and self.mapView.currentSolarsystem:
            self.mapView.currentSolarsystem.StopProbeHandler()

    def OnFocusSelf(self, *args, **kwds):
        self.mapView.FocusSelf()

    def OnMarkersSettingChanged(self, *args, **kwds):
        self.mapView.OnMapViewSettingChanged(*args, **kwds)

    def OnDockModeChanged(self, *args, **kwds):
        self.mapView.OnDockModeChanged(self.IsFullscreen())

    def OnTacticalOverlayChange(self):
        if not self.mapView:
            return
        visible = sm.GetService('tactical').IsTacticalOverlayActive()
        self.showRangeIndicator = visible
        if visible:
            self.mapView.currentSolarsystem.ShowRangeIndicator()
        else:
            self.mapView.currentSolarsystem.HideRangeIndicator()

    def OnBallparkSetState(self):
        if not self.destroyed:
            uthread.new(self.LoadSolarSystem)

    def OnSetCameraOffset(self, cameraOffset):
        if self.mapView.camera:
            if self.IsFullscreen():
                x = -(cameraOffset * 0.5 - 0.5)
                self.mapView.camera.cameraCenter = (x, 0.5)
            else:
                self.mapView.camera.cameraCenter = (0.5, 0.5)

    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid2' in change:
            if is_solarsystem_map_suppressed(session.solarsystemid2):
                self.Close()
                return
        if 'locationid' in change and not IsSolarSystem(change['locationid'][1]):
            uthread.new(self.LoadSolarSystem)

    def LoadSolarSystem(self):
        if self.destroyed:
            return
        self.mapView.LoadSolarSystemDetails(session.solarsystemid2)
        settings.char.ui.Set('solarSystemView_loaded_%s' % self.mapViewID, session.solarsystemid2)
        self.mapView.FrameSolarSystem()
        self.mapView.sceneContainer.display = True
        self.SetCaption(cfg.evelocations.Get(session.solarsystemid2).name)
        if self.showRangeIndicator:
            self.mapView.currentSolarsystem.ShowRangeIndicator()
        self.UpdateProbeHandlers()

    def CmdZoomInOut(self, zoomDelta):
        if self.mapView:
            self.mapView.camera.Zoom(0.001 * zoomDelta)

    def OnProbeScannerOpened(self):
        self.UpdateProbeHandlers()

    def IsDirectionalScannerOpen(self):
        return IsDirectionalScanEmbeddedPanelOpen() or DirectionalScanner.IsOpen()

    def IsProbeScannerOpen(self):
        return IsProbeScanEmbeddedPanelOpen() or ProbeScannerWindow.IsOpen()

    def UpdateProbeHandlers(self):
        if self.IsProbeScannerOpen():
            self.StartProbeHandler()
        else:
            self.StopProbeHandler()
        if self.IsDirectionalScannerOpen():
            self.StartDirectionalScanHandler()
        else:
            self.StopDirectionalScanHandler()

    def OnSetActive_(self, *args):
        PlaySound('scanner_atmo_window_loop_play')

    def OnSetInactive(self, *args):
        super(SolarSystemViewPanel, self).OnSetInactive()
        PlaySound('scanner_atmo_loop_play')

    def OnStartMinimize_(self, *args):
        self.mapView.Hide()

    def OnStartMaximize_(self, *args):
        self.mapView.Show()
